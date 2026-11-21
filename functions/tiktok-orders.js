"use strict";
/* TikTok Shop orders in Hive Admin (every 15 minutes, with the Etsy ones): each TikTok order that is ready to ship
   (AWAITING_SHIPMENT or later; never UNPAID, and never ON_HOLD, TikTok's first hour when the buyer can still cancel)
   becomes an order here, with its own LHH number and the designs it asks for: the SKU's seller_sku "<collection>-<n>"
   is design n of that collection, in the site's order (tiktok-products.js). TikTok sends one line per magnet, so lines
   of the same SKU become one item with its quantity.
   The buyer is TikTok's customer: no email from us (TikTok talks to them, and hides their email).
   Shipping: TikTok Shipping only (US sellers can't use their own labels on TikTok orders since 2026). "TikTok label" on
   the order page ships the package (drop-off) and gets TikTok's label PDF; the tracking number comes from TikTok and
   the order is marked shipped here. Order docs: orders/tiktok-<TikTok order id>. */

const { nowIso, mailAdmin, fail } = require("./config");
const deps = require("./deps");
const O = require("./orders");
const T = () => require("./tiktok")._internal;

const READY = new Set(["AWAITING_SHIPMENT", "AWAITING_COLLECTION", "IN_TRANSIT", "DELIVERED", "COMPLETED"]);
const SHIPPED = new Set(["AWAITING_COLLECTION", "IN_TRANSIT", "DELIVERED", "COMPLETED"]);
const r2 = (n) => Math.round(Number(n || 0) * 100) / 100;
const LISTINGS = () => require("./etsy-listings.json").listings;

/** seller_sku "places-12" -> the design item (or a custom item when it can't tell). */
function itemFor(sku, lines) {
  const first = lines[0];
  const qty = lines.length;
  const unit = r2(first.sale_price);
  const m = /^(.+)-(\d{1,3})$/.exec(String(sku || ""));
  const l = m && LISTINGS().find((x) => x.id === m[1]);
  const id = l && (l.designs || [])[Number(m[2]) - 1];
  if (id) {
    const c = require("./catalog.json").designs[id] || {};
    return { kind: "design", id, title: c.title || String(first.sku_name || first.product_name || "").slice(0, 120), collection: c.collection || l.id, qty, unit,
      tiktok: { productId: String(first.product_id || ""), skuId: String(first.sku_id || ""), sku: String(sku) } };
  }
  return { kind: "custom", title: `${first.product_name || "TikTok item"}${first.sku_name ? `: ${first.sku_name}` : ""}`.slice(0, 120), magnets: qty, price: r2(unit * qty), qty: 1,
    notes: `Couldn't tell which design from TikTok (${sku || "no SKU"}).`, tiktok: { productId: String(first.product_id || ""), skuId: String(first.sku_id || "") } };
}

function address(a) {
  a = a || {};
  const level = (n) => ((a.district_info || []).find((d) => String(d.address_level_name || "").toLowerCase() === n) || {}).address_name || "";
  return {
    name: a.name || "",
    address: { line1: a.address_line1 || a.address_detail || "", line2: [a.address_line2, a.address_line3, a.address_line4].filter(Boolean).join(", "),
      city: level("city") || "", state: level("state") || "", postal_code: a.postal_code || "", country: a.region_code || "US" },
  };
}

/** Builds the Hive Admin order from a TikTok order (pure; the number is given). */
function toOrder(t, number, shopId, at = nowIso()) {
  const groups = new Map();
  for (const li of t.line_items || []) {
    const k = li.seller_sku || li.sku_id || li.id;
    if (!groups.has(k)) groups.set(k, []);
    groups.get(k).push(li);
  }
  const items = [...groups.entries()].map(([sku, lines]) => itemFor(sku, lines));
  const p = t.payment || {};
  const created = t.create_time ? new Date(Number(t.create_time) * 1000).toISOString() : at;
  const paid = t.paid_time ? new Date(Number(t.paid_time) * 1000).toISOString() : created;
  const magnets = items.reduce((n, it) => n + (it.kind === "design" ? it.qty : Number(it.magnets) || 0), 0);
  // what the shop is credited: the products at full price, less the discounts the shop pays for (TikTok's own
  // discounts are paid by TikTok), plus the shipping the buyer paid. Sales tax: TikTok collects and pays it
  // (marketplace facilitator), so it never counts as owed by the shop here.
  const subtotal = r2(p.original_total_product_price || p.sub_total);
  const sellerOff = r2(p.seller_discount);
  const shipFee = r2(p.shipping_fee);
  const ship = address(t.recipient_address);
  const notes = items.filter((it) => it.notes).map((it) => ({ at, by: "tiktok", text: it.notes }));
  if (t.buyer_message) notes.push({ at, by: "tiktok", text: `Message from the buyer: ${t.buyer_message}` });
  const shipped = SHIPPED.has(String(t.status));
  return {
    number: O.formatOrderNumber(number), source: "tiktok", email: "", name: ship.name, status: shipped ? "shipped" : "paid",
    items, shipping: ship, giftMessage: "", notes: t.buyer_message || "", lang: "en",
    pricing: { subtotal, shipping: shipFee, tax: 0, discount: sellerOff, sale: sellerOff ? { name: "TikTok promotion", amount: sellerOff } : null,
      total: r2(subtotal - sellerOff + shipFee), buyerPaid: r2(p.total_amount), currency: "usd", magnets, bundleDiscount: 0, volumeDiscount: 0, volumePct: 0, promo: null },
    payment: { state: "captured", capturedAt: paid, by: "tiktok" }, stripe: null,
    tiktok: { orderId: String(t.id), shopId: String(shopId || ""), status: String(t.status || ""), packageIds: (t.packages || []).map((x) => String(x.id)),
      url: `https://seller-us.tiktok.com/order/detail?order_no=${t.id}` },
    fulfillment: shipped && t.tracking_number ? { carrier: carrierOf(t.shipping_provider), tracking: String(t.tracking_number), shippedAt: at } : null,
    refunds: [], refundedTotal: 0, adminNotes: notes,
    timeline: [{ at: paid, status: "paid", text: "Paid on TikTok Shop." }],
    emails: { confirmation: null, shipped: null, delivered: null, refund: [] },
    createdAt: created, paidAt: paid, updatedAt: at,
  };
}

