// Sent by adminShip: carrier + tracking number and a big track button.
"use strict";
const F = require("../format");
const Lay = require("../layout");
const O = require("../order-parts");

module.exports = function shipped(data, { L }) {
  const order = data.order || {};
  const f = Object.assign({}, order.fulfillment || {}, data.fulfillment || {});
  const num = F.line(order.number, 30);
  const first = F.firstName(order.name || (order.shipping && order.shipping.name));
  const carrier = F.carrierName(f.carrier, f.carrierName);
  const tracking = F.line(f.tracking, 60);
  const url = F.trackingUrl(f.carrier, tracking, f.url) || L.track(num);
  const ad = O.address(order.shipping);
  const country = String((order.shipping && order.shipping.address && order.shipping.address.country) || "US").toUpperCase();
  const eta = F.arrival(f.shippedAt || new Date(), { shipped: true, country });

  const trackBox = Lay.box(
    `<table ${Lay.T} width="100%"><tr>` +
      `<td class="stack" valign="top" style="padding:0 12px 0 0">${Lay.label("Carrier")}${Lay.bodyText(F.esc(carrier), { size: 17, lh: 24, weight: 600 })}</td>` +
      `<td class="stack stack-top" valign="top" style="padding:0">${Lay.label("Tracking number")}${Lay.bodyText(`<span style="font-family:Menlo,Consolas,'Courier New',monospace;letter-spacing:.5px">${F.esc(tracking || "Coming soon")}</span>`, { size: 17, lh: 24, weight: 600 })}</td>` +
    `</tr></table>`,
    `Carrier: ${carrier}\nTracking number: ${tracking || "coming soon"}`, "honey", { pad: "20px 22px" });

  return {
    subject: `Your magnets are on the way!${num ? ` (${num})` : ""}`,
    preheader: `${carrier}${tracking ? ` tracking ${tracking}` : ""}. Follow your package all the way to your door.`,
    blocks: [
      Lay.hero({
        eyebrow: num ? `Order ${num}` : "Shipped",
        title: "They're on their way!",
        lead: [first ? `Good news, ${first}! ` : "Good news! ", "Your magnets are packed snug and headed your way. ",
          eta ? (country === "CA" ? ["Canadian packages usually take 1 to 3 weeks, so expect it about ", { b: eta }, "."] : ["USPS usually delivers in 2 to 5 business days, so expect it about ", { b: eta }, "."]) : "The tracking page shows the expected delivery date."].flat(),
      }),
      Lay.progress(2),
      trackBox,
      Lay.buttons([{ href: url, label: "Track your package", variant: "honey" }], { full: true, pad: "0 0 28px" }),
      Lay.h2("In the box"),
      O.itemList(order, L, { prices: false }),
      ad.lines.length ? Lay.columns([{ label: "Shipping to", html: Lay.bodyText(ad.html, { size: 15, lh: 23 }), text: ad.text }]) : null,
      f.autoUpdates ? Lay.p(["We'll email you again when it's out for delivery, and when it arrives. No need to keep checking!"], { small: true }) : null,
      Lay.p(["Tracking can take a day to wake up after we drop the package off. If anything looks stuck, just reply and we'll chase it for you."], { muted: true, small: true }),
    ],
    reason: "You're getting this email because you placed an order at littlehivehouse.com.",
  };
};
