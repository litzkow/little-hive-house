"use strict";
/* Admin callables. Every one checks request.auth.token.admin === true first. */

const crypto = require("crypto");
const { fail, need, siteUrl, nowIso, adminEmails, AppError } = require("./config");
const deps = require("./deps");
const stripe = require("./stripe");
const mail = require("./mail");
const O = require("./orders");
const U = require("./util");
const { syncRefunds, sendRefundEmail } = require("./webhook");
const { dollars } = require("./pricing");
const { trackerFor } = require("./tracking");

const DEFAULT_SETTINGS = { magnetUnitCost: 0.55, packagingCost: 0.60, defaultLabelCost: 4.50, stripePct: 2.9, stripeFixed: 0.30, monthlyFixedCosts: 0 };

async function loadOrder(orderId) {
  const id = U.text(orderId, 64, { required: true, field: "the order id" });
  if (!/^[A-Za-z0-9_-]+$/.test(id)) fail("invalid-argument", "That order id is not valid.");
  const ref = deps.db().collection("orders").doc(id);
  const snap = await ref.get();
  if (!snap.exists) fail("not-found", "We couldn't find that order.");
  return { ref, id, order: snap.data() };
}

/** Runs fn(order) in a transaction and writes the returned update. fn may throw AppError. */
async function mutate(ref, fn) {
  let after = null;
  await deps.db().runTransaction(async (tx) => {
    const snap = await tx.get(ref);
    if (!snap.exists) fail("not-found", "We couldn't find that order.");
    const o = snap.data();
    const upd = fn(o);
    if (!upd) { after = o; return; }
    upd.updatedAt = nowIso();
    tx.update(ref, upd);
    after = { ...o, ...upd };
  });
  return after;
}

/* ---------- claimAdmin ---------- */
/**
 * Grants admin:true when the caller's email is in ADMIN_EMAILS and either the email is verified or they
 * signed in with email + password. Trade-off (owner convenience): an unverified password account counts, so
 * the owners must create their accounts before anyone else can (Firebase allows one account per email).
 */
async function claimAdmin(data, auth) {
  U.requireAccount(auth);
  const list = adminEmails();
  if (!list.length) need("ADMIN_EMAILS");
  const email = String(auth.token.email || "").toLowerCase();
  if (!email || !list.includes(email)) fail("permission-denied", "This account's email is not on the admin list (ADMIN_EMAILS).");
  const provider = auth.token.firebase && auth.token.firebase.sign_in_provider;
  if (auth.token.email_verified !== true && provider !== "password") {
    fail("permission-denied", "Please verify your email first, or sign in with your email and password.");
  }
  const a = deps.auth();
  const user = await a.getUser(auth.uid);
  if (!(user.customClaims && user.customClaims.admin === true)) {
    await a.setCustomUserClaims(auth.uid, { ...(user.customClaims || {}), admin: true });
    console.log(`[admin] granted admin to ${email} (${auth.uid}), verified=${auth.token.email_verified === true}`);
  }
  return { admin: true, message: "You are an admin now. Reloading your sign-in…" };
}

/* ---------- order status ---------- */
async function adminSetStatus(data, auth) {
  U.requireAdmin(auth);
  const { ref, id } = await loadOrder(data && data.orderId);
  const to = U.text(data && data.status, 40, { required: true, field: "the new status" });
  const note = U.text(data && data.note, 2000);
  const after = await mutate(ref, (o) => {
    const err = O.manualStatusError(o, to);
    if (err) fail("failed-precondition", err);
    const at = nowIso();
    const upd = { status: to, timeline: (o.timeline || []).concat([{ at, status: to, text: O.TIMELINE_TEXT[to] }]) };
    if (note) upd.adminNotes = (o.adminNotes || []).concat([{ at, by: U.who(auth), text: note }]);
    if (to === "shipped") upd.fulfillment = { ...(o.fulfillment || {}), shippedAt: (o.fulfillment && o.fulfillment.shippedAt) || at };
    if (to === "delivered") upd.fulfillment = { ...(o.fulfillment || {}), deliveredAt: at };
    return upd;
  });
  return { ok: true, order: { id, status: after.status } };
}

