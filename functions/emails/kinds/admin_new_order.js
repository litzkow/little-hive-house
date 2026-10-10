// Sent to MAIL_ADMIN when an order is paid: compact operational summary.
"use strict";
const F = require("../format");
const Lay = require("../layout");
const O = require("../order-parts");

module.exports = function adminNewOrder(data, { L }) {
  const order = data.order || {};
  const id = O.orderId(data);
  const num = F.line(order.number, 30) || "New order";
  const cur = order.pricing && order.pricing.currency;
  const total = F.money(order.pricing && order.pricing.total, cur);
  const count = O.magnetCount(order);
  const photos = O.photoCount(order);
  const ad = O.address(order.shipping);
  const promo = order.pricing && order.pricing.promo;
  const fee = order.stripe && F.num(order.stripe.fee) ? F.money(order.stripe.fee, cur) : "";
  const kinds = O.items(order).map((i) => i.kind);
  const todo = [
    kinds.includes("package") ? "Package in this order: email the customer for their artwork and details, then send a proof." : "",
    photos ? `Download the ${F.plural(photos, "customer photo")} from the order page.` : "",
    order.giftMessage ? "Gift order: include the gift message card." : "",
  ].filter(Boolean);

  return {
    subject: `New order ${num} · ${total} · ${F.plural(count, "magnet")}`,
    preheader: `${F.line(order.name, 60) || F.line(order.email, 80)} · ${F.plural(O.items(order).length, "item")}${photos ? ` · ${F.plural(photos, "photo")}` : ""}${ad.lines.length ? ` · ships to ${F.line(order.shipping && order.shipping.address && order.shipping.address.state, 20) || "?"}` : ""}`,
    audience: "admin",
    blocks: [
      Lay.hero({ eyebrow: "New order", title: `${num} · ${total}`, lead: [`${F.plural(count, "magnet")}${photos ? `, ${F.plural(photos, "customer photo")}` : ""}. Paid ${F.fmtDate(order.paidAt || order.createdAt, true) || "just now"}.`] }),
      Lay.buttons([{ href: id ? L.admin(id) : L.adminHome, label: "Open in admin", variant: "ink" }], { pad: "0 0 22px" }),
      todo.length ? Lay.box(todo.map((t) => Lay.bodyText(`• ${F.esc(t)}`, { size: 14, lh: 21 })).join(""), todo.map((t) => `* ${t}`).join("\n"), "honey", { pad: "14px 18px" }) : null,
      Lay.facts([
        ["Customer", [F.line(order.name, 80) || "(no name)", order.uid ? " · account" : " · guest"]],
        ["Email", F.isEmail(order.email) ? [{ a: order.email, href: `mailto:${order.email}` }] : F.line(order.email, 120)],
        ["Phone", F.line(order.shipping && order.shipping.phone, 30)],
        ["Ship to", ad.lines.join(", ")],
        ["Gift message", F.line(order.giftMessage, 300)],
        ["Customer note", F.line(order.notes, 400)],
        ["Promo", promo && promo.code ? `${F.line(promo.code, 30)} (−${F.money(promo.amount, cur)})` : ""],
        ["Stripe fee", fee],
      ]),
      Lay.h2("Items"),
      O.itemList(order, L, { compact: true }),
      O.totals(order),
    ],
  };
};
