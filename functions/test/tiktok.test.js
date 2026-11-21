"use strict";
/* TikTok Shop (tiktok.js): the request signature (TikTok's published algorithm), saving the app secret, connecting
   (authorization link with state, code -> tokens -> the shop's cipher), signed calls with the token in the header,
   refreshing an old token, admins only. TikTok is faked. */
const test = require("node:test");
const assert = require("node:assert/strict");
const crypto = require("crypto");
const { FakeDB, FakeAuth, FakeBucket } = require("./fakes");
const deps = require("../deps");

const ADMIN = { uid: "admin1", token: { admin: true, email: "owner@lhh.com" } };
const SECRET = "0123456789abcdef0123456789abcdef01234567";
const T0 = Date.parse("2026-11-21T20:00:00Z");

function setup(now = T0) {
  Object.assign(process.env, { ADMIN_EMAILS: "owner@lhh.com", SITE_URL: "https://littlehivehouse.com" });
  delete process.env.TIKTOK_APP_SECRET;
  const db = new FakeDB();
  deps.set({ db, auth: new FakeAuth(), bucket: new FakeBucket() });
  const calls = [];
  const clock = { t: now };
  const T = require("../tiktok");
  T.setTransport(async (url, opts = {}) => {
    const u = new URL(String(url));
    calls.push({ m: opts.method || "GET", u, body: opts.body, headers: opts.headers || {} });
    const ok = (j) => ({ ok: true, status: 200, json: async () => j });
    if (u.pathname === "/api/v2/token/get" || u.pathname === "/api/v2/token/refresh") {
      const n = u.pathname.endsWith("get") ? 1 : 2;
      return ok({ code: 0, message: "success", data: { access_token: `TTP_acc${n}`, access_token_expire_in: Math.floor(clock.t / 1000) + 7 * 86400,
        refresh_token: `TTP_ref${n}`, refresh_token_expire_in: Math.floor(clock.t / 1000) + 365 * 86400, open_id: "o1", seller_name: "Little Hive House", seller_base_region: "US", user_type: 0,
        granted_scopes: ["seller.product.basic", "seller.order.info"] } });
    }
    if (u.pathname === "/authorization/202309/shops") return ok({ code: 0, data: { shops: [{ id: "7495", name: "Little Hive House", region: "US", seller_type: "LOCAL", cipher: "GCP_abc", code: "USLC1" }] } });
    if (u.pathname === "/product/202309/categories") return ok({ code: 0, data: { categories: [{ id: "1", local_name: "Home" }] } });
    if (u.pathname === "/fail") return ok({ code: 12052048, message: "Invalid category" });
    return { ok: false, status: 404, json: async () => ({ code: 404, message: "not found" }) };
  }, () => clock.t);
  return { db, calls, T, clock };
}

test("sign: TikTok's algorithm (path + sorted params, no sign/access_token, + body, wrapped in the secret)", () => {
  const { T } = setup();
  const q = { timestamp: "1623812664", app_key: "29a39d", shop_cipher: "GCP_x", sign: "old", access_token: "tok" };
  const body = '{"a":1}';
  const want = crypto.createHmac("sha256", "sec").update("sec" + "/product/202309/products" + "app_key29a39dshop_cipherGCP_xtimestamp1623812664" + body + "sec").digest("hex");
  assert.equal(T._internal.sign("sec", "/product/202309/products", q, body), want);
  // no body (GET / multipart): nothing appended
  const want2 = crypto.createHmac("sha256", "sec").update("sec/xapp_key29a39dsec").digest("hex");
  assert.equal(T._internal.sign("sec", "/x", { app_key: "29a39d" }, ""), want2);
});

test("only admins", async () => {
  const { T } = setup();
  await assert.rejects(T.adminTikTok({ action: "status" }, { uid: "u", token: {} }), /admin/i);
});

test("status before anything: no secret, not connected, the app key known", async () => {
  const { T } = setup();
  const s = await T.adminTikTok({ action: "status" }, ADMIN);
  assert.equal(s.secret, false);
  assert.equal(s.connected, false);
  assert.equal(s.appKey, "6lqcfgtud0gvr");
});

