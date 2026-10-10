// Sent by `subscribe` to a new newsletter subscriber.
"use strict";
const F = require("../format");
const Lay = require("../layout");
const O = require("../order-parts");

module.exports = function newsletterWelcome(data, { L }) {
  const promo = data.promo && F.line(data.promo.code, 30) ? data.promo : null;
  const off = promo && F.offText(promo);
  return {
    subject: "You're on the list! Welcome to the hive",
    preheader: promo ? `Thanks for joining! Here's ${off} your first order.` : "New designs, seasonal drops and the occasional sweet deal. Never spam.",
    blocks: [
      Lay.hero({ eyebrow: "You're in", title: "Welcome to the hive!", lead: ["Thanks for joining our little list. Expect new designs, seasonal drops and the occasional sweet deal, a couple of times a month at most."] }),
      promo ? Lay.p([{ b: "A thank-you for joining: " }, `${off} your first order${promo.expiresAt ? `, until ${F.fmtDate(promo.expiresAt)}` : ""}.`], { pad: "0 0 12px" }) : null,
      promo ? Lay.code(F.line(promo.code, 30), ["Enter it at checkout."]) : null,
      Lay.h2("Fan favorites to start with"),
      Lay.gallery(O.featured(data, L)),
      Lay.p(["Mix any 3 designs for $12, turn your own photos into magnets, and save up to 25% on bigger carts."], { muted: true, small: true }),
      Lay.buttons([
        { href: L.shop, label: "Shop the designs", variant: "honey" },
        { href: L.photos, label: "Photo magnets", variant: "ghost" },
      ]),
    ],
    reason: "You're getting this email because you signed up at littlehivehouse.com.",
    marketing: true,
    unsubscribeUrl: data.unsubscribeUrl,
  };
};
