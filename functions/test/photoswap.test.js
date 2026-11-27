"use strict";
/* The customer swaps a photo of their own order (photoswap.js): only while "Order received", same price, frame and
   caption kept, the print sheet made again, the owners told by email and on the phone. */
const test = require("node:test");
const assert = require("node:assert/strict");
const { FakeDB, FakeAuth, FakeBucket, fakeNet } = require("./fakes");
const deps = require("../deps");

const GUEST = { uid: "guest9", token: { firebase: { sign_in_provider: "anonymous" } } };
const OTHER = { uid: "stranger", token: { firebase: { sign_in_provider: "anonymous" } } };
const MEMBER = { uid: "u1", token: { email: "camila@example.com", email_verified: true, firebase: { sign_in_provider: "password" } } };

function setup({ status = "paid" } = {}) {
  Object.assign(process.env, { STRIPE_SECRET_KEY: "sk_test_x", RESEND_API_KEY: "re_x", SITE_URL: "https://littlehivehouse.com", MAIL_FROM: "Little Hive House <hello@littlehivehouse.com>", MAIL_ADMIN: "support@littlehivehouse.com" });
  const db = new FakeDB(), net = fakeNet(), bucket = new FakeBucket();
  deps.set({ db, auth: new FakeAuth(), bucket });
  globalThis.fetch = net.fetch;
  const photos = Array.from({ length: 20 }, (_, n) => ({ path: `uploads/u1/pack-20/${n + 1}.jpg`, frame: n < 2 ? "polaroid" : "none", caption: n === 1 ? "Mom" : "", crop: { x: 0.5, y: 0.5, z: 1 } }));
  photos.forEach((p) => withThumb(bucket, p.path));
  db.docs.set("orders/o1", {
    number: "LHH-1004", email: "camila@example.com", name: "Camila Reis", status, uid: "u1",
    items: [
      { kind: "design", id: "fall/pumpkin", title: "Pumpkin", collection: "fall", qty: 1, unit: 5 },
      { kind: "photos", title: "Custom photo magnets (20)", packSize: 20, qty: 1, price: 50, photos },
    ],
    // $55 list, Black Friday 20% off -> $44, tax $2.64 -> $46.64; the card is only held (charged when it ships)
    pricing: { subtotal: 55, sale: { name: "Black Friday", pct: 20, amount: 11 }, shipping: 0, tax: 2.64, total: 46.64, currency: "usd" },
    payment: { state: "authorized" }, stripe: { paymentIntent: "pi_1" },
    printBorders: { all: null, items: {}, photos: { "1:0": "#000000", "1:2": "#FFFFFF", "1:5": "#F2A81D" } },
    timeline: [], adminNotes: [], emails: {},
  });
  const pushes = [];
  require("../push").setSender(async (sub, payload) => { pushes.push(JSON.parse(payload)); });
  db.docs.set("adminPush/phone1", { endpoint: "https://web.push.apple.com/x", keys: { p256dh: "p".repeat(60), auth: "a".repeat(20) }, uid: "admin1", prefs: {} });
  db.docs.set("meta/vapid", { publicKey: "pub", privateKey: "priv" });
  const builds = [];
  require("../printsheet").setBuilder(async (id, order) => { builds.push(order); return { pdf: Buffer.from("%PDF"), slip: Buffer.from("%PDF"), pages: 2, sheets: 2, tiles: 21 }; });
  require("../autocrop")._set({ token: async () => { throw Object.assign(new Error("no vision in tests"), { status: 403 }); } });
  return { db, net, bucket, pushes, builds, S: require("../photoswap") };
}
/* the small copies already made, as the Hive Admin leaves them: no sharp needed (the deploy machine has none) */
const JPG = Buffer.from("jpg");
const withThumb = (bucket, path) => { bucket.files.set(path, { data: JPG }); bucket.files.set(`thumbs/${path.replace(/\.[a-z]+$/, "")}.jpg`, { data: JPG }); };
const who = { number: "lhh-1004", email: "Camila@Example.com" };

