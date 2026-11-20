"use strict";
/* Etsy orders into Hive Admin (etsy-orders.js): a collection design and a business pack with the design number the buyer
   wrote, the address and totals, no email to the buyer, one order per receipt, and the tracking number back to Etsy. */
const test = require("node:test");
const assert = require("node:assert/strict");
const { FakeDB, FakeAuth, FakeBucket } = require("./fakes");
const deps = require("../deps");
const EO = require("../etsy-orders");

test("what the buyer wrote: the design number, the phone, the website and the name", () => {
  const p = EO.readPersonalization("Design 12, Tony's Pizza, (555) 123-4567, www.tonyspizza.com");
  assert.equal(p.n, 12);
  assert.deepEqual(p.words, { phone: "(555) 123-4567", web: "www.tonyspizza.com", name: "Tony's Pizza" });
  assert.equal(EO.readPersonalization("#3 - The Garcias - Est. 2015").n, 3);
  assert.equal(EO.readPersonalization("7\nMax\nGood boy").words.name, "Max");
  assert.equal(EO.readPersonalization("just make it pretty").n, null);
});

test("importOrders: an Etsy receipt becomes a paid order with the designs filled in; shipping sends the tracking to Etsy", async () => {
  Object.assign(process.env, { ETSY_KEYSTRING: "k", ETSY_SHARED_SECRET: "s", ADMIN_EMAILS: "owner@lhh.com", SITE_URL: "https://littlehivehouse.com" });
  const db = new FakeDB();
  deps.set({ db, auth: new FakeAuth(), bucket: new FakeBucket() });
  db.docs.set("etsy/auth", { access: "tok", refresh: "r", expiresAt: Date.now() + 3600000, shopId: "777" });
  db.docs.set("etsy/listings", { christmas: { listingId: 111, state: "active" }, "biz-pizza": { listingId: 222, state: "active" } });
  db.docs.set("meta/counters", { orderNumber: 1004 });
  const L = require("../etsy-listings.json").listings;
  const xmas = L.find((l) => l.id === "christmas"), pizza = L.find((l) => l.id === "biz-pizza");
  const posts = [];
  globalThis.fetch = async (url, init = {}) => {
    const u = new URL(url);
    if (init.method === "POST") { posts.push({ path: u.pathname, body: String(init.body) }); return { ok: true, status: 200, json: async () => ({}) }; }
    if (/\/receipts$/.test(u.pathname)) {
      return { ok: true, status: 200, json: async () => ({ count: 1, results: [{
        receipt_id: 9001, name: "Jane Doe", first_line: "1 Main St", second_line: "", city: "Austin", state: "TX", zip: "78701", country_iso: "US",
        create_timestamp: 1795000000, is_shipped: false, message_from_buyer: "Thanks!", subtotal: { amount: 10575, divisor: 100 },
        total_shipping_cost: { amount: 0, divisor: 100 }, total_tax_cost: { amount: 600, divisor: 100 }, grandtotal: { amount: 11175, divisor: 100 },
        transactions: [
          { transaction_id: 1, listing_id: 111, title: "Christmas", quantity: 1, price: { amount: 575, divisor: 100 },
            variations: [{ formatted_name: "Design", formatted_value: xmas.variations[0].options[6] }] },
          { transaction_id: 2, listing_id: 222, title: "Pizza", quantity: 1, price: { amount: 9900, divisor: 100 },
            variations: [{ formatted_name: "Pack size", formatted_value: "50 magnets" }, { formatted_name: "Personalization", formatted_value: "Design 1, Mario&#39;s Pizza, 555-201-3344, mariospizza.com" }] },
        ] }] }) };
    }
    return { ok: false, status: 404, json: async () => ({ error: "no fake" }) };
  };
  const r = await EO.importOrders();
  assert.equal(r.added, 1);
  const o = db.get("orders/etsy-9001");
  assert.equal(o.source, "etsy"); assert.equal(o.status, "paid"); assert.equal(o.email, ""); assert.equal(o.number, "LHH-1005");
  assert.equal(o.pricing.total, 111.75); assert.equal(o.shipping.address.city, "Austin");
  assert.equal(o.items[0].kind, "design"); assert.equal(o.items[0].id, xmas.designs[6]);
  const pk = o.items[1];
  assert.equal(pk.kind, "package"); assert.equal(pk.id, "business-50"); assert.equal(pk.design.slug, pizza.designs[0]);
  assert.equal(Object.values(pk.design.text).includes("Mario's Pizza"), true);
  assert.equal(pk.design.text.phone, "555-201-3344");
  assert.ok(o.adminNotes.some((n) => /Message from the buyer/.test(n.text)));
  // a second run adds nothing
  assert.equal((await EO.importOrders()).added, 0);
  // shipping: the tracking number goes to Etsy
  await EO.shipToEtsy(o, "usps", "9400111");
  assert.ok(posts.some((p) => p.path.endsWith("/shops/777/receipts/9001/tracking") && /tracking_code=9400111/.test(p.body) && /carrier_name=usps/.test(p.body)));
});
