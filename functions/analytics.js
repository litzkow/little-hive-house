"use strict";
/* Visits report for the Hive Admin ("Visitas"), read from Google Analytics 4 (the G-VHW80371B0 tag on every store page,
   property 562104666) through the GA4 Data API.
   The functions run as the project's default compute service account; it was added as a Viewer ("Leitor") in the
   property's access management, and its token comes from the metadata server with the analytics.readonly scope.
   adminAnalytics({range}) : the whole report for 7, 28 or 90 days or 12 months, compared with the period before.
                             Kept 15 minutes in analyticsCache/{range} so the page opens fast; {refresh:true} skips it.
   adminAnalyticsLive()    : who is on the site right now (last 30 minutes), polled by the page while it is open.
   warm()                  : every 3 hours, refreshes the 28-day report and writes analyticsCache/status (ok or the error). */

const { fail } = require("./config");
const deps = require("./deps");
const U = require("./util");

const PROPERTY = process.env.GA_PROPERTY || "562104666";
const API = `https://analyticsdata.googleapis.com/v1beta/properties/${PROPERTY}`;
const SCOPE = "https://www.googleapis.com/auth/analytics.readonly";
const RANGES = { "7d": 7, "28d": 28, "90d": 90, "12m": 365 };
const CACHE_MS = 15 * 60 * 1000;

let tokenCache = null;
async function token() {
  if (tokenCache && tokenCache.exp > Date.now() + 60000) return tokenCache.value;
  const url = "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token?scopes=" + encodeURIComponent(SCOPE);
  let res;
  try { res = await globalThis.fetch(url, { headers: { "Metadata-Flavor": "Google" } }); } catch (e) { res = null; }
  const j = res && res.ok ? await res.json().catch(() => null) : null;
  if (!j || !j.access_token) fail("unavailable", "Couldn't get permission to read Google Analytics. Try again in a minute.");
  tokenCache = { value: j.access_token, exp: Date.now() + (Number(j.expires_in) || 300) * 1000 };
  return tokenCache.value;
}

