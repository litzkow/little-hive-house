// Small pure helpers shared by every email: escaping, money, dates, names, links and catalog labels.
"use strict";

const DEFAULT_SITE = "https://littlehivehouse.com";
const SUPPORT = "support@littlehivehouse.com";
const STORE_TZ = "America/New_York";

// Copied from tools/catalog.py COLLECTIONS and assets/frames/frames.json (labels only; unknown ids are prettified).
const COLLECTION_NAMES = {
  places: "USA Places", world: "World Places", "ink-cities": "Ink Cities", "city-sketches": "City Sketches",
  fall: "Fall", halloween: "Halloween", christmas: "Christmas", holidays: "Holidays & Dates", summer: "Summer",
  "kitchen-words": "Kitchen Words", "bumper-stickers": "Bumper Stickers", "night-sky": "Night Sky",
  "birth-flowers": "Birth Flowers", "bee-kind": "Bee Kind", "furry-friends": "Furry Friends", brasil: "Brasil",
  "home-notes": "Home Notes",
};
const FRAME_NAMES = {
  none: "No border", white: "Crisp white mat", instant: "Instant photo", gallery: "Black gallery mat",
  rounded: "Rounded modern", film: "Film strip", stamp: "Postage stamp", postcard: "Travel postcard",
  honeycomb: "Honeycomb", "gold-cream": "Gold line on cream", lace: "Scalloped lace", floral: "Watercolour peonies",
  eucalyptus: "Eucalyptus wreath", wedding: "Linen & gold leaf", ornate: "Vintage ornate gold", fall: "Painted fall leaves",
  holly: "Christmas holly", snowflakes: "Snowflakes", hearts: "Hearts & confetti", tropical: "Tropical leaves",
  birthday: "Birthday balloons", baby: "Sweet dreams baby", sports: "Team spirit", graduation: "Graduation",
};
const CARRIERS = {
  usps: { name: "USPS", url: (t) => `https://tools.usps.com/go/TrackConfirmAction?tLabels=${encodeURIComponent(t)}` },
  ups: { name: "UPS", url: (t) => `https://www.ups.com/track?tracknum=${encodeURIComponent(t)}` },
  fedex: { name: "FedEx", url: (t) => `https://www.fedex.com/fedextrack/?trknbr=${encodeURIComponent(t)}` },
  dhl: { name: "DHL", url: (t) => `https://www.dhl.com/us-en/home/tracking/tracking-express.html?submit=1&tracking-id=${encodeURIComponent(t)}` },
};
// Refund reasons from the adminRefund contract, in words a customer would use.
const REFUND_REASONS = {
  not_delivered: "your package didn't arrive",
  damaged: "your magnets arrived damaged",
  wrong_item: "we sent the wrong item",
  print_quality: "the print quality wasn't up to our standard",
  late: "your order arrived later than we promised",
  changed_mind: "you changed your mind",
  duplicate: "the order was placed twice",
  other: "",
};

