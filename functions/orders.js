"use strict";
/* Pure order logic: statuses, numbers, refunds, carrier links, the public (customer-safe) view and email data.
   No Firebase here, so all of it is unit-tested. */

const { siteUrl } = require("./config");
const { cents, dollars } = require("./pricing");

const STATUSES = ["pending", "paid", "in_production", "shipped", "delivered", "canceled", "refunded", "partially_refunded"];
const STATUS_LABELS = {
  pending: "Checkout started", paid: "Order received", in_production: "Being made", shipped: "Shipped",
  delivered: "Delivered", canceled: "Canceled", refunded: "Refunded", partially_refunded: "Partially refunded",
};
const TIMELINE_TEXT = {
  pending: "Checkout started.", paid: "Payment received. Thank you!", in_production: "We are printing and pressing your magnets.",
  shipped: "Your order is on its way.", delivered: "Delivered. Enjoy your magnets!", canceled: "This order was canceled.",
  refunded: "This order was refunded.", partially_refunded: "Part of this order was refunded.",
};

/* Every status change, including the ones made by the system (webhook, refunds, ship, delivered). */
const TRANSITIONS = {
  pending: ["paid", "canceled"],
  paid: ["in_production", "shipped", "canceled", "refunded", "partially_refunded"],
  in_production: ["paid", "shipped", "canceled", "refunded", "partially_refunded"],
  shipped: ["in_production", "delivered", "refunded", "partially_refunded"],
  delivered: ["shipped", "refunded", "partially_refunded"],
  partially_refunded: ["in_production", "shipped", "delivered", "canceled", "refunded", "partially_refunded"],
  refunded: [],
  canceled: [],
};
/* What adminSetStatus may set by hand. Shipping, delivery and refunds have their own callables. */
const MANUAL_TARGETS = ["paid", "in_production", "shipped", "delivered", "canceled"];

function canTransition(from, to) {
  return !!(TRANSITIONS[from] && TRANSITIONS[from].includes(to));
}

/** null when allowed, otherwise a friendly reason. */
function manualStatusError(order, to) {
  const from = order.status;
  if (!STATUSES.includes(to)) return `Unknown status "${to}".`;
  if (!MANUAL_TARGETS.includes(to)) return `Use the Refund button to set "${STATUS_LABELS[to]}".`;
  if (from === to) return `This order is already "${STATUS_LABELS[to]}".`;
  if (from === "pending" && to === "paid") return "Orders become paid only when Stripe confirms the payment.";
  if (to === "canceled" && from !== "pending" && paidCents(order) - refundedCents(order) > 0) {
    return "Refund this order first (Refund button), then cancel it.";
  }
  if (!canTransition(from, to)) return `An order that is "${STATUS_LABELS[from] || from}" can't be changed to "${STATUS_LABELS[to]}".`;
  return null;
}

