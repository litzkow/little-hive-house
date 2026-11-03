"use strict";
/* Returns, on the customer's own, from the site (return.html), as returns.html promises:
   - "Something's wrong" (damaged, misprinted, wrong item): any magnet, within 30 days of delivery, with 1 to 3 photos.
     The customer picks a reprint or a refund; the owners approve it with one tap in the Hive Admin (adminReturnDecide).
   - "Changed my mind": ready-made designs only, unused, within 30 days of delivery. A prepaid USPS return label is made
     at once (Shippo, is_return: charged only if it is used; with a QR code to show at the Post Office, no printer needed).
     The return shipping comes out of the refund, and the page shows the amount before the customer confirms.
     When USPS says the parcel reached the shop, the refund goes out by itself (checkReturns, every 2 hours).
   Each request is returns/{id}. The customer proves the order with its number and email, like track.html. */

const { fail, env, nowIso, mailAdmin } = require("./config");
const deps = require("./deps");
const U = require("./util");
const O = require("./orders");
const mail = require("./mail");
const { cents, dollars } = require("./pricing");

const WINDOW_DAYS = 30;
/* an order shipped but never marked delivered: count it delivered this many days after it shipped */
const ASSUME_DELIVERED_DAYS = 5;
const ACTIVE = ["requested", "label_sent", "in_transit", "refunded", "reprinting", "received"];
const REASONS = { damaged: "Arrived damaged", misprint: "Printing problem", wrong_item: "Wrong item", missing: "Something missing", other: "Something else" };
const RETURN_PHOTO = /^returns\/([^/]+)\/([A-Za-z0-9_-]{1,64})\/(\d)\.jpg$/;
const LABEL_DAYS = 60;             // follow an unused return label this long, then give up
const SHIPPO = "https://api.goshippo.com";

/* ---------- the order and what can come back ---------- */
async function findOrder(data) {
  const number = O.normalizeOrderNumber(data && data.number);
  const email = U.cleanEmail(data && data.email);
  if (!number) fail("invalid-argument", "Order numbers look like LHH-1001.");
  const q = await deps.db().collection("orders").where("number", "==", number).limit(1).get();
  const doc = q.empty ? null : q.docs[0];
  if (!doc || String(doc.data().email || "").toLowerCase() !== email) {
    fail("not-found", "We couldn't find an order with that number and email. Please check both and try again.");
  }
  return { ref: doc.ref, id: doc.id, order: doc.data(), email };
}

/** When the 30 days start: delivery (or a few days after it shipped, when nobody marked it delivered). */
function windowOf(order, now = Date.now()) {
  const f = order.fulfillment || {};
  const deliveredAt = Date.parse(f.deliveredAt || "");
  const shippedAt = Date.parse(f.shippedAt || "");
  const start = Number.isFinite(deliveredAt) ? deliveredAt : Number.isFinite(shippedAt) ? shippedAt + ASSUME_DELIVERED_DAYS * 86400000 : null;
  if (start == null) return { shipped: false, open: false, endsAt: null };
  const end = start + WINDOW_DAYS * 86400000;
  return { shipped: true, open: now <= end, endsAt: new Date(end).toISOString() };
}

/** What each paid dollar of goods is worth after discounts, with its sales tax (shipping left out). */
function goodsFactor(order) {
  const p = order.pricing || {};
  const subtotal = cents(p.subtotal || 0);
  const goodsPaid = cents(p.total || 0) - cents(p.shipping || 0);
  return subtotal > 0 && goodsPaid > 0 ? goodsPaid / subtotal : 0;
}

/** The order's items as return lines: magnets that can come back, what each is worth, what's already in a return. */
function lines(order, returns = []) {
  const f = goodsFactor(order);
  const taken = {};
  returns.filter((r) => ACTIVE.includes(r.status)).forEach((r) => (r.lines || []).forEach((l) => { taken[l.index] = (taken[l.index] || 0) + (Number(l.qty) || 0); }));
  return (order.items || []).map((it, index) => {
    let magnets = 0, listEach = 0, title = it.title || "", collection = "";
    if (it.kind === "design") { magnets = Number(it.qty) || 0; listEach = Number(it.unit) || 0; collection = it.collection || ""; }
    else if (it.kind === "photos") { const n = Number(it.packSize) || (it.photos || []).length || 0; magnets = n * (Number(it.qty) || 1); listEach = n ? (Number(it.price) || 0) / n : 0; title = title || `Custom photo magnets (${n})`; }
    else if (it.kind === "package") { const n = Number(it.size) || 0; magnets = n * (Number(it.qty) || 1); listEach = n ? (Number(it.price) || 0) / n : 0; }
    else return null;
    if (!magnets) return null;
    return {
      index, kind: it.kind, title, collection, designId: it.kind === "design" ? it.id || "" : "",
      magnets, left: Math.max(0, magnets - (taken[index] || 0)),
      valueEach: Math.round(listEach * f * 100) / 100,
      changeMind: it.kind === "design",       // ready-made designs only; photos and packages are made for this customer
    };
  }).filter(Boolean);
}

