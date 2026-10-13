"use strict";
/* Phone notifications for the owners (Web Push to the installed Hive Admin app).

   - The VAPID key pair is made once, on first use, with node crypto and kept in meta/vapid. Firestore rules deny every
     client access to meta/*, so the private key never leaves the server (it is not in the repo or in any chat).
   - Each phone that turned notifications on is a doc in adminPush/{sha256(endpoint)} (also server-only) with the
     admin's uid/email and which kinds they want (prefs).
   - mail.send() calls notifyAdmins(kind, data) for every admin_* email, so every alert the shop gets by email also
     arrives as a notification. Never throws: a failed push must not break an order.
   - Sending uses the `web-push` package (VAPID JWT + aes128gcm payload encryption); tests inject a fake sender. */

const crypto = require("crypto");
const deps = require("./deps");
const { nowIso, mailAdmin, fail } = require("./config");
const U = require("./util");

/* email kind -> preference key the owner can switch off in Settings */
const KIND_PREF = {
  admin_new_order: "orders", admin_contact: "messages", admin_quote: "quotes", admin_dispute: "disputes",
  admin_delivery_check: "delivery", admin_payment_hold: "payments", push_test: null,
};
const PREFS = ["orders", "payments", "messages", "quotes", "disputes", "delivery"];
const COLL = "adminPush";

let injectedSender = null;
/** Tests: setSender(async (subscription, payloadString, options) => {...}) ; null restores web-push. */
function setSender(fn) { injectedSender = fn; }
function sender() {
  if (injectedSender) return injectedSender;
  const wp = require("web-push");
  return (sub, payload, opts) => wp.sendNotification(sub, payload, opts);
}

const b64u = (buf) => Buffer.from(buf).toString("base64").replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
const unb64u = (s) => Buffer.from(String(s).replace(/-/g, "+").replace(/_/g, "/"), "base64");

/** A fresh P-256 VAPID pair in the format web-push and PushManager.subscribe use (base64url, public key uncompressed). */
function generateVapidKeys() {
  const { publicKey, privateKey } = crypto.generateKeyPairSync("ec", { namedCurve: "prime256v1" });
  const pub = publicKey.export({ format: "jwk" });
  const priv = privateKey.export({ format: "jwk" });
  return { publicKey: b64u(Buffer.concat([Buffer.from([4]), unb64u(pub.x), unb64u(pub.y)])), privateKey: priv.d };
}

let cachedKeys = null;
async function vapidKeys() {
  if (cachedKeys) return cachedKeys;
  const ref = deps.db().collection("meta").doc("vapid");
  const snap = await ref.get();
  if (snap.exists && snap.data().publicKey && snap.data().privateKey) return (cachedKeys = snap.data());
  const keys = { ...generateVapidKeys(), createdAt: nowIso() };
  try {
    await ref.create(keys);
    cachedKeys = keys;
  } catch (err) {                       // another instance made them first: use theirs
    const again = await ref.get();
    cachedKeys = again.data();
  }
  return cachedKeys;
}
function resetCache() { cachedKeys = null; }

const money = (n) => `$${Number(n || 0).toFixed(2)}`;
const clip = (s, n) => { const t = String(s || "").replace(/\s+/g, " ").trim(); return t.length > n ? t.slice(0, n - 1) + "…" : t; };
const firstName = (s) => clip(String(s || "").split(/\s+/)[0], 30);

function magnetsOf(items) {
  return (items || []).reduce((n, it) => {
    const q = Number(it.qty) || 1;
    if (it.kind === "design") return n + q;
    if (it.kind === "photos") return n + (Number(it.packSize) || (it.photos || []).length || 0) * q;
    if (it.kind === "package") return n + (Number(it.count || it.size) || 0) * q;
    if (it.kind === "custom") return n + (Number(it.magnets) || 0);
    return n;
  }, 0);
}
const orderUrl = (id) => (id ? `/admin/#order/${encodeURIComponent(id)}` : "/admin/");

