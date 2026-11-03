"use strict";
/* USPS labels through Shippo (labels.js): price, buy, and the order marked shipped like the manual form. */
const test = require("node:test");
const assert = require("node:assert/strict");
const { FakeDB, FakeAuth, FakeBucket, fakeNet } = require("./fakes");
const deps = require("../deps");

const ADMIN = { uid: "admin1", token: { admin: true, email: "owner@lhh.com" } };
const SHIP_FROM = { name: "Little Hive House", street1: "100 Main St", city: "Whitesburg", state: "GA", zip: "30185" };

function setup({ key = "shippo_live_x", shipFrom = SHIP_FROM, rates } = {}) {
  Object.assign(process.env, { RESEND_API_KEY: "re_x", ADMIN_EMAILS: "owner@lhh.com", SITE_URL: "https://littlehivehouse.com",
    MAIL_FROM: "Little Hive House <hello@littlehivehouse.com>", MAIL_ADMIN: "support@littlehivehouse.com", SHIPPO_API_KEY: key });
  const db = new FakeDB(), net = fakeNet();
  deps.set({ db, auth: new FakeAuth(), bucket: new FakeBucket() });
  const shippo = [];
  const base = net.fetch;
  globalThis.fetch = async (url, init = {}) => {
    const u = new URL(url);
    if (u.host !== "api.goshippo.com") return base(url, init);
    const body = init.body ? JSON.parse(init.body) : null;
    shippo.push({ path: u.pathname, body, auth: init.headers.Authorization });
    if (u.pathname === "/shipments/") {
      return { ok: true, status: 200, json: async () => ({ object_id: "shp_1", rates: rates || [
        { object_id: "rate_pri", provider: "USPS", amount: "9.85", servicelevel: { token: "usps_priority", name: "Priority Mail" }, estimated_days: 2 },
        { object_id: "rate_ga", provider: "USPS", amount: "4.61", servicelevel: { token: "usps_ground_advantage", name: "Ground Advantage" }, estimated_days: 4 },
        { object_id: "rate_ups", provider: "UPS", amount: "3.10", servicelevel: { token: "ups_ground", name: "Ground" } },
      ], messages: [] }) };
    }
    if (u.pathname === "/transactions/") {
      return { ok: true, status: 200, json: async () => ({ object_id: "tx_1", status: "SUCCESS", tracking_number: "9400111899223344556677",
        label_url: "https://shippo-delivery.s3.amazonaws.com/label.pdf", rate: { amount: "4.61" } }) };
    }
    return { ok: false, status: 404, json: async () => ({ detail: "not found" }) };
  };
  if (shipFrom) db.docs.set("settings/store", { shipFrom });
  db.docs.set("orders/o1", { status: "in_production", email: "ana@example.com", number: 1001,
    items: [{ kind: "design", qty: 3 }, { kind: "photos", packSize: 9, qty: 1, price: 30 }],
    shipping: { name: "Ana Souza", address: { line1: "1 Palm Ave", city: "Orlando", state: "FL", postal_code: "32801", country: "US" } },
    pricing: { subtotal: 40, shipping: 0, total: 40 }, timeline: [] });
  return { db, net, shippo, labels: require("../labels") };
}

test("the price: USPS Ground Advantage for the suggested weight", async () => {
  const { shippo, labels } = setup();
  const q = await labels.adminLabelQuote({ orderId: "o1" }, ADMIN);
  // 12 magnets: 2.5 + 12 x 0.45 = 7.9 oz
  assert.equal(q.suggestedOz, 7.9);
  assert.equal(q.oz, 7.9);
  assert.equal(q.rate.rateId, "rate_ga");
  assert.equal(q.rate.amount, 4.61);
  assert.equal(q.test, false);
  const call = shippo[0];
  assert.equal(call.auth, "ShippoToken shippo_live_x");
  assert.equal(call.body.address_to.zip, "32801");
  assert.equal(call.body.address_from.street1, "100 Main St");
  assert.equal(call.body.parcels[0].weight, "7.9");
  const q2 = await labels.adminLabelQuote({ orderId: "o1", oz: "10.04" }, ADMIN);
  assert.equal(q2.oz, 10.1);
});

