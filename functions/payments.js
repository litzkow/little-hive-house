"use strict";
/* Charge on ship. Checkout and payment links only authorize the card (checkout.js chargeOnShip); this module moves the
   money later and keeps order.payment up to date:

     order.payment = { state: "authorized" | "captured" | "released" | "expired",
                       authorizedAt, captureBefore (when the card hold ends), capturedAt, releasedAt, expiredAt, warnedAt }

   captureOrder  adminShip (before marking shipped) and adminCapture ("Charge now")
   releaseHold   adminRefund of the whole amount before it was charged: cancels the hold, nothing is charged
   checkHolds    every 2 hours: warns the owners 2 days before a hold ends; marks holds that ended
   onCaptured / onCanceled  webhook (charge.captured / payment_intent.canceled): captures or cancels made in Stripe */

const { fail, mailAdmin, nowIso, AppError } = require("./config");
const deps = require("./deps");
const stripe = require("./stripe");
const mail = require("./mail");
const O = require("./orders");
const { dollars } = require("./pricing");

const WARN_HOURS = 48;
const isHeld = (o) => !!(o && o.payment && o.payment.state === "authorized");

function feeOf(pi) {
  const ch = pi && typeof pi.latest_charge === "object" ? pi.latest_charge : null;
  const bt = ch && typeof ch.balance_transaction === "object" ? ch.balance_transaction : null;
  return bt && Number.isFinite(bt.fee) ? dollars(bt.fee) : null;
}

async function markCaptured(ref, pi, by) {
  let after = null;
  await deps.db().runTransaction(async (tx) => {
    const snap = await tx.get(ref);
    if (!snap.exists) return;
    const o = snap.data();
    if (!isHeld(o)) { after = o; return; }
    const at = nowIso();
    const amount = pi && Number.isFinite(pi.amount_received) && pi.amount_received > 0 ? dollars(pi.amount_received) : (o.pricing && o.pricing.total) || 0;
    const fee = feeOf(pi);
    const upd = {
      payment: { ...o.payment, state: "captured", capturedAt: at },
      adminNotes: (o.adminNotes || []).concat([{ at, by: by || "system", text: `Card charged $${Number(amount).toFixed(2)}.` }]),
      updatedAt: at,
    };
    if (fee !== null) upd.stripe = { ...(o.stripe || {}), fee };
    tx.update(ref, upd);
    after = { ...o, ...upd };
  });
  return after;
}

async function markExpired(ref, id, reason) {
  let after = null;
  await deps.db().runTransaction(async (tx) => {
    const snap = await tx.get(ref);
    if (!snap.exists) return;
    const o = snap.data();
    if (!isHeld(o)) return;
    const at = nowIso();
    const upd = {
      status: "canceled", payment: { ...o.payment, state: "expired", expiredAt: at },
      timeline: (o.timeline || []).concat([{ at, status: "canceled", text: "The payment authorization ended before the order was charged. Your card was not charged." }]),
      adminNotes: (o.adminNotes || []).concat([{ at, by: "system", text: `The card hold ended before the order was charged (${reason}). Nothing was charged. Send the customer a payment link (Links) to collect it.` }]),
      updatedAt: at,
    };
    tx.update(ref, upd);
    after = { ...o, ...upd };
  });
  if (after) await mail.send({ to: mailAdmin(), kind: "admin_payment_hold", data: { mode: "expired", order: O.emailOrder(id, after) } });
  return after;
}

const EXPIRED_MSG = "The hold on the customer's card has ended, so this order can't be charged anymore. Nothing was charged. " +
  "Send them a payment link (Links) for the amount, then ship.";

/**
 * Charges a held order. Returns {charged: true, amount} or {charged: false} when there was nothing to charge
 * (already charged, or an order from before charge-on-ship). Throws a friendly AppError when Stripe refuses.
 */
async function captureOrder(ref, id, order, { by } = {}) {
  if (!isHeld(order)) {
    if (order && order.payment && order.payment.state === "expired") fail("failed-precondition", EXPIRED_MSG);
    return { charged: false };
  }
  const pi = order.stripe && order.stripe.paymentIntent;
  if (!pi) fail("failed-precondition", "This order has no Stripe payment to charge.");
  let res;
  try {
    res = await stripe.request("POST", `/payment_intents/${encodeURIComponent(pi)}/capture`, { expand: ["latest_charge.balance_transaction"] },
      { idempotencyKey: `capture-${id}` });
  } catch (err) {
    if (err instanceof stripe.StripeError && err.status >= 400 && err.status < 500) {
      // already captured in the Stripe dashboard, or the hold ended: look at the PaymentIntent
      let cur = null;
      try { cur = await stripe.request("GET", `/payment_intents/${encodeURIComponent(pi)}`, { expand: ["latest_charge.balance_transaction"] }); } catch (e) { cur = null; }
      if (cur && cur.status === "succeeded") { await markCaptured(ref, cur, by); return { charged: true, amount: dollars(cur.amount_received || 0) }; }
      if (cur && cur.status === "canceled") { await markExpired(ref, id, cur.cancellation_reason || "canceled"); fail("failed-precondition", EXPIRED_MSG); }
    }
    throw stripe.friendly(err, "charging the card");
  }
  if (res.status !== "succeeded") fail("aborted", `Stripe could not charge the card (status: ${res.status}). Try again, or send a payment link.`);
  await markCaptured(ref, res, by);
  return { charged: true, amount: dollars(res.amount_received || 0) };
}

