"use strict";
/* Server prices must equal the cart drawer's totals() in assets/site.js, to the cent. */
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("fs");
const path = require("path");
const vm = require("vm");
const P = require("../pricing");
const { priceCart, allocate, computeTotals, rulesOf } = P;
const catalog = require("../catalog.json");

const SITE_JS = path.join(__dirname, "..", "..", "assets", "site.js");

/** Pulls PRICE/BUNDLE/SHIPPING/VOLUME constants and totals() out of site.js and returns totals(cart). */
function loadSiteTotals() {
  const src = fs.readFileSync(SITE_JS, "utf8");
  const names = ["PRICE", "BUNDLE_N", "BUNDLE_PRICE", "SHIPPING", "FREE_SHIP_AT", "VOLUME"];
  const decls = src.split("\n").filter((l) => /^\s*var\s/.test(l) && names.some((n) => new RegExp(`\\b${n}\\s*=`).test(l)));
  for (const n of names) assert.ok(decls.some((l) => new RegExp(`\\b${n}\\s*=`).test(l)), `site.js: constant ${n} not found`);
  const start = src.indexOf("function totals()");
  assert.ok(start >= 0, "site.js: function totals() not found");
  let depth = 0, end = -1;
  for (let i = src.indexOf("{", start); i < src.length; i++) {
    if (src[i] === "{") depth++;
    else if (src[i] === "}") { depth--; if (depth === 0) { end = i + 1; break; } }
  }
  const code = `${decls.join("\n")}\nvar cart = [];\n${src.slice(start, end)}\nthis.run = function (c) { cart = c; return totals(); };`;
  const ctx = {};
  vm.runInNewContext(code, ctx);
  return ctx.run;
}

const designIds = Object.keys(catalog.designs);
const packSizes = Object.keys(catalog.packs).map(Number);
const packageIds = Object.keys(catalog.packages).filter((id) => !catalog.packages[id].digital);   // the design file needs a design (own test)

function seeded(seed) {
  let s = seed >>> 0;
  return () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; };
}

/** A random cart as the site holds it (site lines) and as checkout.js sends it (payload lines). */
function randomCart(rnd) {
  const site = [], payload = [];
  const n = 1 + Math.floor(rnd() * 7);
  const used = new Set();
  for (let i = 0; i < n; i++) {
    const r = rnd();
    const big = rnd() < 0.15;
    const qty = 1 + Math.floor(rnd() * (big ? 60 : 4));
    if (r < 0.6) {
      const id = designIds[Math.floor(rnd() * designIds.length)];
      if (used.has(id)) continue;
      used.add(id);
      site.push({ id, kind: "design", price: 5, qty });
      payload.push({ kind: "design", id, qty });
    } else if (r < 0.85) {
      const size = packSizes[Math.floor(rnd() * packSizes.length)];
      const q = 1 + Math.floor(rnd() * 3);
      site.push({ id: `custom-${i}`, kind: "custom", count: size, price: catalog.packs[size].price, qty: q });
      payload.push({ kind: "photos", packSize: size, qty: q, photos: [{ path: "", frame: "none", caption: "" }] });
    } else {
      const id = packageIds[Math.floor(rnd() * packageIds.length)];
      const p = catalog.packages[id];
      const q = 1 + Math.floor(rnd() * 2);
      site.push({ id, kind: "package", count: p.size, price: p.price, qty: q });
      payload.push({ kind: "package", id, qty: q });
    }
  }
  return { site, payload };
}

const c = (x) => Math.round(x * 100);

test("site.js totals() and pricing.js agree on 5000 random carts", () => {
  const siteTotals = loadSiteTotals();
  const rnd = seeded(20261010);
  let checked = 0, withVolume = 0, freeShip = 0, bundles = 0;
  for (let k = 0; k < 5000; k++) {
    const { site, payload } = randomCart(rnd);
    if (!site.length) continue;
    const a = siteTotals(site);
    const b = priceCart(payload, catalog);
    const t = b.totals;
    const ctx = JSON.stringify(site);
    assert.equal(t.sub, c(a.sub), `subtotal ${ctx}`);
    assert.equal(t.bundle, c(a.disc), `bundle ${ctx}`);
    assert.equal(t.pct, a.pct, `volume pct ${ctx}`);
    assert.equal(t.vol, c(a.vol), `volume discount ${ctx}`);
    assert.equal(t.goods, c(a.goods), `goods ${ctx}`);
    assert.equal(t.ship, c(a.ship), `shipping ${ctx}`);
    assert.equal(t.total, c(a.total), `total ${ctx}`);
    assert.equal(t.magnets, a.magnets, `magnets ${ctx}`);
    assert.equal(b.pricing.total, Math.round(a.total * 100) / 100);
    if (t.pct) withVolume++;
    if (!t.ship) freeShip++;
    if (t.bundle) bundles++;
    checked++;
  }
  assert.ok(checked > 4000 && withVolume > 300 && freeShip > 300 && bundles > 300, `coverage ${checked}/${withVolume}/${freeShip}/${bundles}`);
});

