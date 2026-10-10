"use strict";
/* End-to-end through the handlers with in-memory Firestore/Auth/Storage and a fake Stripe + Resend. */
const test = require("node:test");
const assert = require("node:assert/strict");
const { FakeDB, FakeAuth, FakeBucket, fakeNet } = require("./fakes");
const deps = require("../deps");
const { signPayload } = require("../stripe");

const ENV = {
  STRIPE_SECRET_KEY: "sk_test_x", STRIPE_WEBHOOK_SECRET: "whsec_x", RESEND_API_KEY: "re_x", ADMIN_EMAILS: "owner@lhh.com, karina@lhh.com",
  SITE_URL: "https://littlehivehouse.com", MAIL_FROM: "Little Hive House <hello@littlehivehouse.com>", MAIL_ADMIN: "support@littlehivehouse.com",
};

function setup() {
  Object.assign(process.env, ENV);
  const db = new FakeDB(), auth = new FakeAuth(), bucket = new FakeBucket(), net = fakeNet();
  deps.set({ db, auth, bucket, getDownloadURL: async (f) => `https://dl.example/${f.name}` });
  globalThis.fetch = net.fetch;
  const S = { sessions: {}, refunds: [], n: 0 };
  net.handlers["POST /v1/checkout/sessions"] = (p) => {
    const id = `cs_test_${++S.n}`;
    S.sessions[id] = { params: p, id, url: `https://checkout.stripe.com/c/pay/${id}` };
    return { id, url: S.sessions[id].url };
  };
  net.handlers["GET /v1/checkout/sessions/*"] = (p, u) => {
    const id = decodeURIComponent(u.pathname.split("/").pop());
    const s = S.sessions[id];
    if (!s) { const e = new Error("No such session"); e.status = 404; throw e; }
    return s.full || { id, payment_status: "unpaid", client_reference_id: s.params.client_reference_id };
  };
  net.handlers["POST /v1/refunds"] = (p) => {
    const r = { id: `re_${S.refunds.length + 1}`, amount: Number(p.amount), payment_intent: p.payment_intent, status: "succeeded",
      created: 1760000000, metadata: { reason: p["metadata[reason]"], note: p["metadata[note]"], by: p["metadata[by]"] } };
    S.refunds.push(r);
    return r;
  };
  net.handlers["GET /v1/refunds"] = (p) => ({ data: S.refunds.filter((r) => r.payment_intent === p.payment_intent) });
  net.handlers["GET /v1/promotion_codes/*"] = () => ({ code: "FALL15" });
  net.handlers["GET /v1/promotion_codes"] = () => ({ data: [] });
  return { db, auth, bucket, net, S };
}

/** Pretends the customer paid: fills in the session as Stripe would return it. */
function pay(S, sessionId, { pi = `pi_${sessionId}`, discount = 0, fee = 123, email = "ana@example.com" } = {}) {
  const s = S.sessions[sessionId];
  let total = 0;
  for (let i = 0; s.params[`line_items[${i}][quantity]`]; i++) {
    total += Number(s.params[`line_items[${i}][price_data][unit_amount]`]) * Number(s.params[`line_items[${i}][quantity]`]);
  }
  const ship = Number(s.params["shipping_options[0][shipping_rate_data][fixed_amount][amount]"] || 0);
  s.full = {
    id: sessionId, object: "checkout.session", payment_status: "paid", client_reference_id: s.params.client_reference_id,
    metadata: { orderId: s.params["metadata[orderId]"] }, amount_total: total - discount + ship, customer: "cus_1",
    customer_details: { email, name: "Ana Souza", phone: null, address: { country: "US" } },
    shipping_details: { name: "Ana Souza", address: { line1: "1 Main St", line2: null, city: "Atlanta", state: "GA", postal_code: "30301", country: "US" } },
    total_details: discount ? { amount_discount: discount, breakdown: { discounts: [{ amount: discount, discount: { promotion_code: "promo_1", coupon: { name: "FALL15" } } }] } } : { amount_discount: 0 },
    payment_intent: { id: pi, latest_charge: { id: `ch_${pi}`, balance_transaction: { fee } } },
  };
  return s.full;
}

