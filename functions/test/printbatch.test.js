"use strict";
/* "Print together" (Hive Admin, Orders): several orders share the magnet sheets, each piece labelled with its order;
   logo magnets only when the owner asks for them; one PDF with every packing slip. */
const test = require("node:test");
const assert = require("node:assert/strict");
const { FakeDB, FakeAuth, FakeBucket } = require("./fakes");
const deps = require("../deps");
const P = require("../printsheet");

const ADMIN = { uid: "admin1", token: { admin: true, email: "owner@lhh.com" } };
const design = (n) => ({ kind: "design", id: "fall/x", collection: "fall", title: "X", qty: n, unit: 5 });

test("planBatch: 4 + 5 magnets fit on one sheet; 4 + 6 take two and leave 8 empty spaces; no logo magnets unless asked", () => {
  const a = { id: "a", order: { number: "LHH-1001", items: [design(4)] } };
  const b = { id: "b", order: { number: "LHH-1002", items: [design(5)] } };
  const c = { id: "c", order: { number: "LHH-1003", items: [design(6)] } };
  let p = P.planBatch([a, b]);
  assert.equal(p.sheets, 1);
  assert.equal(p.spaces, 0);
  assert.equal(p.logos, 0);
  assert.deepEqual(p.tiles.map((t) => t.label), [...Array(4).fill("LHH-1001"), ...Array(5).fill("LHH-1002")]);
  p = P.planBatch([a, c]);
  assert.equal(p.sheets, 2);
  assert.equal(p.spaces, 8);
  assert.ok(!p.tiles.some((t) => t.label === "Logo"), "the empty spaces stay empty");
  p = P.planBatch([a, c], { logos: 1, logoStyle: "honey" });
  assert.equal(p.logos, 1);
  assert.equal(p.spaces, 7);
  const logo = p.tiles[p.tiles.length - 1];
  assert.equal(logo.collection, "_shop");
  assert.equal(logo.slug, "logo-honey");
  assert.equal(logo.border, "#F2A81D");
  assert.equal(P.planBatch([], { logos: 9 }).sheets, 1, "a sheet of logo magnets only");
  assert.equal(P.planBatch([], { logos: 999 }).logos, P.MAX_LOGOS);
});

test("adminPrintBatch saves both PDFs and returns links; paid orders only; admins only", async () => {
  process.env.ADMIN_EMAILS = "owner@lhh.com";
  const db = new FakeDB(), bucket = new FakeBucket();
  deps.set({ db, auth: new FakeAuth(), bucket, getDownloadURL: async (f) => `https://dl.example/${f.name}` });
  db.docs.set("orders/a", { number: "LHH-1001", status: "paid", paidAt: "2026-11-05T10:00:00Z", items: [design(4)] });
  db.docs.set("orders/b", { number: "LHH-1002", status: "in_production", paidAt: "2026-11-04T10:00:00Z", items: [design(5)] });
  db.docs.set("orders/p", { number: "LHH-1003", status: "pending", items: [design(2)] });
  let seen = null;
  P.setBatchBuilder(async (entries, opts) => {
    seen = { numbers: entries.map((e) => e.order.number), opts };
    const plan = P.planBatch(entries, opts);
    return { pdf: Buffer.from("%PDF fake"), slip: Buffer.from("%PDF slips"), pages: plan.sheets, sheets: plan.sheets, perPage: 9, tiles: plan.tiles.length, spaces: plan.spaces, logos: plan.logos, numbers: plan.numbers, warnings: [] };
  });
  const A = require("../admin");
  const r = await A.adminPrintBatch({ orderIds: ["a", "b"], logos: 2 }, ADMIN);
  assert.deepEqual(seen.numbers, ["LHH-1002", "LHH-1001"], "oldest first");
  assert.equal(seen.opts.logos, 2);
  assert.equal(seen.opts.logoStyle, "cream");
  assert.equal(r.sheets, 2);
  assert.equal(r.tiles, 11);
  assert.ok(r.url && r.slipUrl);
  const saved = [...bucket.files.keys()].filter((k) => k.startsWith("orders/_batches/"));
  assert.equal(saved.length, 2);
  await assert.rejects(A.adminPrintBatch({ orderIds: ["a", "p"] }, ADMIN), /hasn't been paid/);
  await assert.rejects(A.adminPrintBatch({ orderIds: [] }, ADMIN), /at least one order/);
  await assert.rejects(A.adminPrintBatch({ orderIds: ["a"] }, { uid: "x", token: {} }));
  P.setBatchBuilder(null);
});
