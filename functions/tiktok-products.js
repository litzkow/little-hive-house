"use strict";
/* The design collections on TikTok Shop, one product per collection, made from the same listings as Etsy
   (etsy-listings.json, kind "design"): title, a TikTok version of the description, the Etsy photos made square
   (TikTok shows square photos: the photo on a blurred copy of itself), and one SKU per design ("Design" sales attribute,
   the design's own art as the SKU picture, seller_sku "<collection>-<n>", the same as Etsy's sku). Price: TIKTOK.price
   for one magnet (each channel has its own price; the owners, Nov 2026). Made to order, so stock is always 99.
   Category 854536 "Refrigerator Magnets" (TikTok's own recommendation for these, category version v2).
   tiktok/products remembers each collection's TikTok product id and SKU ids (orders use them). */

const { fail, siteUrl, nowIso } = require("./config");
const deps = require("./deps");
const T = () => require("./tiktok")._internal;

const TIKTOK = {
  price: 5.5,                 // one magnet
  category: "854536",         // Home Supplies > Home Decor > Refrigerator Magnets
  stock: 99,
  // one magnet in its sleeve, in a kraft A7 envelope with the cards: what the label is bought for
  weight: { value: "0.15", unit: "POUND" },
  dims: { length: "7", width: "5", height: "1", unit: "INCH" },
};
// what is true of every magnet (attribute ids and value ids read from the category, Nov 2026)
const ATTRS = [
  ["100548", "1001505"],      // Shape: Square
  ["100917", "1004810"],      // Magnets: With magnets
  ["101652", "1000058"],      // Handmade: Yes
  ["101314", "1000923"],      // Finish type: Glossy
  ["100336", "1024340"],      // Region of origin: United states
  ["101346", "1021181"],      // Included components: Magnet
  ["100347", "1000256"],      // Quantity per pack: 1
  ["101619", "1000059"],      // Dangerous goods: No
  ["101610", "1000325"],      // Contains batteries or cells: None
  ["101400", "1000059"],      // CA prop 65 carcinogens: No
  ["101395", "1000059"],      // CA prop 65 repro. chems: No
];

const LISTINGS = () => require("./etsy-listings.json").listings.filter((l) => l.kind === "design");
const col = () => deps.db().collection("tiktok");

/** "01 January ·" -> "01 January"; TikTok's sales attribute values are short text. */
const optionName = (o) => String(o).replace(/\s*·\s*$/, "").replace(/\s+/g, " ").trim().slice(0, 50);