async function deliver(webhook, event, secret = ENV.STRIPE_WEBHOOK_SECRET) {
  const body = JSON.stringify(event);
  return webhook.handleWebhook(Buffer.from(body), signPayload(body, secret));
}
const evt = (id, type, object) => ({ id, type, created: 1760000000, data: { object } });
const ADMIN = { uid: "admin1", token: { admin: true, email: "owner@lhh.com" } };
const flatSum = (p) => {
  let t = 0;
  for (let i = 0; p[`line_items[${i}][quantity]`]; i++) t += Number(p[`line_items[${i}][price_data][unit_amount]`]) * Number(p[`line_items[${i}][quantity]`]);
  return t;
};

test("checkout → paid → ship → deliver → partial refund → dashboard refund", async () => {
  const { db, net, S } = setup();
  const checkout = require("../checkout"), webhook = require("../webhook"), admin = require("../admin");

  // 7 designs + a team package: bundle (2 groups of 3), 10% off at 19+? no: 7 + 12 = 19 magnets -> no volume
  const cart = [{ kind: "design", id: "places/new-york", qty: 4, price: 0.01 }, { kind: "design", id: "bee-kind/bee-kind", qty: 3 },
    { kind: "package", id: "teams-12", qty: 1 }];
  const r = await checkout.createCheckout({ cart, email: "Ana@Example.com", giftMessage: "For you", marketing: true }, null);
  assert.match(r.url, /^https:\/\/checkout\.stripe\.com/);
  const order0 = db.get(`orders/${r.orderId}`);
  assert.equal(order0.status, "pending");
  assert.equal(order0.number, null);
  assert.equal(order0.email, "ana@example.com");
  assert.equal(order0.pricing.subtotal, 65);
  assert.equal(order0.pricing.bundleDiscount, 6);
  assert.equal(order0.pricing.volumePct, 0);
  assert.equal(order0.pricing.shipping, 0);
  assert.equal(order0.pricing.total, 59);
  const p = S.sessions[order0.stripe.sessionId].params;
  assert.equal(flatSum(p), 5900, "Stripe lines add up to the goods total");
  assert.equal(p.client_reference_id, r.orderId);
  assert.equal(p.allow_promotion_codes, "true");
  assert.equal(p["shipping_address_collection[allowed_countries][1]"], "CA");
  assert.equal(p["shipping_options[0][shipping_rate_data][fixed_amount][amount]"], "0");
  assert.equal(p.success_url, `https://littlehivehouse.com/thank-you.html?order=${r.orderId}&session={CHECKOUT_SESSION_ID}`);
  assert.equal(p.cancel_url, "https://littlehivehouse.com/shop.html?checkout=canceled");
  assert.equal(p.customer_email, "ana@example.com");
  assert.equal(net.calls.find((c) => c.path === "/v1/checkout/sessions").headers["Idempotency-Key"], `checkout-${r.orderId}`);

  // the customer pays with a promo code; Stripe tells us via the webhook
  const sid = order0.stripe.sessionId;
  pay(S, sid, { discount: 500 });
  let res = await deliver(webhook, evt("evt_1", "checkout.session.completed", { id: sid }));
  assert.equal(res.status, 200);
  let o = db.get(`orders/${r.orderId}`);
  assert.equal(o.status, "paid");
  assert.equal(o.number, "LHH-1001");
  assert.equal(o.stripe.fee, 1.23);
  assert.equal(o.stripe.paymentIntent, `pi_${sid}`);
  assert.deepEqual(o.pricing.promo, { code: "FALL15", amount: 5 });
  assert.equal(o.pricing.total, 54);
  assert.equal(o.shipping.address.city, "Atlanta");
  assert.equal(o.adminNotes.length, 0, "amount check passes");
  assert.ok(o.emails.confirmation);
  assert.deepEqual(net.emails.map((e) => e.to[0]), ["ana@example.com", "support@littlehivehouse.com"]);
  assert.ok(db.get("subscribers/ana@example.com"), "marketing consent subscribes");

  // same event again (Stripe retry) and the thank-you page racing the webhook: nothing changes, no new email
  res = await deliver(webhook, evt("evt_1", "checkout.session.completed", { id: sid }));
  assert.equal(res.body, "duplicate");
  res = await deliver(webhook, evt("evt_1b", "checkout.session.completed", { id: sid }));
  assert.equal(res.status, 200);
  assert.equal(net.emails.length, 2);
  assert.equal(db.get(`orders/${r.orderId}`).number, "LHH-1001");

  // thank-you page and guest tracking
  const view = await checkout.orderBySession({ orderId: r.orderId, sessionId: sid }, null, { ip: "1.1.1.1", headers: {} });
  assert.equal(view.number, "LHH-1001");
  assert.ok(!("email" in view) && !("stripe" in view));
  await assert.rejects(checkout.orderBySession({ orderId: r.orderId, sessionId: "cs_test_999" }, null, { ip: "1.1.1.1", headers: {} }), (e) => e.code === "not-found");
  const t = await checkout.trackOrder({ number: "lhh 1001", email: " ANA@example.com " }, null, { ip: "2.2.2.2", headers: {} });
  assert.equal(t.status, "paid");
  await assert.rejects(checkout.trackOrder({ number: "LHH-1001", email: "someone@else.com" }, null, { ip: "2.2.2.2", headers: {} }), (e) => e.code === "not-found");

  // a second order gets the next number
  const r2 = await checkout.createCheckout({ cart: [{ kind: "design", id: "places/chicago", qty: 1 }] }, null);
  const sid2 = db.get(`orders/${r2.orderId}`).stripe.sessionId;
  assert.equal(S.sessions[sid2].params["shipping_options[0][shipping_rate_data][fixed_amount][amount]"], "495");
  pay(S, sid2, { email: "bo@example.com" });
  // the thank-you page arrives before the webhook: it confirms the payment itself
  const v2 = await checkout.orderBySession({ orderId: r2.orderId, sessionId: sid2 }, null, { ip: "1.1.1.1", headers: {} });
  assert.equal(v2.number, "LHH-1002");
  assert.equal(db.get(`orders/${r2.orderId}`).email, "bo@example.com");
  assert.equal(db.get("meta/counters").orderNumber, 1002);

  // fulfil
  await admin.adminSetStatus({ orderId: r.orderId, status: "in_production", note: "printing tonight" }, ADMIN);
  o = db.get(`orders/${r.orderId}`);
  assert.equal(o.status, "in_production");
  assert.equal(o.adminNotes[0].text, "printing tonight");
  await assert.rejects(admin.adminSetStatus({ orderId: r.orderId, status: "canceled" }, ADMIN), (e) => e.code === "failed-precondition" && /Refund/.test(e.message));
  await assert.rejects(admin.adminShip({ orderId: r.orderId, carrier: "pigeon", tracking: "1" }, ADMIN), (e) => e.code === "invalid-argument");
  const ship = await admin.adminShip({ orderId: r.orderId, carrier: "usps", tracking: "9400 1234", labelCost: "4.75" }, ADMIN);
  assert.match(ship.url, /usps\.com.*94001234/);
  o = db.get(`orders/${r.orderId}`);
  assert.equal(o.status, "shipped");
  assert.equal(o.fulfillment.labelCost, 4.75);
  assert.ok(o.fulfillment.shippedAt && o.emails.shipped);
  await admin.adminMarkDelivered({ orderId: r.orderId }, ADMIN);
  o = db.get(`orders/${r.orderId}`);
  assert.equal(o.status, "delivered");
  assert.ok(o.fulfillment.deliveredAt && o.emails.delivered);

  // partial refund from the admin page
  const before = net.emails.length;
  await assert.rejects(admin.adminRefund({ orderId: r.orderId, amount: 54.01, reason: "damaged" }, ADMIN), (e) => e.code === "failed-precondition" && /at most \$54\.00/.test(e.message));
  const rf = await admin.adminRefund({ orderId: r.orderId, amount: 10, reason: "damaged", note: "2 cracked" }, ADMIN);
  assert.equal(rf.status, "partially_refunded");
  assert.equal(rf.refundedTotal, 10);
  const call = net.calls.filter((c) => c.path === "/v1/refunds" && c.method === "POST").pop();
  assert.equal(call.params.amount, "1000");
  assert.equal(call.params["metadata[reason]"], "damaged");
  assert.equal(call.params.reason, "requested_by_customer");
  assert.ok(call.headers["Idempotency-Key"]);
  assert.equal(net.emails.length, before + 1, "one refund email");

  // Stripe then sends charge.refunded for it (no new email), and later the owner refunds $4 in the Stripe dashboard
  await deliver(webhook, evt("evt_r1", "charge.refunded", { id: "ch_1", payment_intent: `pi_${sid}` }));
  assert.equal(net.emails.length, before + 1);
  S.refunds.push({ id: "re_dash", amount: 400, payment_intent: `pi_${sid}`, status: "succeeded", created: 1760000500, metadata: {} });
  await deliver(webhook, evt("evt_r2", "charge.refunded", { id: "ch_1", payment_intent: `pi_${sid}` }));
  o = db.get(`orders/${r.orderId}`);
  assert.equal(o.refunds.length, 2);
  assert.equal(o.refundedTotal, 14);
  assert.equal(o.refunds[1].by, "stripe-dashboard");
  assert.equal(o.status, "partially_refunded");
  assert.equal(net.emails.length, before + 2);
  assert.equal(o.emails.refund.length, 2);

  // refund the rest -> refunded; nothing left to refund
  const rest = await admin.adminRefund({ orderId: r.orderId, amount: 40, reason: "other" }, ADMIN);
  assert.equal(rest.status, "refunded");
  await assert.rejects(admin.adminRefund({ orderId: r.orderId, amount: 1, reason: "other" }, ADMIN), (e) => e.code === "failed-precondition");
  assertTemplated(net.emails);
});

