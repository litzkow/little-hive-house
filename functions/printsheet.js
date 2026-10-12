"use strict";
/* Print-ready PDF for a paid order, made on the server so the owners never have to run anything on a computer:
   US Letter at 300 dpi, 12 magnets per page (3 x 4), every tile 2.5 in (the 2 in face plus the paper that wraps the
   edge), crop marks, a small header, then a packing slip page. A port of tools/print_sheet.py (layout, frames,
   captions, photo repeats) to Node: `sharp` rasterises (photos, the frame SVGs through librsvg, WebP designs) and
   `pdfkit` assembles the PDF. Both are required lazily, so this module loads and its layout math is unit-tested
   without node_modules.

   Tile sources
     design  -> ${SITE_URL}/assets/art/<collection>/<slug>.webp (600 px) upsampled to 750 px (lanczos3)
     photo   -> the customer's file in the Storage bucket (uploads/<uid>/<packId>/<n>.<ext>), EXIF-rotated,
                centre-cropped into the frame's window, the frame SVG (${SITE_URL}/assets/frames/<id>.svg) on top,
                then the caption drawn exactly like tools/frames.py caption_svg (fontmetrics.js)
     package / custom -> no artwork: listed on the packing slip only
   A pack with fewer photos than magnets repeats them in order (as promised on the site); qty multiplies everything.

   The PDF is saved at orders/<orderId>/print-sheet.pdf (private: admins get a short-lived URL from adminPrintSheet)
   and the order gets printSheet: {path, pages, sheets, tiles, bytes, at, warnings}. */

const fs = require("fs");
const os = require("os");
const path = require("path");
const crypto = require("crypto");
const { siteUrl, nowIso, AppError } = require("./config");
const deps = require("./deps");
const FM = require("./fontmetrics");

/* ---------- geometry ---------- */
const DPI = 300;
const COLS = 3, ROWS = 4, PER_PAGE = COLS * ROWS;
const TILE_IN = 2.5;
const TILE_PX = TILE_IN * DPI;                       // 750
const TILE_PT = TILE_IN * 72;                        // 180
const PAGE_PT = { w: 8.5 * 72, h: 11 * 72 };         // 612 x 792
const MARGIN_X = (PAGE_PT.w - COLS * TILE_PT) / 2;   // 36
const MARGIN_Y = (PAGE_PT.h - ROWS * TILE_PT) / 2;   // 36
const MARK_GAP = 15 / DPI * 72;                      // 3.6 pt from the grid, like print_sheet.py (15 px)
const MARK_LEN = 45 / DPI * 72;                      // 10.8 pt long (60 - 15 px)
const SVG_UNITS = 600;                               // the frames' coordinate system
const SCALE = TILE_PX / SVG_UNITS;                   // 1.25 px per unit
const MAX_TILES = 600;                               // 50 sheets: more than any pack x qty the shop sells
const JPEG = { quality: 92, chromaSubsampling: "4:4:4" };
const URL_TTL_MS = 60 * 60 * 1000;
const CONCURRENCY = 4;

const ALIASES = { classic: "white", polaroid: "instant", honey: "honeycomb", scallop: "lace", autumn: "fall", starry: "baby" };
const NONE_FRAME = { id: "none", name: "No border", window: [0, 0, 600, 600], shape: "rect", caption: null };

const toInt = (v, d = 0) => (Number.isFinite(Number(v)) ? Math.max(0, Math.floor(Number(v))) : d);
const frameId = (id) => { const k = String(id || "none").trim(); return ALIASES[k] || k || "none"; };

/** Number of sheet pages for n tiles. */
function pageCount(n) { return n > 0 ? Math.ceil(n / PER_PAGE) : 0; }

/** The 12 tile slots of a sheet: {i, col, row, x, y} in points (unit "pt") or pixels at 300 dpi (unit "px"). */
function tilePositions(unit = "pt") {
  const k = unit === "px" ? DPI / 72 : 1;
  const out = [];
  for (let i = 0; i < PER_PAGE; i++) {
    const col = i % COLS, row = Math.floor(i / COLS);
    const r6 = (v) => Math.round(v * 1e6) / 1e6;
    out.push({ i, col, row, x: r6((MARGIN_X + col * TILE_PT) * k), y: r6((MARGIN_Y + row * TILE_PT) * k), size: r6(TILE_PT * k) });
  }
  return out;
}

