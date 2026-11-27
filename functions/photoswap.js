"use strict";
/* The customer swaps a photo of their own order (track.html with the order number + email, or order.html signed in),
   for example when they sent the same photo twice. Nov 2026, after order LHH-1004.

   - Only while the order is "Order received" (status paid): once the owners mark it "Being made" the photos are
     locked, so nothing changes under a sheet that is already printing.
   - Swapping keeps the price: the pack has the same number of magnets. The frame, caption and lettering stay;
     the framing (crop) starts fresh and autocrop.js places the new photo so no face is cut.
   - The print sheet is rebuilt and the owners get an email and a phone notification right away.

   orderPhotos({number, email} | {id}) -> {editable, reason, packs: [{index, title, packSize, photos: [{n, thumb, frame, caption}]}]}
   swapOrderPhoto({number, email} | {id}, index, n, path, w?, h?) -> {ok, photo: {n, thumb}, swaps} */

const { fail, nowIso, mailAdmin } = require("./config");
const deps = require("./deps");
const O = require("./orders");
const U = require("./util");

const PHOTO_PATH = /^uploads\/([^/]+)\/([A-Za-z0-9_-]{1,64})\/(\d{1,3})\.(jpe?g|png|heic|heif|webp)$/i;
const MAX_SWAPS = 30;                   // per order: plenty for fixing a few photos, not a way to reprint a whole album
const URL_TTL_MS = 60 * 60 * 1000;
const NOT_FOUND = "We couldn't find an order with that number and email. Please check both and try again.";
const LOCKED = "We've already started making this order, so its photos can't be changed anymore. Please contact us and we'll help.";

/** The order the caller may change: by number + email (any visitor who has both), or by id for the signed-in buyer. */
async function findOrder(data, auth) {
  const db = deps.db();
  if (data && data.id) {
    U.requireAccount(auth);
    const id = U.text(data.id, 64);
    if (!/^[A-Za-z0-9_-]+$/.test(id)) fail("not-found", NOT_FOUND);
    const snap = await db.collection("orders").doc(id).get();
    const o = snap.exists ? snap.data() : null;
    if (!o || !require("./customer").ownsOrder(o, auth)) fail("not-found", NOT_FOUND);
    return { ref: snap.ref || db.collection("orders").doc(id), id, order: o };
  }
  const number = O.normalizeOrderNumber(data && data.number);
  const email = U.cleanEmail(data && data.email);
  if (!number) fail("invalid-argument", "Order numbers look like LHH-1001.");
  const q = await db.collection("orders").where("number", "==", number).limit(1).get();
  const doc = q.empty ? null : q.docs[0];
  if (!doc || String(doc.data().email || "").toLowerCase() !== email) fail("not-found", NOT_FOUND);
  return { ref: doc.ref, id: doc.id, order: doc.data() };
}

/** Photo packs the customer uploaded themselves (Etsy / TikTok orders keep their photos elsewhere). */
function swappable(it) {
  return !!(it && it.kind === "photos" && Array.isArray(it.photos) && it.photos.length && it.photos.every((p) => p && PHOTO_PATH.test(p.path || "")));
}
/** null when the customer may swap photos now, otherwise why not (shown to them). */
function lockReason(o) {
  if (!o || !(o.items || []).some(swappable)) return "This order has no photos to change.";
  if (o.status !== "paid") return LOCKED;
  if ((Number(o.photoSwaps) || 0) >= MAX_SWAPS) return "This order has had a lot of photo changes already. Please contact us and we'll help.";
  return null;
}

/** A short-lived link to the small copy of a photo (the thumbnail is made once, shared with the Hive Admin). */
async function thumb(bucket, path) {
  const A = require("./admin")._internal;
  const token = await A.thumbUrl(bucket, path);
  // no small copy (a photo sharp can't read, like some HEIC): the original itself
  const tp = token ? `thumbs/${path.replace(/\.[A-Za-z0-9]+$/, "")}.jpg` : path;
  try {
    const file = bucket.file(tp);
    if (typeof file.getSignedUrl !== "function") throw new Error("no signing");
    const [url] = await file.getSignedUrl({ version: "v4", action: "read", expires: Date.now() + URL_TTL_MS });
    return url;
  } catch (err) {
    return token || (await A.photoUrl(bucket, path));   // the runtime can't sign: the Hive Admin's download-token link
  }
}

