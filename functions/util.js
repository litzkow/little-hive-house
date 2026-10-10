"use strict";
/* Input checks, auth checks and a tiny Firestore rate limiter shared by the handlers. */

const crypto = require("crypto");
const { fail, nowIso } = require("./config");
const deps = require("./deps");

const EMAIL_RE = /^[^\s@<>()",;:]+@[^\s@<>()",;:]+\.[a-z]{2,}$/i;

function cleanEmail(v, { required = true, field = "email" } = {}) {
  const e = typeof v === "string" ? v.trim().toLowerCase() : "";
  if (!e) { if (required) fail("invalid-argument", `Please enter your ${field}.`); return ""; }
  if (e.length > 200 || !EMAIL_RE.test(e)) fail("invalid-argument", "That email address doesn't look right.");
  return e;
}
function text(v, max, { required = false, field = "this field" } = {}) {
  const s = typeof v === "string" ? v.trim().slice(0, max) : (typeof v === "number" ? String(v) : "");
  if (required && !s) fail("invalid-argument", `Please fill in ${field}.`);
  return s;
}
/** Firestore doc id for an email (subscribers/{emailKey}). */
function emailKey(email) { return String(email).trim().toLowerCase().replace(/[/]/g, "_").slice(0, 300); }

function isAnonymous(auth) {
  return !!(auth && auth.token && auth.token.firebase && auth.token.firebase.sign_in_provider === "anonymous");
}
function requireAuth(auth) {
  if (!auth || !auth.uid) fail("unauthenticated", "Please sign in first.");
  return auth;
}
function requireAccount(auth) {
  requireAuth(auth);
  if (isAnonymous(auth)) fail("unauthenticated", "Please sign in to your account first.");
  return auth;
}
function requireAdmin(auth) {
  requireAuth(auth);
  if (!auth.token || auth.token.admin !== true) fail("permission-denied", "Only shop admins can do this. If you are an owner, open Admin and tap \"Activate admin access\".");
  return auth;
}
const who = (auth) => (auth && auth.token && auth.token.email) || (auth && auth.uid) || "system";

/**
 * Allows `max` calls per `windowS` seconds for (action, id). Throws resource-exhausted when over.
 * Fails open (allows) when Firestore is unavailable, so a hiccup never blocks a customer.
 */
async function rateLimit(action, id, max, windowS) {
  if (!id) return;
  const key = crypto.createHash("sha256").update(`${action}:${id}`).digest("hex").slice(0, 40);
  const ref = deps.db().collection("rateLimits").doc(key);
  let over = false;
  try {
    await deps.db().runTransaction(async (tx) => {
      const snap = await tx.get(ref);
      const now = Date.now();
      const d = snap.exists ? snap.data() : null;
      if (!d || now - d.start > windowS * 1000) { tx.set(ref, { action, start: now, count: 1, at: nowIso() }); return; }
      if (d.count >= max) { over = true; return; }
      tx.update(ref, { count: d.count + 1 });
    });
  } catch (err) {
    console.warn("[rateLimit] skipped", err && err.message);
    return;
  }
  if (over) fail("resource-exhausted", "That's a lot of tries. Please wait a few minutes and try again.");
}

function clientIp(rawRequest) {
  if (!rawRequest) return "";
  const xf = rawRequest.headers && rawRequest.headers["x-forwarded-for"];
  return (xf ? String(xf).split(",")[0] : rawRequest.ip || "").trim();
}

module.exports = { cleanEmail, text, emailKey, isAnonymous, requireAuth, requireAccount, requireAdmin, who, rateLimit, clientIp, EMAIL_RE };
