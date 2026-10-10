// Order pieces shared by several emails: item list with thumbnails, totals, shipping address, gift message.
"use strict";

const F = require("./format");
const { C, FD, FB, FS, T, raw, box, label, bodyText, rich } = require("./layout");

const { esc, str, money, num } = F;

/** Line total of one cart item in dollars. */
function lineTotal(it) {
  if (!it) return 0;
  if (typeof it.lineTotal === "number" && Number.isFinite(it.lineTotal)) return it.lineTotal;
  if (it.kind === "design") return num(it.unit) * Math.max(1, num(it.qty) || 1);
  if (it.kind === "photos") return (num(it.price) || num(it.unit)) * Math.max(1, num(it.qty) || 1);
  if (it.kind === "package") return num(it.price) * Math.max(1, num(it.qty) || 1);
  if (it.kind === "custom") return num(it.amount);
  return num(it.price) || num(it.amount);
}
/** Magnets in one item (designs: qty, photo packs: pack size, packages: size × qty). */
function magnets(it) {
  if (!it) return 0;
  if (it.kind === "design") return Math.max(1, num(it.qty) || 1);
  if (it.kind === "photos") return num(it.packSize) * Math.max(1, num(it.qty) || 1);
  if (it.kind === "package") return num(it.size) * Math.max(1, num(it.qty) || 1);
  return 0;
}
function items(order) {
  return Array.isArray(order && order.items) ? order.items.filter((i) => i && typeof i === "object") : [];
}
function magnetCount(order) {
  return items(order).reduce((n, it) => n + magnets(it), 0);
}
function photoCount(order) {
  return items(order).reduce((n, it) => n + (it.kind !== "photos" ? 0 : Array.isArray(it.photos) ? it.photos.length : num(it.photoCount)), 0);
}

