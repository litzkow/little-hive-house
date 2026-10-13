"use strict";
/* createCheckout, orderBySession, trackOrder and completeCheckout (shared with the webhook). */

const { fail, need, env, siteUrl, mailAdmin, nowIso, AppError } = require("./config");
const deps = require("./deps");
const stripe = require("./stripe");
const mail = require("./mail");
const { priceCart, allocate, dollars, cents } = require("./pricing");
const O = require("./orders");
const U = require("./util");
let printsheetMod = null;
const printsheet = () => (printsheetMod = printsheetMod || require("./printsheet"));   // lazy: only paid orders need it

/* Sales tax: Stripe Tax computes it from the shipping address and adds it on top of our prices.
   STRIPE_TAX=off turns it off; otherwise we ask for it and fall back to no tax if Stripe Tax isn't set up yet. */
const TAX_GOODS = "txcd_99999999";      // General - Tangible Goods
const TAX_SHIPPING = "txcd_92010001";   // Shipping
function taxWanted() { return String(env("STRIPE_TAX") || "").toLowerCase() !== "off"; }

/* Charge on ship (the owners' choice, Oct 2026): checkout only authorizes the card ("capture_method: manual"); the money
   is captured when the order is marked shipped or with "Charge now" (payments.js). CAPTURE=now switches back to
   charging at checkout. Card holds last about 7 days; payments.checkHolds() warns the owners before they end. */
function chargeOnShip() { return String(env("CAPTURE") || "").toLowerCase() !== "now"; }
const HOLD_TEXT = "Your card is authorized now and charged only when your order ships.";
function isTaxSetupError(err) {
  if (!err || !(err.status >= 400 && err.status < 500)) return false;
  return /tax/i.test(`${err.message || ""} ${err.code || ""} ${err.param || ""}`);
}

const PHOTO_PATH = /^uploads\/([^/]+)\/([A-Za-z0-9_-]{1,64})\/(\d{1,3})\.(jpe?g|png|heic|heif|webp)$/i;

/** Stripe line items whose amounts add up to the discounted goods total. */
function stripeLineItems(priced, base = siteUrl(), tax = false) {
  const shares = allocate(priced.lines, priced.totals);
  return priced.lines.map((l, i) => {
    const { net, discount } = shares[i];
    const product = { name: l.name.slice(0, 240) };
    if (l.kind === "design") {
      const slug = String(l.id).split("/").pop();
      product.images = [`${base}/assets/email/thumbs/${l.collection}/${slug}.jpg`];
      product.description = "2 × 2 in magnet";
    } else if (l.kind === "photos") {
      product.description = `${l.count} custom photo magnets, 2 × 2 in`;
    } else if (l.kind === "package") {
      product.description = `${l.count} custom magnets. We email you about your design after checkout.`;
    }
    if (tax) product.tax_code = TAX_GOODS;
    if (discount > 0) product.description = `${product.description ? product.description + " · " : ""}bundle and big-order savings included`;
    if (net % l.qty === 0) {
      return { price_data: { currency: "usd", unit_amount: net / l.qty, product_data: product, ...(tax ? { tax_behavior: "exclusive" } : {}) }, quantity: l.qty };
    }
    product.name = `${l.name} × ${l.qty}`.slice(0, 240);
    return { price_data: { currency: "usd", unit_amount: net, product_data: product, ...(tax ? { tax_behavior: "exclusive" } : {}) }, quantity: 1 };
  });
}

