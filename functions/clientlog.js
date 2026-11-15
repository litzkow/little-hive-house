"use strict";
/* clientLog: problems customers hit in the shop (assets/site.js LHH.report and window.onerror), sent with
   navigator.sendBeacon to the HTTP function clientLog. Stored in clientErrors/ (admins read, nobody writes from a
   browser) and, for the problems that cost a sale (checkout failed, photos lost, the photo builder crashed), the owners
   get an email and a phone notification: at most one per kind every 3 hours, with how many happened since.
   Never stores personal data: no email, no name, no IP (only a hash used for the rate limit). */

const deps = require("./deps");
const { nowIso, mailAdmin } = require("./config");
const U = require("./util");

const KINDS = {
  js_error: "Erro de JavaScript numa página",
  checkout_failed: "O pagamento não abriu para um cliente",
  upload_failed: "As fotos de um cliente não subiram",
  photo_unreadable: "Um cliente escolheu um arquivo que não abre",
  photos_lost: "Um pacote de fotos sumiu do carrinho de um cliente",
  builder_crash: "O construtor de fotos recarregou sozinho no celular de um cliente",
};
const ALERT = new Set(["checkout_failed", "upload_failed", "photos_lost", "builder_crash"]);
const ALERT_EVERY_S = 3 * 3600;
const KEEP_DAYS = 90;

function clip(v, n) { return String(v == null ? "" : v).replace(/[\u0000-\u001f]+/g, " ").trim().slice(0, n); }

/** Cleans one report from the browser; null if it isn't one. */
function clean(raw) {
  let d = raw;
  if (Buffer.isBuffer(d)) d = d.toString("utf8");
  if (typeof d === "string") { if (d.length > 8000) return null; try { d = JSON.parse(d); } catch (e) { return null; } }
  if (!d || typeof d !== "object" || !Object.prototype.hasOwnProperty.call(KINDS, d.kind)) return null;
  let page = clip(d.page, 200);
  try { const u = new URL(page); page = u.pathname + (u.search ? u.search.replace(/([?&](order|session|email|token|key)=)[^&]*/gi, "$1…") : ""); } catch (e) { page = page.split("?")[0]; }
  return {
    kind: d.kind, msg: clip(d.msg, 500), code: clip(d.code, 80), page, src: clip(d.src, 200).split("?")[0],
    lang: d.lang === "pt" ? "pt" : "en", ua: clip(d.ua, 220), photos: Number.isFinite(Number(d.photos)) ? Math.max(0, Math.min(500, Math.round(Number(d.photos)))) : null,
  };
}

/** Saves the report; alerts the owners for the serious kinds (throttled). Returns {status, body}. */
async function handle(body, ip) {
  const r = clean(body);
  if (!r) return { status: 400, body: "bad report" };
  try { await U.rateLimit("clientlog", ip || "unknown", 40, 3600); } catch (e) { return { status: 429, body: "slow down" }; }
  const db = deps.db();
  const at = nowIso();
  await db.collection("clientErrors").add({ ...r, at, expireAt: new Date(Date.now() + KEEP_DAYS * 864e5) });
  if (ALERT.has(r.kind)) await alert(r, at).catch((err) => console.warn("[clientlog] alert failed", err && err.message));
  return { status: 204, body: "" };
}

async function alert(r, at) {
  const db = deps.db();
  const ref = db.collection("meta").doc("clientAlerts");
  let send = false, since = 1;
  await db.runTransaction(async (tx) => {
    const snap = await tx.get(ref);
    const d = (snap.exists && snap.data()[r.kind]) || null;
    const now = Date.now();
    if (!d || now - Date.parse(d.sentAt) > ALERT_EVERY_S * 1000) {
      since = (d && d.pending ? d.pending : 0) + 1;
      tx.set(ref, { [r.kind]: { sentAt: at, pending: 0 } }, { merge: true });
      send = true;
    } else {
      tx.set(ref, { [r.kind]: { ...d, pending: (d.pending || 0) + 1 } }, { merge: true });
    }
  });
  if (!send) return;
  const mail = require("./mail");
  await mail.send({ to: mailAdmin(), kind: "admin_site_problem", data: { problem: { ...r, title: KINDS[r.kind], count: since, at } } });
}

module.exports = { handle, clean, KINDS, ALERT };
