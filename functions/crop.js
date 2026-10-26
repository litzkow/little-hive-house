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
   past it with the photo itself (the part just outside what shows), never a reflection or a blur. BLEED is that extra,
   in frame units (600 = the 2 in face): only on the sides where the frame's window touches the edge of the face. */
const BLEED = 60;                                      // 0.2 in: past the punch's cut line (2.45 in piece)
/** {l, t, r, b} in frame units for a frame window [x, y, w, h] (600-unit face). */
function bleedFor(win) {
  const [x, y, w, h] = win || [0, 0, 600, 600];
  return { l: x <= 0 ? BLEED : 0, t: y <= 0 ? BLEED : 0, r: x + w >= 600 ? BLEED : 0, b: y + h >= 600 ? BLEED : 0 };
}

/**
 * The part of a w x h photo that fills a winW x winH window: {left, top, width, height} in photo pixels (not rounded),
 * plus box: the part that also covers the bleed around the window ({l, t, r, b} in window units, see bleedFor). The
 * photo always covers the window and its bleed (so zoom 1 is a touch closer than "just covers" when there is bleed);
 * a centre too close to an edge slides back inside.
 */
function region(w, h, winW, winH, crop, bleed) {
  const c = crop || { x: 0.5, y: 0.5, z: 1 };
  const B = bleed || { l: 0, t: 0, r: 0, b: 0 };
  const z = clamp(Number(c.z) || 1, 1, ZMAX);
  const bw = winW + B.l + B.r, bh = winH + B.t + B.b;
  const s = Math.max(bw / w, bh / h) * z;              // window units per photo pixel
  const width = Math.min(w, winW / s), height = Math.min(h, winH / s);
  const boxW = Math.min(w, bw / s), boxH = Math.min(h, bh / s);
  const cx = (Number.isFinite(Number(c.x)) ? Number(c.x) : 0.5) * w, cy = (Number.isFinite(Number(c.y)) ? Number(c.y) : 0.5) * h;
  const boxL = clamp(cx - (winW / 2 + B.l) / s, 0, w - boxW), boxT = clamp(cy - (winH / 2 + B.t) / s, 0, h - boxH);
  const out = { left: boxL + B.l / s, top: boxT + B.t / s, width, height };
  if (bleed) out.box = { left: boxL, top: boxT, width: boxW, height: boxH };
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
  if (bleed) out.box = px(r.box);
  return out;
}

module.exports = { ZMAX, BLEED, bleedFor, clean, region, regionPx };