/** Every email went through functions/emails (not the plain fallback mail.js uses when a template throws). */
function assertTemplated(emails) {
  for (const e of emails) assert.ok(!/^<pre/.test(e.html) && e.text && e.subject, `fallback used for "${e.subject}"`);
}

test("webhook rejects bad signatures and ignores unrelated events", async () => {
  setup();
  const webhook = require("../webhook");
  const e = evt("evt_x", "checkout.session.completed", { id: "cs_test_1" });
  assert.equal((await deliver(webhook, e, "whsec_wrong")).status, 400);
  const body = JSON.stringify(e);
  assert.equal((await webhook.handleWebhook(Buffer.from(body + " "), signPayload(body, ENV.STRIPE_WEBHOOK_SECRET))).status, 400);
  assert.equal((await deliver(webhook, evt("evt_y", "customer.created", {}))).body, "ignored");
});

test("a failing handler releases the event so Stripe's retry runs it again", async () => {
  const { db, S } = setup();
  const checkout = require("../checkout"), webhook = require("../webhook");
  const r = await checkout.createCheckout({ cart: [{ kind: "design", id: "places/chicago", qty: 1 }] }, null);
  const sid = db.get(`orders/${r.orderId}`).stripe.sessionId;
  // Stripe GET fails the first time (session not filled in -> our fake 404s for unknown id)
  const ev = evt("evt_fail", "checkout.session.completed", { id: "cs_unknown" });
  assert.equal((await deliver(webhook, ev)).status, 500);
  assert.equal(db.get("stripeEvents/evt_fail"), undefined);
  pay(S, sid);
  const ok = evt("evt_fail", "checkout.session.completed", { id: sid });
  assert.equal((await deliver(webhook, ok)).status, 200);
  assert.equal(db.get(`orders/${r.orderId}`).status, "paid");
});

