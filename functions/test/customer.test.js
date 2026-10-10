"use strict";
/* myOrders / myOrder (customers never read orders directly), guest-order linking and the email-confirmation flow. */
const test = require("node:test");
const assert = require("node:assert/strict");
const { FakeDB, FakeAuth, FakeBucket, fakeNet } = require("./fakes");
const deps = require("../deps");

const ENV = { RESEND_API_KEY: "re_x", SITE_URL: "https://littlehivehouse.com", MAIL_ADMIN: "support@littlehivehouse.com" };
function setup() {
  Object.assign(process.env, ENV);
  delete process.env.STRIPE_SECRET_KEY;
  const db = new FakeDB(), auth = new FakeAuth(), net = fakeNet();
  deps.set({ db, auth, bucket: new FakeBucket() });
  globalThis.fetch = net.fetch;
  const order = (id, o) => db._set(`orders/${id}`, {
    number: "LHH-1000", status: "paid", items: [{ kind: "design", id: "places/chicago", title: "Chicago", collection: "places", qty: 1, unit: 5 }],
    pricing: { subtotal: 5, shipping: 4.95, total: 9.95, currency: "usd" }, createdAt: "2026-10-01T00:00:00.000Z", paidAt: o.createdAt || "2026-10-01T00:00:00.000Z",
    shipping: { name: "Jo Lee", phone: "+1 555", address: { line1: "1 Main St", line2: "", city: "Macon", state: "GA", postal_code: "31201", country: "US" } },
    giftMessage: "For mom", adminNotes: [{ at: "x", by: "owner@x.com", text: "INTERNAL" }], stripe: { paymentIntent: "pi_secret", fee: 0.59 },
    fulfillment: { carrier: "usps", tracking: "9400", labelCost: 4.5, shippedAt: null }, timeline: [], ...o,
  });
  return { db, auth, net, order };
}
const jo = (verified, uid = "uJo") => ({ uid, token: { email: "Jo@X.com", email_verified: verified, name: "Jo Lee", firebase: { sign_in_provider: "password" } } });

test("myOrders: own orders + this browser's guest orders; guest orders by email only once the email is verified", async () => {
  const { order } = setup();
  const C = require("../customer");
  order("mine", { uid: "uJo", email: "jo@x.com", number: "LHH-1001", createdAt: "2026-10-01T00:00:00.000Z" });
  order("guestSameBrowser", { uid: null, guestUid: "uJo", email: "other-typo@x.com", number: "LHH-1002", createdAt: "2026-10-02T00:00:00.000Z" });
  order("guestByEmail", { uid: null, email: "jo@x.com", number: "LHH-1003", createdAt: "2026-10-03T00:00:00.000Z", paidAt: "2026-10-03T00:00:00.000Z" });
  order("pending", { uid: "uJo", email: "jo@x.com", status: "pending", number: null });
  order("someoneElses", { uid: "uAna", email: "jo@x.com", number: "LHH-1004" });
  order("strangerGuest", { uid: null, email: "ana@x.com", number: "LHH-1005" });

  let r = await C.myOrders({}, jo(false));
  assert.deepEqual(r.orders.map((o) => o.id), ["guestSameBrowser", "mine"]);
  r = await C.myOrders({}, jo(true));
  assert.deepEqual(r.orders.map((o) => o.id), ["guestByEmail", "guestSameBrowser", "mine"], "newest first, no pending, nobody else's");
  const v = r.orders[2];
  const json = JSON.stringify(r);
  for (const secret of ["INTERNAL", "owner@x.com", "pi_secret", "0.59", "labelCost", "uJo", "jo@x.com", "+1 555"]) assert.ok(!json.includes(secret), `leaked ${secret}`);
  assert.equal(v.shipping.address.line1, "1 Main St", "the owner sees their own address");
  assert.equal(v.giftMessage, "For mom");
  assert.equal(v.fulfillment.tracking, "9400");
  assert.ok(!("labelCost" in v.fulfillment));
});