async function returnsOf(orderId) {
  const q = await deps.db().collection("returns").where("orderId", "==", orderId).get();
  return q.docs.map((d) => ({ id: d.id, ...d.data() }));
}

function publicReturn(r) {
  return {
    id: r.id, kind: r.kind, status: r.status, createdAt: r.createdAt, wants: r.wants || null,
    lines: (r.lines || []).map((l) => ({ title: l.title, qty: l.qty })),
    refund: r.refund ? { amount: r.refund.amount, at: r.refund.at } : null,
    estimate: r.estimate || null,
    label: r.label ? { url: r.label.url, qr: r.label.qr || null, tracking: r.label.tracking, trackUrl: O.trackingUrl("usps", r.label.tracking) } : null,
  };
}

/** returnLookup({number, email}) -> the order, what can be returned and the returns already started. */
async function returnLookup(data, auth, rawRequest) {
  await U.rateLimit("returnLookup", U.clientIp(rawRequest) || (data && data.email), 30, 900);
  const { id, order } = await findOrder(data);
  const existing = await returnsOf(id);
  const w = windowOf(order);
  return {
    order: { number: order.number, firstName: O.firstName(order.name), status: order.status, deliveredAt: (order.fulfillment || {}).deliveredAt || null },
    window: w, lines: w.open ? lines(order, existing) : [],
    returns: existing.sort((a, b) => String(b.createdAt).localeCompare(String(a.createdAt))).map(publicReturn),
  };
}

/* ---------- picking lines ---------- */
function pick(order, existing, wanted, kind) {
  const avail = {};
  lines(order, existing).forEach((l) => { avail[l.index] = l; });
  const out = [];
  (Array.isArray(wanted) ? wanted : []).forEach((w) => {
    const l = avail[Number(w && w.index)], q = Math.floor(Number(w && w.qty));
    if (!l || !(q > 0)) return;
    if (kind === "changed_mind" && !l.changeMind) fail("invalid-argument", "Photo magnets and custom packages are made just for you, so they can't be returned if you change your mind.");
    if (q > l.left) fail("invalid-argument", `You can return at most ${l.left} of “${l.title}”.`);
    out.push({ index: l.index, kind: l.kind, title: l.title, collection: l.collection, designId: l.designId, qty: q, valueEach: l.valueEach });
  });
  if (!out.length) fail("invalid-argument", "Choose at least one magnet.");
  return out;
}
const valueOf = (ls) => dollars(ls.reduce((t, l) => t + Math.round(l.valueEach * 100) * l.qty, 0));
const magnetsOf = (ls) => ls.reduce((t, l) => t + l.qty, 0);

/* ---------- the USPS return label (Shippo) ---------- */
async function shippo(path, body) {
  const k = env("SHIPPO_API_KEY");
  if (!k) fail("failed-precondition", "Return labels aren't available right now. Please email us and we'll send one.");
  const res = await globalThis.fetch(`${SHIPPO}${path}`, { method: "POST", headers: { Authorization: `ShippoToken ${k}`, "Content-Type": "application/json", Accept: "application/json" }, body: JSON.stringify(body) });
  let json = null;
  try { json = await res.json(); } catch (e) { json = null; }
  if (!res.ok) { console.error("[returns] Shippo", path, res.status, JSON.stringify(json).slice(0, 400)); fail("aborted", "We couldn't make the return label right now. Please try again in a few minutes."); }
  return json || {};
}
async function returnRate(order, magnets) {
  const labels = require("./labels");
  const s = await labels._internal.settings();
  const st = { packageBaseOz: 2.5, magnetOz: 0.45, ...s };
  const oz = labels.prudentOz(Number(st.packageBaseOz) + magnets * Number(st.magnetOz));
  const shipment = await shippo("/shipments/", {
    address_from: labels._internal.fromAddress(s), address_to: labels._internal.toAddress(order), parcels: [labels._internal.parcel(s, oz)],
    extra: { is_return: true, qr_code_requested: true }, async: false,
  });
  const rate = labels._internal.pickRate(shipment.rates);
  if (!rate) fail("aborted", "USPS didn't give us a return price for this address. Please email us and we'll sort it out.");
  return { rateId: rate.object_id, amount: Math.round(Number(rate.amount) * 100) / 100, oz };
}

