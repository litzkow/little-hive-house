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
const RETURN_DAYS = 30;

const LISTINGS = require("./etsy-listings.json");
let PAUSE_MS = 3000;
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
  let res;
  for (let attempt = 1; ; attempt++) {
    res = await globalThis.fetch(`${API}${path}`, { method, headers, body });
    if (res.status !== 429 || attempt >= 4) break;
    await new Promise((r) => setTimeout(r, PAUSE_MS * attempt));   // Etsy allows only a few calls per second
  }
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
  if (!out.returnPolicyId) {
    // ready-made designs: returns within 30 days (the site's policy); no exchanges
    const list = (await call("GET", `/shops/${shopId}/policies/return`)).results || [];
    const found = list.find((p) => p.accepts_returns && !p.accepts_exchanges && Number(p.return_deadline) === RETURN_DAYS);
    out.returnPolicyId = found ? found.return_policy_id : (await call("POST", `/shops/${shopId}/policies/return`, { form: {
      accepts_returns: "true", accepts_exchanges: "false", return_deadline: String(RETURN_DAYS) } })).return_policy_id;
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

/** The photo version of one listing: the shop-wide "imagesVersion" (every listing's photos rebuilt), or the listing's
    own "imagesVersion" when only its photos changed (e.g. the owners' real photo added), whichever is newer. */
const imgV = (l) => Math.max(Number(LISTINGS.imagesVersion || 1), Number(l.imagesVersion || 0));
/** Sends the listing's photos from number `from` on, in order (retrying a dropped upload). */
async function uploadImages(l, shopId, id, from = 0) {
  for (let i = from; i < l.images; i++) {
    const blob = await fetchImage(`${siteUrl()}/etsy/img/${l.id}/${i + 1}.jpg?v=${imgV(l)}`);
    for (let attempt = 1; ; attempt++) {
      const fd = new FormData();
      fd.append("image", blob, `${l.id}-${i + 1}.jpg`);
      fd.append("rank", String(i + 1));
      fd.append("alt_text", `${l.alt || l.title}`.slice(0, 250));
      try { await call("POST", `/shops/${shopId}/listings/${id}/images`, { multipart: fd }); break; } catch (err) {
        if (attempt >= 3) throw err;
        await new Promise((r) => setTimeout(r, PAUSE_MS * attempt));   // Etsy's photo service sometimes drops a connection
      }
    }
  }
}
/** New photos for a listing already on Etsy (the photo set changed: imagesVersion). How Etsy behaves (tried on the
    real shop, Nov 2026): a photo sent "at rank 1" does NOT push the others down, it makes two photos at rank 1, and
    Etsy then refuses every later upload ("ListingImages … in an inconsistent order"); deleting leaves gaps in the ranks;
    an active listing can't lose its last photo; re-attaching a photo by its id with a rank moves it there. So:
    1. all old photos out but one, which goes to rank 1 (this also repairs a listing whose ranks are already broken);
    2. the new photos in at ranks 2, 3, … (after it, nothing clashes);
    3. the last old photo out;  4. the new photos moved to ranks 1, 2, 3, …
    It can run again from any half-done state. Photos Etsy hands back as the same id (an identical picture) are kept. */
async function listImages(id) {
  return ((await call("GET", `/listings/${id}/images`)).results || [])
    .map((im) => ({ id: im.listing_image_id, rank: Number(im.rank) || 0 })).sort((a, b) => a.rank - b.rank);
}
async function placeImage(shopId, id, imageId, rank) {
  const fd = new FormData();
  fd.append("listing_image_id", String(imageId));
  fd.append("rank", String(rank));
  await call("POST", `/shops/${shopId}/listings/${id}/images`, { multipart: fd });
}
async function replaceImages(l, shopId, id) {
  const old = await listImages(id);
  const keep = old[old.length - 1];
  for (const im of old.slice(0, -1)) await call("DELETE", `/shops/${shopId}/listings/${id}/images/${im.id}`);
  if (keep && keep.rank !== 1) await placeImage(shopId, id, keep.id, 1);
  const added = [];
  for (let i = 0; i < l.images; i++) {
    const blob = await fetchImage(`${siteUrl()}/etsy/img/${l.id}/${i + 1}.jpg?v=${imgV(l)}`);
    for (let attempt = 1; ; attempt++) {
      const fd = new FormData();
      fd.append("image", blob, `${l.id}-${i + 1}.jpg`);
      fd.append("rank", String(i + 2));
      fd.append("alt_text", `${l.alt || l.title}`.slice(0, 250));
      try { added.push((await call("POST", `/shops/${shopId}/listings/${id}/images`, { multipart: fd })).listing_image_id); break; } catch (err) {
        if (attempt >= 3) throw err;
        await new Promise((r) => setTimeout(r, PAUSE_MS * attempt));
      }
    }
  }
  if (keep && !added.includes(keep.id)) await call("DELETE", `/shops/${shopId}/listings/${id}/images/${keep.id}`);
  for (let i = 0; i < added.length; i++) await placeImage(shopId, id, added[i], i + 1);
  const now = await listImages(id);
  const ok = now.length === added.length && now.every((im, i) => im.rank === i + 1 && im.id === added[i]);
  if (!ok) fail("unavailable", `Etsy: the photos didn't end up in order (${now.map((im) => im.rank).join(",")}). Try again.`);
}

/** What a listing says (title, text, tags, section, personalization): sent when it's made and when it changes. */
function listingTexts(l, s) {
  return {
    title: l.title, description: l.description, tags: l.tags.join(","),
    ...(s.sections && s.sections[l.section] ? { shop_section_id: String(s.sections[l.section]) } : {}),
    // personalization (the photo upload box and the frame/captions box) is set up by the owners in Etsy and never
    // sent from here, so an update can't wipe it
    ...(s.returnPolicyId ? { return_policy_id: String(s.returnPolicyId) } : {}),
  };
}

/** The shop in the site's order (etsy-listings.json is kept in that order): the sections shown in the order their
    listings first appear, and the first 4 listings as the shop's featured ones. Etsy has no way to move a section, only
    to rename it, so the section slots (in Etsy's order) get the wanted titles and each listing goes to its section. */
async function arrange(shopId) {
  const s = await setup(shopId);
  const want = [...new Set(LISTINGS.listings.map((l) => l.section))];
  const all = ((await call("GET", `/shops/${shopId}/sections`)).results || []).sort((x, y) => (x.rank || 0) - (y.rank || 0));
  const mine = all.filter((x) => want.includes(x.title) || /^lhh-tmp-/.test(x.title));
  if (mine.length < want.length) fail("failed-precondition", "Some Etsy sections are missing. Publish once, then arrange.");
  const slots = mine.slice(0, want.length);
  const changed = slots.map((x, i) => ({ id: x.shop_section_id, from: x.title, to: want[i] })).filter((x) => x.from !== x.to);
  for (const c of changed) await call("PUT", `/shops/${shopId}/sections/${c.id}`, { form: { title: `lhh-tmp-${c.id}` } });
  for (const c of changed) await call("PUT", `/shops/${shopId}/sections/${c.id}`, { form: { title: c.to } });
  const sections = {};
  slots.forEach((x, i) => { sections[want[i]] = x.shop_section_id; });
  await col().doc("setup").set({ sections, at: nowIso() }, { merge: true });
  const done = (await readDoc("listings")) || {};
  let rank = 0;
  const moved = [];
  for (const l of LISTINGS.listings) {
    const d = done[l.id];
    if (!d || !d.listingId) continue;
    rank += 1;
    await call("PATCH", `/shops/${shopId}/listings/${d.listingId}`, { form: {
      shop_section_id: String(sections[l.section]), ...(rank <= 4 ? { featured_rank: String(rank) } : {}) } });
    moved.push(l.id);
  }
  return { sections: want, renamed: changed.length, listings: moved };
}

async function publishOne(l, shopId, s, fetchImage, resumeId) {
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
  if (s.returnPolicyId) form.return_policy_id = String(s.returnPolicyId);
  let id = resumeId, have = 0;
  if (id) {
    // a draft from an earlier try: finish it (its texts, the return policy, the photos still missing)
    await call("PATCH", `/shops/${shopId}/listings/${id}`, { form: { title: form.title, description: form.description, tags: form.tags,
      ...(form.return_policy_id ? { return_policy_id: form.return_policy_id } : {}) } });
    have = ((await call("GET", `/listings/${id}/images`)).results || []).length;
  } else {
    id = (await call("POST", `/shops/${shopId}/listings`, { form })).listing_id;
    await col().doc("listings").set({ [l.id]: { listingId: id, state: "draft", at: nowIso() } }, { merge: true });
  }
  await uploadImages(l, shopId, id, have);
  await call("PUT", `/listings/${id}/inventory`, { json: inventory(l, s.readinessStateId) });
  const live = await call("PATCH", `/shops/${shopId}/listings/${id}`, { form: { state: "active" } });
  const row = { listingId: id, state: live.state || "active", imagesV: imgV(l), url: live.url || `https://www.etsy.com/listing/${id}`, at: nowIso(), error: "" };
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
function setImageFetcher(fn, pauseMs) { fetchImage = fn || defaultFetchImage; if (pauseMs !== undefined) PAUSE_MS = pauseMs; }

/* ---------- what the Etsy page shows ---------- */
async function status() {
  const k = keys(), a = await readDoc("auth"), done = (await readDoc("listings")) || {}, s = (await readDoc("setup")) || {};
  return {
    keystring: !!k.keystring, secret: !!k.secret, connected: !!(a && a.refresh), shop: a && a.shopId ? { id: a.shopId, name: a.shopName || "", url: a.shopUrl || "" } : null,
    category: s.taxonomyPath || "",
    listings: LISTINGS.listings.map((l) => {
      const d = done[l.id] || { state: "" };
      return { id: l.id, name: l.name, section: l.section, images: l.images, ...d,
        newPhotos: d.state === "active" && Number(d.imagesV || 1) < imgV(l) };
    }),
  };
}

/** adminEtsy({action: "status" | "start" | "finish" | "publish" | "arrange" | "disconnect", ...}) */
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
      if (done && done.state === "active") {
        if (Number(done.imagesV || 1) >= imgV(l)) return { listing: { id: l.id, ...done }, skipped: true };
        try {
          // a new version of the listing: texts, section and design menu (the site's order) first, then the photos
          const s = await setup(a.shopId);
          await call("PATCH", `/shops/${a.shopId}/listings/${done.listingId}`, { form: listingTexts(l, s) });
          await call("PUT", `/listings/${done.listingId}/inventory`, { json: inventory(l, s.readinessStateId) });
          await replaceImages(l, a.shopId, done.listingId);
        } catch (err) {
          console.error("etsy new photos", l.id, String(err.message || err));
          await col().doc("listings").set({ [l.id]: { ...done, error: String(err.message || err).slice(0, 300), at: nowIso() } }, { merge: true });
          throw err;
        }
        const row = { ...done, imagesV: imgV(l), error: "", at: nowIso() };
        await col().doc("listings").set({ [l.id]: row }, { merge: true });
        return { listing: { id: l.id, ...row, newPhotos: false } };
      }
      try {
        const s = await setup(a.shopId);
        return { listing: { id: l.id, ...(await publishOne(l, a.shopId, s, fetchImage, done && done.listingId)) } };
      } catch (err) {
        console.error("etsy publish", l.id, String(err.message || err));
        await col().doc("listings").set({ [l.id]: { ...(done || {}), state: (done && done.state) || ((done && done.listingId) ? "draft" : ""), error: String(err.message || err).slice(0, 300), at: nowIso() } }, { merge: true });
        throw err;
      }
    }
    case "arrange": {
      const a = await readDoc("auth");
      if (!a || !a.shopId) fail("failed-precondition", "Etsy isn't connected yet. Tap “Connect Etsy” first.");
      return arrange(a.shopId);
    }
    case "disconnect":
      await col().doc("auth").delete();
      return status();
    default:
      fail("invalid-argument", "Unknown action.");
  }
}

/** Maintenance: send only a listing's texts (title, description, tags, section) to Etsy. */
async function patchTexts(l, listingId) {
  const a = await readDoc("auth");
  const s = await setup(a.shopId);
  await call("PATCH", `/shops/${a.shopId}/listings/${listingId}`, { form: listingTexts(l, s) });
}

module.exports = { adminEtsy, setImageFetcher, _internal: { inventory, findTaxonomy, SCOPES, redirectUri, LISTINGS, patchTexts } };
