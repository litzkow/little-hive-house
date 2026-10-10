"use strict";
/* Server-side prices. Must give exactly the same numbers as totals() in assets/site.js
   (test/pricing.test.js loads that function and compares thousands of random carts).
   All math is in integer cents; stored order amounts are dollars with 2 decimals. */

const { AppError } = require("./config");

const MAX_LINES = 100;          // Stripe Checkout allows 100 line items
const MAX_QTY = 500;
const MAX_MAGNETS = 5000;

const cents = (d) => Math.round(Number(d) * 100);
const dollars = (c) => Math.round(c) / 100;

let _catalog = null;
function loadCatalog() {
  if (!_catalog) _catalog = require("./catalog.json");
  return _catalog;
}

/** Rules from catalog.json, as cents. */
function rulesOf(catalog) {
  const r = catalog.rules;
  return {
    designPrice: cents(r.designPrice),
    bundleSize: r.bundle.size,
    bundlePrice: cents(r.bundle.price),
    volume: r.volume.map((v) => [v.min, v.pct]).sort((a, b) => b[0] - a[0]),
    shipping: cents(r.shipping),
    freeShippingAt: cents(r.freeShippingAt),
    currency: r.currency || "usd",
  };
}

/** The same steps as site.js totals(), in cents. lines: [{kind, unit (cents), qty, count}] */
function computeTotals(lines, rules) {
  let sub = 0, designs = 0, magnets = 0;
  for (const l of lines) {
    sub += l.unit * l.qty;
    if (l.kind === "design") designs += l.qty;
    magnets += l.qty * (l.count || 1);
  }
  const bundle = Math.floor(designs / rules.bundleSize) * (rules.bundleSize * rules.designPrice - rules.bundlePrice);
  const tier = rules.volume.find((v) => magnets >= v[0]);
  const pct = tier ? tier[1] : 0;
  const vol = Math.round(((sub - bundle) * pct) / 100);
  const goods = sub - bundle - vol;
  const ship = goods >= rules.freeShippingAt ? 0 : rules.shipping;
  return { sub, bundle, pct, vol, goods, ship, total: goods + ship, magnets, designs };
}

const bad = (msg) => new AppError("invalid-argument", msg);
const str = (v, max) => (typeof v === "string" ? v.trim().slice(0, max) : "");

function intQty(v, max, what) {
  const n = v === undefined || v === null ? 1 : Number(v);
  if (!Number.isInteger(n) || n < 1 || n > max) throw bad(`${what}: quantity must be a whole number from 1 to ${max}.`);
  return n;
}

/**
 * Validates a cart from the site and prices it.
 * Accepted lines (prices sent by the client are ignored):
 *   {kind:"design", id:"places/new-york", qty}
 *   {kind:"photos"|"custom", packSize|count, qty?, photos:[{path, frame, caption}], notes}
 *   {kind:"package", id:"weddings-50", qty}
 * Returns {items (order items, dollars), lines (cents, for Stripe), totals (cents), pricing (dollars)}.
 */