/** Crop marks on the outer grid lines, as line segments in points: [{x1, y1, x2, y2}]. */
function cropMarks() {
  const segs = [];
  const top = MARGIN_Y, bottom = MARGIN_Y + ROWS * TILE_PT, left = MARGIN_X, right = MARGIN_X + COLS * TILE_PT;
  for (let c = 0; c <= COLS; c++) {
    const x = MARGIN_X + c * TILE_PT;
    segs.push({ x1: x, y1: top - MARK_GAP - MARK_LEN, x2: x, y2: top - MARK_GAP });
    segs.push({ x1: x, y1: bottom + MARK_GAP, x2: x, y2: bottom + MARK_GAP + MARK_LEN });
  }
  for (let r = 0; r <= ROWS; r++) {
    const y = MARGIN_Y + r * TILE_PT;
    segs.push({ x1: left - MARK_GAP - MARK_LEN, y1: y, x2: left - MARK_GAP, y2: y });
    segs.push({ x1: right + MARK_GAP, y1: y, x2: right + MARK_GAP + MARK_LEN, y2: y });
  }
  return segs;
}

/** Which photo (0-based) goes on each of `count` magnets when the pack has `available` photos: they repeat in order. */
function fillIndexes(count, available) {
  if (!available || count <= 0) return [];
  const out = [];
  for (let i = 0; i < count; i++) out.push(i % available);
  return out;
}

/** The photo's window inside a 750 px tile, in whole pixels: {x, y, w, h}. */
function windowPx(frame) {
  const [x, y, w, h] = (frame && frame.window) || NONE_FRAME.window;
  const x0 = Math.round(x * SCALE), y0 = Math.round(y * SCALE);
  return { x: x0, y: y0, w: Math.max(1, Math.round((x + w) * SCALE) - x0), h: Math.max(1, Math.round((y + h) * SCALE) - y0) };
}

/**
 * Pure: what to print for an order. {tiles:[{kind:"design", id, collection, slug, title, key} |
 * {kind:"photo", pack, item, n, path, frame, caption, key}], sheets, skipped:[{kind, title, qty, size}], truncated}.
 * `key` is the same for identical tiles, so each unique artwork is rendered and embedded once.
 */
function planTiles(order) {
  const tiles = [], skipped = [];
  let pack = 0;
  (order && Array.isArray(order.items) ? order.items : []).forEach((it, index) => {
    if (!it) return;
    const qty = Math.max(1, toInt(it.qty, 1) || 1);
    if (it.kind === "design" && it.id) {
      const id = String(it.id);
      const slug = id.split("/").pop();
      const collection = String(it.collection || id.split("/")[0] || "");
      for (let q = 0; q < qty; q++) tiles.push({ kind: "design", id, collection, slug, title: it.title || id, key: `design:${id}` });
    } else if (it.kind === "photos") {
      pack += 1;
      const photos = (Array.isArray(it.photos) ? it.photos : []).filter((p) => p && typeof p.path === "string" && p.path);
      const size = (toInt(it.packSize) * qty) || photos.length;
      if (!photos.length) { skipped.push({ kind: "photos", title: it.title || `Photo magnets (${it.packSize || "?"})`, qty, size, reason: "no photos" }); return; }
      fillIndexes(size, photos.length).forEach((j) => {
        const p = photos[j];
        const frame = frameId(p.frame), caption = String(p.caption || "").trim();
        tiles.push({ kind: "photo", pack, item: index, n: j + 1, path: p.path, frame, caption, key: `photo:${p.path}|${frame}|${caption}` });
      });
    } else if (it.kind === "package") {
      skipped.push({ kind: "package", title: it.title || it.id || "Package", qty, size: toInt(it.size) * qty });
    } else if (it.kind === "custom") {
      skipped.push({ kind: "custom", title: it.title || "Custom order", qty: 1, size: toInt(it.magnets) });
    }
  });
  const truncated = tiles.length > MAX_TILES;
  const list = truncated ? tiles.slice(0, MAX_TILES) : tiles;
  return { tiles: list, sheets: pageCount(list.length), skipped, truncated, total: tiles.length };
}

/** Which sheet and slot each tile lands on: [{page, slot, ...tile}]. */
function placeTiles(tiles) {
  return tiles.map((t, i) => ({ ...t, page: Math.floor(i / PER_PAGE), slot: i % PER_PAGE }));
}

function fileName(order) {
  return `${String((order && order.number) || "order").replace(/[^\w-]+/g, "-")}-print-sheet.pdf`;
}
function storagePath(orderId) { return `orders/${orderId}/print-sheet.pdf`; }

/* ---------- packing slip text (pure) ---------- */
function addressLines(sh) {
  sh = sh || {};
  const a = sh.address || {};
  const cityLine = [a.city, [a.state, a.postal_code].filter(Boolean).join(" ")].filter(Boolean).join(", ");
  return [sh.name, a.line1, a.line2, cityLine, a.country && a.country !== "US" ? a.country : ""].map((s) => String(s || "").trim()).filter(Boolean);
}

