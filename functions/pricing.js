"use strict";
/* Server-side prices. Must give exactly the same numbers as totals() in assets/site.js
   (test/pricing.test.js loads that function and compares thousands of random carts).
   All math is in integer cents; stored order amounts are dollars with 2 decimals. */

const { AppError } = require("./config");
const Crop = require("./crop");

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
    sale: r.sale || null,
  };
}

/* The store-wide sale running at `now` (catalog.json rules.sale), or null: {name, pct, free: [[buy, get]], freeShipping}.
   A "day" inside it (Black Friday itself) takes its own name, % and free shipping. Same as site.js saleNow(). */
function saleNow(sale, now) {
  if (!sale) return null;
  const t = Number(now);
  if (!(t >= Date.parse(sale.start) && t < Date.parse(sale.end))) return null;
  const day = (sale.days || []).find((d) => t >= Date.parse(d.start) && t < Date.parse(d.end));
  return { name: (day && day.name) || sale.name, pct: (day && day.pct) || sale.pct || 0, free: sale.free || [], freeShipping: !!(day && day.freeShipping) };
}

/* "Buy N, get M free": how many of `n` ready-made designs are free (the biggest deal first). Same as site.js freeOf(). */
function freeOf(n, tiers) {
  const t = (tiers || []).slice().sort((a, b) => (b[0] + b[1]) - (a[0] + a[1]));
  let left = n, free = 0;
  for (const [buy, get] of t) { const g = buy + get; while (g > 0 && left >= g) { free += get; left -= g; } }
  return free;
}

/** The same steps as site.js totals(), in cents. lines: [{kind, unit (cents), qty, count}] */
function computeTotals(lines, rules, now = Date.now()) {
  // packages already have their quantity price (and a service, like mailing to a list, is no magnet: count 0), so the
  // volume discount is only on designs and photo packs; their magnets still count toward its tier
  let sub = 0, designs = 0, magnets = 0, pkg = 0;
  for (const l of lines) {
    sub += l.unit * l.qty;
    if (l.kind === "design") designs += l.qty;
    if (l.kind === "package") pkg += l.unit * l.qty;
    magnets += l.qty * (l.count == null ? 1 : l.count);
  }
  const bundleOf = (n) => Math.floor(n / rules.bundleSize) * (rules.bundleSize * rules.designPrice - rules.bundlePrice);
  const bundle = bundleOf(designs);
  const tier = rules.volume.find((v) => magnets >= v[0]);
  const pct = tier ? tier[1] : 0;
  const vol = Math.round(((sub - bundle - pkg) * pct) / 100);
  const goods = sub - bundle - vol;
  // the sale: % off what they pay, or some designs free (the rest keep the 3-for-$12 and big-order prices); never both
  const sale = saleNow(rules.sale, now);
  let promo = 0, promoKind = "", free = 0;
  if (sale) {
    const byPct = Math.round((goods * sale.pct) / 100);
    const f = freeOf(designs, sale.free);
    let byFree = 0;
    if (f > 0) {
      const subF = sub - f * rules.designPrice, bundleF = bundleOf(designs - f);
      const volF = Math.round(((subF - bundleF - pkg) * pct) / 100);
      byFree = goods - (subF - bundleF - volF);
    }
    if (byFree > byPct) { promo = byFree; promoKind = "free"; free = f; } else if (byPct > 0) { promo = byPct; promoKind = "pct"; }
  }
  // a cart of design files only ships nothing; free shipping goes by the order before the sale discount
  const ship = lines.length && lines.every((l) => l.digital) ? 0 : sale && sale.freeShipping ? 0 : goods >= rules.freeShippingAt ? 0 : rules.shipping;
  return {
    sub, bundle, pct, vol, goods: goods - promo, ship, total: goods - promo + ship, magnets, designs, promo,
    sale: sale && promo ? { name: sale.name, kind: promoKind, pct: promoKind === "pct" ? sale.pct : 0, free, freeShipping: sale.freeShipping } : sale && sale.freeShipping ? { name: sale.name, kind: "", pct: 0, free: 0, freeShipping: true } : null,
  };
}

const bad = (msg) => new AppError("invalid-argument", msg);
const str = (v, max) => (typeof v === "string" ? v.trim().slice(0, max) : "");

function intQty(v, max, what) {
  const n = v === undefined || v === null ? 1 : Number(v);
  if (!Number.isInteger(n) || n < 1 || n > max) throw bad(`${what}: quantity must be a whole number from 1 to ${max}.`);
  return n;
}

/**
 * Price of `n` photo magnets: the biggest pack that fits plus each extra photo at that pack's rate, never more than
 * the next pack (under the smallest pack: the "0" rate each). Same math as assets/custom.js photoPrice().
 * Example with the shop's packs: 10 -> $25 + 1 x $2.75 = $27.75; 15 -> $40 (the 16 pack costs that).
 */
