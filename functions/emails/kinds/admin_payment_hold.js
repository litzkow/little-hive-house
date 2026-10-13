// Sent to MAIL_ADMIN by payments.js (charge on ship): two days before a card hold ends (mode "due"), and when it ended
// before the order was charged (mode "expired").
"use strict";
const F = require("../format");
const Lay = require("../layout");
const O = require("../order-parts");

module.exports = function adminPaymentHold(data, { L }) {
  const order = data.order || {};
  const id = O.orderId(data);
  const num = F.line(order.number, 30) || "an order";
  const amount = F.money(order.pricing && order.pricing.total, order.pricing && order.pricing.currency);
  const p = order.payment || {};
  const until = F.fmtDate(p.captureBefore, true);
  const open = { href: id ? L.admin(id) : L.adminHome, label: "Open order", variant: "ink" };

  if (data.mode === "expired") {
    return {
      subject: `Card hold expired on ${num} (${amount})`,
      preheader: "Nothing was charged. Send the customer a payment link to collect it.",
      audience: "admin",
      blocks: [
        Lay.hero({ eyebrow: "Charge on ship", title: `The card hold on ${num} ended`, lead: [`The order wasn't shipped or charged in time, so Stripe released the ${amount} hold. Nothing was charged and the order is now canceled.`] }),
        Lay.facts([["Customer", [F.line(order.name, 80), order.email ? ` · ${F.line(order.email, 120)}` : ""]], ["Amount", amount]]),
        Lay.p(["To still make it: open Links in Hive Admin, create a payment link for the amount and send it to the customer. When they pay, it becomes a new order."], { small: true }),
        Lay.buttons([open, { href: L.adminHome + "#links", label: "Payment links", variant: "ghost" }]),
      ],
    };
  }
  const hours = Math.max(1, Math.round(Number(data.hoursLeft) || 0));
  return {
    subject: `Ship or charge ${num} soon: the card hold ends${until ? " " + until : ""}`,
    preheader: `About ${hours} hours left to charge ${amount}.`,
    audience: "admin",
    blocks: [
      Lay.hero({ eyebrow: "Charge on ship", title: `${num}: card hold ends soon`, lead: [`The customer's card is held for ${amount} until ${until || "in about two days"}. Ship it (marking it shipped charges the card) or tap "Charge now" on the order before then.`] }),
      Lay.box(Lay.bodyText("<strong style=\"font-weight:600\">After the hold ends the order can't be charged anymore.</strong> You would need to send the customer a new payment link.", { size: 15, lh: 22 }),
        "After the hold ends the order can't be charged anymore. You would need to send the customer a new payment link.", "alert", { pad: "14px 18px" }),
      Lay.facts([["Customer", [F.line(order.name, 80), order.email ? ` · ${F.line(order.email, 120)}` : ""]], ["Amount", amount], ["Hold ends", until], ["Order status", F.pretty(order.status)]]),
      Lay.buttons([open]),
    ],
  };
};
