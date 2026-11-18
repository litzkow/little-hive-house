"use strict";
/* Anúncios (Hive Admin › Anúncios): the paid ads of every sales channel in one place, run by a small robot.
   The owners approve one number, the most the shop may spend on ads in a month (the "teto"). Inside it the robot
   works alone; above it, it only proposes and waits for "Aprovar".

   Channels:
     meta    Instagram + Facebook through the Marketing API, with a system-user token the owners paste once in the app
             (ads/auth, a doc the apps can't read: firestore.rules has no rule for it). The robot boosts the shop's best
             recent Instagram posts ($1–2 a day each, link to the site with utm_medium=paid and utm_content=<post id>),
             pauses the ones that spend without selling, gives more to the ones that sell and never passes the teto.
     etsy    Etsy doesn't let apps run Etsy Ads. The robot reads what Etsy charged for ads (payment ledger) and the Etsy
             sales (receipts) with the shop's Etsy connection (functions/etsy.js) and advises: turn on, raise, stop.
     google / tiktok / amazon   not automated yet; spend paid by hand can be logged ("Registrar gasto").
   Sales that came from an ad: the site's purchases in Google Analytics with medium "paid" (functions/analytics.js).

   Firestore: ads/config (teto, budgets, rules), ads/auth (Meta token), ads/state (boosted posts, last run, advice),
   adsDaily/{YYYY-MM-DD} (spend and sales per channel), adsLog/{id} (what the robot did and why),
   adsProposals/{id} (waiting for approval), adsManual/{id} (spend logged by hand).
   settings/store.adSpendByDay {day: dollars} is what Reports count as the "Anúncios" cost.

   adminAds({action}) for the page; run() every morning (index.js adsDaily) and on "Rodar agora". */

const crypto = require("crypto");
const { fail, env, siteUrl, nowIso } = require("./config");
const deps = require("./deps");
const U = require("./util");

const TZ = "America/New_York";
const DAY = 86400000;
const CHANNELS = ["meta", "etsy", "google", "tiktok", "amazon"];
const r2 = (n) => Math.round((Number(n) || 0) * 100) / 100;
const num = (v) => (Number.isFinite(Number(v)) ? Number(v) : 0);
const clamp = (v, lo, hi) => Math.min(hi, Math.max(lo, v));

/** What a new shop starts with: $200 a month, about $4 a day on Instagram/Facebook and $2 a day on Etsy. */
const DEFAULTS = {
  monthCap: 200,
  auto: true,
  channels: { meta: { on: true, daily: 4 }, etsy: { on: true, daily: 2 }, google: { on: false, daily: 0 }, tiktok: { on: false, daily: 0 }, amazon: { on: false, daily: 0 } },
  rules: { perPost: 2, maxPosts: 3, maxPerPost: 5, stopAfter: 8, growRoas: 3, postDays: 90 },
};
/* Platform floors the app enforces (TikTok: $20 a day per ad group; Meta and Etsy: $1). */
const MIN_DAILY = { meta: 1, etsy: 1, google: 1, tiktok: 20, amazon: 1 };

const db = () => deps.db();
const doc = (id) => db().collection("ads").doc(id);
async function read(id) { const s = await doc(id).get(); return s.exists ? s.data() : null; }

/* ---------- days in the shop's time zone ---------- */
const fmtDay = new Intl.DateTimeFormat("en-CA", { timeZone: TZ, year: "numeric", month: "2-digit", day: "2-digit" });
function dayKey(ms) { return fmtDay.format(new Date(ms == null ? Date.now() : ms)); }
function monthOf(day) { return String(day).slice(0, 7); }
function daysInMonth(month) { const [y, m] = month.split("-").map(Number); return new Date(Date.UTC(y, m, 0)).getUTCDate(); }
function dayOfMonth(day) { return Number(String(day).slice(8, 10)); }
/** epoch seconds of midnight (New York) of a YYYY-MM-DD; an hour off around the clock change is fine here */
function dayStartSec(day) {
  const guess = Date.parse(`${day}T05:00:00Z`);
  const shown = new Intl.DateTimeFormat("en-US", { timeZone: TZ, hour: "numeric", hourCycle: "h23" }).format(new Date(guess));
  return Math.floor((guess - Number(shown) * 3600000) / 1000);
}
function addDays(day, n) { return dayKey(Date.parse(`${day}T12:00:00Z`) + n * DAY); }

/* ---------- config ---------- */
function cleanConfig(c) {
  c = c || {};
  const out = { monthCap: r2(clamp(num(c.monthCap != null ? c.monthCap : DEFAULTS.monthCap), 0, 100000)), auto: c.auto !== false, channels: {}, rules: {} };
  CHANNELS.forEach((k) => {
    const d = DEFAULTS.channels[k], x = (c.channels && c.channels[k]) || {};
    const daily = r2(clamp(num(x.daily != null ? x.daily : d.daily), 0, 10000));
    out.channels[k] = { on: x.on != null ? !!x.on : d.on, daily };
  });
  const R = DEFAULTS.rules, x = c.rules || {};
  out.rules = {
    perPost: r2(clamp(num(x.perPost != null ? x.perPost : R.perPost), 1, 100)),
    maxPosts: Math.round(clamp(num(x.maxPosts != null ? x.maxPosts : R.maxPosts), 1, 20)),
    maxPerPost: r2(clamp(num(x.maxPerPost != null ? x.maxPerPost : R.maxPerPost), 1, 500)),
    stopAfter: r2(clamp(num(x.stopAfter != null ? x.stopAfter : R.stopAfter), 1, 1000)),
    growRoas: r2(clamp(num(x.growRoas != null ? x.growRoas : R.growRoas), 1, 50)),
    postDays: Math.round(clamp(num(x.postDays != null ? x.postDays : R.postDays), 7, 365)),
  };
  if (out.rules.maxPerPost < out.rules.perPost) out.rules.maxPerPost = out.rules.perPost;
  ["capAt", "capBy"].forEach((k) => { if (c[k]) out[k] = String(c[k]); });
  return out;
}
async function config() { return cleanConfig(await read("config")); }
/** The days of budget the plan uses in a month: what each channel that's on would spend every day. */
function plannedDaily(cfg) {
  return r2(CHANNELS.reduce((t, k) => t + (cfg.channels[k].on ? cfg.channels[k].daily : 0), 0));
}