/** The notification text (Portuguese: it is for the owners) for an admin email kind, or null for kinds we don't push. */
function message(kind, data) {
  const d = data || {};
  const o = d.order || {};
  const id = o.id || d.orderId || null;
  const num = o.number || "";
  switch (kind) {
    case "admin_new_order": {
      const m = magnetsOf(o.items);
      const total = o.pricing && o.pricing.total;
      return { title: `🛒 Novo pedido ${num}`.trim(), body: [money(total), m ? `${m} ${m === 1 ? "ímã" : "ímãs"}` : "", clip(o.name, 40)].filter(Boolean).join(" · "),
        url: orderUrl(id), tag: `order-${id || num}`, urgency: "high" };
    }
    case "admin_contact": {
      const c = d.contact || d;
      return { title: "💬 Mensagem de cliente", body: `${firstName(c.name) || "Alguém"}: ${clip(c.message, 120)}`, url: "/admin/#messages", tag: `msg-${d.messageId || Date.now()}`, urgency: "normal" };
    }
    case "admin_quote": {
      const q = d.quote || d;
      const what = [clip(q.occasion || q.package, 30), q.quantity ? `${q.quantity} ímãs` : ""].filter(Boolean).join(", ");
      return { title: "💍 Pedido de orçamento", body: `${firstName(q.name) || "Um cliente"}${what ? ` · ${what}` : ""}`, url: "/admin/#messages", tag: `quote-${d.quoteId || Date.now()}`, urgency: "normal" };
    }
    case "admin_dispute": {
      const dp = d.dispute || {};
      const due = dp.evidenceDueBy ? new Date(dp.evidenceDueBy).toLocaleDateString("pt-BR", { day: "numeric", month: "short", timeZone: "America/New_York" }) : "";
      return { title: "⚠️ Contestação de pagamento", body: `${num || "Um pedido"} · ${money(dp.amount)}${due ? ` · responda no Stripe até ${due}` : " · responda no Stripe"}`,
        url: orderUrl(id), tag: `dispute-${dp.id || num}`, urgency: "high" };
    }
    case "admin_delivery_check": {
      const n = (d.orders || []).length;
      if (!n) return null;
      const one = n === 1 ? d.orders[0] : null;
      return { title: "📦 Conferir entrega", body: one ? `${one.number}: ${clip(one.issue || `enviado há ${one.days} dias e ainda sem entrega confirmada`, 110)}` : `${n} pedidos enviados ainda sem entrega confirmada`,
        url: one ? orderUrl(one.id) : "/admin/#orders?tab=shipped", tag: "delivery-check", urgency: "normal" };
    }
    case "admin_payment_hold": {
      if (d.mode === "expired") {
        return { title: "❌ Reserva do cartão venceu", body: `${num}: não dá mais para cobrar. Mande um link de pagamento ao cliente.`, url: orderUrl(id), tag: `hold-${id}`, urgency: "high" };
      }
      const h = Math.max(1, Math.round(Number(d.hoursLeft) || 0));
      const left = h >= 36 ? `${Math.round(h / 24)} dias` : h >= 20 ? "1 dia" : `${h} horas`;
      return { title: "⏳ Reserva do cartão vencendo", body: `${num}: vence em ${left}. Envie o pedido ou toque em "Charge now".`, url: orderUrl(id), tag: `hold-${id}`, urgency: "high" };
    }
    case "push_test":
      return { title: "🐝 Notificações ativadas", body: "É assim que os avisos da Little Hive House vão chegar neste aparelho.", url: "/admin/#settings", tag: "push-test", urgency: "normal" };
    default:
      return null;
  }
}

function wants(doc, kind) {
  const key = KIND_PREF[kind];
  if (key === undefined) return false;
  if (key === null) return true;
  return !(doc.prefs && doc.prefs[key] === false);
}

/** Sends one payload to one stored subscription doc. Returns "sent" | "gone" | "failed". */
async function deliver(snap, msg, keys) {
  const s = snap.data();
  const sub = { endpoint: s.endpoint, keys: { p256dh: s.keys && s.keys.p256dh, auth: s.keys && s.keys.auth } };
  const payload = JSON.stringify({ title: msg.title, body: msg.body, url: msg.url, tag: msg.tag });
  try {
    await sender()(sub, payload, {
      TTL: 24 * 3600, urgency: msg.urgency || "normal",
      vapidDetails: { subject: `mailto:${mailAdmin() || "support@littlehivehouse.com"}`, publicKey: keys.publicKey, privateKey: keys.privateKey },
    });
    await snap.ref.update({ lastSentAt: nowIso(), failures: 0 }).catch(() => {});
    return "sent";
  } catch (err) {
    const code = err && (err.statusCode || err.status);
    if (code === 404 || code === 410) {             // the phone unsubscribed or the app was removed
      await snap.ref.delete().catch(() => {});
      return "gone";
    }
    console.warn("[push] send failed", code || "", err && err.message);
    const failures = (Number(s.failures) || 0) + 1;
    if (failures >= 20) await snap.ref.delete().catch(() => {});
    else await snap.ref.update({ failures, lastError: String((err && err.message) || err).slice(0, 200) }).catch(() => {});
    return "failed";
  }
}

