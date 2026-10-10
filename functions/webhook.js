"use strict";
/* stripeWebhook (HTTP): checkout.session.completed / .expired, charge.refunded, charge.dispute.created.
   Every event is processed once (stripeEvents/{eventId}); each handler is also idempotent on its own. */

const { env, mailAdmin, nowIso } = require("./config");
const deps = require("./deps");
const stripe = require("./stripe");
const mail = require("./mail");
const O = require("./orders");
const { completeCheckout, retrieveSession } = require("./checkout");
const { dollars } = require("./pricing");

const HANDLED = new Set(["checkout.session.completed", "checkout.session.async_payment_succeeded", "checkout.session.expired",
  "charge.refunded", "charge.dispute.created"]);
const STALE_LOCK_MS = 5 * 60 * 1000;

async function orderByPaymentIntent(pi) {
  if (!pi) return null;
  const q = await deps.db().collection("orders").where("stripe.paymentIntent", "==", pi).limit(1).get();
  return q.empty ? null : q.docs[0];
}

async function onCompleted(obj) {
  const session = await retrieveSession(obj.id);     // fresh, expanded, in our pinned API version
  return completeCheckout(session);
}

async function onExpired(session) {
  const orderId = session.client_reference_id || (session.metadata && session.metadata.orderId);
  if (!orderId) return { skipped: "no order" };
  const db = deps.db();
  const ref = db.collection("orders").doc(orderId);
  let send = null;
  await db.runTransaction(async (tx) => {
    const snap = await tx.get(ref);
    if (!snap.exists) return;
    const o = snap.data();
    if (o.status !== "pending") return;
    const at = nowIso();
    const email = o.email || ((session.customer_details && session.customer_details.email) || "").toLowerCase();
    const upd = { abandonedAt: o.abandonedAt || at, updatedAt: at };
    if (email && o.marketing === true && !(o.emails && o.emails.abandoned)) {
      upd["emails.abandoned"] = at;
      send = { id: orderId, order: { ...o, email } };
    }
    tx.update(ref, upd);
  });
  if (send) await mail.send({ to: send.order.email, kind: "abandoned_checkout", data: { order: O.emailOrder(send.id, send.order) } });
  return { abandoned: true, emailed: !!send };
}

async function listRefunds(pi) {
  const res = await stripe.request("GET", "/refunds", { payment_intent: pi, limit: 100 });
  return res.data || [];
}

/** Syncs refunds made anywhere (admin page or Stripe dashboard) into the order. Exported for adminRefund. */
async function syncRefunds(orderRef, stripeRefunds, { notify = true } = {}) {
  const db = deps.db();
  let added = [], after = null;
  await db.runTransaction(async (tx) => {
    const snap = await tx.get(orderRef);
    if (!snap.exists) return;
    const o = snap.data();
    const m = O.mergeRefunds(o.refunds, stripeRefunds, nowIso());
    if (!m.added.length && m.refundedTotal === o.refundedTotal) return;
    const at = nowIso();
    const upd = { refunds: m.refunds, refundedTotal: m.refundedTotal, updatedAt: at };
    const next = O.statusAfterRefund(o, Math.round(m.refundedTotal * 100));
    if (next !== o.status && O.canTransition(o.status, next)) {
      upd.status = next;
      upd.timeline = (o.timeline || []).concat([{ at, status: next, text: O.TIMELINE_TEXT[next] }]);
    }
    tx.update(orderRef, upd);
    added = m.added;
    after = { ...o, ...upd };
  });
  if (notify && after && added.length) {
    for (const r of added) await sendRefundEmail(orderRef, after, r);
  }
  return { added, order: after };
}

async function sendRefundEmail(orderRef, o, r) {
  if (!o.email) return { skipped: true };
  const remaining = Math.max(0, dollars(Math.round(((o.pricing && o.pricing.total) || 0) * 100) - Math.round((o.refundedTotal || 0) * 100)));
  const data = {
    order: O.emailOrder(orderRef.id, o),
    // the admin's note is shown to the customer ("A note from us"); dashboard refunds have none
    refund: { amount: r.amount, reason: r.reason, reasonLabel: O.REFUND_REASONS[r.reason] || "Other",
      note: r.by && r.by !== "stripe-dashboard" ? r.note || "" : "",
      full: o.status === "refunded", refundedTotal: o.refundedTotal || 0, remaining },
  };
  const res = await mail.send({ to: o.email, kind: "refund", data });
  if (!res.skipped) {
    const db = deps.db();
    await db.runTransaction(async (tx) => {
      const s = await tx.get(orderRef);
      if (!s.exists) return;
      const em = s.data().emails || {};
      tx.update(orderRef, { "emails.refund": (em.refund || []).concat([{ id: r.id || null, at: nowIso() }]) });
    }).catch(() => {});
  }
  return res;
}

