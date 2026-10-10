"use strict";
/* Sends email through Resend's REST API (fetch). Templates come from ./emails (render(kind, data) -> {subject, html, text}),
   written separately; until that folder exists a plain fallback keeps everything working.

   Data every kind gets (added here): siteUrl, supportEmail, logoUrl, year, and for marketing kinds unsubscribeUrl.
   Kind-specific data (built in the handlers):
     order_confirmation, shipped, out_for_delivery, delivered_review, admin_new_order: {order}   (orders.emailOrder: the
                        stored order + id, firstName, links{order,track,review,shop,admin}, items[] with lineTotal and thumb,
                        photo packs with photos:[{frame, caption}], fulfillment with trackingStatus + events[{at,text,location}];
                        shipped adds fulfillment.autoUpdates when automatic tracking follows the carrier)
     refund:            {order, refund:{amount, reason, reasonLabel, note (shown to the customer), full, refundedTotal, remaining}}
     admin_dispute:     {order|null, dispute:{id, reason, amount, status, evidenceDueBy}}
     abandoned_checkout:{order}   (+ unsubscribeUrl)
     admin_delivery_check: {now, orders:[{id, number, name, email, carrier, carrierName, tracking, url, shippedAt, days, adminUrl}]}
                        trackShipments sends it with mode:"tracking" and an `issue` sentence on each order
     verify_email:      {link, email, name}
     welcome:           {name, email, firstName, promo:{code, percentOff, amountOff, expiresAt, text}|null}   (+ unsubscribeUrl)
     password_reset:    {link, email, expiresMinutes}
     contact_autoreply, admin_contact: {name, email, topic, message, orderNumber, at, contact:{same}}
     quote_received, admin_quote: {name, email, phone, occasion, package, quantity, date, message, quote:{same}}
     payment_link:      {order, paymentLink:{url, title, amount, note}}
     newsletter_welcome:{email}   (+ unsubscribeUrl)
*/

const crypto = require("crypto");
const { env, siteUrl, mailFrom, mailAdmin, AppError } = require("./config");

const MARKETING = new Set(["welcome", "abandoned_checkout", "newsletter_welcome"]);

let renderer = null;
function getRenderer() {
  if (renderer) return renderer;
  try {
    const mod = require("./emails");
    if (mod && typeof mod.render === "function") { renderer = mod.render; return renderer; }
    console.warn("[mail] ./emails has no render(); using the plain fallback");
  } catch (err) {
    if (!(err && err.code === "MODULE_NOT_FOUND" && String(err.message).includes("./emails"))) {
      console.error("[mail] ./emails failed to load; using the plain fallback", err);
    }
  }
  renderer = fallbackRender;
  return renderer;
}

const SUBJECTS = {
  order_confirmation: (d) => `Thank you! Order ${(d.order && d.order.number) || ""} is confirmed`,
  shipped: (d) => `Your order ${(d.order && d.order.number) || ""} is on its way`,
  delivered_review: (d) => `Your magnets have arrived`,
  out_for_delivery: () => "Your magnets arrive today!",
  verify_email: () => "Please confirm your email for Little Hive House",
  refund: (d) => `Your refund for order ${(d.order && d.order.number) || ""}`,
  welcome: () => "Welcome to Little Hive House",
  password_reset: () => "Reset your Little Hive House password",
  abandoned_checkout: () => "You left something in your cart",
  admin_new_order: (d) => `New order ${(d.order && d.order.number) || ""}`,
  admin_dispute: (d) => `Dispute opened on order ${(d.order && d.order.number) || ""}`,
  admin_delivery_check: (d) => `${(d.orders || []).length} shipped orders not marked delivered`,
  contact_autoreply: () => "We got your message",
  admin_contact: (d) => `New message: ${(d.contact && d.contact.topic) || "contact form"}`,
  admin_quote: (d) => `Big order request from ${d.name || "a customer"}`,
  quote_received: () => "We got your big order request",
  payment_link: (d) => `Your Little Hive House payment link${d.paymentLink && d.paymentLink.title ? ": " + d.paymentLink.title : ""}`,
  newsletter_welcome: () => "You're on the Little Hive House list",
};