async function adminShip(data, auth) {
  U.requireAdmin(auth);
  const { ref, id } = await loadOrder(data && data.orderId);
  const carrier = U.text(data && data.carrier, 20).toLowerCase();
  if (!O.CARRIERS[carrier]) fail("invalid-argument", "Carrier must be usps, ups, fedex, dhl or other.");
  const tracking = U.text(data && data.tracking, 80).replace(/\s+/g, "");
  const url = O.trackingUrl(carrier, tracking, U.text(data && data.url, 500));
  let labelCost = null;
  if (data && data.labelCost !== undefined && data.labelCost !== null && data.labelCost !== "") {
    labelCost = Number(data.labelCost);
    if (!Number.isFinite(labelCost) || labelCost < 0 || labelCost > 1000) fail("invalid-argument", "Label cost must be a number like 4.50.");
    labelCost = Math.round(labelCost * 100) / 100;
  }
  const after = await mutate(ref, (o) => {
    if (!["paid", "in_production", "partially_refunded", "shipped"].includes(o.status)) {
      fail("failed-precondition", `An order that is "${O.STATUS_LABELS[o.status]}" can't be shipped.`);
    }
    const at = nowIso();
    const prev = o.fulfillment || {};
    const same = prev.carrier === carrier && prev.tracking === tracking;
    const upd = {
      status: "shipped",
      fulfillment: { ...prev, carrier, tracking, url, labelCost, shippedAt: (o.status === "shipped" && prev.shippedAt) || at, deliveredAt: null },
    };
    if (!same) {
      // a new tracking number starts automatic tracking from scratch (see tracking.js)
      Object.assign(upd.fulfillment, { trackingStatus: null, trackingDetail: "", events: [], lastCheckedAt: null, lastMovementAt: null,
        estimatedDelivery: null, trackingSource: null, trackingStoppedAt: null, trackingStopReason: null, alerts: {} });
      upd["emails.outForDelivery"] = null;
    }
    if (o.status !== "shipped") upd.timeline = (o.timeline || []).concat([{ at, status: "shipped", text: O.TIMELINE_TEXT.shipped }]);
    return upd;
  });
  const autoUpdates = !!trackerFor(carrier);
  const order = O.emailOrder(id, after);
  order.fulfillment.autoUpdates = autoUpdates;
  const sent = await mail.send({ to: after.email, kind: "shipped", data: { order } });
  if (!sent.skipped) await ref.update({ "emails.shipped": nowIso() }).catch(() => {});
  return { ok: true, emailed: !sent.skipped, url, autoTracking: autoUpdates };
}

/**
 * Marks a shipped order delivered and sends the delivered + review email. Shared by adminMarkDelivered (the owner)
 * and trackShipments (the carrier said so). `at`: when it was delivered; `onlyOnceEmail`: skip the email when one went out.
 * Returns {delivered, emailed} (delivered false when the order was no longer shipped).
 */
async function deliverOrder(ref, id, { at, by, onlyOnceEmail = false, strict = false } = {}) {
  let changed = false;
  const after = await mutate(ref, (o) => {
    const shipped = o.status === "shipped" || (o.status === "partially_refunded" && o.fulfillment && o.fulfillment.shippedAt);
    if (!shipped) { if (strict) fail("failed-precondition", "Mark the order as shipped first."); return null; }
    const now = nowIso();
    const when = at || now;
    changed = true;
    const upd = {
      status: "delivered", fulfillment: { ...(o.fulfillment || {}), deliveredAt: when },
      timeline: (o.timeline || []).concat([{ at: now, status: "delivered", text: O.TIMELINE_TEXT.delivered }]),
    };
    if (by && by !== "admin") upd.adminNotes = (o.adminNotes || []).concat([{ at: now, by: "system", text: `Marked delivered automatically (${by}).` }]);
    return upd;
  });
  if (!changed) return { delivered: false, emailed: false };
  if (onlyOnceEmail && after.emails && after.emails.delivered) return { delivered: true, emailed: false };
  const sent = await mail.send({ to: after.email, kind: "delivered_review", data: { order: O.emailOrder(id, after) } });
  if (!sent.skipped) await ref.update({ "emails.delivered": nowIso() }).catch(() => {});
  return { delivered: true, emailed: !sent.skipped };
}

