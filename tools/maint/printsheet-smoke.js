/* Deploy check: builds both print PDFs with the real sharp + pdfkit (installed in functions/) from the artwork and
   frames in this repo and a made-up photo, so a broken renderer stops the deploy instead of a real order.
   Writes the PDFs to $OUT_DIR (default /tmp/printsheet-smoke). No customer data is used. */
"use strict";
const fs = require("fs");
const path = require("path");
const ROOT = path.join(__dirname, "..", "..");
process.env.SITE_URL = process.env.SITE_URL || "https://littlehivehouse.com";
const P = require(path.join(ROOT, "functions", "printsheet.js"));
const sharp = require(path.join(ROOT, "functions", "node_modules", "sharp"));

const fetchImpl = async (url) => {
  const rel = decodeURIComponent(new URL(url).pathname.replace(/^\//, ""));
  const file = path.join(ROOT, rel);
  if (!fs.existsSync(file)) return { ok: false, status: 404, arrayBuffer: async () => new ArrayBuffer(0) };
  const buf = fs.readFileSync(file);
  return { ok: true, status: 200, arrayBuffer: async () => buf.buffer.slice(buf.byteOffset, buf.byteOffset + buf.byteLength) };
};

(async () => {
  const out = process.env.OUT_DIR || "/tmp/printsheet-smoke";
  fs.mkdirSync(out, { recursive: true });
  // a washed-out "phone photo" with an EXIF rotation, 3000 x 2000
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="3000" height="2000"><defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#f6e7d0"/><stop offset="1" stop-color="#cfe3ee"/></linearGradient></defs>
    <rect width="3000" height="2000" fill="url(#g)"/><circle cx="1500" cy="1000" r="600" fill="#e9b98f"/></svg>`;
  const photo = await sharp(Buffer.from(svg)).jpeg().withMetadata({ orientation: 6 }).toBuffer();
  const designs = ["places/grand-canyon", "places/las-vegas", "places/yosemite"].filter((id) => fs.existsSync(path.join(ROOT, "assets/art", id + ".webp")));
  const order = { number: "LHH-SMOKE", name: "Smoke Test", paidAt: new Date().toISOString(),
    shipping: { name: "Smoke Test", address: { line1: "1 Main St", city: "Atlanta", state: "GA", postal_code: "30301", country: "US" } },
    giftMessage: "Happy birthday!",
    items: designs.map((id) => ({ kind: "design", id, collection: id.split("/")[0], title: id, qty: 1 })).concat([
      { kind: "photos", packSize: 9, qty: 1, photos: [
        { path: "a.jpg", frame: "none", caption: "" }, { path: "b.jpg", frame: "instant", caption: "Summer 2026" },
        { path: "c.jpg", frame: "white", caption: "" }, { path: "d.heic", frame: "wedding", caption: "Ana & Leo" }] }]) };
  const res = await P.buildPrintSheetDetailed("smoke", order, { fetchImpl, cut: 2.4, enhance: true,
    readPhoto: async (p) => { if (p.endsWith(".heic")) throw new Error("not a real photo"); return photo; } });
  const head = (b) => b && b.slice(0, 5).toString();
  if (head(res.pdf) !== "%PDF-" || head(res.slip) !== "%PDF-") throw new Error("the PDFs were not made");
  if (res.sheets !== 2 || res.pages !== 2 || res.tiles !== 12) throw new Error(`unexpected layout: ${JSON.stringify({ sheets: res.sheets, pages: res.pages, tiles: res.tiles })}`);
  if (!res.warnings.some((w) => /HEIC|could not be read/.test(w))) throw new Error("the unreadable photo was not reported");
  fs.writeFileSync(path.join(out, "LHH-SMOKE-magnets.pdf"), res.pdf);
  fs.writeFileSync(path.join(out, "LHH-SMOKE-packing-slip.pdf"), res.slip);
  console.log(`print sheet OK: ${res.tiles} magnets on ${res.sheets} sheets (${(res.pdf.length / 1048576).toFixed(1)} MB), slip ${res.slipPages} page(s); warnings: ${res.warnings.length}`);
})().catch((err) => { console.error("::error title=Print sheet broken::", err && err.stack || err); process.exit(1); });
