"use strict";
/* The print-ready PDF: layout math (a port of tools/print_sheet.py), the caption port (tools/frames.py caption_svg),
   email attachments, and the paid-order path (save to Storage, printSheet on the order, attach to the admin email,
   adminPrintSheet link) with a stand-in renderer, since sharp/pdfkit are not installed here. */
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("fs");
const path = require("path");
const { FakeDB, FakeAuth, FakeBucket, fakeNet } = require("./fakes");
const deps = require("../deps");
const P = require("../printsheet");
const FM = require("../fontmetrics");
const mail = require("../mail");

const FRAMES = Object.fromEntries(JSON.parse(fs.readFileSync(path.join(__dirname, "../../assets/frames/frames.json"), "utf8")).map((f) => [f.id, f]));
const ENV = { STRIPE_SECRET_KEY: "sk_test_x", RESEND_API_KEY: "re_x", ADMIN_EMAILS: "owner@lhh.com", SITE_URL: "https://littlehivehouse.com", MAIL_ADMIN: "support@littlehivehouse.com" };
const ADMIN = { uid: "admin1", token: { admin: true, email: "owner@lhh.com" } };

const fakeBuilder = (extra = {}) => async (orderId, order) => {
  const plan = P.planTiles(order);
  return { pdf: plan.sheets ? Buffer.from(`%PDF-1.5 fake ${orderId} ${plan.tiles.length} tiles`) : null, slip: Buffer.from(`%PDF-1.5 fake slip ${orderId}`),
    pages: plan.sheets, slipPages: 1, sheets: plan.sheets, tiles: plan.tiles.length, warnings: [], ...extra };
};

function setup(builder = fakeBuilder()) {
  Object.assign(process.env, ENV);
  const db = new FakeDB(), auth = new FakeAuth(), bucket = new FakeBucket(), net = fakeNet();
  deps.set({ db, auth, bucket, getDownloadURL: async () => null });
  globalThis.fetch = net.fetch;
  P.setBuilder(builder);
  return { db, auth, bucket, net };
}

const ORDER = {
  number: "LHH-1042", status: "pending", email: "ana@example.com", name: "", uid: null,
  items: [
    { kind: "design", id: "places/new-york", title: "New York", collection: "places", qty: 3, unit: 5 },
    { kind: "design", id: "fall/cozy-season", title: "Cozy Season", collection: "fall", qty: 1, unit: 5 },
    { kind: "photos", packSize: 9, qty: 1, price: 25, notes: "make them bright", photos: [
      { path: "uploads/u1/p1/1.jpg", frame: "polaroid", caption: "Summer 2026" },
      { path: "uploads/u1/p1/2.heic", frame: "none", caption: "" },
      { path: "uploads/u1/p1/3.png", frame: "stamp", caption: "with love" },
      { path: "uploads/u1/p1/4.jpg", frame: "wedding", caption: "Ana & Leo · 06.14.26" },
    ] },
    { kind: "package", id: "teams-12", title: "Teams · 12", size: 12, price: 30, qty: 1 },
  ],
  pricing: { subtotal: 75, bundleDiscount: 3, volumePct: 10, volumeDiscount: 7.2, promo: null, shipping: 0, total: 64.8, currency: "usd" },
  shipping: null, giftMessage: "Happy birthday, Leo!", notes: "Please ship before the 20th.", marketing: false,
  stripe: { sessionId: "cs_test_1", paymentIntent: null, customer: null, fee: null }, fulfillment: null, refunds: [], refundedTotal: 0,
  adminNotes: [], timeline: [{ at: "2026-10-11T12:00:00.000Z", status: "pending", text: "Checkout started." }],
  emails: { confirmation: null, shipped: null, delivered: null, refund: [] }, source: "site", createdAt: "2026-10-11T12:00:00.000Z", paidAt: null,
};
const SESSION = {
  id: "cs_test_1", payment_status: "paid", client_reference_id: null, amount_total: 6480, customer: "cus_1",
  customer_details: { email: "ana@example.com", name: "Ana Souza", address: { country: "US" } },
  shipping_details: { name: "Ana Souza", address: { line1: "1 Main St", line2: "Apt 4", city: "Atlanta", state: "GA", postal_code: "30301", country: "US" } },
  total_details: { amount_discount: 0, amount_tax: 0 }, payment_intent: { id: "pi_1", latest_charge: { balance_transaction: { fee: 218 } } },
};