test("edge carts: thresholds for bundle, volume tiers and free shipping", () => {
  const siteTotals = loadSiteTotals();
  const cases = [];
  for (let d = 1; d <= 120; d++) cases.push([{ id: designIds[0], kind: "design", price: 5, qty: d }]);
  for (const s of packSizes) cases.push([{ kind: "custom", count: s, price: catalog.packs[s].price, qty: 1 }, { id: designIds[1], kind: "design", price: 5, qty: 2 }]);
  for (const id of packageIds) cases.push([{ id, kind: "package", count: catalog.packages[id].size, price: catalog.packages[id].price, qty: 1 }]);
  for (const site of cases) {
    const payload = site.map((l) => (l.kind === "design" ? { kind: "design", id: l.id, qty: l.qty }
      : l.kind === "package" ? { kind: "package", id: l.id, qty: l.qty }
        : { kind: "photos", packSize: l.count, qty: l.qty, photos: [{ frame: "none" }] }));
    const a = siteTotals(site), t = priceCart(payload, catalog).totals;
    assert.equal(t.total, c(a.total), JSON.stringify(site));
    assert.equal(t.ship, c(a.ship), JSON.stringify(site));
  }
});

test("client prices are ignored and bad lines are refused", () => {
  const ok = priceCart([{ kind: "design", id: designIds[0], qty: 1, price: 0.01 }], catalog);
  assert.equal(ok.pricing.subtotal, 5);
  const bad = [
    [], [{ kind: "design", id: "nope/nope", qty: 1 }], [{ kind: "design", id: designIds[0], qty: 0 }],
    [{ kind: "design", id: designIds[0], qty: 1.5 }], [{ kind: "design", id: designIds[0], qty: 9999 }],
    [{ kind: "photos", packSize: 7, photos: [{}] }], [{ kind: "photos", packSize: 4, photos: [] }],
    [{ kind: "photos", packSize: 4, photos: [{}, {}, {}, {}, {}] }], [{ kind: "photos", packSize: 4, photos: [{ frame: "made-up" }] }],
    [{ kind: "package", id: "weddings-7", qty: 1 }], [{ kind: "custom", title: "x", amount: 1 }], [{ kind: "other" }], "x",
  ];
  for (const cart of bad) assert.throws(() => priceCart(cart, catalog), (e) => e.code === "invalid-argument", JSON.stringify(cart));
});

test("captions are cut to each frame's limit; frames without captions drop them", () => {
  const capFrame = Object.entries(catalog.frames).find(([, f]) => f.captionMax > 0);
  const r = priceCart([{ kind: "photos", packSize: 4, photos: [
    { path: "uploads/u/p/1.jpg", frame: capFrame[0], caption: "x".repeat(100) },
    { path: "uploads/u/p/2.jpg", frame: "none", caption: "ignored" }] }], catalog);
  assert.equal(r.items[0].photos[0].caption.length, capFrame[1].captionMax);
  assert.equal(r.items[0].photos[1].caption, "");
});

test("duplicate design lines merge; magnets count designs + packs + packages", () => {
  const r = priceCart([{ kind: "design", id: designIds[0], qty: 2 }, { kind: "design", id: designIds[0], qty: 1 },
    { kind: "package", id: "teams-12", qty: 1 }], catalog);
  assert.equal(r.items.length, 2);
  assert.equal(r.items[0].qty, 3);
  assert.equal(r.totals.magnets, 15);
  assert.equal(r.totals.bundle, 300);
});

test("allocate() spreads discounts so Stripe lines add up to the goods total exactly", () => {
  const rnd = seeded(7);
  const rules = rulesOf(catalog);
  for (let k = 0; k < 3000; k++) {
    const { payload } = randomCart(rnd);
    if (!payload.length) continue;
    const p = priceCart(payload, catalog);
    const shares = allocate(p.lines, p.totals);
    assert.equal(shares.reduce((a, s) => a + s.net, 0), p.totals.goods);
    shares.forEach((s, i) => assert.ok(s.net > 0 && s.net <= p.lines[i].unit * p.lines[i].qty));
    assert.deepEqual(computeTotals(p.lines, rules), p.totals);
  }
});

