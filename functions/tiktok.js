"use strict";
/* The shop's TikTok Shop (Little Hive House), run from the Hive Admin's TikTok Shop page through the TikTok Shop Open API.
   The owners' own app "Hive Admin" in the TikTok Shop Partner Center (Custom app, US local sellers): its app key is
   public (APP_KEY below); its app secret is pasted once in the TikTok Shop page and kept in tiktok/auth, a collection
   the apps can't read (firestore.rules has no rule for it). Only these functions use it.
   "Connect TikTok" sends the owner to TikTok to authorize the shop; TikTok sends them back to
   admin/tiktok-callback.html, which hands the code to adminTikTok({action: "finish"}). Tokens: access 7 days (refreshed
   by itself), refresh as long as the authorization lasts.
   API requests (version 202309): host open-api.tiktokglobalshop.com, query app_key + timestamp + sign (+ shop_cipher),
   header x-tts-access-token. sign = hex HMAC-SHA256(secret, secret + path + sorted query {key}{value} (no sign,
   no access_token) + body (not for multipart) + secret). */

const crypto = require("crypto");
const { fail, env, nowIso } = require("./config");
const deps = require("./deps");
const U = require("./util");

const APP_KEY_DEFAULT = "6lqcfgtud0gvr";
const SERVICE_ID_DEFAULT = "7705213161087436558";
const API = "https://open-api.tiktokglobalshop.com";
const AUTH = "https://auth.tiktok-shops.com/api/v2/token";
const AUTHORIZE = "https://services.us.tiktokshop.com/open/authorize";

const col = () => deps.db().collection("tiktok");
async function readDoc(id) { const s = await col().doc(id).get(); return s.exists ? s.data() : null; }

function appKey() { return env("TIKTOK_APP_KEY") || APP_KEY_DEFAULT; }
function serviceId() { return env("TIKTOK_SERVICE_ID") || SERVICE_ID_DEFAULT; }

let fetcher = (...a) => globalThis.fetch(...a);
let clock = () => Date.now();
/** Tests swap the network and the clock. */
function setTransport(fn, now) { fetcher = fn || ((...a) => globalThis.fetch(...a)); clock = now || (() => Date.now()); }

/** TikTok's request signature (see the header). `query` without sign and access_token; `body` the exact JSON text sent. */
function sign(secret, path, query, body) {
  const keys = Object.keys(query).filter((k) => k !== "sign" && k !== "access_token" && query[k] !== undefined).sort();
  let input = path;
  for (const k of keys) input += k + String(query[k]);
  if (body) input += body;
  return crypto.createHmac("sha256", secret).update(secret + input + secret).digest("hex");
}

function apiError(json, res) {
  const msg = (json && (json.message || json.msg)) || `TikTok answered ${res.status}`;
  const code = json && json.code !== undefined ? ` [${json.code}]` : "";
  return `${String(msg).slice(0, 280)}${code}`;
}

/* ---------- tokens ---------- */
async function secretOf() {
  const a = await readDoc("auth");
  const s = (a && a.appSecret) || env("TIKTOK_APP_SECRET");
  if (!s) fail("failed-precondition", "The TikTok app secret isn't saved yet. Paste it on the TikTok Shop page first.");
  return s;
}
async function tokenRequest(kind, params) {
  const q = new URLSearchParams({ app_key: appKey(), app_secret: await secretOf(), ...params });
  const res = await fetcher(`${AUTH}/${kind}?${q.toString()}`, { method: "GET", headers: { Accept: "application/json" } });
  let json = null;
  try { json = await res.json(); } catch (e) { json = null; }
  if (!res.ok || !json || json.code !== 0 || !json.data || !json.data.access_token) {
    fail("failed-precondition", `TikTok: ${apiError(json, res)}`);
  }
  return json.data;
}
function tokenRow(d) {
  return {
    access: d.access_token, refresh: d.refresh_token,
    accessExpiresAt: Number(d.access_token_expire_in) * 1000 || clock() + 6 * 86400000,
    refreshExpiresAt: Number(d.refresh_token_expire_in) * 1000 || 0,
    openId: d.open_id || "", sellerName: d.seller_name || "", region: d.seller_base_region || "",
    scopes: Array.isArray(d.granted_scopes) ? d.granted_scopes : [], at: nowIso(),
  };
}
async function accessToken() {
  const a = await readDoc("auth");
  if (!a || !a.refresh) fail("failed-precondition", "TikTok Shop isn't connected yet. Tap “Connect TikTok” first.");
  if (a.access && Number(a.accessExpiresAt) > clock() + 3600000) return a.access;
  const d = await tokenRequest("refresh", { refresh_token: a.refresh, grant_type: "refresh_token" });
  await col().doc("auth").set(tokenRow(d), { merge: true });
  return d.access_token;
}