const ORDER_PREFIX = "LHH-";
const FIRST_NUMBER = 1001;
function formatOrderNumber(n) {
  if (!Number.isInteger(n) || n < 1) throw new Error("bad order number");
  return ORDER_PREFIX + n;
}
/** Given the stored counter (or undefined), returns the next numeric order number. */
function nextOrderNumber(counter) {
  const c = Number(counter);
  return Number.isInteger(c) && c >= FIRST_NUMBER ? c + 1 : FIRST_NUMBER;
}
function normalizeOrderNumber(s) {
  const m = String(s || "").trim().toUpperCase().replace(/\s+/g, "").match(/^(?:LHH-?|#)?(\d{3,9})$/);
  return m ? ORDER_PREFIX + Number(m[1]) : null;
}

/* ---------- refunds ---------- */
const REFUND_REASONS = {
  not_delivered: "Order not delivered", damaged: "Arrived damaged", wrong_item: "Wrong item", print_quality: "Print quality",
  late: "Arrived late", changed_mind: "Changed their mind", duplicate: "Duplicate order", other: "Other",
};
const paidCents = (order) => cents((order.pricing && order.pricing.total) || 0);
function refundedCents(order) {
  if (Array.isArray(order.refunds) && order.refunds.length) {
    return order.refunds.filter((r) => !r.status || r.status === "succeeded" || r.status === "pending")
      .reduce((a, r) => a + cents(r.amount || 0), 0);
  }
  return cents(order.refundedTotal || 0);
}
const refundableCents = (order) => Math.max(0, paidCents(order) - refundedCents(order));

/** Checks an admin refund. Returns {amountCents, full} or throws Error(friendly message). */
function checkRefund(order, amount, reason) {
  if (!["paid", "in_production", "shipped", "delivered", "partially_refunded"].includes(order.status)) {
    throw new Error(`An order that is "${STATUS_LABELS[order.status] || order.status}" can't be refunded.`);
  }
  if (!REFUND_REASONS[reason]) throw new Error("Please choose a refund reason.");
  const n = Number(amount);
  if (!Number.isFinite(n) || n <= 0) throw new Error("The refund amount must be more than $0.");
  const c = Math.round(n * 100);
  if (Math.abs(n * 100 - c) > 1e-6) throw new Error("The refund amount can have at most 2 decimals.");
  const left = refundableCents(order);
  if (left <= 0) throw new Error("This order has already been fully refunded.");
  if (c > left) throw new Error(`You can refund at most $${(left / 100).toFixed(2)} (paid minus what was already refunded).`);
  return { amountCents: c, full: c === left };
}

/** Status after refunds: refunded when nothing is left, otherwise partially_refunded. */
function statusAfterRefund(order, newRefundedCents) {
  if (newRefundedCents <= 0) return order.status;
  return newRefundedCents >= paidCents(order) ? "refunded" : "partially_refunded";
}

/**
 * Merges Stripe refund objects into order.refunds (dedup by id). Returns {refunds, added, refundedTotal}.
 * Stripe metadata (reason/note/by) set by adminRefund wins; dashboard refunds get reason "other".
 */
function mergeRefunds(existing, stripeRefunds, at) {
  const list = Array.isArray(existing) ? existing.map((r) => ({ ...r })) : [];
  const added = [];
  for (const sr of stripeRefunds || []) {
    if (!sr || !sr.id) continue;
    const found = list.find((r) => r.id === sr.id);
    if (found) { if (sr.status) found.status = sr.status; continue; }
    const md = sr.metadata || {};
    const entry = {
      id: sr.id, amount: dollars(sr.amount || 0),
      reason: REFUND_REASONS[md.reason] ? md.reason : (sr.reason === "duplicate" ? "duplicate" : "other"),
      note: md.note || (md.by ? "" : "Refunded in the Stripe dashboard"),
      at: sr.created ? new Date(sr.created * 1000).toISOString() : at,
      by: md.by || "stripe-dashboard", status: sr.status || "succeeded",
    };
    list.push(entry); added.push(entry);
  }
  const refundedTotal = dollars(refundedCents({ refunds: list }));
  return { refunds: list, added, refundedTotal };
}

/* ---------- shipping carriers ---------- */
const CARRIERS = {
  usps: { name: "USPS", url: (t) => `https://tools.usps.com/go/TrackConfirmAction?tLabels=${encodeURIComponent(t)}` },
  ups: { name: "UPS", url: (t) => `https://www.ups.com/track?tracknum=${encodeURIComponent(t)}` },
  fedex: { name: "FedEx", url: (t) => `https://www.fedex.com/fedextrack/?trknbr=${encodeURIComponent(t)}` },
  dhl: { name: "DHL", url: (t) => `https://www.dhl.com/us-en/home/tracking/tracking-express.html?tracking-id=${encodeURIComponent(t)}` },
  other: { name: "Carrier", url: () => "" },
};
function trackingUrl(carrier, tracking, given) {
  const c = CARRIERS[carrier];
  if (given && /^https?:\/\//i.test(given)) return given;
  return c && tracking ? c.url(tracking) : "";
}

/* ---------- automatic delivery tracking (see tracking.js) ---------- */
const TRACKING_LABELS = {
  pre_transit: "Label created", in_transit: "In transit", out_for_delivery: "Out for delivery", delivered: "Delivered",
  exception: "Needs attention",
};
/** Public-safe carrier scans: [{at, status, text, location}] (no codes, ZIPs or raw payloads). */
function publicEvents(events) {
  return (Array.isArray(events) ? events : []).slice(0, 20).filter((e) => e && (e.at || e.text))
    .map((e) => ({ at: e.at || null, status: TRACKING_LABELS[e.status] ? e.status : null, text: String(e.text || "").slice(0, 160), location: String(e.location || "").slice(0, 80) }));
}
function trackingFields(f) {
  return {
    trackingStatus: TRACKING_LABELS[f.trackingStatus] ? f.trackingStatus : null,
    trackingStatusLabel: TRACKING_LABELS[f.trackingStatus] || "",
    trackingDetail: String(f.trackingDetail || "").slice(0, 200),
    estimatedDelivery: f.estimatedDelivery || null,
    lastCheckedAt: f.lastCheckedAt || null,
    events: publicEvents(f.events),
  };
}

/* ---------- the customer-safe view ---------- */
function publicItem(it) {
  if (!it) return null;
  switch (it.kind) {
    case "design": return { kind: "design", id: it.id, title: it.title, collection: it.collection, qty: it.qty, unit: it.unit };
    case "photos": return {
      kind: "photos", title: it.title || `Custom photo magnets (${it.packSize})`, packSize: it.packSize, price: it.price, qty: it.qty || 1,
      photoCount: Array.isArray(it.photos) ? it.photos.length : 0,
      frames: Array.isArray(it.photos) ? it.photos.map((p) => ({ frame: p.frame, caption: p.caption || "" })) : [],
    };
    case "package": return { kind: "package", id: it.id, title: it.title, size: it.size, price: it.price, qty: it.qty || 1 };
    case "custom": return { kind: "custom", title: it.title, amount: it.amount };
    default: return null;
  }
}

/**
 * What trackOrder / orderBySession / myOrders / myOrder return. Whitelisted: no uid, email, Stripe ids, fees, admin notes,
 * costs or photo paths. `owner: true` (myOrders / myOrder, the signed-in buyer) adds their own shipping name + address
 * and gift message; the guest views (order number + email, or a Stripe session) only get the city.
 */
function publicOrderView(id, o, { owner = false } = {}) {
  const p = o.pricing || {};
  const s = o.shipping || {};
  const a = s.address || {};
  const f = o.fulfillment || {};
  const view = {
    id,
    number: o.number || null,
    status: o.status,
    statusLabel: STATUS_LABELS[o.status] || o.status,
    createdAt: o.createdAt || null,
    paidAt: o.paidAt || null,
    firstName: firstName(o.name || s.name),
    items: (o.items || []).map(publicItem).filter(Boolean),
    pricing: {
      subtotal: p.subtotal || 0, bundleDiscount: p.bundleDiscount || 0, volumePct: p.volumePct || 0,
      volumeDiscount: p.volumeDiscount || 0, promo: p.promo ? { code: p.promo.code || "", amount: p.promo.amount || 0 } : null,
      shipping: p.shipping || 0, total: p.total || 0, currency: p.currency || "usd",
    },
    shipTo: a.city || a.state ? { city: a.city || "", state: a.state || "", country: a.country || "" } : null,
    fulfillment: f.shippedAt || f.tracking ? {
      carrier: f.carrier || "", carrierName: (CARRIERS[f.carrier] || CARRIERS.other).name, tracking: f.tracking || "",
      url: f.url || "", shippedAt: f.shippedAt || null, deliveredAt: f.deliveredAt || null, ...trackingFields(f),
    } : null,
    timeline: (o.timeline || []).map((t) => ({ at: t.at, status: t.status, text: t.text })),
    refunds: (o.refunds || []).filter((r) => r.status !== "failed" && r.status !== "canceled")
      .map((r) => ({ amount: r.amount, at: r.at, reason: r.reason, reasonLabel: REFUND_REASONS[r.reason] || "Other" })),
    refundedTotal: o.refundedTotal || 0,
  };
  if (owner) {
    view.shipping = s.name || a.line1 ? {
      name: s.name || "",
      address: { line1: a.line1 || "", line2: a.line2 || "", city: a.city || "", state: a.state || "", postal_code: a.postal_code || "", country: a.country || "" },
    } : null;
    view.giftMessage = o.giftMessage || "";
  }
  return view;
}

function firstName(name) { return String(name || "").trim().split(/\s+/)[0] || ""; }

/* ---------- data passed to emails.render(kind, data) ---------- */
function emailItems(o) {
  const base = siteUrl();
  // the stored item fields (photos with frame/caption, price, ...) plus lineTotal and a JPG thumbnail
  return (o.items || []).map((it) => {
    if (it.kind === "design") {
      const slug = String(it.id || "").split("/").pop();
      return { ...it, lineTotal: dollars(cents(it.unit) * it.qty), thumb: `${base}/assets/email/thumbs/${it.collection}/${slug}.jpg` };
    }
    if (it.kind === "photos") {
      const first = (it.photos && it.photos[0] && it.photos[0].frame) || "none";
      // photos as [{frame, caption}] so the emails can draw the frame strip (storage paths stay out of emails)
      const photos = (Array.isArray(it.photos) ? it.photos : []).map((p) => ({ frame: (p && p.frame) || "none", caption: (p && p.caption) || "" }));
      return { ...it, photos, title: it.title || `Custom photo magnets (${it.packSize})`, qty: it.qty || 1, unit: it.price,
        lineTotal: dollars(cents(it.price) * (it.qty || 1)), photoCount: (it.photos || []).length,
        thumb: `${base}/assets/email/thumbs/frames/${first}.jpg` };
    }
    if (it.kind === "package") {
      return { ...it, qty: it.qty || 1, unit: it.price, lineTotal: dollars(cents(it.price) * (it.qty || 1)), thumb: "" };
    }
    return { ...it, qty: 1, unit: it.amount, lineTotal: it.amount, thumb: "" };
  });
}

/** Deep link to an order in the admin. The admin router also accepts the older `#order=<id>`. */
function adminOrderUrl(id) { return `${siteUrl()}/admin/#order/${encodeURIComponent(id)}`; }

/** The shared `order` block every order email gets. */
function emailOrder(id, o) {
  const base = siteUrl();
  const f = o.fulfillment || {};
  return {
    id, number: o.number || "", name: o.name || "", firstName: firstName(o.name), email: o.email || "",
    status: o.status, statusLabel: STATUS_LABELS[o.status] || o.status,
    items: emailItems(o), pricing: o.pricing || {}, shipping: o.shipping || null, giftMessage: o.giftMessage || "",
    notes: o.notes || "", createdAt: o.createdAt || null, paidAt: o.paidAt || null, refundedTotal: o.refundedTotal || 0,
    fulfillment: { carrier: f.carrier || "", carrierName: (CARRIERS[f.carrier] || CARRIERS.other).name, tracking: f.tracking || "",
      url: f.url || "", shippedAt: f.shippedAt || null, deliveredAt: f.deliveredAt || null, ...trackingFields(f) },
    links: {
      order: `${base}/order.html?id=${encodeURIComponent(id)}`,
      track: `${base}/track.html?number=${encodeURIComponent(o.number || "")}&email=${encodeURIComponent(o.email || "")}`,
      review: `${base}/order.html?id=${encodeURIComponent(id)}#review`,
      shop: `${base}/shop.html`,
      admin: adminOrderUrl(id),
    },
  };
}

module.exports = {
  STATUSES, STATUS_LABELS, TIMELINE_TEXT, TRANSITIONS, MANUAL_TARGETS, canTransition, manualStatusError,
  formatOrderNumber, nextOrderNumber, normalizeOrderNumber, FIRST_NUMBER,
  REFUND_REASONS, paidCents, refundedCents, refundableCents, checkRefund, statusAfterRefund, mergeRefunds,
  CARRIERS, trackingUrl, publicOrderView, publicItem, emailOrder, emailItems, firstName, adminOrderUrl,
  TRACKING_LABELS, publicEvents,
};