function sessionParams({ orderId, priced, email, tax = false }) {
  const base = siteUrl();
  const ship = priced.totals.ship;
  const p = {
    mode: "payment",
    line_items: stripeLineItems(priced, base, tax),
    shipping_address_collection: { allowed_countries: ["US", "CA"] },
    shipping_options: [{
      shipping_rate_data: {
        type: "fixed_amount", fixed_amount: { amount: ship, currency: "usd" },
        display_name: ship ? "Standard shipping" : "Free shipping",
        delivery_estimate: { minimum: { unit: "business_day", value: 3 }, maximum: { unit: "business_day", value: 10 } },
        ...(tax ? { tax_behavior: "exclusive", tax_code: TAX_SHIPPING } : {}),
      },
    }],
    allow_promotion_codes: true,
    client_reference_id: orderId,
    metadata: { orderId },
    payment_intent_data: { metadata: { orderId }, description: "Little Hive House order", ...(chargeOnShip() ? { capture_method: "manual" } : {}) },
    ...(chargeOnShip() ? { custom_text: { submit: { message: HOLD_TEXT } } } : {}),
    success_url: `${base}/thank-you.html?order=${orderId}&session={CHECKOUT_SESSION_ID}`,
    cancel_url: `${base}/shop.html?checkout=canceled`,
  };
  if (tax) p.automatic_tax = { enabled: true };
  if (email) p.customer_email = email;
  return p;
}

async function checkPhotos(items, auth) {
  const photos = [];
  items.filter((it) => it.kind === "photos").forEach((it) => it.photos.forEach((ph, n) => photos.push({ ph, n })));
  if (!photos.length) return;
  if (!auth || !auth.uid) fail("unauthenticated", "Please wait for your photos to upload, then try again.");
  for (const { ph, n } of photos) {
    const m = PHOTO_PATH.exec(ph.path || "");
    if (!m || m[1] !== auth.uid) fail("invalid-argument", `Photo ${n + 1} didn't upload correctly. Please remove it and add it again.`);
  }
  let bucket;
  try { bucket = deps.bucket(); } catch (err) { console.warn("[checkout] storage unavailable, skipping photo check", err.message); return; }
  const checks = await Promise.all(photos.map(({ ph }) => bucket.file(ph.path).exists().then((r) => r[0]).catch(() => true)));
  const missing = checks.map((ok, i) => (ok ? 0 : i + 1)).filter(Boolean);
  if (missing.length) fail("failed-precondition", `Photo ${missing.join(", ")} didn't finish uploading. Please try again.`);
}

/** createCheckout({cart, email?, giftMessage?, notes?, marketing?}) -> {url, orderId} */
async function createCheckout(data, auth) {
  data = data || {};
  need("STRIPE_SECRET_KEY");
  const priced = priceCart(data.cart);
  const tokenEmail = auth && !U.isAnonymous(auth) && auth.token && auth.token.email ? auth.token.email : "";
  const email = U.cleanEmail(data.email || tokenEmail, { required: false });
  await checkPhotos(priced.items, auth);

  const db = deps.db();
  const ref = db.collection("orders").doc();
  const at = nowIso();
  const anon = U.isAnonymous(auth);
  const order = {
    number: null, uid: auth && auth.uid && !anon ? auth.uid : null, guestUid: auth && anon ? auth.uid : null,
    email, name: "", status: "pending", items: priced.items, pricing: priced.pricing, shipping: null,
    giftMessage: U.text(data.giftMessage, 300), notes: U.text(data.notes, 1000), marketing: data.marketing === true,
    stripe: { sessionId: null, paymentIntent: null, customer: null, fee: null },
    fulfillment: null, refunds: [], refundedTotal: 0, adminNotes: [],
    timeline: [{ at, status: "pending", text: O.TIMELINE_TEXT.pending }],
    emails: { confirmation: null, shipped: null, delivered: null, refund: [] },
    source: "site", createdAt: at, paidAt: null, updatedAt: at,
  };
  await ref.set(order);
  let session;
  let taxOn = taxWanted();
  try {
    try {
      session = await stripe.request("POST", "/checkout/sessions", sessionParams({ orderId: ref.id, priced, email, tax: taxOn }),
        { idempotencyKey: `checkout-${ref.id}${taxOn ? "" : "-notax"}` });
    } catch (err) {
      if (!taxOn || !isTaxSetupError(err)) throw err;
      // Stripe Tax isn't switched on in the Stripe dashboard yet: take the order anyway, without tax, and tell the owners.
      console.warn("[checkout] Stripe Tax unavailable, continuing without tax:", err.message);
      taxOn = false;
      session = await stripe.request("POST", "/checkout/sessions", sessionParams({ orderId: ref.id, priced, email, tax: false }),
        { idempotencyKey: `checkout-${ref.id}-notax` });
    }
  } catch (err) {
    await ref.delete().catch(() => {});
    throw stripe.friendly(err, "opening checkout");
  }
  const upd = { "stripe.sessionId": session.id, "pricing.taxCalculated": taxOn, updatedAt: nowIso() };
  if (!taxOn && taxWanted()) upd.adminNotes = [{ at: nowIso(), by: "system", text: "Sales tax was not charged: Stripe Tax is not set up in the Stripe dashboard yet." }];
  await ref.update(upd);
  return { url: session.url, orderId: ref.id };
}

