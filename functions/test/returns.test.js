"use strict";
/* Returns from the site (returns.js): what can come back, the change-of-mind label with automatic refund on arrival,
   and problems with photos that the owners approve as a refund, a free reprint, or decline. */
const test = require("node:test");
const assert = require("node:assert/strict");
const { FakeDB, FakeAuth, FakeBucket, fakeNet } = require("./fakes");
const deps = require("../deps");

const ADMIN = { uid: "admin1", token: { admin: true, email: "owner@lhh.com" } };
const CUSTOMER = { uid: "guest9", token: { firebase: { sign_in_provider: "anonymous" } } };
const DAY = 86400000;

function setup({ deliveredDaysAgo = 5, shippoTrack = "TRANSIT" } = {}) {
  Object.assign(process.env, { STRIPE_SECRET_KEY: "sk_test_x", RESEND_API_KEY: "re_x", ADMIN_EMAILS: "owner@lhh.com", SITE_URL: "https://littlehivehouse.com",
    MAIL_FROM: "Little Hive House <hello@littlehivehouse.com>", MAIL_ADMIN: "support@littlehivehouse.com", SHIPPO_API_KEY: "shippo_live_x" });
  const db = new FakeDB(), net = fakeNet(), bucket = new FakeBucket();
  deps.set({ db, auth: new FakeAuth(), bucket });
  const refunds = [];
  net.handlers["POST /v1/refunds"] = (p) => { const r = { id: `re_${refunds.length + 1}`, amount: Number(p.amount), payment_intent: p.payment_intent, status: "succeeded", created: 1760000000, metadata: { reason: p["metadata[reason]"], note: p["metadata[note]"], by: p["metadata[by]"] } }; refunds.push(r); return r; };
  const shippo = [], track = { status: shippoTrack };
  globalThis.fetch = async (url, init = {}) => {
    const u = new URL(url);
    if (u.host !== "api.goshippo.com") return net.fetch(url, init);
    if (u.pathname.startsWith("/tracks/")) return { ok: true, status: 200, json: async () => ({ tracking_status: { status: track.status, status_details: "x", status_date: "2026-11-02T10:00:00Z" }, tracking_history: [] }) };
    const body = init.body ? JSON.parse(init.body) : null;
    shippo.push({ path: u.pathname, body });
    if (u.pathname === "/shipments/") return { ok: true, status: 200, json: async () => ({ object_id: "shp_r", rates: [{ object_id: "rate_ret", provider: "USPS", amount: "4.61", servicelevel: { token: "usps_ground_advantage", name: "Ground Advantage" } }] }) };
    if (u.pathname === "/transactions/") return { ok: true, status: 200, json: async () => ({ object_id: "tx_r", status: "SUCCESS", tracking_number: "9202090153540000000000", label_url: "https://shippo/label.pdf", qr_code_url: "https://shippo/qr.png" }) };
    return { ok: false, status: 404, json: async () => ({}) };
  };
  const now = Date.now();
  db.docs.set("settings/store", { shipFrom: { name: "Little Hive House", street1: "100 Main St", city: "Whitesburg", state: "GA", zip: "30185", phone: "4045550123" } });
  db.docs.set("meta/counters", { orderNumber: 1009 });
  db.docs.set("orders/o1", {
    number: "LHH-1009", email: "ana@example.com", name: "Ana Souza", status: "delivered",
    items: [
      { kind: "design", id: "fall/pumpkin", title: "Pumpkin", collection: "fall", qty: 3, unit: 5 },
      { kind: "photos", packSize: 9, qty: 1, price: 30, photos: Array.from({ length: 9 }, (_, n) => ({ path: `uploads/u1/p1/${n + 1}.jpg`, frame: "none" })) },
    ],
    // 3 designs for $12 (bundle) + pack $30 = $42, shipping free, tax $2.10 -> total $44.10
    pricing: { subtotal: 45, bundleDiscount: 3, shipping: 0, tax: 2.1, total: 44.1, currency: "usd" },
    shipping: { name: "Ana Souza", address: { line1: "1 Palm Ave", city: "Orlando", state: "FL", postal_code: "32801", country: "US" } },
    stripe: { paymentIntent: "pi_1" }, payment: { state: "captured" },
    fulfillment: { carrier: "usps", tracking: "9400", shippedAt: new Date(now - (deliveredDaysAgo + 3) * DAY).toISOString(), deliveredAt: new Date(now - deliveredDaysAgo * DAY).toISOString() },
    refunds: [], refundedTotal: 0, timeline: [], emails: {},
  });
  const returns = require("../returns");
  require("../printsheet").setBuilder && require("../printsheet").setBuilder(async () => ({ pdf: Buffer.from("%PDF"), slip: Buffer.from("%PDF"), meta: {} }));
  return { db, net, bucket, shippo, refunds, track, returns };
}
const who = { number: "lhh-1009", email: "Ana@Example.com" };