function carrierOf(name) {
  const n = String(name || "").toLowerCase();
  return /usps/.test(n) ? "usps" : /fedex/.test(n) ? "fedex" : /ups/.test(n) ? "ups" : /dhl/.test(n) ? "dhl" : "other";
}

/** The ready TikTok orders of the last `days` days into Hive Admin (each once). */
async function importOrders({ days = 30 } = {}) {
  const a = await T().readAuth();
  if (!a || !a.shopCipher) return { connected: false };
  const db = deps.db();
  const sum = { checked: 0, added: 0 };
  let token = "";
  for (let page = 0; page < 10; page++) {
    const d = await T().call("POST", "/order/202309/orders/search", {
      query: { page_size: "50", sort_field: "create_time", sort_order: "DESC", ...(token ? { page_token: token } : {}) },
      json: { create_time_ge: Math.floor(Date.now() / 1000) - days * 86400 },
    });
    for (const t of d.orders || []) {
      sum.checked++;
      if (!READY.has(String(t.status))) continue;
      const ref = db.collection("orders").doc(`tiktok-${t.id}`);
      if ((await ref.get()).exists) continue;
      const order = await db.runTransaction(async (tx) => {
        const cRef = db.collection("meta").doc("counters");
        const c = await tx.get(cRef);
        if ((await tx.get(ref)).exists) return null;
        const n = O.nextOrderNumber(c.exists ? c.data().orderNumber : undefined);
        const o = toOrder(t, n, a.shopId);
        tx.set(cRef, { orderNumber: n }, { merge: true });
        tx.set(ref, o);
        return o;
      });
      if (!order) continue;
      sum.added++;
      try { await require("./mail").send({ to: mailAdmin(), kind: "admin_new_order", data: { order: { id: ref.id, ...O.emailOrder(ref.id, order), source: "tiktok" } } }); } catch (e) { /* never blocks */ }
    }
    token = d.next_page_token || "";
    if (!token) break;
  }
  console.log("[tiktokOrders]", JSON.stringify(sum));
  return sum;
}

/** "TikTok label": ships the order's package with TikTok Shipping (drop-off) the first time, then returns the label PDF
    link (TikTok's link expires, so it's asked again each time). The tracking number marks the order shipped here. */
async function label(orderId) {
  const db = deps.db();
  const ref = db.collection("orders").doc(String(orderId));
  const snap = await ref.get();
  if (!snap.exists) fail("not-found", "Order not found.");
  const o = snap.data();
  if (o.source !== "tiktok" || !o.tiktok) fail("failed-precondition", "This isn't a TikTok order.");
  const detail = ((await T().call("GET", "/order/202309/orders", { query: { ids: o.tiktok.orderId } })).orders || [])[0] || {};
  const pkgId = String(((detail.packages || [])[0] || {}).id || (o.tiktok.packageIds || [])[0] || "");
  if (!pkgId) fail("failed-precondition", "TikTok hasn't made a package for this order yet. Try again in a few minutes.");
  if (String(detail.status) === "AWAITING_SHIPMENT") {
    await T().call("POST", `/fulfillment/202309/packages/${pkgId}/ship`, { json: { handover_method: "DROP_OFF" } });
  }
  let doc = null;
  for (let attempt = 1; attempt <= 4 && !doc; attempt++) {
    try {
      doc = await T().call("GET", `/fulfillment/202309/packages/${pkgId}/shipping_documents`, { query: { document_type: "SHIPPING_LABEL", document_size: "A6" } });
    } catch (e) {
      if (!/11034037|11034023|still being generated/i.test(e.message) || attempt >= 4) throw e;
      await new Promise((r) => setTimeout(r, 2500 * attempt));
    }
  }
  const again = ((await T().call("GET", "/order/202309/orders", { query: { ids: o.tiktok.orderId } })).orders || [])[0] || detail;
  const tracking = String(again.tracking_number || doc.tracking_number || "");
  const at = nowIso();
  const upd = { "tiktok.status": String(again.status || ""), "tiktok.packageIds": [pkgId], updatedAt: at };
  if (tracking && o.status !== "shipped" && o.status !== "delivered") {
    upd.status = "shipped";
    upd.fulfillment = { ...(o.fulfillment || {}), carrier: carrierOf(again.shipping_provider), tracking, url: "", labelCost: null, shippedAt: at, deliveredAt: null,
      label: { by: "tiktok", at, packageId: pkgId } };
    upd.timeline = (o.timeline || []).concat([{ at, status: "shipped", text: O.TIMELINE_TEXT.shipped }]);
  }
  await ref.update(upd);
  return { url: doc.doc_url || "", tracking, carrier: carrierOf(again.shipping_provider), status: String(again.status || "") };
}

module.exports = { importOrders, label, toOrder, itemFor, carrierOf };
