// To the shop when a customer swaps or removes a photo of their order (functions/photoswap.js).
// data: {order, swap: {n, rebuilt, swaps, removed?, saved?, held?, refundFailed?, newSize?}}
"use strict";
const F = require("../format");
const Lay = require("../layout");

module.exports = function adminPhotoSwap(data, { L }) {
  const o = data.order || {};
  const sw = data.swap || {};
  const num = F.line(o.number, 30);
  const name = F.line(o.name, 80) || "The customer";
  const n = Number(sw.n) || 0;
  const sheet = sw.rebuilt ? "Made again. If you printed the old one, print it again." : "Could not be made again. Open the order and tap Rebuild before printing.";
  const button = Lay.buttons([{ href: (o.links && o.links.admin) || `${L.site}/admin/`, label: "See the order", variant: "ink" }]);
  if (sw.removed) {
    const money = F.money(sw.saved);
    return {
      subject: `Photo removed ${num}: ${name} took out photo ${n}`,
      preheader: `${Number(sw.newSize) || 0} magnets now, ${money} less.`,
      audience: "admin",
      blocks: [
        Lay.hero({ eyebrow: "Photo removed", title: `${name} took out photo ${n}`, lead: null }),
        Lay.facts([
          ["Order", num],
          ["Magnets now", String(Number(sw.newSize) || 0)],
          ["Money", sw.held ? `${money} less. The card is charged the new total when you ship.` : sw.refundFailed ? `The refund of ${money} failed. Refund it with the Refund button.` : `${money} refunded to the card.`],
          ["Print sheet", sheet],
        ]),
        button,
      ],
    };
  }
  return {
    subject: `Photo changed ${num}: ${name} swapped photo ${n}`,
    preheader: sw.rebuilt ? "The print sheet was made again with the new photo." : "Make the print sheet again before printing.",
    audience: "admin",
    blocks: [
      Lay.hero({ eyebrow: "Photo changed", title: `${name} swapped photo ${n}`, lead: null }),
      Lay.facts([
        ["Order", num],
        ["Photo", `${n}, same frame and caption, same price`],
        ["Print sheet", sw.rebuilt ? "Made again with the new photo. If you printed the old one, print it again." : "Could not be made again. Open the order and tap Rebuild before printing."],
        ["Changes so far", String(Number(sw.swaps) || 1)],
      ]),
      button,
    ],
  };
};