/** Pushes an admin alert to every subscribed phone that wants this kind. Never throws. Returns {sent, gone, failed}. */
async function notifyAdmins(kind, data, { only } = {}) {
  const out = { sent: 0, gone: 0, failed: 0 };
  try {
    const msg = message(kind, data);
    if (!msg) return out;
    const q = await deps.db().collection(COLL).get();
    const targets = q.docs.filter((d) => (only ? d.id === only : true) && wants(d.data(), kind));
    if (!targets.length) return out;
    const keys = await vapidKeys();
    const results = await Promise.all(targets.map((d) => deliver(d, msg, keys)));
    results.forEach((r) => { out[r] += 1; });
  } catch (err) {
    console.warn("[push] notifyAdmins failed", kind, err && err.message);
  }
  return out;
}

/* ---------- the callable the admin app uses: adminPush({action, ...}) ---------- */
const subId = (endpoint) => crypto.createHash("sha256").update(String(endpoint)).digest("hex").slice(0, 40);

function cleanSubscription(s) {
  const sub = s && typeof s === "object" ? s : {};
  const endpoint = U.text(sub.endpoint, 1000, { required: true, field: "the subscription" });
  let host = "";
  try { const u = new URL(endpoint); if (u.protocol !== "https:") throw new Error("not https"); host = u.hostname; } catch (e) { fail("invalid-argument", "That notification subscription is not valid."); }
  const keys = sub.keys && typeof sub.keys === "object" ? sub.keys : {};
  const p256dh = U.text(keys.p256dh, 200), auth = U.text(keys.auth, 100);
  if (!/^[A-Za-z0-9_-]{40,}$/.test(p256dh) || !/^[A-Za-z0-9_-]{10,}$/.test(auth)) fail("invalid-argument", "That notification subscription is missing its keys.");
  return { endpoint, host, keys: { p256dh, auth } };
}
function cleanPrefs(p) {
  const out = {};
  for (const k of PREFS) out[k] = !(p && typeof p === "object" && p[k] === false);
  return out;
}

async function adminPush(data, auth) {
  U.requireAdmin(auth);
  const action = U.text(data && data.action, 20);
  const db = deps.db();
  if (action === "key") return { publicKey: (await vapidKeys()).publicKey, prefs: PREFS };

  const endpoint = data && (data.endpoint || (data.subscription && data.subscription.endpoint));
  if (action === "status") {
    if (!endpoint) return { subscribed: false, prefs: cleanPrefs(null) };
    const snap = await db.collection(COLL).doc(subId(endpoint)).get();
    return snap.exists ? { subscribed: true, prefs: cleanPrefs(snap.data().prefs) } : { subscribed: false, prefs: cleanPrefs(null) };
  }
  if (action === "subscribe") {
    const sub = cleanSubscription(data && data.subscription);
    const ref = db.collection(COLL).doc(subId(sub.endpoint));
    const snap = await ref.get();
    const at = nowIso();
    const prefs = cleanPrefs(data && data.prefs !== undefined ? data.prefs : snap.exists ? snap.data().prefs : null);
    await ref.set({ ...sub, prefs, uid: auth.uid, email: String(auth.token.email || "").toLowerCase(),
      device: U.text(data && data.device, 80), createdAt: snap.exists ? snap.data().createdAt || at : at, updatedAt: at, failures: 0 });
    return { ok: true, subscribed: true, prefs };
  }
  if (action === "unsubscribe") {
    if (endpoint) await db.collection(COLL).doc(subId(endpoint)).delete();
    return { ok: true, subscribed: false };
  }
  if (action === "test") {
    if (!endpoint) fail("invalid-argument", "Turn notifications on first.");
    const id = subId(endpoint);
    const r = await notifyAdmins("push_test", {}, { only: id });
    if (!r.sent) fail("unavailable", r.gone ? "This phone is no longer subscribed. Turn notifications on again." : "The test notification could not be sent. Try again in a minute.");
    return { ok: true };
  }
  fail("invalid-argument", "Unknown action.");
}

module.exports = { notifyAdmins, message, adminPush, setSender, generateVapidKeys, vapidKeys, resetCache, subId, KIND_PREF, PREFS, magnetsOf };
