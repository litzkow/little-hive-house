// Sent by adminMarkDelivered: hope you love them + star links to the review form.
"use strict";
const F = require("../format");
const Lay = require("../layout");
const O = require("../order-parts");

module.exports = function deliveredReview(data, { L }) {
  const order = data.order || {};
  const id = O.orderId(data);
  const num = F.line(order.number, 30);
  const first = F.firstName(order.name || (order.shipping && order.shipping.name));
  const handle = F.line(data.instagram || "@littlehivehouse", 40);
  const igUrl = F.safeUrl(data.instagramUrl);
  const code = data.thankYouCode || data.promo || null;
  const codeText = code && F.line(code.code, 30);
  const off = code && F.offText(code);
  const reviewUrl = id ? `${L.order(id)}#review` : L.track(num);

  return {
    subject: first ? `${first}, how do they look on your fridge?` : "How do they look on your fridge?",
    preheader: "Your magnets have landed. Tap a star to tell us what you think, it takes 30 seconds.",
    blocks: [
      Lay.hero({
        eyebrow: num ? `Order ${num} · Delivered` : "Delivered",
        title: "They've arrived! We hope you love them.",
        lead: ["Every magnet was printed, pressed and packed by hand in our little workshop. We'd love to know how they turned out."],
      }),
      Lay.progress(3),
      Lay.p([{ b: "How did we do?" }, " Tap a star to leave a quick review:"], { center: true, pad: "0 0 10px" }),
      id ? Lay.stars((n) => L.review(id, n)) : Lay.buttons([{ href: reviewUrl, label: "Leave a review" }], { center: true }),
      Lay.p(["Your words help other people find handmade gifts, and they make our whole week."], { muted: true, small: true, center: true, pad: "0 0 26px" }),
      Lay.h2("In your order"),
      O.itemList(order, L, { prices: false, compact: true }),
      Lay.box(
        Lay.bodyText(`<strong style="font-weight:600">Show us your fridge!</strong> Share a photo on Instagram and tag ${igUrl ? `<a class="lh-a" href="${F.esc(igUrl)}" style="color:${Lay.C.link}">${F.esc(handle)}</a>` : `<strong style="font-weight:600">${F.esc(handle)}</strong>`}. We feature our favorites.`, { size: 15, lh: 23 }),
        `Show us your fridge! Share a photo on Instagram and tag ${handle}${igUrl ? ` (${igUrl})` : ""}.`, "cream"),
      codeText ? Lay.p([{ b: "A little thank-you" }, ` for your next order: ${off}${code.expiresAt ? ` until ${F.fmtDate(code.expiresAt)}` : ""}.`], { pad: "6px 0 12px" }) : null,
      codeText ? Lay.code(codeText, ["Enter it at checkout. Share it with a friend if you like!"]) : null,
      Lay.buttons([{ href: L.shop, label: "Shop new designs", variant: "ghost" }], { center: true }),
      Lay.p(["Something not right? Reply to this email and we'll make it right, promise."], { muted: true, small: true, center: true }),
    ],
    reason: "You're getting this email because you placed an order at littlehivehouse.com.",
    unsubscribeUrl: data.unsubscribeUrl,
  };
};