function photoPrice(n, catalog = loadCatalog()) {
  const packs = Object.values(catalog.packs || {}).map((p) => [Number(p.size), Number(p.price)]).sort((a, b) => a[0] - b[0]);
  const extra = (catalog.photoPricing && catalog.photoPricing.extra) || {};
  let base = [0, 0];
  for (const p of packs) if (p[0] <= n) base = p;
  const rate = Number(extra[String(base[0])] !== undefined ? extra[String(base[0])] : (base[0] ? base[1] / base[0] : 4));
  let price = base[1] + (n - base[0]) * rate;
  const next = packs.find((p) => p[0] > n);
  if (next && price > next[1]) price = next[1];
  return Math.round(price * 100) / 100;
}

/**
 * Validates a cart from the site and prices it.
 * Accepted lines (prices sent by the client are ignored):
 *   {kind:"design", id:"places/new-york", qty}
 *   {kind:"photos"|"custom", packSize|count, qty?, photos:[{path, frame, caption, crop?, w?, h?}], notes}
 *   {kind:"package", id:"weddings-50", qty}
 * Returns {items (order items, dollars), lines (cents, for Stripe), totals (cents), pricing (dollars)}.
 */
function priceCart(cart, catalog = loadCatalog(), now = Date.now()) {
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
      const max = Number((catalog.photoPricing && catalog.photoPricing.max) || 0);
      const qty = intQty(raw.qty, 20, "Photo pack");
      const photos = Array.isArray(raw.photos) ? raw.photos : [];
      if (photos.length < 1) throw bad("A photo pack needs at least one photo.");
      // a pack (photos repeat in order to fill it) or exactly the photos added, any number up to `max`
      if (!pack && !(max && Number.isInteger(size) && size >= 1 && size <= max && photos.length === size)) {
        throw bad(max ? `Photo magnets come in any number from 1 to ${max}.` : `Photo packs come in ${Object.keys(catalog.packs).join(", ")} magnets.`);
      }
      if (photos.length > size) throw bad(`This pack holds ${size} photos, but ${photos.length} were added.`);
      const clean = photos.map((p, n) => {
        const frame = str(p && p.frame, 40) || "none";
        const f = frames[frame];
        if (Object.keys(frames).length && !f) throw bad(`Photo ${n + 1}: unknown frame "${frame}".`);
        const max = f && f.captionMax ? f.captionMax : 0;
        const caption = max ? str(p && p.caption, max) : "";
        const out = { path: str(p && p.path, 300), frame, caption };
        const styles = (f && Array.isArray(f.captionStyles)) ? f.captionStyles : [];
        if (caption && p && typeof p.capStyle === "string" && styles.includes(p.capStyle)) out.capStyle = p.capStyle;   // the lettering picked
        const crop = Crop.clean(p && p.crop);                 // where the customer moved / zoomed the photo
        if (crop) out.crop = crop;
        const w = Math.round(Number(p && p.w)), h = Math.round(Number(p && p.h));
        if (w > 0 && h > 0 && w < 100000 && h < 100000) { out.w = w; out.h = h; }   // the photo's size, for the admin preview
        return out;
      });
      const unit = cents(pack ? pack.price : photoPrice(size, catalog));
      const title = pack ? pack.title : `Custom photo magnets (${size})`;
      items.push({ kind: "photos", title, packSize: size, price: dollars(unit), qty, photos: clean, notes: str(raw.notes, 1000) });
      lines.push({ kind: "photos", unit, qty, count: size, name: title });
    } else if (kind === "package") {
      const id = str(raw.id, 60);
      const p = catalog.packages[id];
      if (!p) throw bad(`We couldn't find the package "${id || "?"}".`);
      const qty = intQty(raw.qty, 20, p.title);
      const unit = cents(p.price);
      const item = { kind: "package", id, title: p.title, size: p.size, price: dollars(unit), qty };
      if (p.addresses) item.addresses = p.addresses;          // the mailing service: no magnets, a list of addresses
      const style = /^(sc:)?[a-z0-9-]{2,40}$/.test(String(raw.style || "")) ? String(raw.style) : "";
      if (style) item.style = style;                           // the example they want to start from (bulk-order pages)
      if (raw.qr && typeof raw.qr === "object") {             // the QR magnet maker: what to put on the magnet
        const link = str(raw.qr.url, 200);
        if (!/^https?:\/\/\S+\.\S+$/i.test(link)) throw bad("The QR link doesn't look like a web address.");
        item.qr = { url: link, name: str(raw.qr.name, 40), top: str(raw.qr.top, 60), cta: str(raw.qr.cta, 40), stars: !!raw.qr.stars,
          pal: QR_PALS.includes(raw.qr.pal) ? raw.qr.pal : "fern" };
      }
      if (raw.design && typeof raw.design === "object") item.design = cleanDesign(raw.design);   // made in the design studio
      // the design drawn into a 1200 px PNG by the customer's browser (assets/designer.js): the file they get by email
      const file = String(raw.file || "");
      if (UPLOAD.test(file) && /\.png$/i.test(file) && item.design) item.file = file;
      if (p.digital) {   // the design as a file only, no magnet
        if (!item.design) throw bad("Pick a design first.");
        if (!item.file) throw bad("Your design file didn't upload. Please try again.");
        item.digital = true;
      }
      items.push(item);
      lines.push({ kind: "package", unit, qty, count: p.size, name: p.title, ...(p.digital ? { digital: true } : {}) });
    } else {
      throw bad(`Cart line ${i + 1} has an unknown kind "${String(raw.kind)}".`);
    }
  });

  const totals = computeTotals(lines, rules, now);
  if (totals.magnets > MAX_MAGNETS) throw bad(`That is more than ${MAX_MAGNETS} magnets. Please ask us for a quote instead.`);
  return { items, lines, totals, pricing: pricingDollars(totals, rules.currency) };
}

