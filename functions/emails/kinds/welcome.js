// Sent once by the `welcome` callable after sign-up.
"use strict";
const F = require("../format");
const Lay = require("../layout");
const O = require("../order-parts");

module.exports = function welcome(data, { L }) {
  const first = F.firstName(data.name);
  const promo = data.promo && F.line(data.promo.code, 30) ? data.promo : null;
  const off = promo && F.offText(promo);
  return {
    subject: first ? `Welcome to the hive, ${first}!` : "Welcome to the hive!",
    preheader: promo ? `Your account is ready, and ${off} your first order is waiting.` : "Your account is ready. Save favorites, track orders and reorder in a tap.",
    blocks: [
      Lay.hero({
        eyebrow: "Welcome",
        title: first ? `Welcome to the hive, ${first}!` : "Welcome to the hive!",
        lead: ["We're Karina and Thiago, and we make every magnet by hand, one little batch at a time. We're so glad you're here."],
      }),
      promo ? Lay.p([{ b: "A welcome gift: " }, `${off} your first order${promo.expiresAt ? `, until ${F.fmtDate(promo.expiresAt)}` : ""}.`], { pad: "0 0 12px" }) : null,
      promo ? Lay.code(F.line(promo.code, 30), ["Enter it at checkout."]) : null,
      Lay.h2("With your account you can"),
      Lay.steps([
        { title: "Save favorites", body: "Tap the heart on any design to keep it for later." },
        { title: "Track every order", body: "See where your magnets are, from our workshop to your door." },
        { title: "Reorder in a tap", body: "Loved a set? Buy it again for the next birthday or host gift." },
      ]),
      Lay.h2("Crowd favorites"),
      Lay.gallery(O.featured(data, L)),
      Lay.buttons([
        { href: L.shop, label: "Start shopping", variant: "honey" },
        { href: L.photos, label: "Turn photos into magnets", variant: "ghost" },
      ]),
      Lay.p(["Mix any 3 designs for $12, and the more magnets in your cart, the more you save (up to 25% off)."], { muted: true, small: true }),
    ],
    reason: "You're getting this email because you created an account at littlehivehouse.com.",
    unsubscribeUrl: data.unsubscribeUrl,
  };
};
