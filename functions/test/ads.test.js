"use strict";
/* Anúncios (ads.js): the robot's plan (pause what spends without selling, fit the teto, grow what sells, boost the next
   best post), the month's totals and Etsy advice, saving the teto (approval), connecting Meta, a full morning run with
   Meta + Google Analytics answered by a fake fetch, and the Reports cost. */
const test = require("node:test");
const assert = require("node:assert/strict");
const { FakeDB, FakeAuth, FakeBucket } = require("./fakes");
const deps = require("../deps");

const ADMIN = { uid: "admin1", token: { admin: true, email: "owner@lhh.com" } };
const RULES = { perPost: 2, maxPosts: 3, maxPerPost: 5, stopAfter: 8, growRoas: 3, postDays: 90 };

function setup() {
  Object.assign(process.env, { ADMIN_EMAILS: "owner@lhh.com", SITE_URL: "https://littlehivehouse.com" });
  const db = new FakeDB();
  deps.set({ db, auth: new FakeAuth(), bucket: new FakeBucket() });
  db.docs.set("settings/store", { startupInvestment: 1000 });
  const pushes = [];
  require("../push").setSender(async (sub, payload) => { pushes.push(JSON.parse(payload)); return { statusCode: 201 }; });
  db.docs.set("adminPush/phone1", { endpoint: "https://push.example/1", keys: { p256dh: "k", auth: "a" } });
  require("../analytics")._reset();
  const A = require("../ads");
  A._internal.setPause(1);
  return { db, pushes, A };
}
const rep = (dims, mets, data) => ({ dimensionHeaders: dims.map((name) => ({ name })), metricHeaders: mets.map((name) => ({ name })),
  rows: data.map((r) => ({ dimensionValues: r.slice(0, dims.length).map((value) => ({ value: String(value) })), metricValues: r.slice(dims.length).map((value) => ({ value: String(value) })) })) });
const ok = (j) => ({ ok: true, status: 200, json: async () => j });

