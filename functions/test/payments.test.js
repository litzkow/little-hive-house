"use strict";
/* Charge on ship (payments.js) and the owners' phone notifications (push.js), through the real handlers with
   in-memory Firestore, a fake Stripe + Resend and a fake Web Push sender. */
const test = require("node:test");
const assert = require("node:assert/strict");
const crypto = require("crypto");
const { FakeDB, FakeAuth, FakeBucket, fakeNet } = require("./fakes");
const deps = require("../deps");
const { signPayload } = require("../stripe");
const printsheet = require("../printsheet");
const push = require("../push");

const ENV = {
  STRIPE_SECRET_KEY: "sk_test_x", STRIPE_WEBHOOK_SECRET: "whsec_x", RESEND_API_KEY: "re_x", ADMIN_EMAILS: "owner@lhh.com",
  SITE_URL: "https://littlehivehouse.com", MAIL_FROM: "Little Hive House <hello@littlehivehouse.com>", MAIL_ADMIN: "support@littlehivehouse.com",
};
const ADMIN = { uid: "admin1", token: { admin: true, email: "owner@lhh.com" } };
const HOLD_END = 1760600000;       // unix seconds

function setup() {
  Object.assign(process.env, ENV);
  delete process.env.CAPTURE;
  const db = new FakeDB(), net = fakeNet();
  deps.set({ db, auth: new FakeAuth(), bucket: new FakeBucket(), getDownloadURL: async (f) => `https://dl.example/${f.name}` });
  globalThis.fetch = net.fetch;
  printsheet.setBuilder(async (orderId) => ({ pdf: Buffer.from(`%PDF fake ${orderId}`), pages: 2, sheets: 1, tiles: 1, warnings: [] }));
  push.resetCache();
  const pushed = [];
  push.setSender(async (sub, payload, opts) => {
    if (sub.endpoint.includes("gone")) { const e = new Error("Gone"); e.statusCode = 410; throw e; }
    pushed.push({ endpoint: sub.endpoint, payload: JSON.parse(payload), opts });
  });
  const S = { sessions: {}, pis: {}, n: 0 };
  net.handlers["POST /v1/checkout/sessions"] = (p) => {
    const id = `cs_test_${++S.n}`;
    S.sessions[id] = { params: p, id, url: `https://checkout.stripe.com/c/pay/${id}` };
    return { id, url: S.sessions[id].url };
  };
  net.handlers["GET /v1/checkout/sessions/*"] = (p, u) => S.sessions[decodeURIComponent(u.pathname.split("/").pop())].full;
  net.handlers["POST /v1/payment_intents/*"] = (p, u) => {
    const [, , , id, action] = u.pathname.split("/");
    const pi = S.pis[id];
    if (action === "capture") {
      if (pi.status !== "requires_capture") { const e = new Error(`This PaymentIntent could not be captured because it has a status of ${pi.status}.`); e.status = 400; throw e; }
      Object.assign(pi, { status: "succeeded", amount_received: pi.amount, latest_charge: { id: `ch_${id}`, balance_transaction: { fee: 87 } } });
    } else if (action === "cancel") {
      Object.assign(pi, { status: "canceled", cancellation_reason: p.cancellation_reason });
    }
    return pi;
  };
  net.handlers["GET /v1/payment_intents/*"] = (p, u) => S.pis[u.pathname.split("/").pop()];
  return { db, net, S, pushed };
}