/* ---------- Meta (Instagram + Facebook) ---------- */
const META_VERSION = () => env("META_API_VERSION") || "v26.0";
function metaError(j, res) {
  const e = (j && j.error) || {};
  return String(e.error_user_msg || e.message || `Meta answered ${res && res.status}`).slice(0, 300);
}
/** One Graph API call. GET params go in the query, POST params in the form body (objects as JSON). */
async function graph(meta, method, path, params = {}, host = "graph.facebook.com") {
  if (!meta || !meta.token) fail("failed-precondition", "Instagram/Facebook isn't connected yet. Tap “Connect Meta” first.");
  const p = { ...params, access_token: meta.token };
  if (meta.appSecret) p.appsecret_proof = crypto.createHmac("sha256", meta.appSecret).update(meta.token).digest("hex");
  const enc = Object.entries(p).filter(([, v]) => v !== undefined && v !== null)
    .map(([k, v]) => [k, typeof v === "object" ? JSON.stringify(v) : String(v)]);
  let url = `https://${host}/${META_VERSION()}/${String(path).replace(/^\//, "")}`, body;
  if (method === "GET") url += `?${new URLSearchParams(enc).toString()}`;
  else body = new URLSearchParams(enc);
  let res, j = null;
  for (let attempt = 1; ; attempt++) {
    res = await globalThis.fetch(url, { method, body });
    try { j = await res.json(); } catch (e) { j = null; }
    const code = j && j.error && j.error.code;
    // 4, 17, 80004: too many calls (the free API tier is slow on purpose); wait and try again a little
    if ((res.status === 429 || code === 4 || code === 17 || code === 80004) && attempt < 3) { await new Promise((r) => setTimeout(r, PAUSE_MS * attempt)); continue; }
    break;
  }
  if (!res.ok || (j && j.error)) {
    const err = new Error(`Meta: ${metaError(j, res)}`);
    err.meta = (j && j.error) || {};
    throw err;
  }
  return j || {};
}
let PAUSE_MS = 4000;

const actId = (id) => (String(id || "").startsWith("act_") ? String(id) : `act_${String(id || "").replace(/\D/g, "")}`);
const cents = (dollars) => String(Math.round(num(dollars) * 100));

/** Pastes of the token: find the ad account, the Facebook Page and its Instagram account, and check they answer. */
async function connectMeta(data, auth) {
  const token = U.text(data.token, 1000, { required: true, field: "the Meta token" }).replace(/\s+/g, "");
  if (token.length < 30) fail("invalid-argument", "That doesn't look like a Meta token. Copy the whole token (it is long) and paste it again.");
  const meta = { token, appSecret: U.text(data.appSecret, 100) || "" };
  let me;
  try { me = await graph(meta, "GET", "me", { fields: "id,name" }); } catch (e) { fail("failed-precondition", `Meta didn't accept the token. ${e.message}`); }
  let accounts = [];
  try { accounts = ((await graph(meta, "GET", "me/adaccounts", { fields: "id,name,account_status,currency", limit: 50 })).data) || []; } catch (e) { accounts = []; }
  const wanted = U.text(data.adAccountId, 40).replace(/\D/g, "");
  const acct = wanted ? (accounts.find((a) => String(a.id).replace(/\D/g, "") === wanted) || { id: actId(wanted) }) : accounts[0];
  if (!acct) fail("failed-precondition", "The token works, but it can't see any ad account. In Meta Business settings, give the system user access to the Little Hive House ad account and generate the token again.");
  let detail = acct;
  try { detail = await graph(meta, "GET", actId(acct.id), { fields: "id,name,account_status,currency" }); } catch (e) { fail("failed-precondition", `The token can't open the ad account ${acct.id}. ${e.message}`); }
  if (detail.currency && detail.currency !== "USD") fail("failed-precondition", `The ad account is in ${detail.currency}; the app counts in US dollars. Use a USD ad account.`);
  let pages = [];
  try { pages = ((await graph(meta, "GET", "me/accounts", { fields: "id,name,instagram_business_account{id,username}", limit: 50 })).data) || []; } catch (e) { pages = []; }
  const page = pages.find((p) => /little\s*hive/i.test(p.name || "")) || pages.find((p) => p.instagram_business_account) || pages[0] || null;
  let ig = page && page.instagram_business_account ? page.instagram_business_account : null;
  if (!ig) {
    try { ig = (((await graph(meta, "GET", `${actId(acct.id)}/connected_instagram_accounts`, { fields: "id,username" })).data) || [])[0] || null; } catch (e) { ig = null; }
  }
  const out = {
    token, appSecret: meta.appSecret, userId: me.id || "", userName: me.name || "",
    adAccountId: actId(detail.id || acct.id), accountName: detail.name || acct.name || "", accountStatus: num(detail.account_status) || 1, currency: detail.currency || "USD",
    pageId: page ? String(page.id) : "", pageName: page ? page.name || "" : "", igUserId: ig ? String(ig.id) : "", igUsername: ig ? ig.username || "" : "",
    connectedAt: nowIso(), by: U.who(auth),
  };
  await doc("auth").set({ meta: out }, { merge: true });
  await log("meta", "connect", `Conectado ao Meta: conta de anúncios ${out.accountName || out.adAccountId}${out.igUsername ? `, Instagram @${out.igUsername}` : ""}.`,
    `Connected to Meta: ad account ${out.accountName || out.adAccountId}${out.igUsername ? `, Instagram @${out.igUsername}` : ""}.`);
  return out;
}
const metaPublic = (m) => (m ? { connected: true, accountName: m.accountName, adAccountId: m.adAccountId, accountStatus: m.accountStatus, pageName: m.pageName, pageId: m.pageId,
  igUsername: m.igUsername, igReady: !!(m.igUserId && m.pageId), tokenEnd: String(m.token || "").slice(-4), connectedAt: m.connectedAt } : { connected: false });

/** The shop's recent Instagram posts, best first (likes + 3 x comments), with whether Meta lets them be boosted. */
async function recentPosts(meta, rules) {
  if (!meta.igUserId) return [];
  const j = await graph(meta, "GET", `${meta.igUserId}/media`, {
    fields: "id,caption,media_type,media_product_type,permalink,timestamp,like_count,comments_count,thumbnail_url,media_url,boost_eligibility_info", limit: 40,
  });
  const since = Date.now() - (rules ? rules.postDays : 90) * DAY;
  return ((j && j.data) || []).filter((m) => Date.parse(m.timestamp || 0) >= since).map((m) => {
    const elig = m.boost_eligibility_info || {};
    return {
      id: String(m.id), caption: String(m.caption || "").slice(0, 140), type: m.media_product_type === "REELS" ? "reel" : String(m.media_type || "").toLowerCase(),
      permalink: m.permalink || "", at: m.timestamp || "", likes: num(m.like_count), comments: num(m.comments_count),
      thumb: m.thumbnail_url || (m.media_type === "VIDEO" ? "" : m.media_url) || "", score: num(m.like_count) + 3 * num(m.comments_count),
      eligible: elig.eligible_to_boost !== false, why: elig.eligible_to_boost === false ? String(elig.boost_ineligible_reason || "") : "",
    };
  // Reels first (they reach people who don't follow yet, for less), then likes + comments
  }).sort((a, b) => (b.type === "reel") - (a.type === "reel") || b.score - a.score || String(b.at).localeCompare(String(a.at)));
}
const MIN_AGE = DAY;          // a post is boosted after a day out: by then its likes show whether people like it

