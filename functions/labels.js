"use strict";
/* USPS labels bought from the Hive Admin, through Shippo (https://goshippo.com, the API key is the GitHub secret
   SHIPPO_API_KEY, the same one the automatic tracking uses).
   The owners close the parcel and tap "Buy label" on the order: adminLabelQuote shows the USPS Ground Advantage price for
   the weight the app suggests (from the number of magnets), adminBuyLabel buys it, keeps the label PDF on the order and
   then marks the order shipped exactly like typing the tracking by hand (adminShip: the card is charged, the customer
   gets the shipped email, automatic tracking starts).
   A test key (shippo_test_...) makes sample labels that can't be mailed: the order is NOT marked shipped with one. */

const { fail, env, nowIso } = require("./config");
const deps = require("./deps");
const U = require("./util");
const O = require("./orders");

const BASE = "https://api.goshippo.com";
/* Shippo's free plan: 30 labels a month with no fee, then 7 cents each. The fee goes into the label cost, so the
   reports count it (labelStats/{YYYY-MM}.count is how many labels the shop bought that month). */
const FREE_LABELS = 30, LABEL_FEE = 0.07;
const SERVICE = "usps_ground_advantage";

/* what a package weighs: the mailer with the card, sticker, business card and the logo magnet, plus each magnet (oz) */
const DEFAULTS = { packageBaseOz: 2.5, magnetOz: 0.45, parcelLengthIn: 7, parcelWidthIn: 5, parcelHeightIn: 1 };
const MAX_OZ = 70 * 16;

function key() {
  const k = env("SHIPPO_API_KEY");
  if (!k) fail("failed-precondition", "Labels aren't set up yet: the Shippo key (SHIPPO_API_KEY) is missing. See SETUP.md, “USPS labels”.");
  return k;
}
const isTestKey = () => /^shippo_test_/.test(env("SHIPPO_API_KEY"));

async function shippo(path, body) {
  const res = await globalThis.fetch(`${BASE}${path}`, {
    method: body ? "POST" : "GET",
    headers: { Authorization: `ShippoToken ${key()}`, "Content-Type": "application/json", Accept: "application/json" },
    body: body ? JSON.stringify(body) : undefined,
  });
  let json = null;
  try { json = await res.json(); } catch (e) { json = null; }
  if (!res.ok) {
    const why = json && (json.detail || (Array.isArray(json.__all__) && json.__all__.join(" ")) || JSON.stringify(json).slice(0, 300));
    console.error(`[labels] Shippo ${path} ${res.status}`, why);
    if (res.status === 401 || res.status === 403) fail("failed-precondition", "Shippo didn't accept the key. Check SHIPPO_API_KEY.");
    fail("aborted", `Shippo said: ${why || res.status}`);
  }
  return json || {};
}

async function settings() {
  const snap = await deps.db().collection("settings").doc("store").get();
  return snap.exists ? snap.data() : {};
}

/** The sender on the label (Settings › Shipping › Ship from). */
function fromAddress(s) {
  const a = (s && s.shipFrom) || {};
  const out = { name: a.name || "Little Hive House", company: a.company || "", street1: a.street1 || "", street2: a.street2 || "",
    city: a.city || "", state: a.state || "", zip: a.zip || "", country: "US", phone: a.phone || "", email: a.email || env("MAIL_ADMIN") || "" };
  if (!out.street1 || !out.city || !out.state || !out.zip) {
    fail("failed-precondition", "The return address for labels isn't set yet (Settings › Shipping › Ship from).");
  }
  return out;
}

/** The customer, from the order's shipping address (Stripe's format). */
function toAddress(order) {
  const s = order.shipping || {}, a = s.address || {};
  if (!a.line1 || !a.city || !a.postal_code) fail("failed-precondition", "This order has no full shipping address.");
  if (a.country && a.country !== "US") fail("failed-precondition", "Labels from the app are for US addresses only.");
  return { name: s.name || order.name || "Customer", street1: a.line1, street2: a.line2 || "", city: a.city, state: a.state || "",
    zip: a.postal_code, country: "US", phone: s.phone || order.phone || "", email: order.email || "" };
}