/* ---------------------------------------------------------------- layout math */
test("geometry: US Letter, 9 pieces of the punch size, the picture a hair over 2 in, centred with white paper around", () => {
  assert.equal(P.DPI, 600);
  assert.equal(P.PER_PAGE, 9);
  assert.equal(P.FACE_PX, 1200);
  assert.deepEqual(P.PAGE_PT, { w: 612, h: 792 });
  const g = P.geometry(2.4, 2.08);
  assert.equal(g.cut, 2.4);
  assert.equal(g.image, 2.08);
  assert.equal(g.artPx, 1248);
  assert.equal(g.gap, 0.35);
  const near = (a, b) => Math.abs(a - b) < 1e-6;
  const pt = P.tilePositions(2.4, 2.08);
  assert.equal(pt.length, 9);
  assert.ok(near(pt[0].size, 172.8) && near(pt[0].art.size, 149.76) && near(pt[0].face.size, 144));
  assert.ok(near(pt[0].x, 612 - (pt[2].x + pt[2].size)), "centred left to right");
  assert.ok(near(pt[1].x - (pt[0].x + pt[0].size), 0.35 * 72));
  // the picture is centred in its piece, with white paper all around (0.16 in each side here)
  assert.ok(near(pt[4].art.x - pt[4].x, 0.16 * 72) && near(pt[4].art.y - pt[4].y, 0.16 * 72));
  for (const t of pt) assert.ok(t.art.x >= 0.25 * 72 && t.art.x + t.art.size <= 612 - 0.25 * 72 && t.art.y >= 36 && t.art.y + t.art.size <= 792 - 36);
  // white between two pictures: the gap plus the white of both pieces
  assert.ok(near(pt[1].art.x - (pt[0].art.x + pt[0].art.size), (0.35 + 2 * 0.16) * 72));
  // defaults and limits
  assert.equal(P.imageSize(undefined), 2.08);
  assert.equal(P.imageSize(2.2), 2.2);
  assert.equal(P.imageSize(5), 2.08);
  assert.equal(P.geometry(2.1, 2.3).image, 2.1, "never bigger than the piece");
});

test("no white edge: the picture keeps its size and its edge is carried out past the cut line, with cut marks in the white", () => {
  const near = (a, b, e = 1e-6) => Math.abs(a - b) < e;
  const g = P.geometry(2.4, 2.08);
  assert.equal(g.artPx, 1248, "the picture itself is not made bigger");
  assert.equal(g.padPx, 138);
  assert.equal(g.fullPx, 1248 + 2 * 138);
  assert.ok(near(g.bleed, 0.07));
  const pt = P.tilePositions(2.4, 2.08);
  for (const t of pt) {
    // the printed square covers the whole piece the punch cuts, plus the bleed on every side
    assert.ok(t.print.x < t.x && t.print.y < t.y && t.print.x + t.print.size > t.x + t.size && t.print.y + t.print.size > t.y + t.size);
    assert.ok(near(t.print.x + t.print.size / 2, t.art.x + t.art.size / 2) && near(t.print.y + t.print.size / 2, t.art.y + t.art.size / 2), "picture centred");
  }
  // there is still white between two printed squares
  assert.ok(pt[1].print.x - (pt[0].print.x + pt[0].print.size) >= 0.1 * 72 - 1e-6);
  assert.ok(pt[3].print.y - (pt[0].print.y + pt[0].print.size) >= 0.1 * 72 - 1e-6);
  // the default punch and the biggest one keep at least 0.1 in of white too
  for (const cut of [2.45, 2.55, 2.1]) {
    const q = P.geometry(cut), t = P.tilePositions(cut);
    assert.ok(q.bleed >= 0 && t[1].print.x - (t[0].print.x + t[0].print.size) >= 0.1 * 72 - 0.2, `white between pieces at ${cut}`);
    assert.ok(t[0].print.x > 0 && t[2].print.x + t[2].print.size < 612);
  }
  // cut marks: on the lines of the cut edges, only in the white (never on a printed square)
  const marks = P.cutMarks(pt, g);
  assert.equal(marks.length, 9 * 8);
  const inside = (x, y) => pt.some((t) => x > t.print.x && x < t.print.x + t.print.size && y > t.print.y && y < t.print.y + t.print.size);
  for (const [x1, y1, x2, y2] of marks) {
    assert.ok(!inside(x1, y1) && !inside(x2, y2) && !inside((x1 + x2) / 2, (y1 + y2) / 2));
    assert.ok(pt.some((t) => near(y1, t.y) || near(y1, t.y + t.size) || near(x1, t.x) || near(x1, t.x + t.size)));
  }
  assert.equal(P.LAYOUT_V, 7);
});