function landing(mediaId) {
  const q = new URLSearchParams({ utm_source: "instagram", utm_medium: "paid", utm_campaign: "hive-boost", utm_content: String(mediaId) });
  return `${siteUrl()}/?${q.toString()}`;
}
/** The one campaign every boosted post lives in (made the first time). */
async function campaign(meta, state) {
  if (state.metaCampaignId) return state.metaCampaignId;
  const c = await graph(meta, "POST", `${meta.adAccountId}/campaigns`, {
    name: "Little Hive House · Posts impulsionados (Hive Admin)", objective: "OUTCOME_TRAFFIC", status: "ACTIVE",
    special_ad_categories: [], is_adset_budget_sharing_enabled: false,
  });
  state.metaCampaignId = String(c.id);
  return state.metaCampaignId;
}
/** Meta says the least it takes ("…at least $2.00…"): that amount, or null. */
function minFromError(e) {
  const m = /(?:at least|minimum[^$]*)\s*\$?\s*(\d+(?:\.\d+)?)/i.exec((e && e.message) || "");
  return m ? Number(m[1]) : null;
}
/** Boosts one Instagram post: an ad set with its own daily budget (US, 18–65, Meta's automatic audience) and the ad. */
async function boost(meta, state, post, daily) {
  const cid = await campaign(meta, state);
  const adsetBody = (d) => ({
    name: `Post ${post.id} · ${String(post.caption || "").slice(0, 40) || "Instagram"}`, campaign_id: cid, daily_budget: cents(d),
    billing_event: "IMPRESSIONS", optimization_goal: "LINK_CLICKS", bid_strategy: "LOWEST_COST_WITHOUT_CAP", destination_type: "WEBSITE",
    targeting: { geo_locations: { countries: ["US"] }, age_min: 18, age_max: 65, targeting_automation: { advantage_audience: 1 } }, status: "ACTIVE",
  });
  let adset;
  try { adset = await graph(meta, "POST", `${meta.adAccountId}/adsets`, adsetBody(daily)); } catch (e) {
    const min = minFromError(e);
    if (!min || min <= daily || min > daily * 3) throw e;
    daily = min;
    adset = await graph(meta, "POST", `${meta.adAccountId}/adsets`, adsetBody(daily));
  }
  try {
    const creative = await graph(meta, "POST", `${meta.adAccountId}/adcreatives`, {
      name: `Instagram ${post.id}`, object_id: meta.pageId, instagram_user_id: meta.igUserId, source_instagram_media_id: post.id,
      call_to_action: { type: "SHOP_NOW", value: { link: landing(post.id) } },
    });
    const ad = await graph(meta, "POST", `${meta.adAccountId}/ads`, { name: `Post ${post.id}`, adset_id: adset.id, creative: { creative_id: creative.id }, status: "ACTIVE" });
    return { adsetId: String(adset.id), adId: String(ad.id), creativeId: String(creative.id), daily };
  } catch (e) {
    await graph(meta, "POST", String(adset.id), { status: "DELETED" }).catch(() => {});   // no empty ad set left behind
    throw e;
  }
}
const setAdset = (meta, b, params) => graph(meta, "POST", b.adsetId, params);

/* ---------- reading spend and sales ---------- */
/** Meta: the account's spend, clicks and impressions per day from `since` to today. */
async function metaDays(meta, since, until) {
  const j = await graph(meta, "GET", `${meta.adAccountId}/insights`, {
    level: "account", fields: "spend,impressions,inline_link_clicks", time_range: { since, until }, time_increment: 1, limit: 100,
  });
  const out = {};
  ((j && j.data) || []).forEach((r) => { out[r.date_start] = { spend: r2(r.spend), clicks: num(r.inline_link_clicks), impressions: num(r.impressions) }; });
  return out;
}
/** Meta: each boosted ad's spend and clicks since it started. */
async function metaAdStats(meta, b) {
  const j = await graph(meta, "GET", `${b.adId}/insights`, { fields: "spend,inline_link_clicks,impressions", date_preset: "maximum" });
  const r = ((j && j.data) || [])[0] || {};
  return { spend: r2(r.spend), clicks: num(r.inline_link_clicks), impressions: num(r.impressions) };
}

/** Etsy: ad fees from the payment ledger and the shop's sales, per day. */
const ETSY_AD = /prolist|promoted|etsy[\s_-]*ads?\b|offsite|advertis/i;
function etsyMoney(m) { if (m == null) return 0; if (typeof m === "number") return m / 100; return num(m.amount) / (num(m.divisor) || 100); }
async function etsyDays(since) {
  const E = require("./etsy")._internal;
  const a = await E.readAuth();
  if (!a || !a.shopId) return null;
  const min = dayStartSec(since), max = Math.floor(Date.now() / 1000);
  const out = {};
  const day = (ts) => { const k = dayKey(num(ts) * 1000); return (out[k] = out[k] || { spend: 0, orders: 0, revenue: 0 }); };
  for (let offset = 0; offset < 2000; offset += 100) {
    const j = await E.call("GET", `/shops/${a.shopId}/payment-account/ledger-entries?min_created=${min}&max_created=${max}&limit=100&offset=${offset}`);
    const list = (j && j.results) || [];
    list.forEach((e) => {
      const amount = num(e.amount) / 100;
      if (!ETSY_AD.test(`${e.ledger_type || ""} ${e.description || ""}`)) return;
      day(e.created_timestamp || e.create_date).spend -= amount;   // fees are negative in the ledger
    });
    if (list.length < 100) break;
  }
  for (let offset = 0; offset < 2000; offset += 100) {
    const j = await E.call("GET", `/shops/${a.shopId}/receipts?min_created=${min}&max_created=${max}&limit=100&offset=${offset}`);
    const list = (j && j.results) || [];
    list.filter((r) => r.was_paid !== false && !/cancel/i.test(String(r.status || ""))).forEach((r) => {
      const d = day(r.created_timestamp || r.create_timestamp);
      d.orders += 1; d.revenue += etsyMoney(r.grandtotal);
    });
    if (list.length < 100) break;
  }
  Object.values(out).forEach((d) => { d.spend = r2(Math.max(0, d.spend)); d.revenue = r2(d.revenue); });
  return out;
}

