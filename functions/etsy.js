"use strict";
/* The shop's Etsy store (LittleHiveHouse), run from the Hive Admin's Etsy page through Etsy's Open API v3.
   The owners' own app on etsy.com/developers: its keystring and shared secret are the GitHub secrets ETSY_KEYSTRING and
   ETSY_SHARED_SECRET. "Connect Etsy" sends the owner to Etsy to approve (OAuth 2 with PKCE); Etsy sends them back to
   admin/etsy-callback.html, which hands the code to adminEtsy({action: "finish"}). The tokens live in etsy/auth, a
   collection the apps can't read (firestore.rules has no rule for it); only these functions use them.
   "Publish" puts the listings of etsy-listings.json (texts, tags, prices, variations; the photos are etsy/img/<id>/<n>.jpg
   on the website) on Etsy one at a time: the shipping profile, the processing time and the shop sections are made the
   first time. Each listing is published once; etsy/listings remembers its Etsy id. */

const crypto = require("crypto");
const { fail, env, siteUrl, nowIso } = require("./config");
const deps = require("./deps");
const U = require("./util");

const API = "https://api.etsy.com/v3/application";
const TOKEN_URL = "https://api.etsy.com/v3/public/oauth/token";
const CONNECT_URL = "https://www.etsy.com/oauth/connect";
const SCOPES = "listings_r listings_w shops_r shops_w transactions_r";
const CUSTOM_PROPERTY = 513;   // Etsy's first custom variation ("Design", "Pack size")
const QUANTITY = 99;           // made to order: it never runs out
const SHIPPING = { title: "USPS Ground Advantage", cost: 5.49, minDays: 2, maxDays: 5 };
const PROCESSING = { min: 1, max: 2 };

const LISTINGS = require("./etsy-listings.json");
const col = () => deps.db().collection("etsy");
const r2 = (n) => Math.round(Number(n) * 100) / 100;

function keys() {
  const k = env("ETSY_KEYSTRING"), s = env("ETSY_SHARED_SECRET");
  return { keystring: k, secret: s, ready: !!(k && s) };
}
function redirectUri() { return `${siteUrl()}/admin/etsy-callback.html`; }
const b64url = (buf) => buf.toString("base64").replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");

async function readDoc(id) { const s = await col().doc(id).get(); return s.exists ? s.data() : null; }

function etsyError(json, res) {
  const msg = (json && (json.error_description || json.error || json.message)) || `Etsy answered ${res.status}`;
  return String(msg).slice(0, 300);
}

/* ---------- OAuth ---------- */
async function tokenRequest(body) {
  const k = keys();
  const res = await globalThis.fetch(TOKEN_URL, {
    method: "POST", headers: { "Content-Type": "application/x-www-form-urlencoded", Accept: "application/json" },
    body: new URLSearchParams({ client_id: k.keystring, ...body }).toString(),
  });
  let json = null;
  try { json = await res.json(); } catch (e) { json = null; }
  if (!res.ok || !json || !json.access_token) fail("failed-precondition", `Etsy didn't accept the connection: ${etsyError(json, res)}`);
  return json;
}
function saveTokens(json, extra = {}) {
  return col().doc("auth").set({
    access: json.access_token, refresh: json.refresh_token, expiresAt: Date.now() + (Number(json.expires_in) || 3600) * 1000,
    scope: json.scope || SCOPES, userId: String(json.access_token).split(".")[0], at: nowIso(), ...extra,
  }, { merge: true });
}
async function accessToken() {
  const a = await readDoc("auth");
  if (!a || !a.refresh) fail("failed-precondition", "Etsy isn't connected yet. Tap “Connect Etsy” first.");
  if (a.access && Number(a.expiresAt) > Date.now() + 60000) return a.access;
  const json = await tokenRequest({ grant_type: "refresh_token", refresh_token: a.refresh });
  await saveTokens(json);
  return json.access_token;
}

/* ---------- the API ---------- */
async function call(method, path, { form, json, multipart } = {}) {
  const k = keys();
  if (!k.ready) fail("failed-precondition", "The Etsy keys aren't saved yet (GitHub secrets ETSY_KEYSTRING and ETSY_SHARED_SECRET).");
  const headers = { "x-api-key": `${k.keystring}:${k.secret}`, Authorization: `Bearer ${await accessToken()}`, Accept: "application/json" };
  let body;
  if (form) { headers["Content-Type"] = "application/x-www-form-urlencoded"; body = new URLSearchParams(form).toString(); }
  else if (json) { headers["Content-Type"] = "application/json"; body = JSON.stringify(json); }
  else if (multipart) body = multipart;
  const res = await globalThis.fetch(`${API}${path}`, { method, headers, body });
  let out = null;
  try { out = await res.json(); } catch (e) { out = null; }
  if (!res.ok) fail("unavailable", `Etsy: ${etsyError(out, res)} (${method} ${path.replace(/\d{5,}/g, "…")})`);
  return out || {};
}