function priceCart(cart, catalog = loadCatalog()) {
  if (!Array.isArray(cart) || cart.length === 0) throw bad("Your cart is empty.");
  if (cart.length > MAX_LINES) throw bad(`A cart can hold up to ${MAX_LINES} different items.`);
  const rules = rulesOf(catalog);
  const frames = catalog.frames || {};
  const items = [], lines = [];
  const designIndex = new Map();

  cart.forEach((raw, i) => {
    if (!raw || typeof raw !== "object") throw bad(`Cart line ${i + 1} is not valid.`);
    const kind = raw.kind === "place" ? "design" : raw.kind;
    if (kind === "design") {
      const id = str(raw.id, 120);
      const d = catalog.designs[id];
      if (!d) throw bad(`We couldn't find the design "${id || "?"}". Please remove it from your cart and add it again.`);
      const qty = intQty(raw.qty, MAX_QTY, d.title);
      const unit = cents(d.price);
      if (designIndex.has(id)) {           // the same design twice: merge the lines
        const k = designIndex.get(id);
        lines[k].qty += qty; items[k].qty += qty;
        if (lines[k].qty > MAX_QTY) throw bad(`${d.title}: quantity must be a whole number from 1 to ${MAX_QTY}.`);
        return;
      }
      designIndex.set(id, items.length);
      items.push({ kind: "design", id, title: d.title, collection: d.collection, qty, unit: dollars(unit) });
      lines.push({ kind: "design", unit, qty, count: 1, name: `${d.title} magnet`, id, collection: d.collection });
    } else if (kind === "photos" || kind === "custom") {
      const size = Number(raw.packSize !== undefined ? raw.packSize : raw.count);
      const pack = catalog.packs[String(size)];
      if (!pack) throw bad(`Photo packs come in ${Object.keys(catalog.packs).join(", ")} magnets.`);
      const qty = intQty(raw.qty, 20, "Photo pack");
      const photos = Array.isArray(raw.photos) ? raw.photos : [];
      if (photos.length < 1) throw bad("A photo pack needs at least one photo.");
      if (photos.length > size) throw bad(`This pack holds ${size} photos, but ${photos.length} were added.`);
      const clean = photos.map((p, n) => {
        const frame = str(p && p.frame, 40) || "none";
        const f = frames[frame];
        if (Object.keys(frames).length && !f) throw bad(`Photo ${n + 1}: unknown frame "${frame}".`);
        const max = f && f.captionMax ? f.captionMax : 0;
        const caption = max ? str(p && p.caption, max) : "";
        return { path: str(p && p.path, 300), frame, caption };
      });
      const unit = cents(pack.price);
      items.push({ kind: "photos", title: pack.title, packSize: size, price: dollars(unit), qty, photos: clean, notes: str(raw.notes, 1000) });
      lines.push({ kind: "photos", unit, qty, count: size, name: pack.title });
    } else if (kind === "package") {
      const id = str(raw.id, 60);
      const p = catalog.packages[id];
      if (!p) throw bad(`We couldn't find the package "${id || "?"}".`);
      const qty = intQty(raw.qty, 20, p.title);
      const unit = cents(p.price);
      items.push({ kind: "package", id, title: p.title, size: p.size, price: dollars(unit), qty });
      lines.push({ kind: "package", unit, qty, count: p.size, name: p.title });
    } else {
      throw bad(`Cart line ${i + 1} has an unknown kind "${String(raw.kind)}".`);
    }
  });

  const totals = computeTotals(lines, rules);
  if (totals.magnets > MAX_MAGNETS) throw bad(`That is more than ${MAX_MAGNETS} magnets. Please ask us for a quote instead.`);
  return { items, lines, totals, pricing: pricingDollars(totals, rules.currency) };
}

function pricingDollars(t, currency = "usd") {
  return {
    subtotal: dollars(t.sub), bundleDiscount: dollars(t.bundle), volumePct: t.pct, volumeDiscount: dollars(t.vol),
    promo: null, shipping: dollars(t.ship), total: dollars(t.total), currency, magnets: t.magnets,
  };
}

/**
 * Splits the bundle and big-order discounts over the lines so Stripe line items add up to the goods total
 * exactly (Stripe has no negative lines, and promotion codes can't be combined with a session coupon).
 * Returns [{net}] in cents per line; sum(net) === totals.goods.
 */
function allocate(lines, totals) {
  const share = (weights, amount) => {      // largest remainder, integer cents
    const sum = weights.reduce((a, b) => a + b, 0);
    if (!amount || !sum) return weights.map(() => 0);
    const raw = weights.map((w) => (w * amount) / sum);
    const out = raw.map(Math.floor);
    let left = amount - out.reduce((a, b) => a + b, 0);
    const order = raw.map((r, i) => [r - Math.floor(r), i]).sort((a, b) => b[0] - a[0] || a[1] - b[1]);
    for (let k = 0; left > 0; k = (k + 1) % order.length, left--) out[order[k][1]] += 1;
    return out;
  };
  const gross = lines.map((l) => l.unit * l.qty);
  const b = share(lines.map((l, i) => (l.kind === "design" ? gross[i] : 0)), totals.bundle);
  const afterBundle = gross.map((g, i) => g - b[i]);
  const v = share(afterBundle, totals.vol);
  return afterBundle.map((a, i) => ({ net: a - v[i], discount: b[i] + v[i] }));
}

module.exports = { priceCart, computeTotals, allocate, rulesOf, loadCatalog, cents, dollars, MAX_LINES };