test("photo packs: sign-in, own paths and finished uploads are required", async () => {
  const { db, bucket, S } = setup();
  const checkout = require("../checkout"), admin = require("../admin");
  const anon = { uid: "anonA", token: { firebase: { sign_in_provider: "anonymous" } } };
  const pack = (p) => [{ kind: "photos", packSize: 4, qty: 1, notes: "hi", photos: [{ path: p, frame: "instant", caption: "Summer 2026" }] }];
  await assert.rejects(checkout.createCheckout({ cart: pack("uploads/anonA/custom-1/1.jpg") }, null), (e) => e.code === "unauthenticated");
  await assert.rejects(checkout.createCheckout({ cart: pack("uploads/someoneElse/custom-1/1.jpg") }, anon), (e) => e.code === "invalid-argument");
  await assert.rejects(checkout.createCheckout({ cart: pack("uploads/anonA/custom-1/1.gif") }, anon), (e) => e.code === "invalid-argument");
  await assert.rejects(checkout.createCheckout({ cart: pack("uploads/anonA/custom-1/1.jpg") }, anon), (e) => e.code === "failed-precondition" && /Photo 1/.test(e.message));
  bucket.files.set("uploads/anonA/custom-1/1.jpg", {});
  const r = await checkout.createCheckout({ cart: pack("uploads/anonA/custom-1/1.jpg") }, anon);
  const o = db.get(`orders/${r.orderId}`);
  assert.equal(o.uid, null);
  assert.equal(o.guestUid, "anonA");
  assert.equal(o.items[0].photos[0].caption, "Summer 2026");
  assert.equal(flatSum(S.sessions[o.stripe.sessionId].params), 1400);
  const urls = await admin.adminPhotoUrls({ orderId: r.orderId }, ADMIN);
  assert.equal(urls.packs[0].photos[0].url, "https://dl.example/uploads/anonA/custom-1/1.jpg");
  assert.equal(urls.packs[0].photos[0].frame, "instant");
});