/** The site: purchases per day, and the ones whose visit came from a paid link (utm_medium=paid). */
async function siteDays(since) {
  const A = require("./analytics");
  const rep = await A.ga("runReport", {
    dateRanges: [{ startDate: since, endDate: "today" }],
    dimensions: [{ name: "date" }, { name: "sessionSource" }, { name: "sessionMedium" }, { name: "sessionManualAdContent" }],
    metrics: [{ name: "purchaseRevenue" }, { name: "ecommercePurchases" }], limit: 2000,
  });
  const days = {}, byPost = {};
  A.rows(rep).forEach((r) => {
    if (!r.ecommercePurchases && !r.purchaseRevenue) return;
    const k = `${r.date.slice(0, 4)}-${r.date.slice(4, 6)}-${r.date.slice(6, 8)}`;
    const d = (days[k] = days[k] || { orders: 0, revenue: 0, adOrders: 0, adRevenue: 0, meta: { orders: 0, revenue: 0 } });
    d.orders += r.ecommercePurchases; d.revenue += r.purchaseRevenue;
    const paid = /^(paid|cpc|ppc|paidsocial|paid_social|ads?)$/i.test(r.sessionMedium || "");
    if (!paid) return;
    d.adOrders += r.ecommercePurchases; d.adRevenue += r.purchaseRevenue;
    if (/instagram|facebook|^fb$|^ig$|meta/i.test(r.sessionSource || "")) {
      d.meta.orders += r.ecommercePurchases; d.meta.revenue += r.purchaseRevenue;
      const post = String(r.sessionManualAdContent || "");
      if (/^\d{5,}$/.test(post)) { const p = (byPost[post] = byPost[post] || { orders: 0, revenue: 0 }); p.orders += r.ecommercePurchases; p.revenue += r.purchaseRevenue; }
    }
  });
  Object.values(days).forEach((d) => { ["revenue", "adRevenue"].forEach((k) => { d[k] = r2(d[k]); }); d.meta.revenue = r2(d.meta.revenue); });
  Object.values(byPost).forEach((p) => { p.revenue = r2(p.revenue); });
  return { days, byPost };
}
/** Site sales with a post id over the last `days` days (for each boosted post's return). */
async function siteByPost(days) {
  const s = await siteDays(addDays(dayKey(), -(days - 1)));
  return s.byPost;
}

/* ---------- each sale and where it came from (orders.ref, saved at checkout from assets/store.js) ---------- */
const SALE = new Set(["paid", "in_production", "shipped", "delivered", "refunded", "partially_refunded"]);
const PAID_MEDIUM = /^(paid|cpc|ppc|paidsocial|paid_social|ads?)$/i;
/** Pure: what brought an order. kind: ad | social | search | email | site | direct; channel: meta | google | tiktok | etsy | other. */
function originOf(ref) {
  const r = ref || {}, src = String(r.source || "").toLowerCase(), med = String(r.medium || "").toLowerCase();
  const channel = /instagram|facebook|^fb$|^ig$|meta|messenger/.test(src) ? "meta" : /google|gclid/.test(src) ? "google" : /tiktok/.test(src) ? "tiktok"
    : /etsy/.test(src) ? "etsy" : /pinterest/.test(src) ? "pinterest" : src ? "other" : "";
  if (!src && !med) return { kind: "direct", channel: "" };
  if (PAID_MEDIUM.test(med)) return { kind: "ad", channel: channel || "other", post: /^\d{5,}$/.test(String(r.content || "")) ? String(r.content) : "", campaign: r.campaign || "", source: src };
  if (/mail/.test(med) || /mail|newsletter|resend/.test(src)) return { kind: "email", channel: "email", source: src };
  if (/google|bing|duckduckgo|yahoo|search/.test(src) && !/ads/.test(src)) return { kind: "search", channel: channel || "other", source: src };
  if (channel === "meta" || channel === "tiktok" || channel === "pinterest" || med === "social") return { kind: "social", channel, source: src };
  return { kind: "site", channel: channel || "other", source: src };
}
const orderTotal = (o) => r2(num(o.pricing && o.pricing.total) - num(o.pricing && o.pricing.tax));
const orderDay = (o) => dayKey(Date.parse(o.paidAt || o.createdAt || 0) || 0);
/** The site's sales since `since` (YYYY-MM-DD): per day (from the orders themselves) and each one with its origin. */
async function orderSales(since) {
  const q = await db().collection("orders").where("createdAt", ">=", new Date(dayStartSec(addDays(since, -1)) * 1000).toISOString()).get();
  const days = {}, byPost = {}, list = [];
  q.docs.forEach((d) => {
    const o = d.data();
    if (!SALE.has(o.status)) return;
    const k = orderDay(o);
    if (k < since) return;
    const total = orderTotal(o), org = originOf(o.ref);
    list.push({ id: d.id, number: o.number || "", day: k, at: o.paidAt || o.createdAt, total, origin: org, ref: o.ref || null });
    if (org.kind !== "ad") return;
    const x = (days[k] = days[k] || { adOrders: 0, adRevenue: 0, meta: { orders: 0, revenue: 0 } });
    x.adOrders += 1; x.adRevenue = r2(x.adRevenue + total);
    if (org.channel === "meta") { x.meta.orders += 1; x.meta.revenue = r2(x.meta.revenue + total); }
    if (org.post) { const p = (byPost[org.post] = byPost[org.post] || { orders: 0, revenue: 0 }); p.orders += 1; p.revenue = r2(p.revenue + total); }
  });
  return { days, byPost, list: list.sort((a, b) => String(b.at).localeCompare(String(a.at))) };
}

/* ---------- the log, proposals and notifications ---------- */
async function log(channel, kind, pt, en, extra) {
  await db().collection("adsLog").add({ at: nowIso(), channel, kind, pt, en: en || pt, ...(extra || {}) });
}
async function notify(text, tag) {
  try { await require("./push").notifyAdmins("admin_ads", { text, tag }); } catch (e) { console.warn("[ads] push", e && e.message); }
}

/* ---------- the robot ---------- */
/**
 * Pure: what to do today with the boosted posts. Nothing here talks to Meta.
 *   boosts:   [{id, daily, spend, clicks, revenue}] the active ones
 *   allowed:  how much a day Meta may spend now (inside the teto)
 *   posts:    candidates, best first (already without the boosted, paused-for-good and "never" ones)
 * Returns { pause: [{id, why}], grow: [{id, daily}], start: [{id, daily}] }.
 */