/** Suggested weight in ounces, rounded up to a tenth: the package plus every magnet in the order. */
function suggestOz(order, s) {
  const st = { ...DEFAULTS, ...(s || {}) };
  const n = countMagnets(order);
  return Math.ceil((Number(st.packageBaseOz) + n * Number(st.magnetOz)) * 10) / 10;
}
/** Magnets in the order, counted like the admin's reports (admin/reports.js itemMagnets). */
function countMagnets(order) {
  const num = (v) => (Number.isFinite(Number(v)) ? Number(v) : 0);
  return (order.items || []).reduce((t, it) => {
    const q = it.qty == null ? 1 : num(it.qty);
    if (it.kind === "design") return t + q;
    if (it.kind === "photos") return t + num(it.packSize) * q;
    if (it.kind === "package") return t + num(it.size) * q;
    return t + num(it.magnets) * q;
  }, 0);
}

function parcel(s, oz) {
  const st = { ...DEFAULTS, ...(s || {}) };
  return { length: String(st.parcelLengthIn), width: String(st.parcelWidthIn), height: String(st.parcelHeightIn), distance_unit: "in",
    weight: String(oz), mass_unit: "oz" };
}

function cleanOz(v, fallback) {
  if (v === undefined || v === null || v === "") return fallback;
  const n = Number(v);
  if (!Number.isFinite(n) || n <= 0 || n > MAX_OZ) fail("invalid-argument", "The weight should be in ounces, like 4.5.");
  return Math.ceil(n * 10) / 10;
}

/* USPS Ground Advantage charges by weight bands: up to 4, 8, 12 and 15.99 oz, then by the pound (rounded up). The owners
   type what the scale shows; the label goes out at the top of the band that weight falls in, after a little room for the
   label paper and the tape (SAFETY_OZ). Same price as the exact weight, and the post office never finds it underpaid. */
const SAFETY_OZ = 0.3;
const OZ_BANDS = [4, 8, 12, 15.99];
function prudentOz(scaleOz) {
  const w = Math.max(0.1, Number(scaleOz) || 0) + SAFETY_OZ;
  for (const b of OZ_BANDS) if (w <= b) return b;
  return Math.ceil(w / 16) * 16;
}

/** The USPS Ground Advantage rate (or the cheapest USPS one when Ground Advantage isn't offered). */
function pickRate(rates) {
  const usps = (rates || []).filter((r) => r && /usps/i.test(r.provider || "") && r.object_id);
  if (!usps.length) return null;
  const ga = usps.filter((r) => r.servicelevel && r.servicelevel.token === SERVICE);
  const pool = ga.length ? ga : usps;
  return pool.slice().sort((a, b) => Number(a.amount) - Number(b.amount))[0];
}
const rateView = (r, shipment) => ({ rateId: r.object_id, shipmentId: shipment, amount: Math.round(Number(r.amount) * 100) / 100,
  currency: r.currency || "USD", service: (r.servicelevel && r.servicelevel.name) || "USPS", days: r.estimated_days || r.days || null });

async function loadOrder(orderId) {
  const id = U.text(orderId, 64, { required: true, field: "the order id" });
  if (!/^[A-Za-z0-9_-]+$/.test(id)) fail("invalid-argument", "That order id is not valid.");
  const ref = deps.db().collection("orders").doc(id);
  const snap = await ref.get();
  if (!snap.exists) fail("not-found", "We couldn't find that order.");
  return { ref, id, order: snap.data() };
}
const SHIPPABLE = ["paid", "in_production", "partially_refunded"];

