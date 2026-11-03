"use strict";
/* Customer photos (privacy page): 1 year when they are in a paid order, 30 days when they never became an order. */
const test = require("node:test");
const assert = require("node:assert/strict");
const { FakeDB, FakeAuth, FakeBucket } = require("./fakes");
const deps = require("../deps");

test("ordered photos stay a year, unordered ones go after 30 days, with their small copies", async () => {
  const db = new FakeDB(), bucket = new FakeBucket(), now = Date.parse("2026-11-03T12:00:00Z"), day = 86400000;
  deps.set({ db, auth: new FakeAuth(), bucket });
  const ago = (d) => new Date(now - d * day).toISOString();
  const put = (p, d) => bucket.files.set(p, { data: Buffer.from("x"), created: ago(d) });
  db.docs.set("orders/paid1", { status: "delivered", paidAt: ago(200), items: [{ kind: "photos", photos: [{ path: "uploads/u1/p1/1.jpg" }, { path: "uploads/u1/p1/2.heic" }] }] });
  db.docs.set("orders/old", { status: "delivered", paidAt: ago(380), items: [{ kind: "photos", photos: [{ path: "uploads/u3/p3/1.jpg" }] }] });
  db.docs.set("orders/left", { status: "pending", paidAt: null, items: [{ kind: "photos", photos: [{ path: "uploads/u2/p2/1.jpg" }] }] });
  put("uploads/u1/p1/1.jpg", 201); put("uploads/u1/p1/2.heic", 201); put("thumbs/uploads/u1/p1/2.jpg", 100);   // paid 200 days ago: stay
  put("uploads/u3/p3/1.jpg", 381); put("thumbs/uploads/u3/p3/1.jpg", 300);                                         // paid 380 days ago: go
  put("uploads/u2/p2/1.jpg", 31); put("thumbs/uploads/u2/p2/1.jpg", 31);                                           // checkout never paid: go
  put("uploads/u4/p4/1.jpg", 10);                                                                                  // 10 days, no order yet: stays
  put("orders/o1/print-sheet.pdf", 200); put("orders/o2/print-sheet.pdf", 370);
  put("returns/r1/1.jpg", 100); put("tests/last.json", 900);
  const r = await require("../scheduled").deletePhotos(now);
  assert.deepEqual([...bucket.files.keys()].sort(), [
    "orders/o1/print-sheet.pdf", "returns/r1/1.jpg", "tests/last.json", "thumbs/uploads/u1/p1/2.jpg",
    "uploads/u1/p1/1.jpg", "uploads/u1/p1/2.heic", "uploads/u4/p4/1.jpg"]);
  assert.equal(r.deleted, 5);
});