const ESC = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" };
/** HTML-escape any value (null/undefined -> ""). */
function esc(v) {
  return str(v).replace(/[&<>"']/g, (c) => ESC[c]);
}
/** A value as a clean string: null/undefined/objects become "". */
function str(v) {
  if (v === null || v === undefined) return "";
  if (typeof v === "string") return v;
  if (typeof v === "number") return Number.isFinite(v) ? String(v) : "";
  if (typeof v === "boolean") return String(v);
  return "";
}
/** One line of text (for subjects and headers): no line breaks, trimmed, length-limited. */
function line(v, max = 140) {
  const s = str(v).replace(/[\r\n\t]+/g, " ").replace(/\s{2,}/g, " ").trim();
  return s.length > max ? s.slice(0, max - 1).trimEnd() + "…" : s;
}
/** Only http(s) and mailto links survive; anything else becomes the fallback. */
function safeUrl(u, fallback = "") {
  const s = str(u).trim();
  return /^(https?:\/\/|mailto:)/i.test(s) ? s : fallback;
}
function isEmail(v) {
  return /^[^\s@<>"'(),;:]+@[^\s@<>"'(),;:]+\.[^\s@<>"'(),;:]+$/.test(str(v)) && str(v).length <= 254;
}
function num(v) {
  const n = typeof v === "string" && v.trim() !== "" ? Number(v) : v;
  return typeof n === "number" && Number.isFinite(n) ? n : 0;
}
/** Dollars (number) -> "$12.50". Amounts in the order model are dollars, not cents. */
function money(v, currency = "usd") {
  const n = num(v);
  const cur = /^[a-z]{3}$/i.test(str(currency)) ? str(currency).toUpperCase() : "USD";
  try {
    return new Intl.NumberFormat("en-US", { style: "currency", currency: cur }).format(n);
  } catch (e) {
    return "$" + n.toFixed(2);
  }
}
function toDate(v) {
  if (!v) return null;
  if (v instanceof Date) return isNaN(v) ? null : v;
  if (typeof v.toDate === "function") return toDate(v.toDate());
  if (typeof v === "object" && typeof v.seconds === "number") return new Date(v.seconds * 1000);
  if (typeof v === "object" && typeof v._seconds === "number") return new Date(v._seconds * 1000);
  if (typeof v === "number" || typeof v === "string") {
    const d = new Date(v);
    return isNaN(d) ? null : d;
  }
  return null;
}
/** "Oct 10, 2026" ("" when missing). */
function fmtDate(v, withTime = false) {
  const d = toDate(v);
  if (!d) return "";
  // A bare date (midnight UTC, e.g. "2026-12-31") stays that calendar day; real times show in store time.
  const bare = !withTime && d.getUTCHours() === 0 && d.getUTCMinutes() === 0 && d.getUTCSeconds() === 0;
  const o = { month: "short", day: "numeric", year: "numeric", timeZone: bare ? "UTC" : STORE_TZ };
  if (withTime) Object.assign(o, { hour: "numeric", minute: "2-digit" });
  return new Intl.DateTimeFormat("en-US", o).format(d);
}
/** Whole days between a date and now (or `now`). */
function daysSince(v, now = new Date()) {
  const d = toDate(v);
  return d ? Math.max(0, Math.floor((toDate(now) - d) / 86400000)) : 0;
}
function firstName(name) {
  const n = line(name, 60).split(" ")[0];
  return n || "";
}
function pretty(slug) {
  return str(slug).replace(/[-_]+/g, " ").replace(/\b\w/g, (c) => c.toUpperCase()).trim();
}
function collectionName(slug) {
  return COLLECTION_NAMES[slug] || pretty(slug);
}
function frameName(id) {
  return FRAME_NAMES[id] || pretty(id);
}
function plural(n, one, many) {
  return `${n} ${n === 1 ? one : many || one + "s"}`;
}
function carrierName(carrier, fallback) {
  const c = CARRIERS[str(carrier).toLowerCase()];
  return c ? c.name : line(fallback, 40) || "the carrier";
}
/** Public tracking page for a carrier + number (custom url wins). */
function trackingUrl(carrier, tracking, custom) {
  const u = safeUrl(custom);
  if (u) return u;
  const c = CARRIERS[str(carrier).toLowerCase()];
  return c && str(tracking) ? c.url(str(tracking).trim()) : "";
}
function refundReason(code) {
  return Object.prototype.hasOwnProperty.call(REFUND_REASONS, code) ? REFUND_REASONS[code] : "";
}

/** Site links. `site` has no trailing slash. */
function links(site) {
  const s = site;
  return {
    site: s,
    host: s.replace(/^https?:\/\//, ""),
    shop: `${s}/shop.html`,
    photos: `${s}/photo-magnets.html`,
    big: `${s}/big-orders.html`,
    account: `${s}/account.html`,
    orders: `${s}/orders.html`,
    contact: `${s}/contact.html`,
    returns: `${s}/returns.html`,
    shipping: `${s}/shipping.html`,
    order: (id) => `${s}/order.html?id=${encodeURIComponent(str(id))}`,
    review: (id, stars) => `${s}/order.html?id=${encodeURIComponent(str(id))}&rating=${stars}#review`,
    track: (number) => `${s}/track.html${str(number) ? "?number=" + encodeURIComponent(str(number)) : ""}`,
    admin: (id) => `${s}/admin/#order/${encodeURIComponent(str(id))}`,
    adminHome: `${s}/admin/`,
    logo: `${s}/assets/email/logo.png`,
    hexes: `${s}/assets/email/hexes.png`,
    designThumb: (id) => (/^[a-z0-9-]+\/[a-z0-9-]+$/.test(str(id)) ? `${s}/assets/email/thumbs/${id}.jpg` : ""),
    frameThumb: (id) => (/^[a-z0-9-]+$/.test(str(id)) ? `${s}/assets/email/thumbs/frames/${id}.jpg` : ""),
    /** Prefer the ready-made links the backend puts on order.links ({order, track, review, admin}). */
    fromOrder(order) {
      const given = order && typeof order === "object" && order.links && typeof order.links === "object" ? order.links : {};
      const ok = (k) => safeUrl(given[k]) && /^https?:/.test(given[k]) ? given[k] : "";
      if (ok("order")) { const u = ok("order"); this.order = () => u; this.review = (id, stars) => `${u}&rating=${stars}#review`; }
      if (ok("track")) { const u = ok("track"); this.track = () => u; }
      if (ok("admin")) { const u = ok("admin"); this.admin = () => u; }
      return this;
    },
  };
}
/** "10% off" from {percentOff} | {amountOff} | {text}. */
function offText(p) {
  if (!p || typeof p !== "object") return "";
  if (num(p.percentOff)) return `${num(p.percentOff)}% off`;
  if (num(p.amountOff)) return `${money(p.amountOff)} off`;
  return line(p.text, 40) || "a little something off";
}
function siteUrl(data) {
  const raw = str((data && data.siteUrl) || process.env.SITE_URL).trim();
  const u = /^https?:\/\/[^\s"'<>]+$/i.test(raw) ? raw : DEFAULT_SITE;
  return u.replace(/\/+$/, "");
}

module.exports = {
  DEFAULT_SITE, SUPPORT, COLLECTION_NAMES, FRAME_NAMES, CARRIERS, REFUND_REASONS,
  esc, str, line, safeUrl, isEmail, num, money, toDate, fmtDate, daysSince, firstName, pretty, collectionName, frameName,
  plural, carrierName, trackingUrl, refundReason, links, siteUrl, offText,
};
