"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const { verifyWebhook, signPayload, encode } = require("../stripe");

const SECRET = "whsec_test_123";
const body = JSON.stringify({ id: "evt_1", type: "checkout.session.completed", data: { object: { id: "cs_1" } } });
const now = 1760000000;

test("valid signature returns the event (string and Buffer bodies)", () => {
  const h = signPayload(body, SECRET, now);
  assert.equal(verifyWebhook(body, h, SECRET, { now }).id, "evt_1");
  assert.equal(verifyWebhook(Buffer.from(body), h, SECRET, { now: now + 299 }).type, "checkout.session.completed");
});

test("any of several v1 signatures may match (secret rotation)", () => {
  const good = signPayload(body, SECRET, now).split("v1=")[1];
  const h = `t=${now},v1=${"0".repeat(64)},v1=${good}`;
  assert.equal(verifyWebhook(body, h, SECRET, { now }).id, "evt_1");
});

test("tampered body is rejected", () => {
  const h = signPayload(body, SECRET, now);
  assert.throws(() => verifyWebhook(body.replace("cs_1", "cs_2"), h, SECRET, { now }), /does not match/);
  assert.throws(() => verifyWebhook(body + " ", h, SECRET, { now }), /does not match/);
});

test("wrong secret is rejected", () => {
  const h = signPayload(body, "whsec_other", now);
  assert.throws(() => verifyWebhook(body, h, SECRET, { now }), /does not match/);
});

test("empty or missing secret is always rejected, even with a matching empty-key signature", () => {
  const h = signPayload(body, "", now);
  for (const s of ["", "   ", undefined, null]) assert.throws(() => verifyWebhook(body, h, s, { now }), /secret/);
});

test("old (and far future) timestamps are rejected", () => {
  const h = signPayload(body, SECRET, now - 301);
  assert.throws(() => verifyWebhook(body, h, SECRET, { now }), /too old/);
  const f = signPayload(body, SECRET, now + 301);
  assert.throws(() => verifyWebhook(body, f, SECRET, { now }), /too old/);
});

test("malformed headers are rejected", () => {
  for (const h of [undefined, "", "garbage", `t=${now}`, "v1=abc", `t=abc,v1=${"a".repeat(64)}`, `t=${now},v1=short`]) {
    assert.throws(() => verifyWebhook(body, h, SECRET, { now }));
  }
});

test("timestamp in the signed payload matters (replaying with a new t fails)", () => {
  const sig = signPayload(body, SECRET, now).split("v1=")[1];
  assert.throws(() => verifyWebhook(body, `t=${now + 1},v1=${sig}`, SECRET, { now }), /does not match/);
});

test("Stripe form encoding of nested params", () => {
  const s = encode({ a: 1, b: { c: "x y", d: [{ e: 2 }, { e: 3 }] }, skip: undefined, n: null, ok: true }).join("&");
  assert.equal(decodeURIComponent(s), "a=1&b[c]=x y&b[d][0][e]=2&b[d][1][e]=3&ok=true");
});
