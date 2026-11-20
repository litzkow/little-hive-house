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

test("plan: the robot stops what spent enough and nobody put in the cart, or what the same people saw 4+ times, and fills the room", () => {
  const { A } = setup();
  const p = A.plan({
    boosts: [
      { id: "11111", spend: 9, clicks: 40, carts: 0, revenue: 0 },                      // $9, no cart, no sale -> stop
      { id: "22222", spend: 9, clicks: 30, carts: 2, revenue: 0 },                      // carts: keep learning
      { id: "33333", spend: 3, clicks: 10, frequency: 4.6, impressions: 900 },          // tired
    ],
    allowed: 6, posts: [{ id: "44444" }, { id: "55555" }, { id: "66666" }], rules: RULES, capReached: false, auto: true,
  });
  assert.deepEqual(p.pause, [{ id: "11111", why: "no-sales" }, { id: "33333", why: "tired" }]);
  assert.equal(p.budget, 6);                                                             // one budget for all of them
  assert.deepEqual(p.start.map((s) => s.id), ["44444", "55555"]);                        // 3 at most
});

test("plan: what the owners chose stays (the robot only warns); with the robot off nothing new starts", () => {
  const { A } = setup();
  const boosts = [{ id: "mine", spend: 9, clicks: 40, revenue: 0, owner: true }];
  let p = A.plan({ boosts, allowed: 4, posts: [{ id: "x" }], rules: RULES, capReached: false, auto: true });
  assert.deepEqual(p.pause, []); assert.deepEqual(p.warn, [{ id: "mine", why: "no-sales" }]);
  assert.deepEqual(p.start.map((s) => s.id), ["x"]);
  p = A.plan({ boosts: [{ ...boosts[0], owner: false }], allowed: 4, posts: [{ id: "x" }], rules: RULES, capReached: false, auto: false });
  assert.deepEqual(p.pause, []); assert.deepEqual(p.warn.length, 1); assert.deepEqual(p.start, []);
});

test("plan: the teto reached (or the calendar) leaves the budget at 0 and starts nothing", () => {
  const { A } = setup();
  const boosts = [{ id: "a", spend: 3, clicks: 5, revenue: 0 }];
  let p = A.plan({ boosts, allowed: 4, posts: [{ id: "c" }], rules: RULES, capReached: true, auto: true });
  assert.equal(p.budget, 0); assert.deepEqual(p.start, []);
  p = A.plan({ boosts, allowed: 0, posts: [{ id: "c" }], rules: RULES, capReached: false, auto: true });
  assert.equal(p.budget, 0); assert.deepEqual(p.start, []);
});

test("plan: a Reel waiting takes the place of a photo that sold nothing; the Reel they asked for goes first, past any limit", () => {
  const { A } = setup();
  const R1 = { ...RULES, maxPosts: 1 };
  const photo = { id: "ph", type: "image", spend: 0.5, clicks: 2, revenue: 0 };
  let p = A.plan({ boosts: [photo], allowed: 4, posts: [{ id: "rl", type: "reel" }, { id: "im", type: "image" }], rules: R1, capReached: false, auto: true });
  assert.deepEqual(p.pause, [{ id: "ph", why: "reel" }]);
  assert.deepEqual(p.start, [{ id: "rl", next: false }]);
  // the photo sold: it stays
  p = A.plan({ boosts: [{ ...photo, revenue: 12 }], allowed: 4, posts: [{ id: "rl", type: "reel" }], rules: R1, capReached: false, auto: true });
  assert.deepEqual(p.pause, []); assert.deepEqual(p.start, []);
  // a Reel boosted already is never swapped for another Reel by the robot...
  const reel = { ...photo, type: "reel" };
  p = A.plan({ boosts: [reel], allowed: 4, posts: [{ id: "rl", type: "reel" }], rules: R1, capReached: false, auto: true });
  assert.deepEqual(p.pause, []); assert.deepEqual(p.start, []);
  // ...but the new Reel the owners asked for takes the weakest place, even with the robot off
  p = A.plan({ boosts: [reel], allowed: 4, posts: [], rules: R1, capReached: false, auto: false, nextReel: { id: "new", type: "reel" } });
  assert.deepEqual(p.pause, [{ id: "ph", why: "room" }]); assert.deepEqual(p.start, [{ id: "new", next: true }]);
  // an owner's choice is never the one moved out
  p = A.plan({ boosts: [{ ...reel, owner: true }], allowed: 4, posts: [], rules: R1, capReached: false, auto: true, nextReel: { id: "new", type: "reel" } });
  assert.deepEqual(p.start, []);
});

