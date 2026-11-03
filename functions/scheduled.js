"use strict";
/* deliveredFollowUp (daily): orders shipped 10+ days ago and not marked delivered -> one reminder email to the shop.
   Orders that automatic tracking (tracking.js) checked successfully in the last 2 days are left out: it alerts on those
   itself (carrier problem, 7+ quiet days, 30 days). So this covers manual carriers and a tracker that stopped working. */

const { mailAdmin } = require("./config");
const deps = require("./deps");
const mail = require("./mail");
const O = require("./orders");

const DAYS = 10;

/** Pure: picks the late orders from [{id, data}] at time `now` (ms). */
function lateShipments(docs, now = Date.now()) {
  return docs
    .map(({ id, data }) => {
      const f = data.fulfillment || {};
      const t = Date.parse(f.shippedAt || "");
      if (data.status !== "shipped" || !Number.isFinite(t) || f.deliveredAt) return null;
      const checked = Date.parse(f.lastCheckedAt || "");
      if (Number.isFinite(checked) && now - checked < 2 * 86400000 && !f.trackingStoppedAt) return null;
      const days = Math.floor((now - t) / 86400000);
      if (days < DAYS) return null;
      return {
        id, number: data.number || "", name: data.name || "", email: data.email || "",
        carrier: f.carrier || "", carrierName: (O.CARRIERS[f.carrier] || O.CARRIERS.other).name, tracking: f.tracking || "", url: f.url || "",
        shippedAt: f.shippedAt, days, adminUrl: O.adminOrderUrl(id),
      };
    })
    .filter(Boolean)
    .sort((a, b) => b.days - a.days);
}

async function deliveredFollowUp() {
  const q = await deps.db().collection("orders").where("status", "==", "shipped").get();
  const late = lateShipments(q.docs.map((d) => ({ id: d.id, data: d.data() })));
  if (!late.length) { console.log("[deliveredFollowUp] nothing late"); return { late: 0 }; }
  await mail.send({ to: mailAdmin(), kind: "admin_delivery_check", data: { orders: late, now: new Date().toISOString() } });
  return { late: late.length };
}

/* backfillFees (every 2 hours): Stripe often settles the card fee a moment after checkout, so the fee may be missing
   when the order is marked paid. Fetch it later so reports use the real fee instead of an estimate. */
async function backfillFees(limit = 40) {
  const stripe = require("./stripe");
  const { dollars } = require("./pricing");
  const q = await deps.db().collection("orders").where("stripe.fee", "==", null).limit(limit * 3).get();
  let fixed = 0;
  for (const d of q.docs) {
    if (fixed >= limit) break;
    const o = d.data();
    const pi = o.stripe && o.stripe.paymentIntent;
    if (!pi || o.status === "pending" || o.status === "canceled") continue;
    if (o.payment && o.payment.state === "authorized") continue;   // not charged yet: no fee until it ships
    try {
      const p = await stripe.request("GET", `/payment_intents/${encodeURIComponent(pi)}`, { expand: ["latest_charge.balance_transaction"] });
      const bt = p && p.latest_charge && p.latest_charge.balance_transaction;
      if (bt && typeof bt === "object" && Number.isFinite(bt.fee)) {
        await d.ref.update({ "stripe.fee": dollars(bt.fee) });
        fixed += 1;
      }
    } catch (err) { console.warn("[backfillFees]", d.id, err.message); }
  }
  if (fixed) console.log(`[backfillFees] saved the real Stripe fee on ${fixed} order(s)`);
  return { fixed };
}

/* deletePhotos (daily), as the privacy page says: photos in a paid order are kept 1 year (time to make, ship, reprint
   and order the same photos again), photos that never became an order (a checkout left halfway) only 30 days.
   The small copies the admin shows (thumbs/uploads/...) follow their photo; print sheets (orders/<id>/...), which hold
   the photos, and the photos sent with a return (returns/...) are kept 1 year. */
const KEEP_ORDERED_DAYS = 365, KEEP_UNORDERED_DAYS = 30;
const stem = (p) => String(p || "").replace(/^thumbs\//, "").replace(/\.[A-Za-z0-9]+$/, "");
async function deletePhotos(now = Date.now()) {
  const bucket = deps.bucket(), day = 86400000;
  // every photo used in a paid order (reprints too) -> when it was paid
  const paid = new Map();
  const q = await deps.db().collection("orders").get();
  q.docs.forEach((d) => {
    const o = d.data();
    const at = Date.parse(o.paidAt || "");
    if (!Number.isFinite(at) || o.status === "pending") return;
    (o.items || []).forEach((it) => (it.photos || []).forEach((ph) => {
      const k = stem(ph && ph.path);
      if (k && (!paid.has(k) || paid.get(k) < at)) paid.set(k, at);
    }));
  });
  let deleted = 0;
  const drop = async (f) => { try { await f.delete(); deleted += 1; } catch (err) { console.warn("[deletePhotos]", f.name, err.message); } };
  for (const prefix of ["uploads/", "thumbs/uploads/", "orders/", "returns/", "thumbs/returns/"]) {
    const [files] = await bucket.getFiles({ prefix });
    for (const f of files) {
      const made = Date.parse((f.metadata && f.metadata.timeCreated) || "");
      if (!Number.isFinite(made)) continue;
      let until;
      if (prefix === "orders/" || /returns\//.test(prefix)) until = made + KEEP_ORDERED_DAYS * day;
      else {
        const paidAt = paid.get(stem(f.name));
        until = paidAt ? paidAt + KEEP_ORDERED_DAYS * day : made + KEEP_UNORDERED_DAYS * day;
      }
      if (now > until) await drop(f);
    }
  }
  if (deleted) console.log(`[deletePhotos] deleted ${deleted} old file(s)`);
  return { deleted };
}

module.exports = { deliveredFollowUp, backfillFees, lateShipments, deletePhotos, DAYS, KEEP_ORDERED_DAYS, KEEP_UNORDERED_DAYS };