function magnetCount(order) {
  return (order.items || []).reduce((n, it) => {
    if (!it) return n;
    const qty = Math.max(1, toInt(it.qty, 1) || 1);
    if (it.kind === "design") return n + qty;
    if (it.kind === "photos") return n + (toInt(it.packSize) * qty || (it.photos || []).length);
    if (it.kind === "package") return n + toInt(it.size) * qty;
    if (it.kind === "custom") return n + toInt(it.magnets);
    return n;
  }, 0);
}

/** Rows for the slip: [{qty, title, sub, lines:[...]}], with a frames map {id -> frame} for the names. */
function slipRows(order, frames = {}) {
  const frameOf = (id) => frames[frameId(id)] || (frameId(id) === "none" ? NONE_FRAME : null);
  return (order.items || []).filter(Boolean).map((it) => {
    const qty = Math.max(1, toInt(it.qty, 1) || 1);
    if (it.kind === "design") return { qty, title: it.title || it.id || "Design", sub: `${titleCase(it.collection || String(it.id || "").split("/")[0])} · 2 × 2 in magnet`, lines: [] };
    if (it.kind === "photos") {
      const photos = (it.photos || []).filter(Boolean);
      const size = toInt(it.packSize) * qty || photos.length;
      const lines = photos.map((p, j) => {
        const f = frameOf(p.frame);
        const cap = FM.captionText(f || NONE_FRAME, p.caption);
        const rep = photos.length && size > photos.length ? Math.floor(size / photos.length) + (j < size % photos.length ? 1 : 0) : 1;
        return `${j + 1}. ${f ? f.name : frameId(p.frame)}${cap ? ` · “${cap}”` : ""}${rep > 1 ? ` ×${rep}` : ""}`;
      });
      return { qty, title: `Photo magnets, ${toInt(it.packSize) || photos.length}-pack`, sub: `${size} magnets${photos.length && size > photos.length ? ` from ${photos.length} photos (they repeat in order)` : ""}`, lines };
    }
    if (it.kind === "package") return { qty, title: it.title || it.id || "Package", sub: `${toInt(it.size)} custom magnets · artwork by email`, lines: [] };
    return { qty: 1, title: it.title || "Custom order", sub: "Made to order", lines: [] };
  });
}
function titleCase(s) { return String(s || "").split(/[-_\s]+/).filter(Boolean).map((w) => w[0].toUpperCase() + w.slice(1)).join(" "); }

