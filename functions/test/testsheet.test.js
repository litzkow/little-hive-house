"use strict";
/* Test sheets without an order, and deleting test orders. */
const test = require("node:test");
const assert = require("node:assert/strict");
const { FakeDB, FakeAuth, FakeBucket, fakeNet } = require("./fakes");
const deps = require("../deps");
const P = require("../printsheet");

const ADMIN = { uid: "admin1", token: { admin: true, email: "owner@lhh.com" } };
function setup() {
  Object.assign(process.env, { STRIPE_SECRET_KEY: "sk_test_x", RESEND_API_KEY: "re_x", ADMIN_EMAILS: "owner@lhh.com", SITE_URL: "https://littlehivehouse.com" });
  const db = new FakeDB(), bucket = new FakeBucket(), net = fakeNet();
  deps.set({ db, auth: new FakeAuth(), bucket, getDownloadURL: async () => null });
  globalThis.fetch = net.fetch;
  return { db, bucket };
}

test("deletable: free, test-mode, unpaid or never-charged orders only; never one with money or a live card hold", () => {
  const A = require("../admin");
  assert.equal(A.deletable({ pricing: { total: 0 }, status: "paid", paidAt: "x" }), true, "free with a 100% coupon");
  assert.equal(A.deletable({ pricing: { total: 20 }, stripe: { sessionId: "cs_test_1" }, status: "paid" }), true);
  assert.equal(A.deletable({ pricing: { total: 20 }, status: "pending" }), true);
  assert.equal(A.deletable({ pricing: { total: 20 }, status: "paid", paidAt: "x", payment: { state: "captured" } }), false);
  assert.equal(A.deletable({ pricing: { total: 20 }, status: "paid", paidAt: "x", payment: { state: "authorized" } }), false);
  assert.equal(A.deletable({ pricing: { total: 20 }, status: "canceled", paidAt: "x", payment: { state: "released" } }), true);
  assert.equal(A.deletable({ pricing: { total: 20 }, status: "shipped", paidAt: "x" }), false, "an old paid order");
});

test("adminDeleteOrder: confirm, admins only, removes the order and its print files", async () => {
  const { db, bucket } = setup();
  const A = require("../admin");
  await db.collection("orders").doc("free1").set({ number: "LHH-1005", pricing: { total: 0 }, status: "paid", paidAt: "2026-10-20T00:00:00Z" });
  await db.collection("orders").doc("real1").set({ number: "LHH-1006", pricing: { total: 30 }, status: "paid", paidAt: "2026-10-20T00:00:00Z", payment: { state: "captured" } });
  await bucket.file("orders/free1/print-sheet.pdf").save(Buffer.from("x"), {});
  await assert.rejects(A.adminDeleteOrder({ orderId: "free1" }, ADMIN), /confirm/);
  await assert.rejects(A.adminDeleteOrder({ orderId: "free1", confirm: "DELETE" }, { uid: "u", token: {} }), (e) => e.code === "permission-denied");
  await assert.rejects(A.adminDeleteOrder({ orderId: "real1", confirm: "DELETE" }, ADMIN), /Only test orders/);
  const r = await A.adminDeleteOrder({ orderId: "free1", confirm: "DELETE" }, ADMIN);
  assert.equal(r.deleted, "LHH-1005");
  assert.equal(db.get("orders/free1"), undefined);
  assert.ok(db.get("orders/real1"));
});