async function ga(path, body) {
  const res = await globalThis.fetch(`${API}:${path}`, {
    method: "POST",
    headers: { Authorization: `Bearer ${await token()}`, "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const j = await res.json().catch(() => null);
  if (!res.ok) {
    const st = (j && j.error && j.error.status) || "";
    const msg = (j && j.error && j.error.message) || `HTTP ${res.status}`;
    console.warn("[analytics]", res.status, st, msg);
    if (st === "PERMISSION_DENIED" && /has not been used|disabled/i.test(msg)) fail("failed-precondition", "The Google Analytics Data API is off for this project. It turns on with the next update of the store.");
    if (st === "PERMISSION_DENIED") fail("failed-precondition", "Google Analytics hasn't given the shop access yet. In Google Analytics, Admin, Property access management, add 752604920358-compute@developer.gserviceaccount.com as Viewer.");
    if (st === "RESOURCE_EXHAUSTED") fail("resource-exhausted", "Google Analytics asked us to slow down. Try again in an hour.");
    fail("aborted", `Google Analytics didn't answer: ${msg}`);
  }
  return j || {};
}

/* ---------- reading the answers ---------- */
const num = (v) => { const n = Number(v); return Number.isFinite(n) ? n : 0; };
function rows(rep) {
  const dims = (rep.dimensionHeaders || []).map((d) => d.name), mets = (rep.metricHeaders || []).map((m) => m.name);
  return (rep.rows || []).map((r) => {
    const o = {};
    dims.forEach((d, i) => { o[d] = r.dimensionValues[i].value; });
    mets.forEach((m, i) => { o[m] = num(r.metricValues[i].value); });
    return o;
  });
}
const NOT_SET = new Set(["(not set)", "(other)", ""]);
function list(rep, dim, metric, n) {
  return rows(rep).filter((r) => !NOT_SET.has(r[dim]))
    .map((r) => ({ name: r[dim], value: r[metric] })).sort((a, b) => b.value - a.value).slice(0, n || 50);
}

/** The dateRanges for `days` (the current period ends today) and the same length right before it. */
function periods(days) {
  return [{ startDate: `${days - 1}daysAgo`, endDate: "today", name: "cur" }, { startDate: `${2 * days - 1}daysAgo`, endDate: `${days}daysAgo`, name: "prev" }];
}

const TOTALS = ["activeUsers", "newUsers", "sessions", "screenPageViews", "averageSessionDuration", "engagementRate", "userEngagementDuration", "purchaseRevenue", "ecommercePurchases", "addToCarts"];

function requests(days) {
  const cur = [periods(days)[0]];
  const by = (dim, metrics, opts = {}) => ({ dateRanges: cur, dimensions: [].concat(dim).map((name) => ({ name })), metrics: metrics.map((name) => ({ name })),
    orderBys: [{ metric: { metricName: metrics[0] }, desc: true }], limit: opts.limit || 50, ...(opts.filter ? { dimensionFilter: opts.filter } : {}) });
  return [
    [
      { dateRanges: periods(days), metrics: TOTALS.map((name) => ({ name })) },
      { dateRanges: cur, dimensions: [{ name: "date" }], metrics: [{ name: "activeUsers" }, { name: "sessions" }, { name: "screenPageViews" }], orderBys: [{ dimension: { dimensionName: "date" } }], limit: 400 },
      by("country", ["activeUsers", "sessions"], { limit: 30 }),
      by("region", ["activeUsers"], { limit: 60, filter: { filter: { fieldName: "countryId", stringFilter: { value: "US" } } } }),
      by(["city", "region", "countryId"], ["activeUsers"], { limit: 30 }),
    ],
    [
      by("userAgeBracket", ["activeUsers"]),
      by("userGender", ["activeUsers"]),
      by("newVsReturning", ["activeUsers"]),
      by("sessionDefaultChannelGroup", ["sessions", "activeUsers"]),
      by("sessionSource", ["sessions"], { limit: 15 }),
    ],
    [
      by("deviceCategory", ["activeUsers"]),
      by("operatingSystem", ["activeUsers"], { limit: 8 }),
      by("pagePath", ["screenPageViews", "activeUsers", "userEngagementDuration"], { limit: 100 }),
      by("eventName", ["eventCount", "totalUsers"], { limit: 40 }),
      by(["itemName", "itemCategory"], ["itemsViewed", "itemsAddedToCart", "itemsPurchased"], { limit: 25 }),
    ],
    [
      { dateRanges: cur, dimensions: [{ name: "dayOfWeek" }, { name: "hour" }], metrics: [{ name: "sessions" }], limit: 200 },
      by("landingPage", ["sessions"], { limit: 12 }),
    ],
  ];
}

/* "/collections/fall.html" -> "fall"; the shop's pages by name */
const PAGE_NAMES = { "/": "Home", "/shop": "Shop", "/photo-magnets": "Photo magnets", "/big-orders": "Big orders", "/order": "Checkout",
  "/thank-you": "Thank you", "/favorites": "Favorites", "/account": "Account", "/orders": "My orders", "/track": "Track order", "/contact": "Contact",
  "/shipping": "Shipping", "/returns": "Returns", "/privacy": "Privacy", "/terms": "Terms", "/suggestions": "Suggestions" };
function cleanPath(p) { return (String(p || "/").split("?")[0].replace(/\.html$/, "").replace(/\/index$/, "").replace(/\/+$/, "") || "/"); }

/** Pure: the GA answers -> the report the page draws. */
function shape(batches, days) {
  const [A, B, C, D] = batches.map((b) => (b && b.reports) || []);
  const tot = { cur: {}, prev: {} };
  rows(A[0] || {}).forEach((r) => { const k = r.dateRange === "prev" || r.dateRange === "date_range_1" ? "prev" : "cur"; tot[k] = r; });
  const pick = (o) => Object.fromEntries(TOTALS.map((m) => [m, num(o[m])]));
  const series = rows(A[1] || {}).map((r) => ({ date: `${r.date.slice(0, 4)}-${r.date.slice(4, 6)}-${r.date.slice(6, 8)}`, users: r.activeUsers, visits: r.sessions, views: r.screenPageViews }));

  const pages = {}, collections = {};
  rows(C[2] || {}).forEach((r) => {
    const p = cleanPath(r.pagePath);
    const x = pages[p] || (pages[p] = { path: p, views: 0, users: 0, seconds: 0 });
    x.views += r.screenPageViews; x.users += r.activeUsers; x.seconds += r.userEngagementDuration;
    const m = /^\/collections\/([a-z0-9-]+)$/.exec(p);
    if (m) {
      const c = collections[m[1]] || (collections[m[1]] = { slug: m[1], views: 0, users: 0, seconds: 0 });
      c.views += r.screenPageViews; c.users += r.activeUsers; c.seconds += r.userEngagementDuration;
    }
  });
  const pageList = Object.values(pages).map((x) => ({ ...x, name: PAGE_NAMES[x.path] || null, avgSeconds: x.users ? Math.round(x.seconds / x.users) : 0 }))
    .sort((a, b) => b.views - a.views).slice(0, 25);
  const colList = Object.values(collections).map((x) => ({ ...x, avgSeconds: x.users ? Math.round(x.seconds / x.users) : 0 })).sort((a, b) => b.views - a.views);

  const ev = {};
  rows(C[3] || {}).forEach((r) => { ev[r.eventName] = { count: r.eventCount, users: r.totalUsers }; });
  const step = (name) => (ev[name] ? ev[name].users : 0);
  const funnel = [["page_view", "Visited"], ["view_item", "Looked at a magnet"], ["add_to_cart", "Added to cart"], ["begin_checkout", "Went to checkout"], ["purchase", "Bought"]]
    .map(([k, label]) => ({ key: k, label, users: step(k) }));
  if (funnel[0].users === 0) funnel[0].users = num(tot.cur.activeUsers);

  const heat = Array.from({ length: 7 }, () => Array(24).fill(0));
  rows(D[0] || {}).forEach((r) => { const d = Number(r.dayOfWeek), hr = Number(r.hour); if (heat[d] && hr >= 0 && hr < 24) heat[d][hr] += r.sessions; });

  return {
    days, property: PROPERTY,
    totals: pick(tot.cur), previous: pick(tot.prev),
    series,
    countries: list(A[2] || {}, "country", "activeUsers", 30),
    states: list(A[3] || {}, "region", "activeUsers", 60),
    cities: rows(A[4] || {}).filter((r) => !NOT_SET.has(r.city)).map((r) => ({ name: r.city, region: NOT_SET.has(r.region) ? "" : r.region, country: r.countryId, value: r.activeUsers }))
      .sort((a, b) => b.value - a.value).slice(0, 25),
    age: list(B[0] || {}, "userAgeBracket", "activeUsers").sort((a, b) => a.name.localeCompare(b.name)),
    gender: list(B[1] || {}, "userGender", "activeUsers"),
    newVsReturning: list(B[2] || {}, "newVsReturning", "activeUsers"),
    channels: list(B[3] || {}, "sessionDefaultChannelGroup", "sessions", 12),
    sources: list(B[4] || {}, "sessionSource", "sessions", 15),
    devices: list(C[0] || {}, "deviceCategory", "activeUsers"),
    os: list(C[1] || {}, "operatingSystem", "activeUsers", 8),
    pages: pageList,
    collections: colList,
    events: ev,
    funnel,
    items: rows(C[4] || {}).filter((r) => !NOT_SET.has(r.itemName)).map((r) => ({ name: r.itemName, category: NOT_SET.has(r.itemCategory) ? "" : r.itemCategory,
      viewed: r.itemsViewed, added: r.itemsAddedToCart, bought: r.itemsPurchased })).sort((a, b) => (b.viewed + b.added * 3) - (a.viewed + a.added * 3)).slice(0, 20),
    heat,
    landing: list(D[1] || {}, "landingPage", "sessions", 12).map((x) => ({ ...x, path: cleanPath(x.name), name: PAGE_NAMES[cleanPath(x.name)] || null })),
  };
}

async function fetchReport(days) {
  const batches = await Promise.all(requests(days).map((reqs) => ga("batchRunReports", { requests: reqs })));
  return shape(batches, days);
}

async function adminAnalytics(data, auth) {
  U.requireAdmin(auth);
  const range = RANGES[data.range] ? data.range : "28d";
  const ref = deps.db().collection("analyticsCache").doc(range);
  if (!data.refresh) {
    const snap = await ref.get();
    const c = snap.exists ? snap.data() : null;
    if (c && c.report && Date.now() - Date.parse(c.at) < CACHE_MS) return { ...c.report, range, at: c.at, cached: true };
  }
  const report = await fetchReport(RANGES[range]);
  const at = new Date().toISOString();
  await ref.set({ at, report }).catch((e) => console.warn("[analytics] cache", e.message));
  return { ...report, range, at, cached: false };
}

/* ---------- right now (GA realtime: the last 30 minutes) ---------- */
function shapeLive(answers) {
  const [total, places, screens, minutes, devices] = answers;
  const perMin = Array(30).fill(0);
  rows(minutes || {}).forEach((r) => { const m = Number(r.minutesAgo); if (m >= 0 && m < 30) perMin[m] += r.activeUsers; });
  return {
    now: num((rows(total || {})[0] || {}).activeUsers),
    places: rows(places || {}).filter((r) => !NOT_SET.has(r.country)).map((r) => ({ city: NOT_SET.has(r.city) ? "" : r.city, country: r.country, value: r.activeUsers }))
      .sort((a, b) => b.value - a.value).slice(0, 10),
    pages: list(screens || {}, "unifiedScreenName", "activeUsers", 10),
    devices: list(devices || {}, "deviceCategory", "activeUsers", 5),
    perMinute: perMin.reverse(),   // oldest first, the last one is this minute
  };
}
async function adminAnalyticsLive(data, auth) {
  U.requireAdmin(auth);
  const rt = (dims) => ga("runRealtimeReport", { dimensions: dims.map((name) => ({ name })), metrics: [{ name: "activeUsers" }], limit: 50 });
  const answers = await Promise.all([rt([]), rt(["city", "country"]), rt(["unifiedScreenName"]), rt(["minutesAgo"]), rt(["deviceCategory"])]);
  return { ...shapeLive(answers), at: new Date().toISOString() };
}

/* ---------- every 3 hours: a fresh 28-day report, and a status the maintenance check can read ---------- */
async function warm() {
  const status = deps.db().collection("analyticsCache").doc("status");
  try {
    const report = await fetchReport(28);
    const at = new Date().toISOString();
    await deps.db().collection("analyticsCache").doc("28d").set({ at, report });
    await status.set({ ok: true, at, users: report.totals.activeUsers, visits: report.totals.sessions, error: null });
    return { ok: true, users: report.totals.activeUsers };
  } catch (e) {
    await status.set({ ok: false, at: new Date().toISOString(), error: String(e.message || e).slice(0, 400) }).catch(() => {});
    return { ok: false, error: e.message };
  }
}

module.exports = { adminAnalytics, adminAnalyticsLive, warm, shape, shapeLive, requests, periods, cleanPath, RANGES,
  _reset: () => { tokenCache = null; } };