function fmtDate(iso) {
  const t = Date.parse(iso || "");
  const d = Number.isFinite(t) ? new Date(t) : new Date();
  try { return d.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric", timeZone: "America/New_York" }); } catch (e) { return d.toISOString().slice(0, 10); }
}

/* ---------- fonts for librsvg (sharp) ---------- */
let fontconfigReady = false;
/** Points fontconfig at ./fonts (a filled-in copy of fonts/fonts.conf in /tmp). Must run before sharp is loaded. */
function ensureFontconfig() {
  if (fontconfigReady) return;
  fontconfigReady = true;
  try {
    const dir = path.join(os.tmpdir(), "lhh-fontconfig");
    fs.mkdirSync(path.join(dir, "cache"), { recursive: true });
    const tpl = fs.readFileSync(path.join(FM.FONTS_DIR, "fonts.conf"), "utf8");
    const conf = tpl.replace("@FONTS_DIR@", FM.FONTS_DIR).replace("@CACHE_DIR@", path.join(dir, "cache"));
    fs.writeFileSync(path.join(dir, "fonts.conf"), conf);
    process.env.FONTCONFIG_FILE = path.join(dir, "fonts.conf");
    process.env.FONTCONFIG_PATH = dir;
  } catch (err) {
    console.warn("[printsheet] fontconfig setup failed; captions may use a fallback font", err && err.message);
  }
}

let sharpMod = null, pdfkitMod = null;
function loadSharp() {
  if (!sharpMod) { ensureFontconfig(); sharpMod = require("sharp"); sharpMod.cache(false); sharpMod.concurrency(2); }
  return sharpMod;
}
function loadPdfkit() { return pdfkitMod || (pdfkitMod = require("pdfkit")); }

/* ---------- fetching ---------- */
const frameCache = new Map();   // url -> Promise<Buffer|string>
async function fetchBuffer(url, fetchImpl) {
  const res = await (fetchImpl || fetch)(url, { headers: { "User-Agent": "LittleHiveHouse-printsheet/1" } });
  if (!res.ok) throw new Error(`HTTP ${res.status} for ${url}`);
  return Buffer.from(await res.arrayBuffer());
}
function cached(url, fetchImpl) {
  if (!frameCache.has(url)) {
    const p = fetchBuffer(url, fetchImpl).catch((err) => { frameCache.delete(url); throw err; });
    frameCache.set(url, p);
  }
  return frameCache.get(url);
}

async function loadFrames(ctx) {
  try {
    const buf = await cached(`${ctx.site}/assets/frames/frames.json`, ctx.fetchImpl);
    const list = JSON.parse(buf.toString("utf8"));
    const map = {};
    (Array.isArray(list) ? list : []).forEach((f) => { if (f && f.id) map[f.id] = f; });
    if (!map.none) map.none = NONE_FRAME;
    return map;
  } catch (err) {
    ctx.warn(`The frame list could not be loaded (${err.message}); photos are printed without their frames.`);
    return { none: NONE_FRAME };
  }
}

/** The inside of a frame SVG (everything between the root tags), or "" for none. */
async function frameInner(id, ctx) {
  if (!id || id === "none") return "";
  const svg = (await cached(`${ctx.site}/assets/frames/${encodeURIComponent(id)}.svg`, ctx.fetchImpl)).toString("utf8");
  return svg.replace(/^[\s\S]*?<svg[^>]*>/, "").replace(/<\/svg>\s*$/, "");
}

/** The overlay drawn over the photo: frame + fitted caption, in a 750 px canvas with the frames' 600-unit viewBox. */
function overlaySvg(inner, captionMarkup) {
  return `<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="${TILE_PX}" height="${TILE_PX}" viewBox="0 0 ${SVG_UNITS} ${SVG_UNITS}">${inner}${captionMarkup}</svg>`;
}

/** A readable stand-in tile when the artwork can't be made, so the sheet still prints and the owner sees why. */
function placeholderSvg(lines) {
  const text = lines.slice(0, 4).map((s, i) => `<text x="300" y="${270 + i * 40}" text-anchor="middle" ${FM.FONTS.jost.attrs} font-size="${i ? 22 : 28}" fill="${i ? "#6B5A48" : "#2B2118"}">${FM.esc(s)}</text>`).join("");
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${TILE_PX}" height="${TILE_PX}" viewBox="0 0 600 600"><rect width="600" height="600" fill="#FFF6E5"/>` +
    `<rect x="60" y="60" width="480" height="480" fill="none" stroke="#E2B252" stroke-width="3" stroke-dasharray="10 8"/>${text}</svg>`;
}

/* ---------- rendering tiles (sharp) ---------- */
async function renderDesign(tile, ctx) {
  const sharp = loadSharp();
  const url = `${ctx.site}/assets/art/${encodeURIComponent(tile.collection)}/${encodeURIComponent(tile.slug)}.webp`;
  try {
    const buf = await fetchBuffer(url, ctx.fetchImpl);
    return await sharp(buf, { failOn: "none" }).resize(TILE_PX, TILE_PX, { fit: "fill", kernel: "lanczos3" })
      .flatten({ background: "#FFFFFF" }).jpeg(JPEG).toBuffer();
  } catch (err) {
    ctx.warn(`Design "${tile.title}" (${tile.id}) could not be fetched from the site: ${err.message}. Its tile is a placeholder.`);
    return sharp(Buffer.from(placeholderSvg(["Missing artwork", tile.title, tile.id]))).jpeg(JPEG).toBuffer();
  }
}

async function renderPhoto(tile, ctx) {
  const sharp = loadSharp();
  const frame = ctx.frames[tile.frame] || null;
  if (!frame) ctx.warn(`Photo ${tile.n} (pack ${tile.pack}): unknown frame "${tile.frame}", printed without a frame.`);
  const f = frame || ctx.frames.none || NONE_FRAME;
  const win = windowPx(f);
  const label = `Photo ${tile.n}${tile.pack > 1 || ctx.packs > 1 ? ` (pack ${tile.pack})` : ""}`;
  let photoLayer = null;
  try {
    const buf = await ctx.readPhoto(tile.path);
    const { data, info } = await sharp(buf, { failOn: "none", limitInputPixels: 120e6, animated: false }).rotate()
      .resize(win.w, win.h, { fit: "cover", position: "centre", kernel: "lanczos3" })
      .flatten({ background: "#FFFFFF" }).removeAlpha().raw().toBuffer({ resolveWithObject: true });
    photoLayer = { input: data, raw: { width: info.width, height: info.height, channels: info.channels }, left: win.x, top: win.y };
  } catch (err) {
    ctx.warn(`${label} could not be read (${err.message}). Its tile is a placeholder: download the photo from the admin and print it by hand.`);
    return sharp(Buffer.from(placeholderSvg([`${label} could not be read`, "Download it from the admin", "and print it by hand", path.basename(tile.path)]))).jpeg(JPEG).toBuffer();
  }
  const layers = [photoLayer];
  const captionMarkup = FM.captionSvg(f, tile.caption);
  let inner = "";
  if (f.id !== "none") {
    try { inner = await frameInner(f.id, ctx); } catch (err) { ctx.warn(`${label}: the "${f.name || f.id}" frame could not be loaded (${err.message}); printed without it.`); }
  }
  if (inner || captionMarkup) layers.push({ input: Buffer.from(overlaySvg(inner, captionMarkup)), left: 0, top: 0 });
  return sharp({ create: { width: TILE_PX, height: TILE_PX, channels: 3, background: "#FFFFFF" } }).composite(layers).jpeg(JPEG).toBuffer();
}

async function pool(items, n, fn) {
  let i = 0;
  const workers = Array.from({ length: Math.min(n, items.length) }, async () => {
    while (i < items.length) { const k = i++; await fn(items[k], k); }
  });
  await Promise.all(workers);
}

/* ---------- the PDF (pdfkit) ---------- */
function registerFonts(doc) {
  const fonts = {};
  const tryFont = (name, key) => { try { fs.accessSync(FM.fontFile(key)); doc.registerFont(name, FM.fontFile(key)); fonts[name] = name; } catch (e) { fonts[name] = null; } };
  tryFont("Body", "jost");
  tryFont("Head", "dms");
  tryFont("Caps", "jos");
  return { body: fonts.Body || "Helvetica", head: fonts.Head || "Helvetica-Bold", caps: fonts.Caps || "Helvetica-Bold" };
}

function drawSheet(doc, F, { order, page, sheets, placed, images, date }) {
  doc.addPage({ size: "LETTER", margin: 0 });
  const num = order.number || "";
  const left = `Little Hive House · Order ${num}${order.name ? ` · ${String(order.name).slice(0, 40)}` : ""}`;
  const right = `Sheet ${page + 1} of ${sheets} · ${date} · print at 100% (actual size) and cut on the marks`;
  doc.font(F.body).fontSize(7.5).fillColor("#2B2118");
  doc.text(left, MARGIN_X, 11, { width: 230, lineBreak: false, ellipsis: true });
  doc.text(right, 272, 11, { width: PAGE_PT.w - MARGIN_X - 272, align: "right", lineBreak: false });
  const slots = tilePositions("pt");
  for (const t of placed) {
    const img = images.get(t.key);
    const s = slots[t.slot];
    if (img) doc.image(img, s.x, s.y, { width: TILE_PT, height: TILE_PT });
  }
  doc.lineWidth(0.5).strokeColor("#000000");
  for (const m of cropMarks()) doc.moveTo(m.x1, m.y1).lineTo(m.x2, m.y2);
  doc.stroke();
  doc.font(F.body).fontSize(6.5).fillColor("#8A7A66");
  doc.text(`${placed.length} of ${PER_PAGE} tiles · each tile ${TILE_IN} in = the 2 in magnet face plus the edge wrap`, MARGIN_X, PAGE_PT.h - 22, { width: PAGE_PT.w - 2 * MARGIN_X, align: "center", lineBreak: false });
}

function drawNotesPage(doc, F, warnings) {
  doc.addPage({ size: "LETTER", margins: { top: 54, bottom: 54, left: 54, right: 54 } });
  doc.font(F.head).fontSize(22).fillColor("#2B2118").text("Before you print");
  doc.moveDown(0.3);
  doc.font(F.body).fontSize(11).fillColor("#6B5A48").text("These things need a look. This page is for you, not for the parcel.");
  doc.moveDown(0.8);
  doc.font(F.body).fontSize(11).fillColor("#2B2118");
  warnings.forEach((w) => { doc.text(`•  ${w}`, { indent: 0, paragraphGap: 6 }); });
}

function drawSlip(doc, F, { order, frames, skipped, date }) {
  const M = 54, W = PAGE_PT.w - 2 * M;
  doc.addPage({ size: "LETTER", margins: { top: M, bottom: M, left: M, right: M } });
  const num = order.number || "";
  doc.font(F.head).fontSize(26).fillColor("#2B2118").text("Packing slip", M, M, { width: W / 2, lineBreak: false });
  doc.font(F.body).fontSize(11).fillColor("#2B2118").text(`Order ${num}`, M + W / 2, M + 6, { width: W / 2, align: "right", lineBreak: false });
  doc.fontSize(10).fillColor("#6B5A48").text(date, M + W / 2, M + 22, { width: W / 2, align: "right", lineBreak: false });
  doc.fontSize(10).fillColor("#6B5A48").text("Little Hive House · Handmade fridge magnets · littlehivehouse.com", M, M + 34, { width: W, lineBreak: false });
  let y = M + 56;
  doc.moveTo(M, y).lineTo(M + W, y).lineWidth(1).strokeColor("#F2A81D").stroke();
  y += 18;
  // ship to + questions
  const colW = W / 2 - 10;
  doc.font(F.caps).fontSize(8.5).fillColor("#8A7A66").text("SHIP TO", M, y, { width: colW, characterSpacing: 1.2 });
  doc.text("QUESTIONS?", M + W / 2 + 10, y, { width: colW, characterSpacing: 1.2 });
  y += 14;
  const lines = addressLines(order.shipping);
  doc.font(F.body).fontSize(11.5).fillColor("#2B2118");
  const addrText = lines.length ? lines.join("\n") : "(no address on the order)";
  const addrH = doc.heightOfString(addrText, { width: colW });
  doc.text(addrText, M, y, { width: colW });
  doc.fontSize(10.5).text("support@littlehivehouse.com\nReply to your order email any time.", M + W / 2 + 10, y, { width: colW });
  y += Math.max(addrH, 30) + 22;
  // items
  doc.font(F.caps).fontSize(8.5).fillColor("#8A7A66").text("QTY", M, y, { width: 40, characterSpacing: 1.2 });
  doc.text("ITEM", M + 48, y, { width: W - 48, characterSpacing: 1.2 });
  y += 14;
  doc.moveTo(M, y).lineTo(M + W, y).lineWidth(0.6).strokeColor("#E8DCC8").stroke();
  y += 8;
  const rows = slipRows(order, frames);
  for (const r of rows) {
    if (y > PAGE_PT.h - M - 80) { doc.addPage({ size: "LETTER", margins: { top: M, bottom: M, left: M, right: M } }); y = M; }
    doc.rect(M + 2, y + 2, 9, 9).lineWidth(0.8).strokeColor("#B8A890").stroke();   // tick box
    doc.font(F.body).fontSize(11.5).fillColor("#2B2118").text(String(r.qty), M + 18, y, { width: 26, lineBreak: false });
    doc.text(r.title, M + 48, y, { width: W - 48 });
    y = doc.y;
    doc.fontSize(9.5).fillColor("#6B5A48").text(r.sub, M + 48, y, { width: W - 48 });
    y = doc.y + 2;
    for (const l of r.lines) {
      if (y > PAGE_PT.h - M - 40) { doc.addPage({ size: "LETTER", margins: { top: M, bottom: M, left: M, right: M } }); y = M; }
      doc.fontSize(9.5).fillColor("#2B2118").text(l, M + 60, y, { width: W - 60 });
      y = doc.y + 1;
    }
    y += 8;
    doc.moveTo(M, y).lineTo(M + W, y).lineWidth(0.4).strokeColor("#EFE6D6").stroke();
    y += 8;
  }
  doc.font(F.body).fontSize(10.5).fillColor("#2B2118").text(`${plural(magnetCount(order), "magnet")} in this order.`, M, y, { width: W });
  y = doc.y + 10;
  const special = skipped.filter((s) => s.kind === "package" || s.kind === "custom");
  if (special.length) {
    doc.fontSize(9.5).fillColor("#6B5A48").text(`Not on the print sheets (artwork made by hand): ${special.map((s) => `${s.title}${s.size ? ` (${s.size} magnets)` : ""}`).join(", ")}.`, M, y, { width: W });
    y = doc.y + 10;
  }
  if (order.giftMessage) {
    const msg = String(order.giftMessage).trim();
    doc.font(F.body).fontSize(12);
    const h = doc.heightOfString(msg, { width: W - 40 }) + 40;
    if (y + h > PAGE_PT.h - M) { doc.addPage({ size: "LETTER", margins: { top: M, bottom: M, left: M, right: M } }); y = M; }
    doc.roundedRect(M, y, W, h, 8).fillColor("#FFF6E5").fill();
    doc.font(F.caps).fontSize(8.5).fillColor("#8A7A66").text("GIFT MESSAGE", M + 20, y + 12, { width: W - 40, characterSpacing: 1.2 });
    doc.font(F.body).fontSize(12).fillColor("#2B2118").text(msg, M + 20, y + 26, { width: W - 40 });
    y += h + 12;
  }
  if (order.notes) {
    doc.font(F.caps).fontSize(8.5).fillColor("#8A7A66").text("NOTE FROM THE CUSTOMER", M, y, { width: W, characterSpacing: 1.2 });
    y += 13;
    doc.font(F.body).fontSize(10.5).fillColor("#2B2118").text(String(order.notes).trim(), M, y, { width: W });
    y = doc.y + 12;
  }
  if (y > PAGE_PT.h - M - 50) { doc.addPage({ size: "LETTER", margins: { top: M, bottom: M, left: M, right: M } }); y = M; }
  doc.moveTo(M, y).lineTo(M + W, y).lineWidth(1).strokeColor("#F2A81D").stroke();
  y += 14;
  doc.font(F.head).fontSize(14).fillColor("#2B2118").text("Thank you for shopping small!", M, y, { width: W });
  doc.font(F.body).fontSize(10.5).fillColor("#6B5A48").text("Made by hand with love by Karina & Thiago. Tag us when your fridge looks sweet.", M, doc.y + 2, { width: W });
}

function plural(n, word) { return `${n} ${word}${n === 1 ? "" : "s"}`; }

async function assemblePdf({ order, plan, images, warnings, frames }) {
  const PDFDocument = loadPdfkit();
  const doc = new PDFDocument({ size: "LETTER", margin: 0, autoFirstPage: false, pdfVersion: "1.5", compress: true,
    info: { Title: `Print sheet · Order ${order.number || ""}`, Author: "Little Hive House", Subject: "Fridge magnets, 12 per sheet, 2.5 in tiles at 300 dpi" } });
  const chunks = [];
  const done = new Promise((resolve, reject) => {
    doc.on("data", (c) => chunks.push(c));
    doc.on("end", () => resolve(Buffer.concat(chunks)));
    doc.on("error", reject);
  });
  let pages = 0;
  doc.on("pageAdded", () => { pages++; });     // counts the slip's overflow pages too
  const F = registerFonts(doc);
  const date = fmtDate(order.paidAt || order.createdAt);
  // embed each unique artwork once (openImage), then place it as many times as needed
  const embedded = new Map();
  for (const [key, jpeg] of images) { try { embedded.set(key, doc.openImage(jpeg)); } catch (e) { warnings.push(`A tile could not be embedded (${e.message}).`); } }
  const placed = placeTiles(plan.tiles);
  for (let p = 0; p < plan.sheets; p++) {
    drawSheet(doc, F, { order, page: p, sheets: plan.sheets, placed: placed.filter((t) => t.page === p), images: embedded, date });
  }
  if (plan.truncated) warnings.push(`This order has ${plan.total} magnets to print but the sheet stops at ${MAX_TILES}. Print the rest from the admin ZIP.`);
  if (warnings.length) drawNotesPage(doc, F, warnings);
  drawSlip(doc, F, { order, frames, skipped: plan.skipped, date });
  doc.end();
  const pdf = await done;
  return { pdf, pages };
}

/* ---------- building ---------- */
function makeContext(order, opts) {
  const warnings = [];
  const ctx = {
    site: siteUrl(), fetchImpl: opts.fetchImpl, warnings,
    warn(msg) { if (warnings.length < 40) warnings.push(msg); console.warn("[printsheet]", msg); },
    packs: (order.items || []).filter((it) => it && it.kind === "photos").length,
    readPhoto: opts.readPhoto || (async (p) => {
      const bucket = opts.bucket || deps.bucket();
      const [buf] = await bucket.file(p).download();
      return buf;
    }),
    frames: null,
  };
  return ctx;
}

/**
 * Renders the whole PDF. Returns {pdf: Buffer, pages, sheets, tiles, warnings}. Options (tests / callers):
 * fetchImpl, bucket, readPhoto(path) -> Buffer.
 */
async function buildPrintSheetDetailed(orderId, order, opts = {}) {
  order = order || {};
  const plan = planTiles(order);
  const ctx = makeContext(order, opts);
  ctx.frames = ctx.packs ? await loadFrames(ctx) : { none: NONE_FRAME };
  const uniq = new Map();
  for (const t of plan.tiles) if (!uniq.has(t.key)) uniq.set(t.key, t);
  const images = new Map();
  await pool(Array.from(uniq.values()), CONCURRENCY, async (t) => {
    images.set(t.key, await (t.kind === "design" ? renderDesign(t, ctx) : renderPhoto(t, ctx)));
  });
  const { pdf, pages } = await assemblePdf({ order, plan, images, warnings: ctx.warnings, frames: ctx.frames });
  return { pdf, pages, sheets: plan.sheets, tiles: plan.tiles.length, warnings: ctx.warnings.slice(0, 10) };
}

/** buildPrintSheet(orderId, order) -> Buffer (the PDF). */
async function buildPrintSheet(orderId, order, opts) { return (await buildPrintSheetDetailed(orderId, order, opts)).pdf; }

let builder = buildPrintSheetDetailed;
/** Tests swap the renderer (sharp/pdfkit are not installed there). */
function setBuilder(fn) { builder = fn || buildPrintSheetDetailed; }

/**
 * Builds the PDF, saves it at orders/<orderId>/print-sheet.pdf and writes order.printSheet. Throws on failure
 * (callers that must not block an order use tryGenerate). Returns {pdf, meta}.
 */
async function generateForOrder(ref, orderId, order, { by = "system" } = {}) {
  const t0 = Date.now();
  const out = await builder(orderId, order);
  const p = storagePath(orderId);
  const bucket = deps.bucket();
  await bucket.file(p).save(out.pdf, {
    contentType: "application/pdf", resumable: false,
    metadata: { cacheControl: "private, max-age=0", contentDisposition: `inline; filename="${fileName(order)}"`, metadata: { orderId, number: order.number || "", by } },
  });
  const meta = { path: p, pages: out.pages, sheets: out.sheets, tiles: out.tiles, bytes: out.pdf.length, at: nowIso(), by, warnings: out.warnings || [], ms: Date.now() - t0 };
  if (ref) await ref.update({ printSheet: meta, updatedAt: nowIso() }).catch((err) => console.warn("[printsheet] could not save printSheet on the order", err && err.message));
  console.log(`[printsheet] ${order.number || orderId}: ${out.tiles} tiles, ${out.pages} pages, ${(out.pdf.length / 1048576).toFixed(1)} MB in ${meta.ms} ms`);
  return { pdf: out.pdf, meta };
}

/** Same, but never throws: null when the sheet could not be made (the order itself is never blocked). */
async function tryGenerate(ref, orderId, order, opts) {
  try { return await generateForOrder(ref, orderId, order, opts); } catch (err) {
    console.error(`[printsheet] could not build the print sheet for ${order && order.number ? order.number : orderId}:`, err && err.message);
    if (ref) await ref.update({ printSheet: { path: null, error: String((err && err.message) || err).slice(0, 300), at: nowIso() } }).catch(() => {});
    return null;
  }
}

/* ---------- download links ---------- */
/** Permanent Firebase download-token URL (same mechanism as the customer photos), the fallback when signing fails. */
async function tokenUrl(bucket, file, p) {
  const [meta] = await file.getMetadata();
  const existing = meta && meta.metadata && meta.metadata.firebaseStorageDownloadTokens;
  const tok = existing ? String(existing).split(",")[0] : crypto.randomUUID();
  if (!existing) await file.setMetadata({ metadata: { firebaseStorageDownloadTokens: tok } });
  return `https://firebasestorage.googleapis.com/v0/b/${bucket.name}/o/${encodeURIComponent(p)}?alt=media&token=${tok}`;
}

/** A short-lived (1 h) signed URL for the PDF; falls back to a download-token URL when the runtime can't sign. */
async function downloadUrl(p, filename) {
  const bucket = deps.bucket();
  const file = bucket.file(p);
  const expiresAt = new Date(Date.now() + URL_TTL_MS).toISOString();
  try {
    if (typeof file.getSignedUrl !== "function") throw new Error("getSignedUrl unavailable");
    const [url] = await file.getSignedUrl({ version: "v4", action: "read", expires: Date.now() + URL_TTL_MS, responseDisposition: `inline; filename="${filename || "print-sheet.pdf"}"` });
    return { url, expiresAt, signed: true };
  } catch (err) {
    console.warn("[printsheet] signed URL failed, using a download token:", err && err.message);
    try { return { url: await tokenUrl(bucket, file, p), expiresAt: null, signed: false }; } catch (e) {
      throw new AppError("unavailable", `The print sheet is saved but a download link could not be made (${e.message}).`);
    }
  }
}

module.exports = {
  DPI, COLS, ROWS, PER_PAGE, TILE_IN, TILE_PX, TILE_PT, PAGE_PT, MARGIN_X, MARGIN_Y, MARK_GAP, MARK_LEN, SCALE, MAX_TILES, ALIASES,
  pageCount, tilePositions, cropMarks, fillIndexes, windowPx, planTiles, placeTiles, frameId, fileName, storagePath,
  addressLines, magnetCount, slipRows, fmtDate, overlaySvg, placeholderSvg, ensureFontconfig,
  buildPrintSheet, buildPrintSheetDetailed, generateForOrder, tryGenerate, setBuilder, downloadUrl, tokenUrl,
  _internal: { renderDesign, renderPhoto, makeContext, loadFrames, assemblePdf },   // for diagnostics / visual checks
};
