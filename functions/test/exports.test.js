"use strict";
/* index.js must export every function named in the store spec, with the right trigger type and region.
   firebase-functions can't be installed here, so it is replaced by a recording stub. */
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("fs");
const path = require("path");
const Module = require("module");

const CALLABLES = [
  "createCheckout", "trackOrder", "orderBySession", "subscribe", "contact", "requestQuote", "sendPasswordReset", "welcome",
  "submitReview", "unsubscribe", "myOrders", "myOrder", "sendVerifyEmail",
  "claimAdmin", "adminSetStatus", "adminShip", "adminMarkDelivered", "adminRefund", "adminAddNote", "adminResendEmail",
  "adminCreatePaymentLink", "adminCreatePromo", "adminListPromos", "adminSaveSettings", "adminPhotoUrls", "adminModerateReview",
];
const HTTP = ["stripeWebhook"];
const SCHEDULED = ["deliveredFollowUp", "trackShipments"];

class HttpsError extends Error { constructor(code, message, details) { super(message); this.code = code; this.details = details; } }
const stubs = {
  "firebase-functions/v2/https": {
    HttpsError,
    onCall: (opts, handler) => Object.assign(handler, { __kind: "callable", __opts: opts }),
    onRequest: (opts, handler) => Object.assign(handler, { __kind: "http", __opts: opts }),
  },
  "firebase-functions/v2/scheduler": { onSchedule: (opts, handler) => Object.assign(handler, { __kind: "schedule", __opts: opts }) },
  "firebase-functions/v2": { setGlobalOptions: (o) => { stubs.__global = o; } },
};

function loadIndex() {
  const orig = Module._load;
  Module._load = function (request, parent, isMain) {
    if (Object.prototype.hasOwnProperty.call(stubs, request)) return stubs[request];
    if (request.startsWith("firebase-admin")) throw new Error(`index.js must not load ${request} at import time`);
    return orig.apply(this, arguments);
  };
  try {
    delete require.cache[require.resolve("../index.js")];
    return require("../index.js");
  } finally {
    Module._load = orig;
  }
}

test("every callable, HTTP and scheduled function in the spec is exported", () => {
  const idx = loadIndex();
  for (const n of CALLABLES) {
    assert.equal(typeof idx[n], "function", `missing callable ${n}`);
    assert.equal(idx[n].__kind, "callable", `${n} should be onCall`);
    assert.equal(idx[n].__opts.region, "us-east1", `${n} region`);
  }
  for (const n of HTTP) assert.equal(idx[n] && idx[n].__kind, "http", n);
  for (const n of SCHEDULED) assert.equal(idx[n] && idx[n].__kind, "schedule", n);
  assert.equal(stubs.__global.region, "us-east1");
  const extra = Object.keys(idx).filter((k) => ![...CALLABLES, ...HTTP, ...SCHEDULED].includes(k));
  assert.deepEqual(extra, [], "unexpected exports");
});

test("the source names match too (static check)", () => {
  const src = fs.readFileSync(path.join(__dirname, "..", "index.js"), "utf8");
  for (const n of [...CALLABLES, ...HTTP, ...SCHEDULED]) assert.match(src, new RegExp(`exports\\.${n}\\s*=`), n);
});

test("admin callables refuse non-admins with permission-denied / unauthenticated", async () => {
  const idx = loadIndex();
  const admins = CALLABLES.filter((n) => n.startsWith("admin"));
  for (const n of admins) {
    await assert.rejects(idx[n]({ data: {}, auth: null }), (e) => e instanceof HttpsError && e.code === "unauthenticated", `${n} anonymous`);
    await assert.rejects(idx[n]({ data: {}, auth: { uid: "u1", token: { email: "x@y.com" } } }),
      (e) => e instanceof HttpsError && e.code === "permission-denied", `${n} non-admin`);
    await assert.rejects(idx[n]({ data: {}, auth: { uid: "u1", token: { email: "x@y.com", admin: "true" } } }),
      (e) => e instanceof HttpsError && e.code === "permission-denied", `${n} string claim`);
  }
});

test("customer callables need a real (not anonymous) account", async () => {
  const idx = loadIndex();
  for (const n of ["myOrders", "myOrder", "sendVerifyEmail"]) {
    await assert.rejects(idx[n]({ data: {}, auth: null }), (e) => e instanceof HttpsError && e.code === "unauthenticated", `${n} signed out`);
    await assert.rejects(idx[n]({ data: {}, auth: { uid: "a1", token: { firebase: { sign_in_provider: "anonymous" } } } }),
      (e) => e instanceof HttpsError && e.code === "unauthenticated", `${n} anonymous`);
  }
  assert.equal(idx.trackShipments.__opts.schedule, "every 2 hours");
});

test("missing env gives a clear failed-precondition error, not a crash", async () => {
  const idx = loadIndex();
  const saved = { ...process.env };
  delete process.env.STRIPE_SECRET_KEY;
  try {
    await assert.rejects(idx.createCheckout({ data: { cart: [{ kind: "design", id: "places/new-york", qty: 1 }] }, auth: null }),
      (e) => e instanceof HttpsError && e.code === "failed-precondition" && /STRIPE_SECRET_KEY/.test(e.message) && /SETUP/.test(e.message));
    const admin = { uid: "a", token: { admin: true, email: "a@b.com" } };
    await assert.rejects(idx.adminListPromos({ data: {}, auth: admin }), (e) => e.code === "failed-precondition");
    await assert.rejects(idx.adminRefund({ data: { orderId: "x" }, auth: admin }), (e) => e.code === "failed-precondition");
    delete process.env.ADMIN_EMAILS;
    await assert.rejects(idx.claimAdmin({ data: {}, auth: { uid: "u", token: { email: "a@b.com", email_verified: true, firebase: { sign_in_provider: "password" } } } }),
      (e) => e.code === "failed-precondition" && /ADMIN_EMAILS/.test(e.message));
  } finally {
    process.env = saved;
  }
});

test("webhook answers 500 (Stripe retries) when its secret is missing, 405 on GET", async () => {
  const idx = loadIndex();
  const saved = { ...process.env };
  delete process.env.STRIPE_WEBHOOK_SECRET;
  const res = { code: 0, body: "", headers: {}, status(c) { this.code = c; return this; }, send(b) { this.body = b; return this; }, set(k, v) { this.headers[k] = v; return this; } };
  try {
    await idx.stripeWebhook({ method: "POST", rawBody: Buffer.from("{}"), get: () => "t=1,v1=x" }, res);
    assert.equal(res.code, 500);
    await idx.stripeWebhook({ method: "GET", get: () => "" }, res);
    assert.equal(res.code, 405);
  } finally {
    process.env = saved;
  }
});