function fallbackRender(kind, data) {
  const subject = (SUBJECTS[kind] || (() => "Little Hive House"))(data || {}).replace(/\s+/g, " ").trim();
  const lines = [subject, ""];
  const d = data || {};
  if (d.order) {
    lines.push(`Order: ${d.order.number || d.order.id}`);
    (d.order.items || []).forEach((it) => lines.push(`- ${it.title} x ${it.qty || 1}`));
    if (d.order.pricing && d.order.pricing.total !== undefined) lines.push(`Total: $${Number(d.order.pricing.total).toFixed(2)}`);
    if (d.order.fulfillment && d.order.fulfillment.url) lines.push(`Tracking: ${d.order.fulfillment.url}`);
    if (d.order.links) lines.push(`Your order: ${d.order.links.order}`);
  }
  if (d.refund) lines.push(`Refund: $${Number(d.refund.amount).toFixed(2)}`);
  if (d.link) lines.push(d.link);
  if (d.paymentLink) lines.push(`Pay here: ${d.paymentLink.url}`);
  if (d.contact) lines.push(`${d.contact.name} <${d.contact.email}>`, d.contact.message || "");
  if (d.quote) lines.push(JSON.stringify(d.quote, null, 2));
  if (d.orders) d.orders.forEach((o) => lines.push(`- ${o.number} ${o.name} shipped ${o.days} days ago ${o.url || ""}`));
  lines.push("", `Questions? ${d.supportEmail}`, d.siteUrl || "");
  if (d.unsubscribeUrl) lines.push(`Unsubscribe: ${d.unsubscribeUrl}`);
  const text = lines.join("\n");
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  return { subject, text, html: `<pre style="font-family:Arial,sans-serif;white-space:pre-wrap">${esc(text)}</pre>` };
}

/* ---------- unsubscribe tokens ---------- */
function unsubscribeKey() { return env("UNSUBSCRIBE_SECRET") || env("RESEND_API_KEY") || ""; }
function unsubscribeToken(email, key = unsubscribeKey()) {
  if (!key) return "";
  return crypto.createHmac("sha256", "lhh-unsubscribe:" + key).update(String(email).trim().toLowerCase()).digest("hex").slice(0, 32);
}
function checkUnsubscribeToken(email, token, key = unsubscribeKey()) {
  const want = unsubscribeToken(email, key);
  if (!want || typeof token !== "string" || token.length !== want.length) return false;
  return crypto.timingSafeEqual(Buffer.from(want), Buffer.from(token));
}
function unsubscribeUrl(email) {
  return `${siteUrl()}/unsubscribe.html?e=${encodeURIComponent(email)}&t=${unsubscribeToken(email)}`;
}

function baseData(kind, to, data) {
  const out = {
    siteUrl: siteUrl(), supportEmail: mailAdmin(), logoUrl: `${siteUrl()}/assets/email/logo.png`,
    year: new Date().getFullYear(), ...data,
  };
  if (MARKETING.has(kind) && to && !out.unsubscribeUrl) out.unsubscribeUrl = unsubscribeUrl(Array.isArray(to) ? to[0] : to);
  return out;
}

/**
 * send({to, kind, data, replyTo, required}) -> {id} | {skipped:true, reason}
 * Never throws for a missing key or a Resend failure unless `required` (then an AppError the admin sees).
 */
async function send({ to, kind, data = {}, replyTo, required = false, fetchImpl }) {
  const key = env("RESEND_API_KEY");
  if (!to) return { skipped: true, reason: "no recipient" };
  if (!key) {
    console.warn(`[mail] RESEND_API_KEY missing; not sending ${kind} to ${to}`);
    if (required) throw new AppError("failed-precondition", "Email is not set up yet (RESEND_API_KEY is missing). See SETUP.md.");
    return { skipped: true, reason: "no key" };
  }
  const d = baseData(kind, to, data);
  let msg;
  try {
    msg = getRenderer()(kind, d);
    if (!msg || !msg.subject || !(msg.html || msg.text)) throw new Error("render returned no subject/body");
  } catch (err) {
    console.error(`[mail] render ${kind} failed; using fallback`, err);
    msg = fallbackRender(kind, d);
  }
  const payload = { from: mailFrom(), to: Array.isArray(to) ? to : [to], subject: msg.subject, html: msg.html, text: msg.text };
  if (replyTo || msg.replyTo) payload.reply_to = replyTo || msg.replyTo;
  if (msg.headers && typeof msg.headers === "object") payload.headers = msg.headers;
  else if (d.unsubscribeUrl && MARKETING.has(kind)) payload.headers = { "List-Unsubscribe": `<${d.unsubscribeUrl}>` };
  try {
    const res = await (fetchImpl || fetch)("https://api.resend.com/emails", {
      method: "POST",
      headers: { Authorization: `Bearer ${key}`, "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const json = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(`Resend ${res.status}: ${json.message || json.name || "error"}`);
    return { id: json.id };
  } catch (err) {
    console.error(`[mail] sending ${kind} to ${to} failed`, err && err.message);
    if (required) throw new AppError("unavailable", `The email could not be sent (${err.message}).`);
    return { skipped: true, reason: err.message };
  }
}

module.exports = { send, fallbackRender, unsubscribeToken, checkUnsubscribeToken, unsubscribeUrl, MARKETING, mailAdmin };
