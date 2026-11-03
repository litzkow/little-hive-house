"use strict";
/* The "Visitas" report (analytics.js): GA4 answers shaped for the admin page, the cache, live visitors and errors. */
const test = require("node:test");
const assert = require("node:assert/strict");
const { FakeDB, FakeAuth, FakeBucket } = require("./fakes");
const deps = require("../deps");

const ADMIN = { uid: "admin1", token: { admin: true, email: "owner@lhh.com" } };
const rep = (dims, mets, data) => ({ dimensionHeaders: dims.map((name) => ({ name })), metricHeaders: mets.map((name) => ({ name })),
  rows: data.map((r) => ({ dimensionValues: r.slice(0, dims.length).map((value) => ({ value: String(value) })), metricValues: r.slice(dims.length).map((value) => ({ value: String(value) })) })) });

function answers(body) {
  const names = body.requests.map((r) => (r.dimensions || []).map((d) => d.name).join(","));
  return { reports: names.map((n, i) => {
    const r = body.requests[i];
    if (!n) return rep(["dateRange"], r.metrics.map((m) => m.name), [["cur", 12, 9, 15, 60, 95.5, 0.62, 1400, 30, 1, 4], ["prev", 6, 6, 7, 20, 60, 0.5, 400, 0, 0, 1]]);
    if (n === "date") return rep(["date"], ["activeUsers", "sessions", "screenPageViews"], [["20261102", 4, 5, 20], ["20261103", 8, 10, 40]]);
    if (n === "country") return rep(["country"], ["activeUsers", "sessions"], [["United States", 10, 12], ["Brazil", 2, 3], ["(not set)", 1, 1]]);
    if (n === "region") return rep(["region"], ["activeUsers"], [["Georgia", 6], ["Florida", 4]]);
    if (n === "city,region,countryId") return rep(["city", "region", "countryId"], ["activeUsers"], [["Atlanta", "Georgia", "US", 5], ["(not set)", "", "US", 3]]);
    if (n === "userAgeBracket") return rep([n], ["activeUsers"], [["35-44", 3], ["25-34", 5]]);
    if (n === "pagePath") return rep(["pagePath"], ["screenPageViews", "activeUsers", "userEngagementDuration"],
      [["/", 30, 10, 300], ["/index.html", 5, 2, 20], ["/collections/fall.html", 12, 6, 240], ["/collections/fall", 3, 2, 60], ["/collections/brasil.html?x=1", 4, 2, 10]]);
    if (n === "eventName") return rep(["eventName"], ["eventCount", "totalUsers"], [["page_view", 60, 12], ["view_item", 9, 5], ["add_to_cart", 4, 3], ["begin_checkout", 2, 2], ["purchase", 1, 1]]);
    if (n === "itemName,itemCategory") return rep(["itemName", "itemCategory"], ["itemsViewed", "itemsAddedToCart", "itemsPurchased"], [["Pumpkin", "fall", 6, 2, 1], ["(not set)", "", 3, 0, 0]]);
    if (n === "dayOfWeek,hour") return rep(["dayOfWeek", "hour"], ["sessions"], [["2", "02", 7], ["1", "20", 3]]);
    if (n === "landingPage") return rep([n], ["sessions"], [["/collections/fall.html", 4], ["/", 6]]);
    return rep([n], ["activeUsers"], []);
  }) };
}

function setup({ deny = false } = {}) {
  const db = new FakeDB();
  deps.set({ db, auth: new FakeAuth(), bucket: new FakeBucket() });
  const calls = [];
  globalThis.fetch = async (url, init = {}) => {
    const u = new URL(url);
    if (u.host === "metadata.google.internal") {
      calls.push({ meta: true, scopes: u.searchParams.get("scopes"), flavor: init.headers["Metadata-Flavor"] });
      return { ok: true, status: 200, json: async () => ({ access_token: "ya29.fake", expires_in: 3600 }) };
    }
    assert.equal(u.host, "analyticsdata.googleapis.com");
    const body = JSON.parse(init.body);
    calls.push({ path: u.pathname, body, auth: init.headers.Authorization });
    if (deny) return { ok: false, status: 403, json: async () => ({ error: { code: 403, status: "PERMISSION_DENIED", message: "User does not have sufficient permissions for this property." } }) };
    if (/runRealtimeReport$/.test(u.pathname)) {
      const d = (body.dimensions || []).map((x) => x.name).join(",");
      if (!d) return { ok: true, status: 200, json: async () => rep([], ["activeUsers"], [[3]]) };
      if (d === "city,country") return { ok: true, status: 200, json: async () => rep(["city", "country"], ["activeUsers"], [["Orlando", "United States", 2], ["(not set)", "Brazil", 1]]) };
      if (d === "minutesAgo") return { ok: true, status: 200, json: async () => rep(["minutesAgo"], ["activeUsers"], [["00", 2], ["05", 1]]) };
      return { ok: true, status: 200, json: async () => rep([d], ["activeUsers"], [["Fall magnets", 2]]) };
    }
    return { ok: true, status: 200, json: async () => answers(body) };
  };
  const analytics = require("../analytics");
  analytics._reset();
  return { db, calls, analytics };
}