test("continueEdges: the picture untouched in the middle, each side carried on as its own reflection (no seam, no blur)", () => {
  const n = 8, ch = 1, pad = 5;
  const data = Buffer.from(Array.from({ length: n * n }, (_, i) => i % 256));
  const { data: out, size } = P.continueEdges(data, n, ch, pad, 3);
  assert.equal(size, n + 2 * pad);
  const at = (x, y) => out[(y + pad) * size + (x + pad)];
  for (let y = 0; y < n; y++) for (let x = 0; x < n; x++) assert.equal(at(x, y), data[y * n + x], "picture untouched");
  // left of column 0: 0,1,2 then folds back 2,1 (reach 3)
  assert.deepEqual([-1, -2, -3, -4, -5].map((x) => at(x, 2)), [0, 1, 2, 2, 1].map((x) => data[2 * n + x]));
  // right of the last column, and above the top row
  assert.deepEqual([8, 9, 10].map((x) => at(x, 0)), [7, 6, 5].map((x) => data[x]));
  assert.deepEqual([-1, -2].map((y) => at(3, y)), [0, 1].map((y) => data[y * n + 3]));
  // one colour stays exactly that colour
  const flat = P.continueEdges(Buffer.alloc(n * n * 3, 200), n, 3, pad).data;
  assert.ok(flat.every((v) => v === 200));
});

test("the punch size: any measured size from 2.10 to 2.55 in, anything else falls back to 2.45", () => {
  assert.equal(P.cutSize(2.25), 2.25);
  assert.equal(P.cutSize("2.5"), 2.5);
  assert.equal(P.cutSize(3), 2.45);
  assert.equal(P.cutSize(undefined), 2.45);
  const big = P.geometry(2.55), small = P.geometry(2.1);
  assert.ok(big.gap > 0.1 && small.gap === 0.5);
  for (const g of [big, small]) {
    const pt = P.tilePositions(g.cut);
    assert.ok(pt[2].art.x + pt[2].art.size < 612 && pt[0].art.x > 0);
  }
});

test("photo touch-up: overexposed photos are darkened a little, dark ones lifted a little, never too much", () => {
  const mid = P.enhanceParams(118), bright = P.enhanceParams(200), dark = P.enhanceParams(60);
  assert.equal(mid.brightness, 1);
  assert.ok(bright.brightness < 1 && bright.brightness >= 0.84);
  assert.ok(dark.brightness > 1 && dark.brightness <= 1.12);
  assert.equal(P.enhanceParams(255).brightness, 0.84);
  assert.equal(P.enhanceParams(0).brightness, 1.12);
  assert.ok(mid.saturation > 1 && mid.contrast > 1 && mid.offset < 0);
});

test("page count: 9 per sheet", () => {
  assert.deepEqual([0, 1, 8, 9, 10, 18, 19, 50].map(P.pageCount), [0, 1, 1, 1, 2, 2, 3, 6]);
});

test("fill: a pack with fewer photos than magnets repeats them in order (print_sheet.py --order, admin photoPlan)", () => {
  assert.deepEqual(P.fillIndexes(9, 4), [0, 1, 2, 3, 0, 1, 2, 3, 0]);
  assert.deepEqual(P.fillIndexes(4, 4), [0, 1, 2, 3]);
  assert.deepEqual(P.fillIndexes(3, 5), [0, 1, 2], "more photos than magnets: the first ones");
  assert.deepEqual(P.fillIndexes(5, 0), []);
  assert.deepEqual(P.fillIndexes(0, 3), []);
});

test("planTiles: designs x qty, photo packs filled x qty, packages and custom items only on the slip", () => {
  const plan = P.planTiles(ORDER);
  assert.equal(plan.tiles.length, 3 + 1 + 9);
  assert.equal(plan.sheets, 2);
  assert.equal(plan.truncated, false);
  assert.deepEqual(plan.tiles.slice(0, 3).map((t) => t.key), ["design:places/new-york", "design:places/new-york", "design:places/new-york"]);
  assert.deepEqual(plan.tiles[0], { kind: "design", id: "places/new-york", collection: "places", slug: "new-york", title: "New York", key: "design:places/new-york" });
  const photos = plan.tiles.filter((t) => t.kind === "photo");
  assert.deepEqual(photos.map((t) => t.n), [1, 2, 3, 4, 1, 2, 3, 4, 1]);
  assert.equal(photos[0].frame, "instant", "frame aliases are resolved (polaroid -> instant)");
  assert.equal(photos[0].caption, "Summer 2026");
  assert.equal(photos[0].pack, 1);
  assert.equal(photos[4].key, photos[0].key, "repeated photos share a key, so the artwork is rendered once");
  assert.deepEqual(plan.skipped.map((s) => [s.kind, s.size]), [["package", 12]]);
  // placed on pages
  const placed = P.placeTiles(plan.tiles);
  assert.deepEqual([placed[0].page, placed[0].slot, placed[8].page, placed[8].slot, placed[9].page, placed[9].slot], [0, 0, 0, 8, 1, 0]);
});

