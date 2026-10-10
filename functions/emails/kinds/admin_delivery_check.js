// Daily deliveredFollowUp: orders shipped 10+ days ago and not marked delivered.
// Also sent by trackShipments (data.mode === "tracking") when automatic tracking needs a human: a carrier problem,
// 7+ days without a new scan, or 30 days without delivery. Then each order carries `issue` (what to look at).
"use strict";
const F = require("../format");
const Lay = require("../layout");

module.exports = function adminDeliveryCheck(data, { L }) {
  const orders = Array.isArray(data.orders) ? data.orders.filter((o) => o && typeof o === "object") : [];
  const n = orders.length;
  const now = data.now || new Date();
  const C = Lay.C;
  const auto = data.mode === "tracking";
  const rows = orders.map((o, i) => {
    const f = o.fulfillment || {};
    const carrier = o.carrier || f.carrier;
    const tracking = F.line(o.tracking || f.tracking, 60);
    const shippedAt = o.shippedAt || f.shippedAt;
    const days = typeof o.days === "number" && Number.isFinite(o.days) ? o.days : F.daysSince(shippedAt, now);
    const url = F.trackingUrl(carrier, tracking, o.url || f.url);
    const top = i ? `border-top:1px solid ${C.line};` : "";
    const id = F.str(o.id || o.orderId);
    const adminUrl = /^https?:\/\//.test(F.str(o.adminUrl)) ? F.str(o.adminUrl) : id ? L.admin(id) : L.adminHome;
    const issue = F.line(o.issue, 200);
    return {
      html: `<tr><td class="lh-line" valign="top" style="${top}padding:12px 10px 12px 0">` +
        Lay.bodyText(`<a class="lh-a" href="${F.esc(adminUrl)}" style="color:${C.link};font-weight:600">${F.esc(F.line(o.number, 30) || "Order")}</a> · ${F.esc(F.line(o.name, 60))}`, { size: 15, lh: 21 }) +
        (issue ? Lay.bodyText(`<strong style="font-weight:600;color:${C.red}">${F.esc(issue)}</strong>`, { size: 14, lh: 20, margin: "3px 0 0" }) : "") +
        Lay.bodyText(`${F.esc(F.carrierName(carrier, o.carrierName))}${tracking ? ` · ${url ? `<a class="lh-a" href="${F.esc(url)}" style="color:${C.link}">${F.esc(tracking)}</a>` : F.esc(tracking)}` : ""}${o.email ? ` · ${F.esc(F.line(o.email, 120))}` : ""}`, { muted: true, size: 13, lh: 19, margin: "2px 0 0" }) +
        `</td><td class="lh-line" valign="top" align="right" style="${top}padding:12px 0;white-space:nowrap">${Lay.bodyText(`<strong style="font-weight:600">${days} days</strong>`, { size: 14, lh: 21 })}${Lay.bodyText(F.esc(F.fmtDate(shippedAt)), { muted: true, size: 12, lh: 18 })}</td></tr>`,
      text: `- ${F.line(o.number, 30)} ${F.line(o.name, 60)} · ${F.carrierName(carrier, o.carrierName)} ${tracking} · shipped ${F.fmtDate(shippedAt)} (${days} days)${issue ? `\n  ${issue}` : ""}${url ? `\n  Track: ${url}` : ""}\n  Admin: ${adminUrl}`,
    };
  });
  if (auto) {
    return {
      subject: n ? `${F.plural(n, "shipment")} need${n === 1 ? "s" : ""} a look (automatic tracking)` : "Automatic tracking: all good",
      preheader: n ? "The carrier reported a problem, or a package has gone quiet. Customers were not emailed about this." : "Every tracked package is moving.",
      audience: "admin",
      blocks: [
        Lay.hero({ eyebrow: "Automatic tracking", title: n ? `${F.plural(n, "package")} to check on` : "All good", lead: [n ? "Automatic tracking spotted something it can't fix on its own. The customers were not emailed about this." : "Every tracked package is moving."] }),
        n ? Lay.raw(`<table ${Lay.T} width="100%">${rows.map((r) => r.html).join("")}</table>`, rows.map((r) => r.text).join("\n"), "0 0 22px") : null,
        n ? Lay.p(["Open the tracking link first. A delivery attempt or a held package usually means the customer has to pick it up: a short friendly email to them helps. If it looks lost, reship or refund from the order page."], { muted: true, small: true }) : null,
        Lay.buttons([{ href: L.adminHome, label: "Open the admin", variant: "ink" }]),
      ],
    };
  }
  return {
    subject: n ? `${F.plural(n, "shipment")} to check on (shipped 10+ days ago)` : "Delivery check: nothing to chase today",
    preheader: n ? "Check the tracking, then mark them delivered or reach out to the customer." : "Every shipment is delivered or still on time.",
    audience: "admin",
    blocks: [
      Lay.hero({ eyebrow: "Daily delivery check", title: n ? `${F.plural(n, "package")} to check on` : "All caught up", lead: [n ? "These orders shipped at least 10 days ago and aren't marked delivered yet. Customers were not emailed." : "Nothing shipped 10+ days ago is waiting to be marked delivered."] }),
      n ? Lay.raw(`<table ${Lay.T} width="100%">${rows.map((r) => r.html).join("")}</table>`, rows.map((r) => r.text).join("\n"), "0 0 22px") : null,
      n ? Lay.p(["For each one: open the tracking link. If it says delivered, mark it delivered in the admin (that sends the review email). If it's stuck, a friendly note to the customer goes a long way."], { muted: true, small: true }) : null,
      Lay.buttons([{ href: L.adminHome, label: "Open the admin", variant: "ink" }]),
    ],
  };
};
