"use strict";
/* The site's sale on TikTok (tiktok-promotions.js): one part for the whole sale and one for each special day, never in
   the past, ended parts dropped. */
const test = require("node:test");
const assert = require("node:assert/strict");
const P = require("../tiktok-promotions");

const SALE = { name: "Black Friday", start: "2026-11-20T05:00:00Z", end: "2026-12-01T05:00:00Z", pct: 20,
  days: [{ name: "Black Friday", start: "2026-11-27T05:00:00Z", end: "2026-11-28T05:00:00Z", pct: 30, freeShipping: true }] };

test("parts: the long sale starts now when it already began, the special day keeps its own time", () => {
  const now = Date.parse("2026-11-21T20:00:00Z");
  const p = P.parts(SALE, now);
  assert.equal(p.length, 2);
  assert.equal(p[0].pct, 20);
  assert.equal(p[0].begin, Math.floor(now / 1000) + 120);
  assert.equal(p[0].end, Date.parse(SALE.end) / 1000);
  assert.equal(p[1].pct, 30);
  assert.equal(p[1].begin, Date.parse("2026-11-27T05:00:00Z") / 1000);
});

test("parts: a day that is over is dropped; no sale, nothing", () => {
  const p = P.parts(SALE, Date.parse("2026-11-29T12:00:00Z"));
  assert.deepEqual(p.map((x) => x.pct), [20]);
  assert.deepEqual(P.parts(null, Date.now()), []);
  assert.deepEqual(P.parts(SALE, Date.parse("2026-12-02T00:00:00Z")), []);
});
