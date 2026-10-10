"use strict";
/* Signed-in customer callables: myOrders(), myOrder({id}), sendVerifyEmail(), plus the guest-order linking used by welcome().
   Customers never read orders/{id} directly (firestore.rules: admins only), because the stored order holds admin notes,
   Stripe fees, label costs and photo paths. They get the same whitelisted view as trackOrder (orders.publicOrderView),
   plus their own shipping address and gift message.

   Which orders are "mine":
     - uid == my uid (ordered while signed in), or
     - guestUid == my uid and no uid (ordered as a guest in this browser, then created the account: same uid), or
     - my email is VERIFIED, the order's email is the same and it has no uid (guest orders placed with my email).
       welcome() then writes uid onto those orders so they stay mine. */

const { fail, siteUrl, nowIso, env } = require("./config");
const deps = require("./deps");
const mail = require("./mail");
const O = require("./orders");
const U = require("./util");

const MAX_ORDERS = 200;

/** The caller's email when Firebase says it is verified, else "". */
function verifiedEmail(auth) {
  const t = (auth && auth.token) || {};
  return t.email_verified === true && t.email ? String(t.email).trim().toLowerCase() : "";
}

/** Pure: does this order belong to the signed-in caller? */
function ownsOrder(o, auth) {
  if (!o || !auth || !auth.uid) return false;
  if (o.uid) return o.uid === auth.uid;
  if (o.guestUid && o.guestUid === auth.uid) return true;
  const email = verifiedEmail(auth);
  return !!(email && String(o.email || "").trim().toLowerCase() === email);
}

const createdMs = (o) => { const t = Date.parse(o.paidAt || o.createdAt || ""); return Number.isFinite(t) ? t : 0; };

/** All of the caller's orders as [{id, data}], paid or later, newest first. */
async function findMine(auth) {
  const col = deps.db().collection("orders");
  const email = verifiedEmail(auth);
  const snaps = await Promise.all([
    col.where("uid", "==", auth.uid).limit(MAX_ORDERS).get(),
    col.where("guestUid", "==", auth.uid).limit(MAX_ORDERS).get(),
    email ? col.where("email", "==", email).limit(MAX_ORDERS).get() : Promise.resolve({ docs: [] }),
  ]);
  const byId = new Map();
  for (const s of snaps) for (const d of s.docs) if (!byId.has(d.id)) byId.set(d.id, d.data());
  return [...byId.entries()]
    .filter(([, o]) => ownsOrder(o, auth) && o.status && o.status !== "pending")
    .sort((a, b) => createdMs(b[1]) - createdMs(a[1]))
    .slice(0, MAX_ORDERS)
    .map(([id, data]) => ({ id, data }));
}

/** myOrders() -> {orders: [public view]} */
async function myOrders(data, auth) {
  U.requireAccount(auth);
  const mine = await findMine(auth);
  return { orders: mine.map(({ id, data: o }) => O.publicOrderView(id, o, { owner: true })) };
}

/** myOrder({id}) -> public view of one of the caller's orders (not-found for anything else, so ids can't be probed). */
async function myOrder(data, auth) {
  U.requireAccount(auth);
  const id = U.text(data && data.id, 64, { required: true, field: "the order" });
  const nf = "We couldn't find this order in your account. If you ordered as a guest, track it with your order number and email.";
  if (!/^[A-Za-z0-9_-]+$/.test(id)) fail("not-found", nf);
  const snap = await deps.db().collection("orders").doc(id).get();
  const o = snap.exists ? snap.data() : null;
  if (!o || !ownsOrder(o, auth) || !o.status || o.status === "pending") fail("not-found", nf);
  return O.publicOrderView(id, o, { owner: true });
}

/**
 * Writes uid onto guest orders placed with the caller's verified email (and onto orders from this browser's guest
 * session). Returns how many were linked. Safe to call again: linked orders have a uid and are skipped.
 */
async function linkGuestOrders(auth) {
  const email = verifiedEmail(auth);
  const col = deps.db().collection("orders");
  const snaps = await Promise.all([
    email ? col.where("email", "==", email).limit(MAX_ORDERS).get() : Promise.resolve({ docs: [] }),
    col.where("guestUid", "==", auth.uid).limit(MAX_ORDERS).get(),
  ]);
  const seen = new Set();
  const todo = [];
  for (const s of snaps) {
    for (const d of s.docs) {
      if (seen.has(d.id)) continue;
      seen.add(d.id);
      const o = d.data();
      if (!o.uid && ownsOrder(o, auth)) todo.push(d.ref);
    }
  }
  const at = nowIso();
  const db = deps.db();
  let linked = 0;
  for (const ref of todo) {
    await db.runTransaction(async (tx) => {
      const s = await tx.get(ref);
      if (!s.exists || s.data().uid) return;              // someone else got there first
      tx.update(ref, { uid: auth.uid, linkedAt: at, updatedAt: at });
      linked++;
    });
  }
  if (linked) console.log(`[customer] linked ${linked} guest order(s) to ${auth.uid}`);
  return linked;
}

/**
 * Sends the branded "confirm your email" email (verify_email) with Firebase's verification link.
 * Used by welcome() right after sign-up and by sendVerifyEmail() (the "Resend" button). Returns the mail.send result.
 */
async function sendVerification(auth, { name } = {}) {
  const email = String(auth.token.email || "").trim().toLowerCase();
  if (!email) fail("failed-precondition", "This account has no email address.");
  let link;
  try {
    link = await deps.auth().generateEmailVerificationLink(email, { url: `${siteUrl()}/account.html?verified=1` });
  } catch (err) {
    console.error("[sendVerification]", err && (err.code || err.message));
    fail("unavailable", "We couldn't make your confirmation link right now. Please try again in a few minutes.");
  }
  const res = await mail.send({ to: email, kind: "verify_email", data: { link, email, name: name || auth.token.name || "" } });
  if (!res.skipped) await deps.db().collection("users").doc(auth.uid).set({ verifySentAt: nowIso() }, { merge: true }).catch(() => {});
  return res;
}

/** sendVerifyEmail() -> {ok, already?}: the account page's "Resend the email" button. */
async function sendVerifyEmail(data, auth) {
  U.requireAccount(auth);
  if (auth.token.email_verified === true) return { ok: true, already: true };
  await U.rateLimit("verify", auth.uid, 4, 3600);
  if (!env("RESEND_API_KEY")) fail("failed-precondition", "Email is not set up yet. Please write to support@littlehivehouse.com.");
  const res = await sendVerification(auth);
  if (res.skipped) fail("unavailable", "We couldn't send the email right now. Please try again in a few minutes.");
  return { ok: true };
}

module.exports = { myOrders, myOrder, sendVerifyEmail, sendVerification, linkGuestOrders, ownsOrder, verifiedEmail, findMine };