test("the report: totals against the period before, places, collections, the funnel", async () => {
  const { calls, analytics } = setup();
  const r = await analytics.adminAnalytics({ range: "7d" }, ADMIN);
  assert.equal(r.range, "7d");
  assert.equal(r.days, 7);
  assert.equal(r.totals.activeUsers, 12);
  assert.equal(r.previous.activeUsers, 6);
  assert.equal(r.totals.purchaseRevenue, 30);
  assert.deepEqual(r.series[1], { date: "2026-11-03", users: 8, visits: 10, views: 40 });
  assert.deepEqual(r.countries.map((c) => c.name), ["United States", "Brazil"]);   // no "(not set)"
  assert.equal(r.states[0].name, "Georgia");
  assert.deepEqual(r.cities, [{ name: "Atlanta", region: "Georgia", country: "US", value: 5 }]);
  assert.deepEqual(r.age.map((a) => a.name), ["25-34", "35-44"]);
  // /collections/fall.html and /collections/fall are the same page; ?x=1 is dropped
  assert.deepEqual(r.collections.map((c) => [c.slug, c.views]), [["fall", 15], ["brasil", 4]]);
  assert.equal(r.collections[0].avgSeconds, 38);    // 300 s over 8 visitors
  assert.equal(r.pages[0].path, "/");
  assert.equal(r.pages[0].views, 35);
  assert.equal(r.pages[0].name, "Home");
  assert.deepEqual(r.funnel.map((f) => f.users), [12, 5, 3, 2, 1]);
  assert.deepEqual(r.items, [{ name: "Pumpkin", category: "fall", viewed: 6, added: 2, bought: 1 }]);
  assert.equal(r.heat[2][2], 7);
  assert.equal(r.landing[0].name, "Home");
  // the token asks only for reading Analytics; 4 batches go to the property
  const meta = calls.find((c) => c.meta);
  assert.equal(meta.scopes, "https://www.googleapis.com/auth/analytics.readonly");
  assert.equal(meta.flavor, "Google");
  const ga = calls.filter((c) => !c.meta);
  assert.equal(ga.length, 4);
  assert.ok(ga.every((c) => c.path === "/v1beta/properties/562104666:batchRunReports" && c.auth === "Bearer ya29.fake"));
  assert.ok(ga.every((c) => c.body.requests.length <= 5), "GA takes at most 5 reports per batch");
  assert.deepEqual(ga[0].body.requests[0].dateRanges.map((d) => [d.startDate, d.endDate]), [["6daysAgo", "today"], ["13daysAgo", "7daysAgo"]]);
});

test("the cache: a second look within 15 minutes doesn't ask Google again, refresh does", async () => {
  const { db, calls, analytics } = setup();
  await analytics.adminAnalytics({}, ADMIN);
  const n = calls.length;
  const again = await analytics.adminAnalytics({}, ADMIN);
  assert.equal(again.cached, true);
  assert.equal(again.range, "28d");
  assert.equal(calls.length, n);
  assert.ok(db.get("analyticsCache/28d").report);
  const fresh = await analytics.adminAnalytics({ refresh: true }, ADMIN);
  assert.equal(fresh.cached, false);
  assert.ok(calls.length > n);
});

test("live: visitors now, where they are, per minute", async () => {
  const { analytics } = setup();
  const l = await analytics.adminAnalyticsLive({}, ADMIN);
  assert.equal(l.now, 3);
  assert.deepEqual(l.places, [{ city: "Orlando", country: "United States", value: 2 }, { city: "", country: "Brazil", value: 1 }]);
  assert.equal(l.perMinute.length, 30);
  assert.equal(l.perMinute[29], 2);   // this minute is last
  assert.equal(l.perMinute[24], 1);
  assert.equal(l.pages[0].name, "Fall magnets");
});

test("without access in Google Analytics: a clear message, and the status says so", async () => {
  const { db, analytics } = setup({ deny: true });
  await assert.rejects(analytics.adminAnalytics({ refresh: true }, ADMIN), (e) => e.code === "failed-precondition" && /Viewer/.test(e.message));
  const w = await analytics.warm();
  assert.equal(w.ok, false);
  assert.equal(db.get("analyticsCache/status").ok, false);
  assert.match(db.get("analyticsCache/status").error, /access/);
});

test("warm writes the 28-day report and an ok status; only admins can read", async () => {
  const { db, analytics } = setup();
  const w = await analytics.warm();
  assert.equal(w.ok, true);
  assert.equal(db.get("analyticsCache/status").ok, true);
  assert.equal(db.get("analyticsCache/status").users, 12);
  assert.ok(db.get("analyticsCache/28d").report.series.length);
  await assert.rejects(analytics.adminAnalytics({}, { uid: "x", token: {} }));
  await assert.rejects(analytics.adminAnalyticsLive({}, null));
});
