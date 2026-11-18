"use strict";
/* Meta Conversions API (metaevents.js): a paid site order goes to Meta as Purchase, hashed, with the order number as the
   event_id the browser's Pixel also sends; nothing for GPC, other channels or with no Pixel; a Meta error never throws. */
const test = require("node:test");
const assert = require("node:assert/strict");
const crypto = require("crypto");
const { FakeDB, FakeAuth, FakeBucket } = require("./fakes");
const deps = require("../deps");
const sha = (v) => crypto.createHash("sha256").update(v).digest("hex");
const META = { token: "EAAB" + "x".repeat(60), adAccountId: "act_123", pageId: "999", igUserId: "1784", pixelId: "1824876368823217" };
const ORDER = { number: 1042, source: "site", email: " Ana@Example.com ", uid: "u1", paidAt: "2026-11-18T23:00:00.000Z",
  shipping: { name: "Ana Maria Silva", phone: "(404) 555-0101", address: { city: "Fayetteville", state: "GA", postal_code: "30214-1234", country: "US" } },
  pricing: { total: 17.49 }, items: [{ kind: "design", id: "brasil/saudade", qty: 2 }, { kind: "photos", packSize: 4, qty: 1 }],
  client: { ip: "1.2.3.4", ua: "Mozilla/5.0", fbp: "fb.1.1700000000000.123", fbc: "fb.1.1700000000000.IwAR" } };

function setup(meta) {
  const db = new FakeDB();
  deps.set({ db, auth: new FakeAuth(), bucket: new FakeBucket() });
  if (meta) db.docs.set("ads/auth", { meta });
  const calls = [];
  globalThis.fetch = async (url, init = {}) => {
    calls.push({ url, params: Object.fromEntries(new URLSearchParams(init.body.toString())) });
    return { ok: true, status: 200, json: async () => ({ events_received: 1 }) };
  };
  return { calls, M: require("../metaevents") };
}

test("a paid site order goes to Meta as Purchase: hashed, with the order number as the event_id", async () => {
  const { calls, M } = setup(META);
  const r = await M.purchase(ORDER, "o1");
  assert.equal(r.sent, true);
  assert.match(calls[0].url, /\/1824876368823217\/events$/);
  const ev = JSON.parse(calls[0].params.data)[0];
  assert.equal(ev.event_name, "Purchase"); assert.equal(ev.event_id, "1042"); assert.equal(ev.action_source, "website");
  assert.equal(ev.event_time, Date.parse(ORDER.paidAt) / 1000);
  const u = ev.user_data;
  assert.deepEqual(u.em, [sha("ana@example.com")]);
  assert.deepEqual(u.ph, [sha("14045550101")]);
  assert.deepEqual(u.fn, [sha("ana")]); assert.deepEqual(u.ln, [sha("silva")]);
  assert.deepEqual(u.ct, [sha("fayetteville")]); assert.deepEqual(u.st, [sha("ga")]); assert.deepEqual(u.zp, [sha("30214")]);
  assert.deepEqual(u.country, [sha("us")]); assert.deepEqual(u.external_id, [sha("u1")]);
  assert.equal(u.client_ip_address, "1.2.3.4"); assert.equal(u.fbp, ORDER.client.fbp); assert.equal(u.fbc, ORDER.client.fbc);
  assert.ok(!JSON.stringify(ev).includes("Ana@") && !JSON.stringify(ev).includes("555-0101"));   // nothing in the clear
  assert.deepEqual(ev.custom_data, { currency: "USD", value: 17.49, order_id: "1042", content_type: "product", content_ids: ["brasil/saudade", "photos"], num_items: 3 });
});

test("nothing goes to Meta with Global Privacy Control, for Etsy orders, or without a Pixel; an error never throws", async () => {
  let { calls, M } = setup(META);
  assert.ok((await M.purchase({ ...ORDER, client: { gpc: true } }, "o1")).skipped);
  assert.ok((await M.purchase({ ...ORDER, source: "etsy" }, "o1")).skipped);
  assert.equal(calls.length, 0);
  ({ calls, M } = setup({ ...META, pixelId: "" }));
  assert.ok((await M.purchase(ORDER, "o1")).skipped);
  setup(META);
  globalThis.fetch = async () => { throw new Error("offline"); };
  assert.match((await M.purchase(ORDER, "o1")).error, /offline/);
});
