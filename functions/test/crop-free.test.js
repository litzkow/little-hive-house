"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const C = require("../crop");

test("crop: customers' crops always cover the window; the test print's free crops (f) can move past the edges and shrink", () => {
  assert.deepEqual(C.clean({ x: 0.2, y: 0.5, z: 0.6 }), { x: 0.2, y: 0.5, z: 1 });              // a customer can't shrink the photo
  assert.deepEqual(C.clean({ x: 0.2, y: 0.5, z: 0.6, f: 1 }), { x: 0.2, y: 0.5, z: 0.6, f: 1 });
  assert.deepEqual(C.clean({ x: 0.5, y: 0.5, z: 0.2, f: 1 }), { x: 0.5, y: 0.5, z: 0.5, f: 1 });  // no smaller than half
  assert.equal(C.clean({ x: 0.5, y: 0.5, z: 1, f: 1 }), null);
  // a landscape 2000 x 1000 photo in a square window: covered, it can only slide sideways; free, it moves up too
  const cover = C.region(2000, 1000, 600, 600, { x: 0.5, y: 0.2, z: 1 });
  assert.equal(cover.top, 0);
  const free = C.region(2000, 1000, 600, 600, { x: 0.5, y: 0.2, z: 1, f: 1 });
  assert.ok(free.top < 0, "the window goes above the photo: white paper there");
  const pl = C.placePx(2000, 1000, 600, 600, { x: 0.5, y: 0.2, z: 1, f: 1 });
  assert.deepEqual(pl.src, { left: 500, top: 0, width: 1000, height: 700 });
  assert.deepEqual(pl.dst, { x: 0, y: 180, w: 600, h: 420 });
  const small = C.placePx(1000, 1000, 600, 600, { x: 0.5, y: 0.5, z: 0.5, f: 1 });
  assert.deepEqual(small.dst, { x: 150, y: 150, w: 300, h: 300 });
});
