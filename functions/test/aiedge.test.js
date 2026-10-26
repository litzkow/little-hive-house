"use strict";
/* The AI edge for photos (aiedge.js): the request, the cache, the failures. */
const test = require("node:test");
const assert = require("node:assert/strict");
const { FakeBucket } = require("./fakes");
const deps = require("../deps");
const AI = require("../aiedge");

test("fields: only the missing strips, kept in range; low creativity; PNG back", () => {
  assert.deepEqual(AI.fields({ l: 120, t: 0, r: 119.6, b: -5 }), { left: "120", right: "120", up: "0", down: "0", creativity: AI.CREATIVITY, prompt: AI.PROMPT, output_format: "png" });
  assert.equal(AI.fields({ l: 5000 }).left, "2000");
});

test("cacheKey: same photo and same ask = same key; anything different = a new one", () => {
  const a = Buffer.from("photo-a"), b = Buffer.from("photo-b");
  assert.equal(AI.cacheKey(a, { x: 1 }), AI.cacheKey(Buffer.from("photo-a"), { x: 1 }));
  assert.notEqual(AI.cacheKey(a, { x: 1 }), AI.cacheKey(b, { x: 1 }));
  assert.notEqual(AI.cacheKey(a, { x: 1 }), AI.cacheKey(a, { x: 2 }));
});

test("outpaint: posts the photo with the key, keeps the result, never pays twice for the same edge", async () => {
  const bucket = new FakeBucket();
  deps.set({ bucket });
  process.env.STABILITY_API_KEY = "sk-test";
  const calls = [];
  const png = Buffer.alloc(500, 3);
  const fetchImpl = async (url, init) => {
    calls.push({ url, init, left: init.body.get("left"), right: init.body.get("right"), image: init.body.get("image") });
    return { ok: true, status: 200, arrayBuffer: async () => png.buffer.slice(png.byteOffset, png.byteOffset + png.length) };
  };
  try {
    const out = await AI.outpaint(Buffer.from("in"), { l: 120, r: 120 }, { key: "k1", fetchImpl });
    assert.deepEqual(out, png);
    assert.equal(calls.length, 1);
    assert.equal(calls[0].url, AI.ENDPOINT);
    assert.equal(calls[0].init.headers.Authorization, "Bearer sk-test");
    assert.equal(calls[0].init.headers.Accept, "image/*");
    assert.equal(calls[0].left, "120");
    assert.ok(calls[0].image);
    assert.ok(bucket.files.has("print-cache/edges/k1.png"));
    await AI.outpaint(Buffer.from("in"), { l: 120, r: 120 }, { key: "k1", fetchImpl });
    assert.equal(calls.length, 1, "the second time comes from Storage");
    // errors say what is wrong
    const bad = (status) => async () => ({ ok: false, status, text: async () => "nope" });
    await assert.rejects(AI.outpaint(Buffer.from("x"), { l: 1 }, { key: "k2", fetchImpl: bad(402) }), /no credits/);
    await assert.rejects(AI.outpaint(Buffer.from("x"), { l: 1 }, { key: "k3", fetchImpl: bad(401) }), /key is wrong/);
    delete process.env.STABILITY_API_KEY;
    assert.equal(AI.configured(), false);
    await assert.rejects(AI.outpaint(Buffer.from("x"), { l: 1 }, { key: "k4", fetchImpl }), /STABILITY_API_KEY/);
  } finally { delete process.env.STABILITY_API_KEY; }
});
