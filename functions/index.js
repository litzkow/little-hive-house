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
const payments = lazy("./payments");
const push = lazy("./push");
const newsletter = lazy("./newsletter");

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
// orderBySession may confirm the payment itself (before the webhook) and then builds the print sheet: give it room
exports.orderBySession = callable("orderBySession", checkout, null, { timeoutSeconds: 120, memory: "1GiB" });
exports.subscribe = callable("subscribe", pub);
exports.unsubscribe = callable("unsubscribe", pub);
exports.setMarketing = callable("setMarketing", pub);
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
exports.adminCapture = callable("adminCapture", admin);
exports.adminPush = callable("adminPush", push);
exports.adminMarkDelivered = callable("adminMarkDelivered", admin);
exports.adminRefund = callable("adminRefund", admin);
exports.adminAddNote = callable("adminAddNote", admin);
exports.adminResendEmail = callable("adminResendEmail", admin);
exports.adminCreatePaymentLink = callable("adminCreatePaymentLink", admin);
exports.adminCreatePromo = callable("adminCreatePromo", admin);
exports.adminListPromos = callable("adminListPromos", admin);
exports.adminSaveSettings = callable("adminSaveSettings", admin);
// makes small copies of the customer photos for the order page (sharp): more memory than the other callables
exports.adminPhotoUrls = callable("adminPhotoUrls", admin, null, { timeoutSeconds: 120, memory: "1GiB" });
exports.adminModerateReview = callable("adminModerateReview", admin);
// emails to the subscribers (newsletter.js): a send can take a few minutes for a big list
exports.adminNewsletter = callable("adminNewsletter", newsletter, null, { timeoutSeconds: 540, memory: "512MiB" });
// builds the print-ready PDF (sharp + pdfkit) on demand: more memory and time than the other callables
exports.adminPrintSheet = callable("adminPrintSheet", admin, null, { timeoutSeconds: 300, memory: "1GiB" });

/* ---------- Stripe webhook (HTTP): marks orders paid and renders their print sheet (1 GiB, 300 s for the PDF) ---------- */
exports.stripeWebhook = onRequest({ region: REGION, timeoutSeconds: 300, memory: "1GiB", maxInstances: 10 }, async (req, res) => {
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
// the 1st and 15th, 10 am: the automatic email to the subscribers (newsletter.js autoNewsletter)
exports.autoNewsletter = onSchedule({ region: REGION, schedule: "0 10 1,15 * *", timeZone: "America/New_York", timeoutSeconds: 540, memory: "512MiB" }, async () => {
  const r = await newsletter().autoNewsletter();
  console.log("[autoNewsletter]", JSON.stringify(r));
});

exports.trackShipments = onSchedule({ region: REGION, schedule: "every 2 hours", timeZone: "America/New_York", timeoutSeconds: 300, memory: "256MiB" }, async () => {
  await tracking().trackShipments();
  await payments().checkHolds().catch((err) => console.warn("[checkHolds] failed", err.message));
  await scheduled().backfillFees().catch((err) => console.warn("[backfillFees] failed", err.message));
});

/* ---------- monthly: Georgia sales tax return reminder (due the 20th) ---------- */
exports.salesTaxReminder = onSchedule({ region: REGION, schedule: "0 9 12 * *", timeZone: "America/New_York" }, async () => {
  await require("./salestax").salesTaxReminder();
});

/* ---------- daily ---------- */
exports.deliveredFollowUp = onSchedule({ region: REGION, schedule: "every day 09:00", timeZone: "America/New_York" }, async () => {
  await scheduled().deliveredFollowUp();
});
