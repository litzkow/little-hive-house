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
const labels = lazy("./labels");
const analytics = lazy("./analytics");
const returns = lazy("./returns");
const supplies = lazy("./supplies");
const ads = lazy("./ads");
const content = lazy("./content");
const social = lazy("./social");

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
exports.suggest = callable("suggest", pub);
exports.requestQuote = callable("requestQuote", pub);
exports.sendPasswordReset = callable("sendPasswordReset", pub);
exports.welcome = callable("welcome", pub);
exports.submitReview = callable("submitReview", pub);
// returns from the site (returns.js): find the order, price a change-of-mind return, start it (label or photos)
exports.returnLookup = callable("returnLookup", returns);
exports.returnQuote = callable("returnQuote", returns, null, { timeoutSeconds: 60 });
exports.returnStart = callable("returnStart", returns, null, { timeoutSeconds: 120 });

/* ---------- signed-in customers (their own orders, email confirmation) ---------- */
exports.myOrders = callable("myOrders", customer);
exports.myOrder = callable("myOrder", customer);
exports.sendVerifyEmail = callable("sendVerifyEmail", customer);

/* ---------- admin (each checks the admin claim) ---------- */
exports.claimAdmin = callable("claimAdmin", admin);
exports.adminSetStatus = callable("adminSetStatus", admin);
exports.adminShip = callable("adminShip", admin);
exports.adminLabelQuote = callable("adminLabelQuote", labels, null, { timeoutSeconds: 60 });
exports.adminBuyLabel = callable("adminBuyLabel", labels, null, { timeoutSeconds: 120 });
exports.adminLabelPdf = callable("adminLabelPdf", labels, null, { timeoutSeconds: 60, memory: "512MiB" });
exports.adminCapture = callable("adminCapture", admin);
exports.adminPush = callable("adminPush", push);
exports.adminMarkDelivered = callable("adminMarkDelivered", admin);
exports.adminRefund = callable("adminRefund", admin);
exports.adminAddNote = callable("adminAddNote", admin);
exports.adminPhotoFraming = callable("adminPhotoFraming", admin);
exports.adminResendEmail = callable("adminResendEmail", admin);
exports.adminPreviewEmail = callable("adminPreviewEmail", admin);
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
exports.adminEtsy = callable("adminEtsy", () => require("./etsy"), null, { timeoutSeconds: 300, memory: "512MiB" });
// TikTok Shop (tiktok.js): connection, products, orders
exports.adminTikTok = callable("adminTikTok", () => require("./tiktok"), null, { timeoutSeconds: 300, memory: "512MiB" });
exports.adminPrintBatch = callable("adminPrintBatch", admin, null, { timeoutSeconds: 540, memory: "2GiB" });
// a test PDF of designs / photos without an order, and deleting test orders
exports.adminTestSheet = callable("adminTestSheet", admin, null, { timeoutSeconds: 300, memory: "1GiB" });
exports.adminLastTestSheet = callable("adminLastTestSheet", admin);
exports.adminDeleteOrder = callable("adminDeleteOrder", admin);
// the "Visitas" page: Google Analytics (analytics.js)
exports.adminReturnDecide = callable("adminReturnDecide", returns, null, { timeoutSeconds: 300, memory: "1GiB" });
exports.adminReturnPhotos = callable("adminReturnPhotos", returns);
// Materiais (supplies.js): what the shop has, what orders used, purchases
exports.adminSupplies = callable("adminSupplies", supplies, null, { timeoutSeconds: 60 });
exports.adminContent = callable("adminContent", content, null, { timeoutSeconds: 120 });
// Instagram & Facebook: comments, Direct, product tags (social.js)
exports.adminSocial = callable("adminSocial", social, null, { timeoutSeconds: 300, memory: "512MiB" });
exports.adminAds = callable("adminAds", ads, null, { timeoutSeconds: 300, memory: "512MiB" });
exports.adminAnalytics = callable("adminAnalytics", analytics, null, { timeoutSeconds: 60 });
exports.adminAnalyticsLive = callable("adminAnalyticsLive", analytics, null, { timeoutSeconds: 30 });