/* ---------- payment confirmed ---------- */
/** When the card hold ends (ISO), from the expanded PaymentIntent's charge, or null. */
function captureBefore(pi) {
  const ch = pi && typeof pi.latest_charge === "object" ? pi.latest_charge : null;
  const t = ch && ch.payment_method_details && ch.payment_method_details.card && ch.payment_method_details.card.capture_before;
  return Number.isFinite(t) ? new Date(t * 1000).toISOString() : null;
}
async function retrieveSession(id) {
  return stripe.request("GET", `/checkout/sessions/${encodeURIComponent(id)}`,
    { expand: ["total_details.breakdown", "payment_intent.latest_charge.balance_transaction"] });
}

async function promoFromSession(session) {
  const td = session.total_details || {};
  const amount = td.amount_discount || 0;
  if (!amount) return null;
  let code = "";
  const ds = (td.breakdown && td.breakdown.discounts) || [];
  for (const d of ds) {
    const disc = d.discount || {};
    const pc = disc.promotion_code;
    if (pc && typeof pc === "object" && pc.code) { code = pc.code; break; }
    if (typeof pc === "string") {
      try { code = (await stripe.request("GET", `/promotion_codes/${encodeURIComponent(pc)}`)).code || ""; } catch (e) { /* keep going */ }
      if (code) break;
    }
    if (disc.coupon && disc.coupon.name) code = code || disc.coupon.name;
  }
  return { code, amount: dollars(amount) };
}

function feeFromSession(session) {
  const pi = session.payment_intent;
  const ch = pi && typeof pi === "object" ? pi.latest_charge : null;
  const bt = ch && typeof ch === "object" ? ch.balance_transaction : null;
  return bt && typeof bt === "object" && Number.isFinite(bt.fee) ? dollars(bt.fee) : null;
}

function addressFromSession(session) {
  const sd = session.shipping_details || (session.collected_information && session.collected_information.shipping_details) || null;
  const cd = session.customer_details || {};
  const a = (sd && sd.address) || cd.address || {};
  return {
    name: (sd && sd.name) || cd.name || "",
    phone: cd.phone || "",
    address: {
      line1: a.line1 || "", line2: a.line2 || "", city: a.city || "", state: a.state || "",
      postal_code: a.postal_code || "", country: a.country || "",
    },
  };
}

async function findOrderIdForSession(session) {
  const id = session.client_reference_id || (session.metadata && session.metadata.orderId);
  if (id) return id;
  const db = deps.db();
  const q = session.payment_link
    ? await db.collection("orders").where("stripe.paymentLink", "==", session.payment_link).limit(1).get()
    : await db.collection("orders").where("stripe.sessionId", "==", session.id).limit(1).get();
  return q.empty ? null : q.docs[0].id;
}

/**
 * Marks an order paid from a (retrieved, expanded) Checkout Session. Safe to call many times:
 * only the first call assigns the order number and sends emails. Returns {orderId, status, newlyPaid}.
 */