/** The suggested weight and the price, before buying. {orderId, oz?} */
async function adminLabelQuote(data, auth) {
  U.requireAdmin(auth);
  key();
  const { order } = await loadOrder(data && data.orderId);
  if (!SHIPPABLE.includes(order.status)) fail("failed-precondition", `An order that is "${O.STATUS_LABELS[order.status] || order.status}" can't get a label.`);
  const s = await settings();
  const suggested = suggestOz(order, s);
  const scale = cleanOz(data && data.oz, null);          // what the scale showed (empty: the app's guess)
  const oz = prudentOz(scale == null ? suggested : scale);
  const shipment = await shippo("/shipments/", { address_from: fromAddress(s), address_to: toAddress(order), parcels: [parcel(s, oz)], async: false });
  const rate = pickRate(shipment.rates);
  if (!rate) {
    const msg = (shipment.messages || []).map((m) => m && m.text).filter(Boolean).join(" ");
    fail("aborted", `USPS gave no price for this address${msg ? `: ${msg}` : "."} Check the address on the order.`);
  }
  return { ok: true, oz, scaleOz: scale, suggestedOz: suggested, test: isTestKey(), rate: rateView(rate, shipment.object_id) };
}

/** Buys the label for {orderId, rateId, oz} and marks the order shipped with its tracking. */
async function adminBuyLabel(data, auth) {
  U.requireAdmin(auth);
  key();
  const rateId = U.text(data && data.rateId, 64, { required: true, field: "the price" });
  const { ref, id, order } = await loadOrder(data && data.orderId);
  if (!SHIPPABLE.includes(order.status)) fail("failed-precondition", `An order that is "${O.STATUS_LABELS[order.status] || order.status}" can't get a label.`);
  const prev = (order.fulfillment && order.fulfillment.label) || null;
  if (prev && prev.tracking && !prev.test && !(data && data.again)) {
    fail("already-exists", "This order already has a label. Open it from the order, or buy a new one only if that one wasn't used.");
  }
  const tx = await shippo("/transactions/", { rate: rateId, label_file_type: "PNG", async: false, metadata: `order ${id}` });
  if (tx.status !== "SUCCESS" || !tx.tracking_number || !tx.label_url) {
    const msg = (tx.messages || []).map((m) => m && m.text).filter(Boolean).join(" ");
    console.error("[labels] Shippo transaction", tx.status, JSON.stringify(tx.messages || []).slice(0, 800));
    fail("aborted", `The label wasn't bought${msg ? `: ${msg}` : "."} Nothing was charged for it.`);
  }
  const test = isTestKey();
  const month = nowIso().slice(0, 7), statRef = deps.db().collection("labelStats").doc(month);
  let used = 0;
  if (!test) { try { const st = await statRef.get(); used = st.exists ? Number(st.data().count) || 0 : 0; } catch (e) { used = 0; } }
  const fee = !test && used >= FREE_LABELS ? LABEL_FEE : 0;
  let cost = null;
  if (data && data.amount !== undefined) { const c = Number(data.amount); if (Number.isFinite(c) && c >= 0 && c < 1000) cost = Math.round(c * 100) / 100; }
  if (tx.rate && typeof tx.rate === "object" && Number.isFinite(Number(tx.rate.amount))) cost = Math.round(Number(tx.rate.amount) * 100) / 100;
  if (cost != null) cost = Math.round((cost + fee) * 100) / 100;
  if (!test) await statRef.set({ count: used + 1, updatedAt: nowIso() }, { merge: true }).catch(() => {});
  const label = { url: tx.label_url, tracking: tx.tracking_number, transaction: tx.object_id || "", rate: rateId, cost, fee,
    oz: cleanOz(data && data.oz, null), at: nowIso(), by: U.who(auth), test };
  await ref.update({ "fulfillment.label": label, "fulfillment.labels": ((order.fulfillment && order.fulfillment.labels) || []).concat([label]) });
  if (test) return { ok: true, test: true, label, shipped: false };
  // same as typing the tracking by hand: charge the card, mark shipped, email the customer, start tracking
  const admin = require("./admin");
  try {
    const ship = await admin.adminShip({ orderId: id, carrier: "usps", tracking: tx.tracking_number, labelCost: cost == null ? "" : cost }, auth);
    return { ok: true, test: false, label, shipped: true, ship };
  } catch (err) {
    // the label is bought and saved on the order; the shipping step can be retried with the same tracking
    return { ok: true, test: false, label, shipped: false, shipError: err && err.message ? err.message : String(err) };
  }
}

