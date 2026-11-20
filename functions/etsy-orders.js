"use strict";
/* Etsy orders in Hive Admin (etsyOrders, every 15 minutes): each paid Etsy receipt becomes an order here, with its own
   LHH number, the buyer's address, and items the Hive Admin knows how to make:
   - a design from a collection listing ("07 Ho Ho Ho!" in the Design menu) -> the same design item as a site order;
   - a business or Personalize listing (tools/etsy_custom.py): the pack and the design number the buyer wrote in the
     personalization box -> a package with the design already filled in (name, phone, website), so the print file is
     made like for a site order; the owners fix the words in the design editor if the buyer wrote something else;
   - a photo-magnet listing -> a custom item (the photos come in Etsy; the owners download them there).
   The buyer is Etsy's customer: no email from us (Etsy talks to them). When the owners ship, the tracking number goes to
   Etsy (functions/admin.js adminShip -> shipToEtsy), which tells the buyer. Order docs: orders/etsy-<receipt id>. */

const { nowIso, mailAdmin } = require("./config");
const deps = require("./deps");
const O = require("./orders");
const E = () => require("./etsy")._internal;

const DAY = 86400000;
const money = (m) => (m && m.divisor ? Math.round((Number(m.amount) / Number(m.divisor)) * 100) / 100 : 0);

/** The listing in functions/etsy-listings.json for an Etsy listing id (etsy/listings remembers which is which). */
async function listingMap() {
  const done = ((await deps.db().collection("etsy").doc("listings").get()).data()) || {};
  const byEtsy = {};
  for (const [id, row] of Object.entries(done)) if (row && row.listingId) byEtsy[String(row.listingId)] = id;
  const L = E().LISTINGS.listings;
  return (etsyId) => L.find((l) => l.id === byEtsy[String(etsyId)]) || null;
}

const vari = (t, re) => ((t.variations || []).find((v) => re.test(String(v.formatted_name || ""))) || {}).formatted_value || "";