test("planTiles: qty multiplies photo packs, photos without a file are skipped, a pack with no files is listed as skipped", () => {
  const two = P.planTiles({ items: [{ kind: "photos", packSize: 4, qty: 2, photos: [{ path: "uploads/u/p/1.jpg", frame: "none" }, { path: "", frame: "none" }, { frame: "none" }] }] });
  assert.equal(two.tiles.length, 8);
  assert.ok(two.tiles.every((t) => t.path === "uploads/u/p/1.jpg"));
  const none = P.planTiles({ items: [{ kind: "photos", packSize: 4, photos: [] }, { kind: "custom", title: "Wedding favours", amount: 120, magnets: 40 }] });
  assert.equal(none.tiles.length, 0);
  assert.equal(none.sheets, 0);
  assert.deepEqual(none.skipped.map((s) => s.kind), ["photos", "custom"]);
  assert.deepEqual(P.planTiles(null).tiles, []);
  assert.deepEqual(P.planTiles({ items: [{ kind: "design", id: "x/y", qty: 0 }] }).tiles.length, 1, "qty 0 still prints one");
});

test("planTiles caps at MAX_TILES and says so", () => {
  const plan = P.planTiles({ items: [{ kind: "design", id: "a/b", qty: 700 }] });
  assert.equal(plan.tiles.length, P.MAX_TILES);
  assert.equal(plan.truncated, true);
  assert.equal(plan.total, 700);
});

test("windowPx: the frame window on the 1200 px face (2 px per frame unit), in whole pixels", () => {
  assert.deepEqual(P.windowPx(FRAMES.none), { x: 0, y: 0, w: 1200, h: 1200 });
  assert.deepEqual(P.windowPx(FRAMES.white), { x: 200, y: 200, w: 800, h: 800 });
  const inst = P.windowPx(FRAMES.instant);   // [52, 50, 496, 414]
  assert.deepEqual(inst, { x: 104, y: 100, w: 992, h: 828 });
  const hex = P.windowPx(FRAMES.honeycomb);  // fractional window
  assert.ok(hex.w > 0 && hex.h > 0 && hex.x + hex.w <= 1200 && hex.y + hex.h <= 1200);
});

test("packing slip rows, address lines and the magnet count", () => {
  const order = { ...ORDER, shipping: { name: "Ana Souza", phone: "", address: { line1: "1 Main St", line2: "Apt 4", city: "Atlanta", state: "GA", postal_code: "30301", country: "US" } } };
  assert.deepEqual(P.addressLines(order.shipping), ["Ana Souza", "1 Main St", "Apt 4", "Atlanta, GA 30301"]);
  assert.deepEqual(P.addressLines({ name: "Léa", address: { line1: "10 Rue", city: "Montréal", state: "QC", postal_code: "H2X", country: "CA" } }), ["Léa", "10 Rue", "Montréal, QC H2X", "CA"]);
  assert.deepEqual(P.addressLines(null), []);
  assert.equal(P.magnetCount(order), 3 + 1 + 9 + 12);
  const rows = P.slipRows(order, FRAMES);
  assert.equal(rows.length, 4);
  assert.deepEqual([rows[0].qty, rows[0].title, rows[0].sub], [3, "New York", "Places · 2 × 2 in magnet"]);
  assert.equal(rows[2].title, "Photo magnets, 9-pack");
  assert.match(rows[2].sub, /9 magnets from 4 photos/);
  assert.deepEqual(rows[2].lines, ["1. Instant print · “Summer 2026” ×3", "2. Full photo ×2", "3. Postage stamp · “WITH LOVE” ×2", "4. Wedding · “Ana & Leo · 06.14.26” ×2"]);
  assert.deepEqual([rows[3].qty, rows[3].sub], [1, "12 custom magnets · artwork by email"]);
  assert.equal(P.fileName(order), "LHH-1042-magnets.pdf");
  assert.equal(P.fileName(order, "slip"), "LHH-1042-packing-slip.pdf");
  assert.equal(P.storagePath("abc"), "orders/abc/print-sheet.pdf");
  assert.equal(P.storagePath("abc", "slip"), "orders/abc/packing-slip.pdf");
  assert.equal(P.fmtDate("2026-10-11T12:00:00.000Z"), "Oct 11, 2026");
});

