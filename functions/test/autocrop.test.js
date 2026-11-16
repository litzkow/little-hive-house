"use strict";
/* Automatic framing (autocrop.js): faces found by Vision decide where the window sits; customer-placed photos are never
   touched; any failure leaves the order as it was. Real case: order LHH-1003 (15 Nov 2026) had heads cut. */
const test = require("node:test");
const assert = require("node:assert/strict");
const { FakeDB } = require("./fakes");
const deps = require("../deps");
const A = require("../autocrop");
const Crop = require("../crop");

const SQUARE = [0, 0, 600, 600];
test("pick: a face cut at the top of a portrait photo slides the window up, with headroom", () => {
  // LHH-1003 photo 1: 2880x5120, face at 14%..39% of the height
  const c = A.pick(2880, 5120, SQUARE, [{ x: 0.25, y: 0.14, w: 0.35, h: 0.25 }]);
  assert.ok(c && c.y < 0.5);
  const r = Crop.region(2880, 5120, 600, 600, c);
  assert.ok(r.top / 5120 <= 0.14 - 0.25 * 0.3, "room above the face");
});
test("pick: no faces, or people already well placed: no change; otherwise every face stays inside", () => {
  assert.equal(A.pick(3000, 4000, SQUARE, []), null, "no faces: no change");
  assert.equal(A.pick(3000, 4000, SQUARE, [{ x: 0.4, y: 0.34, w: 0.2, h: 0.15 }]), null, "already where it would go");
  for (let y = 0; y <= 0.8; y += 0.05) {
    const f = { x: 0.35, y, w: 0.3, h: 0.18 };
    const c = A.pick(3000, 4000, SQUARE, [f]);
    const r = Crop.region(3000, 4000, 600, 600, c);
    assert.ok(f.y * 4000 >= r.top - 1 && (f.y + f.h) * 4000 <= r.top + r.height + 1, `face at ${y.toFixed(2)} kept`);
  }
});
test("pick: kids sitting low in the photo: the window slides down to show their legs (LHH-1003 photo 3)", () => {
  const faces = [{ x: 0.66, y: 0.59, w: 0.07, h: 0.06 }, { x: 0.28, y: 0.6, w: 0.09, h: 0.08 }, { x: 0.48, y: 0.49, w: 0.08, h: 0.07 }];
  const c = A.pick(3840, 5120, SQUARE, faces);
  assert.ok(c && c.y > 0.55, "slides down for the legs");
});
test("pick: a landscape photo slides sideways to the people; a framed window (instant print) uses its own shape", () => {
  const c = A.pick(4000, 3000, SQUARE, [{ x: 0.02, y: 0.3, w: 0.12, h: 0.16 }]);
  assert.ok(c && c.x < 0.5);
  const inst = A.pick(3000, 4000, [52, 50, 496, 414], [{ x: 0.3, y: 0.03, w: 0.3, h: 0.2 }]);
  assert.ok(inst && inst.y < 0.5);
});

function order(photos) {
  return { number: "LHH-1099", items: [{ kind: "design", id: "x" }, { kind: "photos", packSize: photos.length, photos }] };
}
function vision(facesByPath) {
  let calls = 0;
  A._set({ token: async () => "tok", fetch: async (url, opt) => {
    calls++;
    const path = JSON.parse(opt.body).requests[0].image.content;
    const faces = facesByPath[Buffer.from(path, "base64").toString()] || [];
    return { ok: true, json: async () => ({ responses: [{ faceAnnotations: faces.map((f) => ({ detectionConfidence: 0.9,
      fdBoundingPoly: { vertices: [{ x: f[0], y: f[1] }, { x: f[0] + f[2], y: f[1] }, { x: f[0] + f[2], y: f[1] + f[3] }, { x: f[0], y: f[1] + f[3] }] } })) }] }) };
  } });
  return () => calls;
}
const prepareImpl = async (path) => ({ buffer: Buffer.from(path), width: 1200, height: 1600 });