async function adminMarkDelivered(data, auth) {
  U.requireAdmin(auth);
  const { ref, id } = await loadOrder(data && data.orderId);
  const r = await deliverOrder(ref, id, { by: "admin", strict: true });
  return { ok: true, emailed: r.emailed };
}

/* ---------- refunds ---------- */
async function adminRefund(data, auth) {
  U.requireAdmin(auth);
  need("STRIPE_SECRET_KEY");
  const { ref, id, order } = await loadOrder(data && data.orderId);
  const reason = U.text(data && data.reason, 40);
  const note = U.text(data && data.note, 1000);
  let check;
  try { check = O.checkRefund(order, data && data.amount, reason); } catch (e) { fail("failed-precondition", e.message); }
  const pi = order.stripe && order.stripe.paymentIntent;
  if (!pi) fail("failed-precondition", "This order has no Stripe payment to refund.");
  const already = Math.round((order.refundedTotal || 0) * 100);
  let refund;
  try {
    refund = await stripe.request("POST", "/refunds", {
      payment_intent: pi, amount: check.amountCents,
      reason: reason === "duplicate" ? "duplicate" : "requested_by_customer",
      metadata: { orderId: id, orderNumber: order.number || "", reason, note: note.slice(0, 450), by: U.who(auth) },
    }, { idempotencyKey: `refund-${id}-${already}-${check.amountCents}` });
  } catch (err) {
    throw stripe.friendly(err, "making the refund");
  }
  if (refund.status === "failed" || refund.status === "canceled") fail("aborted", `Stripe could not make this refund (${refund.failure_reason || refund.status}).`);
  // the webhook (charge.refunded) may get here first; syncRefunds dedups by refund id and sends the email once
  const r = await syncRefunds(ref, [refund], { notify: true });
  const snap = await ref.get();
  const o = snap.data();
  return { ok: true, refundId: refund.id, amount: dollars(check.amountCents), refundedTotal: o.refundedTotal, status: o.status, emailed: r.added.length > 0 };
}

async function adminAddNote(data, auth) {
  U.requireAdmin(auth);
  const { ref } = await loadOrder(data && data.orderId);
  const t = U.text(data && data.text, 2000, { required: true, field: "the note" });
  const note = { at: nowIso(), by: U.who(auth), text: t };
  await mutate(ref, (o) => ({ adminNotes: (o.adminNotes || []).concat([note]) }));
  return { ok: true, note };
}