async function completeCheckout(session) {
  const orderId = await findOrderIdForSession(session);
  if (!orderId) { console.warn("[checkout] no order for session", session.id); return { orderId: null, newlyPaid: false }; }
  const piObj = session.payment_intent && typeof session.payment_intent === "object" ? session.payment_intent : null;
  // charge on ship: Checkout says "unpaid" but the card is authorized (the PaymentIntent waits for capture)
  const authorized = session.payment_status === "unpaid" && !!piObj && piObj.status === "requires_capture";
  const paid = authorized || session.payment_status === "paid" || session.payment_status === "no_payment_required";
  const db = deps.db();
  const ref = db.collection("orders").doc(orderId);
  if (!paid) {
    await ref.update({ "stripe.sessionId": session.id, updatedAt: nowIso() }).catch(() => {});
    return { orderId, status: "pending", newlyPaid: false };
  }
  const promo = await promoFromSession(session);
  const fee = authorized ? null : feeFromSession(session);
  const ship = addressFromSession(session);
  const holdUntil = authorized ? captureBefore(piObj) : null;
  const pi = session.payment_intent;
  const piId = pi && typeof pi === "object" ? pi.id : pi || null;
  const email = ((session.customer_details && session.customer_details.email) || session.customer_email || "").toLowerCase();
  const amountTotal = Number.isFinite(session.amount_total) ? session.amount_total : null;
  const taxCents = Number.isFinite(session.total_details && session.total_details.amount_tax) ? session.total_details.amount_tax : 0;

  let result = { orderId, status: null, newlyPaid: false };
  let after = null;
  await db.runTransaction(async (tx) => {
    const snap = await tx.get(ref);
    if (!snap.exists) { result.status = null; return; }
    const o = snap.data();
    if (o.status !== "pending") { result.status = o.status; return; }
    const cRef = db.collection("meta").doc("counters");
    const cSnap = await tx.get(cRef);
    const n = O.nextOrderNumber(cSnap.exists ? cSnap.data().orderNumber : undefined);
    const at = nowIso();
    const pricing = { ...(o.pricing || {}) };
    if (promo) pricing.promo = promo;
    pricing.tax = dollars(taxCents);          // sales tax the customer paid: belongs to the state, not to the shop
    pricing.taxState = taxCents > 0 ? (ship.address.state || "") : "";
    pricing.taxCountry = taxCents > 0 ? (ship.address.country || "") : "";
    const notes = Array.isArray(o.adminNotes) ? o.adminNotes.slice() : [];
    if (amountTotal !== null) {
      const expected = cents(pricing.total || 0) - (promo ? cents(promo.amount) : 0) + taxCents;
      if (Math.abs(expected - amountTotal) > 0) {
        notes.push({ at, by: "system", text: `Check: we expected $${(expected / 100).toFixed(2)} but Stripe charged $${(amountTotal / 100).toFixed(2)}.` });
      }
      pricing.total = dollars(amountTotal);
    }
    const update = {
      status: "paid", number: O.formatOrderNumber(n), paidAt: at, updatedAt: at,
      payment: authorized ? { state: "authorized", authorizedAt: at, captureBefore: holdUntil || new Date(Date.parse(at) + 7 * 86400000).toISOString() }
        : { state: "captured", capturedAt: at },
      email: o.email || email, name: ship.name || o.name || "",
      shipping: ship, pricing, adminNotes: notes,
      stripe: { ...(o.stripe || {}), sessionId: session.id, paymentIntent: piId, customer: session.customer || null, fee },
      timeline: (o.timeline || []).concat([{ at, status: "paid", text: authorized ? O.TIMELINE_TEXT.authorized : O.TIMELINE_TEXT.paid }]),
    };
    tx.set(cRef, { orderNumber: n }, { merge: true });
    tx.update(ref, update);
    after = { ...o, ...update };
    result = { orderId, status: "paid", newlyPaid: true };
  });

  if (result.newlyPaid && after) {
    const data = { order: O.emailOrder(orderId, after) };
    const sent = await mail.send({ to: after.email, kind: "order_confirmation", data });
    if (!sent.skipped) await ref.update({ "emails.confirmation": nowIso() }).catch(() => {});
    // the print-ready PDF for the owners: saved on the order and attached to the new-order alert (never blocks the order)
    const ps = await printsheet().tryGenerate(ref, orderId, after);
    const attach = !!(ps && ps.pdf.length <= mail.MAX_ATTACHMENT_BYTES);
    const adminData = { ...data, printSheet: ps ? { ...ps.meta, attached: attach } : null };
    await mail.send({ to: mailAdmin(), kind: "admin_new_order", data: adminData, replyTo: after.email || undefined,
      attachments: attach ? [{ filename: printsheet().fileName(after), content: ps.pdf, contentType: "application/pdf" }] : undefined });
    if (after.marketing && after.email) {
      await db.collection("subscribers").doc(U.emailKey(after.email))
        .set({ email: after.email, at: nowIso(), source: "checkout" }, { merge: true }).catch(() => {});
    }
  }
  return result;
}

