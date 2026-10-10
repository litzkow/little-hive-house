// Sent by adminRefund (and charge.refunded sync): full or partial refund.
"use strict";
const F = require("../format");
const Lay = require("../layout");
const O = require("../order-parts");

module.exports = function refund(data, { L }) {
  const order = data.order || {};
  const r = data.refund || {};
  const id = O.orderId(data);
  const num = F.line(order.number, 30);
  const first = F.firstName(order.name || (order.shipping && order.shipping.name));
  const cur = order.pricing && order.pricing.currency;
  const amount = F.num(r.amount);
  const total = F.num(order.pricing && order.pricing.total);
  const refundedTotal = F.num(r.refundedTotal) || F.num(order.refundedTotal) || amount;
  const full = typeof r.full === "boolean" ? r.full : typeof data.full === "boolean" ? data.full : total > 0 && refundedTotal >= total - 0.005;
  const why = F.refundReason(r.reason);
  const note = F.line(r.note, 400);

  const amountBox = Lay.box(
    `${Lay.label(full ? "Full refund" : "Partial refund")}<p class="lh-t" style="margin:2px 0 0;font-family:${Lay.FD};font-weight:700;font-size:38px;line-height:44px;color:${Lay.C.ink}">${F.esc(F.money(amount, cur))}</p>` +
    Lay.bodyText(`Back to your original payment method${num ? ` for order ${F.esc(num)}` : ""}`, { muted: true, size: 14, lh: 20, margin: "4px 0 0" }),
    `${full ? "Full refund" : "Partial refund"}: ${F.money(amount, cur)}${num ? ` (order ${num})` : ""}`, "honey", { center: true, pad: "24px 22px" });

  const reasonLine = why
    ? ["We've refunded you because ", why, ". ", full ? "We're sorry this one didn't work out." : "We're sorry about that, and thank you for letting us know."]
    : [full ? "We're sorry this one didn't work out." : "Thank you for your patience while we sorted this out."];

  return {
    subject: full ? `Your refund for ${num || "your order"} is on its way` : `A partial refund of ${F.money(amount, cur)} for ${num || "your order"}`,
    preheader: `${F.money(amount, cur)} is heading back to you. Banks usually show it within 5 to 10 business days.`,
    blocks: [
      Lay.hero({
        eyebrow: num ? `Order ${num}` : "Refund",
        title: full ? "Your refund is on its way" : "We've sent you a partial refund",
        lead: [first ? `Hi ${first}. ` : "", ...reasonLine],
      }),
      amountBox,
      note ? Lay.box(`${Lay.label("A note from us")}${Lay.bodyText(F.esc(note), { size: 15, lh: 23 })}`, `A note from us: ${note}`, "cream") : null,
      Lay.h2("When will I see it?"),
      Lay.p(["Refunds go back to the card or wallet you paid with. Most banks show it within ", { b: "5 to 10 business days" }, ", sometimes sooner. You don't need to do anything."]),
      !full && refundedTotal > amount ? Lay.p([`Refunded on this order so far: ${F.money(refundedTotal, cur)} of ${F.money(total, cur)}.`], { muted: true, small: true }) : null,
      Lay.buttons([
        order.uid !== null && id ? { href: L.order(id), label: "View your order", variant: "honey" } : { href: L.track(num), label: "View your order", variant: "honey" },
        { href: L.returns, label: "Refund policy", variant: "ghost" },
      ]),
      Lay.p(["Questions about this refund? Just reply and a real person will answer."], { muted: true, small: true }),
    ],
    reason: "You're getting this email because you placed an order at littlehivehouse.com.",
  };
};