async function adminResendEmail(data, auth) {
  U.requireAdmin(auth);
  const { ref, id, order } = await loadOrder(data && data.orderId);
  const kind = U.text(data && data.kind, 40);
  if (!order.email) fail("failed-precondition", "This order has no customer email.");
  const base = { order: O.emailOrder(id, order) };
  if (kind === "order_confirmation") {
    if (order.status === "pending") fail("failed-precondition", "This order hasn't been paid yet.");
    await mail.send({ to: order.email, kind, data: base, required: true });
    await ref.update({ "emails.confirmation": nowIso() });
  } else if (kind === "shipped") {
    if (!order.fulfillment || !order.fulfillment.shippedAt) fail("failed-precondition", "This order hasn't shipped yet.");
    await mail.send({ to: order.email, kind, data: base, required: true });
    await ref.update({ "emails.shipped": nowIso() });
  } else if (kind === "out_for_delivery") {
    if (!order.fulfillment || !order.fulfillment.shippedAt) fail("failed-precondition", "This order hasn't shipped yet.");
    await mail.send({ to: order.email, kind, data: base, required: true });
    await ref.update({ "emails.outForDelivery": nowIso() });
  } else if (kind === "delivered_review") {
    if (!order.fulfillment || !order.fulfillment.deliveredAt) fail("failed-precondition", "This order isn't marked delivered yet.");
    await mail.send({ to: order.email, kind, data: base, required: true });
    await ref.update({ "emails.delivered": nowIso() });
  } else if (kind === "refund") {
    const last = (order.refunds || []).filter((r) => r.status !== "failed" && r.status !== "canceled").slice(-1)[0];
    if (!last) fail("failed-precondition", "This order has no refunds.");
    const res = await sendRefundEmail(ref, order, last);
    if (res.skipped) fail("unavailable", `The email could not be sent (${res.reason || "email is not set up"}).`);
  } else if (kind === "payment_link") {
    const url = order.stripe && order.stripe.paymentLinkUrl;
    if (!url || order.status !== "pending") fail("failed-precondition", "This order has no open payment link.");
    const item = (order.items || [])[0] || {};
    await mail.send({ to: order.email, kind, data: { ...base, paymentLink: { url, title: item.title || "", amount: item.amount || 0, note: order.notes || "" } }, required: true });
  } else {
    fail("invalid-argument", "Email kind must be order_confirmation, shipped, out_for_delivery, delivered_review, refund or payment_link.");
  }
  return { ok: true };
}

/* ---------- custom payment links (quotes) ---------- */
async function adminCreatePaymentLink(data, auth) {
  U.requireAdmin(auth);
  need("STRIPE_SECRET_KEY");
  const title = U.text(data && data.title, 200, { required: true, field: "a title" });
  const amount = Number(data && data.amount);
  if (!Number.isFinite(amount) || amount < 0.5 || amount > 50000) fail("invalid-argument", "The amount must be between $0.50 and $50,000.");
  const amountCents = Math.round(amount * 100);
  const email = U.cleanEmail(data && data.email, { required: false });
  const note = U.text(data && data.note, 2000);
  const magnets = Number.isInteger(Number(data && data.magnets)) && Number(data.magnets) > 0 ? Number(data.magnets) : null;
  const db = deps.db();
  const ref = db.collection("orders").doc();
  const at = nowIso();
  const item = { kind: "custom", title, amount: dollars(amountCents) };
  if (magnets) item.magnets = magnets;
  const order = {
    number: null, uid: null, guestUid: null, email, name: "", status: "pending", items: [item],
    pricing: { subtotal: dollars(amountCents), bundleDiscount: 0, volumePct: 0, volumeDiscount: 0, promo: null, shipping: 0, total: dollars(amountCents), currency: "usd" },
    shipping: null, giftMessage: "", notes: note, marketing: false,
    stripe: { sessionId: null, paymentIntent: null, customer: null, fee: null, paymentLink: null, paymentLinkUrl: null },
    fulfillment: null, refunds: [], refundedTotal: 0, adminNotes: [{ at, by: U.who(auth), text: `Payment link created for $${dollars(amountCents).toFixed(2)}.` }],
    timeline: [{ at, status: "pending", text: "Payment link sent." }],
    emails: { confirmation: null, shipped: null, delivered: null, refund: [] },
    source: "payment_link", createdAt: at, paidAt: null, updatedAt: at,
  };
  await ref.set(order);
  let link;
  try {
    // A Payment Link (not a Checkout Session) so the customer can pay days later; one payment only.
    const price = await stripe.request("POST", "/prices", { currency: "usd", unit_amount: amountCents, product_data: { name: title.slice(0, 240) } },
      { idempotencyKey: `plink-price-${ref.id}` });
    link = await stripe.request("POST", "/payment_links", {
      line_items: [{ price: price.id, quantity: 1 }],
      metadata: { orderId: ref.id },
      payment_intent_data: { metadata: { orderId: ref.id }, description: `Little Hive House: ${title}`.slice(0, 900) },
      shipping_address_collection: { allowed_countries: ["US", "CA"] },
      restrictions: { completed_sessions: { limit: 1 } },
      after_completion: { type: "redirect", redirect: { url: `${siteUrl()}/thank-you.html?order=${ref.id}&session={CHECKOUT_SESSION_ID}` } },
    }, { idempotencyKey: `plink-${ref.id}` });
  } catch (err) {
    await ref.delete().catch(() => {});
    throw stripe.friendly(err, "creating the payment link");
  }
  const url = `${link.url}?client_reference_id=${ref.id}${email ? `&prefilled_email=${encodeURIComponent(email)}` : ""}`;
  await ref.update({ "stripe.paymentLink": link.id, "stripe.paymentLinkUrl": url, updatedAt: nowIso() });
  let emailed = false;
  if (email) {
    const res = await mail.send({ to: email, kind: "payment_link", data: { order: O.emailOrder(ref.id, { ...order, email }), paymentLink: { url, title, amount: dollars(amountCents), note } } });
    emailed = !res.skipped;
  }
  return { url, orderId: ref.id, emailed };
}