test("Stripe failure removes the pending order and explains", async () => {
  const { db, net } = setup();
  net.handlers["POST /v1/checkout/sessions"] = () => { const e = new Error("Invalid API Key provided"); e.status = 401; throw e; };
  const checkout = require("../checkout");
  await assert.rejects(checkout.createCheckout({ cart: [{ kind: "design", id: "places/chicago", qty: 1 }] }, null),
    (e) => e.code === "failed-precondition" && /STRIPE_SECRET_KEY/.test(e.message));
  assert.equal([...db.docs.keys()].filter((k) => k.startsWith("orders/")).length, 0);
});

test("expired checkout: one reminder, only with marketing consent", async () => {
  const { db, net } = setup();
  const checkout = require("../checkout"), webhook = require("../webhook");
  const yes = await checkout.createCheckout({ cart: [{ kind: "design", id: "places/chicago", qty: 1 }], email: "a@x.com", marketing: true }, null);
  const no = await checkout.createCheckout({ cart: [{ kind: "design", id: "places/chicago", qty: 1 }], email: "b@x.com" }, null);
  await deliver(webhook, evt("evt_e1", "checkout.session.expired", { id: "cs", client_reference_id: yes.orderId }));
  await deliver(webhook, evt("evt_e2", "checkout.session.expired", { id: "cs", client_reference_id: yes.orderId }));
  await deliver(webhook, evt("evt_e3", "checkout.session.expired", { id: "cs", client_reference_id: no.orderId }));
  assert.deepEqual(net.emails.map((e) => e.to[0]), ["a@x.com"]);
  assert.ok(net.emails[0].headers["List-Unsubscribe"]);
  assert.equal(db.get(`orders/${yes.orderId}`).status, "pending");
  assert.ok(db.get(`orders/${no.orderId}`).abandonedAt);
});