/* ---------- setup made once: shipping profile, processing time, category, sections ---------- */
function findTaxonomy(nodes) {
  const flat = [];
  (function walk(list, path) { (list || []).forEach((n) => { const p = path.concat(n.name); flat.push({ id: n.id, name: n.name, path: p.join(" > ") }); walk(n.children, p); }); })(nodes, []);
  return flat.find((n) => /refrigerator magnet|fridge magnet/i.test(n.name))
    || flat.find((n) => /^magnets?$/i.test(n.name) && /home/i.test(n.path))
    || flat.find((n) => /magnet/i.test(n.name)) || null;
}
async function setup(shopId) {
  const have = (await readDoc("setup")) || {};
  const out = { ...have };
  if (!out.shippingProfileId) {
    const list = await call("GET", `/shops/${shopId}/shipping-profiles`);
    const found = (list.results || []).find((p) => p.title === SHIPPING.title);
    if (found) out.shippingProfileId = found.shipping_profile_id;
    else {
      const zip = (((await deps.db().collection("settings").doc("store").get()).data() || {}).shipFrom || {}).zip;
      const p = await call("POST", `/shops/${shopId}/shipping-profiles`, { form: {
        title: SHIPPING.title, origin_country_iso: "US", ...(zip ? { origin_postal_code: String(zip) } : {}),
        primary_cost: String(SHIPPING.cost), secondary_cost: "0", destination_country_iso: "US",
        min_delivery_days: String(SHIPPING.minDays), max_delivery_days: String(SHIPPING.maxDays) } });
      out.shippingProfileId = p.shipping_profile_id;
    }
  }
  if (!out.readinessStateId) {
    const r = await call("POST", `/shops/${shopId}/readiness-state-definitions`, { form: {
      readiness_state: "made_to_order", min_processing_time: String(PROCESSING.min), max_processing_time: String(PROCESSING.max), processing_time_unit: "days" } });
    out.readinessStateId = r.readiness_state_id;
  }
  if (!out.taxonomyId) {
    const t = findTaxonomy((await call("GET", "/seller-taxonomy/nodes")).results);
    if (!t) fail("unavailable", "Couldn't find Etsy's fridge magnet category.");
    out.taxonomyId = t.id; out.taxonomyPath = t.path;
  }
  out.sections = out.sections || {};
  const want = [...new Set(LISTINGS.listings.map((l) => l.section))].filter((s) => !out.sections[s]);
  if (want.length) {
    const existing = (await call("GET", `/shops/${shopId}/sections`)).results || [];
    for (const title of want) {
      const e = existing.find((s) => s.title === title);
      out.sections[title] = e ? e.shop_section_id : (await call("POST", `/shops/${shopId}/sections`, { form: { title } })).shop_section_id;
    }
  }
  await col().doc("setup").set({ ...out, at: nowIso() }, { merge: true });
  return out;
}

/* ---------- one listing ---------- */
function inventory(l, readinessStateId) {
  const v = l.variations[0];
  const products = v.options.map((o, i) => ({
    sku: `${l.id}-${i + 1}`.slice(0, 32),
    property_values: [{ property_id: CUSTOM_PROPERTY, property_name: v.name, value_ids: [], values: [o] }],
    offerings: [{ price: r2(v.prices ? v.prices[i] : l.price), quantity: QUANTITY, is_enabled: true, readiness_state_id: readinessStateId }],
  }));
  return { products, price_on_property: v.prices ? [CUSTOM_PROPERTY] : [], quantity_on_property: [], sku_on_property: [CUSTOM_PROPERTY], readiness_state_on_property: [] };
}

async function publishOne(l, shopId, s, fetchImage) {
  const minPrice = r2(Math.min(...(l.variations[0].prices || [l.price])));
  const form = {
    quantity: String(QUANTITY), title: l.title, description: l.description, price: String(minPrice),
    who_made: "i_did", when_made: "made_to_order", taxonomy_id: String(s.taxonomyId), type: "physical",
    shipping_profile_id: String(s.shippingProfileId), readiness_state_id: String(s.readinessStateId),
    tags: l.tags.join(","), should_auto_renew: "true", is_supply: "false",
    ...(s.sections[l.section] ? { shop_section_id: String(s.sections[l.section]) } : {}),
    ...(l.personalization ? { is_personalizable: "true", personalization_is_required: "true", personalization_char_count_max: "500",
      personalization_instructions: l.personalization } : {}),
  };
  const draft = await call("POST", `/shops/${shopId}/listings`, { form });
  const id = draft.listing_id;
  await col().doc("listings").set({ [l.id]: { listingId: id, state: "draft", at: nowIso() } }, { merge: true });
  for (let i = 0; i < l.images; i++) {
    const blob = await fetchImage(`${siteUrl()}/etsy/img/${l.id}/${i + 1}.jpg`);
    const fd = new FormData();
    fd.append("image", blob, `${l.id}-${i + 1}.jpg`);
    fd.append("rank", String(i + 1));
    fd.append("alt_text", `${l.alt || l.title}`.slice(0, 250));
    await call("POST", `/shops/${shopId}/listings/${id}/images`, { multipart: fd });
  }
  await call("PUT", `/listings/${id}/inventory`, { json: inventory(l, s.readinessStateId) });
  const live = await call("PATCH", `/shops/${shopId}/listings/${id}`, { form: { state: "active" } });
  const row = { listingId: id, state: live.state || "active", url: live.url || `https://www.etsy.com/listing/${id}`, at: nowIso(), error: "" };
  await col().doc("listings").set({ [l.id]: row }, { merge: true });
  return row;
}
async function defaultFetchImage(url) {
  const res = await globalThis.fetch(url);
  if (!res.ok) fail("unavailable", `A photo didn't load (${url.split("/etsy/")[1]}).`);
  return new Blob([Buffer.from(await res.arrayBuffer())], { type: "image/jpeg" });
}
let fetchImage = defaultFetchImage;
/** Tests swap how the photos are fetched. */
function setImageFetcher(fn) { fetchImage = fn || defaultFetchImage; }