/** returnQuote({number, email, lines}) -> what a change-of-mind return pays back, before the label is made. */
async function returnQuote(data, auth, rawRequest) {
  await U.rateLimit("returnQuote", U.clientIp(rawRequest) || (data && data.email), 20, 900);
  const { id, order } = await findOrder(data);
  if (!windowOf(order).open) fail("failed-precondition", "The 30 days to return this order have passed.");
  const ls = pick(order, await returnsOf(id), data.lines, "changed_mind");
  const value = valueOf(ls), r = await returnRate(order, magnetsOf(ls));
  return { value, labelCost: r.amount, refund: Math.max(0, dollars(cents(value) - cents(r.amount))) };
}

/* ---------- starting a return ---------- */
async function returnStart(data, auth, rawRequest) {
  data = data || {};
  await U.rateLimit("returnStart", U.clientIp(rawRequest) || data.email, 8, 3600);
  const { id, order, email } = await findOrder(data);
  if (!windowOf(order).open) fail("failed-precondition", "The 30 days to start a return for this order have passed. If something is wrong, please write to us.");
  const kind = data.kind === "changed_mind" ? "changed_mind" : "problem";
  const existing = await returnsOf(id);
  const ls = pick(order, existing, data.lines, kind);
  const db = deps.db(), ref = db.collection("returns").doc(), at = nowIso();
  const base = { orderId: id, number: order.number, email, name: order.name || "", kind, lines: ls, value: valueOf(ls), magnets: magnetsOf(ls),
    note: U.text(data.note, 1000), createdAt: at, updatedAt: at, timeline: [] };

  if (kind === "problem") {
    const reason = REASONS[data.reason] ? data.reason : "other";
    const wants = data.wants === "reprint" ? "reprint" : "refund";
    const photos = (Array.isArray(data.photos) ? data.photos : []).slice(0, 3).map(String);
    if (!photos.length) fail("invalid-argument", "Please add at least one photo of the problem.");
    if (!auth || !auth.uid) fail("unauthenticated", "Please wait for your photos to upload, then try again.");
    for (const p of photos) { const m = RETURN_PHOTO.exec(p); if (!m || m[1] !== auth.uid) fail("invalid-argument", "A photo didn't upload correctly. Please add it again."); }
    const r = { ...base, reason, reasonLabel: REASONS[reason], wants, photos, status: "requested", timeline: [{ at, status: "requested", text: "Return requested" }] };
    await ref.set(r);
    await mail.send({ to: email, kind: "return_update", data: { mode: "received", ret: { id: ref.id, ...r }, order: O.emailOrder(id, order) } });
    await mail.send({ to: mailAdmin(), kind: "admin_return", data: { ret: { id: ref.id, ...r }, order: O.emailOrder(id, order) }, replyTo: email });
    await require("./push").notifyAdmins("admin_return", { ret: { id: ref.id, ...r } }).catch(() => {});
    return { ok: true, id: ref.id, status: "requested" };
  }

  if (data.unused !== true) fail("invalid-argument", "Please confirm the magnets are unused and in their packaging.");
  const rate = await returnRate(order, base.magnets);
  const estimate = { value: base.value, labelCost: rate.amount, refund: Math.max(0, dollars(cents(base.value) - cents(rate.amount))) };
  const tx = await shippo("/transactions/", { rate: rate.rateId, label_file_type: "PDF_4x6", async: false, metadata: `return ${ref.id} order ${id}` });
  if (tx.status !== "SUCCESS" || !tx.tracking_number || !tx.label_url) {
    console.error("[returns] label", tx.status, JSON.stringify(tx.messages || []).slice(0, 500));
    fail("aborted", "We couldn't make the return label right now. Nothing was charged. Please try again in a few minutes.");
  }
  const label = { url: tx.label_url, qr: tx.qr_code_url || null, tracking: tx.tracking_number, transaction: tx.object_id || "", cost: rate.amount, oz: rate.oz, at };
  const r = { ...base, reason: "changed_mind", reasonLabel: "Changed their mind", estimate, label, status: "label_sent",
    timeline: [{ at, status: "label_sent", text: "Return label sent" }] };
  await ref.set(r);
  await mail.send({ to: email, kind: "return_update", data: { mode: "label", ret: { id: ref.id, ...r }, order: O.emailOrder(id, order) } });
  await require("./push").notifyAdmins("admin_return", { ret: { id: ref.id, ...r } }).catch(() => {});
  return { ok: true, id: ref.id, status: "label_sent", label: publicReturn({ id: ref.id, ...r }).label, estimate };
}

