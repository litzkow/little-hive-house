"use strict";
/* TikTok orders (tiktok-orders.js): a ready TikTok order becomes a Hive Admin order once, with the designs from the
   SKUs (one line per magnet -> one item with its quantity), no email to the buyer, TikTok's tax left out; unpaid and
   on-hold orders wait; the TikTok label ships the package and marks the order shipped with TikTok's tracking. */
const test = require("node:test");
const assert = require("node:assert/strict");
const { FakeDB, FakeAuth, FakeBucket } = require("./fakes");
const deps = require("../deps");

function setup(orders, extra = {}) {
  Object.assign(process.env, { ADMIN_EMAILS: "owner@lhh.com", SITE_URL: "https://littlehivehouse.com" });
  const db = new FakeDB();
  deps.set({ db, auth: new FakeAuth(), bucket: new FakeBucket() });
  db.docs.set("tiktok/auth", { appSecret: "x".repeat(40), access: "TTP_a", refresh: "TTP_r", accessExpiresAt: Date.now() + 7 * 864e5, shopCipher: "GCP_c", shopId: "S1" });
  db.docs.set("meta/counters", { orderNumber: 1041 });
  const calls = [];
  const T = require("../tiktok");
  T.setTransport(async (url, opts = {}) => {
    const u = new URL(String(url));
    calls.push({ m: opts.method, p: u.pathname, q: Object.fromEntries(u.searchParams), body: opts.body });
    const ok = (data) => ({ ok: true, status: 200, json: async () => ({ code: 0, data }) });
    if (u.pathname === "/order/202309/orders/search") return ok({ orders, next_page_token: "" });
    if (u.pathname === "/order/202309/orders") return ok({ orders: [extra.detail ? extra.detail() : orders[0]] });
    if (/\/packages\/.+\/ship$/.test(u.pathname)) { extra.shipped = true; return ok({}); }
    if (/shipping_documents$/.test(u.pathname)) return ok({ doc_url: "https://label.pdf", tracking_number: "" });
    return { ok: false, status: 404, json: async () => ({ code: 1, message: "nope" }) };
  });
  return { db, calls, T };
}

const ORDER = (status, more = {}) => ({
  id: "5770001", status, create_time: 1795300000, paid_time: 1795300100, buyer_message: "Happy birthday Mom",
  recipient_address: { name: "Ann Lee", address_line1: "1 Main St", postal_code: "30301", region_code: "US",
    district_info: [{ address_level_name: "State", address_name: "Georgia" }, { address_level_name: "City", address_name: "Atlanta" }] },
  payment: { original_total_product_price: "15.00", sub_total: "12.00", shipping_fee: "5.49", tax: "1.05", total_amount: "18.54", seller_discount: "3.00", platform_discount: "0" },
  line_items: [
    { id: "a", sku_id: "K1", product_id: "P1", seller_sku: "places-1", sale_price: "5.00", product_name: "USA Places", sku_name: "01 Grand Canyon" },
    { id: "b", sku_id: "K1", product_id: "P1", seller_sku: "places-1", sale_price: "5.00", product_name: "USA Places", sku_name: "01 Grand Canyon" },
    { id: "c", sku_id: "K2", product_id: "P1", seller_sku: "places-2", sale_price: "5.00", product_name: "USA Places", sku_name: "02 Atlanta" },
  ],
  packages: [{ id: "PK1" }], ...more,
});

test("a ready order comes in once, with its designs and quantities, no tax owed, no buyer email", async () => {
  const { db } = setup([ORDER("AWAITING_SHIPMENT")]);
  const O = require("../tiktok-orders");
  const r = await O.importOrders();
  assert.equal(r.added, 1);
  const o = db.docs.get("orders/tiktok-5770001");
  const l = require("../etsy-listings.json").listings.find((x) => x.id === "places");
  assert.equal(o.source, "tiktok");
  assert.equal(o.email, "");
  assert.equal(o.status, "paid");
  assert.equal(o.items.length, 2);
  assert.deepEqual([o.items[0].kind, o.items[0].id, o.items[0].qty], ["design", l.designs[0], 2]);
  assert.equal(o.items[1].id, l.designs[1]);
  assert.equal(o.pricing.tax, 0);
  assert.equal(o.pricing.total, 17.49);           // 15 - 3 (shop's discount) + 5.49 shipping
  assert.equal(o.shipping.address.city, "Atlanta");
  assert.equal(o.shipping.address.state, "Georgia");
  assert.match(o.adminNotes.map((n) => n.text).join(" "), /Happy birthday Mom/);
  assert.equal(o.number, require("../orders").formatOrderNumber(1042));
  assert.equal((await O.importOrders()).added, 0);
});

test("unpaid and on-hold orders wait", async () => {
  const { db } = setup([ORDER("UNPAID"), ORDER("ON_HOLD", { id: "5770002" })]);
  const r = await require("../tiktok-orders").importOrders();
  assert.equal(r.added, 0);
  assert.equal(db.docs.has("orders/tiktok-5770001"), false);
});

test("TikTok label: ships the package (drop-off), returns the PDF, marks the order shipped with TikTok's tracking", async () => {
  const extra = {};
  extra.detail = () => (extra.shipped ? ORDER("AWAITING_COLLECTION", { tracking_number: "9400111", shipping_provider: "USPS" }) : ORDER("AWAITING_SHIPMENT"));
  const { db, calls } = setup([ORDER("AWAITING_SHIPMENT")], extra);
  const O = require("../tiktok-orders");
  await O.importOrders();
  const r = await O.label("tiktok-5770001");
  assert.equal(r.url, "https://label.pdf");
  assert.equal(r.tracking, "9400111");
  const ship = calls.find((c) => /\/ship$/.test(c.p));
  assert.deepEqual(JSON.parse(ship.body), { handover_method: "DROP_OFF" });
  const o = db.docs.get("orders/tiktok-5770001");
  assert.equal(o.status, "shipped");
  assert.equal(o.fulfillment.carrier, "usps");
  assert.equal(o.fulfillment.tracking, "9400111");
  // again: no second shipment, just the label
  calls.length = 0;
  await O.label("tiktok-5770001");
  assert.equal(calls.some((c) => /\/ship$/.test(c.p)), false);
});