/* ---------- what the Etsy page shows ---------- */
async function status() {
  const k = keys(), a = await readDoc("auth"), done = (await readDoc("listings")) || {}, s = (await readDoc("setup")) || {};
  return {
    keystring: !!k.keystring, secret: !!k.secret, connected: !!(a && a.refresh), shop: a && a.shopId ? { id: a.shopId, name: a.shopName || "", url: a.shopUrl || "" } : null,
    category: s.taxonomyPath || "",
    listings: LISTINGS.listings.map((l) => ({ id: l.id, name: l.name, section: l.section, images: l.images, ...(done[l.id] || { state: "" }) })),
  };
}

/** adminEtsy({action: "status" | "start" | "finish" | "publish" | "disconnect", ...}) */
async function adminEtsy(data, auth) {
  U.requireAdmin(auth);
  data = data || {};
  switch (data.action) {
    case "status": return status();
    case "start": {
      const k = keys();
      if (!k.keystring) fail("failed-precondition", "The Etsy keystring isn't saved yet (GitHub secret ETSY_KEYSTRING).");
      const verifier = b64url(crypto.randomBytes(48)), state = b64url(crypto.randomBytes(16));
      await col().doc("oauth").set({ verifier, state, by: U.who(auth), at: nowIso() });
      const challenge = b64url(crypto.createHash("sha256").update(verifier).digest());
      const q = new URLSearchParams({ response_type: "code", client_id: k.keystring, redirect_uri: redirectUri(), scope: SCOPES, state,
        code_challenge: challenge, code_challenge_method: "S256" });
      return { url: `${CONNECT_URL}?${q.toString()}` };
    }
    case "finish": {
      const o = await readDoc("oauth");
      const code = U.text(data.code, 512), state = U.text(data.state, 128);
      if (!o || !o.state || o.state !== state) fail("failed-precondition", "This Etsy approval doesn't match. Tap “Connect Etsy” again.");
      if (Date.now() - new Date(o.at).getTime() > 30 * 60000) fail("failed-precondition", "The Etsy approval took too long. Tap “Connect Etsy” again.");
      const json = await tokenRequest({ grant_type: "authorization_code", redirect_uri: redirectUri(), code, code_verifier: o.verifier });
      await saveTokens(json, { by: U.who(auth) });
      await col().doc("oauth").delete();
      const me = await call("GET", "/users/me");
      let shop = {};
      if (me.shop_id) { try { shop = await call("GET", `/shops/${me.shop_id}`); } catch (e) { shop = {}; } }
      await col().doc("auth").set({ shopId: me.shop_id || null, shopName: shop.shop_name || "", shopUrl: shop.url || "" }, { merge: true });
      return status();
    }
    case "publish": {
      const l = LISTINGS.listings.find((x) => x.id === data.id);
      if (!l) fail("invalid-argument", "Unknown listing.");
      const a = await readDoc("auth");
      if (!a || !a.shopId) fail("failed-precondition", "Etsy isn't connected yet. Tap “Connect Etsy” first.");
      const done = ((await readDoc("listings")) || {})[l.id];
      if (done && done.state === "active") return { listing: { id: l.id, ...done }, skipped: true };
      try {
        const s = await setup(a.shopId);
        return { listing: { id: l.id, ...(await publishOne(l, a.shopId, s, fetchImage)) } };
      } catch (err) {
        await col().doc("listings").set({ [l.id]: { ...(done || {}), state: (done && done.listingId) ? "draft" : "", error: String(err.message || err).slice(0, 300), at: nowIso() } }, { merge: true });
        throw err;
      }
    }
    case "disconnect":
      await col().doc("auth").delete();
      return status();
    default:
      fail("invalid-argument", "Unknown action.");
  }
}

module.exports = { adminEtsy, setImageFetcher, _internal: { inventory, findTaxonomy, SCOPES, redirectUri, LISTINGS } };
