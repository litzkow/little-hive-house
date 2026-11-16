"use strict";
/* 15 Nov 2026: what the photo builder shows must be exactly what is seen on the front of the finished magnet. */
const test = require("node:test");
const assert = require("node:assert/strict");
let sharp = null;
try { sharp = require("sharp"); } catch (e) { /* the deploy runner tests without the image library: these run where it is installed */ }
const P = require("../printsheet");

test("geometry: the visible front is kept apart from the printed size and stays inside it", () => {
  const g = P.geometry(2.45, 2.02, 1.9);
  assert.equal(g.visPx, 1140);
  assert.equal(g.artPx, 1212);
  assert.equal(P.geometry(2.45, 2.02).visPx, Math.round(P.VISIBLE_IN * P.DPI));
  assert.equal(P.geometry(2.45, 2.02, 5).visPx, Math.round(P.VISIBLE_IN * P.DPI), "out of range falls back to the default");
  assert.equal(P.geometry(2.45, 1.9, 2.02).visPx, 1140, "never bigger than the printed picture");
  assert.equal(P.visibleSize("1.85"), 1.85);
});

/* a 3000 x 2000 photo: grey, with a red band just inside the chosen square and blue outside it */
async function markedPhoto() {
  const W = 3000, H = 2000, side = 1600, L = 700, T = 200;     // chosen square: x 700..2300, y 200..1800
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}">
    <rect width="${W}" height="${H}" fill="#0000FF"/>
    <rect x="${L}" y="${T}" width="${side}" height="${side}" fill="#FF0000"/>
    <rect x="${L + 40}" y="${T + 40}" width="${side - 80}" height="${side - 80}" fill="#808080"/></svg>`;
  return { buf: await sharp(Buffer.from(svg)).jpeg({ quality: 95 }).toBuffer(), W, H, crop: { x: 1500 / W, y: 1000 / H, z: H / side } };     // z 1.25: zoomed in to the 1600 px square
}
async function px(img, x, y) {
  const { data, info } = await sharp(img).raw().toBuffer({ resolveWithObject: true });
  const i = (y * info.width + x) * info.channels;
  return [data[i], data[i + 1], data[i + 2]];
}
const isRed = (c) => c[0] > 180 && c[1] < 80 && c[2] < 80;
const isBlue = (c) => c[2] > 180 && c[0] < 80 && c[1] < 80;

test("photo with no frame: the chosen part fills the visible front exactly and the real photo carries on over the edge", { skip: !sharp && "no sharp here" }, async () => {
  const ph = await markedPhoto();
  const geo = P.geometry(2.45, 2.02, 1.9);
  // and the picture itself
  const img = await P._renderOne({ path: "p/1.jpg", frame: "none", crop: ph.crop }, { geo, enhance: false, readPhoto: async () => ph.buf });
  const meta = await sharp(img).metadata();
  assert.equal(meta.width, geo.artPx);
  const off = (geo.artPx - geo.visPx) / 2;                       // 36 px of edge on each side
  const mid = Math.round(geo.artPx / 2);
  assert.ok(isRed(await px(img, Math.round(off + 6), mid)), "the red edge of the chosen part starts right at the visible front");
  assert.ok(isRed(await px(img, Math.round(geo.artPx - off - 6), mid)));
  assert.ok(isBlue(await px(img, Math.round(off - 12), mid)), "outside the visible front: the photo's real pixels, not stretched red");
  assert.ok(isBlue(await px(img, mid, Math.round(off - 12))));
  assert.ok(isBlue(await px(img, mid, Math.round(geo.artPx - off + 12))));
});

test("photo at the very edge of the original: the missing part repeats the edge instead of leaving white", { skip: !sharp && "no sharp here" }, async () => {
  const ph = await markedPhoto();
  const geo = P.geometry(2.45, 2.02, 1.9);
  const crop = { x: 0.5, y: 0, z: 1 };                           // square touching the top of the photo
  const img = await P._renderOne({ path: "p/1.jpg", frame: "none", crop }, { geo, enhance: false, readPhoto: async () => ph.buf });
  const top = await px(img, Math.round(geo.artPx / 2), 2);
  assert.ok(!(top[0] > 240 && top[1] > 240 && top[2] > 240), "no white band at the top");
  assert.equal((await sharp(img).metadata()).height, geo.artPx);
});

test("framed photo: the whole frame face lands on the visible front", { skip: !sharp && "no sharp here" }, async () => {
  const geo = P.geometry(2.45, 2.02, 1.9);
  const face = await sharp({ create: { width: P.FACE_PX, height: P.FACE_PX, channels: 3, background: "#00AA00" } })
    .composite([{ input: await sharp({ create: { width: 20, height: P.FACE_PX, channels: 3, background: "#FF0000" } }).png().toBuffer(), left: 0, top: 0 }])
    .jpeg().toBuffer();
  const img = await P._toPrintVisible(sharp, face, geo);
  const off = (geo.artPx - geo.visPx) / 2, mid = Math.round(geo.artPx / 2);
  assert.equal((await sharp(img).metadata()).width, geo.artPx);
  assert.ok(isRed(await px(img, Math.round(off + 5), mid)), "the left edge of the face is at the visible front");
  assert.ok(isRed(await px(img, Math.round(off - 5), mid)), "and carries on over the edge (mirrored)");
  const g = await px(img, Math.round(off + 40), mid);
  assert.ok(g[1] > 140 && g[0] < 80, "inside: the face");
});

test("photos get a black border unless the order chooses one; designs keep the sheet default", () => {
  const order = { items: [{ kind: "design", id: "d1", qty: 1 }, { kind: "photos", packSize: 1, photos: [{ path: "p/1.jpg" }] }] };
  const plan = P.planTiles(order, "#000000");
  assert.equal(plan.tiles.find((t) => t.kind === "photo").border, "#000000");
  assert.equal(plan.tiles.find((t) => t.kind === "design").border, undefined);
  const chosen = P.planTiles({ ...order, printBorders: { items: { 1: "#FFFFFF" } } }, "#000000");
  assert.equal(chosen.tiles.find((t) => t.kind === "photo").border, "#FFFFFF");
  assert.notEqual(plan.tiles[1].key, chosen.tiles[1].key, "a different border is a different picture");
  assert.deepEqual(P.fillFor("#000000"), { extendWith: "background", background: { r: 0, g: 0, b: 0 } });
  assert.deepEqual(P.fillFor("auto"), { extendWith: "mirror" });
});

test("where the photo runs out over the edge: the border colour, not stripes of repeated pixels", { skip: !sharp && "no sharp here" }, async () => {
  const ph = await markedPhoto();
  const geo = P.geometry(2.45, 2.02, 1.9);
  const img = await P._renderOne({ path: "p/1.jpg", frame: "none", crop: { x: 0.5, y: 0, z: 1 }, border: "#000000" },
    { geo, enhance: false, readPhoto: async () => ph.buf });
  const top = await px(img, Math.round(geo.artPx / 2), 4);
  assert.ok(top[0] < 30 && top[1] < 30 && top[2] < 30, `black above the photo, got ${top}`);
});

test("photos with no frame bleed past the cut line; the preview still lands exactly on the visible front", { skip: !sharp && "no sharp here" }, async () => {
  const geo = P.geometry(2.45, 2.0, 1.9);
  assert.ok(geo.bleedPx > Math.round(2.45 * P.DPI), "past the cut");
  const plan = P.planTiles({ items: [{ kind: "photos", packSize: 2, photos: [{ path: "p/1.jpg" }, { path: "p/2.jpg", frame: "polaroid" }] }] }, "#000000");
  assert.equal(plan.tiles[0].bleed, true);
  assert.equal(plan.tiles[1].bleed, undefined, "framed photos keep their size");
  const ph = await markedPhoto();
  const img = await P._renderOne({ path: "p/1.jpg", frame: "none", crop: ph.crop, bleed: true, border: "#000000" }, { geo, enhance: false, readPhoto: async () => ph.buf });
  assert.equal((await sharp(img).metadata()).width, geo.bleedPx);
  const off = (geo.bleedPx - geo.visPx) / 2, mid = Math.round(geo.bleedPx / 2);
  assert.ok(isRed(await px(img, Math.round(off + 6), mid)), "the chosen part still starts at the visible front");
  assert.ok(isBlue(await px(img, Math.round(off - 40), mid)), "and the real photo carries on far past it");
});
