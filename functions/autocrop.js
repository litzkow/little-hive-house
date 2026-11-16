"use strict";
/* Automatic framing of customer photos (15 Nov 2026, asked by the owners after an order where heads were cut).

   When an order is paid (checkout.js markPaid), every photo the customer did NOT move or zoom themselves (no crop) is
   checked: Google Cloud Vision finds the faces, and the window slides so every face fits with headroom and as much of
   the bodies below as fits (a nudge under 3% is skipped when no face is cut). The result is
   saved as the photo's crop ({x, y, z}, the same one the customer's "move and zoom" makes, see crop.js), with
   autoCrop: true, so the order page, the print sheet and any later reprint all use it. Photos the customer placed
   themselves are never touched. Nothing here can block an order: any failure leaves the photos as they were.

   Privacy: the photo goes to Google Cloud Vision (the same Google Cloud that already stores it) only to find faces;
   only box positions come back and only the crop numbers are kept. */

const deps = require("./deps");
const Crop = require("./crop");

const VISION_URL = "https://vision.googleapis.com/v1/images:annotate";
const HEADROOM = 1.1;     // space kept above the top face, in face heights (hair, hats, bows)
const BODY = 2.2;         // how much below the lowest face we'd like to show, in face heights
const BUDGET_MS = 25000;  // the whole order; photos not reached in time keep the default framing
const PARALLEL = 4;

let fetchImpl = (...a) => fetch(...a);
let tokenImpl = async () => {
  const r = await fetchImpl("http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token",
    { headers: { "Metadata-Flavor": "Google" } });
  if (!r.ok) throw new Error(`metadata token ${r.status}`);
  return (await r.json()).access_token;
};

/** Faces in an image: [{x, y, w, h}] as fractions of the upright image. */
async function findFaces(jpeg, token) {
  const r = await fetchImpl(VISION_URL, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
    body: JSON.stringify({ requests: [{ image: { content: jpeg.buffer.toString("base64") }, features: [{ type: "FACE_DETECTION", maxResults: 30 }] }] }),
  });
  const j = await r.json().catch(() => ({}));
  if (!r.ok) { const e = new Error(`vision ${r.status} ${(j.error && j.error.message) || ""}`.trim()); e.status = r.status; throw e; }
  const res = (j.responses && j.responses[0]) || {};
  if (res.error) throw new Error(`vision ${res.error.message || "error"}`);
  const W = jpeg.width, H = jpeg.height, m = Math.min(W, H);
  return (res.faceAnnotations || [])
    .filter((f) => (f.detectionConfidence || 0) >= 0.5)
    .map((f) => {
      const v = ((f.fdBoundingPoly || f.boundingPoly || {}).vertices || []).map((p) => ({ x: p.x || 0, y: p.y || 0 }));
      if (!v.length) return null;
      const xs = v.map((p) => p.x), ys = v.map((p) => p.y);
      const x = Math.min(...xs), y = Math.min(...ys), w = Math.max(...xs) - x, h = Math.max(...ys) - y;
      return w >= 0.04 * m ? { x: x / W, y: y / H, w: w / W, h: h / H } : null;
    })
    .filter(Boolean);
}

/** Is every face fully inside region r (photo fractions), with some room above it? */
function allInside(faces, r) {
  return faces.every((f) => f.x >= r.left - 1e-6 && f.x + f.w <= r.left + r.width + 1e-6
    && f.y - 0.3 * f.h >= r.top - 1e-6 && f.y + f.h <= r.top + r.height + 1e-6);
}

/**
 * The crop for a photo of aspect W:H in a window winW x winH, given its faces (fractions), or null to keep the
 * default (no faces, or the centred window already keeps every face with headroom).
 */