test("adminTestSheet: designs and photos into a PDF without an order", async () => {
  const { bucket } = setup();
  const A = require("../admin");
  let seen = null;
  P.setBuilder(null);
  const real = P.buildPrintSheetDetailed;
  // stand-in for sharp/pdfkit: check what would be printed
  const orig = P.buildPrintSheetDetailed;
  P.buildPrintSheetDetailed = async (id, order, opts) => { seen = { order, opts, photo: await opts.readPhoto("test/1.jpg") }; return { pdf: Buffer.from("%PDF-1.5 test"), sheets: 1, tiles: 4, warnings: [] }; };
  try {
    await assert.rejects(A.adminTestSheet({}, ADMIN), /at least one/);
    await assert.rejects(A.adminTestSheet({ designs: [{ id: "nope/nope" }] }, ADMIN), /Unknown design/);
    await assert.rejects(A.adminTestSheet({ designs: [{ id: "places/new-york", qty: 30 }] }, ADMIN), /holds up to 27/);
    const png = Buffer.alloc(200, 7).toString("base64");
    const r = await A.adminTestSheet({ designs: [{ id: "places/new-york", qty: 2 }], photos: [{ data: "data:image/jpeg;base64," + png, frame: "instant", caption: "Hi", capStyle: "classic", qty: 2 }] }, ADMIN);
    assert.equal(r.ok, true);
    assert.equal(seen.order.number, "TEST");
    assert.deepEqual(seen.order.items.map((i) => i.kind), ["design", "photos"]);
    assert.deepEqual(seen.order.items[1].photos[0], { path: "test/1.jpg", frame: "instant", caption: "Hi", capStyle: "classic" });
    assert.equal(seen.photo.length, 200);
    assert.ok(bucket.files.has("tests/test-sheet.pdf"));
  } finally { P.buildPrintSheetDetailed = orig; void real; }
});

test("the last test sheet is saved and can be made again from Storage without picking the photos again", async () => {
  const { bucket } = setup();
  const A = require("../admin");
  const orig = P.buildPrintSheetDetailed;
  let seen = null;
  let seenOpts = null;
  P.buildPrintSheetDetailed = async (id, order, opts) => { seenOpts = opts; seen = { order, photo: await opts.readPhoto("test/1.jpg") }; return { pdf: Buffer.from("%PDF-1.5 test"), sheets: 1, tiles: 3, warnings: [] }; };
  try {
    assert.deepEqual(await A.adminLastTestSheet({}, ADMIN), { sheet: null, pdfUrl: null });
    await assert.rejects(A.adminLastTestSheet({}, { uid: "u", token: {} }), (e) => e.code === "permission-denied");
    const jpg = Buffer.alloc(300, 9);
    const r = await A.adminTestSheet({ border: "black", designs: [{ id: "places/new-york", qty: 2 }], photos: [{ data: jpg.toString("base64"), name: "beach.jpg", frame: "instant", caption: "Hi", qty: 1 }] }, ADMIN);
    assert.equal(r.saved, true);
    assert.equal(r.border, "black");
    assert.equal(seenOpts.border, "black");
    assert.ok(bucket.files.has("tests/last/1.jpg") && bucket.files.has("tests/last.json"));
    const last = await A.adminLastTestSheet({}, ADMIN);
    assert.ok(last.pdfUrl);
    assert.equal(last.sheet.designs[0].id, "places/new-york");
    assert.equal(last.sheet.border, "black");
    assert.equal(last.sheet.designs[0].qty, 2);
    assert.equal(last.sheet.photos[0].saved, "tests/last/1.jpg");
    assert.equal(last.sheet.photos[0].name, "beach.jpg");
    assert.equal(last.sheet.photos[0].caption, "Hi");
    assert.ok(last.sheet.photos[0].url);
    // made again: the photo comes from Storage
    seen = null;
    const again = await A.adminTestSheet({ designs: last.sheet.designs, photos: last.sheet.photos.map((p) => ({ saved: p.saved, name: p.name, frame: p.frame, caption: p.caption, qty: p.qty })) }, ADMIN);
    assert.equal(again.ok, true);
    assert.deepEqual(seen.photo, jpg);
    // only its own saved photos can be read back
    await assert.rejects(A.adminTestSheet({ photos: [{ saved: "orders/x/print-sheet.pdf", qty: 1 }] }, ADMIN), /at least one/);
  } finally { P.buildPrintSheetDetailed = orig; }
});