async function onRefunded(charge) {
  const pi = typeof charge.payment_intent === "object" && charge.payment_intent ? charge.payment_intent.id : charge.payment_intent;
  const doc = await orderByPaymentIntent(pi);
  if (!doc) return { skipped: "no order" };
  const refunds = await listRefunds(pi);
  const r = await syncRefunds(doc.ref, refunds);
  return { synced: r.added.length };
}

async function onDispute(dispute) {
  let pi = dispute.payment_intent;
  if (!pi && dispute.charge) {
    try { pi = (await stripe.request("GET", `/charges/${encodeURIComponent(dispute.charge)}`)).payment_intent; } catch (e) { pi = null; }
  }
  const doc = await orderByPaymentIntent(typeof pi === "object" && pi ? pi.id : pi);
  const at = nowIso();
  const due = dispute.evidence_details && dispute.evidence_details.due_by;
  const info = { id: dispute.id, reason: dispute.reason || "", amount: dollars(dispute.amount || 0), status: dispute.status || "", at,
    evidenceDueBy: due ? new Date(due * 1000).toISOString() : null };
  let o = null;
  if (doc) {
    const db = deps.db();
    let fresh = false;
    await db.runTransaction(async (tx) => {
      const s = await tx.get(doc.ref);
      const d = s.data();
      if (d.dispute && d.dispute.id === dispute.id) { o = d; return; }
      fresh = true;
      tx.update(doc.ref, {
        dispute: info, updatedAt: at,
        adminNotes: (d.adminNotes || []).concat([{ at, by: "stripe", text: `Dispute opened: ${info.reason || "no reason given"} ($${info.amount.toFixed(2)}). Answer it in the Stripe dashboard.` }]),
      });
      o = { ...d, dispute: info };
    });
    if (!fresh) return { duplicate: true };
  }
  await mail.send({ to: mailAdmin(), kind: "admin_dispute", data: { order: o ? O.emailOrder(doc.id, o) : null, dispute: info } });
  return { flagged: !!doc };
}

async function dispatch(event) {
  const obj = event.data && event.data.object;
  switch (event.type) {
    case "checkout.session.completed":
    case "checkout.session.async_payment_succeeded": return onCompleted(obj);
    case "checkout.session.expired": return onExpired(obj);
    case "charge.refunded": return onRefunded(obj);
    case "charge.dispute.created": return onDispute(obj);
    default: return { ignored: true };
  }
}

/** Claims stripeEvents/{id}. Returns false when the event was already handled (or is being handled right now). */
async function claimEvent(event) {
  const db = deps.db();
  const ref = db.collection("stripeEvents").doc(event.id);
  let claimed = false;
  await db.runTransaction(async (tx) => {
    const s = await tx.get(ref);
    if (s.exists) {
      const d = s.data();
      if (d.status === "done") return;
      if (d.status === "processing" && Date.now() - Date.parse(d.startedAt || 0) < STALE_LOCK_MS) return;
    }
    tx.set(ref, { type: event.type, status: "processing", startedAt: nowIso(), created: event.created || null });
    claimed = true;
  });
  return claimed;
}

/** The HTTP handler body. Returns {status, body} so it is testable without Express. */
async function handleWebhook(rawBody, signature) {
  const secret = env("STRIPE_WEBHOOK_SECRET");
  if (!secret) {
    console.error("[webhook] STRIPE_WEBHOOK_SECRET is missing; rejecting. See SETUP.md.");
    return { status: 500, body: "Webhook secret is not configured" };
  }
  let event;
  try {
    event = stripe.verifyWebhook(rawBody, signature, secret);
  } catch (err) {
    console.warn("[webhook] bad signature:", err.message);
    return { status: 400, body: `Webhook error: ${err.message}` };
  }
  if (!event || !event.id || !event.type) return { status: 400, body: "Not a Stripe event" };
  if (!HANDLED.has(event.type)) return { status: 200, body: "ignored" };
  if (!env("STRIPE_SECRET_KEY")) {
    console.error("[webhook] STRIPE_SECRET_KEY is missing; Stripe will retry. See SETUP.md.");
    return { status: 500, body: "Stripe key is not configured" };
  }
  const db = deps.db();
  if (!(await claimEvent(event))) return { status: 200, body: "duplicate" };
  const ref = db.collection("stripeEvents").doc(event.id);
  try {
    const result = await dispatch(event);
    await ref.set({ status: "done", doneAt: nowIso(), result: JSON.parse(JSON.stringify(result || {})) }, { merge: true });
    return { status: 200, body: "ok" };
  } catch (err) {
    console.error("[webhook]", event.type, event.id, err);
    await ref.delete().catch(() => {});     // let Stripe's retry run it again
    return { status: 500, body: "Handler failed; Stripe will retry" };
  }
}

module.exports = { handleWebhook, dispatch, syncRefunds, sendRefundEmail, listRefunds, orderByPaymentIntent, HANDLED };