test("saveSecret: checks the shape, keeps it on the server, never sends it back", async () => {
  const { T, db } = setup();
  await assert.rejects(T.adminTikTok({ action: "saveSecret", secret: "abc" }, ADMIN), /doesn't look like/);
  const s = await T.adminTikTok({ action: "saveSecret", secret: ` ${SECRET}\n` }, ADMIN);
  assert.equal(s.secret, true);
  assert.equal(s.secretEnd, "4567");
  assert.equal(JSON.stringify(s).includes(SECRET), false);
  assert.equal(db.docs.get("tiktok/auth").appSecret, SECRET);
});

test("connect: start needs the secret; the link carries the service id and a state; finish gets tokens and the shop", async () => {
  const { T, db, calls } = setup();
  await assert.rejects(T.adminTikTok({ action: "start" }, ADMIN), /secret isn't saved/);
  await T.adminTikTok({ action: "saveSecret", secret: SECRET }, ADMIN);
  const { url } = await T.adminTikTok({ action: "start" }, ADMIN);
  const u = new URL(url);
  assert.equal(u.origin + u.pathname, "https://services.us.tiktokshop.com/open/authorize");
  assert.equal(u.searchParams.get("service_id"), "7705213161087436558");
  const state = u.searchParams.get("state");
  assert.ok(state && state.length >= 16);
  await assert.rejects(T.adminTikTok({ action: "finish", code: "TTP_code", state: "wrong" }, ADMIN), /doesn't match/);
  const s = await T.adminTikTok({ action: "finish", code: "TTP_code", state }, ADMIN);
  assert.equal(s.connected, true);
  assert.equal(s.shop.name, "Little Hive House");
  const tok = calls.find((c) => c.u.pathname === "/api/v2/token/get");
  assert.equal(tok.u.searchParams.get("grant_type"), "authorized_code");
  assert.equal(tok.u.searchParams.get("auth_code"), "TTP_code");
  assert.equal(tok.u.searchParams.get("app_secret"), SECRET);
  const shops = calls.find((c) => c.u.pathname === "/authorization/202309/shops");
  assert.equal(shops.headers["x-tts-access-token"], "TTP_acc1");
  assert.equal(shops.u.searchParams.get("shop_cipher"), null);
  assert.equal(shops.u.searchParams.has("access_token"), false);
  const a = db.docs.get("tiktok/auth");
  assert.equal(a.shopCipher, "GCP_abc");
  assert.equal(a.refresh, "TTP_ref1");
  assert.equal(db.docs.has("tiktok/oauth"), false);
});

async function connected() {
  const env = setup();
  await env.T.adminTikTok({ action: "saveSecret", secret: SECRET }, ADMIN);
  const { url } = await env.T.adminTikTok({ action: "start" }, ADMIN);
  await env.T.adminTikTok({ action: "finish", code: "c", state: new URL(url).searchParams.get("state") }, ADMIN);
  env.calls.length = 0;
  return env;
}

test("call: signed with the secret, shop_cipher and timestamp in the query, the signature checks out", async () => {
  const { T, calls, clock } = await connected();
  const d = await T._internal.call("GET", "/product/202309/categories", { query: { locale: "en-US" } });
  assert.equal(d.categories[0].id, "1");
  const c = calls[0];
  const q = Object.fromEntries(c.u.searchParams.entries());
  assert.equal(q.shop_cipher, "GCP_abc");
  assert.equal(q.timestamp, String(Math.floor(clock.t / 1000)));
  assert.equal(q.app_key, "6lqcfgtud0gvr");
  assert.equal(q.sign, T._internal.sign(SECRET, "/product/202309/categories", q, ""));
});

test("call: a JSON body is signed too; TikTok's refusals come back readable", async () => {
  const { T, calls } = await connected();
  await assert.rejects(T._internal.call("POST", "/fail", { json: { x: 1 } }), /TikTok: Invalid category \[12052048\]/);
  const c = calls[0];
  const q = Object.fromEntries(c.u.searchParams.entries());
  assert.equal(c.body, '{"x":1}');
  assert.equal(q.sign, T._internal.sign(SECRET, "/fail", q, '{"x":1}'));
});

test("an access token close to expiring is refreshed first", async () => {
  const { T, calls, clock, db } = await connected();
  clock.t += 7 * 86400000 - 1000;
  await T._internal.call("GET", "/product/202309/categories");
  assert.equal(calls[0].u.pathname, "/api/v2/token/refresh");
  assert.equal(calls[0].u.searchParams.get("refresh_token"), "TTP_ref1");
  assert.equal(calls[1].headers["x-tts-access-token"], "TTP_acc2");
  assert.equal(db.docs.get("tiktok/auth").refresh, "TTP_ref2");
});

test("disconnect forgets the tokens but keeps the app secret", async () => {
  const { T, db } = await connected();
  const s = await T.adminTikTok({ action: "disconnect" }, ADMIN);
  assert.equal(s.connected, false);
  assert.equal(s.secret, true);
  assert.equal(db.docs.get("tiktok/auth").appSecret, SECRET);
});