test("dispute flags the order and alerts the shop once", async () => {
  const { db, net, S } = setup();
  const checkout = require("../checkout"), webhook = require("../webhook");
  const r = await checkout.createCheckout({ cart: [{ kind: "design", id: "places/chicago", qty: 1 }] }, null);
  const sid = db.get(`orders/${r.orderId}`).stripe.sessionId;
  pay(S, sid, { pi: "pi_d" });
  await deliver(webhook, evt("evt_p", "checkout.session.completed", { id: sid }));
  const n = net.emails.length;
  const d = { id: "dp_1", payment_intent: "pi_d", reason: "fraudulent", amount: 995, status: "needs_response" };
  await deliver(webhook, evt("evt_d1", "charge.dispute.created", d));
  await deliver(webhook, evt("evt_d2", "charge.dispute.created", d));
  const o = db.get(`orders/${r.orderId}`);
  assert.equal(o.dispute.id, "dp_1");
  assert.equal(net.emails.length, n + 1);
  assert.equal(net.emails[n].to[0], "support@littlehivehouse.com");
  assertTemplated(net.emails);
});

test("claimAdmin: listed email + (verified or password sign-in) only", async () => {
  const { auth } = setup();
  const admin = require("../admin");
  auth.users.set("u1", { uid: "u1", customClaims: { other: 1 } });
  await assert.rejects(admin.claimAdmin({}, { uid: "u1", token: { email: "nope@x.com", email_verified: true, firebase: { sign_in_provider: "password" } } }), (e) => e.code === "permission-denied");
  await assert.rejects(admin.claimAdmin({}, { uid: "u1", token: { email: "karina@lhh.com", email_verified: false, firebase: { sign_in_provider: "google.com" } } }), (e) => e.code === "permission-denied");
  await assert.rejects(admin.claimAdmin({}, { uid: "u1", token: { firebase: { sign_in_provider: "anonymous" } } }), (e) => e.code === "unauthenticated");
  const r = await admin.claimAdmin({}, { uid: "u1", token: { email: "Karina@lhh.com", email_verified: false, firebase: { sign_in_provider: "password" } } });
  assert.equal(r.admin, true);
  assert.deepEqual(auth.users.get("u1").customClaims, { other: 1, admin: true });
});

test("custom payment link: pending custom order, link emailed, paid via client_reference_id", async () => {
  const { db, net, S } = setup();
  net.handlers["POST /v1/prices"] = () => ({ id: "price_1" });
  net.handlers["POST /v1/payment_links"] = () => ({ id: "plink_1", url: "https://buy.stripe.com/test_1" });
  const admin = require("../admin"), webhook = require("../webhook");
  const r = await admin.adminCreatePaymentLink({ title: "200 wedding magnets", amount: 310.5, email: "bride@x.com", note: "Proof approved" }, ADMIN);
  assert.equal(r.url, `https://buy.stripe.com/test_1?client_reference_id=${r.orderId}&prefilled_email=bride%40x.com`);
  const o = db.get(`orders/${r.orderId}`);
  assert.equal(o.items[0].kind, "custom");
  assert.equal(o.pricing.total, 310.5);
  assert.equal(net.emails[0].to[0], "bride@x.com");
  const pl = net.calls.find((c) => c.path === "/v1/payment_links").params;
  assert.equal(pl["restrictions[completed_sessions][limit]"], "1");
  // completed through the link
  S.sessions.cs_link = { params: {}, full: { id: "cs_link", payment_status: "paid", client_reference_id: r.orderId, payment_link: "plink_1", amount_total: 31050,
    customer_details: { email: "bride@x.com", name: "Bea" }, shipping_details: { name: "Bea", address: { city: "Macon", state: "GA", country: "US" } },
    total_details: { amount_discount: 0 }, payment_intent: { id: "pi_link", latest_charge: { balance_transaction: { fee: 931 } } } } };
  await deliver(webhook, evt("evt_l", "checkout.session.completed", { id: "cs_link" }));
  const paid = db.get(`orders/${r.orderId}`);
  assert.equal(paid.status, "paid");
  assert.equal(paid.number, "LHH-1001");
  assert.equal(paid.stripe.fee, 9.31);
  assertTemplated(net.emails);
});