function pick(W, H, win, faces) {
  if (!faces || !faces.length) return null;
  const [, , winW, winH] = win;
  const reg = Crop.region(W, H, winW, winH, null);          // centred, zoom 1, in photo pixels
  const r = { left: reg.left / W, top: reg.top / H, width: reg.width / W, height: reg.height / H };
  const fh = Math.max(...faces.map((f) => f.h));
  let x = 0.5, y = 0.5;
  if (r.height < 0.999) {   // the window slides up/down
    const needTop = Math.max(0, Math.min(...faces.map((f) => f.y)) - HEADROOM * fh);
    const wantBottom = Math.min(1, Math.max(...faces.map((f) => f.y + f.h)) + BODY * fh);
    const lo = wantBottom - r.height, hi = needTop;
    let top = lo <= hi ? (lo + hi) / 2 : needTop;            // both if they fit, heads first if not
    top = Math.min(Math.max(0, top), 1 - r.height);
    y = top + r.height / 2;
  }
  if (r.width < 0.999) {    // the window slides left/right, centred on the people
    const l = Math.max(0, Math.min(...faces.map((f) => f.x)) - 0.4 * fh * H / W);
    const rr = Math.min(1, Math.max(...faces.map((f) => f.x + f.w)) + 0.4 * fh * H / W);
    const left = Math.min(Math.max(0, (l + rr) / 2 - r.width / 2), 1 - r.width);
    x = left + r.width / 2;
  }
  // a nudge of a few percent isn't worth changing what the customer saw; a face the centred window cuts always is
  if (Math.abs(x - 0.5) < 0.03 && Math.abs(y - 0.5) < 0.03 && allInside(faces, r)) return null;
  return Crop.clean({ x, y, z: 1 });
}

/** A light upright JPEG of a stored photo, for face finding: {buffer, width, height}. */
async function prepare(path) {
  const [buf] = await deps.bucket().file(path).download();
  const sharp = require("sharp");
  const { data, info } = await sharp(buf, { failOn: "none" }).rotate().resize({ width: 1600, height: 1600, fit: "inside", withoutEnlargement: true })
    .jpeg({ quality: 85 }).toBuffer({ resolveWithObject: true });
  return { buffer: data, width: info.width, height: info.height };
}

/**
 * Frames every photo of a paid order the customer didn't place themselves. Saves the crops on the order and returns
 * the order as updated (or unchanged). opts: {catalog, prepareImpl, now}.
 */
async function tryOrder(ref, order, opts = {}) {
  try {
    const catalog = opts.catalog || require("./pricing").loadCatalog();
    const frames = catalog.frames || {};
    const items = JSON.parse(JSON.stringify(order.items || []));
    const jobs = [];
    items.forEach((it, i) => {
      if (it.kind !== "photos") return;
      (it.photos || []).forEach((p, j) => { if (p && p.path && !p.crop) jobs.push({ i, j, p }); });
    });
    if (!jobs.length) return order;
    const start = Date.now(), token = await tokenImpl();
    const prep = opts.prepareImpl || prepare;
    let next = 0, changed = 0, fails = 0;
    const done = [];
    async function worker() {
      while (next < jobs.length && Date.now() - start < BUDGET_MS) {
        const job = jobs[next++];
        try {
          const img = await prep(job.p.path);
          const faces = await findFaces(img, token);
          const f = frames[job.p.frame] || {};
          const crop = pick(img.width, img.height, f.window || [0, 0, 600, 600], faces);
          // autoCrop keeps what the customer had (no crop = centred), so the owners can compare and undo (admin order page)
          if (crop) { const was = job.p.crop || null; items[job.i].photos[job.j].autoCrop = { from: was }; items[job.i].photos[job.j].crop = crop; changed++; done.push(job.j + 1); }
        } catch (err) {
          fails++;
          if (err && (err.status === 403 || err.status === 401)) { next = jobs.length; }   // API not enabled: stop asking
          console.warn("[autocrop]", job.p.path, err && err.message);
        }
      }
    }
    await Promise.all(Array.from({ length: Math.min(PARALLEL, jobs.length) }, worker));
    console.log(`[autocrop] ${order.number || ref.id}: ${jobs.length} photos checked, ${changed} reframed, ${fails} failed, ${Date.now() - start} ms`);
    if (!changed) return order;
    const at = (opts.now || (() => new Date().toISOString()))();
    await ref.update({ items, autoCrop: { at, photos: done.sort((a, b) => a - b) } });
    return { ...order, items, autoCrop: { at, photos: done } };
  } catch (err) {
    console.warn("[autocrop] skipped", err && err.message);
    return order;
  }
}

module.exports = { tryOrder, pick, findFaces, allInside,
  _set(o) { if (o.fetch) fetchImpl = o.fetch; if (o.token) tokenImpl = o.token; } };