/* ---------- promotion codes ---------- */
async function adminCreatePromo(data, auth) {
  U.requireAdmin(auth);
  need("STRIPE_SECRET_KEY");
  const code = U.text(data && data.code, 40).toUpperCase();
  if (!/^[A-Z0-9_-]{3,40}$/.test(code)) fail("invalid-argument", "Codes use 3 to 40 letters, numbers, - or _ (like WELCOME10).");
  const pct = data && data.percentOff !== undefined && data.percentOff !== null && data.percentOff !== "" ? Number(data.percentOff) : null;
  const amt = data && data.amountOff !== undefined && data.amountOff !== null && data.amountOff !== "" ? Number(data.amountOff) : null;
  if ((pct === null) === (amt === null)) fail("invalid-argument", "Choose either a percent off or an amount off.");
  if (pct !== null && !(pct > 0 && pct <= 100)) fail("invalid-argument", "Percent off must be between 1 and 100.");
  if (amt !== null && !(amt >= 0.5 && amt <= 10000)) fail("invalid-argument", "Amount off must be at least $0.50.");
  const max = data && data.maxRedemptions ? Number(data.maxRedemptions) : null;
  if (max !== null && !(Number.isInteger(max) && max > 0)) fail("invalid-argument", "Max uses must be a whole number.");
  let expiresAt = null;
  if (data && data.expiresAt) {
    const t = Date.parse(data.expiresAt);
    if (!Number.isFinite(t) || t < Date.now() + 60000) fail("invalid-argument", "The end date must be in the future.");
    expiresAt = Math.floor(t / 1000);
  }
  try {
    const existing = await stripe.request("GET", "/promotion_codes", { code, limit: 1 });
    if (existing.data && existing.data.length) fail("already-exists", `The code ${code} already exists.`);
    const coupon = await stripe.request("POST", "/coupons", {
      name: code, duration: "once",
      ...(pct !== null ? { percent_off: pct } : { amount_off: Math.round(amt * 100), currency: "usd" }),
    });
    const promo = await stripe.request("POST", "/promotion_codes", {
      coupon: coupon.id, code, max_redemptions: max || undefined, expires_at: expiresAt || undefined,
      metadata: { createdBy: U.who(auth) },
    });
    return { ok: true, promo: promoView({ ...promo, coupon }) };
  } catch (err) {
    throw err instanceof AppError ? err : stripe.friendly(err, "creating the code");
  }
}

function promoView(p) {
  const c = p.coupon && typeof p.coupon === "object" ? p.coupon : {};
  return {
    id: p.id, code: p.code, active: !!p.active,
    percentOff: c.percent_off || null, amountOff: c.amount_off ? dollars(c.amount_off) : null,
    timesRedeemed: p.times_redeemed || 0, maxRedemptions: p.max_redemptions || null,
    expiresAt: p.expires_at ? new Date(p.expires_at * 1000).toISOString() : null,
    createdAt: p.created ? new Date(p.created * 1000).toISOString() : null,
  };
}