/** What the buyer wrote: "Design 12, Tony's Pizza, (555) 123-4567, tonyspizza.com" -> {n, words, rest}. */
function readPersonalization(text) {
  const raw = String(text || "").replace(/&quot;/g, "\"").replace(/&#39;/g, "'").replace(/&amp;/g, "&").trim();
  let n = null, s = raw;
  const m = /(?:design|#|n[ºo°]\.?|number)\s*#?\s*(\d{1,3})\b/i.exec(s) || /^\s*(\d{1,3})\b[\s.,:)\-–]*/.exec(s);
  if (m) { n = Number(m[1]); s = (s.slice(0, m.index) + " " + s.slice(m.index + m[0].length)).trim(); }
  const parts = s.split(/\s*(?:\n|;|,(?!\d{3})|\s[-–|]\s)\s*/).map((x) => x.trim()).filter(Boolean);
  const words = {}, rest = [];
  for (const p of parts) {
    const ph = /(\+?1[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}/.exec(p);
    if (ph && !words.phone) { words.phone = ph[0].trim(); const left = p.replace(ph[0], "").replace(/^(phone|tel|cell)\s*:?\s*/i, "").trim(); if (left) rest.push(left); continue; }
    if (!words.web && /(https?:\/\/|www\.|\.[a-z]{2,}(\/|$)|^@\w)/i.test(p)) { words.web = p.replace(/^https?:\/\//i, "").replace(/^(website|site|web)\s*:?\s*/i, ""); continue; }
    rest.push(p.replace(/^(name|business|business name)\s*:?\s*/i, ""));
  }
  if (rest.length) words.name = rest.shift();
  return { n, words, rest, raw };
}

/** One Etsy line -> an order item. */
function itemFor(t, l) {
  const qty = Math.max(1, Number(t.quantity) || 1);
  const unit = money(t.price);
  const perso = vari(t, /personali/i);
  const note = perso ? `Etsy personalization: ${perso}` : "";
  if (!l) return { kind: "custom", title: String(t.title || "Etsy item").slice(0, 120), magnets: qty, price: unit, qty: 1, notes: note, etsy: { listingId: t.listing_id, transactionId: t.transaction_id } };
  if (l.kind === "design") {
    const opt = vari(t, /design/i);
    const n = Number((/^(\d{1,3})/.exec(opt) || [])[1]);
    const id = (l.designs || [])[n - 1];
    if (id) {
      const c = require("./catalog.json").designs[id] || {};
      return { kind: "design", id, title: c.title || opt.replace(/^\d+\s*/, ""), collection: c.collection || l.id, qty, unit, etsy: { listingId: t.listing_id, option: opt } };
    }
    return { kind: "custom", title: `${l.name}: ${opt || t.title}`.slice(0, 120), magnets: qty, price: unit, qty: 1, notes: "Couldn't tell which design from the Etsy menu. " + note };
  }
  if (l.kind === "custom") {
    const pack = vari(t, /pack|size|quantity/i);
    const size = Number((/(\d+)/.exec(pack) || [])[1]) || 1;
    const biz = l.id.startsWith("biz-");
    const p = readPersonalization(perso);
    const slug = p.n && (l.designs || [])[p.n - 1];
    const item = { kind: "package", id: `${biz ? "business" : "personal"}-${size}`, title: `${biz ? "Business" : "Personalized"} magnets, ${l.name}`, size, price: unit, qty,
      notes: note, etsy: { listingId: t.listing_id, designNumber: p.n || null } };
    if (slug) { item.style = slug; item.design = { slug, text: {}, fromEtsy: p.words }; }
    return item;
  }
  // photo magnets: the photos are in Etsy's personalization (download them there)
  const pack = vari(t, /pack|size/i);
  const size = Number((/(\d+)/.exec(pack) || [])[1]) || 1;
  return { kind: "custom", title: `Photo magnets from Etsy (${pack || size})`, magnets: size * qty, price: unit * qty, qty: 1, notes: (note || "") + " Photos: in the Etsy order." };
}

/** The design's own words with what the buyer wrote put in (only the fields the design has). */
function fillWords(design, words) {
  const k = (require("./design-keys.json")[design.slug] || "").split(",");
  if (!k[0]) return {};
  const out = {};
  if (words.name) { const f = ["name", "head", "a", "line"].find((x) => k.includes(x)); if (f) out[f] = words.name; }
  if (words.phone && k.includes("phone")) out.phone = words.phone;
  if (words.web && k.includes("web")) out.web = words.web;
  return out;
}

async function importOrders({ days = 30 } = {}) {
  const a = await E().readAuth();
  if (!a || !a.shopId) return { connected: false };
  const find = await listingMap();
  const db = deps.db();
  const since = Math.floor((Date.now() - days * DAY) / 1000);
  const sum = { checked: 0, added: 0 };
  let offset = 0;
  for (let page = 0; page < 5; page++) {
    const j = await E().call("GET", `/shops/${a.shopId}/receipts?was_paid=true&min_created=${since}&limit=50&offset=${offset}`);
    const list = j.results || [];
    for (const r of list) {
      sum.checked++;
      const ref = db.collection("orders").doc(`etsy-${r.receipt_id}`);
      if ((await ref.get()).exists) continue;
      const items = (r.transactions || []).map((t) => itemFor(t, find(t.listing_id)));
      for (const it of items) if (it.design) {
        try { it.design.text = fillWords(it.design, it.design.fromEtsy || {}); } catch (e) { it.design.text = {}; }
      }
      const at = nowIso();
      const created = r.create_timestamp ? new Date(Number(r.create_timestamp) * 1000).toISOString() : at;
      const magnets = items.reduce((n, it) => n + (it.kind === "design" ? it.qty : it.kind === "package" ? it.size * it.qty : Number(it.magnets) || 0), 0);
      const pricing = { subtotal: money(r.subtotal), shipping: money(r.total_shipping_cost), tax: money(r.total_tax_cost), discount: money(r.discount_amt),
        total: money(r.grandtotal), currency: "usd", magnets, bundleDiscount: 0, volumeDiscount: 0, volumePct: 0, promo: null };
      const shipping = { name: r.name || "", address: { line1: r.first_line || "", line2: r.second_line || "", city: r.city || "", state: r.state || "",
        postal_code: r.zip || "", country: r.country_iso || "US" } };
      const notes = [];
      items.forEach((it) => { if (it.notes) notes.push({ at, by: "etsy", text: it.notes.trim() }); });
      if (r.message_from_buyer) notes.push({ at, by: "etsy", text: `Message from the buyer: ${r.message_from_buyer}` });
      const order = await db.runTransaction(async (tx) => {
        const cRef = db.collection("meta").doc("counters");
        const c = await tx.get(cRef);
        const again = await tx.get(ref);
        if (again.exists) return null;
        const n = O.nextOrderNumber(c.exists ? c.data().orderNumber : undefined);
        const o = {
          number: O.formatOrderNumber(n), source: "etsy", email: "", name: r.name || "", status: r.is_shipped ? "shipped" : "paid",
          items, pricing, shipping, giftMessage: r.gift_message || "", notes: r.message_from_buyer || "", lang: "en",
          payment: { state: "captured", capturedAt: created, by: "etsy" }, stripe: null,
          etsy: { receiptId: String(r.receipt_id), shopId: String(a.shopId), url: `https://www.etsy.com/your/orders/sold?order_id=${r.receipt_id}`, isGift: !!r.is_gift },
          fulfillment: null, refunds: [], refundedTotal: 0, adminNotes: notes,
          timeline: [{ at: created, status: "paid", text: "Paid on Etsy." }],
          emails: { confirmation: null, shipped: null, delivered: null, refund: [] },
          createdAt: created, paidAt: created, updatedAt: at,
        };
        tx.set(cRef, { orderNumber: n }, { merge: true });
        tx.set(ref, o);
        return o;
      });
      if (!order) continue;
      sum.added++;
      // the owners hear about it like a site order (email + phone); the buyer gets nothing from us
      try { await require("./mail").send({ to: mailAdmin(), kind: "admin_new_order", data: { order: { id: ref.id, ...O.emailOrder(ref.id, order), source: "etsy" } } }); } catch (e) { /* never blocks */ }
    }
    if (list.length < 50) break;
    offset += 50;
  }
  console.log("[etsyOrders]", JSON.stringify(sum));
  return sum;
}

/** The tracking number to Etsy, which marks the order shipped and emails the buyer. */
async function shipToEtsy(order, carrier, tracking) {
  const e = order.etsy || {};
  if (!e.receiptId) return { sent: false };
  const names = { usps: "usps", ups: "ups", fedex: "fedex", dhl: "dhl" };
  await E().call("POST", `/shops/${e.shopId}/receipts/${e.receiptId}/tracking`, { form: { tracking_code: tracking, carrier_name: names[carrier] || "other", send_bcc: "false" } });
  return { sent: true };
}

module.exports = { importOrders, shipToEtsy, readPersonalization, itemFor };
