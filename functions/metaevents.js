"use strict";
/* The Meta Conversions API: when a site order is paid, the sale goes straight to Meta (server to server), so the ads
   learn who buys even when the browser blocks the Pixel. The browser's Pixel sends the same Purchase with the order
   number as its eventID; Meta sees the same event_id here and counts the sale once.
   The customer's email, phone, name and address go hashed (SHA-256), never in the clear. Nothing is sent when the
   browser asked for no tracking (Global Privacy Control), nor for orders that didn't come from the site.
   A failure here never touches the order: it is only logged. */
const crypto = require("crypto");
const deps = require("./deps");

const sha = (v) => (v ? crypto.createHash("sha256").update(String(v)).digest("hex") : undefined);
const low = (v) => String(v || "").trim().toLowerCase();

/** Meta's rules for each field, before hashing. */
function userData(o) {
  const ship = o.shipping || {}, a = ship.address || {};
  const name = low(ship.name || o.name).replace(/[^\p{L}\s'-]/gu, "").split(/\s+/).filter(Boolean);
  let ph = String(ship.phone || "").replace(/\D/g, "");
  if (ph.length === 10 && low(a.country || "us") === "us") ph = "1" + ph;
  const country = low(a.country).slice(0, 2);
  const c = o.client || {};
  const u = {
    em: o.email ? [sha(low(o.email))] : undefined,
    ph: ph.length >= 8 ? [sha(ph)] : undefined,
    fn: name.length ? [sha(name[0])] : undefined,
    ln: name.length > 1 ? [sha(name[name.length - 1])] : undefined,
    ct: a.city ? [sha(low(a.city).replace(/[^\p{L}]/gu, ""))] : undefined,
    st: a.state ? [sha(low(a.state).replace(/[^a-z]/g, "").slice(0, 2))] : undefined,
    zp: a.postal_code ? [sha(low(a.postal_code).replace(/\s/g, "").slice(0, country === "us" || !country ? 5 : 10))] : undefined,
    country: country ? [sha(country)] : undefined,
    external_id: o.uid || o.guestUid ? [sha(o.uid || o.guestUid)] : undefined,
    client_ip_address: c.ip || undefined,
    client_user_agent: c.ua || undefined,
    fbp: c.fbp || undefined,
    fbc: c.fbc || undefined,
  };
  Object.keys(u).forEach((k) => { if (u[k] === undefined) delete u[k]; });
  return u;
}

/** The Purchase event for a paid order (pure). */
function purchaseEvent(o, orderId, siteUrl) {
  const items = o.items || [];
  const t = Date.parse(o.paidAt || o.createdAt || "") || Date.now();
  return {
    event_name: "Purchase", event_time: Math.floor(t / 1000), event_id: String(o.number), action_source: "website",
    event_source_url: `${siteUrl}/thank-you.html`, user_data: userData(o),
    custom_data: {
      currency: "USD", value: Math.round((Number(o.pricing && o.pricing.total) || 0) * 100) / 100, order_id: String(o.number),
      content_type: "product", content_ids: items.map((it) => String(it.id || it.kind || "")).filter(Boolean),   // the same ids the browser sends
      num_items: items.reduce((n, it) => n + (Number(it.qty) || 1), 0),
    },
  };
}

/** Sends the sale to Meta. Never throws. */
async function purchase(o, orderId) {
  try {
    if (!o || o.source !== "site" || !o.number) return { skipped: "not a site order" };
    if (o.client && o.client.gpc) return { skipped: "no tracking (GPC)" };
    const snap = await deps.db().collection("ads").doc("auth").get();
    const meta = snap.exists ? (snap.data() || {}).meta : null;
    if (!meta || !meta.pixelId || !meta.token) return { skipped: "no pixel" };
    const site = (process.env.SITE_URL || "https://littlehivehouse.com").replace(/\/+$/, "");
    const graph = require("./ads")._internal.graph;
    const r = await graph(meta, "POST", `${meta.pixelId}/events`, { data: [purchaseEvent(o, orderId, site)] });
    return { sent: true, received: r.events_received };
  } catch (e) {
    console.log("[metaevents] purchase", orderId, e.message);
    return { error: e.message };
  }
}

module.exports = { purchase, purchaseEvent, userData };
