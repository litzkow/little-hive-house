"use strict";
/* Stripe over plain REST (fetch, form-encoded) and webhook signature checks with node crypto. No Stripe SDK. */

const crypto = require("crypto");
const { AppError, need } = require("./config");

const API = "https://api.stripe.com/v1";
// Pinned so the response shapes this code reads never change under us (e.g. shipping_details, charge.refunds).
const STRIPE_VERSION = "2024-06-20";
const TOLERANCE_S = 300;

/** Stripe's form encoding: a[b][0][c]=v. Skips undefined/null. */
function encode(params, prefix, out = []) {
  if (params === undefined || params === null) return out;
  if (Array.isArray(params)) {
    params.forEach((v, i) => encode(v, `${prefix}[${i}]`, out));
  } else if (typeof params === "object") {
    for (const [k, v] of Object.entries(params)) encode(v, prefix ? `${prefix}[${k}]` : k, out);
  } else {
    out.push(`${encodeURIComponent(prefix)}=${encodeURIComponent(String(params))}`);
  }
  return out;
}
const form = (params) => encode(params).join("&");

class StripeError extends Error {
  constructor(status, body) {
    const e = (body && body.error) || {};
    super(e.message || `Stripe request failed (${status})`);
    this.status = status;
    this.type = e.type;
    this.code = e.code;
  }
}

/** request("POST", "/checkout/sessions", {...}, {idempotencyKey}) -> parsed JSON. */
async function request(method, path, params, opts = {}) {
  const key = need("STRIPE_SECRET_KEY");
  let url = API + path;
  const headers = { Authorization: `Bearer ${key}`, "Stripe-Version": STRIPE_VERSION };
  let body;
  if (method === "GET" || method === "DELETE") {
    const q = form(params || {});
    if (q) url += (url.includes("?") ? "&" : "?") + q;
  } else {
    headers["Content-Type"] = "application/x-www-form-urlencoded";
    body = form(params || {});
  }
  if (opts.idempotencyKey) headers["Idempotency-Key"] = opts.idempotencyKey;
  let res;
  try {
    res = await (opts.fetch || fetch)(url, { method, headers, body });
  } catch (err) {
    console.error("[stripe] network error", path, err && err.message);
    throw new AppError("unavailable", "We couldn't reach Stripe. Please try again in a minute.");
  }
  let json = null;
  try { json = await res.json(); } catch (e) { json = null; }
  if (!res.ok) {
    const err = new StripeError(res.status, json);
    console.error("[stripe]", method, path, res.status, err.type, err.code, err.message);
    throw err;
  }
  return json;
}

/** Turns a Stripe failure into a friendly AppError (for callables). */
function friendly(err, what) {
  if (err instanceof AppError) return err;
  if (err instanceof StripeError) {
    if (err.status === 401) return new AppError("failed-precondition", "The Stripe secret key is not valid. Check STRIPE_SECRET_KEY (see SETUP.md).");
    if (err.status >= 400 && err.status < 500) return new AppError("failed-precondition", `Stripe said: ${err.message}`);
    return new AppError("unavailable", `Stripe is having trouble ${what || "right now"}. Please try again in a minute.`);
  }
  return new AppError("internal", `Something went wrong ${what || ""}. Please try again.`.replace(/\s+\./, "."));
}

/**
 * Verifies a Stripe-Signature header (t=...,v1=...[,v1=...]) over `${t}.${rawBody}` with HMAC-SHA256.
 * Returns the parsed event; throws Error("...") on any problem. Empty secrets are always rejected.
 */
function verifyWebhook(rawBody, header, secret, opts = {}) {
  const tolerance = opts.tolerance === undefined ? TOLERANCE_S : opts.tolerance;
  const now = opts.now === undefined ? Math.floor(Date.now() / 1000) : opts.now;
  if (!secret || typeof secret !== "string" || !secret.trim()) throw new Error("webhook secret is not configured");
  if (!header || typeof header !== "string") throw new Error("missing Stripe-Signature header");
  if (rawBody === undefined || rawBody === null) throw new Error("missing body");
  const body = Buffer.isBuffer(rawBody) ? rawBody.toString("utf8") : String(rawBody);
  let t = null;
  const sigs = [];
  for (const part of header.split(",")) {
    const i = part.indexOf("=");
    if (i < 0) continue;
    const k = part.slice(0, i).trim(), v = part.slice(i + 1).trim();
    if (k === "t") t = v;
    else if (k === "v1") sigs.push(v);
  }
  if (!t || !/^\d+$/.test(t)) throw new Error("signature has no timestamp");
  if (!sigs.length) throw new Error("signature has no v1 value");
  const expected = crypto.createHmac("sha256", secret.trim()).update(`${t}.${body}`, "utf8").digest("hex");
  const exp = Buffer.from(expected, "utf8");
  const ok = sigs.some((s) => {
    const got = Buffer.from(s, "utf8");
    return got.length === exp.length && crypto.timingSafeEqual(got, exp);
  });
  if (!ok) throw new Error("signature does not match");
  if (tolerance > 0 && Math.abs(now - Number(t)) > tolerance) throw new Error("signature timestamp is too old");
  try { return JSON.parse(body); } catch (e) { throw new Error("body is not JSON"); }
}

/** Builds a header the way Stripe does (used by tests). */
function signPayload(body, secret, t = Math.floor(Date.now() / 1000)) {
  const sig = crypto.createHmac("sha256", secret).update(`${t}.${body}`, "utf8").digest("hex");
  return `t=${t},v1=${sig}`;
}

module.exports = { request, encode, form, verifyWebhook, signPayload, friendly, StripeError, STRIPE_VERSION };