/** A fake internet: Meta's Graph API, Google's metadata server and GA4. `meta` answers by "METHOD path". */
function net({ meta = {}, ga = [] } = {}) {
  const calls = [];
  globalThis.fetch = async (url, init = {}) => {
    const u = new URL(url);
    if (u.host === "metadata.google.internal") return ok({ access_token: "ya29.fake", expires_in: 3600 });
    if (u.host === "analyticsdata.googleapis.com") {
      calls.push({ ga: JSON.parse(init.body) });
      return ok(rep(["date", "sessionSource", "sessionMedium", "sessionManualAdContent"], ["purchaseRevenue", "ecommercePurchases"], ga));
    }
    if (u.host === "graph.facebook.com") {
      const path = u.pathname.replace(/^\/v\d+\.\d+\//, "");
      const params = init.method === "POST" ? Object.fromEntries(new URLSearchParams(init.body.toString())) : Object.fromEntries(u.searchParams);
      calls.push({ method: init.method, path, params });
      const key = `${init.method} ${path}`;
      const h = meta[key] || Object.entries(meta).find(([k]) => k.endsWith("*") && key.startsWith(k.slice(0, -1)))?.[1];
      if (!h) return { ok: false, status: 400, json: async () => ({ error: { message: `no fake for ${key}` } }) };
      const out = typeof h === "function" ? h(params, path) : h;
      if (out && out.error) return { ok: false, status: 400, json: async () => out };
      return ok(out);
    }
    throw new Error(`unexpected fetch ${url}`);
  };
  return calls;
}
const META = { token: "EAAB" + "x".repeat(60), adAccountId: "act_123", pageId: "999", igUserId: "17841400000000000", accountName: "LHH", igUsername: "littlehivehouse" };

test("plan: stops what spent enough and sold nothing, grows what sells, boosts the next best posts", () => {
  const { A } = setup();
  const p = A.plan({
    boosts: [
      { id: "11111", daily: 2, spend: 9, clicks: 40, revenue: 0 },     // spent $9, no sale -> stop
      { id: "22222", daily: 2, spend: 6, clicks: 30, revenue: 30 },    // 5x return -> +$1
    ],
    allowed: 6, posts: [{ id: "33333" }, { id: "44444" }], rules: RULES, capReached: false,
  });
  assert.deepEqual(p.pause, [{ id: "11111", why: "no-sales" }]);
  assert.deepEqual(p.grow, [{ id: "22222", daily: 3 }]);
  assert.deepEqual(p.start, [{ id: "33333", daily: 2 }]);   // $3 + $2 fits the $6; a fourth $2 would not
});

test("plan: fills the room with new posts, never past maxPosts or the day's budget", () => {
  const { A } = setup();
  let p = A.plan({ boosts: [], allowed: 5, posts: [{ id: "1" }, { id: "2" }, { id: "3" }, { id: "4" }], rules: RULES, capReached: false });
  assert.deepEqual(p.start.map((s) => s.id), ["1", "2"]);   // $2 + $2, a third would be $6 > $5
  p = A.plan({ boosts: [], allowed: 50, posts: [{ id: "1" }, { id: "2" }, { id: "3" }, { id: "4" }], rules: RULES, capReached: false });
  assert.equal(p.start.length, 3);
});

test("plan: the teto reached pauses everything; a smaller budget pauses the weakest first", () => {
  const { A } = setup();
  const boosts = [{ id: "a", daily: 2, spend: 3, clicks: 5, revenue: 0 }, { id: "b", daily: 2, spend: 3, clicks: 20, revenue: 12 }];
  assert.deepEqual(A.plan({ boosts, allowed: 4, posts: [], rules: RULES, capReached: true }).pause.map((x) => x.why), ["cap", "cap"]);
  const p = A.plan({ boosts, allowed: 2.5, posts: [{ id: "c" }], rules: RULES, capReached: false });
  assert.deepEqual(p.pause, [{ id: "a", why: "budget" }]);
  assert.deepEqual(p.start, []);
});

test("plan: a Reel waiting takes the place of a photo that sold nothing; a photo that sells keeps its money", () => {
  const { A } = setup();
  const photo = { id: "ph", type: "image", daily: 1, spend: 0.5, clicks: 2, revenue: 0 };
  let p = A.plan({ boosts: [photo], allowed: 1, posts: [{ id: "rl", type: "reel" }, { id: "im", type: "image" }], rules: RULES, capReached: false });
  assert.deepEqual(p.pause, [{ id: "ph", why: "reel" }]);
  assert.deepEqual(p.start, [{ id: "rl", daily: 1 }]);
  // the photo sold: it stays; no room for the Reel today
  p = A.plan({ boosts: [{ ...photo, revenue: 12 }], allowed: 1, posts: [{ id: "rl", type: "reel" }], rules: RULES, capReached: false });
  assert.deepEqual(p.pause, []); assert.deepEqual(p.start, []);
  // a Reel boosted already is never swapped for another Reel
  p = A.plan({ boosts: [{ ...photo, type: "reel" }], allowed: 1, posts: [{ id: "rl", type: "reel" }], rules: RULES, capReached: false });
  assert.deepEqual(p.pause, []); assert.deepEqual(p.start, []);
  // with room in the budget, the Reel just starts too
  p = A.plan({ boosts: [photo], allowed: 5, posts: [{ id: "rl", type: "reel" }], rules: RULES, capReached: false });
  assert.deepEqual(p.pause, []); assert.deepEqual(p.start, [{ id: "rl", daily: 2 }]);
});

test("month totals and Etsy advice", () => {
  const { A } = setup();
  const daily = {
    "2026-11-01": { meta: { spend: 4 }, etsy: { spend: 2, orders: 0, revenue: 0 }, site: { orders: 2, revenue: 50, adOrders: 1, adRevenue: 20, meta: { orders: 1, revenue: 20 } } },
    "2026-11-02": { meta: { spend: 4 }, etsy: { spend: 7 } },
    "2026-10-31": { meta: { spend: 100 } },
  };
  const t = A.monthTotals(daily, [{ channel: "google", amount: 5, date: "2026-11-02" }, { channel: "google", amount: 9, date: "2026-10-02" }], "2026-11");
  assert.deepEqual(t.spend, { meta: 8, etsy: 9, google: 5, tiktok: 0, amazon: 0 });
  assert.equal(t.total, 22);
  assert.equal(t.sales.ads, 20);
  const cfg = A.cleanConfig({});
  assert.equal(A.etsyAdvice(cfg, t).kind, "stop");              // $9 on Etsy ads, no Etsy sale
  t.sales.etsy = 40;
  assert.equal(A.etsyAdvice(cfg, t).kind, "raise");             // 40 / 9 > 3
  assert.equal(A.etsyAdvice(A.cleanConfig({ channels: { etsy: { on: false } } }), t).kind, "off");
});

test("saving: the teto change is logged as approved; TikTok can't go under $20 a day", async () => {
  const { db, A } = setup();
  let v = await A.adminAds({ action: "view" }, ADMIN);
  assert.equal(v.config.monthCap, 200);
  assert.equal(v.planned, 6);                                     // $4 Meta + $2 Etsy
  await assert.rejects(A.adminAds({ action: "save", config: { channels: { tiktok: { on: true, daily: 5 } } } }, ADMIN), /\$20/);
  v = await A.adminAds({ action: "save", config: { monthCap: 150, channels: { meta: { daily: 3 } } } }, ADMIN);
  assert.equal(v.config.monthCap, 150);
  assert.equal(v.config.channels.meta.daily, 3);
  assert.equal(v.config.channels.etsy.daily, 2);                  // untouched
  assert.equal(v.config.capBy, "owner@lhh.com");
  assert.ok(v.log.some((l) => l.kind === "cap" && /150/.test(l.pt)));
  await assert.rejects(A.adminAds({ action: "view" }, { uid: "x", token: {} }), /admins/);
  assert.ok(db.get("ads/config"));
});

test("connect Meta: finds the ad account, the Little Hive page and its Instagram; the token never goes back to the app", async () => {
  const { db, A } = setup();
  net({ meta: {
    "GET me": { id: "55", name: "Hive Admin" },
    "GET me/adaccounts": { data: [{ id: "act_123", name: "Little Hive House", currency: "USD", account_status: 1 }] },
    "GET act_123": { id: "act_123", name: "Little Hive House", currency: "USD", account_status: 1 },
    "GET me/accounts": { data: [{ id: "777", name: "Other page" }, { id: "999", name: "Little Hive House", instagram_business_account: { id: "1784", username: "littlehivehouse" } }] },
  } });
  await assert.rejects(A.adminAds({ action: "connectMeta", token: "short" }, ADMIN), /doesn't look like/);
  const v = await A.adminAds({ action: "connectMeta", token: META.token }, ADMIN);
  assert.equal(v.meta.connected, true);
  assert.equal(v.meta.pageId, "999");
  assert.equal(v.meta.igUsername, "littlehivehouse");
  assert.equal(v.meta.tokenEnd, "xxxx");
  assert.equal(JSON.stringify(v).includes(META.token), false);
  assert.equal(db.get("ads/auth").meta.token, META.token);
});

test("a morning run: saves the days, boosts the best eligible post with a tracked link, notifies, and counts the cost in Reports", async () => {
  const { db, pushes, A } = setup();
  db.docs.set("ads/auth", { meta: META });
  const today = A.dayKey(), ymd = today.replace(/-/g, "");
  const calls = net({
    meta: {
      "GET act_123/insights": { data: [{ date_start: today, spend: "1.50", impressions: "300", inline_link_clicks: "9" }] },
      [`GET ${META.igUserId}/media`]: { data: [
        { id: "18000000000000001", caption: "Old one", timestamp: new Date(Date.now() - 400 * 86400000).toISOString(), like_count: 900, comments_count: 0 },
        { id: "18000000000000002", caption: "Not allowed", timestamp: new Date(Date.now() - 2 * 86400000).toISOString(), like_count: 80, comments_count: 1, boost_eligibility_info: { eligible_to_boost: false } },
        { id: "18000000000000003", caption: "Packing an order with me", timestamp: new Date(Date.now() - 2 * 86400000).toISOString(), like_count: 40, comments_count: 5 },
        { id: "18000000000000004", caption: "Fall collection", timestamp: new Date(Date.now() - 2 * 86400000).toISOString(), like_count: 10, comments_count: 0 },
      ] },
      "POST act_123/campaigns": { id: "c1" },
      "POST act_123/adsets": (p) => ({ id: `as-${p.name.slice(5, 22)}` }),
      "POST act_123/adcreatives": (p) => ({ id: `cr-${p.source_instagram_media_id}` }),
      "POST act_123/ads": (p) => ({ id: `ad-${p.adset_id}` }),
    },
    ga: [[ymd, "instagram", "paid", "18000000000000003", 24, 1], [ymd, "(direct)", "(none)", "(not set)", 30, 1]],
  });
  await A.adminAds({ action: "save", config: { channels: { etsy: { on: false } } } }, ADMIN);
  const r = await A.run({ by: "test" });
  assert.deepEqual(r.errors, {});
  const day = db.get(`adsDaily/${today}`);
  assert.equal(day.meta.spend, 1.5);
  assert.equal(day.site.adRevenue, 24);
  assert.equal(day.site.revenue, 54);
  // the campaign, then one ad set + creative + ad per post: the two best eligible recent posts ($2 + $2 fit the $4 a day)
  const camp = calls.find((c) => c.path === "act_123/campaigns");
  assert.equal(camp.params.objective, "OUTCOME_TRAFFIC");
  assert.equal(camp.params.special_ad_categories, "[]");
  const sets = calls.filter((c) => c.path === "act_123/adsets");
  assert.equal(sets.length, 2);
  assert.equal(sets[0].params.daily_budget, "200");
  assert.deepEqual(JSON.parse(sets[0].params.targeting).geo_locations, { countries: ["US"] });
  const cr = calls.filter((c) => c.path === "act_123/adcreatives");
  assert.deepEqual(cr.map((c) => c.params.source_instagram_media_id), ["18000000000000003", "18000000000000004"]);
  const link = JSON.parse(cr[0].params.call_to_action).value.link;
  assert.match(link, /^https:\/\/littlehivehouse\.com\/\?utm_source=instagram&utm_medium=paid&utm_campaign=hive-boost&utm_content=18000000000000003$/);
  assert.equal(cr[0].params.instagram_user_id, META.igUserId);
  assert.equal(cr[0].params.object_id, "999");
  const st = db.get("ads/state");
  assert.equal(st.boosts["18000000000000003"].status, "active");
  assert.equal(st.metaCampaignId, "c1");
  assert.equal(st.boosts["18000000000000002"], undefined);       // not eligible
  assert.equal(st.boosts["18000000000000001"], undefined);       // older than 90 days
  assert.ok(pushes.some((p) => /Anúncios/.test(p.title) && /2 mudanças/.test(p.body)));
  assert.equal(db.get("settings/store").adSpendByDay[today], 1.5);
  const v = await A.adminAds({ action: "view" }, ADMIN);
  assert.equal(v.boosts.length, 2);
  assert.equal(v.totals.spend.meta, 1.5);
  assert.ok(v.log.filter((l) => l.kind === "start").length === 2);
});

test("the next run pauses a post that spent past the limit without a sale, and keeps one that sells", async () => {
  const { db, A } = setup();
  db.docs.set("ads/auth", { meta: META });
  db.docs.set("ads/config", { ...A.DEFAULTS, channels: { ...A.DEFAULTS.channels, etsy: { on: false, daily: 2 } } });
  db.docs.set("ads/state", { metaCampaignId: "c1", boosts: {
    "18000000000000003": { id: "18000000000000003", adsetId: "as3", adId: "ad3", daily: 2, status: "active", caption: "Packing" },
    "18000000000000004": { id: "18000000000000004", adsetId: "as4", adId: "ad4", daily: 2, status: "active", caption: "Fall" },
  } });
  const ymd = A.dayKey().replace(/-/g, "");
  const calls = net({
    meta: {
      "GET act_123/insights": { data: [] },
      "GET ad3/insights": { data: [{ spend: "4.00", inline_link_clicks: "30" }] },
      "GET ad4/insights": { data: [{ spend: "9.10", inline_link_clicks: "12" }] },
      [`GET ${META.igUserId}/media`]: { data: [] },
      "POST as4": { success: true },
      "POST as3": { success: true },
    },
    ga: [[ymd, "instagram", "paid", "18000000000000003", 24, 1]],
  });
  await A.run();
  const st = db.get("ads/state");
  assert.equal(st.boosts["18000000000000004"].status, "stopped");
  assert.equal(st.boosts["18000000000000003"].status, "active");
  assert.equal(st.boosts["18000000000000003"].revenue, 24);
  const pause = calls.find((c) => c.path === "as4");
  assert.equal(pause.params.status, "PAUSED");
  // 24 / 4 = 6x return after more than $3: one more dollar a day, since $3 still fits the $4 a day for Meta
  assert.equal(calls.find((c) => c.path === "as3").params.daily_budget, "300");
  assert.equal(st.boosts["18000000000000003"].daily, 3);
  const v = await A.adminAds({ action: "view" }, ADMIN);
  assert.ok(v.log.some((l) => l.kind === "pause" && /\$9\.10/.test(l.pt)));
});

test("a Meta error never breaks the run: it goes in the log and the page shows it", async () => {
  const { db, A } = setup();
  db.docs.set("ads/auth", { meta: META });
  net({ meta: {
    "GET act_123/insights": { error: { message: "Invalid OAuth access token.", code: 190 } },
    [`GET ${META.igUserId}/media`]: { data: [{ id: "18000000000000003", caption: "x", timestamp: new Date(Date.now() - 2 * 86400000).toISOString(), like_count: 1 }] },
    "POST act_123/campaigns": { error: { message: "Ad account has no payment method", code: 100 } },
  } });
  const r = await A.run();
  assert.match(r.errors.meta, /payment method|OAuth/);
  const v = await A.adminAds({ action: "view" }, ADMIN);
  assert.ok(v.log.some((l) => l.kind === "error" && /payment method/.test(l.pt)));
  assert.equal(v.lastRun.errors.meta != null, true);
});

test("Meta's minimum budget message is understood", () => {
  const { A } = setup();
  assert.equal(A.minFromError(new Error("Meta: Your budget is too low. The minimum budget for this ad set is $2.50.")), 2.5);
  assert.equal(A.minFromError(new Error("Meta: Invalid parameter")), null);
  assert.equal(A.minFromError(new Error("Meta: Daily budget must be at least $2.50 for this objective")), 2.5);
});

test("spend logged by hand counts in the month and in Reports, and can be removed", async () => {
  const { db, A } = setup();
  const today = A.dayKey();
  let v = await A.adminAds({ action: "manual", channel: "google", amount: 12.5, date: today, note: "Google Ads test" }, ADMIN);
  assert.equal(v.totals.spend.google, 12.5);
  assert.equal(db.get("settings/store").adSpendByDay[today], 12.5);
  await assert.rejects(A.adminAds({ action: "manual", channel: "google", amount: 0 }, ADMIN), /how much/);
  v = await A.adminAds({ action: "removeManual", id: v.manual[0].id }, ADMIN);
  assert.equal(v.totals.spend.google, 0);
  assert.equal(db.get("settings/store").adSpendByDay[today], undefined);
});

test("a proposal to raise the teto changes it only when approved", async () => {
  const { db, A } = setup();
  db.docs.set("adsProposals/p1", { status: "pending", kind: "cap", from: 200, to: 300, pt: "Subir?" });
  let v = await A.adminAds({ action: "view" }, ADMIN);
  assert.equal(v.proposals.length, 1);
  v = await A.adminAds({ action: "approve", id: "p1" }, ADMIN);
  assert.equal(v.config.monthCap, 300);
  assert.equal(v.proposals.length, 0);
  await assert.rejects(A.adminAds({ action: "decline", id: "p1" }, ADMIN), /already answered/);
});

test("days in New York time", () => {
  const { A } = setup();
  assert.equal(A.dayKey(Date.parse("2026-11-18T03:00:00Z")), "2026-11-17");   // 10 pm in New York
  assert.equal(A.dayStartSec("2026-11-18"), Date.parse("2026-11-18T05:00:00Z") / 1000);
  assert.equal(A.dayStartSec("2026-07-04"), Date.parse("2026-07-04T04:00:00Z") / 1000);
  assert.equal(A.addDays("2026-11-30", 1), "2026-12-01");
});

test("where each sale came from: an ad (which post), a normal Instagram post, Google, email or nothing", () => {
  const { A } = setup();
  assert.deepEqual(A.originOf({ source: "instagram", medium: "paid", campaign: "hive-boost", content: "18000000000000003" }),
    { kind: "ad", channel: "meta", post: "18000000000000003", campaign: "hive-boost", source: "instagram" });
  assert.equal(A.originOf({ source: "l.instagram.com", medium: "referral" }).kind, "social");
  assert.equal(A.originOf({ source: "google", medium: "cpc" }).kind, "ad");
  assert.equal(A.originOf({ source: "google.com", medium: "referral" }).kind, "search");
  assert.equal(A.originOf({ source: "newsletter", medium: "email" }).kind, "email");
  assert.equal(A.originOf(null).kind, "direct");
});

test("the orders themselves count for the post that brought them, even when Google Analytics missed it", async () => {
  const { db, A } = setup();
  db.docs.set("ads/auth", { meta: META });
  db.docs.set("ads/config", { ...A.DEFAULTS, channels: { ...A.DEFAULTS.channels, etsy: { on: false, daily: 2 } } });
  db.docs.set("ads/state", { metaCampaignId: "c1", boosts: { "18000000000000003": { id: "18000000000000003", adsetId: "as3", adId: "ad3", daily: 2, status: "active", caption: "Packing" } } });
  const now = new Date().toISOString();
  db.docs.set("orders/o1", { number: "LHH-1012", status: "paid", createdAt: now, paidAt: now, pricing: { total: 26.5, tax: 2.5 },
    ref: { source: "instagram", medium: "paid", campaign: "hive-boost", content: "18000000000000003" } });
  db.docs.set("orders/o2", { number: "LHH-1013", status: "paid", createdAt: now, paidAt: now, pricing: { total: 10 }, ref: { source: "l.instagram.com", medium: "referral" } });
  db.docs.set("orders/o3", { number: "LHH-1014", status: "pending", createdAt: now, pricing: { total: 99 }, ref: { source: "instagram", medium: "paid", content: "18000000000000003" } });
  net({ meta: { "GET act_123/insights": { data: [] }, "GET ad3/insights": { data: [{ spend: "9.00", inline_link_clicks: "30" }] }, [`GET ${META.igUserId}/media`]: { data: [] } }, ga: [] });
  await A.run();
  const st = db.get("ads/state");
  assert.equal(st.boosts["18000000000000003"].revenue, 24);           // $26.50 - $2.50 tax; the unpaid one doesn't count
  assert.equal(st.boosts["18000000000000003"].status, "active");      // it sold, so it isn't stopped at $9
  assert.equal(db.get(`adsDaily/${A.dayKey()}`).site.meta.revenue, 24);
  const v = await A.adminAds({ action: "view" }, ADMIN);
  assert.deepEqual(v.sales.map((x) => [x.number, x.origin.kind]).sort(), [["LHH-1012", "ad"], ["LHH-1013", "social"]]);
  assert.equal(v.sales.find((x) => x.number === "LHH-1012").post.caption, "Packing");
});

test("posts: Reels come first, then the most liked; a post less than a day old waits", async () => {
  const { A } = setup();
  const old = new Date(Date.now() - 3 * 86400000).toISOString();
  globalThis.fetch = async () => ({ ok: true, status: 200, json: async () => ({ data: [
    { id: "p1", caption: "Welcome", media_type: "IMAGE", media_product_type: "FEED", timestamp: old, like_count: 90, comments_count: 4 },
    { id: "r1", caption: "Packing", media_type: "VIDEO", media_product_type: "REELS", timestamp: old, like_count: 12, comments_count: 1 },
    { id: "r2", caption: "Tonight", media_type: "VIDEO", media_product_type: "REELS", timestamp: new Date().toISOString(), like_count: 30, comments_count: 0 },
  ] }) });
  const posts = await A._internal.recentPosts(META, RULES);
  assert.deepEqual(posts.map((p) => p.id), ["r2", "r1", "p1"]);
  assert.equal(posts[0].type, "reel");
});