/** orderBySession({orderId, sessionId}) -> public view, for thank-you.html. */
async function orderBySession(data, auth, rawRequest) {
  const orderId = U.text(data && data.orderId, 64, { required: true, field: "the order" });
  const sessionId = U.text(data && data.sessionId, 255, { required: true, field: "the session" });
  if (!/^[A-Za-z0-9]+$/.test(orderId) || !/^cs_[A-Za-z0-9_]+$/.test(sessionId)) fail("not-found", "We couldn't find that order.");
  await U.rateLimit("orderBySession", U.clientIp(rawRequest) || orderId, 60, 600);
  const ref = deps.db().collection("orders").doc(orderId);
  let snap = await ref.get();
  if (!snap.exists) fail("not-found", "We couldn't find that order.");
  let o = snap.data();
  const known = o.stripe && o.stripe.sessionId === sessionId;
  if (!known || o.status === "pending") {
    let session = null;
    try { session = await retrieveSession(sessionId); } catch (err) {
      if (!known) throw err instanceof AppError ? err : new AppError("not-found", "We couldn't find that order.");
    }
    if (session) {
      if ((session.client_reference_id || (session.metadata && session.metadata.orderId)) !== orderId) fail("not-found", "We couldn't find that order.");
      if (o.status === "pending") {          // the webhook may still be on its way: confirm right now
        await completeCheckout(session);
        snap = await ref.get(); o = snap.data();
      }
    }
  }
  return O.publicOrderView(orderId, o);
}

/** trackOrder({number, email}) -> public view (guest tracking). */
async function trackOrder(data, auth, rawRequest) {
  const number = O.normalizeOrderNumber(data && data.number);
  const email = U.cleanEmail(data && data.email);
  if (!number) fail("invalid-argument", "Order numbers look like LHH-1001.");
  await U.rateLimit("trackOrder", U.clientIp(rawRequest) || email, 30, 900);
  const q = await deps.db().collection("orders").where("number", "==", number).limit(1).get();
  const doc = q.empty ? null : q.docs[0];
  if (!doc || String(doc.data().email || "").toLowerCase() !== email) {
    fail("not-found", "We couldn't find an order with that number and email. Please check both and try again.");
  }
  return O.publicOrderView(doc.id, doc.data());
}

module.exports = { chargeOnShip, HOLD_TEXT, captureBefore, TAX_GOODS, TAX_SHIPPING, taxWanted, isTaxSetupError, createCheckout, completeCheckout, orderBySession, trackOrder, retrieveSession, sessionParams, stripeLineItems, PHOTO_PATH, addressFromSession, feeFromSession };
