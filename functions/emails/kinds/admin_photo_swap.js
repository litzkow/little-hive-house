// To the shop when a customer swaps a photo of their order (functions/photoswap.js). data: {order, swap: {n, rebuilt, swaps}}
"use strict";
const F = require("../format");
const Lay = require("../layout");

module.exports = function adminPhotoSwap(data, { L }) {
  const o = data.order || {};
  const sw = data.swap || {};
  const num = F.line(o.number, 30);
  const name = F.line(o.name, 80) || "The customer";
  const n = Number(sw.n) || 0;
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
      Lay.buttons([{ href: (o.links && o.links.admin) || `${L.site}/admin/`, label: "See the order", variant: "ink" }]),
    ],
  };
};
