"use strict";
/* How a customer placed their photo in the magnet (the "move and zoom" step of the photo builder, assets/custom.js).

     crop = {x, y, z}   x, y: the point of the photo at the centre of the frame's window, as a fraction of the photo's
                        width and height (0..1, after EXIF rotation); z: zoom, 1 = the photo just covers the window
                        (the old centre-crop), up to ZMAX.

   The same math runs in three places, so what the customer saw is what prints:
     assets/custom.js (the builder), admin/admin-order.js (order page), printsheet.js (the PDF, through region()).
   Fractions don't depend on the file's resolution, so a photo shrunk or converted on upload still lines up. */

const ZMAX = 4;
const clamp = (v, lo, hi) => Math.min(hi, Math.max(lo, v));
const r4 = (v) => Math.round(v * 10000) / 10000;

/** A crop from the browser, checked: {x, y, z} or null for the default (centred, no zoom). */
function clean(c) {
  if (!c || typeof c !== "object") return null;
  const x = Number(c.x), y = Number(c.y), z = Number(c.z);
  if (![x, y, z].every(Number.isFinite)) return null;
  const out = { x: r4(clamp(x, 0, 1)), y: r4(clamp(y, 0, 1)), z: r4(clamp(z, 1, ZMAX)) };
  return out.x === 0.5 && out.y === 0.5 && out.z === 1 ? null : out;
}

/* The paper around a magnet wraps over its sides, so a photo that reaches the edge of the face is printed a little
   past it with the photo itself, where the photo has more to show (the part just outside what the customer picked).
   The photo is never zoomed for it: what shows on the front is exactly what the customer saw. BLEED is how far, in
   frame units (600 = the 2 in face), only on the sides where the frame's window touches the edge of the face. */
const BLEED = 60;                                      // 0.2 in: past the punch's cut line (2.45 in piece)
/** {l, t, r, b} in frame units for a frame window [x, y, w, h] (600-unit face). */
function bleedFor(win) {
  const [x, y, w, h] = win || [0, 0, 600, 600];
  return { l: x <= 0 ? BLEED : 0, t: y <= 0 ? BLEED : 0, r: x + w >= 600 ? BLEED : 0, b: y + h >= 600 ? BLEED : 0 };
}

/**
 * The part of a w x h photo that fills a winW x winH window: {left, top, width, height} in photo pixels (not rounded).
 * The photo always covers the whole window; a centre too close to an edge slides back inside. With `bleed` ({l, t, r,
 * b} in window units) also box: the window grown by the bleed, as far as the photo goes (it may be less on a side).
 */
function region(w, h, winW, winH, crop, bleed) {
  const c = crop || { x: 0.5, y: 0.5, z: 1 };
  const z = clamp(Number(c.z) || 1, 1, ZMAX);
  const s = Math.max(winW / w, winH / h) * z;          // window units per photo pixel
  const width = Math.min(w, winW / s), height = Math.min(h, winH / s);
  const left = clamp((Number.isFinite(Number(c.x)) ? Number(c.x) : 0.5) * w - width / 2, 0, w - width);
  const top = clamp((Number.isFinite(Number(c.y)) ? Number(c.y) : 0.5) * h - height / 2, 0, h - height);
  const out = { left, top, width, height };
  if (bleed) {
    const bl = Math.max(0, left - bleed.l / s), bt = Math.max(0, top - bleed.t / s);
    const br = Math.min(w, left + width + bleed.r / s), bb = Math.min(h, top + height + bleed.b / s);
    out.box = { left: bl, top: bt, width: br - bl, height: bb - bt };
    out.scale = s;
  }
  return out;
}

/** region() in whole pixels inside the photo, for sharp's extract() (box too, when there is bleed). */
function regionPx(w, h, winW, winH, crop, bleed) {
  const r = region(w, h, winW, winH, crop, bleed);
  const px = (q) => {
    const left = clamp(Math.round(q.left), 0, w - 1), top = clamp(Math.round(q.top), 0, h - 1);
    return { left, top, width: clamp(Math.round(q.width), 1, w - left), height: clamp(Math.round(q.height), 1, h - top) };
  };
  const out = px(r);
  if (bleed) {
    out.box = px(r.box);
    // how far the box reaches past the window on each side, in window units (what the photo really has there)
    out.ext = { l: Math.round((out.left - out.box.left) * r.scale), t: Math.round((out.top - out.box.top) * r.scale),
      r: Math.round((out.box.left + out.box.width - out.left - out.width) * r.scale), b: Math.round((out.box.top + out.box.height - out.top - out.height) * r.scale) };
  }
  return out;
}

module.exports = { ZMAX, BLEED, bleedFor, clean, region, regionPx };
