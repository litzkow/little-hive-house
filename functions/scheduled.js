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

module.exports = { deliveredFollowUp, backfillFees, lateShipments, DAYS };
