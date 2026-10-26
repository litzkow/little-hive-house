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
const { TAX_GOODS, taxWanted, isTaxSetupError, chargeOnShip, HOLD_TEXT } = require("./checkout");
const payments = require("./payments");

const DEFAULT_SETTINGS = { magnetUnitCost: 0.55, packagingCost: 0.60, defaultLabelCost: 4.50, stripePct: 2.9, stripeFixed: 0.30, monthlyFixedCosts: 0, stripeTaxPct: 0.5, incomeTaxPct: 25,
  printCutIn: 2.45, printImageIn: 2.08, printEnhance: 1, autoNewsletter: 1 };   // Settings › Printing: the punch's paper size and the printed picture size (inches), photo touch-up (1 on, 0 off)

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
  // charge on ship: the card is charged first; if Stripe refuses, the order is not marked shipped
  const cur = (await ref.get()).data();
  let charged = { charged: false };
  if (payments.isHeld(cur) && ["paid", "in_production", "shipped"].includes(cur.status)) charged = await payments.captureOrder(ref, id, cur, { by: U.who(auth) });
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
  return { ok: true, emailed: !sent.skipped, url, autoTracking: autoUpdates, charged: charged.charged, chargedAmount: charged.amount || 0 };
}

/* ---------- charge on ship: "Charge now" ---------- */
async function adminCapture(data, auth) {
  U.requireAdmin(auth);
  need("STRIPE_SECRET_KEY");
  const { ref, id, order } = await loadOrder(data && data.orderId);
  if (!payments.isHeld(order)) fail("failed-precondition", order.payment && order.payment.state === "expired" ? payments.EXPIRED_MSG : "This order has already been charged.");
  const r = await payments.captureOrder(ref, id, order, { by: U.who(auth) });
  return { ok: true, charged: r.charged, amount: r.amount || 0 };
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
  if (payments.isHeld(order)) {
    // not charged yet: a full refund just releases the card hold; part of it would need a charge first
    if (!check.full) fail("failed-precondition", "This order hasn't been charged yet. Refund the full amount to cancel it (the card hold is released), or tap \"Charge now\" first and then refund part of it.");
    const r = await payments.releaseHold(ref, id, order, { by: U.who(auth), reason, note });
    return { ok: true, released: true, amount: dollars(check.amountCents), refundedTotal: 0, status: "canceled", emailed: r.emailed };
  }
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
    const makeLink = async (tax) => {
      const k = tax ? "" : "-notax";
      const price = await stripe.request("POST", "/prices", { currency: "usd", unit_amount: amountCents,
        product_data: { name: title.slice(0, 240), ...(tax ? { tax_code: TAX_GOODS } : {}) }, ...(tax ? { tax_behavior: "exclusive" } : {}) },
        { idempotencyKey: `plink-price-${ref.id}${k}` });
      return stripe.request("POST", "/payment_links", {
        line_items: [{ price: price.id, quantity: 1 }],
        metadata: { orderId: ref.id },
        payment_intent_data: { metadata: { orderId: ref.id }, description: `Little Hive House: ${title}`.slice(0, 900), ...(chargeOnShip() ? { capture_method: "manual" } : {}) },
        ...(chargeOnShip() ? { custom_text: { submit: { message: HOLD_TEXT } } } : {}),
        shipping_address_collection: { allowed_countries: ["US", "CA"] },
        ...(tax ? { automatic_tax: { enabled: true } } : {}),
        restrictions: { completed_sessions: { limit: 1 } },
        after_completion: { type: "redirect", redirect: { url: `${siteUrl()}/thank-you.html?order=${ref.id}&session={CHECKOUT_SESSION_ID}` } },
      }, { idempotencyKey: `plink-${ref.id}${k}` });
    };
    // sales tax is added on top, from the customer's shipping address (falls back to no tax until Stripe Tax is set up)
    try { link = await makeLink(taxWanted()); } catch (err) {
      if (!taxWanted() || !isTaxSetupError(err)) throw err;
      console.warn("[paymentLink] Stripe Tax unavailable, continuing without tax:", err.message);
      link = await makeLink(false);
    }
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
    if (k === "printCutIn" && (n < 2.1 || n > 2.55)) fail("invalid-argument", "The punch size should be between 2.10 and 2.55 inches (measure a piece the punch cut).");
    if (k === "printImageIn" && (n < 2 || n > 2.3)) fail("invalid-argument", "The picture size should be between 2.00 and 2.30 inches.");
    if (k === "autoNewsletter" && n !== 0 && n !== 1) fail("invalid-argument", "Automatic emails are on (1) or off (0).");
    if (k === "printEnhance" && n !== 0 && n !== 1) fail("invalid-argument", "The photo touch-up is on (1) or off (0).");
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

/* Phone photos are 3-12 MB; drawing several of them on the order page froze the admin on iPhone. The page shows a
   small copy instead (thumbs/<path>.jpg, 800 px, made once with sharp) and links to the original. */
const THUMB_PX = 800;
async function thumbUrl(bucket, path) {
  const tp = `thumbs/${path.replace(/\.[A-Za-z0-9]+$/, "")}.jpg`;
  const file = bucket.file(tp);
  let exists = false;
  try { [exists] = await file.exists(); } catch (e) { exists = false; }
  if (!exists) {
    try {
      const sharp = require("./printsheet")._internal.loadSharp();
      const [buf] = await bucket.file(path).download();
      const jpg = await sharp(buf, { failOn: "none", limitInputPixels: 120e6, animated: false }).rotate()
        .resize(THUMB_PX, THUMB_PX, { fit: "inside", withoutEnlargement: true }).flatten({ background: "#FFFFFF" }).jpeg({ quality: 82 }).toBuffer();
      await file.save(jpg, { contentType: "image/jpeg", resumable: false, metadata: { cacheControl: "private, max-age=86400" } });
    } catch (err) {
      console.warn("[adminPhotoUrls] no thumbnail for", path, err && err.message);
      return null;
    }
  }
  return photoUrl(bucket, tp);
}

async function adminPhotoUrls(data, auth) {
  U.requireAdmin(auth);
  const { order } = await loadOrder(data && data.orderId);
  const packs = (order.items || []).map((it, index) => ({ it, index })).filter(({ it }) => it.kind === "photos");
  if (!packs.length) return { packs: [] };
  const bucket = deps.bucket();
  const out = [];
  for (const { it, index } of packs) {
    const list = it.photos || [];
    const photos = new Array(list.length);
    let next = 0;
    const worker = async () => {
      while (next < list.length) {
        const n = next++, p = list[n];
        const [url, thumb] = p.path ? await Promise.all([photoUrl(bucket, p.path), thumbUrl(bucket, p.path)]) : [null, null];
        photos[n] = { n: n + 1, path: p.path, frame: p.frame, caption: p.caption || "", url, thumb: thumb || url };
      }
    };
    await Promise.all([worker(), worker(), worker()]);
    out.push({ index, packSize: it.packSize, qty: it.qty || 1, notes: it.notes || "", photos });
  }
  return { packs: out };
}

/* ---------- the print-ready PDFs (printsheet.js) ---------- */
/**
 * adminPrintSheet({orderId, rebuild?, which?: "sheet" | "slip"}) -> {url, expiresAt, rebuilt, which, printSheet}
 * Returns a short-lived link to the magnets PDF (orders/<id>/print-sheet.pdf, glossy paper) or, with which "slip",
 * the packing slip (packing-slip.pdf, plain paper); makes (or remakes, with rebuild) the PDFs first when needed.
 */
async function adminPrintSheet(data, auth) {
  U.requireAdmin(auth);
  const printsheet = require("./printsheet");
  const { ref, id, order } = await loadOrder(data && data.orderId);
  if (order.status === "pending") fail("failed-precondition", "This order hasn't been paid yet, so there is nothing to print.");
  const rebuild = !!(data && data.rebuild);
  const which = data && data.which === "slip" ? "slip" : "sheet";
  const pathOf = (m) => (m ? (which === "slip" ? m.slipPath : m.path) : null);
  // PDFs made with an older layout (v under 3) are made again
  let meta = order.printSheet && order.printSheet.v === 3 && (order.printSheet.path || order.printSheet.slipPath) ? order.printSheet : null;
  let exists = false;
  if (meta && !rebuild && pathOf(meta)) {
    try { exists = (await deps.bucket().file(pathOf(meta)).exists())[0] === true; } catch (err) { exists = false; }
  }
  let rebuilt = false;
  if (!exists) {
    try {
      meta = (await printsheet.generateForOrder(ref, id, order, { by: U.who(auth) })).meta;
    } catch (err) {
      console.error("[adminPrintSheet] build failed", id, err);
      fail("unavailable", `The print sheet could not be made (${(err && err.message) || "unknown error"}). Try again in a minute, or use the photo ZIP under More.`);
    }
    rebuilt = true;
  }
  if (!pathOf(meta)) fail("failed-precondition", which === "slip" ? "The packing slip could not be made." : "Nothing in this order prints on the magnet sheets (packages and custom orders are made by hand).");
  const link = await printsheet.downloadUrl(pathOf(meta), printsheet.fileName(order, which));
  return { ok: true, url: link.url, expiresAt: link.expiresAt, signed: link.signed, rebuilt, which, printSheet: meta };
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

/* ---------- test orders and test sheets ---------- */
/** Orders that may be deleted: never charged (free with a coupon, Stripe test mode, unpaid, or a card hold released). */
function deletable(o) {
  const total = Number((o.pricing && o.pricing.total) || 0);
  const testMode = String((o.stripe && o.stripe.sessionId) || "").startsWith("cs_test_") || (o.stripe && o.stripe.livemode === false);
  const charged = o.payment && o.payment.state === "captured";
  const held = o.payment && o.payment.state === "authorized";
  if (testMode) return true;
  if (held) return false;                                   // release the hold first (Refund), so the card isn't left blocked
  if (total <= 0) return true;                              // free (100% coupon): nothing was paid
  if (o.status === "pending" && !o.paidAt) return true;     // never paid
  return !!(!charged && o.payment && (o.payment.state === "released" || o.payment.state === "expired"));
}

/** adminDeleteOrder({orderId, confirm: "DELETE"}): removes a test order (see deletable) and its print files for good. */
async function adminDeleteOrder(data, auth) {
  U.requireAdmin(auth);
  const { ref, id, order } = await loadOrder(data && data.orderId);
  if (U.text(data && data.confirm, 20).toUpperCase() !== "DELETE") fail("failed-precondition", "Please confirm the delete.");
  if (!deletable(order)) {
    fail("failed-precondition", order.payment && order.payment.state === "authorized"
      ? "The customer's card is still on hold for this order. Cancel it first (Refund the whole amount), then delete."
      : "Only test orders can be deleted: free orders, unpaid ones, or ones never charged. Orders with money in them stay for your records; refund them instead.");
  }
  try { await deps.bucket().deleteFiles({ prefix: `orders/${id}/` }); } catch (e) { /* no files */ }
  await ref.delete();
  console.log(`[adminDeleteOrder] ${order.number || id} deleted by ${U.who(auth)}`);
  return { ok: true, deleted: order.number || id };
}

const TEST_MAX_MAGNETS = 27;
/**
 * adminTestSheet({designs: [{id, qty}], photos: [{data (base64 JPEG/PNG), frame, caption, capStyle, qty}]})
 * -> {url, sheets, tiles}: a magnets PDF exactly like an order's, without an order. Saved at tests/test-sheet.pdf.
 */
async function adminTestSheet(data, auth) {
  U.requireAdmin(auth);
  const printsheet = require("./printsheet");
  const catalog = require("./catalog.json");
  const items = [];
  let count = 0;
  for (const d of (Array.isArray(data && data.designs) ? data.designs : []).slice(0, TEST_MAX_MAGNETS)) {
    const id = U.text(d && d.id, 120);
    const c = catalog.designs[id];
    if (!c) fail("invalid-argument", `Unknown design "${id}".`);
    const qty = Math.min(99, Math.max(1, Math.floor(Number(d.qty) || 1)));
    count += qty;
    items.push({ kind: "design", id, title: c.title, collection: c.collection, qty });
  }
  const photos = new Map(), keep = [];
  const list = (Array.isArray(data && data.photos) ? data.photos : []).slice(0, 9);
  for (let n = 0; n < list.length; n++) {
    const p = list[n] || {};
    let buf = null;
    const b64 = String(p.data || "").replace(/^data:image\/[a-z]+;base64,/, "");
    if (b64) buf = Buffer.from(b64, "base64");
    else if (typeof p.saved === "string" && TEST_SAVED_RE.test(p.saved)) {
      // a photo from the saved test sheet (adminLastTestSheet), still in Storage
      try { [buf] = await deps.bucket().file(p.saved).download(); } catch (err) { fail("not-found", `Photo ${n + 1} from the saved test sheet is gone. Add it again.`); }
    }
    if (!buf) continue;
    if (buf.length < 100 || buf.length > 8 * 1024 * 1024) fail("invalid-argument", `Photo ${n + 1} is too big or empty.`);
    const path = `test/${n + 1}.jpg`;
    photos.set(path, buf);
    const frame = U.text(p.frame, 40) || "none";
    const qty = Math.min(99, Math.max(1, Math.floor(Number(p.qty) || 1)));
    const caption = U.text(p.caption, 40), capStyle = U.text(p.capStyle, 20) || null;
    count += qty;
    items.push({ kind: "photos", packSize: qty, qty: 1, photos: [{ path, frame, caption, capStyle }] });
    keep.push({ buf, name: U.text(p.name, 80) || `Photo ${n + 1}`, frame, caption, capStyle, qty });
  }
  if (!items.length) fail("invalid-argument", "Add at least one design or photo.");
  if (count > TEST_MAX_MAGNETS) fail("invalid-argument", `That is ${count} magnets; a test sheet holds up to ${TEST_MAX_MAGNETS} (3 sheets).`);
  const settings = await printsheet.printSettings();
  const out = await printsheet.buildPrintSheetDetailed("test", { number: "TEST", name: "Test sheet", items, paidAt: nowIso() },
    { cut: settings.cut, image: settings.image, enhance: settings.enhance, readPhoto: async (p) => { if (!photos.has(p)) throw new Error("missing"); return photos.get(p); } });
  if (!out.pdf) fail("unavailable", "The test sheet could not be made.");
  const path = "tests/test-sheet.pdf";
  await deps.bucket().file(path).save(out.pdf, { contentType: "application/pdf", resumable: false, metadata: { cacheControl: "private, max-age=0" } });
  const link = await printsheet.downloadUrl(path, "TEST-magnets.pdf");
  let saved = false;
  try { await saveTestSheet(items.filter((i) => i.kind === "design"), keep); saved = true; } catch (err) { console.warn("[adminTestSheet] could not save the test sheet for next time", err && err.message); }
  return { ok: true, url: link.url, sheets: out.sheets, tiles: out.tiles, warnings: out.warnings, saved };
}

/* The last test sheet is kept (tests/last.json + its photos at tests/last/<n>.jpg) so it can be made again later,
   e.g. after a change to the print layout, without picking the designs and photos again. */
const TEST_SAVED_RE = /^tests\/last\/[1-9]\.jpg$/;
async function saveTestSheet(designs, photos) {
  const bucket = deps.bucket();
  const opts = { resumable: false, metadata: { cacheControl: "private, max-age=0" } };
  const out = { at: nowIso(), designs: designs.map((d) => ({ id: d.id, name: d.title || d.id, qty: d.qty })), photos: [] };
  for (let n = 0; n < photos.length; n++) {
    const p = photos[n], file = `tests/last/${n + 1}.jpg`;
    await bucket.file(file).save(p.buf, { ...opts, contentType: "image/jpeg" });
    out.photos.push({ saved: file, name: p.name, frame: p.frame, caption: p.caption, capStyle: p.capStyle, qty: p.qty });
  }
  for (let n = photos.length + 1; n <= 9; n++) { try { await bucket.file(`tests/last/${n}.jpg`).delete(); } catch (e) { /* not there */ } }
  await bucket.file("tests/last.json").save(Buffer.from(JSON.stringify(out)), { ...opts, contentType: "application/json" });
  return out;
}

/** adminLastTestSheet() -> {sheet: {at, designs, photos: [{saved, url, name, frame, caption, capStyle, qty}]} | null, pdfUrl} */
async function adminLastTestSheet(data, auth) {
  U.requireAdmin(auth);
  const printsheet = require("./printsheet");
  const bucket = deps.bucket();
  let sheet = null;
  try {
    const [buf] = await bucket.file("tests/last.json").download();
    sheet = JSON.parse(buf.toString("utf8"));
  } catch (err) { sheet = null; }
  if (sheet) {
    sheet.designs = Array.isArray(sheet.designs) ? sheet.designs : [];
    sheet.photos = Array.isArray(sheet.photos) ? sheet.photos.filter((p) => p && TEST_SAVED_RE.test(p.saved)) : [];
    for (const p of sheet.photos) { try { p.url = (await printsheet.downloadUrl(p.saved, p.saved.split("/").pop())).url; } catch (e) { p.url = null; } }
  }
  let pdfUrl = null;
  try { if ((await bucket.file("tests/test-sheet.pdf").exists())[0]) pdfUrl = (await printsheet.downloadUrl("tests/test-sheet.pdf", "TEST-magnets.pdf")).url; } catch (e) { pdfUrl = null; }
  return { sheet, pdfUrl };
}

module.exports = {
  adminDeleteOrder, adminTestSheet, adminLastTestSheet, deletable,
  claimAdmin, adminSetStatus, adminShip, adminCapture, adminMarkDelivered, adminRefund, adminAddNote, adminResendEmail,
  adminCreatePaymentLink, adminCreatePromo, adminListPromos, adminSaveSettings, adminPhotoUrls, adminModerateReview, adminPrintSheet,
  DEFAULT_SETTINGS, promoView, deliverOrder,
};