/* ---------- printing on half-sheet labels (8.5 x 5.5 in, 2 per Letter sheet) ----------
   The USPS label is 4 x 6 in standing up; each half of the sheet is 8.5 x 5.5 lying down. The label is turned on its side
   and centred in the top or the bottom half of a Letter page, so it lands on one sticker and the other stays for the next. */
function pngSize(buf) {
  if (!buf || buf.length < 24 || buf.readUInt32BE(0) !== 0x89504e47) return null;
  return { w: buf.readUInt32BE(16), h: buf.readUInt32BE(20) };
}
function halfSheetPdf(png, half) {
  const PDFDocument = require("./printsheet")._internal.loadPdfkit();
  const size = pngSize(png);
  if (!size) throw new Error("the label image isn't a PNG");
  return new Promise((resolve, reject) => {
    const doc = new PDFDocument({ size: "LETTER", margin: 0, info: { Title: "USPS label · Little Hive House" } });
    const out = [];
    doc.on("data", (b) => out.push(b)); doc.on("end", () => resolve(Buffer.concat(out))); doc.on("error", reject);
    const W = 612, HALF = 396, LW = 432, LH = 288;          // points: the page, half the page, the label lying down (6 x 4 in)
    const x0 = (W - LW) / 2, y0 = (half === "bottom" ? HALF : 0) + (HALF - LH) / 2;
    if (size.w > size.h) doc.image(png, x0, y0, { width: LW, height: LH });
    else { doc.save(); doc.translate(x0 + LW, y0); doc.rotate(90); doc.image(png, 0, 0, { width: LH, height: LW }); doc.restore(); }
    doc.end();
  });
}
let makeHalf = halfSheetPdf;
/** Tests swap the PDF maker (pdfkit is not installed there). */
function setHalfSheet(fn) { makeHalf = fn || halfSheetPdf; }

/** A fresh link to the order's label laid out for the top or the bottom half of a label sheet. {orderId, half} */
async function adminLabelPdf(data, auth) {
  U.requireAdmin(auth);
  const half = data && data.half === "bottom" ? "bottom" : "top";
  const { id, order } = await loadOrder(data && data.orderId);
  const L = order.fulfillment && order.fulfillment.label;
  if (!L || !L.url) fail("not-found", "This order has no label from the app.");
  const printsheet = require("./printsheet");
  const p = `labels/${id}-${half}.pdf`, bucket = deps.bucket();
  let exists = false;
  try { [exists] = await bucket.file(p).exists(); } catch (e) { exists = false; }
  if (!exists || (L.builtFor && L.builtFor !== L.url)) {
    const res = await globalThis.fetch(L.url);
    if (!res.ok) fail("unavailable", `Couldn't get the label from Shippo (${res.status}). Try again in a minute.`);
    const png = Buffer.from(await res.arrayBuffer());
    const pdf = await makeHalf(png, half);
    await bucket.file(p).save(pdf, { contentType: "application/pdf", resumable: false,
      metadata: { cacheControl: "private, max-age=0", contentDisposition: `inline; filename="USPS-label-${order.number || id}.pdf"` } });
  }
  const link = await printsheet.downloadUrl(p, `USPS-label-${order.number || id}-${half}.pdf`);
  return { ok: true, url: link.url, half };
}

module.exports = { prudentOz, SAFETY_OZ, adminLabelPdf, setHalfSheet, halfSheetPdf, pngSize, FREE_LABELS, LABEL_FEE, adminLabelQuote, adminBuyLabel, DEFAULTS, suggestOz, pickRate, fromAddress, toAddress, countMagnets };
