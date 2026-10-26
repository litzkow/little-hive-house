"use strict";
/* Photo placement (move & zoom): the checked crop, the region that prints, and that it reaches the order and the print plan. */
const test = require("node:test");
const assert = require("node:assert/strict");
const C = require("../crop");
const P = require("../printsheet");

test("clean: keeps a real placement, drops the default and junk, clamps the rest", () => {
  assert.deepEqual(C.clean({ x: 0.3, y: 0.71234567, z: 1.5 }), { x: 0.3, y: 0.7123, z: 1.5 });
  assert.equal(C.clean({ x: 0.5, y: 0.5, z: 1 }), null, "centred and not zoomed = nothing to store");
  assert.equal(C.clean(null), null);
  assert.equal(C.clean("x"), null);
  assert.equal(C.clean({ x: "a", y: 0.5, z: 1 }), null);
  assert.deepEqual(C.clean({ x: -2, y: 3, z: 99 }), { x: 0, y: 1, z: C.ZMAX });
  assert.deepEqual(C.clean({ x: 0.5, y: 0.5, z: 0.2 }), null, "zoom under 1 means 1");
});

test("region: no crop = centred and just covering the window (the old behaviour)", () => {
  // a 4000 x 3000 landscape photo in a square window: the full height, centred
  assert.deepEqual(C.region(4000, 3000, 600, 600, null), { left: 500, top: 0, width: 3000, height: 3000 });
  // portrait in the instant frame's wide window (412 x 344)
  const r = C.region(3000, 4000, 412, 344, null);
  assert.equal(r.width, 3000);
  assert.ok(Math.abs(r.height - 3000 * 344 / 412) < 1e-9);
  assert.ok(Math.abs(r.top - (4000 - r.height) / 2) < 1e-9);
});

test("region: moving keeps the top of a tall photo (the 'photo loses the top' problem) and never shows past the edge", () => {
  const top = C.region(3000, 4000, 600, 600, { x: 0.5, y: 0, z: 1 });
  assert.deepEqual(top, { left: 0, top: 0, width: 3000, height: 3000 }, "slid back inside: starts at the very top");
  const zoomed = C.region(3000, 4000, 600, 600, { x: 0.25, y: 0.3, z: 2 });
  assert.deepEqual(zoomed, { left: 0, top: 450, width: 1500, height: 1500 });
  const max = C.region(3000, 4000, 600, 600, { x: 0.5, y: 0.5, z: 10 });
  assert.equal(max.width, 3000 / C.ZMAX, "zoom is capped");
  const px = C.regionPx(3001, 4001, 600, 600, { x: 0.9, y: 0.9, z: 1.37 });
  assert.ok(px.left + px.width <= 3001 && px.top + px.height <= 4001 && Number.isInteger(px.left) && px.width >= 1);
});

test("the placement reaches the order (pricing) and the print plan, and a moved photo prints separately from the same photo unmoved", () => {
  const { priceCart } = require("../pricing");
  const priced = priceCart([{ kind: "photos", packSize: 4, qty: 1, photos: [
    { path: "uploads/u/p/1.jpg", frame: "none", caption: "", crop: { x: 0.5, y: 0.1, z: 1.2 }, w: 3024, h: 4032 },
    { path: "uploads/u/p/2.jpg", frame: "none", caption: "", crop: { x: 0.5, y: 0.5, z: 1 }, w: "x", h: 10 },
  ] }]);
  const ph = priced.items[0].photos;
  assert.deepEqual(ph[0], { path: "uploads/u/p/1.jpg", frame: "none", caption: "", crop: { x: 0.5, y: 0.1, z: 1.2 }, w: 3024, h: 4032 });
  assert.deepEqual(ph[1], { path: "uploads/u/p/2.jpg", frame: "none", caption: "" }, "no crop, no bad size");
  const plan = P.planTiles({ items: [{ kind: "photos", packSize: 4, qty: 1, photos: [ph[0], { ...ph[0], crop: null }] }] });
  assert.deepEqual(plan.tiles[0].crop, { x: 0.5, y: 0.1, z: 1.2 });
  assert.equal(plan.tiles[1].crop, null);
  assert.notEqual(plan.tiles[0].key, plan.tiles[1].key);
  assert.equal(plan.tiles[2].key, plan.tiles[0].key, "repeats still share the artwork");
});

test("the caption lettering reaches the order only when the frame offers it and there is a caption", () => {
  const { priceCart } = require("../pricing");
  const ph = priceCart([{ kind: "photos", packSize: 4, qty: 1, photos: [
    { path: "a.jpg", frame: "instant", caption: "Summer", capStyle: "classic" },
    { path: "b.jpg", frame: "instant", caption: "Summer", capStyle: "comic-sans" },
    { path: "c.jpg", frame: "instant", caption: "", capStyle: "classic" },
    { path: "d.jpg", frame: "border", caption: "x", capStyle: "classic" },
  ] }]).items[0].photos;
  assert.equal(ph[0].capStyle, "classic");
  assert.equal(ph[1].capStyle, undefined);
  assert.equal(ph[2].capStyle, undefined);
  assert.equal(ph[3].capStyle, undefined);
  const plan = P.planTiles({ items: [{ kind: "photos", packSize: 2, photos: [ph[0], { ...ph[0], capStyle: undefined }] }] });
  assert.equal(plan.tiles[0].capStyle, "classic");
  assert.notEqual(plan.tiles[0].key, plan.tiles[1].key);
});
