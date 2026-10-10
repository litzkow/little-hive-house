"use strict";
/* Public callables: subscribe, contact, requestQuote, sendPasswordReset, welcome, submitReview, unsubscribe. */

const { fail, siteUrl, mailAdmin, nowIso, env } = require("./config");
const deps = require("./deps");
const stripe = require("./stripe");
const mail = require("./mail");
const U = require("./util");
const customer = require("./customer");

async function subscribe(data, auth, rawRequest) {
  const email = U.cleanEmail(data && data.email);
  const source = U.text(data && data.source, 40) || "site";
  await U.rateLimit("subscribe", U.clientIp(rawRequest) || email, 10, 3600);
  const db = deps.db();
  const ref = db.collection("subscribers").doc(U.emailKey(email));
  let fresh = false;
  await db.runTransaction(async (tx) => {
    const s = await tx.get(ref);
    if (s.exists && !s.data().unsubscribed) return;
    fresh = true;
    tx.set(ref, { email, at: nowIso(), source, unsubscribed: false });
  });
  if (fresh) await mail.send({ to: email, kind: "newsletter_welcome", data: { email } });
  return { ok: true, already: !fresh };
}

async function unsubscribe(data) {
  const email = U.cleanEmail(data && data.e);
  const t = U.text(data && data.t, 100);
  if (!mail.checkUnsubscribeToken(email, t)) fail("permission-denied", "This unsubscribe link is not valid. Reply to any of our emails and we will remove you by hand.");
  const db = deps.db();
  await db.collection("subscribers").doc(U.emailKey(email)).set({ email, unsubscribed: true, unsubscribedAt: nowIso() }, { merge: true });
  const users = await db.collection("users").where("email", "==", email).limit(5).get();
  await Promise.all(users.docs.map((d) => d.ref.update({ marketing: false })));
  return { ok: true };
}

async function contact(data, auth, rawRequest) {
  const name = U.text(data && data.name, 120, { required: true, field: "your name" });
  const email = U.cleanEmail(data && data.email);
  const message = U.text(data && data.message, 5000, { required: true, field: "your message" });
  const topic = U.text(data && data.topic, 80) || "General";
  if (data && data.website) return { ok: true };            // honeypot field: bots fill it, people don't see it
  await U.rateLimit("contact", U.clientIp(rawRequest) || email, 5, 3600);
  const doc = { name, email, message, topic, orderNumber: U.text(data && data.orderNumber, 30), at: nowIso(), status: "new", uid: auth ? auth.uid : null };
  const ref = await deps.db().collection("messages").add(doc);
  const c = { name, email, topic, message, orderNumber: U.text(data && data.orderNumber, 30), at: doc.at };
  await mail.send({ to: mailAdmin(), kind: "admin_contact", data: { ...c, contact: c, messageId: ref.id }, replyTo: email });
  await mail.send({ to: email, kind: "contact_autoreply", data: { ...c, contact: c } });
  return { ok: true, id: ref.id };
}

async function requestQuote(data, auth, rawRequest) {
  const d = data || {};
  const quote = {
    name: U.text(d.name, 120, { required: true, field: "your name" }),
    email: U.cleanEmail(d.email),
    phone: U.text(d.phone, 40),
    occasion: U.text(d.occasion, 80) || "Something else",
    package: U.text(d.package, 60),
    quantity: Math.max(0, Math.min(100000, parseInt(d.quantity, 10) || 0)),
    date: U.text(d.date, 40),
    message: U.text(d.message, 5000),
  };
  if (d.website) return { ok: true };
  await U.rateLimit("quote", U.clientIp(rawRequest) || quote.email, 5, 3600);
  const ref = await deps.db().collection("quotes").add({ ...quote, at: nowIso(), status: "new", uid: auth ? auth.uid : null });
  const at = nowIso();
  await mail.send({ to: mailAdmin(), kind: "admin_quote", data: { ...quote, quote, quoteId: ref.id, at }, replyTo: quote.email });
  await mail.send({ to: quote.email, kind: "quote_received", data: { ...quote, quote } });
  return { ok: true, id: ref.id };
}

async function sendPasswordReset(data, auth, rawRequest) {
  const email = U.cleanEmail(data && data.email);
  await U.rateLimit("reset", email, 5, 3600);
  await U.rateLimit("reset-ip", U.clientIp(rawRequest), 20, 3600);
  if (!env("RESEND_API_KEY")) fail("failed-precondition", "Email is not set up yet. Please write to support@littlehivehouse.com.");
  let link;
  try {
    link = await deps.auth().generatePasswordResetLink(email, { url: `${siteUrl()}/account.html` });
  } catch (err) {
    // never tell strangers whether an account exists
    if (err && /user-not-found|email-not-found/.test(err.code || err.message)) return { ok: true };
    console.error("[sendPasswordReset]", err);
    fail("unavailable", "We couldn't send the reset email right now. Please try again in a few minutes.");
  }
  const res = await mail.send({ to: email, kind: "password_reset", data: { link, email, expiresMinutes: 60 } });
  if (res.skipped) fail("unavailable", "We couldn't send the reset email right now. Please try again in a few minutes.");
  return { ok: true };
}

/**
 * welcome({name?, marketing?}) after sign-up (and again from the account page once the email is verified):
 * creates users/{uid}, sends the welcome email once, sends the "confirm your email" email once while unverified,
 * and links guest orders placed with the verified email (customer.linkGuestOrders). Returns {ok, welcomed, verifySent, linked}.
 */