/* ---------- the owners decide (problems), or refund a change-of-mind return by hand ---------- */
async function loadReturn(returnId) {
  const id = U.text(returnId, 64, { required: true, field: "the return" });
  if (!/^[A-Za-z0-9_-]+$/.test(id)) fail("invalid-argument", "That return id is not valid.");
  const ref = deps.db().collection("returns").doc(id);
  const snap = await ref.get();
  if (!snap.exists) fail("not-found", "We couldn't find that return.");
  return { ref, id, ret: snap.data() };
}
async function orderOf(ret) {
  const ref = deps.db().collection("orders").doc(ret.orderId);
  const snap = await ref.get();
  if (!snap.exists) fail("not-found", "The order of this return is gone.");
  return { ref, id: ret.orderId, order: snap.data() };
}
const step = (ret, status, text, extra = {}) => ({ status, updatedAt: nowIso(), timeline: (ret.timeline || []).concat([{ at: nowIso(), status, text }]), ...extra });

async function refundReturn(r, { by, amount }) {
  const o = await orderOf(r.ret);
  const admin = require("./admin");
  const label = r.ret.kind === "changed_mind" ? ` minus ${"$" + Number((r.ret.label && r.ret.label.cost) || 0).toFixed(2)} return shipping` : "";
  const what = `${r.ret.magnets} ${r.ret.magnets === 1 ? "magnet" : "magnets"}`;
  const note = r.ret.kind === "changed_mind" ? `Your return arrived. This is the refund for the ${what} you sent back${label}.` : `For the ${what} that arrived with a problem. You don't need to send anything back.`;
  const res = await admin.refundOrder(o.ref, o.id, o.order, { amount, reason: r.ret.kind === "changed_mind" ? "changed_mind" : r.ret.reason === "wrong_item" ? "wrong_item" : r.ret.reason === "misprint" ? "print_quality" : "damaged", note, by });
  await r.ref.update(step(r.ret, "refunded", `Refunded $${Number(amount).toFixed(2)}`, { refund: { amount: Number(amount), at: nowIso(), by, id: res.refundId || null } }));
  return res;
}

/** A free reprint: a new order with the same magnets (the same photos), at $0, that goes through production as usual. */
async function makeReprint(r, { by, photos }) {
  const o = await orderOf(r.ret);
  const db = deps.db(), nref = db.collection("orders").doc(), at = nowIso();
  const items = [];
  r.ret.lines.forEach((l) => {
    const it = o.order.items[l.index];
    if (!it) return;
    if (it.kind === "design") items.push({ ...it, qty: l.qty });
    else if (it.kind === "photos") {
      // the photos to print again: the ones the owners ticked, or the first ones of the pack
      const chosen = Array.isArray(photos) && photos.length ? photos.map(Number).filter((n) => it.photos[n]) : it.photos.map((p, n) => n).slice(0, l.qty);
      const ph = chosen.map((n) => it.photos[n]);
      if (ph.length) items.push({ ...it, photos: ph, packSize: ph.length, qty: 1, price: 0 });
    } else items.push({ ...it, qty: 1 });
  });
  if (!items.length) fail("failed-precondition", "Nothing to reprint.");
  let number = null;
  await db.runTransaction(async (tx) => {
    const cRef = db.collection("meta").doc("counters");
    const c = await tx.get(cRef);
    const n = O.nextOrderNumber(c.exists ? c.data().orderNumber : undefined);
    number = O.formatOrderNumber(n);
    tx.set(cRef, { orderNumber: n }, { merge: true });
    tx.set(nref, {
      number, uid: o.order.uid || null, guestUid: o.order.guestUid || null, email: o.order.email, name: o.order.name || "", status: "paid",
      items, pricing: { subtotal: 0, shipping: 0, tax: 0, total: 0, currency: "usd", reprint: true }, shipping: o.order.shipping || null,
      giftMessage: "", notes: `Free reprint for ${o.order.number} (return)`, marketing: false,
      stripe: { sessionId: null, paymentIntent: null, customer: null, fee: 0 }, payment: { state: "none" },
      fulfillment: null, refunds: [], refundedTotal: 0, reprintOf: { orderId: o.id, number: o.order.number, returnId: r.id },
      adminNotes: [{ at, by, text: `Free reprint for ${o.order.number}: ${r.ret.reasonLabel || "problem"}.` }],
      timeline: [{ at, status: "paid", text: "Reprint on the way" }],
      emails: { confirmation: null, shipped: null, delivered: null, refund: [] }, source: "reprint", createdAt: at, paidAt: at, updatedAt: at,
    });
  });
  const snap = await nref.get();
  await require("./printsheet").tryGenerate(nref, nref.id, snap.data()).catch((e) => console.warn("[returns] reprint sheet", e.message));
  await r.ref.update(step(r.ret, "reprinting", `Reprint ${number}`, { reprint: { orderId: nref.id, number, at } }));
  return { orderId: nref.id, number };
}