test("public forms: subscribe once, contact, quote, reset, welcome, unsubscribe, review", async () => {
  const { db, net, auth } = setup();
  const pub = require("../public"), mail = require("../mail"), checkout = require("../checkout");
  const req = { ip: "9.9.9.9", headers: {} };
  assert.equal((await pub.subscribe({ email: "Fan@x.com", source: "footer" }, null, req)).already, false);
  assert.equal((await pub.subscribe({ email: "fan@x.com" }, null, req)).already, true);
  assert.equal(net.emails.length, 1);
  await assert.rejects(pub.subscribe({ email: "not-an-email" }, null, req), (e) => e.code === "invalid-argument");

  await pub.contact({ name: "Jo", email: "jo@x.com", message: "Hi!", topic: "Order" }, null, req);
  assert.equal(net.emails.slice(-2)[0].reply_to, "jo@x.com");
  await pub.requestQuote({ name: "Jo", email: "jo@x.com", occasion: "Weddings", quantity: "150", message: "Gold" }, null, req);
  assert.equal([...db.docs.keys()].filter((k) => k.startsWith("quotes/")).length, 1);

  auth.users.set("u9", { uid: "u9", email: "jo@x.com" });
  assert.deepEqual(await pub.sendPasswordReset({ email: "jo@x.com" }, null, req), { ok: true });
  assert.match(net.emails.at(-1).text + net.emails.at(-1).html, /oobCode/);
  const count = net.emails.length;
  assert.deepEqual(await pub.sendPasswordReset({ email: "ghost@x.com" }, null, req), { ok: true });
  assert.equal(net.emails.length, count, "no email and no hint for unknown accounts");

  const user = { uid: "u9", token: { email: "jo@x.com", email_verified: true, name: "Jo Lee", firebase: { sign_in_provider: "password" } } };
  assert.equal((await pub.welcome({ marketing: true }, user)).welcomed, true);
  assert.equal((await pub.welcome({}, user)).welcomed, false);
  assert.equal(db.get("users/u9").marketing, true);

  await assert.rejects(pub.unsubscribe({ e: "jo@x.com", t: "0".repeat(32) }), (e) => e.code === "permission-denied");
  await pub.unsubscribe({ e: "jo@x.com", t: mail.unsubscribeToken("jo@x.com") });
  assert.equal(db.get("users/u9").marketing, false);
  assert.equal(db.get("subscribers/jo@x.com").unsubscribed, true);

  // reviews: buyers only, items in the order only
  const r = await checkout.createCheckout({ cart: [{ kind: "design", id: "places/chicago", qty: 1 }] }, user);
  const o = db.get(`orders/${r.orderId}`);
  assert.equal(o.uid, "u9");
  await assert.rejects(pub.submitReview({ orderId: r.orderId, designId: "places/chicago", rating: 5 }, user), (e) => e.code === "failed-precondition");
  db._update(`orders/${r.orderId}`, { status: "delivered" });
  await assert.rejects(pub.submitReview({ orderId: r.orderId, designId: "places/boston", rating: 5 }, user), (e) => e.code === "invalid-argument");
  await assert.rejects(pub.submitReview({ orderId: r.orderId, designId: "places/chicago", rating: 5 }, { uid: "zz", token: { email: "z@x.com", firebase: { sign_in_provider: "password" } } }), (e) => e.code === "permission-denied");
  await assert.rejects(pub.submitReview({ orderId: r.orderId, designId: "places/chicago", rating: 6 }, user), (e) => e.code === "invalid-argument");
  const rv = await pub.submitReview({ orderId: r.orderId, designId: "places/chicago", rating: 5, text: "Love it" }, user);
  const doc = db.get(`reviews/${rv.id}`);
  assert.equal(doc.status, "pending");
  assert.equal(doc.name, "Jo L.");
  const admin = require("../admin");
  await admin.adminModerateReview({ id: rv.id, status: "published" }, ADMIN);
  assert.equal(db.get(`reviews/${rv.id}`).status, "published");
  assertTemplated(net.emails);
});