/* ---------- the API ---------- */
/** call("GET", "/product/202309/categories", {query, json, form, shop: true}) -> data. `shop` adds shop_cipher. */
async function call(method, path, { query = {}, json, form, shop = true } = {}) {
  const secret = await secretOf();
  const token = await accessToken();
  const q = { ...query, app_key: appKey(), timestamp: String(Math.floor(clock() / 1000)) };
  if (shop) {
    const a = await readDoc("auth");
    if (!a || !a.shopCipher) fail("failed-precondition", "TikTok Shop isn't connected yet. Tap “Connect TikTok” first.");
    q.shop_cipher = a.shopCipher;
  }
  const headers = { "x-tts-access-token": token, Accept: "application/json" };
  let body;
  if (json !== undefined) { headers["Content-Type"] = "application/json"; body = JSON.stringify(json); }
  q.sign = sign(secret, path, q, json !== undefined ? body : "");
  if (form) body = form;   // multipart (FormData): fetch sets the boundary; not part of the signature
  const url = `${API}${path}?${new URLSearchParams(q).toString()}`;
  let res, out = null;
  for (let attempt = 1; ; attempt++) {
    res = await fetcher(url, { method, headers, body });
    try { out = await res.json(); } catch (e) { out = null; }
    const limited = res.status === 429 || (out && Number(out.code) === 36009003);
    if (!limited || attempt >= 4) break;
    await new Promise((r) => setTimeout(r, 1500 * attempt));
  }
  if (!res.ok || !out || Number(out.code) !== 0) fail("unavailable", `TikTok: ${apiError(out, res)} (${method} ${path.replace(/\d{8,}/g, "…")})`);
  return out.data || {};
}

/* ---------- what the TikTok Shop page shows ---------- */
async function status() {
  const a = (await readDoc("auth")) || {};
  return {
    appKey: appKey(), secret: !!(a.appSecret || env("TIKTOK_APP_SECRET")), secretEnd: a.appSecret ? String(a.appSecret).slice(-4) : "",
    connected: !!(a.refresh && a.shopCipher),
    shop: a.shopCipher ? { id: a.shopId || "", name: a.shopName || a.sellerName || "", region: a.shopRegion || a.region || "" } : null,
    scopes: a.scopes || [], connectedAt: a.connectedAt || "",
    refreshEnds: a.refreshExpiresAt ? new Date(Number(a.refreshExpiresAt)).toISOString() : "",
  };
}

/** adminTikTok({action: "status" | "saveSecret" | "start" | "finish" | "disconnect", ...}) */
async function adminTikTok(data, auth) {
  U.requireAdmin(auth);
  data = data || {};
  switch (data.action) {
    case "status": return status();
    case "saveSecret": {
      const secret = U.text(data.secret, 200, { required: true, field: "the app secret" }).replace(/\s+/g, "");
      if (!/^[A-Za-z0-9_-]{20,128}$/.test(secret)) fail("invalid-argument", "That doesn't look like the app secret. In the Partner Center, open the Hive Admin app › App secret › Manage app secret, copy it and paste it again.");
      await col().doc("auth").set({ appSecret: secret, secretAt: nowIso(), secretBy: U.who(auth) }, { merge: true });
      return status();
    }
    case "start": {
      await secretOf();
      const state = crypto.randomBytes(16).toString("hex");
      await col().doc("oauth").set({ state, by: U.who(auth), at: nowIso() });
      return { url: `${AUTHORIZE}?${new URLSearchParams({ service_id: serviceId(), state }).toString()}` };
    }
    case "finish": {
      const o = await readDoc("oauth");
      const code = U.text(data.code, 600), state = U.text(data.state, 128);
      if (!code) fail("invalid-argument", "TikTok didn't send the authorization back. Tap “Connect TikTok” again.");
      if (!o || !o.state || o.state !== state) fail("failed-precondition", "This TikTok authorization doesn't match. Tap “Connect TikTok” again.");
      if (clock() - new Date(o.at).getTime() > 30 * 60000) fail("failed-precondition", "The TikTok authorization took too long. Tap “Connect TikTok” again.");
      const d = await tokenRequest("get", { auth_code: code, grant_type: "authorized_code" });
      await col().doc("auth").set({ ...tokenRow(d), connectedAt: nowIso(), by: U.who(auth) }, { merge: true });
      await col().doc("oauth").delete();
      const shops = (await call("GET", "/authorization/202309/shops", { shop: false })).shops || [];
      const s = shops.find((x) => String(x.region || "").toUpperCase() === "US") || shops[0];
      if (!s) fail("failed-precondition", "TikTok connected, but no shop came with it. Authorize with the Little Hive House seller account.");
      await col().doc("auth").set({ shopCipher: s.cipher, shopId: String(s.id || ""), shopName: s.name || "", shopRegion: s.region || "", shopCode: s.code || "" }, { merge: true });
      return status();
    }
    case "products": {
      const P = require("./tiktok-products");
      if (data.check) await P.refresh();
      return { products: await P.status() };
    }
    case "publish": {
      const P = require("./tiktok-products");
      const id = U.text(data.id, 80, { required: true, field: "the collection" });
      try { return await P.publish(id); } catch (err) {
        console.error("tiktok publish", id, String(err.message || err));
        await col().doc("products").set({ [id]: { state: "", error: String(err.message || err).slice(0, 300), at: nowIso() } }, { merge: true });
        throw err;
      }
    }
    case "disconnect": {
      const a = (await readDoc("auth")) || {};
      // the app secret stays (it belongs to the app, not to the connection)
      await col().doc("auth").set({ appSecret: a.appSecret || "", access: "", refresh: "", shopCipher: "", accessExpiresAt: 0 }, { merge: false });
      return status();
    }
    default:
      fail("invalid-argument", "Unknown action.");
  }
}

module.exports = { adminTikTok, setTransport, _internal: { sign, call, accessToken, readAuth: () => readDoc("auth"), appKey, serviceId, tokenRow } };