/** The customer finishes checkout: the card is only authorized (PaymentIntent requires_capture). */
function authorize(S, sessionId, amount = 1495) {
  const s = S.sessions[sessionId];
  const pi = `pi_${sessionId}`;
  S.pis[pi] = { id: pi, status: "requires_capture", amount, amount_received: 0,
    latest_charge: { id: `ch_${pi}`, captured: false, balance_transaction: null, payment_method_details: { card: { capture_before: HOLD_END } } } };
  s.full = {
    id: sessionId, object: "checkout.session", payment_status: "unpaid", status: "complete", client_reference_id: s.params.client_reference_id,
    metadata: { orderId: s.params["metadata[orderId]"] }, amount_total: amount, customer: "cus_1",
    customer_details: { email: "ana@example.com", name: "Ana Souza", address: { country: "US" } },
    shipping_details: { name: "Ana Souza", address: { line1: "1 Main St", city: "Atlanta", state: "GA", postal_code: "30301", country: "US" } },
    total_details: { amount_discount: 0, amount_tax: 0 },
    payment_intent: S.pis[pi],
  };
  return pi;
}
async function deliver(webhook, event) {
  const body = JSON.stringify(event);
  return webhook.handleWebhook(Buffer.from(body), signPayload(body, ENV.STRIPE_WEBHOOK_SECRET));
}
const evt = (id, type, object) => ({ id, type, created: 1760000000, data: { object } });
const CART = [{ kind: "design", id: "places/new-york", qty: 2 }];

async function heldOrder(ctx) {
  const checkout = require("../checkout"), webhook = require("../webhook");
  const r = await checkout.createCheckout({ cart: CART, email: "ana@example.com" }, null);
  const sid = ctx.db.get(`orders/${r.orderId}`).stripe.sessionId;
  const pi = authorize(ctx.S, sid);
  const res = await deliver(webhook, evt(`evt_${sid}`, "checkout.session.completed", { id: sid }));
  assert.equal(res.status, 200);
  return { id: r.orderId, sid, pi };
}
function phone(db, name, prefs) {
  const endpoint = `https://web.push.apple.com/${name}`;
  db._set(`adminPush/${push.subId(endpoint)}`, { endpoint, keys: { p256dh: "x".repeat(87), auth: "y".repeat(22) }, prefs: prefs || {}, uid: "admin1" });
  return endpoint;
}

test("checkout only authorizes the card, with a note on the pay button; CAPTURE=now charges at once", async () => {
  const ctx = setup();
  const checkout = require("../checkout");
  const r = await checkout.createCheckout({ cart: CART, email: "ana@example.com" }, null);
  const p = ctx.S.sessions[ctx.db.get(`orders/${r.orderId}`).stripe.sessionId].params;
  assert.equal(p["payment_intent_data[capture_method]"], "manual");
  assert.match(p["custom_text[submit][message]"], /charged only when your order ships/);
  process.env.CAPTURE = "now";
  const r2 = await checkout.createCheckout({ cart: CART, email: "ana@example.com" }, null);
  const p2 = ctx.S.sessions[ctx.db.get(`orders/${r2.orderId}`).stripe.sessionId].params;
  assert.equal(p2["payment_intent_data[capture_method]"], undefined);
  assert.equal(p2["custom_text[submit][message]"], undefined);
  delete process.env.CAPTURE;
});

test("authorized checkout becomes an order (held card), owners get email + phone notification", async () => {
  const ctx = setup();
  phone(ctx.db, "thiago");
  phone(ctx.db, "karina", { orders: false });
  const { id } = await heldOrder(ctx);
  const o = ctx.db.get(`orders/${id}`);
  assert.equal(o.status, "paid");
  assert.equal(o.number, "LHH-1001");
  assert.equal(o.payment.state, "authorized");
  assert.equal(o.payment.captureBefore, new Date(HOLD_END * 1000).toISOString());
  assert.equal(o.stripe.fee, null, "no fee until it is charged");
  assert.match(o.timeline.pop().text, /charged when your order ships/);
  assert.deepEqual(ctx.net.emails.map((e) => e.to[0]), ["ana@example.com", "support@littlehivehouse.com"]);
  assert.equal(ctx.pushed.length, 1, "Karina switched order alerts off");
  const n = ctx.pushed[0];
  assert.equal(n.endpoint, "https://web.push.apple.com/thiago");
  assert.equal(n.payload.title, "🛒 Novo pedido LHH-1001");
  assert.equal(n.payload.body, "$14.95 · 2 ímãs · Ana Souza");
  assert.equal(n.payload.url, `/admin/#order/${id}`);
  assert.equal(n.opts.urgency, "high");
  assert.equal(n.opts.vapidDetails.subject, "mailto:support@littlehivehouse.com");
});

