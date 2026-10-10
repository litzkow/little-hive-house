"use strict";
/* Little Hive House store backend: Cloud Functions 2nd gen, region us-east1, Node 22.
   Only this file touches firebase-functions; the logic lives in small modules that load without it (tested with
   `node --test`). Callable names are a contract with the site and admin pages — see STORE_SPEC. */

const { REGION, AppError } = require("./config");

const { onCall, onRequest, HttpsError } = require("firebase-functions/v2/https");
const { onSchedule } = require("firebase-functions/v2/scheduler");
const { setGlobalOptions } = require("firebase-functions/v2");

setGlobalOptions({ region: REGION, maxInstances: 10 });

// Loaded on first use so a cold start only pays for what it runs.
const lazy = (path) => { let m; return () => (m = m || require(path)); };
const checkout = lazy("./checkout");
const admin = lazy("./admin");
const pub = lazy("./public");
const webhook = lazy("./webhook");
const scheduled = lazy("./scheduled");
const customer = lazy("./customer");
const tracking = lazy("./tracking");

const HTTPS_CODES = new Set(["cancelled", "unknown", "invalid-argument", "deadline-exceeded", "not-found", "already-exists",
  "permission-denied", "resource-exhausted", "failed-precondition", "aborted", "out-of-range", "unimplemented", "internal",
  "unavailable", "data-loss", "unauthenticated"]);

/** Wraps a handler(data, auth, rawRequest): AppErrors become HttpsErrors with the same friendly message. */
function callable(name, mod, fnName, opts = {}) {
  return onCall({ region: REGION, ...opts }, async (request) => {
    try {
      return await mod()[fnName || name](request.data || {}, request.auth || null, request.rawRequest);
    } catch (err) {
      if (err instanceof HttpsError) throw err;
      if (err instanceof AppError) {
        throw new HttpsError(HTTPS_CODES.has(err.code) ? err.code : "internal", err.message, err.details);
      }
      console.error(`[${name}] unexpected error`, err);
      throw new HttpsError("internal", "Something went wrong on our side. Please try again in a minute.");
    }
  });
}

/* ---------- public ---------- */
exports.createCheckout = callable("createCheckout", checkout, null, { timeoutSeconds: 60, memory: "256MiB" });
exports.trackOrder = callable("trackOrder", checkout);
exports.orderBySession = callable("orderBySession", checkout);
exports.subscribe = callable("subscribe", pub);
exports.unsubscribe = callable("unsubscribe", pub);
exports.contact = callable("contact", pub);
exports.requestQuote = callable("requestQuote", pub);
exports.sendPasswordReset = callable("sendPasswordReset", pub);
exports.welcome = callable("welcome", pub);
exports.submitReview = callable("submitReview", pub);

/* ---------- signed-in customers (their own orders, email confirmation) ---------- */
exports.myOrders = callable("myOrders", customer);
exports.myOrder = callable("myOrder", customer);
exports.sendVerifyEmail = callable("sendVerifyEmail", customer);

/* ---------- admin (each checks the admin claim) ---------- */
exports.claimAdmin = callable("claimAdmin", admin);
exports.adminSetStatus = callable("adminSetStatus", admin);
exports.adminShip = callable("adminShip", admin);
exports.adminMarkDelivered = callable("adminMarkDelivered", admin);
exports.adminRefund = callable("adminRefund", admin);
exports.adminAddNote = callable("adminAddNote", admin);
exports.adminResendEmail = callable("adminResendEmail", admin);
exports.adminCreatePaymentLink = callable("adminCreatePaymentLink", admin);
exports.adminCreatePromo = callable("adminCreatePromo", admin);
exports.adminListPromos = callable("adminListPromos", admin);
exports.adminSaveSettings = callable("adminSaveSettings", admin);
exports.adminPhotoUrls = callable("adminPhotoUrls", admin);
exports.adminModerateReview = callable("adminModerateReview", admin);

/* ---------- Stripe webhook (HTTP) ---------- */
exports.stripeWebhook = onRequest({ region: REGION, timeoutSeconds: 120, maxInstances: 10 }, async (req, res) => {
  if (req.method !== "POST") { res.set("Allow", "POST").status(405).send("Method not allowed"); return; }
  try {
    const out = await webhook().handleWebhook(req.rawBody, req.get("stripe-signature"));
    res.status(out.status).send(out.body);
  } catch (err) {
    console.error("[stripeWebhook] unexpected error", err);
    res.status(500).send("error");
  }
});

/* ---------- automatic delivery tracking: every 2 hours (tracking.js) ---------- */
exports.trackShipments = onSchedule({ region: REGION, schedule: "every 2 hours", timeZone: "America/New_York", timeoutSeconds: 300, memory: "256MiB" }, async () => {
  await tracking().trackShipments();
});

/* ---------- daily ---------- */
exports.deliveredFollowUp = onSchedule({ region: REGION, schedule: "every day 09:00", timeZone: "America/New_York" }, async () => {
  await scheduled().deliveredFollowUp();
});
