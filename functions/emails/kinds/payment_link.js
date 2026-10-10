// Sent by adminCreatePaymentLink: a custom amount and a "Pay securely" button.
"use strict";
const F = require("../format");
const Lay = require("../layout");

module.exports = function paymentLink(data, { L }) {
  const first = F.firstName(data.name);
  const title = F.line(data.title, 120) || "Your custom order";
  const amount = F.money(data.amount, data.currency);
  const url = F.safeUrl(data.url);
  const note = F.str(data.note).trim().slice(0, 1500);
  const expires = F.fmtDate(data.expiresAt);
  return {
    subject: `Your payment link for ${title}`,
    preheader: `${amount} for ${title}. Pay securely by card, Apple Pay or Google Pay.`,
    blocks: [
      Lay.hero({ eyebrow: "Custom order", title: first ? `Here's your link, ${first}` : "Here's your payment link", lead: ["Thank you for trusting us with something special. When you're ready, you can pay below and we'll get started right away."] }),
      Lay.box(`${Lay.label(title)}<p class="lh-t" style="margin:2px 0 0;font-family:${Lay.FD};font-weight:700;font-size:40px;line-height:46px;color:${Lay.C.ink}">${F.esc(amount)}</p>` +
        (note ? Lay.bodyText(F.esc(note).replace(/\r?\n/g, "<br>"), { muted: true, size: 15, lh: 22, margin: "8px 0 0" }) : ""),
        `${title}: ${amount}${note ? `\n${note}` : ""}`, "honey", { center: true, pad: "24px 22px" }),
      Lay.buttons([{ href: url || L.contact, label: url ? "Pay securely" : "Contact us to pay", variant: "honey" }], { full: true }),
      Lay.p([`Payments are processed by Stripe. We never see or store your card number.${expires ? ` This link works until ${expires}.` : ""}`], { muted: true, small: true, center: true }),
      Lay.p(["Questions or changes before you pay? Just reply to this email."], { muted: true, small: true, center: true }),
    ],
    reason: "You're getting this email because you asked Little Hive House for a custom order.",
  };
};