/* ---------------------------------------------------------------- captions with real font metrics */
test("font metrics read from the bundled TTFs match the Python tool (fontTools) to the hundredth", () => {
  assert.equal(FM.measure("Summer 2026", "serif", 46).toFixed(2), "292.01");
  assert.equal(FM.measure("WITH LOVE", "jos", 30, 4).toFixed(2), "211.19");
  for (const k of Object.keys(FM.FONTS)) {
    const m = FM.metrics(k);
    assert.ok(m.unitsPerEm >= 1000, k);
    assert.ok(FM.measure("Hello", k, 40) > 50 && FM.measure("Hello", k, 40) < 200, k);
    assert.ok(FM.measure("Hello", k, 40) < FM.measure("Hello there", k, 40), `${k}: longer is wider`);
  }
  assert.ok(FM.measure("\u{1F41D}", "serif", 40) === 20, "a glyph the font lacks counts half an em, like common.py");
});

test("captionSvg is a faithful port of tools/frames.py caption_svg (same output for the same input)", () => {
  assert.equal(FM.captionSvg(FRAMES.instant, "Summer 2026"),
    '<text x="300" y="540" text-anchor="middle" font-family="Caveat, cursive" font-weight="600" font-size="66" fill="#2E3550" transform="rotate(-1.5 300 540)">Summer 2026</text>');
  // the lettering the customer picked replaces the frame's default
  assert.equal(FM.captionSvg(FRAMES.instant, "Summer 2026", "classic"),
    '<text x="300" y="540" text-anchor="middle" font-family="\'Cormorant Garamond\', Georgia, serif" font-style="italic" font-weight="600" font-size="61" fill="#2E3550" transform="rotate(-1.5 300 540)">Summer 2026</text>');
  assert.equal(FM.captionSvg(FRAMES.instant, "Summer 2026", "modern"),
    '<text x="302.65" y="540" text-anchor="middle" font-family="Jost, sans-serif" font-weight="500" font-size="33" letter-spacing="5.3" fill="#2E3550" transform="rotate(-1.5 300 540)">SUMMER 2026</text>');
  assert.equal(FM.captionSvg(FRAMES.instant, "Summer 2026", "nope"), FM.captionSvg(FRAMES.instant, "Summer 2026"), "an unknown lettering falls back to the default");
  // first-edition frames (hidden from the builder) still draw: upper-cased, cut to the max (20), shrunk to fit
  assert.equal(FRAMES.stamp.hidden, true);
  assert.equal(FM.captionSvg(FRAMES.stamp, "with love and a very long caption here"),
    '<text x="302" y="494" text-anchor="middle" font-family="\'Josefin Sans\', sans-serif" font-weight="700" font-size="19" letter-spacing="4" fill="#FBF5EA">WITH LOVE AND A VERY</text>');
  // the kicker comes first
  assert.equal(FM.captionSvg(FRAMES.postcard, "Lisbon"),
    '<text x="302" y="496" text-anchor="middle" font-family="Jost, sans-serif" font-weight="500" font-size="17" letter-spacing="4" fill="#B4483C">GREETINGS FROM</text>' +
    '<text x="300" y="556" text-anchor="middle" font-family="\'Dancing Script\', cursive" font-weight="600" font-size="57" fill="#22406E">Lisbon</text>');
  assert.equal(FM.captionSvg(FRAMES.sports, "Mia #12"),
    '<text x="303.35" y="548" text-anchor="middle" font-family="Jost, sans-serif" font-weight="500" font-size="42" letter-spacing="6.7" fill="#FFFFFF">MIA #12</text>');
  assert.equal(FM.captionSvg(FRAMES.border, "anything"), "", "frames without a caption draw nothing");
  assert.equal(FM.captionSvg(FRAMES.instant, "   "), "");
  assert.match(FM.captionSvg(FRAMES.wedding, 'Ana & Leo <3 "forever"'), /Ana &amp; Leo &lt;3 &quot;forever&quot;/);
});

test("caption fitting never goes below the frame's minimum size and always fits otherwise", () => {
  for (const f of Object.values(FRAMES).filter((x) => x.caption)) {
    const c = f.caption;
    const long = "W".repeat(c.max || 40);
    const svg = FM.captionSvg(f, long);
    const sizeOf = (markup) => Number(markup.match(/font-size="(\d+)"/g).pop().match(/\d+/)[0]);   // the caption is the last <text>
    const size = sizeOf(svg);
    assert.ok(size >= c.min && size <= c.size, `${f.id}: ${size} within [${c.min}, ${c.size}]`);
    const w = FM.measure(FM.captionText(f, long), c.font, size, c.ls || 0);
    assert.ok(size === c.min || w <= c.w, `${f.id}: fits or is at the minimum`);
    const short = FM.captionSvg(f, "Hi");
    assert.equal(sizeOf(short), c.size, `${f.id}: short captions keep the full size`);
  }
  assert.equal(FM.captionText(FRAMES.stamp, "  hello world, this is long  "), "HELLO WORLD, THIS IS");
});

