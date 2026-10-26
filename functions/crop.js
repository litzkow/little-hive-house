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

/**
 * The part of a w x h photo that fills a winW x winH window: {left, top, width, height} in photo pixels (not rounded).
 * The photo always covers the whole window; a centre too close to an edge slides back inside.
 */
function region(w, h, winW, winH, crop) {
  const c = crop || { x: 0.5, y: 0.5, z: 1 };
  const z = clamp(Number(c.z) || 1, 1, ZMAX);
  const s = Math.max(winW / w, winH / h) * z;          // window units per photo pixel
  const width = Math.min(w, winW / s), height = Math.min(h, winH / s);
  const left = clamp((Number.isFinite(Number(c.x)) ? Number(c.x) : 0.5) * w - width / 2, 0, w - width);
  const top = clamp((Number.isFinite(Number(c.y)) ? Number(c.y) : 0.5) * h - height / 2, 0, h - height);
  return { left, top, width, height };
}

/** region() in whole pixels inside the photo, for sharp's extract(). */
function regionPx(w, h, winW, winH, crop) {
  const r = region(w, h, winW, winH, crop);
  const left = clamp(Math.round(r.left), 0, w - 1), top = clamp(Math.round(r.top), 0, h - 1);
  return { left, top, width: clamp(Math.round(r.width), 1, w - left), height: clamp(Math.round(r.height), 1, h - top) };
}

module.exports = { ZMAX, clean, region, regionPx };
