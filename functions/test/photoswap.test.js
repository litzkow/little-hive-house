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
  Object.assign(process.env, { RESEND_API_KEY: "re_x", SITE_URL: "https://littlehivehouse.com", MAIL_FROM: "Little Hive House <hello@littlehivehouse.com>", MAIL_ADMIN: "support@littlehivehouse.com" });
  const db = new FakeDB(), net = fakeNet(), bucket = new FakeBucket();
  deps.set({ db, auth: new FakeAuth(), bucket });
  globalThis.fetch = net.fetch;
  const photos = Array.from({ length: 20 }, (_, n) => ({ path: `uploads/u1/pack-20/${n + 1}.jpg`, frame: n < 2 ? "polaroid" : "none", caption: n === 1 ? "Mom" : "", crop: { x: 0.5, y: 0.5, z: 1 } }));
  photos.forEach((p) => withThumb(bucket, p.path));
  db.docs.set("orders/o1", {
    number: "LHH-1004", email: "camila@example.com", name: "Camila Reis", status, uid: "u1",
    items: [
      { kind: "design", id: "fall/pumpkin", title: "Pumpkin", collection: "fall", qty: 1, unit: 5 },
      { kind: "photos", title: "Custom photo magnets (20)", packSize: 20, qty: 1, price: 31.4, photos },
    ],
    pricing: { subtotal: 36.4, shipping: 0, tax: 0, total: 36.4, currency: "usd" },
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
  assert.equal(o.pricing.total, 36.4);
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