function plan({ boosts, allowed, posts, rules, capReached }) {
  const out = { pause: [], grow: [], start: [] };
  let active = boosts.slice();
  if (capReached || allowed < 1) {
    active.forEach((b) => out.pause.push({ id: b.id, why: "cap" }));
    return out;
  }
  // 1. spent enough to know and sold nothing: stop it
  active = active.filter((b) => {
    if (b.spend >= rules.stopAfter && !(b.revenue > 0)) { out.pause.push({ id: b.id, why: "no-sales" }); return false; }
    return true;
  });
  const roas = (b) => (b.spend > 0 ? b.revenue / b.spend : (b.revenue > 0 ? Infinity : 0));
  // 2. over the day's budget (the teto got closer): pause the weakest until it fits
  const sum = () => r2(active.reduce((t, b) => t + b.daily, 0));
  active.sort((a, b) => roas(b) - roas(a) || b.clicks - a.clicks);
  while (active.length && sum() > allowed + 0.001) {
    const weakest = active.pop();
    out.pause.push({ id: weakest.id, why: "budget" });
  }
  // 3. selling well: one more dollar a day, the best first, while it fits
  active.forEach((b) => {
    if (b.spend >= 3 && roas(b) >= rules.growRoas && b.daily + 1 <= rules.maxPerPost && sum() + 1 <= allowed + 0.001) {
      out.grow.push({ id: b.id, daily: r2(b.daily + 1) });
      b.daily = r2(b.daily + 1);
    }
  });
  // 4. a Reel is waiting and the money is on a photo that sold nothing: the photo gives its place to the Reel
  if (posts[0] && posts[0].type === "reel") {
    const photo = active.slice().reverse().find((b) => b.type && b.type !== "reel" && !(b.revenue > 0) && !out.grow.some((g) => g.id === b.id));
    const room = allowed - sum();
    if (photo && room < rules.perPost - 0.001) {
      out.pause.push({ id: photo.id, why: "reel" });
      active = active.filter((b) => b !== photo);
      out.start.push({ id: posts[0].id, daily: photo.daily });
      posts = posts.slice(1);
    }
  }
  // 5. room left: boost the next best posts
  let count = active.length + out.start.length;
  for (const p of posts) {
    if (count >= rules.maxPosts) break;
    if (sum() + out.start.reduce((t, s) => t + s.daily, 0) + rules.perPost > allowed + 0.001) break;
    out.start.push({ id: p.id, daily: rules.perPost });
    count += 1;
  }
  return out;
}

/** Month to date: spend per channel (meta, etsy, logged by hand) and sales from ads. */
function monthTotals(daily, manual, month) {
  const t = { spend: { meta: 0, etsy: 0, google: 0, tiktok: 0, amazon: 0 }, total: 0, sales: { site: 0, siteOrders: 0, ads: 0, adOrders: 0, meta: 0, metaOrders: 0, etsy: 0, etsyOrders: 0 } };
  Object.entries(daily).forEach(([day, d]) => {
    if (monthOf(day) !== month) return;
    t.spend.meta += num(d.meta && d.meta.spend);
    t.spend.etsy += num(d.etsy && d.etsy.spend);
    t.sales.site += num(d.site && d.site.revenue); t.sales.siteOrders += num(d.site && d.site.orders);
    t.sales.ads += num(d.site && d.site.adRevenue); t.sales.adOrders += num(d.site && d.site.adOrders);
    t.sales.meta += num(d.site && d.site.meta && d.site.meta.revenue); t.sales.metaOrders += num(d.site && d.site.meta && d.site.meta.orders);
    t.sales.etsy += num(d.etsy && d.etsy.revenue); t.sales.etsyOrders += num(d.etsy && d.etsy.orders);
  });
  manual.forEach((m) => { if (monthOf(m.date) === month && t.spend[m.channel] != null) t.spend[m.channel] += num(m.amount); });
  Object.keys(t.spend).forEach((k) => { t.spend[k] = r2(t.spend[k]); });
  Object.keys(t.sales).forEach((k) => { t.sales[k] = r2(t.sales[k]); });
  t.total = r2(Object.values(t.spend).reduce((a, b) => a + b, 0));
  return t;
}
/** Etsy advice from the month so far (Etsy Ads can only be changed in Etsy's own app). */
function etsyAdvice(cfg, t) {
  const c = cfg.channels.etsy, spend = t.spend.etsy, sales = t.sales.etsy;
  if (!c.on) return spend > 0 ? { kind: "off", pt: "Etsy Ads está desligado aqui, mas o Etsy ainda está cobrando anúncios. Desligue no app do Etsy.", en: "Etsy Ads is off here, but Etsy is still charging for ads. Turn it off in the Etsy app." } : { kind: "idle" };
  if (spend >= cfg.rules.stopAfter && sales <= 0) return { kind: "stop", pt: `O Etsy Ads gastou ${money(spend)} este mês e nenhuma venda no Etsy. Pause no app do Etsy ou baixe para $1 por dia.`, en: `Etsy Ads spent ${money(spend)} this month and there were no Etsy sales. Pause it in the Etsy app or lower it to $1 a day.` };
  if (spend >= 5 && sales / spend >= cfg.rules.growRoas) return { kind: "raise", pt: `O Etsy vendeu ${money(sales)} com ${money(spend)} de anúncio. Vale subir o Etsy Ads em $1 por dia, se couber no teto.`, en: `Etsy sold ${money(sales)} on ${money(spend)} of ads. Worth raising Etsy Ads by $1 a day if it fits the cap.` };
  return { kind: "ok", pt: `Deixe o Etsy Ads em ${money(c.daily)} por dia no app do Etsy.`, en: `Keep Etsy Ads at ${money(c.daily)} a day in the Etsy app.` };
}
const money = (n) => `$${(Number(n) || 0).toFixed(2)}`;