test("overlay and placeholder SVGs are 1200 px canvases (the face) over the frames' 600-unit viewBox", () => {
  const o = P.overlaySvg("<g id=\"frame\"/>", "<text>cap</text>");
  assert.match(o, /^<svg xmlns="http:\/\/www\.w3\.org\/2000\/svg"[^>]*width="1200" height="1200" viewBox="0 0 600 600">/);
  assert.match(o, /<g id="frame"\/><text>cap<\/text><\/svg>$/);
  const ph = P.placeholderSvg(["Photo 3 could not be read", "a & b"]);
  assert.match(ph, /width="1200" height="1200"/);
  assert.match(ph, /a &amp; b/);
  assert.match(ph, /font-family="Jost/);
});

test("ensureFontconfig points librsvg at functions/fonts through a filled-in fonts.conf in the temp dir", () => {
  P.ensureFontconfig();
  const file = process.env.FONTCONFIG_FILE;
  assert.ok(file && fs.existsSync(file), "fonts.conf written");
  const conf = fs.readFileSync(file, "utf8");
  assert.ok(conf.includes(`<dir>${FM.FONTS_DIR}</dir>`));
  assert.ok(!conf.includes("@FONTS_DIR@") && !conf.includes("@CACHE_DIR@"));
  assert.equal(path.dirname(file), process.env.FONTCONFIG_PATH);
  for (const f of Object.values(FM.FONTS)) assert.ok(fs.existsSync(path.join(FM.FONTS_DIR, f.file)), f.file);
});

/* ---------------------------------------------------------------- email attachments */
test("mail.send attaches files to the Resend payload as base64, skipping anything over the limit", async () => {
  const { net } = setup();
  const pdf = Buffer.from("%PDF-1.5 hello");
  assert.deepEqual(mail.encodeAttachments([{ filename: "LHH-1 print/sheet.pdf", content: pdf, contentType: "application/pdf" }, { filename: "big.pdf", content: Buffer.alloc(mail.MAX_ATTACHMENT_BYTES + 1) }, null, { filename: "empty" }]),
    [{ filename: "LHH-1 print-sheet.pdf", content: pdf.toString("base64"), content_type: "application/pdf" }]);
  assert.deepEqual(mail.encodeAttachments([{ filename: "x.txt", content: Buffer.from("hi").toString("base64") }]), [{ filename: "x.txt", content: "aGk=" }], "base64 strings pass through");
  await mail.send({ to: "support@littlehivehouse.com", kind: "admin_new_order", data: { order: { number: "LHH-9", items: [] } }, attachments: [{ filename: "a.pdf", content: pdf }] });
  assert.equal(net.emails.length, 1);
  assert.deepEqual(net.emails[0].attachments, [{ filename: "a.pdf", content: pdf.toString("base64") }]);
  await mail.send({ to: "ana@example.com", kind: "order_confirmation", data: { order: { number: "LHH-9", items: [] } } });
  assert.equal(net.emails[1].attachments, undefined, "no attachments key when there are none");
});

/* ---------------------------------------------------------------- the paid-order path */
test("a newly paid order gets its PDF in Storage, printSheet on the order and the PDF attached to the admin email", async () => {
  const { db, bucket, net } = setup();
  const checkout = require("../checkout");
  await db.collection("orders").doc("ord1").set(ORDER);
  const res = await checkout.completeCheckout({ ...SESSION, client_reference_id: "ord1" });
  assert.equal(res.newlyPaid, true);
  const o = db.get("orders/ord1");
  assert.equal(o.status, "paid");
  assert.equal(o.printSheet.path, "orders/ord1/print-sheet.pdf");
  assert.equal(o.printSheet.tiles, 13);
  assert.equal(o.printSheet.sheets, 2);
  assert.equal(o.printSheet.pages, 2);
  assert.equal(o.printSheet.slipPath, "orders/ord1/packing-slip.pdf");
  assert.equal(o.printSheet.cut, 2.45, "the default punch size");
  assert.equal(o.printSheet.enhance, true);
  assert.equal(o.printSheet.v, 7);
  assert.equal(o.printSheet.image, 2.08);
  assert.ok(o.printSheet.at && o.printSheet.bytes > 0 && o.printSheet.slipBytes > 0);
  const slip = bucket.files.get("orders/ord1/packing-slip.pdf");
  assert.equal(slip.data.toString(), "%PDF-1.5 fake slip ord1");
  const f = bucket.files.get("orders/ord1/print-sheet.pdf");
  assert.ok(f, "saved in the bucket");
  assert.equal(f.contentType, "application/pdf");
  assert.equal(f.data.toString(), "%PDF-1.5 fake ord1 13 tiles");
  assert.equal(f.metadata.orderId, "ord1");
  assert.deepEqual(net.emails.map((e) => e.to[0]), ["ana@example.com", "support@littlehivehouse.com"]);
  assert.equal(net.emails[0].attachments, undefined, "the customer never gets the print sheet");
  const adminMail = net.emails[1];
  assert.deepEqual(adminMail.attachments, [{ filename: "LHH-1001-magnets.pdf", content: f.data.toString("base64"), content_type: "application/pdf" },
    { filename: "LHH-1001-packing-slip.pdf", content: slip.data.toString("base64"), content_type: "application/pdf" }]);
  assert.match(adminMail.subject, /print sheet attached/);
  assert.match(adminMail.text, /Two PDFs attached\. The magnets \(2 sheets, 9 per sheet\): glossy photo paper/);
  assert.match(adminMail.text, /packing slip: plain paper/);
  assert.match(adminMail.text, /100%/);
  assert.doesNotMatch(adminMail.text, /Download the 4 customer photos/, "no need to download photos by hand any more");
  // paying twice does not rebuild or re-send
  const again = await checkout.completeCheckout({ ...SESSION, client_reference_id: "ord1" });
  assert.equal(again.newlyPaid, false);
  assert.equal(net.emails.length, 2);
});

test("a PDF over the attachment limit is linked instead of attached; a renderer failure never blocks the order", async () => {
  const big = setup(fakeBuilder({ pdf: Buffer.alloc(mail.MAX_ATTACHMENT_BYTES + 10, 1) }));
  const checkout = require("../checkout");
  await big.db.collection("orders").doc("ord2").set(ORDER);
  await checkout.completeCheckout({ ...SESSION, id: "cs_2", client_reference_id: "ord2" });
  assert.equal(big.db.get("orders/ord2").printSheet.path, "orders/ord2/print-sheet.pdf");
  assert.equal(big.net.emails[1].attachments, undefined);
  assert.match(big.net.emails[1].text, /too big to attach/);
  assert.doesNotMatch(big.net.emails[1].subject, /attached/);

  const broken = setup(async () => { throw new Error("sharp exploded"); });
  await broken.db.collection("orders").doc("ord3").set(ORDER);
  const res = await checkout.completeCheckout({ ...SESSION, id: "cs_3", client_reference_id: "ord3" });
  assert.equal(res.newlyPaid, true);
  const o = broken.db.get("orders/ord3");
  assert.equal(o.status, "paid");
  assert.equal(o.number, "LHH-1001");
  assert.equal(o.printSheet.path, null);
  assert.match(o.printSheet.error, /sharp exploded/);
  assert.equal(broken.net.emails.length, 2, "both emails still go out");
  assert.match(broken.net.emails[1].text, /could not be made automatically/);
  assert.ok(!broken.bucket.files.has("orders/ord3/print-sheet.pdf"));
});

test("a paid payment-link (custom) order gets a slip-only PDF", async () => {
  const { db, net } = setup();
  const checkout = require("../checkout");
  const custom = { ...ORDER, number: null, items: [{ kind: "custom", title: "Wedding favours", amount: 120, magnets: 40 }], source: "payment_link",
    stripe: { sessionId: null, paymentIntent: null, customer: null, fee: null, paymentLink: "plink_1", paymentLinkUrl: "https://buy.stripe.com/x" } };
  await db.collection("orders").doc("ord4").set(custom);
  const res = await checkout.completeCheckout({ ...SESSION, id: "cs_4", client_reference_id: null, metadata: {}, payment_link: "plink_1" });
  assert.equal(res.orderId, "ord4");
  const o = db.get("orders/ord4");
  assert.deepEqual([o.printSheet.tiles, o.printSheet.sheets, o.printSheet.pages, o.printSheet.path], [0, 0, 0, null]);
  assert.equal(o.printSheet.slipPath, "orders/ord4/packing-slip.pdf");
  assert.deepEqual(net.emails[1].attachments.map((x) => x.filename), ["LHH-1001-packing-slip.pdf"]);
  assert.match(net.emails[1].text, /Nothing in this order prints on the magnet sheets/);
  const admin = require("../admin");
  await assert.rejects(admin.adminPrintSheet({ orderId: "ord4" }, ADMIN), (e) => e.code === "failed-precondition" && /made by hand/.test(e.message));
  const slip = await admin.adminPrintSheet({ orderId: "ord4", which: "slip" }, ADMIN);
  assert.match(slip.url, /packing-slip\.pdf/);
});

test("adminPrintSheet: admins only, paid orders only, returns a short-lived signed link, rebuilds on demand or when the file is gone", async () => {
  const { db, bucket } = setup();
  const checkout = require("../checkout"), admin = require("../admin");
  await db.collection("orders").doc("ord5").set(ORDER);
  await checkout.completeCheckout({ ...SESSION, id: "cs_5", client_reference_id: "ord5" });
  const first = db.get("orders/ord5").printSheet;

  await assert.rejects(admin.adminPrintSheet({ orderId: "ord5" }, null), (e) => e.code === "unauthenticated");
  await assert.rejects(admin.adminPrintSheet({ orderId: "ord5" }, { uid: "u", token: { email: "x@y.com" } }), (e) => e.code === "permission-denied");
  await assert.rejects(admin.adminPrintSheet({ orderId: "nope" }, ADMIN), (e) => e.code === "not-found");
  await db.collection("orders").doc("pend").set({ ...ORDER, status: "pending" });
  await assert.rejects(admin.adminPrintSheet({ orderId: "pend" }, ADMIN), (e) => e.code === "failed-precondition");

  const r1 = await admin.adminPrintSheet({ orderId: "ord5" }, ADMIN);
  assert.equal(r1.rebuilt, false);
  assert.equal(r1.signed, true);
  assert.match(r1.url, /^https:\/\/storage\.googleapis\.com\/test-bucket\/orders%2Ford5%2Fprint-sheet\.pdf\?X-Goog-Signature=/);
  assert.ok(Date.parse(r1.expiresAt) - Date.now() <= 60 * 60 * 1000 + 5000);
  const signed = bucket.signed[bucket.signed.length - 1];
  assert.equal(signed.opts.action, "read");
  assert.equal(signed.opts.version, "v4");
  assert.match(signed.opts.responseDisposition, /inline; filename="LHH-1001-magnets\.pdf"/);
  assert.equal(r1.printSheet.at, first.at, "no rebuild when the file is there");
  const rs = await admin.adminPrintSheet({ orderId: "ord5", which: "slip" }, ADMIN);
  assert.equal(rs.which, "slip");
  assert.match(rs.url, /orders%2Ford5%2Fpacking-slip\.pdf/);
  assert.equal(rs.rebuilt, false);
  // a PDF from the old 12-per-sheet layout is made again
  await db.collection("orders").doc("ord5").update({ printSheet: { ...first, v: undefined } });
  const old = await admin.adminPrintSheet({ orderId: "ord5" }, ADMIN);
  assert.equal(old.rebuilt, true);
  assert.equal(db.get("orders/ord5").printSheet.v, 7);

  await new Promise((r) => setTimeout(r, 5));
  const r2 = await admin.adminPrintSheet({ orderId: "ord5", rebuild: true }, ADMIN);
  assert.equal(r2.rebuilt, true);
  assert.notEqual(r2.printSheet.at, first.at);
  assert.equal(db.get("orders/ord5").printSheet.by, "owner@lhh.com");

  bucket.files.delete("orders/ord5/print-sheet.pdf");
  const r3 = await admin.adminPrintSheet({ orderId: "ord5" }, ADMIN);
  assert.equal(r3.rebuilt, true, "missing file: made again");
  assert.ok(bucket.files.has("orders/ord5/print-sheet.pdf"));

  // when the runtime can't sign (no IAM signBlob), fall back to a download-token link rather than failing
  bucket.noSigning = true;
  const r4 = await admin.adminPrintSheet({ orderId: "ord5" }, ADMIN);
  assert.equal(r4.signed, false);
  assert.match(r4.url, /^https:\/\/firebasestorage\.googleapis\.com\/v0\/b\/test-bucket\/o\/orders%2Ford5%2Fprint-sheet\.pdf\?alt=media&token=/);
  const r5 = await admin.adminPrintSheet({ orderId: "ord5" }, ADMIN);
  assert.equal(r5.url, r4.url, "the token is kept, not minted again");

  // a renderer failure is a clear error for the admin
  P.setBuilder(async () => { throw new Error("no sharp here"); });
  await assert.rejects(admin.adminPrintSheet({ orderId: "ord5", rebuild: true }, ADMIN), (e) => e.code === "unavailable" && /no sharp here/.test(e.message));
});

test("buildPrintSheet without sharp/pdfkit installed fails cleanly (the real renderer is only loaded on use)", async () => {
  P.setBuilder(null);
  let hasSharp = true;
  try { require.resolve("sharp"); } catch (e) { hasSharp = false; }
  if (hasSharp) return;   // CI with node_modules: covered after deploy
  await assert.rejects(P.buildPrintSheet("x", { items: [{ kind: "design", id: "places/new-york", qty: 1 }] }, { fetchImpl: async () => ({ ok: true, arrayBuffer: async () => new ArrayBuffer(8) }) }),
    (e) => e.code === "MODULE_NOT_FOUND");
});
