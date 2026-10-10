// Sent to MAIL_ADMIN on charge.dispute.created.
"use strict";
const F = require("../format");
const Lay = require("../layout");
const O = require("../order-parts");

const REASONS = {
  fraudulent: "The cardholder says they didn't make this purchase",
  product_not_received: "The customer says the order never arrived",
  product_unacceptable: "The customer says the product was damaged or not as described",
  duplicate: "The customer says they were charged twice",
  subscription_canceled: "The customer says they canceled",
  credit_not_processed: "The customer says a promised refund never arrived",
  unrecognized: "The customer doesn't recognize the charge",
  general: "General dispute",
};

module.exports = function adminDispute(data, { L }) {
  const order = data.order || {};
  const d = data.dispute || {};
  const id = O.orderId(data);
  const num = F.line(order.number, 30) || "an order";
  const cur = d.currency || (order.pricing && order.pricing.currency);
  const amount = F.money(F.num(d.amount) || (order.pricing && order.pricing.total), cur);
  const due = F.fmtDate(d.evidenceDueBy || d.dueBy, true);
  const reason = REASONS[d.reason] || F.pretty(d.reason) || "Not given";
  const stripeUrl = /^dp_[A-Za-z0-9]+$/.test(F.str(d.id)) ? `https://dashboard.stripe.com/disputes/${d.id}` : "https://dashboard.stripe.com/disputes";
  const f = order.fulfillment || {};

  return {
    subject: `Action needed: dispute on ${num} (${amount})`,
    preheader: `${reason}.${due ? ` Respond in Stripe by ${due}.` : " Respond in Stripe soon."}`,
    audience: "admin",
    blocks: [
      Lay.hero({ eyebrow: "Payment dispute", title: `Dispute on ${num}`, lead: [`A customer's bank opened a dispute for ${amount}. Stripe holds the money until it's decided.`] }),
      Lay.box(Lay.bodyText(`<strong style="font-weight:600">Respond${due ? ` by ${F.esc(due)}` : " soon"}.</strong> If we don't answer in time, the dispute is lost automatically.`, { size: 15, lh: 22 }),
        `Respond${due ? ` by ${due}` : " soon"}. If we don't answer in time, the dispute is lost automatically.`, "alert", { pad: "14px 18px" }),
      Lay.facts([
        ["Reason", reason],
        ["Amount", amount],
        ["Status", F.pretty(d.status)],
        ["Customer", [F.line(order.name, 80), order.email ? ` · ${F.line(order.email, 120)}` : ""]],
        ["Order status", F.pretty(order.status)],
        ["Shipped", f.tracking ? `${F.carrierName(f.carrier, f.carrierName)} ${F.line(f.tracking, 60)}${f.shippedAt ? ` on ${F.fmtDate(f.shippedAt)}` : ""}` : "Not shipped yet"],
        ["Delivered", f.deliveredAt ? F.fmtDate(f.deliveredAt) : ""],
      ]),
      Lay.buttons([
        { href: stripeUrl, label: "Respond in Stripe", variant: "ink" },
        { href: id ? L.admin(id) : L.adminHome, label: "Open order", variant: "ghost" },
      ]),
      Lay.h2("Good evidence to send"),
      Lay.p(["Tracking number and delivery confirmation, the order confirmation email, photos of the magnets, and any messages with the customer. Stay polite and factual."], { small: true }),
    ],
  };
};
