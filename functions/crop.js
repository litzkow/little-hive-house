"use strict";
/* How a customer placed their photo in the magnet (the "move and zoom" step of the photo builder, assets/custom.js).

     crop = {x, y, z}   x, y: the point of the photo at the centre of the frame's window, as a fraction of the photo's
                        width and height (0..1, after EXIF rotation); z: zoom, 1 = the photo just covers the window
                        (the old centre-crop), up to ZMAX.

   The same math runs in three places, so what the customer saw is what prints:
     assets/custom.js (the builder), admin/admin-order.js (order page), printsheet.js (the PDF, through region()).
   Fractions don't depend on the file's resolution, so a photo shrunk or converted on upload still lines up. */

const ZMAX = 4;
/* "free" placement (crop.f = 1, the owners' test print): the photo can sit anywhere and smaller than the window, and the
   rest of the window is white paper. Customers' crops stay "cover" (the photo always fills the window). */
const ZMIN_FREE = 0.5;
const clamp = (v, lo, hi) => Math.min(hi, Math.max(lo, v));
const r4 = (v) => Math.round(v * 10000) / 10000;

/** A crop from the browser, checked: {x, y, z} or null for the default (centred, no zoom). */
function clean(c) {
  if (!c || typeof c !== "object") return null;
  const x = Number(c.x), y = Number(c.y), z = Number(c.z);
  if (![x, y, z].every(Number.isFinite)) return null;
  const free = c.f === 1 || c.f === true;
  const out = { x: r4(clamp(x, 0, 1)), y: r4(clamp(y, 0, 1)), z: r4(clamp(z, free ? ZMIN_FREE : 1, ZMAX)) };
  if (out.x === 0.5 && out.y === 0.5 && out.z === 1) return null;
  if (free) out.f = 1;
  return out;
}

/**
 * The part of a w x h photo that fills a winW x winH window: {left, top, width, height} in photo pixels (not rounded).
 * The photo always covers the whole window; a centre too close to an edge slides back inside.
 */
function region(w, h, winW, winH, crop) {
  const c = crop || { x: 0.5, y: 0.5, z: 1 };
  const cx = Number.isFinite(Number(c.x)) ? Number(c.x) : 0.5, cy = Number.isFinite(Number(c.y)) ? Number(c.y) : 0.5;
  if (c.f) {   // free: may reach past the photo's edges (the outside is white)
    const zf = clamp(Number(c.z) || 1, ZMIN_FREE, ZMAX), sf = Math.max(winW / w, winH / h) * zf;
    const wf = winW / sf, hf = winH / sf;
    return { left: cx * w - wf / 2, top: cy * h - hf / 2, width: wf, height: hf };
  }
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

/** Free placement in whole pixels: the part of the photo inside the window (src, for extract) and where it goes in the
 *  winW x winH window (dst), or null when no part of the photo shows. */
function placePx(w, h, winW, winH, crop) {
  const r = region(w, h, winW, winH, crop), k = winW / r.width;     // window pixels per photo pixel
  const l = Math.max(0, r.left), t = Math.max(0, r.top), rr = Math.min(w, r.left + r.width), bb = Math.min(h, r.top + r.height);
  if (rr - l < 1 || bb - t < 1) return null;
  const src = { left: Math.round(l), top: Math.round(t), width: Math.max(1, Math.min(w - Math.round(l), Math.round(rr - l))), height: Math.max(1, Math.min(h - Math.round(t), Math.round(bb - t))) };
  const dst = { x: Math.round((l - r.left) * k), y: Math.round((t - r.top) * k), w: Math.max(1, Math.round((rr - l) * k)), h: Math.max(1, Math.round((bb - t) * k)) };
  dst.w = Math.min(dst.w, winW - dst.x); dst.h = Math.min(dst.h, winH - dst.y);
  return { src, dst };
}

module.exports = { ZMAX, ZMIN_FREE, clean, region, regionPx, placePx };
