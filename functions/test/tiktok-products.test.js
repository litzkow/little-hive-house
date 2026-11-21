"use strict";
/* TikTok Shop products (tiktok-products.js): the product body (site price, one SKU per design in the site's order,
   the category's fixed attributes, square site-look photos), the description without Etsy words, and publishing:
   photos uploaded, product made once, then updated in place (same SKU ids) when the photo version changes. */
const test = require("node:test");
const assert = require("node:assert/strict");
const { FakeDB, FakeAuth, FakeBucket } = require("./fakes");
const deps = require("../deps");

const ADMIN = { uid: "a", token: { admin: true, email: "owner@lhh.com" } };

test("body: site price, numbered designs, all SKUs from the listing, attributes, package", () => {
  const P = require("../tiktok-products")._internal;
  const l = require("../etsy-listings.json").listings.find((x) => x.id === "places");
  const b = P.body(l, ["m1", "m2"], l.designs.map((_, i) => `s${i}`), "wh");
  assert.equal(b.category_id, "854536");
  assert.equal(b.skus.length, l.variations[0].options.length);
  assert.equal(b.skus[0].price.amount, "5.00");
  assert.equal(b.skus[0].seller_sku, "places-1");
  assert.match(b.skus[0].sales_attributes[0].value_name, /^01 /);
  assert.equal(b.skus[3].sales_attributes[0].sku_img.uri, "s3");
  assert.equal(b.main_images.length, 2);
  assert.ok(b.product_attributes.some((a) => a.id === "100548" && a.values[0].id === "1001505"));   // square
  assert.match(b.title, /^USA Places Fridge Magnets/);
  assert.ok(b.package_weight && b.package_dimensions);
});

test("description: no Etsy menu or USPS promise, HTML paragraphs", () => {
  const P = require("../tiktok-products")._internal;
  const l = require("../etsy-listings.json").listings.find((x) => x.id === "fall");
  const d = P.description(l);
  assert.doesNotMatch(d, /in the menu|USPS|SHIPPING/);
  assert.match(d, /<p><strong>WHAT YOU GET<\/strong><\/p>/);
  assert.equal(P.optionName("01 January ·"), "01 January");
});

test("publish: uploads the photos, makes the product once, updates it in place on a new photo version", async () => {
  Object.assign(process.env, { ADMIN_EMAILS: "owner@lhh.com", SITE_URL: "https://littlehivehouse.com" });
  const db = new FakeDB();
  deps.set({ db, auth: new FakeAuth(), bucket: new FakeBucket() });
  db.docs.set("tiktok/auth", { appSecret: "x".repeat(40), access: "TTP_a", refresh: "TTP_r", accessExpiresAt: Date.now() + 7 * 864e5, shopCipher: "GCP_c" });
  const T = require("../tiktok");
  const P = require("../tiktok-products");
  const calls = [];
  let n = 0;
  T.setTransport(async (url, opts = {}) => {
    const u = new URL(String(url));
    calls.push({ m: opts.method, p: u.pathname, body: opts.body });
    const ok = (data) => ({ ok: true, status: 200, json: async () => ({ code: 0, data }) });
    if (u.pathname.endsWith("/warehouses")) return ok({ warehouses: [{ id: "W1", type: "SALES_WAREHOUSE", is_default: true }] });
    if (u.pathname.endsWith("/images/upload")) return ok({ uri: `img${++n}` });
    if (u.pathname === "/product/202309/products" && opts.method === "POST") {
      const b = JSON.parse(opts.body);
      return ok({ product_id: "P1", skus: b.skus.map((s, i) => ({ id: `K${i + 1}`, seller_sku: s.seller_sku })) });
    }
    if (u.pathname === "/product/202309/products/P1" && opts.method === "PUT") return ok({ product_id: "P1", skus: [] });
    return { ok: false, status: 404, json: async () => ({ code: 1, message: "nope" }) };
  });
  P.setPhotoTools(async () => Buffer.from("jpg"), async (b) => b);
  const l = require("../etsy-listings.json").listings.find((x) => x.id === "birth-flowers");
  const r = await T.adminTikTok({ action: "publish", id: "birth-flowers" }, ADMIN);
  assert.equal(r.product.productId, "P1");
  const photos = require("../tiktok-photos.json").photos["birth-flowers"];
  assert.equal(calls.filter((c) => c.p.endsWith("/images/upload")).length, photos + l.designs.length);
  assert.equal(Object.keys(r.product.skus).length, l.designs.length);
  // again: nothing to do
  const again = await T.adminTikTok({ action: "publish", id: "birth-flowers" }, ADMIN);
  assert.equal(again.skipped, true);
  // forced update keeps the SKU ids
  calls.length = 0;
  await P.publish("birth-flowers", { force: true });
  const put = calls.find((c) => c.m === "PUT");
  assert.ok(put);
  const sent = JSON.parse(put.body);
  assert.equal(sent.skus[0].id, "K1");
  assert.equal(db.docs.get("tiktok/products")["birth-flowers"].skus["birth-flowers-1"], "K1");
});