test("marking shipped charges the card first; Charge now; already charged is a no-op", async () => {
  const ctx = setup();
  const admin = require("../admin");
  const { id, pi } = await heldOrder(ctx);
  const r = await admin.adminShip({ orderId: id, carrier: "usps", tracking: "9400 1000", labelCost: 4.5 }, ADMIN);
  assert.equal(r.charged, true);
  assert.equal(r.chargedAmount, 14.95);
  const cap = ctx.net.calls.find((c) => c.path === `/v1/payment_intents/${pi}/capture`);
  assert.equal(cap.headers["Idempotency-Key"], `capture-${id}`);
  let o = ctx.db.get(`orders/${id}`);
  assert.equal(o.status, "shipped");
  assert.equal(o.payment.state, "captured");
  assert.equal(o.stripe.fee, 0.87);
  assert.match(o.adminNotes.pop().text, /Card charged \$14\.95/);
  // fixing the tracking number later doesn't charge again
  const before = ctx.net.calls.length;
  const r2 = await admin.adminShip({ orderId: id, carrier: "usps", tracking: "9400 2000" }, ADMIN);
  assert.equal(r2.charged, false);
  assert.equal(ctx.net.calls.filter((c, i) => i >= before && /capture/.test(c.path)).length, 0);

  // Charge now on another held order
  const b = await heldOrder(ctx);
  const c = await admin.adminCapture({ orderId: b.id }, ADMIN);
  assert.deepEqual(c, { ok: true, charged: true, amount: 14.95 });
  o = ctx.db.get(`orders/${b.id}`);
  assert.equal(o.payment.state, "captured");
  assert.equal(o.status, "paid", "charging doesn't change the order stage");
  await assert.rejects(admin.adminCapture({ orderId: b.id }, ADMIN), /already been charged/);
});