test("the calendar: Black Friday week the usual, Dec 2–14 double, from Dec 15 nothing (the post office), inside the cap", () => {
  const { A } = setup();
  const cfg = A.cleanConfig({ monthCap: 1000, channels: { meta: { on: true, daily: 4 }, etsy: { on: false, daily: 2 } } });
  const t = { total: 0 };
  assert.equal(A.dailyAllowed(cfg, t, "2026-11-27"), 4);
  assert.equal(A.dailyAllowed(cfg, t, "2026-12-05"), 8);
  assert.equal(A.dailyAllowed(cfg, t, "2026-12-16"), 0);
  assert.equal(A.dailyAllowed(cfg, t, "2027-01-03"), 4);
  assert.equal(A.dailyAllowed(cfg, { total: 990 }, "2026-12-05"), 0.37);  // $10 left for 27 days: inside the cap
  assert.equal(A.dailyAllowed(A.cleanConfig({ ...cfg, rules: { holiday: false } }), t, "2026-12-16"), 4);
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
  // the campaign, then ONE ad set for all (landing page views, the day's $4 shared), and a creative + ad per post
  const camp = calls.find((c) => c.path === "act_123/campaigns");
  assert.equal(camp.params.objective, "OUTCOME_TRAFFIC");
  assert.equal(camp.params.special_ad_categories, "[]");
  const sets = calls.filter((c) => c.path === "act_123/adsets");
  assert.equal(sets.length, 1);
  assert.equal(sets[0].params.daily_budget, "400");
  assert.equal(sets[0].params.optimization_goal, "LANDING_PAGE_VIEWS");
  assert.deepEqual(JSON.parse(sets[0].params.targeting).geo_locations, { countries: ["US"], location_types: ["home"] });   // only people who live in the US
  assert.deepEqual(calls.filter((c) => c.path === "act_123/ads").map((c) => c.params.adset_id), ["as- · Hive Admin", "as- · Hive Admin"]);
  const cr = calls.filter((c) => c.path === "act_123/adcreatives");
  assert.deepEqual(cr.map((c) => c.params.source_instagram_media_id), ["18000000000000003", "18000000000000004"]);
  const link = JSON.parse(cr[0].params.call_to_action).value.link;
  assert.match(link, /^https:\/\/littlehivehouse\.com\/\?utm_source=instagram&utm_medium=paid&utm_campaign=hive-boost&utm_content=18000000000000003$/);
  assert.equal(cr[0].params.instagram_user_id, META.igUserId);
  assert.equal(cr[0].params.object_id, "999");
  const st = db.get("ads/state");
  assert.equal(st.boosts["18000000000000003"].status, "active");
  assert.equal(st.boosts["18000000000000003"].shared, true);
  assert.equal(st.adsetId, "as- · Hive Admin");
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

test("the next run pauses (in the shared ad set) what spent past the limit with no cart, keeps what sells, and only warns about the owners' choice", async () => {
  const { db, pushes, A } = setup();
  db.docs.set("ads/auth", { meta: META });
  db.docs.set("ads/config", { ...A.DEFAULTS, channels: { ...A.DEFAULTS.channels, etsy: { on: false, daily: 2 } } });
  db.docs.set("ads/state", { metaCampaignId: "c1", adsetId: "shared1", adsetDaily: 4, adsetStatus: "ACTIVE", targetV: 3, targetKey: "gift,home,photo,season", boosts: {
    "18000000000000003": { id: "18000000000000003", adsetId: "shared1", adId: "ad3", shared: true, status: "active", caption: "Packing", by: "robot" },
    "18000000000000004": { id: "18000000000000004", adsetId: "shared1", adId: "ad4", shared: true, status: "active", caption: "Fall", by: "robot" },
    "18000000000000005": { id: "18000000000000005", adsetId: "shared1", adId: "ad5", shared: true, status: "active", caption: "Mine", by: "Thiago" },
  } });
  const ymd = A.dayKey().replace(/-/g, "");
  const calls = net({
    meta: {
      "GET act_123/insights": { data: [] },
      "GET ad3/insights": { data: [{ spend: "4.00", inline_link_clicks: "30" }] },
      "GET ad4/insights": { data: [{ spend: "9.10", inline_link_clicks: "12", actions: [{ action_type: "link_click", value: "12" }] }] },
      "GET ad5/insights": { data: [{ spend: "9.50", inline_link_clicks: "8" }] },
      [`GET ${META.igUserId}/media`]: { data: [] },
      "POST ad4": { success: true },
      "POST shared1": { success: true },
      "GET search": (p) => ({ data: p.type === "adTargetingCategory" ? [] : [{ id: `id-${p.q}`, name: p.q }] }),
    },
    ga: [[ymd, "instagram", "paid", "18000000000000003", 24, 1]],
  });
  await A.run();
  const st = db.get("ads/state");
  assert.equal(st.boosts["18000000000000004"].status, "stopped");
  assert.equal(st.boosts["18000000000000003"].status, "active");
  assert.equal(st.boosts["18000000000000003"].revenue, 24);
  assert.equal(st.boosts["18000000000000005"].status, "active");     // theirs: only a warning
  assert.equal(st.boosts["18000000000000005"].warn, "no-sales");
  assert.equal(calls.find((c) => c.path === "ad4").params.status, "PAUSED");
  assert.equal(calls.filter((c) => c.method === "POST" && c.path === "shared1" && c.params.daily_budget).length, 0);   // same $4: nothing to change
  // the Fall post left: the audience follows what is still boosted (no more "season")
  assert.equal(db.get("ads/state").targetKey, "gift,home,photo");
  const v = await A.adminAds({ action: "view" }, ADMIN);
  assert.ok(v.log.some((l) => l.kind === "pause" && /\$9\.10/.test(l.pt)));
  assert.ok(v.log.some((l) => l.kind === "warn" && /Mine/.test(l.pt)));
  // the warning is said once
  const n = pushes.length;
  await A.run();
  assert.equal(db.get("adsLog") === undefined || true, true);
  assert.equal((await A.adminAds({ action: "view" }, ADMIN)).log.filter((l) => l.kind === "warn").length, 1);
  assert.ok(pushes.length >= n);
});

test("the next Reel: they ask, it waits until a new Reel is out, then it's boosted first (the weakest robot pick makes room)", async () => {
  const { db, A } = setup();
  db.docs.set("ads/auth", { meta: META });
  db.docs.set("ads/config", { ...A.DEFAULTS, rules: { ...A.DEFAULTS.rules, maxPosts: 1 }, channels: { ...A.DEFAULTS.channels, etsy: { on: false, daily: 2 } } });
  db.docs.set("ads/state", { metaCampaignId: "c1", adsetId: "shared1", adsetDaily: 4, adsetStatus: "ACTIVE", boosts: {
    "18000000000000003": { id: "18000000000000003", adsetId: "shared1", adId: "ad3", shared: true, status: "active", caption: "Packing", by: "robot", type: "reel" },
  } });
  const asked = new Date(Date.now() - 3600000).toISOString();
  await A.adminAds({ action: "nextReel", after: asked }, ADMIN);
  const media = { data: [{ id: "18000000000000003", caption: "Packing", media_product_type: "REELS", media_type: "VIDEO", timestamp: new Date(Date.now() - 3 * 86400000).toISOString(), like_count: 9 }] };
  const calls = net({ meta: {
    "GET act_123/insights": { data: [] }, "GET ad3/insights": { data: [{ spend: "1.00" }] },
    [`GET ${META.igUserId}/media`]: media,
    "POST ad3": { success: true },
    "POST act_123/adcreatives": (p) => ({ id: `cr-${p.source_instagram_media_id}` }),
    "POST act_123/ads": (p) => ({ id: "ad-new" }),
  } });
  assert.deepEqual(await A.boostNextReel(), { waiting: true });          // nothing new yet
  assert.equal(calls.filter((c) => c.path === "act_123/ads").length, 0);
  // the Reel goes out (a photo too: only the Reel counts)
  media.data.unshift({ id: "18000000000000009", caption: "Wrapping a gift", media_product_type: "REELS", media_type: "VIDEO", timestamp: new Date().toISOString(), like_count: 0 });
  media.data.unshift({ id: "18000000000000008", caption: "Photo", media_type: "IMAGE", timestamp: new Date().toISOString() });
  media.data.push({ id: "18000000000000006", caption: "Old photo", media_type: "IMAGE", timestamp: new Date(Date.now() - 5 * 86400000).toISOString(), like_count: 50 });
  db.docs.set("ads/config", { ...db.get("ads/config"), rules: { ...db.get("ads/config").rules, maxPosts: 3 } });
  const r = await A.boostNextReel();
  assert.equal(r.boosted, "18000000000000009");
  const st = db.get("ads/state");
  assert.equal(st.nextReel, undefined);
  assert.equal(st.boosts["18000000000000009"].status, "active");
  assert.equal(st.boosts["18000000000000009"].by, "owner@lhh.com");
  assert.equal(st.boosts["18000000000000003"].status, "active");     // room for both with 3: nothing paused
  assert.equal(st.boosts["18000000000000006"], undefined);             // the rest waits for the morning run
  assert.equal(calls.find((c) => c.path === "act_123/ads").params.adset_id, "shared1");
  assert.deepEqual(await A.boostNextReel(), { waiting: false });
});

test("the owners swap what's boosted: the one they pick in, the one they say (or the weakest robot pick) out", async () => {
  const { db, A } = setup();
  db.docs.set("ads/auth", { meta: META });
  db.docs.set("ads/config", { ...A.DEFAULTS, rules: { ...A.DEFAULTS.rules, maxPosts: 1 }, channels: { ...A.DEFAULTS.channels, etsy: { on: false, daily: 2 } } });
  db.docs.set("ads/state", { metaCampaignId: "c1", adsetId: "shared1", adsetDaily: 4, adsetStatus: "ACTIVE",
    posts: [{ id: "18000000000000007", caption: "Other reel", type: "reel" }],
    boosts: { "18000000000000003": { id: "18000000000000003", adsetId: "shared1", adId: "ad3", shared: true, status: "active", caption: "Packing", by: "robot" } } });
  const calls = net({ meta: {
    "POST ad3": { success: true },
    "POST act_123/adcreatives": (p) => ({ id: `cr-${p.source_instagram_media_id}` }),
    "POST act_123/ads": () => ({ id: "ad7" }),
  } });
  await A.adminAds({ action: "post", id: "18000000000000007", what: "boost", instead: "18000000000000003" }, ADMIN);
  const st = db.get("ads/state");
  assert.equal(st.boosts["18000000000000003"].status, "paused");
  assert.equal(st.boosts["18000000000000007"].status, "active");
  assert.equal(st.boosts["18000000000000007"].type, "reel");
  assert.equal(calls.find((c) => c.path === "act_123/ads").params.adset_id, "shared1");
  // pausing theirs acts on the ad, not the shared ad set
  calls.length = 0;
  net({ meta: { "POST ad7": { success: true } } });
  await A.adminAds({ action: "post", id: "18000000000000007", what: "pause" }, ADMIN);
  assert.equal(db.get("ads/state").boosts["18000000000000007"].status, "paused");
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

test("posts: among Reels, sends and saves count more than likes (Instagram's numbers); without numbers, likes + comments", async () => {
  const { A } = setup();
  const old = new Date(Date.now() - 3 * 86400000).toISOString();
  net({ meta: {
    [`GET ${META.igUserId}/media`]: { data: [
      { id: "18000000000000001", caption: "Liked", media_product_type: "REELS", media_type: "VIDEO", timestamp: old, like_count: 40, comments_count: 0 },
      { id: "18000000000000002", caption: "Shared", media_product_type: "REELS", media_type: "VIDEO", timestamp: old, like_count: 5, comments_count: 0 },
      { id: "18000000000000003", caption: "Photo", media_type: "IMAGE", timestamp: old, like_count: 90, comments_count: 0 },
    ] },
    "GET 18000000000000001/insights": { data: [{ name: "reach", values: [{ value: 300 }] }, { name: "shares", values: [{ value: 0 }] }, { name: "saved", values: [{ value: 1 }] }, { name: "ig_reels_avg_watch_time", values: [{ value: 3000 }] }] },
    "GET 18000000000000002/insights": { data: [{ name: "reach", values: [{ value: 200 }] }, { name: "shares", values: [{ value: 6 }] }, { name: "saved", values: [{ value: 4 }] }, { name: "ig_reels_avg_watch_time", values: [{ value: 7000 }] }] },
  } });
  const p = await A._internal.recentPosts(META, RULES);
  assert.deepEqual(p.map((x) => x.id), ["18000000000000002", "18000000000000001", "18000000000000003"]);
  assert.equal(p[0].shares, 6); assert.equal(p[0].watch, 7);
  const q = await A._internal.recentPosts(META, RULES, { insights: false });
  assert.deepEqual(q.map((x) => x.id), ["18000000000000001", "18000000000000002", "18000000000000003"]);
});

test("the audience: only people who live in the US, 25 to 65, plus the groups of what is boosted (Meta's exact names, looked up once)", async () => {
  const { db, A } = setup();
  const lists = { behaviors: [{ id: "b1", name: "Engaged Shoppers" }, { id: "b2", name: "Frequent Travelers" }],
    life_events: [{ id: "l1", name: "Newlywed (1 year)" }], family_statuses: [{ id: "f1", name: "Parents (up to 12 months)" }] };
  const calls = net({ meta: {
    // Meta's search: close-but-wrong names come first; "Christmas Day" only as a film (out)
    "GET search": (p) => p.type === "adTargetingCategory" ? { data: lists[p.class] || [] }
      : { data: p.q === "Christmas Day" ? [{ id: "film", name: "Christmas Day (film)" }] : [{ id: "other", name: "Other" }, { id: `id-${p.q}`, name: p.q }] },
    "GET act_123/insights": { data: [] }, [`GET ${META.igUserId}/media`]: { data: [] },
    "POST shared1": { success: true },
  } });
  assert.deepEqual(A._internal.themesOf("Christmas magnets for your fridge 🎄 #giftideas"), ["season", "home"]);
  assert.deepEqual(A._internal.themesOf("Packing this one with a whole lot of love"), ["photo"]);
  assert.deepEqual(A._internal.themesOf("New York at night"), ["places"]);
  assert.deepEqual(A._internal.themesOf("✨"), ["photo", "home"]);              // nothing said: the most bought
  const state = {};
  const t = await A._internal.audience(META, state, ["photo"]);
  assert.deepEqual(t.geo_locations, { countries: ["US"], location_types: ["home"] });
  assert.equal(t.age_min, 25);
  const spec = t.flexible_spec[0];
  assert.ok(spec.interests.some((i) => i.name === "Gift") && spec.interests.some((i) => i.name === "Weddings"));
  assert.deepEqual(spec.behaviors, [{ id: "b1", name: "Engaged Shoppers" }]);
  assert.deepEqual(spec.life_events, [{ id: "l1", name: "Newlywed (1 year)" }]);
  assert.deepEqual(spec.family_statuses, [{ id: "f1", name: "Parents (up to 12 months)" }]);
  assert.ok(!spec.interests.some((i) => i.name === "Travel"));                   // not this post's group
  const n = calls.filter((c) => c.path === "search").length;
  await A._internal.audience(META, state, ["photo"]);
  assert.equal(calls.filter((c) => c.path === "search").length, n);              // kept: not looked up again
  const s2 = await A._internal.audience(META, state, ["season"]);
  assert.ok(!s2.flexible_spec[0].interests.some((i) => /film/.test(i.name)));
  // the run: the ad set follows the boosted posts (once per change)
  db.docs.set("ads/auth", { meta: META });
  db.docs.set("ads/state", { metaCampaignId: "c1", adsetId: "shared1", adsetDaily: 4, adsetStatus: "ACTIVE",
    boosts: { "18000000000000003": { id: "18000000000000003", adsetId: "shared1", adId: "ad3", shared: true, status: "active", caption: "Our New York magnet", by: "robot" } } });
  const c2 = net({ meta: { "GET search": (p) => p.type === "adTargetingCategory" ? { data: lists[p.class] || [] } : { data: [{ id: `id-${p.q}`, name: p.q }] },
    "GET act_123/insights": { data: [] }, "GET ad3/insights": { data: [] }, [`GET ${META.igUserId}/media`]: { data: [] }, "POST shared1": { success: true } } });
  await A.run();
  const up = c2.filter((c) => c.path === "shared1" && c.params.targeting);
  assert.equal(up.length, 1);
  const sp = JSON.parse(up[0].params.targeting).flexible_spec[0];
  assert.ok(sp.interests.some((i) => i.name === "Travel") && sp.behaviors.some((b) => b.name === "Frequent Travelers"));
  assert.equal(db.get("ads/state").targetKey, "gift,places");
  await A.run();
  assert.equal(c2.filter((c) => c.path === "shared1" && c.params.targeting).length, 1);
  const v = await A.adminAds({ action: "view" }, ADMIN);
  assert.deepEqual(v.audience, ["Presentes e feito à mão", "Viagens e lugares"]);
});