test("what can come back: values after the bundle discount, with tax; only designs for a change of mind", async () => {
  const { returns } = setup();
  const r = await returns.returnLookup(who, null, null);
  assert.equal(r.window.open, true);
  const [d, p] = r.lines;
  assert.equal(d.magnets, 3); assert.equal(d.changeMind, true);
  assert.equal(d.valueEach, 4.9);           // $5 x (44.10 / 45)
  assert.equal(p.magnets, 9); assert.equal(p.changeMind, false);
  assert.equal(p.valueEach, 3.27);          // $30 / 9 x 0.98
  await assert.rejects(returns.returnLookup({ number: "LHH-1009", email: "x@y.com" }, null, null), (e) => e.code === "not-found");
});

test("after 30 days nothing can be returned", async () => {
  const { returns } = setup({ deliveredDaysAgo: 31 });
  const r = await returns.returnLookup(who, null, null);
  assert.equal(r.window.open, false);
  assert.deepEqual(r.lines, []);
  await assert.rejects(returns.returnStart({ ...who, kind: "changed_mind", lines: [{ index: 0, qty: 1 }], unused: true }, null, null), (e) => e.code === "failed-precondition");
});

test("changed my mind: a USPS return label with a QR code, the refund minus the label goes out when it arrives", async () => {
  const { db, net, shippo, refunds, track, returns } = setup();
  const q = await returns.returnQuote({ ...who, lines: [{ index: 0, qty: 2 }] }, null, null);
  assert.deepEqual(q, { value: 9.8, labelCost: 4.61, refund: 5.19 });
  await assert.rejects(returns.returnStart({ ...who, kind: "changed_mind", lines: [{ index: 1, qty: 1 }], unused: true }, null, null), (e) => /made just for you/.test(e.message));
  await assert.rejects(returns.returnStart({ ...who, kind: "changed_mind", lines: [{ index: 0, qty: 2 }] }, null, null), (e) => /unused/.test(e.message));
  const s = await returns.returnStart({ ...who, kind: "changed_mind", lines: [{ index: 0, qty: 2 }], unused: true }, null, null);
  assert.equal(s.status, "label_sent");
  assert.equal(s.label.qr, "https://shippo/qr.png");
  const ship = shippo.find((c) => c.path === "/shipments/");
  assert.equal(ship.body.extra.is_return, true);
  assert.equal(ship.body.extra.qr_code_requested, true);
  assert.equal(ship.body.address_from.street1, "100 Main St");     // the shop: Shippo swaps them for a return
  assert.equal(ship.body.parcels[0].weight, "4");                   // 2.5 + 2 x 0.45 = 3.4 oz -> 4 oz band
  const mailOut = net.emails.find((e) => /return label/.test(e.subject));
  assert.ok(mailOut && /qr\.png/.test(mailOut.html), "the label email with the QR code");
  // only 1 more Pumpkin can come back now
  const after = await returns.returnLookup(who, null, null);
  assert.equal(after.lines[0].left, 1);
  // USPS: mailed, then delivered to the shop -> refund by itself
  await returns.checkReturns();
  assert.equal(db.get(`returns/${s.id}`).status, "in_transit");
  assert.equal(refunds.length, 0);
  track.status = "DELIVERED";
  await returns.checkReturns();
  const ret = db.get(`returns/${s.id}`);
  assert.equal(ret.status, "refunded");
  assert.equal(refunds[0].amount, 519);
  assert.equal(db.get("orders/o1").refundedTotal, 5.19);
  assert.ok(net.emails.some((e) => /refund/i.test(e.subject) && /return shipping/.test(e.html)), "the refund email says why");
});

