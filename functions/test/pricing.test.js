"use strict";
/* Server prices must equal the cart drawer's totals() in assets/site.js, to the cent. */
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("fs");
const path = require("path");
const vm = require("vm");
const { priceCart, allocate, computeTotals, rulesOf } = require("../pricing");
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
const packageIds = Object.keys(catalog.packages);

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
  for (const [, n, p] of packs) assert.equal(catalog.packs[n] && catalog.packs[n].price, Number(p), `photo pack ${n}`);
  const big = fs.readFileSync(path.join(root, "big-orders.html"), "utf8");
  const tiers = [...big.matchAll(/value="([a-z]+-\d+)" data-size="(\d+)" data-price="(\d+(?:\.\d+)?)"/g)];
  assert.ok(tiers.length >= Object.keys(catalog.packages).length, "package tiers found");
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