test("tryOrder: frames the photos the customer didn't place, keeps the ones they did, saves autoCrop", async () => {
  const db = new FakeDB(); deps.set({ db });
  const ref = db.collection("orders").doc("o1");
  const o = order([
    { path: "uploads/u/p/1.jpg", frame: "none" },                                   // head cut at the top
    { path: "uploads/u/p/2.jpg", frame: "none", crop: { x: 0.5, y: 0.2, z: 1.5 } }, // customer placed it
    { path: "uploads/u/p/3.jpg", frame: "none" },                                   // fine as it is
  ]);
  await ref.set(o);
  const calls = vision({ "uploads/u/p/1.jpg": [[480, 120, 260, 300]], "uploads/u/p/3.jpg": [[500, 569, 200, 220]] });
  const out = await A.tryOrder(ref, o, { prepareImpl });
  const saved = db.get("orders/o1");
  const ph = saved.items[1].photos;
  assert.ok(ph[0].crop && ph[0].crop.y < 0.5 && ph[0].autoCrop && ph[0].autoCrop.from === null, "photo 1 reframed, the customer's framing (centred) kept for undo");
  assert.deepEqual(ph[1].crop, { x: 0.5, y: 0.2, z: 1.5 }, "the customer's own framing is never touched");
  assert.equal(ph[1].autoCrop, undefined);
  assert.equal(ph[2].crop, undefined, "a photo that already fits stays centred");
  assert.deepEqual(saved.autoCrop.photos, [1]);
  assert.equal(calls(), 2, "only the 2 photos without a crop were checked");
  assert.equal(out.items[1].photos[0].crop.y, ph[0].crop.y, "the updated order goes on to the print sheet");
});

test("tryOrder: Vision not enabled (403) or anything failing leaves the order as it was, without throwing", async () => {
  const db = new FakeDB(); deps.set({ db });
  const ref = db.collection("orders").doc("o2");
  const o = order([{ path: "uploads/u/p/1.jpg", frame: "none" }]);
  await ref.set(o);
  A._set({ token: async () => "tok", fetch: async () => ({ ok: false, status: 403, json: async () => ({ error: { message: "Cloud Vision API has not been used" } }) }) });
  const out = await A.tryOrder(ref, o, { prepareImpl });
  assert.equal(out, o);
  assert.equal(db.get("orders/o2").autoCrop, undefined);
  A._set({ token: async () => { throw new Error("no metadata server"); } });
  assert.equal(await A.tryOrder(ref, o, { prepareImpl }), o);
});

test("adminPhotoFraming: the owners can put back the customer's framing and bring the automatic one back", async () => {
  const db = new FakeDB();
  deps.set({ db });
  const admin = require("../admin");
  const ADMIN = { uid: "a1", token: { admin: true, email: "owner@lhh.com" } };
  const auto = { x: 0.5, y: 0.31, z: 1 };
  await db.collection("orders").doc("o9").set({
    number: "LHH-9", printSheet: { v: 4, path: "orders/o9/print-sheet.pdf" },
    items: [{ kind: "design", id: "d1" }, { kind: "photos", packSize: 4, photos: [{ path: "a.jpg" }, { path: "b.jpg", crop: auto, autoCrop: { from: null } }] }],
  });
  await assert.rejects(admin.adminPhotoFraming({ orderId: "o9", pack: 0, photo: 1, use: "customer" }, { uid: "x", token: {} }), (e) => e.code === "permission-denied");
  await assert.rejects(admin.adminPhotoFraming({ orderId: "o9", pack: 0, photo: 0, use: "customer" }, ADMIN), (e) => e.code === "failed-precondition", "not framed automatically");
  let r = await admin.adminPhotoFraming({ orderId: "o9", pack: 0, photo: 1, use: "customer" }, ADMIN);
  assert.equal(r.crop, null);
  let o = (await db.collection("orders").doc("o9").get()).data(), p = o.items[1].photos[1];
  assert.equal(p.crop, undefined, "centred again, like the customer left it");
  assert.deepEqual(p.autoCrop.auto, auto);
  assert.equal(p.autoCrop.undone, true);
  assert.equal(o.printSheet.v, 0, "the print sheet is made again");
  assert.equal(o.items[0].id, "d1");
  r = await admin.adminPhotoFraming({ orderId: "o9", pack: 0, photo: 1, use: "auto" }, ADMIN);
  assert.deepEqual(r.crop, auto);
  p = (await db.collection("orders").doc("o9").get()).data().items[1].photos[1];
  assert.deepEqual(p.crop, auto);
  assert.ok(!p.autoCrop.undone);
});
