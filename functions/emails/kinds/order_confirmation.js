// Sent when Stripe confirms payment (stripeWebhook checkout.session.completed).
"use strict";
const F = require("../format");
const Lay = require("../layout");
const O = require("../order-parts");

module.exports = function orderConfirmation(data, { L }) {
  const order = data.order || {};
  const id = O.orderId(data);
  const num = F.line(order.number, 30);
  const first = F.firstName(order.name || (order.shipping && order.shipping.name));
  const count = O.magnetCount(order);
  const hasPackage = O.items(order).some((i) => i.kind === "package");
  const hasPhotos = O.items(order).some((i) => i.kind === "photos");
  const placed = F.fmtDate(order.paidAt || order.createdAt);
  // Guests (uid === null) have no account page; the backend may omit uid, then both buttons show.
  const viewUrl = order.uid === null || !id ? "" : L.order(id);

  const next = [
    hasPackage
      ? { title: "We send you a proof", body: "Within 1 business day we'll email you to collect your names, date, logo or photos, then send a proof to approve before anything is printed." }
      : { title: "We make them by hand", body: hasPhotos ? "We print your photos, frame them and press every magnet by hand. That takes 3 to 5 business days." : "We print and press every magnet by hand. That takes 3 to 5 business days." },
    { title: "We ship them to you", body: "You'll get an email with your tracking number the moment they leave the hive." },
    { title: "Fridge time", body: "Unwrap, stick, smile. Tag us on Instagram if you share a photo, we love seeing them." },
  ];

  const cols = [O.addressColumn(order)];
  const contact = [F.line(order.email, 120), F.line(order.shipping && order.shipping.phone, 30)].filter(Boolean);
  if (contact.length) cols.push({ label: "Contact", html: Lay.bodyText(contact.map(F.esc).join("<br>"), { size: 15, lh: 23 }), text: contact.join("\n") });

  return {
    subject: num ? `Thank you! Order ${num} is confirmed` : "Thank you! Your order is confirmed",
    preheader: `${F.plural(count, "magnet")} coming your way. We'll start making them by hand right away.`,
    blocks: [
      Lay.hero({
        eyebrow: num ? `Order ${num}` : "Order confirmed",
        title: first ? `Thank you, ${first}!` : "Thank you for your order!",
        lead: ["Your order is in and our hands are already itching to start. ", count ? `Here's everything that's coming your way${placed ? `, ordered ${placed}` : ""}.` : ""],
      }),
      Lay.progress(0),
      Lay.h2("Your order"),
      O.itemList(order, L),
      O.totals(order),
      O.giftMessage(order.giftMessage),
      Lay.columns(cols),
      order.notes ? Lay.p([{ b: "Your note to us: " }, F.line(order.notes, 400)], { muted: true, small: true }) : null,
      Lay.h2("What happens next"),
      Lay.steps(next),
      Lay.buttons([
        viewUrl ? { href: viewUrl, label: "View your order", variant: "honey" } : null,
        { href: L.track(num), label: viewUrl ? "Track it" : "Track your order", variant: viewUrl ? "ghost" : "honey" },
      ]),
      Lay.p(["Need to change something? Reply to this email as soon as you can and we'll do our best to catch it before your magnets go to print."], { muted: true, small: true }),
    ],
    reason: "You're getting this email because you placed an order at littlehivehouse.com.",
  };
};