/** adminReturnDecide({returnId, action: refund | reprint | decline, note?, amount?, photos?}) */
async function adminReturnDecide(data, auth) {
  U.requireAdmin(auth);
  const r = await loadReturn(data && data.returnId);
  const by = U.who(auth), action = data && data.action;
  const open = r.ret.kind === "problem" ? ["requested"] : ["label_sent", "in_transit", "received"];
  if (!open.includes(r.ret.status)) fail("failed-precondition", "This return was already handled.");
  const o = await orderOf(r.ret);
  const em = O.emailOrder(o.id, o.order);
  if (action === "decline") {
    const note = U.text(data.note, 1000);
    await r.ref.update(step(r.ret, "declined", "Declined", { declineNote: note }));
    await mail.send({ to: r.ret.email, kind: "return_update", data: { mode: "declined", ret: { id: r.id, ...r.ret, declineNote: note }, order: em } });
    return { ok: true, status: "declined" };
  }
  if (action === "reprint") {
    if (r.ret.kind !== "problem") fail("failed-precondition", "Reprints are for magnets that arrived with a problem.");
    const rep = await makeReprint(r, { by, photos: data.photos });
    await mail.send({ to: r.ret.email, kind: "return_update", data: { mode: "reprint", ret: { id: r.id, ...r.ret }, reprintNumber: rep.number, order: em } });
    return { ok: true, status: "reprinting", reprint: rep };
  }
  if (action === "refund") {
    const auto = r.ret.kind === "changed_mind" ? (r.ret.estimate && r.ret.estimate.refund) : r.ret.value;
    const amount = data.amount !== undefined && data.amount !== "" ? Number(data.amount) : auto;
    if (!(amount > 0)) fail("invalid-argument", "There is nothing to refund on this return.");
    const res = await refundReturn(r, { by, amount: Math.round(amount * 100) / 100 });
    return { ok: true, status: "refunded", amount, emailed: res.emailed };
  }
  fail("invalid-argument", "Choose refund, reprint or decline.");
}

/** adminReturnPhotos({returnId}) -> links to the customer's photos of the problem. */
async function adminReturnPhotos(data, auth) {
  U.requireAdmin(auth);
  const r = await loadReturn(data && data.returnId);
  const bucket = deps.bucket(), admin = require("./admin");
  const urls = await Promise.all((r.ret.photos || []).map((p) => admin._internal.photoUrl(bucket, p)));
  return { ok: true, photos: urls.filter(Boolean) };
}

/* ---------- every 2 hours: follow the return labels; refund when the parcel reaches the shop ---------- */
async function checkReturns({ now = Date.now(), fetchImpl } = {}) {
  if (!env("SHIPPO_API_KEY")) return { checked: 0 };
  const tracking = require("./tracking");
  const q = await deps.db().collection("returns").where("status", "in", ["label_sent", "in_transit"]).get();
  let checked = 0, refunded = 0;
  for (const d of q.docs) {
    const ret = d.data(), r = { ref: d.ref, id: d.id, ret };
    const age = now - Date.parse(ret.createdAt || "");
    try {
      const raw = await tracking.fetchShippo("usps", ret.label.tracking, fetchImpl || fetch);
      const p = tracking.parseShippo(raw);
      checked += 1;
      const st = p && p.status;
      if (st === "delivered") {
        const amount = ret.estimate ? ret.estimate.refund : 0;
        if (amount > 0) { await refundReturn(r, { by: "system", amount }); refunded += 1; }
        else await d.ref.update(step(ret, "received", "Return arrived (nothing left to refund after return shipping)"));
      } else if (st && st !== "pre_transit" && ret.status === "label_sent") {
        await d.ref.update(step(ret, "in_transit", "Customer mailed the return", { mailedAt: nowIso() }));
      } else if (ret.status === "label_sent" && age > LABEL_DAYS * 86400000) {
        await d.ref.update(step(ret, "expired", "Return label never used (no cost)"));
      }
    } catch (err) {
      console.warn("[checkReturns]", d.id, err.message);
    }
  }
  return { checked, refunded };
}

module.exports = { returnLookup, returnQuote, returnStart, adminReturnDecide, adminReturnPhotos, checkReturns,
  windowOf, lines, goodsFactor, pick, REASONS, WINDOW_DAYS, RETURN_PHOTO };