async function adminListPromos(data, auth) {
  U.requireAdmin(auth);
  need("STRIPE_SECRET_KEY");
  try {
    const res = await stripe.request("GET", "/promotion_codes", { limit: 100, expand: ["data.coupon"] });
    return { promos: (res.data || []).map(promoView) };
  } catch (err) {
    throw stripe.friendly(err, "loading the codes");
  }
}

/* ---------- settings ---------- */
async function adminSaveSettings(data, auth) {
  U.requireAdmin(auth);
  const s = (data && data.settings && typeof data.settings === "object") ? data.settings : (data || {});
  const out = {};
  for (const k of Object.keys(DEFAULT_SETTINGS)) {
    if (s[k] === undefined || s[k] === null || s[k] === "") continue;
    const n = Number(s[k]);
    if (!Number.isFinite(n) || n < 0 || n > 100000) fail("invalid-argument", `"${k}" must be a number of 0 or more.`);
    out[k] = Math.round(n * 10000) / 10000;
  }
  if (!Object.keys(out).length) fail("invalid-argument", "Nothing to save.");
  out.updatedAt = nowIso();
  out.updatedBy = U.who(auth);
  const ref = deps.db().collection("settings").doc("store");
  await ref.set(out, { merge: true });
  const snap = await ref.get();
  return { ok: true, settings: { ...DEFAULT_SETTINGS, ...snap.data() } };
}

/* ---------- customer photos ---------- */
async function photoUrl(bucket, path) {
  const file = bucket.file(path);
  try {
    const u = await deps.getDownloadURL(file);
    if (u) return u;
  } catch (e) { /* no download token yet: make one below */ }
  try {
    const token = crypto.randomUUID();
    const [meta] = await file.getMetadata();
    const existing = meta && meta.metadata && meta.metadata.firebaseStorageDownloadTokens;
    const tok = existing ? String(existing).split(",")[0] : token;
    if (!existing) await file.setMetadata({ metadata: { firebaseStorageDownloadTokens: tok } });
    return `https://firebasestorage.googleapis.com/v0/b/${bucket.name}/o/${encodeURIComponent(path)}?alt=media&token=${tok}`;
  } catch (err) {
    console.warn("[adminPhotoUrls]", path, err && err.message);
    return null;
  }
}

async function adminPhotoUrls(data, auth) {
  U.requireAdmin(auth);
  const { order } = await loadOrder(data && data.orderId);
  const packs = (order.items || []).map((it, index) => ({ it, index })).filter(({ it }) => it.kind === "photos");
  if (!packs.length) return { packs: [] };
  const bucket = deps.bucket();
  const out = [];
  for (const { it, index } of packs) {
    const photos = await Promise.all((it.photos || []).map(async (p, n) => ({
      n: n + 1, path: p.path, frame: p.frame, caption: p.caption || "", url: p.path ? await photoUrl(bucket, p.path) : null,
    })));
    out.push({ index, packSize: it.packSize, qty: it.qty || 1, notes: it.notes || "", photos });
  }
  return { packs: out };
}

/* ---------- reviews ---------- */
async function adminModerateReview(data, auth) {
  U.requireAdmin(auth);
  const id = U.text(data && data.id, 200, { required: true, field: "the review id" });
  const status = U.text(data && data.status, 20);
  const ref = deps.db().collection("reviews").doc(id);
  const snap = await ref.get();
  if (!snap.exists) fail("not-found", "We couldn't find that review.");
  if (status === "deleted") { await ref.delete(); return { ok: true, deleted: true }; }
  if (!["pending", "published"].includes(status)) fail("invalid-argument", "Status must be published, pending or deleted.");
  await ref.update({ status, moderatedAt: nowIso(), moderatedBy: U.who(auth) });
  return { ok: true, status };
}

module.exports = {
  claimAdmin, adminSetStatus, adminShip, adminMarkDelivered, adminRefund, adminAddNote, adminResendEmail,
  adminCreatePaymentLink, adminCreatePromo, adminListPromos, adminSaveSettings, adminPhotoUrls, adminModerateReview,
  DEFAULT_SETTINGS, promoView, deliverOrder,
};
