// Makes sure the store's Stripe webhook endpoint (the one pointing at the stripeWebhook function) is subscribed to
// every event functions/webhook.js handles. Run by .github/workflows/firebase.yml after each deploy, with
// STRIPE_SECRET_KEY from GitHub secrets (never printed). Works for test and live keys alike.
"use strict";
const path = require("path");
const { HANDLED } = require(path.join(__dirname, "../../functions/webhook.js"));

const key = (process.env.STRIPE_SECRET_KEY || "").trim();
if (!key) { console.log("STRIPE_SECRET_KEY is not set; skipping the webhook check."); process.exit(0); }
const mode = key.startsWith("sk_live_") || key.startsWith("rk_live_") ? "live" : "test";

async function stripe(method, p, params) {
  const body = params ? new URLSearchParams(params).toString() : undefined;
  const res = await fetch(`https://api.stripe.com/v1${p}`, {
    method, body, headers: { Authorization: `Bearer ${key}`, ...(body ? { "Content-Type": "application/x-www-form-urlencoded" } : {}) },
  });
  const json = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(`${res.status} ${(json.error && json.error.message) || ""}`);
  return json;
}

(async () => {
  const list = await stripe("GET", "/webhook_endpoints?limit=100");
  const ours = (list.data || []).filter((e) => /stripeWebhook/i.test(e.url || ""));
  if (!ours.length) {
    console.log(`::warning title=Stripe webhook::No ${mode}-mode webhook endpoint points at stripeWebhook yet (see SETUP.md).`);
    return;
  }
  const need = [...HANDLED];
  for (const e of ours) {
    const have = e.enabled_events || [];
    if (have.includes("*")) { console.log(`${mode} webhook ${e.id}: listens to all events.`); continue; }
    const missing = need.filter((t) => !have.includes(t));
    if (!missing.length) { console.log(`${mode} webhook ${e.id}: all ${need.length} events on.`); continue; }
    const params = new URLSearchParams();
    [...new Set(have.concat(need))].forEach((t, i) => params.append(`enabled_events[${i}]`, t));
    await stripe("POST", `/webhook_endpoints/${e.id}`, Object.fromEntries(params));
    console.log(`${mode} webhook ${e.id}: added ${missing.join(", ")}.`);
  }
})().catch((err) => {
  console.log(`::warning title=Stripe webhook::Could not check the webhook events (${err.message}).`);
});
