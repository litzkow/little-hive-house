"use strict";
/* Problems customers hit on the site (clientlog.js): saved without personal data, the serious ones emailed and pushed
   to the owners at most once per kind every 3 hours, junk and floods refused. Also the createCheckout rate limit. */
const test = require("node:test");
const assert = require("node:assert/strict");
const { FakeDB, FakeAuth, FakeBucket, fakeNet } = require("./fakes");
const deps = require("../deps");
const push = require("../push");

function setup() {
  Object.assign(process.env, { STRIPE_SECRET_KEY: "sk_test_x", RESEND_API_KEY: "re_x", ADMIN_EMAILS: "owner@lhh.com", SITE_URL: "https://littlehivehouse.com", MAIL_ADMIN: "support@littlehivehouse.com" });
  const db = new FakeDB(), net = fakeNet();
  deps.set({ db, auth: new FakeAuth(), bucket: new FakeBucket(), getDownloadURL: async () => null });
  globalThis.fetch = net.fetch;
  push.resetCache();
  const pushed = [];
  push.setSender(async (sub, payload) => { pushed.push(JSON.parse(payload)); return { statusCode: 201 }; });
  return { db, net, pushed };
}
const all = (db, coll) => [...db.docs.entries()].filter(([k]) => k.startsWith(coll + "/")).map(([, v]) => v);

test("a checkout failure is saved, emailed and pushed to the owners in Portuguese; private bits of the link are dropped", async () => {
  const { db, net, pushed } = setup();
  await db.collection("adminPush").doc("p1").set({ endpoint: "https://web.push.apple.com/x", keys: { p256dh: "B".repeat(87), auth: "a".repeat(22) }, uid: "admin1", prefs: {} });
  const C = require("../clientlog");
  const r = await C.handle(JSON.stringify({ kind: "checkout_failed", msg: "Your connection dropped while uploading photos.", code: "storage/retry-limit-exceeded",
    page: "https://littlehivehouse.com/thank-you.html?order=abc123&session=cs_live_secret", lang: "pt", ua: "iPhone", photos: 9 }), "1.2.3.4");
  assert.equal(r.status, 204);
  const saved = all(db, "clientErrors");
  assert.equal(saved.length, 1);
  assert.equal(saved[0].kind, "checkout_failed");
  assert.equal(saved[0].photos, 9);
  assert.ok(!/abc123|cs_live_secret/.test(saved[0].page), saved[0].page);
  assert.ok(!JSON.stringify(saved[0]).includes("1.2.3.4"), "no IP stored");
  assert.equal(net.emails.length, 1);
  assert.match(net.emails[0].subject, /pagamento não abriu/);
  assert.equal(pushed.length, 1);
  assert.match(pushed[0].title, /pagamento/);
});

test("alerts are throttled: one email per kind every 3 hours, the next one says how many happened", async () => {
  const { db, net } = setup();
  const C = require("../clientlog");
  for (let i = 0; i < 5; i++) await C.handle({ kind: "upload_failed", msg: "x" }, "9.9.9." + i);
  assert.equal(all(db, "clientErrors").length, 5);
  assert.equal(net.emails.length, 1);
  // three hours later
  const st = db.get("meta/clientAlerts");
  st.upload_failed.sentAt = new Date(Date.now() - 4 * 3600e3).toISOString();
  await db.collection("meta").doc("clientAlerts").set(st);
  await C.handle({ kind: "upload_failed", msg: "y" }, "9.9.9.9");
  assert.equal(net.emails.length, 2);
  assert.match(net.emails[1].subject, /5 vezes/);
  // a plain JS error is only saved
  await C.handle({ kind: "js_error", msg: "TypeError" }, "8.8.8.8");
  assert.equal(net.emails.length, 2);
});

test("junk is refused and one IP can't flood the log", async () => {
  const { db } = setup();
  const C = require("../clientlog");
  assert.equal((await C.handle("not json", "5.5.5.5")).status, 400);
  assert.equal((await C.handle({ kind: "drop_tables" }, "5.5.5.5")).status, 400);
  assert.equal((await C.handle("x".repeat(9000), "5.5.5.5")).status, 400);
  let last;
  for (let i = 0; i < 45; i++) last = await C.handle({ kind: "js_error", msg: "e" + i }, "6.6.6.6");
  assert.equal(last.status, 429);
  assert.equal(all(db, "clientErrors").length, 40);
});

test("createCheckout: a script calling it over and over is stopped (each call makes an order and a Stripe session)", async () => {
  const { net } = setup();
  let n = 0;
  net.handlers["POST /v1/checkout/sessions"] = () => ({ id: `cs_test_${++n}`, url: `https://checkout.stripe.com/c/pay/cs_test_${n}` });
  const checkout = require("../checkout");
  const cart = [{ kind: "design", id: Object.keys(require("../pricing").loadCatalog().designs)[0], qty: 1 }];
  const raw = { ip: "4.4.4.4", headers: {} };
  let err = null;
  for (let i = 0; i < 31 && !err; i++) {
    try { await checkout.createCheckout({ cart }, null, raw); } catch (e) { err = e; }
  }
  assert.ok(err, "the 31st call is refused");
  assert.equal(n, 30, "30 real tries went through first");
  assert.equal(err.code, "resource-exhausted", err.message);
});