async function orderPhotos(data, auth, rawRequest) {
  await U.rateLimit("orderPhotos", U.clientIp(rawRequest) || (data && data.email) || (auth && auth.uid), 40, 900);
  const { order } = await findOrder(data, auth);
  const reason = lockReason(order);
  const bucket = deps.bucket();
  const packs = [];
  for (const [index, it] of (order.items || []).entries()) {
    if (!swappable(it)) continue;
    const photos = new Array(it.photos.length);
    let next = 0;
    const worker = async () => {
      while (next < it.photos.length) {
        const n = next++, p = it.photos[n];
        let url = null;
        try { url = await thumb(bucket, p.path); } catch (err) { console.warn("[photoswap] thumb", p.path, err && err.message); }
        photos[n] = { n: n + 1, thumb: url, frame: p.frame || "none", caption: p.caption || "" };
      }
    };
    await Promise.all([worker(), worker(), worker(), worker()]);
    packs.push({ index, title: it.title || `Custom photo magnets (${it.packSize})`, packSize: it.packSize, photos });
  }
  return { editable: !reason, reason: reason || "", number: order.number || "", packs };
}

async function swapOrderPhoto(data, auth, rawRequest) {
  U.requireAuth(auth);
  await U.rateLimit("swapOrderPhoto", U.clientIp(rawRequest) || auth.uid, 40, 3600);
  const { ref, id } = await findOrder(data, auth);
  const index = Number(data && data.index), n = Number(data && data.n);
  const path = U.text(data && data.path, 300);
  const m = PHOTO_PATH.exec(path);
  if (!m || m[1] !== auth.uid) fail("invalid-argument", "The new photo didn't upload correctly. Please try again.");
  let exists = true;
  try { [exists] = await deps.bucket().file(path).exists(); } catch (err) { exists = true; }
  if (!exists) fail("failed-precondition", "The new photo didn't finish uploading. Please try again.");
  const w = Math.round(Number(data && data.w)), h = Math.round(Number(data && data.h));

  const db = deps.db();
  let after = null, oldPath = "";
  await db.runTransaction(async (tx) => {
    const snap = await tx.get(ref);
    const o = snap.exists ? snap.data() : null;
    const why = lockReason(o);
    if (why) fail("failed-precondition", why);
    const it = (o.items || [])[index];
    if (!Number.isInteger(index) || !swappable(it)) fail("invalid-argument", "That photo pack isn't in this order.");
    if (!Number.isInteger(n) || n < 1 || n > it.photos.length) fail("invalid-argument", "That photo isn't in this order.");
    const items = JSON.parse(JSON.stringify(o.items));
    const was = items[index].photos[n - 1];
    oldPath = was.path;
    if (oldPath === path) fail("invalid-argument", "That's the same photo. Please pick a different one.");
    const photo = { path, frame: was.frame || "none", caption: was.caption || "" };
    if (was.capStyle) photo.capStyle = was.capStyle;
    if (w > 0 && h > 0 && w < 100000 && h < 100000) { photo.w = w; photo.h = h; }
    photo.swapped = { at: nowIso(), from: oldPath };
    items[index].photos[n - 1] = photo;
    const at = nowIso();
    const label = items.filter(swappable).length > 1 ? `Photo ${n} (pack ${items.slice(0, index + 1).filter(swappable).length})` : `Photo ${n}`;
    const update = {
      items, photoSwaps: (Number(o.photoSwaps) || 0) + 1, updatedAt: at,
      timeline: (o.timeline || []).concat([{ at, status: "photo_swap", text: `${label} was changed for a new one.` }]),
      adminNotes: (o.adminNotes || []).concat([{ at, by: "system", text: `The customer swapped photo ${n} for a new one.` }]),
    };
    tx.update(ref, update);
    after = { ...o, ...update };
  });

  // the new photo framed so no face is cut, then the print sheet made again (neither blocks the swap)
  after = await require("./autocrop").tryOrder(ref, after);
  const ps = await require("./printsheet").tryGenerate(ref, id, after);
  const bucket = deps.bucket();
  let url = null;
  try { url = await thumb(bucket, path); } catch (err) { /* the page shows the photo it already has */ }
  try {
    const mail = require("./mail");
    await mail.send({ to: mailAdmin(), kind: "admin_photo_swap", replyTo: after.email || undefined,
      data: { order: O.emailOrder(id, after), swap: { n, index, rebuilt: !!ps, swaps: after.photoSwaps, thumb: url } } });
  } catch (err) { console.warn("[photoswap] owners' alert", err && err.message); }
  return { ok: true, photo: { n, thumb: url }, swaps: after.photoSwaps };
}

module.exports = { orderPhotos, swapOrderPhoto, lockReason, swappable, MAX_SWAPS, PHOTO_PATH };