async function welcome(data, auth) {
  U.requireAccount(auth);
  const db = deps.db();
  const ref = db.collection("users").doc(auth.uid);
  const email = String(auth.token.email || "").toLowerCase();
  const name = U.text((data && data.name) || auth.token.name, 80);
  const marketing = !!(data && data.marketing === true);
  const verified = auth.token.email_verified === true;
  let send = false, verify = false;
  await db.runTransaction(async (tx) => {
    const s = await tx.get(ref);
    const cur = s.exists ? s.data() : {};
    const upd = { email };
    if (!cur.createdAt) upd.createdAt = nowIso();
    if (name && !cur.name) upd.name = name;
    if (cur.marketing === undefined) upd.marketing = marketing;
    if (!Array.isArray(cur.favorites)) upd.favorites = [];
    if (!cur.welcomedAt && email) { upd.welcomedAt = nowIso(); send = true; }
    if (!verified && email && !cur.verifySentAt) { upd.verifySentAt = nowIso(); verify = true; }
    tx.set(ref, upd, { merge: true });
  });
  let verifySent = false;
  if (verify) {
    try { verifySent = !(await customer.sendVerification(auth, { name })).skipped; } catch (e) { verifySent = false; }
    if (!verifySent) await ref.set({ verifySentAt: null }, { merge: true }).catch(() => {});   // the account page offers "Resend"
  }
  const linked = verified ? await customer.linkGuestOrders(auth) : 0;
  if (marketing && email) {
    await db.collection("subscribers").doc(U.emailKey(email)).set({ email, at: nowIso(), source: "account", unsubscribed: false }, { merge: true });
  }
  if (send) {
    let promo = null;
    if (env("STRIPE_SECRET_KEY")) {
      try {
        const r = await stripe.request("GET", "/promotion_codes", { code: "WELCOME10", active: true, limit: 1, expand: ["data.coupon"] });
        const p = r.data && r.data[0];
        if (p) {
          const c = p.coupon || {};
          promo = { code: p.code, percentOff: c.percent_off || null, amountOff: c.amount_off ? c.amount_off / 100 : null,
            expiresAt: p.expires_at ? new Date(p.expires_at * 1000).toISOString() : null,
            text: c.percent_off ? `${c.percent_off}% off` : c.amount_off ? `$${(c.amount_off / 100).toFixed(2)} off` : "a discount" };
        }
      } catch (e) { promo = null; }
    }
    await mail.send({ to: email, kind: "welcome", data: { name, email, firstName: name.split(/\s+/)[0] || "", promo } });
  }
  return { ok: true, welcomed: send, verifySent, linked };
}

/** submitReview({orderId, designId, rating, text}) — buyers only, one review per order + item, published by an admin. */
async function submitReview(data, auth) {
  U.requireAccount(auth);
  const orderId = U.text(data && data.orderId, 64, { required: true, field: "the order" });
  const designId = U.text(data && data.designId, 120, { required: true, field: "the item" });
  const rating = Number(data && data.rating);
  if (!Number.isInteger(rating) || rating < 1 || rating > 5) fail("invalid-argument", "Please choose 1 to 5 stars.");
  const text = U.text(data && data.text, 2000);
  if (!/^[A-Za-z0-9]+$/.test(orderId)) fail("not-found", "We couldn't find that order.");
  const db = deps.db();
  const snap = await db.collection("orders").doc(orderId).get();
  if (!snap.exists) fail("not-found", "We couldn't find that order.");
  const o = snap.data();
  const email = String(auth.token.email || "").toLowerCase();
  const mine = o.uid === auth.uid || (auth.token.email_verified === true && email && email === String(o.email || "").toLowerCase());
  if (!mine) fail("permission-denied", "Only the person who placed this order can review it.");
  if (!["paid", "in_production", "shipped", "delivered", "partially_refunded"].includes(o.status)) fail("failed-precondition", "You can review items from paid orders.");
  const items = o.items || [];
  const ok = items.some((it) => (it.kind === "design" && it.id === designId) || (it.kind === "package" && it.id === designId)) ||
    (designId === "photo-magnets" && items.some((it) => it.kind === "photos"));
  if (!ok) fail("invalid-argument", "That item isn't in this order.");
  let name = U.text(data && data.name, 60);
  if (!name) {
    const u = await db.collection("users").doc(auth.uid).get();
    const full = (u.exists && u.data().name) || o.name || "";
    const parts = full.trim().split(/\s+/).filter(Boolean);
    name = parts.length ? parts[0] + (parts.length > 1 ? ` ${parts[parts.length - 1][0]}.` : "") : "A happy customer";
  }
  const id = `${orderId}_${designId.replace(/[^A-Za-z0-9-]/g, "_")}`;
  const ref = db.collection("reviews").doc(id);
  const prev = await ref.get();
  if (prev.exists && prev.data().status === "published") fail("already-exists", "You already reviewed this item. Thank you!");
  const at = nowIso();
  await ref.set({ orderId, designId, rating, text, name, uid: auth.uid, status: "pending", createdAt: (prev.exists && prev.data().createdAt) || at, updatedAt: at });
  return { ok: true, id, status: "pending" };
}

module.exports = { subscribe, unsubscribe, contact, requestQuote, sendPasswordReset, welcome, submitReview };
