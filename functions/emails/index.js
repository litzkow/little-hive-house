// Little Hive House emails: render(kind, data) -> {subject, html, text, preheader, replyTo?, headers?}
// Amounts are dollars (numbers), dates may be Firestore Timestamps, Dates, ISO strings or millis.
// SITE_URL comes from data.siteUrl or process.env.SITE_URL (default https://littlehivehouse.com).
"use strict";

const F = require("./format");
const { page } = require("./layout");

const KINDS = {
  order_confirmation: require("./kinds/order_confirmation"),
  shipped: require("./kinds/shipped"),
  out_for_delivery: require("./kinds/out_for_delivery"),
  delivered_review: require("./kinds/delivered_review"),
  refund: require("./kinds/refund"),
  welcome: require("./kinds/welcome"),
  password_reset: require("./kinds/password_reset"),
  verify_email: require("./kinds/verify_email"),
  abandoned_checkout: require("./kinds/abandoned_checkout"),
  admin_new_order: require("./kinds/admin_new_order"),
  admin_dispute: require("./kinds/admin_dispute"),
  admin_delivery_check: require("./kinds/admin_delivery_check"),
  contact_autoreply: require("./kinds/contact_autoreply"),
  admin_contact: require("./kinds/admin_contact"),
  quote_received: require("./kinds/quote_received"),
  admin_quote: require("./kinds/admin_quote"),
  payment_link: require("./kinds/payment_link"),
  newsletter_welcome: require("./kinds/newsletter_welcome"),
};
/** Kinds that are marketing (need consent + unsubscribe link). */
const MARKETING = new Set(["abandoned_checkout", "newsletter_welcome"]);

/** Accepts the nested shapes the backend sends ({contact}, {quote}, {paymentLink}) as well as flat data. */
function normalize(kind, d) {
  const pick = (o) => (o && typeof o === "object" && !Array.isArray(o) ? o : null);
  let x = { ...d };
  if (pick(d.contact)) x = { ...x, ...d.contact };
  if (kind === "quote_received" && pick(d.quote)) x = { ...x, ...d.quote };
  if (kind === "payment_link" && pick(d.paymentLink)) x = { ...x, ...d.paymentLink };
  const o = pick(d.order);
  if (!x.name && o && o.name) x.name = o.name;
  if (!x.name && d.firstName) x.name = d.firstName;
  return x;
}

/**
 * Render one email.
 * @param {string} kind one of Object.keys(KINDS)
 * @param {object} data see README in the report / each kinds/*.js
 * @returns {{subject:string, html:string, text:string, preheader:string, replyTo?:string, headers?:object}}
 */
function render(kind, data) {
  const build = Object.prototype.hasOwnProperty.call(KINDS, kind) ? KINDS[kind] : null;
  if (!build) throw new Error(`Unknown email kind: ${kind}`);
  const d = normalize(kind, data && typeof data === "object" ? data : {});
  const L = F.links(F.siteUrl(d));
  L.fromOrder(d.order);
  const out = build(d, { L });
  const subject = F.line(out.subject, 160);
  const marketing = MARKETING.has(kind) || !!out.marketing;
  const unsub = F.safeUrl(out.unsubscribeUrl || d.unsubscribeUrl);
  const { html, text } = page({
    title: subject,
    preheader: F.line(out.preheader, 200),
    blocks: out.blocks,
    links: L,
    audience: out.audience || "customer",
    marketing,
    unsubscribeUrl: unsub,
    reason: out.reason,
    postalAddress: d.postalAddress,
  });
  const result = { subject, html, text, preheader: F.line(out.preheader, 200) };
  if (out.replyTo) result.replyTo = out.replyTo;
  if (marketing && unsub) result.headers = { "List-Unsubscribe": `<${unsub}>, <mailto:${F.SUPPORT}?subject=unsubscribe>` };
  return result;
}

module.exports = { render, KINDS: Object.keys(KINDS), MARKETING: [...MARKETING], trackingUrl: F.trackingUrl, carrierName: F.carrierName, money: F.money };
