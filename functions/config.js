"use strict";
/* Environment and small shared helpers. Nothing here talks to Firebase, so it loads in plain `node --test`.
   Env (functions/.env, written by CI from the GitHub secret FUNCTIONS_ENV — never committed):
     STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET, RESEND_API_KEY, ADMIN_EMAILS, SITE_URL, MAIL_FROM, MAIL_ADMIN,
     UNSUBSCRIBE_SECRET (signs unsubscribe links), MAIL_POSTAL_ADDRESS (shown in every customer email footer, CAN-SPAM),
     USPS_CLIENT_ID + USPS_CLIENT_SECRET (automatic USPS tracking), SHIPPO_API_KEY (optional: UPS / FedEx / DHL tracking) */

const REGION = "us-east1";

/** Errors meant for the caller. index.js turns them into HttpsError(code, message). */
class AppError extends Error {
  constructor(code, message, details) {
    super(message);
    this.code = code;          // an HttpsError code: invalid-argument, not-found, permission-denied, ...
    this.details = details;
  }
}
const fail = (code, message, details) => { throw new AppError(code, message, details); };

function env(name) {
  const v = process.env[name];
  return typeof v === "string" ? v.trim() : "";
}

const HELP = {
  STRIPE_SECRET_KEY: "Payments are not set up yet (STRIPE_SECRET_KEY is missing). See SETUP.md.",
  STRIPE_WEBHOOK_SECRET: "The Stripe webhook is not set up yet (STRIPE_WEBHOOK_SECRET is missing). See SETUP.md.",
  RESEND_API_KEY: "Email is not set up yet (RESEND_API_KEY is missing). See SETUP.md.",
  ADMIN_EMAILS: "No admin emails are configured (ADMIN_EMAILS is missing). See SETUP.md.",
  SITE_URL: "SITE_URL is missing. See SETUP.md.",
};

/** Returns the env value or throws a clear failed-precondition error (and logs it for the owner). */
function need(name) {
  const v = env(name);
  if (!v) {
    console.error(`[config] missing env ${name}`);
    fail("failed-precondition", HELP[name] || `${name} is not set. See SETUP.md.`);
  }
  return v;
}

function siteUrl() { return (env("SITE_URL") || "https://littlehivehouse.com").replace(/\/+$/, ""); }
function mailFrom() { return env("MAIL_FROM") || "Little Hive House <hello@littlehivehouse.com>"; }
function mailAdmin() { return env("MAIL_ADMIN") || "support@littlehivehouse.com"; }
function adminEmails() {
  return env("ADMIN_EMAILS").split(",").map((s) => s.trim().toLowerCase()).filter(Boolean);
}

const nowIso = () => new Date().toISOString();

module.exports = { REGION, AppError, fail, env, need, siteUrl, mailFrom, mailAdmin, adminEmails, nowIso };