test("catalog.json matches the prices printed on the built pages", () => {
  const root = path.join(__dirname, "..", "..");
  const photo = fs.readFileSync(path.join(root, "photo-magnets.html"), "utf8");
  const packs = [...photo.matchAll(/name="pack"[^>]*value="(\d+)" data-price="(\d+(?:\.\d+)?)"/g)];
  assert.ok(packs.length >= 5, "photo pack radios found");
  for (const [, n, p] of packs) {
    if (n === "1") { assert.equal(catalog.photoPricing.extra["0"], Number(p), "1 to 3 photos, each"); continue; }   // "1 to 3": per photo
    assert.equal(catalog.packs[n] && catalog.packs[n].price, Number(p), `photo pack ${n}`);
  }
  const rules = JSON.parse(photo.match(/data-pricing='([^']+)'/)[1].replace(/&#39;/g, "'"));   // the builder's own copy of the photo prices
  assert.deepEqual(rules.extra, catalog.photoPricing.extra);
  assert.equal(rules.max, catalog.photoPricing.max);
  assert.deepEqual(rules.packs, Object.values(catalog.packs).map((p) => [p.size, p.price]));
  // the packs are sold on big-orders.html and on the bulk pages (business, weddings, graduation, parties: the mailing service too)
  const big = ["big-orders.html", "business.html", "weddings.html", "graduation.html", "parties.html"].map((f) => fs.readFileSync(path.join(root, f), "utf8")).join("\n");
  const tiers = [...big.matchAll(/value="([a-z]+-\d+)" data-size="(\d+)" data-price="(\d+(?:\.\d+)?)"/g)];
  assert.deepEqual([...new Set(tiers.map((t) => t[1]))].sort(), Object.keys(catalog.packages).filter((id) => !catalog.packages[id].digital).sort(), "every package is on a page");
  // the design file: its price on the studio's button
  assert.ok(big.includes(`data-dz-digital data-price="${catalog.packages["digital-file"].price}"`), "design file price on the studio");
  for (const [, id, size, price] of tiers) {
    assert.ok(catalog.packages[id], `package ${id} in catalog.json`);
    assert.equal(catalog.packages[id].size, Number(size), id);
    assert.equal(catalog.packages[id].price, Number(price), id);
  }
  const shop = fs.readFileSync(path.join(root, "shop.html"), "utf8");
  const ids = [...shop.matchAll(/data-add="([^"]+)"/g)].map((m) => m[1]);
  assert.ok(ids.length > 100);
  for (const id of ids) assert.ok(catalog.designs[id], `design ${id} in catalog.json`);
});

/* Any number of photo magnets (15 Nov 2026): pack + extra photos at that pack's rate, never more than the next pack. */
test("photoPrice: pack + extras, capped at the next pack, $4 each under 4", () => {
  const want = { 1: 4, 3: 12, 4: 14, 5: 17, 8: 25, 9: 25, 10: 27.75, 12: 33.25, 15: 40, 16: 40, 18: 45, 20: 50, 24: 60, 25: 65, 30: 77.5, 47: 120, 50: 120, 51: 122.4, 100: 240 };
  for (const [n, p] of Object.entries(want)) assert.equal(P.photoPrice(Number(n), catalog), p, `${n} photos`);
  let last = 0;
  for (let n = 1; n <= 100; n++) { const p = P.photoPrice(n, catalog); assert.ok(p >= last, `price never goes down (${n})`); last = p; }
});

test("priceCart: any number of photos from 1 to 100, priced on the server", () => {
  const photos = (k) => Array.from({ length: k }, (_, i) => ({ path: `uploads/u/custom-1/${i + 1}.jpg`, frame: "none" }));
  const r = P.priceCart([{ kind: "photos", packSize: 18, qty: 1, photos: photos(18), price: 0.01 }], catalog);
  assert.equal(r.items[0].price, 45);
  assert.equal(r.items[0].title, "Custom photo magnets (18)");
  assert.equal(r.lines[0].count, 18);
  assert.equal(P.priceCart([{ kind: "photos", packSize: 16, qty: 1, photos: photos(10) }], catalog).items[0].price, 40, "a pack still repeats photos");
  assert.throws(() => P.priceCart([{ kind: "photos", packSize: 18, qty: 1, photos: photos(10) }], catalog), /any number from 1 to 100/, "18 magnets from 10 photos is not a thing");
  assert.throws(() => P.priceCart([{ kind: "photos", packSize: 101, qty: 1, photos: photos(101) }], catalog), /1 to 100/);
  assert.throws(() => P.priceCart([{ kind: "photos", packSize: 2.5, qty: 1, photos: photos(2) }], catalog), /1 to 100/);
});