test("settings and promos", async () => {
  const { db, net } = setup();
  const admin = require("../admin");
  const s = await admin.adminSaveSettings({ magnetUnitCost: "0.6", stripePct: 2.9, junk: 5 }, ADMIN);
  assert.equal(s.settings.magnetUnitCost, 0.6);
  assert.equal(s.settings.packagingCost, 0.6);
  assert.equal(db.get("settings/store").junk, undefined);
  await assert.rejects(admin.adminSaveSettings({ magnetUnitCost: -1 }, ADMIN), (e) => e.code === "invalid-argument");

  net.handlers["POST /v1/coupons"] = (p) => ({ id: "co_1", percent_off: Number(p.percent_off) });
  net.handlers["POST /v1/promotion_codes"] = (p) => ({ id: "promo_9", code: p.code, active: true, coupon: p.coupon, max_redemptions: Number(p.max_redemptions) });
  const pr = await admin.adminCreatePromo({ code: "welcome10", percentOff: 10, maxRedemptions: 100 }, ADMIN);
  assert.equal(pr.promo.code, "WELCOME10");
  assert.equal(pr.promo.percentOff, 10);
  await assert.rejects(admin.adminCreatePromo({ code: "X1", percentOff: 10 }, ADMIN), (e) => e.code === "invalid-argument");
  await assert.rejects(admin.adminCreatePromo({ code: "BOTH", percentOff: 10, amountOff: 5 }, ADMIN), (e) => e.code === "invalid-argument");
  net.handlers["GET /v1/promotion_codes"] = () => ({ data: [{ id: "promo_9", code: "WELCOME10", active: true, coupon: { percent_off: 10 }, times_redeemed: 3 }] });
  const list = await admin.adminListPromos({}, ADMIN);
  assert.equal(list.promos[0].timesRedeemed, 3);
  await assert.rejects(admin.adminCreatePromo({ code: "WELCOME10", percentOff: 10 }, ADMIN), (e) => e.code === "already-exists");
});

test("daily delivery check emails the shop only when something is late", async () => {
  const { db, net } = setup();
  const { deliveredFollowUp } = require("../scheduled");
  assert.deepEqual(await deliveredFollowUp(), { late: 0 });
  assert.equal(net.emails.length, 0);
  db._set("orders/o1", { status: "shipped", number: "LHH-1001", name: "Ana", email: "a@x.com",
    fulfillment: { carrier: "usps", tracking: "9400", url: "https://tools.usps.com/x", shippedAt: new Date(Date.now() - 12 * 86400000).toISOString() } });
  db._set("orders/o2", { status: "shipped", number: "LHH-1002", fulfillment: { shippedAt: new Date().toISOString() } });
  assert.deepEqual(await deliveredFollowUp(), { late: 1 });
  assert.equal(net.emails[0].to[0], "support@littlehivehouse.com");
  assert.match(net.emails[0].text, /LHH-1001/);
  assertTemplated(net.emails);
});
