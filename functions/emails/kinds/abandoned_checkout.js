// Sent once by stripeWebhook checkout.session.expired, only with marketing consent.
"use strict";
const F = require("../format");
const Lay = require("../layout");
const O = require("../order-parts");

module.exports = function abandonedCheckout(data, { L }) {
  const order = data.order || {};
  const first = F.firstName(order.name || data.name);
  const url = F.safeUrl(data.checkoutUrl) || `${L.shop}?cart=open`;
  const count = O.magnetCount(order);
  return {
    subject: first ? `${first}, your magnets are still waiting` : "Your magnets are still waiting for you",
    preheader: count ? `We saved your ${F.plural(count, "magnet")}. Pick up right where you left off.` : "We saved your cart. Pick up right where you left off.",
    blocks: [
      Lay.hero({
        eyebrow: "Saved for you",
        title: "Still thinking it over?",
        lead: [first ? `Hi ${first}! ` : "", "Your checkout timed out before it was finished, so nothing was charged. Your picks are right where you left them."],
      }),
      O.itemList(order, L),
      O.totals(order),
      Lay.buttons([{ href: url, label: "Return to checkout", variant: "honey" }], { full: true }),
      Lay.p(["Questions about sizes, frames or a big order? Just reply, we answer every email ourselves."], { muted: true, small: true, center: true }),
    ],
    reason: "You're getting this email because you started a checkout at littlehivehouse.com and agreed to hear from us.",
    marketing: true,
    unsubscribeUrl: data.unsubscribeUrl,
  };
};