/** The Etsy description, for TikTok: no Etsy menu words, no shipping promise (TikTok shows its own), plain HTML. */
function description(l) {
  let t = String(l.description || "");
  t = t.replace(/Pick your design in the menu\./g, "Pick your design from the options.");
  t = t.replace(/\n*SHIPPING\n[^\n]*(\n|$)/, "\n");
  t = t.replace(/ships in 1 to 2 business days with USPS tracking/gi, "ships in 1 to 2 business days with tracking");
  t = t.replace(/Questions\? Send us a message\./, "Questions? Send us a message on TikTok.");
  const esc = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  return t.split(/\n{2,}/).map((block) => {
    const lines = block.split("\n").map((x) => x.trim()).filter(Boolean);
    if (!lines.length) return "";
    if (/^[A-Z][A-Z ,&']+$/.test(lines[0]) && lines.length > 1) return `<p><strong>${esc(lines[0])}</strong></p>` + lines.slice(1).map((x) => `<p>${esc(x)}</p>`).join("");
    return lines.map((x) => `<p>${esc(x)}</p>`).join("");
  }).join("");
}

/* ---------- photos ---------- */
let fetchBytes = async (url) => {
  const res = await globalThis.fetch(url);
  if (!res.ok) fail("unavailable", `A photo didn't load (${url.replace(siteUrl(), "")}).`);
  return Buffer.from(await res.arrayBuffer());
};
let shape = async (buf, square) => {
  const sharp = require("sharp");
  if (!square) return sharp(buf).flatten({ background: "#ffffff" }).jpeg({ quality: 90 }).toBuffer();
  const S = 1600;
  const bg = await sharp(buf).resize(S, S, { fit: "cover" }).blur(40).modulate({ brightness: 0.92 }).toBuffer();
  const fg = await sharp(buf).resize(S, S, { fit: "inside" }).toBuffer();
  return sharp(bg).composite([{ input: fg, gravity: "center" }]).jpeg({ quality: 86 }).toBuffer();
};
/** Tests swap the photo download and the resizing. */
function setPhotoTools(fetchFn, shapeFn) { if (fetchFn) fetchBytes = fetchFn; if (shapeFn) shape = shapeFn; }

async function upload(buf, name, useCase) {
  for (let attempt = 1; ; attempt++) {
    const fd = new FormData();
    fd.append("data", new Blob([buf], { type: "image/jpeg" }), name);
    fd.append("use_case", useCase);
    try {
      const d = await T().call("POST", "/product/202309/images/upload", { form: fd, shop: false });
      if (!d.uri) fail("unavailable", "TikTok: the photo upload gave no picture id.");
      return d.uri;
    } catch (err) {
      if (attempt >= 3) throw err;
      await new Promise((r) => setTimeout(r, 1500 * attempt));
    }
  }
}

const etsyImg = (l, n) => {
  const v = Math.max(Number(require("./etsy-listings.json").imagesVersion || 1), Number(l.imagesVersion || 0));
  return `${siteUrl()}/etsy/img/${l.id}/${n}.jpg?v=${v}`;
};
const artImg = (slug) => `${siteUrl()}/assets/art/${slug}.webp`;

/* ---------- the product ---------- */
async function warehouseId() {
  const a = (await T().readAuth()) || {};
  if (a.warehouseId) return a.warehouseId;
  const list = (await T().call("GET", "/logistics/202309/warehouses")).warehouses || [];
  const w = list.find((x) => x.type === "SALES_WAREHOUSE" && x.is_default) || list.find((x) => x.type === "SALES_WAREHOUSE");
  if (!w) fail("failed-precondition", "TikTok Shop has no sales warehouse yet. Add the shop's address in Seller Center › Logistics.");
  await col().doc("auth").set({ warehouseId: w.id }, { merge: true });
  return w.id;
}

function body(l, mainUris, skuUris, wh) {
  const v = l.variations[0];
  return {
    title: String(l.title).slice(0, 255),
    description: description(l),
    category_id: TIKTOK.category,
    category_version: "v2",
    main_images: mainUris.map((uri) => ({ uri })),
    package_weight: TIKTOK.weight,
    package_dimensions: TIKTOK.dims,
    product_attributes: ATTRS.map(([id, value]) => ({ id, values: [{ id: value }] })),
    is_cod_allowed: false,
    skus: v.options.map((o, i) => ({
      seller_sku: `${l.id}-${i + 1}`.slice(0, 50),
      sales_attributes: [{ name: "Design", value_name: optionName(o), ...(skuUris[i] ? { sku_img: { uri: skuUris[i] } } : {}) }],
      price: { amount: TIKTOK.price.toFixed(2), currency: "USD" },
      inventory: [{ warehouse_id: wh, quantity: TIKTOK.stock }],
    })),
  };
}

/** Puts one collection on TikTok (photos up, then the product). Done once; tiktok/products remembers it. */
async function publish(id, { draft = false } = {}) {
  const l = LISTINGS().find((x) => x.id === id);
  if (!l) fail("invalid-argument", "Unknown collection.");
  const done = ((await col().doc("products").get()).data() || {})[l.id];
  if (done && done.productId) return { product: { id: l.id, ...done }, skipped: true };
  const wh = await warehouseId();
  const main = [];
  for (let n = 1; n <= Math.min(9, l.images); n++) main.push(await upload(await shape(await fetchBytes(etsyImg(l, n)), true), `${l.id}-${n}.jpg`, "MAIN_IMAGE"));
  const skuUris = [];
  for (const slug of l.designs || []) skuUris.push(await upload(await shape(await fetchBytes(artImg(slug)), false), `${slug.replace(/\//g, "-")}.jpg`, "ATTRIBUTE_IMAGE"));
  if (skuUris.length !== l.variations[0].options.length) skuUris.length = 0;   // all or none (TikTok's rule)
  const d = await T().call("POST", "/product/202309/products", { json: { ...body(l, main, skuUris, wh), ...(draft ? { save_mode: "AS_DRAFT" } : {}) } });
  const skus = {};
  (d.skus || []).forEach((s) => { if (s.seller_sku) skus[s.seller_sku] = String(s.id); });
  const row = { productId: String(d.product_id), skus, state: draft ? "draft" : "pending", price: TIKTOK.price, at: nowIso(), error: "" };
  await col().doc("products").set({ [l.id]: row }, { merge: true });
  return { product: { id: l.id, ...row } };
}

/** TikTok reviews each new product: asks it where each one is now (PENDING, ACTIVATE, FAILED…). */
async function refresh() {
  const done = (await col().doc("products").get()).data() || {};
  for (const [id, row] of Object.entries(done)) {
    if (!row || !row.productId) continue;
    try {
      const p = await T().call("GET", `/product/202309/products/${row.productId}`);
      const st = String(p.status || "").toUpperCase();
      const state = st === "ACTIVATE" ? "active" : st === "PENDING" ? "pending" : st === "FAILED" ? "failed" : st.toLowerCase() || row.state;
      const reason = ((p.audit_failed_reasons || [])[0] || {});
      await col().doc("products").set({ [id]: { ...row, state, error: state === "failed" ? String((reason.reasons || []).join("; ") || "TikTok didn't approve it.").slice(0, 300) : "", checkedAt: nowIso() } }, { merge: true });
    } catch (e) { /* the next check tries again */ }
  }
}

async function status() {
  const done = (await col().doc("products").get()).data() || {};
  return LISTINGS().map((l) => ({ id: l.id, name: l.name, section: l.section, designs: l.variations[0].options.length, ...(done[l.id] || { state: "" }) }));
}

module.exports = { publish, refresh, status, setPhotoTools, _internal: { body, description, optionName, TIKTOK, ATTRS } };