/** Describes one item: {title, details[], thumb, badge, frames[], captions[], notes, total} */
function describe(it, opts = {}) {
  const qty = Math.max(1, num(it.qty) || 1);
  if (it.kind === "design") {
    const slug = str(it.id).split("/")[1] || str(it.id);
    const col = it.collection || str(it.id).split("/")[0];
    return {
      title: str(it.title) || F.pretty(slug) || "Magnet",
      details: [F.collectionName(col), qty > 1 ? (opts.prices === false ? `Qty ${qty}` : `${qty} × ${money(it.unit)}`) : ""].filter(Boolean),
      thumbId: str(it.id),
      alt: `${str(it.title) || F.pretty(slug)} magnet`,
    };
  }
  if (it.kind === "photos") {
    const photos = Array.isArray(it.photos) ? it.photos.filter(Boolean) : [];
    const frames = [...new Set(photos.map((ph) => str(ph.frame)).filter(Boolean))];
    const names = frames.map(F.frameName);
    const size = num(it.packSize);
    return {
      title: size ? `${size} photo magnets` : F.line(it.title, 80) || "Photo magnets",
      thumbUrl: /^https?:\/\/[^"'<>\s]+\.jpg$/.test(str(it.thumb)) ? str(it.thumb) : "",
      details: [
        qty > 1 ? `${qty} packs` : "",
        photos.length || num(it.photoCount) ? F.plural(photos.length || num(it.photoCount), "photo") : "",
        names.length === 1 ? `${names[0]} frame` : names.length > 1 ? `${names.length} frames` : "",
      ].filter(Boolean),
      frameId: frames[0] || (str(it.thumb) ? "" : "none"),
      frames,
      captions: photos.map((ph) => F.line(ph.caption, 40)).filter(Boolean),
      notes: F.line(it.notes, 220),
      alt: "Photo magnet frame preview",
    };
  }
  if (it.kind === "package") {
    return {
      title: str(it.title) || "Big order package",
      details: [`${num(it.size)} magnets${qty > 1 ? ` × ${qty}` : ""}`, "Custom design and proof included"],
      badge: String(num(it.size) * qty || ""),
      badgeSub: "magnets",
    };
  }
  return { title: str(it.title) || "Custom order", details: ["Made just for you"], badge: "★", badgeSub: "custom" };
}

function thumbCell(d, L, size) {
  const img = (src, alt) => `<img class="lh-thumb thumb" src="${esc(src)}" width="${size}" height="${size}" alt="${esc(alt)}" style="display:block;width:${size}px;height:${size}px;border:1px solid ${C.line};border-radius:12px;background:${C.cream}">`;
  if (d.thumbId && L.designThumb(d.thumbId)) return img(L.designThumb(d.thumbId), d.alt);
  if (d.thumbUrl) return img(d.thumbUrl, d.alt);
  if (d.frameId && L.frameThumb(d.frameId)) return img(L.frameThumb(d.frameId), d.alt);
  const big = d.badge && d.badge.length > 3 ? 16 : 22;
  return `<table ${T} width="${size}" class="thumb"><tr><td class="thumb" align="center" valign="middle" width="${size}" height="${size}" bgcolor="${C.honeySoft}" style="width:${size}px;height:${size}px;border-radius:12px;background:${C.honeySoft};text-align:center">` +
    `<p style="margin:0;font-family:${FD};font-weight:700;font-size:${big}px;line-height:${big + 2}px;color:${C.ink}">${esc(d.badge || "")}</p>` +
    `<p style="margin:2px 0 0;font-family:${FB};font-size:10px;line-height:12px;letter-spacing:1px;text-transform:uppercase;color:${C.ink}">${esc(d.badgeSub || "")}</p></td></tr></table>`;
}

/**
 * Item list block. opts: {compact (admin), prices (default true)}
 */
function itemList(order, L, opts = {}) {
  const list = items(order);
  if (!list.length) return { html: "", text: "" };
  const size = opts.compact ? 52 : 72;
  const currency = order.pricing && order.pricing.currency;
  const rows = list.map((it, i) => {
    const d = describe(it, opts);
    const top = i ? `border-top:1px solid ${C.line};` : "";
    let extra = "";
    if (d.frames && d.frames.length > 1) {
      const shown = d.frames.slice(0, 4);
      extra += `<table ${T} style="margin-top:8px"><tr>` + shown.map((f) =>
        `<td style="padding:0 5px 0 0"><img class="lh-thumb" src="${esc(L.frameThumb(f))}" width="30" height="30" alt="${esc(F.frameName(f))} frame" title="${esc(F.frameName(f))}" style="display:block;width:30px;height:30px;border:1px solid ${C.line};border-radius:7px"></td>`).join("") +
        (d.frames.length > 4 ? `<td class="lh-m" style="font-family:${FB};font-size:13px;color:${C.muted}">+${d.frames.length - 4}</td>` : "") + "</tr></table>";
    }
    if (d.captions && d.captions.length) {
      const caps = d.captions.slice(0, 4).map((c) => `“${c}”`).join(", ") + (d.captions.length > 4 ? ` +${d.captions.length - 4} more` : "");
      extra += bodyText(`Captions: ${esc(caps)}`, { muted: true, size: 13, lh: 19, margin: "6px 0 0" });
    }
    if (d.notes) extra += bodyText(`Note: ${esc(d.notes)}`, { muted: true, size: 13, lh: 19, margin: "4px 0 0" });
    const price = opts.prices === false ? "" : money(lineTotal(it), currency);
    return `<tr>
<td class="lh-line${opts.compact ? "" : " thumb-td"}" valign="top" width="${size}" style="${top}padding:${i ? 14 : 2}px 14px 14px 0;width:${size}px">${thumbCell(d, L, size)}</td>
<td class="lh-line" valign="top" style="${top}padding:${i ? 14 : 2}px 10px 14px 0">${bodyText(`<strong style="font-weight:600">${esc(d.title)}</strong>`, { size: opts.compact ? 15 : 16, lh: 22 })}${d.details.length ? bodyText(esc(d.details.join(" · ")), { muted: true, size: 14, lh: 20, margin: "3px 0 0" }) : ""}${extra}</td>
<td class="lh-line lh-t" valign="top" align="right" style="${top}padding:${i ? 14 : 2}px 0 14px;white-space:nowrap;font-family:${FB};font-size:16px;line-height:22px;color:${C.ink}">${esc(price)}</td>
</tr>`;
  }).join("");
  const text = list.map((it) => {
    const d = describe(it, opts);
    const bits = [d.details.join(", "), d.captions && d.captions.length ? `captions: ${d.captions.join(", ")}` : "", d.notes ? `note: ${d.notes}` : ""].filter(Boolean);
    return `- ${d.title}${bits.length ? ` (${bits.join("; ")})` : ""}${opts.prices === false ? "" : `  ${money(lineTotal(it), currency)}`}`;
  }).join("\n");
  return raw(`<table ${T} width="100%">${rows}</table>`, text, "0 0 10px");
}

/** Totals table from order.pricing (+ refunds when `withRefunds`). */
function totals(order, opts = {}) {
  const pr = (order && order.pricing) || {};
  const cur = pr.currency;
  const rows = [];
  const subtotal = num(pr.subtotal) || items(order).reduce((n, it) => n + lineTotal(it), 0);
  rows.push(["Subtotal", money(subtotal, cur)]);
  if (num(pr.bundleDiscount) > 0) rows.push(["Bundle savings (3 for $12)", "−" + money(pr.bundleDiscount, cur), "save"]);
  if (num(pr.volumeDiscount) > 0) rows.push([`Volume discount${num(pr.volumePct) ? ` (${num(pr.volumePct)}% off)` : ""}`, "−" + money(pr.volumeDiscount, cur), "save"]);
  if (pr.promo && num(pr.promo.amount) > 0) rows.push([`Promo code${pr.promo.code ? " " + F.line(pr.promo.code, 30) : ""}`, "−" + money(pr.promo.amount, cur), "save"]);
  if (pr.shipping !== undefined && pr.shipping !== null) rows.push(["Shipping", num(pr.shipping) > 0 ? money(pr.shipping, cur) : "Free", num(pr.shipping) > 0 ? "" : "save"]);
  const total = num(pr.total);
  const refunded = num(order && order.refundedTotal);
  const showRefund = opts.withRefunds && refunded > 0;
  const cell = (t, kind, right) => `<td class="${kind === "save" ? "lh-green" : kind === "total" ? "lh-t" : "lh-m"}" ${right ? 'align="right" ' : ""}style="padding:5px 0;${right ? "padding-left:12px;white-space:nowrap;" : ""}font-family:${kind === "total" ? FD : FB};font-size:${kind === "total" ? 20 : 15}px;line-height:${kind === "total" ? 26 : 21}px;font-weight:${kind === "total" ? 700 : 400};color:${kind === "save" ? C.green : kind === "total" ? C.ink : C.muted}">${esc(t)}</td>`;
  let html = rows.map(([k, v, kind]) => `<tr>${cell(k, "")}${cell(v, kind, true)}</tr>`).join("");
  html += `<tr><td colspan="2" style="padding:8px 0 0"><table ${T} width="100%"><tr><td class="lh-line" style="border-top:2px solid ${C.ink};font-size:0;line-height:0;height:1px">&nbsp;</td></tr></table></td></tr>`;
  html += `<tr>${cell("Total", "total")}${cell(money(total, cur), "total", true)}</tr>`;
  if (showRefund) {
    html += `<tr>${cell("Refunded", "")}${cell("−" + money(refunded, cur), "", true)}</tr>`;
    html += `<tr>${cell("Net paid", "")}${cell(money(Math.max(0, total - refunded), cur), "", true)}</tr>`;
  }
  const text = rows.map(([k, v]) => `${k}: ${v}`).concat([`TOTAL: ${money(total, cur)}`],
    showRefund ? [`Refunded: -${money(refunded, cur)}`, `Net paid: ${money(Math.max(0, total - refunded), cur)}`] : []).join("\n");
  return raw(`<table ${T} width="100%" style="max-width:340px" align="right">${html}</table>`, text, "6px 0 30px");
}

/** Address lines (escaped html with <br>, and text). */
function address(ship) {
  const s = ship || {};
  const a = s.address || {};
  const cityLine = [F.line(a.city, 60), [F.line(a.state, 30), F.line(a.postal_code, 20)].filter(Boolean).join(" ")].filter(Boolean).join(", ");
  const country = { US: "United States", CA: "Canada" }[str(a.country).toUpperCase()] || F.line(a.country, 40);
  const lines = [F.line(s.name, 80), F.line(a.line1, 100), F.line(a.line2, 100), cityLine, country].filter(Boolean);
  return { html: lines.map(esc).join("<br>"), text: lines.join("\n"), lines };
}

/** Address + optional extra column, side by side. */
function addressColumn(order) {
  const ad = address(order && order.shipping);
  if (!ad.lines.length) return null;
  return { label: "Shipping to", html: bodyText(ad.html, { size: 15, lh: 23 }), text: ad.text };
}

function giftMessage(msg) {
  const m = str(msg).trim().slice(0, 600);
  if (!m) return { html: "", text: "" };
  const html = esc(m).replace(/\r?\n/g, "<br>");
  return box(`${label("Gift message")}<p class="lh-t" style="margin:4px 0 0;font-family:${FS};font-style:italic;font-size:18px;line-height:28px;color:${C.ink}">“${html}”</p>` +
    bodyText("We'll tuck it in with your magnets.", { muted: true, size: 13, lh: 19, margin: "8px 0 0" }),
  `GIFT MESSAGE\n"${m}"`);
}

/** Featured designs for welcome emails: data.featured [{id, title}] or three crowd favorites. */
const FAVORITES = [
  { id: "places/new-york", title: "New York" },
  { id: "fall/apple-picking", title: "Apple Picking" },
  { id: "bee-kind/bee-happy", title: "Bee Happy" },
];
function featured(data, L) {
  const list = Array.isArray(data.featured) && data.featured.length ? data.featured : FAVORITES;
  return list.slice(0, 3).map((f) => {
    const id = str(f && f.id);
    const [col, slug] = id.split("/");
    return { src: L.designThumb(id), title: F.line(f.title, 40) || F.pretty(slug), sub: F.collectionName(col), alt: `${F.line(f.title, 40) || F.pretty(slug)} magnet`, href: /^[a-z0-9-]+$/.test(col || "") ? `${L.site}/collections/${col}.html` : L.shop };
  });
}

function orderId(data) {
  return str((data.order && (data.order.id || data.order.orderId)) || data.orderId);
}

module.exports = { lineTotal, magnets, magnetCount, photoCount, items, describe, itemList, totals, address, addressColumn, giftMessage, featured, orderId, rich };