/* ---------- problems customers hit on the site (clientlog.js), sent by navigator.sendBeacon ---------- */
exports.clientLog = onRequest({ region: REGION, timeoutSeconds: 30, memory: "256MiB", maxInstances: 3, cors: ["https://littlehivehouse.com", "https://www.littlehivehouse.com"] }, async (req, res) => {
  if (req.method !== "POST") { res.set("Allow", "POST").status(405).send("Method not allowed"); return; }
  try {
    const out = await require("./clientlog").handle(req.rawBody || req.body, require("./util").clientIp(req));
    res.status(out.status).send(out.body);
  } catch (err) {
    console.error("[clientLog] unexpected error", err);
    res.status(500).send("error");
  }
});

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
  await returns().checkReturns().catch((err) => console.warn("[checkReturns] failed", err.message));
});

/* ---------- every 3 hours: the 28-day visits report stays fresh (analytics.js warm) ---------- */
exports.analyticsWarm = onSchedule({ region: REGION, schedule: "every 3 hours", timeZone: "America/New_York", timeoutSeconds: 120 }, async () => {
  console.log("[analyticsWarm]", JSON.stringify(await analytics().warm()));
});

/* ---------- monthly: Georgia sales tax return reminder (due the 20th) ---------- */
exports.salesTaxReminder = onSchedule({ region: REGION, schedule: "0 9 12 * *", timeZone: "America/New_York" }, async () => {
  await require("./salestax").salesTaxReminder();
});

/* ---------- daily ---------- */
exports.deliveredFollowUp = onSchedule({ region: REGION, schedule: "every day 09:00", timeZone: "America/New_York" }, async () => {
  await scheduled().deliveredFollowUp();
  // customer photos older than 90 days (privacy page)
  await scheduled().deletePhotos().catch((err) => console.warn("[deletePhotos] failed", err.message));
  // materials that got low (supplies.js)
  await supplies().checkSupplies().catch((err) => console.warn("[checkSupplies] failed", err.message));
});

/* ---------- every morning: the ads robot reads what each channel spent and sold, and acts inside the teto (ads.js) ---------- */
/* ---------- every 15 minutes: the paid Etsy orders come into Hive Admin (etsy-orders.js) ---------- */
exports.etsyOrders = onSchedule({ region: REGION, schedule: "every 15 minutes", timeZone: "America/New_York", timeoutSeconds: 300, memory: "256MiB" }, async () => {
  try { await require("./etsy-orders").importOrders(); } catch (e) { console.warn("[etsyOrders]", e.message); }
  // the TikTok Shop orders ready to ship come in the same way (tiktok-orders.js), and new products' review is checked
  try { await require("./tiktok-orders").importOrders(); } catch (e) { console.warn("[tiktokOrders]", e.message); }
  try { await require("./tiktok-products").refresh({ onlyPending: true }); } catch (e) { console.warn("[tiktokProducts]", e.message); }
  try { await require("./tiktok-promotions").sync(); } catch (e) { console.warn("[tiktokPromos]", e.message); }
});

/* ---------- every 10 minutes: Instagram & Facebook looked after (social.js): products tagged on the posts, comments and Direct ---------- */
exports.socialSync = onSchedule({ region: REGION, schedule: "every 10 minutes", timeZone: "America/New_York", timeoutSeconds: 300, memory: "512MiB" }, async () => {
  await social().socialSync();
});

/* ---------- every 5 minutes: what was scheduled in the app goes out on Instagram / Facebook (content.js) ---------- */
exports.contentPublish = onSchedule({ region: REGION, schedule: "every 5 minutes", timeZone: "America/New_York", timeoutSeconds: 300, memory: "512MiB" }, async () => {
  const r = await content().publishDue();
  // what is scheduled or already out on Instagram and Facebook is checked here too (every 10 minutes), without anyone opening the app
  try { await content().syncMeta(); } catch (e) { console.log("[contentPublish] sync", e.message); }
  // the Reel the owners asked to boost as soon as it's out
  try { const n = await ads().boostNextReel(); if (n.boosted) console.log("[contentPublish] next reel", JSON.stringify(n)); } catch (e) { console.log("[contentPublish] next reel", e.message); }
  if (r.done || r.processing || r.error) console.log("[contentPublish]", JSON.stringify(r));
});

exports.adsDaily = onSchedule({ region: REGION, schedule: "every day 07:40", timeZone: "America/New_York", timeoutSeconds: 300, memory: "512MiB" }, async () => {
  const r = await ads().run({ by: "robot" });
  console.log("[adsDaily]", JSON.stringify({ total: r.totals.total, did: r.did.length, errors: r.errors }));
});