test("a problem with photos: the owners refund it, reprint it for free, or decline it", async () => {
  const { db, net, bucket, refunds, returns } = setup();
  await assert.rejects(returns.returnStart({ ...who, kind: "problem", reason: "damaged", lines: [{ index: 0, qty: 1 }], photos: [] }, CUSTOMER, null), (e) => /photo/.test(e.message));
  await assert.rejects(returns.returnStart({ ...who, kind: "problem", lines: [{ index: 0, qty: 1 }], photos: ["returns/someoneelse/k1/1.jpg"] }, CUSTOMER, null), (e) => e.code === "invalid-argument");
  const a = await returns.returnStart({ ...who, kind: "problem", reason: "damaged", wants: "refund", note: "Cracked corner", lines: [{ index: 0, qty: 1 }], photos: ["returns/guest9/k1/1.jpg"] }, CUSTOMER, null);
  assert.equal(a.status, "requested");
  assert.ok(net.emails.some((e) => e.to === "ana@example.com" || (Array.isArray(e.to) && e.to.includes("ana@example.com"))), "the customer hears we got it");
  assert.ok(net.emails.some((e) => /Return request LHH-1009/.test(e.subject)), "the shop gets an email");
  await assert.rejects(returns.adminReturnDecide({ returnId: a.id, action: "refund" }, { uid: "x", token: {} }));
  const r1 = await returns.adminReturnDecide({ returnId: a.id, action: "refund" }, ADMIN);
  assert.equal(r1.status, "refunded");
  assert.equal(refunds[0].amount, 490);
  await assert.rejects(returns.adminReturnDecide({ returnId: a.id, action: "refund" }, ADMIN), (e) => /already/.test(e.message));

  // two photo magnets reprinted: a new $0 order with those two photos, number LHH-1010
  const b = await returns.returnStart({ ...who, kind: "problem", reason: "misprint", wants: "reprint", lines: [{ index: 1, qty: 2 }], photos: ["returns/guest9/k2/1.jpg"] }, CUSTOMER, null);
  const r2 = await returns.adminReturnDecide({ returnId: b.id, action: "reprint", photos: [3, 5] }, ADMIN);
  assert.equal(r2.reprint.number, "LHH-1010");
  const rep = db.get(`orders/${r2.reprint.orderId}`);
  assert.equal(rep.status, "paid");
  assert.equal(rep.pricing.total, 0);
  assert.equal(rep.source, "reprint");
  assert.deepEqual(rep.items[0].photos.map((p) => p.path), ["uploads/u1/p1/4.jpg", "uploads/u1/p1/6.jpg"]);
  assert.equal(rep.reprintOf.number, "LHH-1009");
  assert.ok(net.emails.some((e) => /reprinting/.test(e.subject)));

  const c = await returns.returnStart({ ...who, kind: "problem", reason: "other", lines: [{ index: 1, qty: 1 }], photos: ["returns/guest9/k3/1.jpg"] }, CUSTOMER, null);
  await returns.adminReturnDecide({ returnId: c.id, action: "decline", note: "That is how the photo looked." }, ADMIN);
  assert.equal(db.get(`returns/${c.id}`).status, "declined");
  assert.ok(net.emails.some((e) => /About your return/.test(e.subject) && /how the photo looked/.test(e.html)));
  // a declined return gives the magnet back to the list
  const l = await returns.returnLookup(who, null, null);
  assert.equal(l.lines[1].left, 7);
  void bucket;
});