/** Reads every channel, saves the days and the Reports cost, then lets the robot act. Never throws: errors go in the log. */
async function run({ by = "robot" } = {}) {
  const cfg = await config();
  const auth = (await read("auth")) || {};
  const meta = auth.meta || null;
  const state = (await read("state")) || {};
  state.boosts = state.boosts || {};
  state.never = state.never || {};
  const today = dayKey(), month = monthOf(today);
  const since = [`${month}-01`, addDays(today, -3)].sort()[0];
  const errors = {};
  const days = {};
  const put = (k, part, v) => { days[k] = days[k] || {}; days[k][part] = v; };

  if (meta) {
    try { Object.entries(await metaDays(meta, since, today)).forEach(([k, v]) => put(k, "meta", v)); } catch (e) { errors.meta = e.message; }
  }
  try {
    const e = await etsyDays(since);
    if (e) Object.entries(e).forEach(([k, v]) => put(k, "etsy", v));
  } catch (e) { errors.etsy = e.message; }
  let byPost = {};
  try {
    const s = await siteDays(since);
    Object.entries(s.days).forEach(([k, v]) => put(k, "site", v));
    byPost = await siteByPost(cfg.rules.postDays);
  } catch (e) { errors.site = e.message; }
  // the orders themselves say which ad brought them: they win over Google Analytics when they count more
  try {
    const os = await orderSales(addDays(dayKey(), -(cfg.rules.postDays - 1)));
    Object.entries(os.days).forEach(([k, v]) => {
      if (k < since) return;
      const s0 = (days[k] && days[k].site) || { orders: 0, revenue: 0, adOrders: 0, adRevenue: 0, meta: { orders: 0, revenue: 0 } };
      const m0 = s0.meta || { orders: 0, revenue: 0 };
      put(k, "site", { ...s0, adOrders: Math.max(num(s0.adOrders), v.adOrders), adRevenue: Math.max(num(s0.adRevenue), v.adRevenue),
        meta: { orders: Math.max(num(m0.orders), v.meta.orders), revenue: Math.max(num(m0.revenue), v.meta.revenue) } });
    });
    Object.entries(os.byPost).forEach(([id, v]) => { const g = byPost[id] || { orders: 0, revenue: 0 }; byPost[id] = { orders: Math.max(g.orders, v.orders), revenue: Math.max(g.revenue, v.revenue) }; });
  } catch (e) { errors.orders = e.message; }

  // save the days (only the parts that were read, so a failed read keeps yesterday's numbers)
  const batchDays = Object.keys(days).sort();
  for (const k of batchDays) await db().collection("adsDaily").doc(k).set({ ...days[k], at: nowIso() }, { merge: true });

  // everything since the 1st, as saved
  const saved = {};
  (await db().collection("adsDaily").get()).docs.forEach((d) => { if (monthOf(d.id) === month) saved[d.id] = d.data(); });
  for (const k of batchDays) if (monthOf(k) === month) saved[k] = { ...(saved[k] || {}), ...days[k] };
  const manual = (await db().collection("adsManual").get()).docs.map((d) => ({ id: d.id, ...d.data() }));
  const totals = monthTotals(saved, manual, month);
  await syncReports(manual);

  // the robot (Instagram/Facebook); Etsy only gets advice
  const capReached = cfg.monthCap > 0 ? totals.total >= cfg.monthCap - 0.01 : true;
  const daysLeft = daysInMonth(month) - dayOfMonth(today) + 1;
  const room = Math.max(0, cfg.monthCap - totals.total);
  const others = CHANNELS.filter((k) => k !== "meta" && cfg.channels[k].on).reduce((t, k) => t + cfg.channels[k].daily, 0);
  const allowed = r2(Math.max(0, Math.min(cfg.channels.meta.on ? cfg.channels.meta.daily : 0, room / daysLeft - others)));
  const did = [];
  if (meta && cfg.auto && meta.igUserId && meta.pageId) {
    try {
      const activeIds = Object.keys(state.boosts).filter((id) => state.boosts[id].status === "active");
      const boosts = [];
      for (const id of activeIds) {
        const b = state.boosts[id];
        let st = { spend: num(b.spend), clicks: num(b.clicks) };
        try { st = await metaAdStats(meta, b); } catch (e) { errors.meta = errors.meta || e.message; }
        Object.assign(b, st, { revenue: num(byPost[id] && byPost[id].revenue), orders: num(byPost[id] && byPost[id].orders) });
        boosts.push({ id, daily: num(b.daily), spend: st.spend, clicks: st.clicks, revenue: b.revenue });
      }
      let posts = [];
      try { posts = await recentPosts(meta, cfg.rules); } catch (e) { errors.meta = errors.meta || e.message; }
      state.posts = posts.slice(0, 24);
      const candidates = posts.filter((p) => p.eligible && !state.never[p.id] && !state.boosts[p.id] && Date.now() - Date.parse(p.at || 0) >= MIN_AGE);
      boosts.forEach((b) => { const p = posts.find((x) => x.id === b.id); b.type = (p && p.type) || state.boosts[b.id].type || ""; });
      const P = plan({ boosts, allowed, posts: candidates, rules: cfg.rules, capReached });
      for (const p of P.pause) {
        const b = state.boosts[p.id];
        try {
          await setAdset(meta, b, { status: "PAUSED" });
          b.status = p.why === "no-sales" ? "stopped" : "paused"; b.why = p.why; b.pausedAt = nowIso();
          const pt = p.why === "no-sales" ? `Pausei o post ${short(b)}: gastou ${money(b.spend)} e não vendeu.`
            : p.why === "reel" ? `Pausei o post ${short(b)} para passar o dinheiro para um Reel (Reels alcançam mais gente por menos).`
            : p.why === "cap" ? `Pausei o post ${short(b)}: o teto do mês (${money(cfg.monthCap)}) chegou.` : `Pausei o post ${short(b)} para caber no orçamento do dia.`;
          const en = p.why === "no-sales" ? `Paused post ${short(b)}: spent ${money(b.spend)} and sold nothing.`
            : p.why === "reel" ? `Paused post ${short(b)} to move its money to a Reel.`
            : p.why === "cap" ? `Paused post ${short(b)}: the month's cap (${money(cfg.monthCap)}) was reached.` : `Paused post ${short(b)} to fit the day's budget.`;
          await log("meta", "pause", pt, en, { post: p.id }); did.push(pt);
        } catch (e) { errors.meta = e.message; await log("meta", "error", `Não consegui pausar o post ${short(b)}: ${e.message}`, `Couldn't pause post ${short(b)}: ${e.message}`); }
      }
      for (const g of P.grow) {
        const b = state.boosts[g.id];
        try {
          await setAdset(meta, b, { daily_budget: cents(g.daily) });
          b.daily = g.daily;
          const pt = `O post ${short(b)} está vendendo (${money(b.revenue)} com ${money(b.spend)}). Subi para ${money(g.daily)} por dia.`;
          await log("meta", "grow", pt, `Post ${short(b)} is selling (${money(b.revenue)} on ${money(b.spend)}). Raised to ${money(g.daily)} a day.`, { post: g.id }); did.push(pt);
        } catch (e) { errors.meta = e.message; }
      }
      for (const s of P.start) {
        const post = candidates.find((p) => p.id === s.id);
        try {
          const made = await boost(meta, state, post, s.daily);
          state.boosts[post.id] = { id: post.id, ...made, type: post.type || "", status: "active", startedAt: nowIso(), by, caption: post.caption, permalink: post.permalink, thumb: post.thumb, spend: 0, clicks: 0, revenue: 0 };
          const pt = `Comecei a impulsionar o post ${short(state.boosts[post.id])} com ${money(made.daily)} por dia.`;
          await log("meta", "start", pt, `Started boosting post ${short(state.boosts[post.id])} at ${money(made.daily)} a day.`, { post: post.id }); did.push(pt);
        } catch (e) {
          errors.meta = e.message;
          state.failed = { ...(state.failed || {}), [post.id]: { at: nowIso(), error: e.message } };
          await log("meta", "error", `Não consegui impulsionar o post ${short(post)}: ${e.message}`, `Couldn't boost post ${short(post)}: ${e.message}`, { post: post.id });
          break;   // one failure a day is enough to look at; tomorrow tries again
        }
      }
    } catch (e) { errors.meta = e.message; }
  }

  // asking for more: the ads pay well and the teto will run out before the month ends
  const adSales = r2(totals.sales.ads + totals.sales.etsy), roas = totals.total > 0 ? adSales / totals.total : 0;
  if (cfg.monthCap > 0 && totals.total >= cfg.monthCap * 0.6 && roas >= cfg.rules.growRoas) {
    const pending = (await db().collection("adsProposals").where("status", "==", "pending").get()).docs;
    if (!pending.length) {
      const newCap = Math.ceil((cfg.monthCap * 1.5) / 10) * 10;
      const pt = `Os anúncios estão dando retorno: ${money(adSales)} em vendas com ${money(totals.total)} de gasto. Quer subir o teto do mês de ${money(cfg.monthCap)} para ${money(newCap)}?`;
      await db().collection("adsProposals").add({ at: nowIso(), kind: "cap", from: cfg.monthCap, to: newCap, status: "pending", pt,
        en: `The ads are paying off: ${money(adSales)} in sales on ${money(totals.total)} spent. Raise the monthly cap from ${money(cfg.monthCap)} to ${money(newCap)}?` });
      await notify(pt, "ads-proposal");
    }
  }
  // the teto was reached today: one notice
  if (capReached && cfg.monthCap > 0 && state.capNoticed !== month) {
    state.capNoticed = month;
    const pt = `O teto de anúncios do mês (${money(cfg.monthCap)}) chegou. Os anúncios do Instagram/Facebook foram pausados${cfg.channels.etsy.on ? "; pause o Etsy Ads no app do Etsy" : ""}.`;
    await log("all", "cap", pt, `The month's ad cap (${money(cfg.monthCap)}) was reached. Instagram/Facebook ads were paused${cfg.channels.etsy.on ? "; pause Etsy Ads in the Etsy app" : ""}.`);
    await notify(pt, "ads-cap");
  }
  const advice = etsyAdvice(cfg, totals);
  if (advice.kind !== (state.etsyAdvice && state.etsyAdvice.kind) && ["stop", "raise", "off"].includes(advice.kind)) await notify(advice.pt, "ads-etsy");
  state.etsyAdvice = advice;
  if (did.length) await notify(did.length === 1 ? did[0] : `${did.length} mudanças nos anúncios. Veja em Anúncios.`, "ads-robot");

  state.lastRun = { at: nowIso(), by, errors, allowed, total: totals.total };
  await doc("state").set(state);
  return { totals, errors, did };
}
const short = (b) => {
  const c = String((b && b.caption) || "").replace(/\s+/g, " ").trim();
  return c ? `“${c.length > 32 ? c.slice(0, 31) + "…" : c}”` : (b && b.id ? `#${String(b.id).slice(-5)}` : "");
};

