// Sent once by trackShipments when the carrier says the package is out for delivery today.
"use strict";
const F = require("../format");
const Lay = require("../layout");
const O = require("../order-parts");

module.exports = function outForDelivery(data, { L }) {
  const order = data.order || {};
  const f = Object.assign({}, order.fulfillment || {}, data.fulfillment || {});
  const num = F.line(order.number, 30);
  const first = F.firstName(order.name || (order.shipping && order.shipping.name));
  const carrier = F.carrierName(f.carrier, f.carrierName);
  const tracking = F.line(f.tracking, 60);
  const url = F.trackingUrl(f.carrier, tracking, f.url) || L.track(num);
  const events = Array.isArray(f.events) ? f.events.filter((e) => e && typeof e === "object") : [];
  const last = events[0] || null;
  const lastText = last ? F.line(last.text, 120) : "";
  const lastWhere = last ? F.line(last.location, 60) : "";
  const lastWhen = last ? F.fmtDate(last.at, true) : "";
  const ad = O.address(order.shipping);

  const scan = lastText
    ? `<table ${Lay.T} width="100%" style="margin-top:14px"><tr><td class="lh-line" style="border-top:1px solid ${Lay.C.line};padding-top:12px">` +
      Lay.label("Latest scan") +
      Lay.bodyText(`<strong style="font-weight:600">${F.esc(lastText)}</strong>`, { size: 15, lh: 22 }) +
      (lastWhere || lastWhen ? Lay.bodyText(F.esc([lastWhere, lastWhen].filter(Boolean).join(" · ")), { muted: true, size: 14, lh: 20, margin: "2px 0 0" }) : "") +
      `</td></tr></table>`
    : "";
  const trackBox = Lay.box(
    `<table ${Lay.T} width="100%"><tr>` +
      `<td class="stack" valign="top" style="padding:0 12px 0 0">${Lay.label("Carrier")}${Lay.bodyText(F.esc(carrier), { size: 17, lh: 24, weight: 600 })}</td>` +
      `<td class="stack stack-top" valign="top" style="padding:0">${Lay.label("Tracking number")}${Lay.bodyText(`<span style="font-family:Menlo,Consolas,'Courier New',monospace;letter-spacing:.5px">${F.esc(tracking || "See the tracking page")}</span>`, { size: 17, lh: 24, weight: 600 })}</td>` +
    `</tr></table>` + scan,
    [`Carrier: ${carrier}`, `Tracking number: ${tracking || "see the tracking page"}`,
      lastText ? `Latest scan: ${lastText}${lastWhere || lastWhen ? ` (${[lastWhere, lastWhen].filter(Boolean).join(", ")})` : ""}` : ""].filter(Boolean).join("\n"),
    "honey", { pad: "20px 22px" });

  return {
    subject: first ? `${first}, your magnets arrive today!` : "Your magnets arrive today!",
    preheader: `${carrier} has your package out for delivery${num ? ` (order ${num})` : ""}. Keep an eye on the porch!`,
    blocks: [
      Lay.hero({
        eyebrow: num ? `Order ${num} · Out for delivery` : "Out for delivery",
        title: "Your magnets arrive today!",
        lead: [first ? `Good news, ${first}! ` : "Good news! ", `${carrier} has your package out for delivery. Keep an eye on the porch and the mailbox.`],
      }),
      Lay.progress(2),
      trackBox,
      Lay.buttons([{ href: url, label: "Follow your package", variant: "honey" }], { full: true, pad: "0 0 28px" }),
      ad.lines.length ? Lay.columns([{ label: "Coming to", html: Lay.bodyText(ad.html, { size: 15, lh: 23 }), text: ad.text }]) : null,
      Lay.p(["We'll send one last note when it's delivered. If it doesn't turn up by tomorrow, just reply and we'll chase it with the carrier for you."], { muted: true, small: true }),
    ],
    reason: "You're getting this email because you placed an order at littlehivehouse.com.",
  };
};
