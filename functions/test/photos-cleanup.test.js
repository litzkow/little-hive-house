"use strict";
/* Customer photos are deleted 90 days after upload (privacy page), with their small copies and the print sheets. */
const test = require("node:test");
const assert = require("node:assert/strict");
const { FakeDB, FakeAuth, FakeBucket } = require("./fakes");
const deps = require("../deps");

test("photos older than 90 days go; newer ones and the shop's own files stay", async () => {
  const bucket = new FakeBucket(), now = Date.parse("2026-11-03T12:00:00Z");
  deps.set({ db: new FakeDB(), auth: new FakeAuth(), bucket });
  const put = (p, daysAgo) => bucket.files.set(p, { data: Buffer.from("x"), created: new Date(now - daysAgo * 86400000).toISOString() });
  put("uploads/u1/p1/1.jpg", 91); put("uploads/u1/p1/2.jpg", 120); put("thumbs/uploads/u1/p1/1.jpg", 91);
  put("orders/o1/print-sheet.pdf", 95); put("uploads/u2/p2/1.jpg", 30); put("orders/o2/print-sheet.pdf", 10); put("tests/last.json", 400);
  const r = await require("../scheduled").deletePhotos(now);
  assert.equal(r.deleted, 4);
  assert.deepEqual([...bucket.files.keys()].sort(), ["orders/o2/print-sheet.pdf", "tests/last.json", "uploads/u2/p2/1.jpg"]);
});