/* What the customer made in the design studio (assets/studio.js): which design, their colors, the words they changed,
   a drawing, the QR link and the paths of their uploaded logo and photo. Anything odd is dropped, never trusted. */
const HEX = /^#[0-9a-f]{6}$/i;
const QR_PALS = ["fern", "honey", "navy", "blush", "brick", "teal", "sky", "plum", "black", "red", "sun", "forest", "lilac", "orange"];   // the QR magnet maker's colors (site.css .qrm)
const UPLOAD = /^uploads\/[A-Za-z0-9]{6,64}\/[A-Za-z0-9_-]{1,64}\/[0-9]{1,3}\.(png|jpg|jpeg|webp)$/;
const ADMIN_FILE = /^prints\/[A-Za-z0-9_-]{4,64}\/[A-Za-z0-9_-]{1,40}\.(png|jpg|jpeg|webp)$/;   // a logo or photo the owners put in (Hive Admin)
function cleanDesign(d, { admin = false } = {}) {
  const slug = String(d.slug || "");
  if (!/^[a-z0-9-]{2,40}$/.test(slug)) throw bad("That design doesn't look right. Please pick it again.");
  const out = { slug };
  if (d.colors && typeof d.colors === "object" && ["bg", "ink", "ac"].every((k) => HEX.test(String(d.colors[k] || "")))) {
    out.colors = { bg: d.colors.bg.toUpperCase(), ink: d.colors.ink.toUpperCase(), ac: d.colors.ac.toUpperCase() };
  }
  const text = {};
  if (d.text && typeof d.text === "object") {
    for (const k of Object.keys(d.text).slice(0, 40)) {
      if (/^[a-z][a-z0-9]{0,11}$/.test(k)) text[k] = String(d.text[k] == null ? "" : d.text[k]).slice(0, 120);
    }
  }
  out.text = text;
  if (/^[a-z]{2,12}$/.test(String(d.icon || ""))) out.icon = d.icon;
  if (d.url) {
    const u = str(d.url, 200);
    if (!/^https?:\/\/\S+\.\S+$/i.test(u)) throw bad("The QR link doesn't look like a web address.");
    out.url = u;
  }
  for (const k of ["logo", "photo"]) if (UPLOAD.test(String(d[k] || "")) || (admin && ADMIN_FILE.test(String(d[k] || "")))) out[k] = d[k];
  if (!out.photo && /^[a-z][a-z-]{1,30}-\d{1,2}$/.test(String(d.stock || ""))) out.stock = d.stock;   // one of our stock photos (assets/stock)
  return out;
}

function pricingDollars(t, currency = "usd") {
  return {
    subtotal: dollars(t.sub), bundleDiscount: dollars(t.bundle), volumePct: t.pct, volumeDiscount: dollars(t.vol),
    promo: null, shipping: dollars(t.ship), total: dollars(t.total), currency, magnets: t.magnets,
    sale: t.sale ? { ...t.sale, amount: dollars(t.promo || 0) } : null,
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
  const afterVol = afterBundle.map((a, i) => a - v[i]);
  // the sale: free designs come off the design lines, a % off comes off everything
  const free = totals.sale && totals.sale.kind === "free";
  const s = share(afterVol.map((a, i) => (!free || lines[i].kind === "design" ? a : 0)), totals.promo || 0);
  return afterVol.map((a, i) => ({ net: a - s[i], discount: b[i] + v[i] + s[i] }));
}

module.exports = {
  photoPrice, priceCart, computeTotals, allocate, rulesOf, loadCatalog, cents, dollars, MAX_LINES, cleanDesign, saleNow, freeOf };