test("hold ended: shipping is refused, the order is canceled and the owners are told", async () => {
  const ctx = setup();
  phone(ctx.db, "thiago");
  const admin = require("../admin");
  const { id, pi } = await heldOrder(ctx);
  ctx.pushed.length = 0;
  ctx.S.pis[pi].status = "canceled";
  ctx.S.pis[pi].cancellation_reason = "automatic";
  await assert.rejects(admin.adminShip({ orderId: id, carrier: "usps", tracking: "9400" }, ADMIN), /hold on the customer's card has ended/);
  const o = ctx.db.get(`orders/${id}`);
  assert.equal(o.status, "canceled");
  assert.equal(o.payment.state, "expired");
  assert.equal(o.fulfillment, null, "not shipped");
  assert.equal(ctx.pushed.length, 1);
  assert.equal(ctx.pushed[0].payload.title, "❌ Reserva do cartão venceu");
  assert.ok(ctx.net.emails.some((e) => /Card hold expired/.test(e.subject)));
});

test("refund before charging: the full amount releases the hold, part of it is refused", async () => {
  const ctx = setup();
  const admin = require("../admin");
  const { id, pi } = await heldOrder(ctx);
  await assert.rejects(admin.adminRefund({ orderId: id, amount: 5, reason: "changed_mind" }, ADMIN), /hasn't been charged yet/);
  const r = await admin.adminRefund({ orderId: id, amount: 14.95, reason: "changed_mind", note: "Sorry!" }, ADMIN);
  assert.equal(r.released, true);
  assert.equal(r.emailed, true);
  assert.ok(ctx.net.calls.some((c) => c.path === `/v1/payment_intents/${pi}/cancel`));
  assert.ok(!ctx.net.calls.some((c) => c.path === "/v1/refunds"), "nothing was charged, so nothing to refund");
  const o = ctx.db.get(`orders/${id}`);
  assert.equal(o.status, "canceled");
  assert.equal(o.payment.state, "released");
  const mail = ctx.net.emails.pop();
  assert.equal(mail.to[0], "ana@example.com");
  assert.match(mail.text, /never charged/);
});

test("checkHolds warns once two days before the hold ends, then marks it ended", async () => {
  const ctx = setup();
  phone(ctx.db, "thiago");
  phone(ctx.db, "karina", { payments: false });
  const payments = require("../payments");
  const { id, pi } = await heldOrder(ctx);
  ctx.pushed.length = 0;
  const end = HOLD_END * 1000;
  let r = await payments.checkHolds(end - 72 * 3600000);
  assert.deepEqual(r, { held: 1, warned: 0, ended: 0 });
  r = await payments.checkHolds(end - 40 * 3600000);
  assert.equal(r.warned, 1);
  assert.equal(ctx.pushed.length, 1);
  assert.equal(ctx.pushed[0].payload.title, "⏳ Reserva do cartão vencendo");
  assert.match(ctx.pushed[0].payload.body, /LHH-1001: vence em 2 dias/);
  r = await payments.checkHolds(end - 30 * 3600000);
  assert.equal(r.warned, 0, "only once");
  // Stripe still shows it held right after the deadline: wait; then it is canceled
  r = await payments.checkHolds(end + 3600000);
  assert.equal(r.ended, 0);
  ctx.S.pis[pi].status = "canceled";
  r = await payments.checkHolds(end + 3 * 3600000);
  assert.equal(r.ended, 1);
  assert.equal(ctx.db.get(`orders/${id}`).payment.state, "expired");
  r = await payments.checkHolds(end + 5 * 3600000);
  assert.equal(r.held, 0);
});

test("webhook: captured or canceled in the Stripe dashboard updates the order", async () => {
  const ctx = setup();
  const webhook = require("../webhook");
  const a = await heldOrder(ctx);
  Object.assign(ctx.S.pis[a.pi], { status: "succeeded", amount_received: 1495, latest_charge: { id: "ch_a", balance_transaction: { fee: 73 } } });
  let res = await deliver(webhook, evt("evt_cap", "charge.captured", { id: "ch_a", payment_intent: a.pi }));
  assert.equal(res.status, 200);
  let o = ctx.db.get(`orders/${a.id}`);
  assert.equal(o.payment.state, "captured");
  assert.equal(o.stripe.fee, 0.73);
  const b = await heldOrder(ctx);
  res = await deliver(webhook, evt("evt_can", "payment_intent.canceled", { id: b.pi, status: "canceled", cancellation_reason: "automatic" }));
  assert.equal(res.status, 200);
  o = ctx.db.get(`orders/${b.id}`);
  assert.equal(o.status, "canceled");
  assert.equal(o.payment.state, "expired");
  // our own release fires payment_intent.canceled too: an order that is no longer held is left alone
  res = await deliver(webhook, evt("evt_can2", "payment_intent.canceled", { id: b.pi, status: "canceled" }));
  assert.equal(ctx.db.get(`orders/${b.id}`).payment.state, "expired");
});

test("payment links authorize too", async () => {
  const ctx = setup();
  ctx.net.handlers["POST /v1/prices"] = () => ({ id: "price_1" });
  ctx.net.handlers["POST /v1/payment_links"] = () => ({ id: "plink_1", url: "https://buy.stripe.com/x" });
  const admin = require("../admin");
  await admin.adminCreatePaymentLink({ title: "Wedding favors", amount: 120 }, ADMIN);
  const p = ctx.net.calls.find((c) => c.path === "/v1/payment_links").params;
  assert.equal(p["payment_intent_data[capture_method]"], "manual");
  assert.match(p["custom_text[submit][message]"], /charged only when/);
});

test("push: VAPID keys made once and kept server-side; subscribe, prefs, test, unsubscribe, dead phones removed", async () => {
  const ctx = setup();
  await assert.rejects(push.adminPush({ action: "key" }, { uid: "u", token: { email: "x@y.com" } }), /admin/i);
  const k = await push.adminPush({ action: "key" }, ADMIN);
  const raw = Buffer.from(k.publicKey.replace(/-/g, "+").replace(/_/g, "/"), "base64");
  assert.equal(raw.length, 65);
  assert.equal(raw[0], 4, "uncompressed P-256 point, as PushManager.subscribe wants");
  const stored = ctx.db.get("meta/vapid");
  assert.equal(stored.publicKey, k.publicKey);
  assert.equal(Buffer.from(stored.privateKey.replace(/-/g, "+").replace(/_/g, "/"), "base64").length, 32);
  assert.equal(k.privateKey, undefined, "the private key never leaves the server");
  push.resetCache();
  assert.equal((await push.adminPush({ action: "key" }, ADMIN)).publicKey, k.publicKey, "same keys after a cold start");
  // the private key really signs for the public key
  const sig = crypto.sign("sha256", Buffer.from("hi"), { key: { kty: "EC", crv: "P-256", d: stored.privateKey,
    x: raw.subarray(1, 33).toString("base64url"), y: raw.subarray(33).toString("base64url") }, format: "jwk" });
  assert.ok(crypto.verify("sha256", Buffer.from("hi"), { key: { kty: "EC", crv: "P-256", x: raw.subarray(1, 33).toString("base64url"), y: raw.subarray(33).toString("base64url") }, format: "jwk" }, sig));

  const sub = { endpoint: "https://web.push.apple.com/abc", keys: { p256dh: "B".repeat(87), auth: "a".repeat(22) } };
  await assert.rejects(push.adminPush({ action: "subscribe", subscription: { ...sub, endpoint: "http://evil" } }, ADMIN), /not valid/);
  let r = await push.adminPush({ action: "subscribe", subscription: sub, prefs: { quotes: false }, device: "iPhone" }, ADMIN);
  assert.equal(r.prefs.quotes, false);
  assert.equal(r.prefs.orders, true);
  r = await push.adminPush({ action: "status", endpoint: sub.endpoint }, ADMIN);
  assert.equal(r.subscribed, true);
  await push.adminPush({ action: "test", endpoint: sub.endpoint }, ADMIN);
  assert.equal(ctx.pushed.pop().payload.title, "🐝 Notificações ativadas");

  // a quote request: this phone said no to quotes
  const mail = require("../mail");
  await mail.send({ to: "support@littlehivehouse.com", kind: "admin_quote", data: { name: "Bia Lima", quote: { name: "Bia Lima", occasion: "Wedding", quantity: 100 } } });
  assert.equal(ctx.pushed.length, 0);
  await push.adminPush({ action: "subscribe", subscription: sub, prefs: { quotes: true } }, ADMIN);
  await mail.send({ to: "support@littlehivehouse.com", kind: "admin_quote", data: { name: "Bia Lima", quote: { name: "Bia Lima", occasion: "Wedding", quantity: 100 } } });
  assert.equal(ctx.pushed.pop().payload.body, "Bia · Wedding, 100 ímãs");
  await mail.send({ to: "support@littlehivehouse.com", kind: "admin_contact", data: { contact: { name: "Jo Lee", message: "Do you ship to Canada?" } } });
  assert.equal(ctx.pushed.pop().payload.body, "Jo: Do you ship to Canada?");
  await mail.send({ to: "ana@example.com", kind: "order_confirmation", data: { order: { number: "LHH-1" } } });
  assert.equal(ctx.pushed.length, 0, "customer emails never push");

  // a phone that removed the app answers 410 and is forgotten
  const gone = phone(ctx.db, "gone-phone");
  await mail.send({ to: "support@littlehivehouse.com", kind: "admin_contact", data: { contact: { name: "Jo", message: "hi" } } });
  assert.equal(ctx.db.get(`adminPush/${push.subId(gone)}`), undefined);
  r = await push.adminPush({ action: "unsubscribe", endpoint: sub.endpoint }, ADMIN);
  assert.equal(r.subscribed, false);
  assert.equal((await push.adminPush({ action: "status", endpoint: sub.endpoint }, ADMIN)).subscribed, false);
});

test("sales tax reminder: last month's Georgia numbers (charged in the month), zero months too", async () => {
  const ctx = setup();
  phone(ctx.db, "thiago");
  const st = require("../salestax");
  const now = Date.parse("2026-12-12T14:00:00Z");
  const p = st.previousMonth(now);
  assert.equal(p.label, "novembro de 2026");
  assert.equal(p.due, "2026-12-21", "the 20th is a Sunday: due Monday");
  assert.equal(new Date(p.start).toISOString(), "2026-11-01T04:00:00.000Z");
  assert.equal(new Date(p.end).toISOString(), "2026-12-01T05:00:00.000Z");
  const ga = { country: "US", state: "GA" }, fl = { country: "US", state: "FL" };
  const put = (id, o) => ctx.db._set(`orders/${id}`, { status: "paid", number: id, refunds: [], ...o });
  put("a", { paidAt: "2026-11-03T15:00:00Z", payment: { state: "captured", capturedAt: "2026-11-05T15:00:00Z" }, pricing: { total: 23.18, tax: 1.68, taxState: "GA" }, shipping: { address: ga } });
  put("b", { paidAt: "2026-10-28T15:00:00Z", payment: { state: "captured", capturedAt: "2026-11-02T15:00:00Z" }, pricing: { total: 10.6, tax: 0.6, taxState: "GA" }, shipping: { address: ga },
    refunds: [{ amount: 5.3, at: "2026-11-20T15:00:00Z", status: "succeeded" }] });
  put("c", { paidAt: "2026-11-10T15:00:00Z", payment: { state: "captured", capturedAt: "2026-11-11T15:00:00Z" }, pricing: { total: 14.95, tax: 0 }, shipping: { address: fl } });
  put("d", { paidAt: "2026-11-28T15:00:00Z", payment: { state: "authorized" }, pricing: { total: 30, tax: 2 }, shipping: { address: ga } });
  put("e", { paidAt: "2026-11-27T15:00:00Z", payment: { state: "captured", capturedAt: "2026-12-01T06:00:00Z" }, pricing: { total: 30, tax: 2 }, shipping: { address: ga } });
  put("f", { paidAt: "2026-11-09T15:00:00Z", status: "canceled", payment: { state: "released" }, pricing: { total: 30, tax: 2 }, shipping: { address: ga } });
  const r = await st.salesTaxReminder(now);
  assert.equal(r.orders, 3);
  assert.equal(r.gaOrders, 2);
  assert.equal(r.gaSales, 31.5);
  assert.equal(r.gaTax, 2.28);
  assert.equal(r.otherSales, 14.95);
  assert.equal(r.sales, 46.45);
  assert.equal(r.refunds, 5.3);
  assert.equal(r.gaRefundedTax, 0.3);
  const mailOut = ctx.net.emails.pop();
  assert.equal(mailOut.subject, "Sales tax de novembro de 2026: declarar $2.28 até 21 de dezembro");
  assert.match(mailOut.text, /Stripe › Tax › Reports/);
  assert.equal(ctx.pushed.pop().payload.title, "🧾 Sales tax de novembro de 2026");

  // a month without sales: file a zero return
  const z = await st.salesTaxReminder(Date.parse("2026-11-12T14:00:00Z"));
  assert.equal(z.gaSales, 0);
  assert.match(ctx.net.emails.pop().subject, /outubro de 2026: declarar zerado até 20 de novembro/);
  assert.match(ctx.pushed.pop().payload.body, /zerado/);
});