/** Reports: settings/store.adSpendByDay = Meta + Etsy (from adsDaily) + spend logged by hand, the last 400 days. */
async function syncReports(manual) {
  const from = addDays(dayKey(), -400);
  const q = await db().collection("adsDaily").get();
  const byDay = {};
  q.docs.forEach((d) => {
    if (d.id < from) return;
    const x = d.data(), v = num(x.meta && x.meta.spend) + num(x.etsy && x.etsy.spend);
    if (v) byDay[d.id] = r2((byDay[d.id] || 0) + v);
  });
  (manual || []).forEach((m) => { if (m.date >= from) byDay[m.date] = r2((byDay[m.date] || 0) + num(m.amount)); });
  await db().collection("settings").doc("store").set({ adSpendByDay: byDay }, { merge: true });
  // Firestore merge keeps old keys; write the whole map again when days were removed
  const s = (await db().collection("settings").doc("store").get()).data() || {};
  if (Object.keys(s.adSpendByDay || {}).some((k) => !(k in byDay))) await db().collection("settings").doc("store").update({ adSpendByDay: byDay });
  return byDay;
}

/* ---------- what the page shows ---------- */
async function view() {
  const cfg = await config();
  const auth = (await read("auth")) || {};
  const state = (await read("state")) || {};
  const today = dayKey(), month = monthOf(today);
  const q = await db().collection("adsDaily").get();
  const daily = {};
  q.docs.forEach((d) => { daily[d.id] = d.data(); });
  const manual = (await db().collection("adsManual").get()).docs.map((d) => ({ id: d.id, ...d.data() })).sort((a, b) => String(b.date).localeCompare(String(a.date)));
  const totals = monthTotals(daily, manual, month);
  const logQ = await db().collection("adsLog").get();
  const logs = logQ.docs.map((d) => ({ id: d.id, ...d.data() })).sort((a, b) => String(b.at).localeCompare(String(a.at))).slice(0, 30);
  const props = (await db().collection("adsProposals").get()).docs.map((d) => ({ id: d.id, ...d.data() })).filter((p) => p.status === "pending");
  const last30 = Object.keys(daily).filter((k) => k > addDays(today, -30)).sort().map((k) => {
    const d = daily[k];
    return { day: k, spend: r2(num(d.meta && d.meta.spend) + num(d.etsy && d.etsy.spend)), sales: r2(num(d.site && d.site.adRevenue) + num(d.etsy && d.etsy.revenue)) };
  });
  const boosts = Object.values(state.boosts || {}).sort((a, b) => String(b.startedAt).localeCompare(String(a.startedAt)));
  let sales = [];
  try {
    const caps = {}; (state.posts || []).forEach((p) => { caps[p.id] = p.caption; }); Object.values(state.boosts || {}).forEach((b) => { caps[b.id] = caps[b.id] || b.caption; });
    sales = (await orderSales(`${month}-01`)).list.slice(0, 60).map((x) => ({ ...x, post: x.origin.post ? { id: x.origin.post, caption: caps[x.origin.post] || "" } : null }));
  } catch (e) { sales = []; }
  let etsyConnected = false;
  try { const a = await require("./etsy")._internal.readAuth(); etsyConnected = !!(a && a.shopId); } catch (e) { etsyConnected = false; }
  return {
    config: cfg, planned: plannedDaily(cfg), month, today, daysInMonth: daysInMonth(month), dayOfMonth: dayOfMonth(today),
    totals, meta: metaPublic(auth.meta), etsy: { connected: etsyConnected, advice: state.etsyAdvice || etsyAdvice(cfg, totals) },
    boosts, posts: (state.posts || []).map((p) => ({ ...p, never: !!(state.never || {})[p.id], boosted: !!(state.boosts || {})[p.id] })),
    lastRun: state.lastRun || null, log: logs, proposals: props, manual: manual.slice(0, 30), last30, minDaily: MIN_DAILY, sales,
  };
}