test("the order page says when a photo can be swapped", () => {
  const O = require("../orders");
  const it = { kind: "photos", photos: [{ path: "uploads/a/b/1.jpg" }] };
  assert.equal(O.publicOrderView("x", { status: "paid", items: [it] }).photoSwap, "open");
  assert.equal(O.publicOrderView("x", { status: "in_production", items: [it] }).photoSwap, "closed");
  assert.equal(O.publicOrderView("x", { status: "paid", items: [{ kind: "design", id: "a/b" }] }).photoSwap, undefined);
  assert.equal(O.publicOrderView("x", { status: "paid", items: [{ kind: "photos", photos: [{ path: "etsy/123.jpg" }] }] }).photoSwap, undefined);
});

test("lists the customer's photos with small links, by number + email or signed in", async () => {
  const { S } = setup();
  const r = await S.orderPhotos(who, null, null);
  assert.equal(r.editable, true);
  assert.equal(r.packs.length, 1);
  assert.equal(r.packs[0].index, 1);
  assert.equal(r.packs[0].photos.length, 20);
  assert.equal(r.packs[0].photos[1].caption, "Mom");
  assert.match(r.packs[0].photos[0].thumb, /thumbs%2Fuploads%2Fu1%2Fpack-20%2F1\.jpg/);
  const mine = await S.orderPhotos({ id: "o1" }, MEMBER, null);
  assert.equal(mine.packs[0].photos.length, 20);
  await assert.rejects(S.orderPhotos({ number: "LHH-1004", email: "someone@else.com" }, null, null), /couldn't find/);
  await assert.rejects(S.orderPhotos({ id: "o1" }, { uid: "x", token: { email: "x@y.com", email_verified: true, firebase: { sign_in_provider: "password" } } }, null), /couldn't find/);
});

test("swapping a photo keeps the price, frame and caption, rebuilds the sheet and tells the owners", async () => {
  const { S, db, bucket, net, pushes, builds } = setup();
  withThumb(bucket, "uploads/guest9/swap-lhh-1004-a/2.jpg");
  const r = await S.swapOrderPhoto({ ...who, index: 1, n: 2, path: "uploads/guest9/swap-lhh-1004-a/2.jpg", w: 3000, h: 4000 }, GUEST, null);
  assert.equal(r.ok, true);
  assert.equal(r.swaps, 1);
  assert.match(r.photo.thumb, /thumbs%2Fuploads%2Fguest9/);
  const o = db.get("orders/o1");
  const p = o.items[1].photos[1];
  assert.equal(p.path, "uploads/guest9/swap-lhh-1004-a/2.jpg");
  assert.equal(p.frame, "polaroid");
  assert.equal(p.caption, "Mom");
  assert.equal(p.crop, undefined);                     // framing starts fresh for the new photo
  assert.equal(p.swapped.from, "uploads/u1/pack-20/2.jpg");
  assert.deepEqual([p.w, p.h], [3000, 4000]);
  assert.equal(o.items[1].photos[0].path, "uploads/u1/pack-20/1.jpg");   // the others untouched
  assert.equal(o.pricing.total, 46.64);
  assert.equal(o.status, "paid");
  assert.match(o.timeline.at(-1).text, /Photo 2 was changed/);
  assert.match(o.adminNotes.at(-1).text, /swapped photo 2/);
  assert.equal(builds.length, 1);
  assert.equal(builds[0].items[1].photos[1].path, "uploads/guest9/swap-lhh-1004-a/2.jpg");
  assert.ok(o.printSheet && o.printSheet.path);
  const mail = net.emails.find((e) => /Photo changed LHH-1004/.test(e.subject));
  assert.ok(mail, "the owners get an email");
  assert.equal(mail.reply_to, "camila@example.com");
  assert.equal(pushes.length, 1);
  assert.match(pushes[0].title, /Foto trocada LHH-1004/);
  assert.match(pushes[0].body, /foto 2/);
});

test("swaps are refused once the order is being made, for photos not uploaded by the caller, or wrong slots", async () => {
  const { S, bucket } = setup();
  bucket.files.set("uploads/guest9/swap-x/1.jpg", { data: Buffer.from("new") });
  const ok = { ...who, index: 1, n: 1, path: "uploads/guest9/swap-x/1.jpg" };
  await assert.rejects(S.swapOrderPhoto(ok, OTHER, null), /didn't upload correctly/);       // someone else's upload
  await assert.rejects(S.swapOrderPhoto({ ...ok, path: "uploads/guest9/swap-x/9.jpg" }, GUEST, null), /didn't finish uploading/);
  await assert.rejects(S.swapOrderPhoto({ ...ok, index: 0 }, GUEST, null), /pack isn't in this order/);
  await assert.rejects(S.swapOrderPhoto({ ...ok, n: 21 }, GUEST, null), /photo isn't in this order/);
  await assert.rejects(S.swapOrderPhoto(ok, null, null), /sign in/i);

  const made = setup({ status: "in_production" });
  made.bucket.files.set("uploads/guest9/swap-x/1.jpg", { data: Buffer.from("new") });
  await assert.rejects(made.S.swapOrderPhoto(ok, GUEST, null), /already started making/);
  const view = await made.S.orderPhotos(who, null, null);
  assert.equal(view.editable, false);
  assert.match(view.reason, /already started making/);
});

test("a cap on swaps per order", async () => {
  const { S, db, bucket } = setup();
  const o = db.get("orders/o1"); o.photoSwaps = S.MAX_SWAPS; db.docs.set("orders/o1", o);
  bucket.files.set("uploads/guest9/swap-x/1.jpg", { data: Buffer.from("new") });
  await assert.rejects(S.swapOrderPhoto({ ...who, index: 1, n: 1, path: "uploads/guest9/swap-x/1.jpg" }, GUEST, null), /a lot of photo changes/);
});

test("the owners' email renders", () => {
  const E = require("../emails");
  const { SAMPLES } = require("../emails/sample-data");
  const r = E.render("admin_photo_swap", SAMPLES.admin_photo_swap);
  assert.match(r.subject, /Photo changed LHH-1042: Karina Vargas swapped photo 7/);
  assert.match(r.text, /same price/);
});

test("removing a photo: one magnet less at the site's price, same discount and tax, charged at shipping", async () => {
  const { S, db, net, pushes, builds } = setup();
  const view = await S.orderPhotos(who, null, null);
  assert.equal(view.packs[0].removable, true);
  assert.equal(view.packs[0].removeSaves, 2.12);        // 20 -> 19 photos is $50 -> $47.50 list, 20% off = $2.00, + 6% tax
  const r = await S.removeOrderPhoto({ ...who, index: 1, n: 2 }, null, null);
  assert.deepEqual([r.ok, r.saved, r.total, r.packSize, r.held, r.refunded], [true, 2.12, 44.52, 19, true, 0]);
  const o = db.get("orders/o1");
  const it = o.items[1];
  assert.equal(it.packSize, 19); assert.equal(it.price, 47.5); assert.equal(it.photos.length, 19);
  assert.equal(it.title, "Custom photo magnets (19)");
  assert.equal(it.photos[1].path, "uploads/u1/pack-20/3.jpg");               // photo 3 moved up
  assert.deepEqual(o.printBorders.photos, { "1:0": "#000000", "1:1": "#FFFFFF", "1:4": "#F2A81D" });   // colours follow their photos
  assert.deepEqual([o.pricing.removed, o.pricing.removedList, o.pricing.tax, o.pricing.total], [2, 2.5, 2.52, 44.52]);
  // a later return values each magnet as before the removal: $5 design x (44.52 / 52.50) = $4.24
  const later = db.get("orders/o1"); later.status = "delivered"; later.fulfillment = { deliveredAt: new Date().toISOString() }; db.docs.set("orders/o1", later);
  assert.equal((await require("../returns").returnLookup(who, null, null)).lines[0].valueEach, 4.24);
  later.status = "paid"; delete later.fulfillment; db.docs.set("orders/o1", later);
  // the summary still adds up: 55 - 11 - 2 + 0 + 2.52 = 44.52
  assert.equal(Math.round((o.pricing.subtotal - o.pricing.sale.amount - o.pricing.removed + o.pricing.shipping + o.pricing.tax) * 100) / 100, o.pricing.total);
  assert.match(o.timeline.at(-1).text, /Photo 2 was removed\. 19 magnets now\./);
  assert.equal(builds.at(-1).items[1].photos.length, 19);
  assert.ok(net.emails.some((e) => /Photo removed LHH-1004/.test(e.subject)));
  assert.match(pushes.at(-1).title, /Foto tirada/);
  assert.equal(net.calls.filter((c) => c.path === "/v1/refunds").length, 0);   // nothing was charged: nothing to refund
  assert.equal(require("../orders").publicOrderView("o1", o).pricing.removed, 2);

  // a second one stays fair: same discount share
  const r2 = await S.removeOrderPhoto({ ...who, index: 1, n: 1 }, null, null);
  assert.equal(r2.packSize, 18);
  assert.equal(r2.saved, 2.12);
  assert.equal(db.get("orders/o1").pricing.total, 42.4);

  // shipping charges only the new total
  net.handlers["POST /v1/payment_intents/pi_1/capture"] = (p) => ({ id: "pi_1", status: "succeeded", amount_received: Number(p.amount_to_capture) });
  const pay = require("../payments");
  const cur = db.get("orders/o1");
  const c = await pay.captureOrder(db.collection("orders").doc("o1"), "o1", cur, { by: "test" });
  assert.equal(c.amount, 42.4);
  assert.equal(net.calls.find((x) => x.path === "/v1/payment_intents/pi_1/capture").params.amount_to_capture, "4240");
});

test("removing a photo from an order already charged refunds the difference", async () => {
  const { S, db, net } = setup();
  const o = db.get("orders/o1"); o.payment = { state: "captured" }; db.docs.set("orders/o1", o);
  net.handlers["POST /v1/refunds"] = (p) => ({ id: "re_1", amount: Number(p.amount), payment_intent: p.payment_intent, status: "succeeded", created: 1760000000, metadata: { reason: p["metadata[reason]"], note: p["metadata[note]"], by: p["metadata[by]"] } });
  const r = await S.removeOrderPhoto({ ...who, index: 1, n: 20 }, null, null);
  assert.deepEqual([r.held, r.refunded, r.saved], [false, 2.12, 2.12]);
  const after = db.get("orders/o1");
  assert.equal(after.pricing.total, 46.64);       // what was charged stays; the refund records the difference
  assert.equal(after.refundedTotal, 2.12);
  assert.equal(after.items[1].packSize, 19);
  assert.equal(net.calls.find((c) => c.path === "/v1/refunds").params.amount, "212");
});

test("photos can't be removed from packs that repeat photos, the last photo, or once it is being made", async () => {
  const { S, db } = setup();
  const o = db.get("orders/o1");
  o.items.push({ kind: "photos", title: "Custom photo magnets (pack of 4)", packSize: 4, qty: 1, price: 14, photos: [{ path: "uploads/u1/p4/1.jpg", frame: "none" }, { path: "uploads/u1/p4/2.jpg", frame: "none" }] });
  o.items.push({ kind: "photos", title: "Custom photo magnets (1)", packSize: 1, qty: 1, price: 4, photos: [{ path: "uploads/u1/p1/1.jpg", frame: "none" }] });
  db.docs.set("orders/o1", o);
  await assert.rejects(S.removeOrderPhoto({ ...who, index: 2, n: 1 }, null, null), /repeats your photos/);
  await assert.rejects(S.removeOrderPhoto({ ...who, index: 3, n: 1 }, null, null), /last photo/);
  const made = setup({ status: "in_production" });
  await assert.rejects(made.S.removeOrderPhoto({ ...who, index: 1, n: 1 }, null, null), /already started making/);
});

test("the owners' email for a removed photo", () => {
  const E = require("../emails");
  const r = E.render("admin_photo_swap", { order: { number: "LHH-1004", name: "Camila Reis" }, swap: { n: 2, removed: true, saved: 2.12, held: true, newSize: 19, rebuilt: true } });
  assert.match(r.subject, /Photo removed LHH-1004: Camila Reis took out photo 2/);
  assert.match(r.text, /\$2\.12 less/);
});