/** Cancels the card hold of an order that was never charged (full "refund" before shipping). */
async function releaseHold(ref, id, order, { by, reason, note } = {}) {
  const pi = order.stripe && order.stripe.paymentIntent;
  if (!pi) fail("failed-precondition", "This order has no Stripe payment.");
  let res;
  try {
    res = await stripe.request("POST", `/payment_intents/${encodeURIComponent(pi)}/cancel`, { cancellation_reason: reason === "duplicate" ? "duplicate" : "requested_by_customer" },
      { idempotencyKey: `release-${id}` });
  } catch (err) {
    throw stripe.friendly(err, "releasing the card hold");
  }
  if (res.status !== "canceled") fail("aborted", `Stripe could not release the hold (status: ${res.status}).`);
  let after = null;
  await deps.db().runTransaction(async (tx) => {
    const snap = await tx.get(ref);
    const o = snap.data();
    const at = nowIso();
    const upd = {
      status: "canceled", payment: { ...(o.payment || {}), state: "released", releasedAt: at }, updatedAt: at,
      cancel: { reason: reason || "other", note: note || "", by: by || "admin", at },
      timeline: (o.timeline || []).concat([{ at, status: "canceled", text: "Order canceled. Your card was not charged." }]),
      adminNotes: (o.adminNotes || []).concat([{ at, by: by || "admin", text: `Canceled before charging: the card hold was released, nothing was charged.${note ? " Note: " + note : ""}` }]),
    };
    tx.update(ref, upd);
    after = { ...o, ...upd };
  });
  let emailed = false;
  if (after && after.email) {
    const total = (after.pricing && after.pricing.total) || 0;
    const r = await mail.send({ to: after.email, kind: "refund", data: { order: O.emailOrder(id, after), refund: {
      amount: total, reason: reason || "other", reasonLabel: O.REFUND_REASONS[reason] || "Other", full: true, refundedTotal: total, remaining: 0,
      note: `${note ? note + " " : ""}Your card was never charged: we released the hold, so the pending amount disappears from your statement in a few days.`,
    } } });
    emailed = !r.skipped;
  }
  return { released: true, emailed, order: after };
}

/** Every 2 hours: warn 2 days before a hold ends; after it ends, check Stripe and mark the order. */
async function checkHolds(now = Date.now()) {
  const q = await deps.db().collection("orders").where("payment.state", "==", "authorized").get();
  let warned = 0, ended = 0;
  for (const d of q.docs) {
    const o = d.data();
    const until = Date.parse((o.payment && o.payment.captureBefore) || "");
    if (!Number.isFinite(until)) continue;
    const hoursLeft = (until - now) / 3600000;
    if (hoursLeft <= 0) {
      const pi = o.stripe && o.stripe.paymentIntent;
      let cur = null;
      try { cur = pi ? await stripe.request("GET", `/payment_intents/${encodeURIComponent(pi)}`, { expand: ["latest_charge.balance_transaction"] }) : null; } catch (e) { cur = null; }
      if (cur && cur.status === "succeeded") { await markCaptured(d.ref, cur, "stripe"); continue; }
      if (cur && cur.status === "requires_capture" && hoursLeft > -24) continue;   // Stripe hasn't closed it yet: try again later
      if (cur || hoursLeft <= -24) { await markExpired(d.ref, d.id, cur ? cur.cancellation_reason || cur.status : "no answer from Stripe"); ended += 1; }
      continue;
    }
    if (hoursLeft <= WARN_HOURS && !o.payment.warnedAt && !["shipped", "delivered", "canceled", "refunded"].includes(o.status)) {
      await d.ref.update({ "payment.warnedAt": nowIso() });
      await mail.send({ to: mailAdmin(), kind: "admin_payment_hold", data: { mode: "due", hoursLeft: Math.round(hoursLeft), order: O.emailOrder(d.id, o) } });
      warned += 1;
    }
  }
  return { held: q.size, warned, ended };
}

/* ---------- webhook ---------- */
async function orderDocByPi(pi) {
  if (!pi) return null;
  const q = await deps.db().collection("orders").where("stripe.paymentIntent", "==", pi).limit(1).get();
  return q.empty ? null : q.docs[0];
}

/** charge.captured: charged in the Stripe dashboard (or our own capture arriving again). */
async function onCaptured(charge) {
  const piId = typeof charge.payment_intent === "object" && charge.payment_intent ? charge.payment_intent.id : charge.payment_intent;
  const doc = await orderDocByPi(piId);
  if (!doc || !isHeld(doc.data())) return { skipped: true };
  const pi = await stripe.request("GET", `/payment_intents/${encodeURIComponent(piId)}`, { expand: ["latest_charge.balance_transaction"] });
  await markCaptured(doc.ref, pi, "stripe-dashboard");
  return { captured: true };
}

/** payment_intent.canceled: the hold ended (Stripe cancels it automatically) or someone canceled it in Stripe. */
async function onCanceled(pi) {
  const doc = await orderDocByPi(pi.id);
  if (!doc || !isHeld(doc.data())) return { skipped: true };
  await markExpired(doc.ref, doc.id, pi.cancellation_reason || "canceled");
  return { expired: true };
}

module.exports = { captureOrder, releaseHold, checkHolds, onCaptured, onCanceled, isHeld, EXPIRED_MSG, WARN_HOURS, AppError };