test("buying marks the order shipped with the tracking, like the manual form", async () => {
  const { db, net, labels } = setup();
  const r = await labels.adminBuyLabel({ orderId: "o1", rateId: "rate_ga", oz: 7.9 }, ADMIN);
  assert.equal(r.shipped, true);
  const o = db.get("orders/o1");
  assert.equal(o.status, "shipped");
  assert.equal(o.fulfillment.carrier, "usps");
  assert.equal(o.fulfillment.tracking, "9400111899223344556677");
  assert.equal(o.fulfillment.labelCost, 4.61);
  assert.equal(o.fulfillment.label.url, "https://shippo-delivery.s3.amazonaws.com/label.pdf");
  assert.ok(net.emails.some((e) => e.to === "ana@example.com" || (Array.isArray(e.to) && e.to.includes("ana@example.com"))), "the shipped email went out");
  // a second label for the same order needs an explicit "again"
  await assert.rejects(labels.adminBuyLabel({ orderId: "o1", rateId: "rate_ga" }, ADMIN), (e) => e.code === "already-exists" || e.code === "failed-precondition");
});

test("after 30 labels in a month, the 7 cent Shippo fee goes into the label cost", async () => {
  const { db, labels } = setup();
  db.docs.set(`labelStats/${new Date().toISOString().slice(0, 7)}`, { count: 30 });
  await labels.adminBuyLabel({ orderId: "o1", rateId: "rate_ga" }, ADMIN);
  const o = db.get("orders/o1");
  assert.equal(o.fulfillment.labelCost, 4.68);
  assert.equal(o.fulfillment.label.fee, 0.07);
  assert.equal(db.get(`labelStats/${new Date().toISOString().slice(0, 7)}`).count, 31);
});

test("a test key makes a sample label and leaves the order alone", async () => {
  const { db, labels } = setup({ key: "shippo_test_x" });
  const r = await labels.adminBuyLabel({ orderId: "o1", rateId: "rate_ga" }, ADMIN);
  assert.equal(r.test, true);
  assert.equal(r.shipped, false);
  const o = db.get("orders/o1");
  assert.equal(o.status, "in_production");
  assert.equal(o.fulfillment.label.test, true);
});

test("clear messages when something is missing", async () => {
  let s = setup({ shipFrom: null });
  await assert.rejects(s.labels.adminLabelQuote({ orderId: "o1" }, ADMIN), (e) => e.code === "failed-precondition" && /return address/.test(e.message));
  s = setup({ key: "" });
  await assert.rejects(s.labels.adminLabelQuote({ orderId: "o1" }, ADMIN), (e) => e.code === "failed-precondition" && /Shippo key/.test(e.message));
  s = setup({ rates: [] });
  await assert.rejects(s.labels.adminLabelQuote({ orderId: "o1" }, ADMIN), (e) => e.code === "unavailable");
  s = setup();
  await assert.rejects(s.labels.adminLabelQuote({ orderId: "o1" }, { uid: "x", token: {} }));
  await assert.rejects(s.labels.adminLabelQuote({ orderId: "o1", oz: "-2" }, ADMIN), (e) => e.code === "invalid-argument");
});

test("the settings keep a return address", async () => {
  const { db } = setup({ shipFrom: null });
  const admin = require("../admin");
  await assert.rejects(admin.adminSaveSettings({ settings: { shipFrom: { street1: "1 A St", city: "X", state: "Georgia", zip: "30185" } } }, ADMIN), (e) => e.code === "invalid-argument");
  await admin.adminSaveSettings({ settings: { shipFrom: { name: "Little Hive House", street1: " 1 A St ", city: "Whitesburg", state: "ga", zip: "30185" }, magnetOz: 0.5 } }, ADMIN);
  const s = db.get("settings/store");
  assert.equal(s.shipFrom.street1, "1 A St");
  assert.equal(s.shipFrom.state, "GA");
  assert.equal(s.magnetOz, 0.5);
});