/* ---------- adminAds({action, ...}) ---------- */
async function adminAds(data, auth) {
  U.requireAdmin(auth);
  data = data || {};
  switch (data.action) {
    case "view":
    case undefined:
      return view();
    case "save": {
      const before = await config();
      const next = cleanConfig({ ...before, ...(data.config || {}), channels: { ...before.channels, ...((data.config || {}).channels || {}) }, rules: { ...before.rules, ...((data.config || {}).rules || {}) } });
      CHANNELS.forEach((k) => {
        const c = next.channels[k];
        if (c.on && c.daily < MIN_DAILY[k]) fail("invalid-argument", k === "tiktok" ? "TikTok only runs ads from $20 a day." : `The least a day is ${money(MIN_DAILY[k])}.`);
      });
      if (next.monthCap !== before.monthCap) { next.capAt = nowIso(); next.capBy = U.who(auth); }
      await doc("config").set(next);
      if (next.monthCap !== before.monthCap) await log("all", "cap", `Teto do mês aprovado: ${money(next.monthCap)} (antes ${money(before.monthCap)}).`, `Monthly cap approved: ${money(next.monthCap)} (was ${money(before.monthCap)}).`, { by: U.who(auth) });
      return view();
    }
    case "approve":
    case "decline": {
      const id = U.text(data.id, 80, { required: true });
      const ref = db().collection("adsProposals").doc(id);
      const p = (await ref.get()).data();
      if (!p || p.status !== "pending") fail("failed-precondition", "This proposal was already answered.");
      await ref.set({ status: data.action === "approve" ? "approved" : "declined", answeredAt: nowIso(), by: U.who(auth) }, { merge: true });
      if (data.action === "approve" && p.kind === "cap") {
        const cfg = await config();
        await doc("config").set({ ...cfg, monthCap: r2(p.to), capAt: nowIso(), capBy: U.who(auth) });
        await log("all", "cap", `Teto do mês aprovado: ${money(p.to)} (antes ${money(cfg.monthCap)}).`, `Monthly cap approved: ${money(p.to)} (was ${money(cfg.monthCap)}).`, { by: U.who(auth) });
      }
      return view();
    }
    case "connectMeta":
      await connectMeta(data, auth);
      return view();
    case "disconnectMeta": {
      const a = (await read("auth")) || {};
      delete a.meta;
      await doc("auth").set(a);
      await log("meta", "connect", "Meta desconectado do app (os anúncios que já estavam rodando continuam no Meta).", "Meta disconnected (ads already running keep running in Meta).");
      return view();
    }
    case "run": {
      await U.rateLimit("adsRun", auth.uid, 6, 3600);
      await run({ by: U.who(auth) });
      return view();
    }
    case "post": {
      // the owners decide about one post: boost now, pause, never boost, or let the robot choose again
      const id = U.text(data.id, 40, { required: true }).replace(/\D/g, "");
      const what = U.text(data.what, 10);
      const cfg = await config();
      const meta = ((await read("auth")) || {}).meta;
      const state = (await read("state")) || {};
      state.boosts = state.boosts || {}; state.never = state.never || {};
      const b = state.boosts[id];
      if (what === "never") { state.never[id] = true; if (b && b.status === "active") { await setAdset(meta, b, { status: "PAUSED" }); b.status = "stopped"; b.why = "owner"; } }
      else if (what === "allow") { delete state.never[id]; }
      else if (what === "pause") {
        if (!b || b.status !== "active") fail("failed-precondition", "This post isn't being boosted.");
        await setAdset(meta, b, { status: "PAUSED" }); b.status = "paused"; b.why = "owner"; b.pausedAt = nowIso();
        await log("meta", "pause", `Post ${short(b)} pausado por vocês.`, `Post ${short(b)} paused by you.`, { post: id, by: U.who(auth) });
      } else if (what === "boost") {
        if (!meta) fail("failed-precondition", "Instagram/Facebook isn't connected yet.");
        const totals = (await view()).totals;
        const activeDaily = Object.values(state.boosts).filter((x) => x.status === "active").reduce((t, x) => t + num(x.daily), 0);
        const month = monthOf(dayKey()), daysLeft = daysInMonth(month) - dayOfMonth(dayKey()) + 1;
        const daily = b ? num(b.daily) || cfg.rules.perPost : cfg.rules.perPost;
        if (totals.total + (activeDaily + daily) * daysLeft > cfg.monthCap + 0.01)
          fail("failed-precondition", `This would pass the monthly cap (${money(cfg.monthCap)}). Raise the cap or pause another post first.`);
        if (b) { await setAdset(meta, b, { status: "ACTIVE" }); b.status = "active"; b.why = ""; }
        else {
          const post = (state.posts || []).find((p) => p.id === id) || { id };
          const made = await boost(meta, state, post, daily);
          state.boosts[id] = { id, ...made, status: "active", startedAt: nowIso(), by: U.who(auth), caption: post.caption || "", permalink: post.permalink || "", thumb: post.thumb || "", spend: 0, clicks: 0, revenue: 0 };
        }
        delete state.never[id];
        await log("meta", "start", `Post ${short(state.boosts[id])} impulsionado por vocês (${money(state.boosts[id].daily)} por dia).`, `Post ${short(state.boosts[id])} boosted by you (${money(state.boosts[id].daily)} a day).`, { post: id, by: U.who(auth) });
      } else fail("invalid-argument", "Unknown choice.");
      await doc("state").set(state);
      return view();
    }
    case "manual": {
      const channel = CHANNELS.includes(data.channel) ? data.channel : fail("invalid-argument", "Pick a channel.");
      const amount = r2(num(data.amount));
      if (!(amount > 0) || amount > 10000) fail("invalid-argument", "Type how much was spent.");
      const date = /^\d{4}-\d{2}-\d{2}$/.test(String(data.date || "")) ? String(data.date) : dayKey();
      await db().collection("adsManual").add({ channel, amount, date, note: U.text(data.note, 120), at: nowIso(), by: U.who(auth) });
      await syncReports((await db().collection("adsManual").get()).docs.map((d) => d.data()));
      return view();
    }
    case "removeManual": {
      await db().collection("adsManual").doc(U.text(data.id, 80, { required: true })).delete();
      await syncReports((await db().collection("adsManual").get()).docs.map((d) => d.data()));
      return view();
    }
    default:
      fail("invalid-argument", "Unknown action.");
  }
}

module.exports = { adminAds, run, plan, originOf, orderSales, monthTotals, etsyAdvice, cleanConfig, plannedDaily, dayKey, dayStartSec, addDays, landing, minFromError, DEFAULTS,
  _internal: { graph, version: () => META_VERSION(), boost, recentPosts, metaDays, etsyDays, siteDays, syncReports, setPause: (ms) => { PAUSE_MS = ms; } } };