test("bulk packs keep the price on the page (no volume discount on top); the mailing service counts no magnets", () => {
  const r = priceCart([{ kind: "package", id: "business-100", qty: 1, style: "pizza" }, { kind: "package", id: "mailing-100", qty: 1 }], catalog);
  assert.equal(r.pricing.subtotal, 400);
  assert.equal(r.pricing.volumeDiscount, 0);
  assert.equal(r.pricing.total, 400);
  assert.equal(r.pricing.magnets, 100);
  assert.equal(r.items[0].style, "pizza");
  assert.equal(r.items[1].addresses, 100);
  // designs next to a pack still get their volume discount (the pack's magnets count toward the tier)
  const d = Object.keys(catalog.designs)[0];
  const m = priceCart([{ kind: "package", id: "business-100", qty: 1 }, { kind: "design", id: d, qty: 1 }], catalog);
  assert.equal(m.pricing.volumePct, 25);
  assert.equal(m.pricing.volumeDiscount, 1.25);
  // a style that isn't a slug is dropped
  assert.equal(priceCart([{ kind: "package", id: "weddings-50", qty: 1, style: "<b>x</b>" }], catalog).items[0].style, undefined);
});

test("the QR magnet maker: the link, name and message go with the pack; a link that isn't a web address is refused", () => {
  const qr = { url: "https://g.page/r/abc/review", name: "Little Fern Café", top: "Loved your visit?", cta: "SCAN & TELL US", stars: true, pal: "navy" };
  const r = priceCart([{ kind: "package", id: "business-100", qty: 1, style: "qr", qr }], catalog);
  assert.deepEqual(r.items[0].qr, qr);
  assert.equal(r.items[0].style, "qr");
  assert.equal(r.pricing.total, 160);
  assert.equal(priceCart([{ kind: "package", id: "business-50", qty: 1, qr: { ...qr, pal: "<x>" } }], catalog).items[0].qr.pal, "fern");
  assert.throws(() => priceCart([{ kind: "package", id: "business-50", qty: 1, qr: { ...qr, url: "javascript:alert(1)" } }], catalog), /web address/);
});

test("the design studio: colors, changed words, drawing, QR link and uploaded files go with the pack; anything odd is dropped", () => {
  const design = { slug: "pizza-night", colors: { bg: "#b3261e", ink: "#FFFFFF", ac: "#FFD166" }, text: { name: "Luigi’s", phone: "(555) 123-4567", "<x>": "no" },
    icon: "pizza", url: "https://luigis.com/menu", logo: "uploads/AbC123xyz/d1abc/1.png", photo: "../../etc/passwd" };
  const r = priceCart([{ kind: "package", id: "business-100", qty: 1, style: "pizza-night", design }], catalog);
  assert.deepEqual(r.items[0].design, { slug: "pizza-night", colors: { bg: "#B3261E", ink: "#FFFFFF", ac: "#FFD166" }, text: { name: "Luigi’s", phone: "(555) 123-4567" },
    icon: "pizza", url: "https://luigis.com/menu", logo: "uploads/AbC123xyz/d1abc/1.png" });
  assert.equal(r.pricing.total, 160);
  const bad = priceCart([{ kind: "package", id: "business-50", qty: 1, design: { slug: "pizza-night", colors: { bg: "red", ink: "#000000", ac: "#000000" }, icon: "<svg>" } }], catalog);
  assert.equal(bad.items[0].design.colors, undefined);
  assert.equal(bad.items[0].design.icon, undefined);
  assert.throws(() => priceCart([{ kind: "package", id: "business-50", qty: 1, design: { slug: "<b>" } }], catalog), /design/);
  assert.throws(() => priceCart([{ kind: "package", id: "business-50", qty: 1, design: { slug: "x-y", url: "javascript:alert(1)" } }], catalog), /web address/);
});

test("a design file only: no magnet, no shipping, needs the design and its uploaded PNG; magnet packs may carry the file free", () => {
  const design = { slug: "pizza-night", text: {} };
  const file = "uploads/AbC123xyz/d1abc/3.png";
  const r = priceCart([{ kind: "package", id: "digital-file", qty: 1, style: "pizza-night", design, file }], catalog);
  assert.equal(r.items[0].digital, true);
  assert.equal(r.items[0].file, file);
  assert.equal(r.totals.ship, 0);
  assert.equal(r.pricing.total, 4.99);
  assert.equal(r.totals.magnets, 0);
  assert.throws(() => priceCart([{ kind: "package", id: "digital-file", qty: 1, design }], catalog), /didn't upload/);
  assert.throws(() => priceCart([{ kind: "package", id: "digital-file", qty: 1, file }], catalog), /Pick a design/);
  // with a magnet pack: the file rides along, and shipping is the pack's
  const both = priceCart([{ kind: "package", id: "business-50", qty: 1, design, file }, { kind: "package", id: "digital-file", qty: 1, design, file }], catalog);
  assert.equal(both.items[0].file, file);
  assert.equal(both.items[0].digital, undefined);
  // a file path that isn't an upload is dropped
  assert.equal(priceCart([{ kind: "package", id: "business-50", qty: 1, design, file: "../x.png" }], catalog).items[0].file, undefined);
});