test("myOrder: one order, same rules; everything else is not-found", async () => {
  const { order } = setup();
  const C = require("../customer");
  order("mine", { uid: "uJo", email: "jo@x.com" });
  order("guestByEmail", { uid: null, email: "jo@x.com" });
  order("someoneElses", { uid: "uAna", email: "jo@x.com" });
  order("pending", { uid: "uJo", status: "pending" });
  assert.equal((await C.myOrder({ id: "mine" }, jo(false))).id, "mine");
  for (const id of ["guestByEmail", "someoneElses", "pending", "nope", "../x", ""]) {
    await assert.rejects(C.myOrder({ id }, jo(false)), (e) => e.code === "not-found" || e.code === "invalid-argument", id);
  }
  assert.equal((await C.myOrder({ id: "guestByEmail" }, jo(true))).id, "guestByEmail");
  await assert.rejects(C.myOrder({ id: "someoneElses" }, jo(true)), (e) => e.code === "not-found" && /track it with your order number/.test(e.message));
});

test("sign-up: welcome sends the confirm-email once; after verification welcome links guest orders", async () => {
  const { db, auth, net, order } = setup();
  const pub = require("../public"), C = require("../customer");
  order("g1", { uid: null, email: "jo@x.com" });
  order("g2", { uid: null, email: "JO@x.com".toLowerCase(), status: "delivered" });
  order("taken", { uid: "uAna", email: "jo@x.com" });

  const w1 = await pub.welcome({ name: "Jo Lee" }, jo(false));
  assert.equal(w1.verifySent, true);
  assert.equal(w1.linked, 0);
  const kinds = net.emails.map((e) => e.subject);
  assert.equal(net.emails.length, 2, "welcome + confirm email");
  const verify = net.emails.find((e) => /confirm your email/i.test(e.subject));
  assert.ok(verify, kinds.join(" | "));
  assert.match(verify.html, /mode=verifyEmail/);
  assert.equal(auth.verifyLinks[0].email, "jo@x.com");
  assert.equal(auth.verifyLinks[0].settings.url, "https://littlehivehouse.com/account.html?verified=1");
  assert.ok(!/^<pre/.test(verify.html));
  assert.ok(db.get("users/uJo").verifySentAt);
  await pub.welcome({}, jo(false));
  assert.equal(net.emails.length, 2, "nothing sent twice");
  assert.equal(db.get("orders/g1").uid, null, "not linked before verification");

  // resend button: works while unverified, rate-limited, no-op once verified
  assert.deepEqual(await C.sendVerifyEmail({}, jo(false)), { ok: true });
  assert.equal(net.emails.length, 3);
  for (let i = 0; i < 3; i++) await C.sendVerifyEmail({}, jo(false));
  await assert.rejects(C.sendVerifyEmail({}, jo(false)), (e) => e.code === "resource-exhausted");
  assert.deepEqual(await C.sendVerifyEmail({}, jo(true)), { ok: true, already: true });

  const w2 = await pub.welcome({}, jo(true));
  assert.equal(w2.linked, 2);
  assert.equal(db.get("orders/g1").uid, "uJo");
  assert.ok(db.get("orders/g1").linkedAt);
  assert.equal(db.get("orders/g2").uid, "uJo");
  assert.equal(db.get("orders/taken").uid, "uAna", "someone else's order stays theirs");
  assert.equal((await pub.welcome({}, jo(true))).linked, 0, "already linked");
  // linked orders now show up even before a fresh token says verified
  assert.deepEqual((await C.myOrders({}, jo(false))).orders.map((o) => o.id).sort(), ["g1", "g2"]);
});

test("sendVerifyEmail explains when email isn't set up", async () => {
  setup();
  delete process.env.RESEND_API_KEY;
  const C = require("../customer");
  await assert.rejects(C.sendVerifyEmail({}, jo(false, "uX")), (e) => e.code === "failed-precondition");
});
