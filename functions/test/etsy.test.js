"use strict";
/* The Etsy store (etsy.js): connecting with OAuth + PKCE, publishing a listing (shipping profile, processing time,
   category and sections made once; photos, variations, then active), never twice; admins only. Etsy is faked. */
const test = require("node:test");
const assert = require("node:assert/strict");
const crypto = require("crypto");
const { FakeDB, FakeAuth, FakeBucket } = require("./fakes");
const deps = require("../deps");

const ADMIN = { uid: "admin1", token: { admin: true, email: "owner@lhh.com" } };

function setup() {
  Object.assign(process.env, { ADMIN_EMAILS: "owner@lhh.com", SITE_URL: "https://littlehivehouse.com", ETSY_KEYSTRING: "key123", ETSY_SHARED_SECRET: "sec456" });
  const db = new FakeDB();
  deps.set({ db, auth: new FakeAuth(), bucket: new FakeBucket() });
  db.docs.set("settings/store", { shipFrom: { zip: "30185" } });
  const calls = [];
  let n = 1000;
  const IMGS = { 5151: [{ id: 71, rank: 1 }, { id: 72, rank: 2 }] }, ACTIVE = new Set();
  globalThis.__lenient = false;
  globalThis.fetch = async (url, opts = {}) => {
    const u = String(url), m = opts.method || "GET";
    const body = typeof opts.body === "string" ? opts.body : opts.body instanceof FormData ? "multipart" : "";
    calls.push({ m, u, body, headers: opts.headers || {}, form: opts.body instanceof FormData ? opts.body : null });
    const ok = (j) => ({ ok: true, status: 200, json: async () => j });
    if (u.endsWith("/oauth/token")) return ok({ access_token: "777.abc", refresh_token: "r1", expires_in: 3600, token_type: "Bearer" });
    if (u.endsWith("/users/me")) return ok({ user_id: 777, shop_id: 55 });
    if (/\/shops\/55$/.test(u)) return ok({ shop_id: 55, shop_name: "LittleHiveHouse", url: "https://www.etsy.com/shop/LittleHiveHouse" });
    if (u.endsWith("/shipping-profiles") && m === "GET") return ok({ results: [] });
    if (u.endsWith("/shipping-profiles")) return ok({ shipping_profile_id: 9001 });
    if (u.endsWith("/readiness-state-definitions")) return ok({ readiness_state_id: 9002 });
    if (u.endsWith("/policies/return") && m === "GET") return ok({ results: [{ return_policy_id: 1, accepts_returns: false, accepts_exchanges: false, return_deadline: null }] });
    if (u.endsWith("/policies/return")) return ok({ return_policy_id: 9003 });
    // photos, the way the real Etsy keeps them: a rank per photo, an upload at a taken rank doesn't push the others
    // (two at the same rank), and after that every upload is refused; an active listing keeps its last photo
    const im = /\/listings\/(\d+)\/images(?:\/(\d+))?$/.exec(u);
    if (im) {
      const list = IMGS[im[1]] = IMGS[im[1]] || [];
      if (m === "GET") return ok({ count: list.length, results: list.slice().sort((a, b) => a.rank - b.rank).map((x) => ({ listing_image_id: x.id, rank: x.rank })) });
      if (m === "DELETE") {
        if (list.length === 1 && ACTIVE.has(im[1])) return { ok: false, status: 400, json: async () => ({ error: "An active listing must have at least one image." }) };
        IMGS[im[1]] = list.filter((x) => String(x.id) !== im[2]); return ok({});
      }
      const f = opts.body;
      if (f.get("listing_image_id")) { const x = list.find((y) => String(y.id) === f.get("listing_image_id")); x.rank = Number(f.get("rank")); return ok({ listing_image_id: x.id, rank: x.rank }); }
      const ranks = list.map((x) => x.rank).sort((a, b) => a - b);
      if (ranks.some((r, i) => r !== i + 1) && !globalThis.__lenient) return { ok: false, status: 400, json: async () => ({ error: "The ListingImages for this Listing are in an inconsistent order." }) };
      if (globalThis.__dropImage > 0) { globalThis.__dropImage -= 1; return { ok: false, status: 500, json: async () => ({ error: "photos-writer failure upload" }) }; }
      const x = { id: ++n, rank: Number(f.get("rank")) || 1 }; list.push(x); return ok({ listing_image_id: x.id, rank: x.rank });
    }
    if (u.endsWith("/seller-taxonomy/nodes")) return ok({ results: [{ id: 1, name: "Home & Living", children: [{ id: 2, name: "Home Decor", children: [{ id: 1068, name: "Magnets", children: [] }] }] }] });
    if (u.endsWith("/sections") && m === "GET") return ok({ results: [] });
    if (u.endsWith("/sections")) return ok({ shop_section_id: ++n });
    if (/\/shops\/55\/listings$/.test(u)) { IMGS[4242] = []; return ok({ listing_id: 4242, state: "draft" }); }   // every new draft is 4242 here: it starts with no photos
    if (u.endsWith("/inventory")) return ok({ products: [] });
    if (/\/listings\/(4242|5151)$/.test(u) && m === "PATCH") return ok({ listing_id: 4242, state: "active", url: "https://www.etsy.com/listing/4242/x" });
    return { ok: false, status: 404, json: async () => ({ error: "not faked: " + u }) };
  };
  const E = require("../etsy");
  E.setImageFetcher(async () => new Blob([Buffer.from("jpg")], { type: "image/jpeg" }), 0);
  globalThis.__dropImage = 0;
  return { db, calls, E, IMGS, ACTIVE };
}

test("connect: the Etsy link carries PKCE and the scopes; the approval is checked, saved, and the shop is found", async () => {
  const { db, calls, E } = setup();
  let st = await E.adminEtsy({ action: "status" }, ADMIN);
  assert.equal(st.keystring, true);
  assert.equal(st.connected, false);
  const { url } = await E.adminEtsy({ action: "start" }, ADMIN);
  const q = new URL(url).searchParams;
  assert.equal(q.get("client_id"), "key123");
  assert.equal(q.get("redirect_uri"), "https://littlehivehouse.com/admin/etsy-callback.html");
  assert.match(q.get("scope"), /listings_w/);
  assert.equal(q.get("code_challenge_method"), "S256");
  const o = db.get("etsy/oauth");
  const challenge = crypto.createHash("sha256").update(o.verifier).digest("base64").replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
  assert.equal(q.get("code_challenge"), challenge);
  await assert.rejects(E.adminEtsy({ action: "finish", code: "c", state: "wrong" }, ADMIN), /doesn't match/);
  st = await E.adminEtsy({ action: "finish", code: "c1", state: q.get("state") }, ADMIN);
  assert.equal(st.connected, true);
  assert.equal(st.shop.name, "LittleHiveHouse");
  const tok = calls.find((c) => c.u.endsWith("/oauth/token"));
  assert.match(tok.body, /code_verifier=/);
  assert.match(tok.body, /grant_type=authorization_code/);
  const me = calls.find((c) => c.u.endsWith("/users/me"));
  assert.equal(me.headers["x-api-key"], "key123:sec456");
  assert.equal(me.headers.Authorization, "Bearer 777.abc");
  assert.equal(db.get("etsy/oauth"), undefined, "the one-time PKCE secret is gone");
  await assert.rejects(E.adminEtsy({ action: "status" }, { uid: "x", token: {} }));
});

test("publish: setup once, photos in order, variations, then active; the second time it's skipped", async () => {
  const { db, calls, E } = setup();
  db.docs.set("etsy/auth", { access: "777.abc", refresh: "r1", expiresAt: Date.now() + 3600e3, shopId: 55 });
  const r = await E.adminEtsy({ action: "publish", id: "brasil" }, ADMIN);
  assert.equal(r.listing.state, "active");
  assert.equal(r.listing.listingId, 4242);
  const draft = calls.find((c) => /\/shops\/55\/listings$/.test(c.u));
  const f = new URLSearchParams(draft.body);
  assert.equal(f.get("who_made"), "i_did");
  assert.equal(f.get("when_made"), "made_to_order");
  assert.equal(f.get("taxonomy_id"), "1068");
  assert.equal(f.get("shipping_profile_id"), "9001");
  assert.equal(f.get("readiness_state_id"), "9002");
  assert.equal(f.get("return_policy_id"), "9003");
  const rp = new URLSearchParams(calls.find((c) => c.u.endsWith("/policies/return") && c.m === "POST").body);
  assert.equal(rp.get("return_deadline"), "30");
  assert.equal(rp.get("accepts_exchanges"), "false");
  assert.equal(f.get("price"), "5.75");
  assert.equal(f.get("tags").split(",").length, 13);
  assert.equal(calls.filter((c) => c.u.endsWith("/images")).length, 6);
  const inv = JSON.parse(calls.find((c) => c.u.endsWith("/inventory")).body);
  assert.ok(inv.products.length > 10);
  assert.equal(inv.products[0].property_values[0].property_name, "Design");
  assert.equal(inv.products[0].offerings[0].readiness_state_id, 9002);
  const ship = new URLSearchParams(calls.find((c) => c.u.endsWith("/shipping-profiles") && c.m === "POST").body);
  assert.equal(ship.get("primary_cost"), "5.49");
  assert.equal(ship.get("origin_postal_code"), "30185");
  // a photo listing: prices by pack size, personalization on
  const before = calls.length;
  db.docs.set("etsy/listings", { ...db.get("etsy/listings") });
  globalThis.__noop = 1;
  const p = await E.adminEtsy({ action: "publish", id: "photo-magnets" }, ADMIN);
  assert.equal(p.listing.state, "active");
  const d2 = new URLSearchParams(calls.slice(before).find((c) => /\/shops\/55\/listings$/.test(c.u)).body);
  assert.equal(d2.get("price"), "15.5");
  assert.equal(d2.get("is_personalizable"), "true");
  const inv2 = JSON.parse(calls.slice(before).find((c) => c.u.endsWith("/inventory")).body);
  assert.deepEqual(inv2.price_on_property, [513]);
  assert.deepEqual(inv2.products.map((x) => x.offerings[0].price), [15.5, 27, 43.5, 70, 129]);
  assert.equal(calls.slice(before).filter((c) => c.u.endsWith("/shipping-profiles")).length, 0, "the setup is made once");
  const again = await E.adminEtsy({ action: "publish", id: "brasil" }, ADMIN);
  assert.equal(again.skipped, true);
  const st = await E.adminEtsy({ action: "status" }, ADMIN);
  assert.equal(st.listings.filter((l) => l.state === "active").length, 2);
  assert.equal(st.category, "Home & Living > Home Decor > Magnets");
});

test("an expired access token is refreshed before calling Etsy", async () => {
  const { db, calls, E } = setup();
  db.docs.set("etsy/auth", { access: "777.old", refresh: "r1", expiresAt: Date.now() - 1000, shopId: 55 });
  await E.adminEtsy({ action: "publish", id: "christmas" }, ADMIN);
  const refresh = calls.find((c) => c.u.endsWith("/oauth/token"));
  assert.match(refresh.body, /grant_type=refresh_token/);
  assert.match(refresh.body, /refresh_token=r1/);
  assert.equal(db.get("etsy/auth").access, "777.abc");
});

test("a draft left by an earlier try is finished (no second listing), and a dropped photo upload is tried again", async () => {
  const { db, calls, E } = setup();
  db.docs.set("etsy/auth", { access: "777.abc", refresh: "r1", expiresAt: Date.now() + 3600e3, shopId: 55 });
  db.docs.set("etsy/listings", { christmas: { listingId: 5151, state: "draft", error: "return policy cannot be null" } });
  globalThis.__dropImage = 1;
  const r = await E.adminEtsy({ action: "publish", id: "christmas" }, ADMIN);
  assert.equal(r.listing.state, "active");
  assert.equal(r.listing.listingId, 5151);
  assert.equal(calls.filter((c) => /\/shops\/55\/listings$/.test(c.u)).length, 0, "no new draft");
  const patch = new URLSearchParams(calls.find((c) => /\/listings\/5151$/.test(c.u) && c.m === "PATCH").body);
  assert.equal(patch.get("return_policy_id"), "9003");
  const posts = calls.filter((c) => c.u.endsWith("/5151/images") && c.m === "POST");
  assert.equal(posts.length, 6 - 2 + 1, "the 2 photos already there are kept; the 4 missing are sent, one of them twice");
});

const order = (IMGS, id) => IMGS[id].slice().sort((a, b) => a.rank - b.rank);

test("new photos for a listing already on Etsy: the new set ends up alone, at ranks 1..6, nothing duplicated, once", async () => {
  const { db, calls, E, IMGS, ACTIVE } = setup();
  db.docs.set("etsy/auth", { access: "777.abc", refresh: "r1", expiresAt: Date.now() + 3600e3, shopId: 55 });
  db.docs.set("etsy/listings", { brasil: { listingId: 4242, state: "active", url: "u" } });
  IMGS[4242] = [1, 2, 3, 4, 5, 6].map((r) => ({ id: 70 + r, rank: r }));
  ACTIVE.add("4242");
  let st = await E.adminEtsy({ action: "status" }, ADMIN);
  assert.equal(st.listings.find((l) => l.id === "brasil").newPhotos, true);
  const r = await E.adminEtsy({ action: "publish", id: "brasil" }, ADMIN);
  assert.equal(r.listing.state, "active");
  const now = order(IMGS, 4242);
  assert.deepEqual(now.map((x) => x.rank), [1, 2, 3, 4, 5, 6]);
  assert.ok(now.every((x) => x.id > 1000), "only the new photos are left");
  assert.equal(calls.filter((c) => /\/shops\/55\/listings$/.test(c.u)).length, 0);
  st = await E.adminEtsy({ action: "status" }, ADMIN);
  assert.equal(st.listings.find((l) => l.id === "brasil").newPhotos, false);
  const again = await E.adminEtsy({ action: "publish", id: "brasil" }, ADMIN);
  assert.equal(again.skipped, true);
});

test("new photos: a listing left broken by an earlier try (one old photo at rank 3, or two at rank 1) is repaired", async () => {
  for (const broken of [[{ id: 71, rank: 3 }], [{ id: 71, rank: 1 }, { id: 72, rank: 1 }]]) {
    const { db, E, IMGS, ACTIVE } = setup();
    db.docs.set("etsy/auth", { access: "777.abc", refresh: "r1", expiresAt: Date.now() + 3600e3, shopId: 55 });
    db.docs.set("etsy/listings", { brasil: { listingId: 4242, state: "active", url: "u", error: "Etsy: The ListingImages for this Listing are in an inconsistent order." } });
    IMGS[4242] = broken; ACTIVE.add("4242");
    globalThis.__lenient = false;
    await E.adminEtsy({ action: "publish", id: "brasil" }, ADMIN);
    const now = order(IMGS, 4242);
    assert.deepEqual(now.map((x) => x.rank), [1, 2, 3, 4, 5, 6]);
    assert.ok(now.every((x) => x.id > 1000));
    const st = await E.adminEtsy({ action: "status" }, ADMIN);
    const b = st.listings.find((l) => l.id === "brasil");
    assert.equal(b.newPhotos, false);
    assert.equal(b.error, "");
  }
});

test("new photos: if Etsy refuses midway, the error is saved and a second tap finishes the job", async () => {
  const { db, E, IMGS, ACTIVE } = setup();
  db.docs.set("etsy/auth", { access: "777.abc", refresh: "r1", expiresAt: Date.now() + 3600e3, shopId: 55 });
  db.docs.set("etsy/listings", { brasil: { listingId: 4242, state: "active", url: "u" } });
  IMGS[4242] = [1, 2, 3, 4, 5, 6].map((r) => ({ id: 70 + r, rank: r })); ACTIVE.add("4242");
  globalThis.__dropImage = 3;   // three drops in a row: the third photo gives up
  await assert.rejects(E.adminEtsy({ action: "publish", id: "brasil" }, ADMIN));
  let st = await E.adminEtsy({ action: "status" }, ADMIN);
  assert.match(st.listings.find((l) => l.id === "brasil").error, /photos-writer/);
  assert.equal(st.listings.find((l) => l.id === "brasil").newPhotos, true);
  await E.adminEtsy({ action: "publish", id: "brasil" }, ADMIN);
  const now = order(IMGS, 4242);
  assert.deepEqual(now.map((x) => x.rank), [1, 2, 3, 4, 5, 6]);
  assert.ok(now.every((x) => x.id > 1000));
  st = await E.adminEtsy({ action: "status" }, ADMIN);
  assert.equal(st.listings.find((l) => l.id === "brasil").newPhotos, false);
});

test("Etsy's per-second limit (429): waits and tries the same call again", async () => {
  const { db, E, IMGS, ACTIVE } = setup();
  db.docs.set("etsy/auth", { access: "777.abc", refresh: "r1", expiresAt: Date.now() + 3600e3, shopId: 55 });
  db.docs.set("etsy/listings", { brasil: { listingId: 4242, state: "active", url: "u" } });
  IMGS[4242] = [{ id: 71, rank: 1 }]; ACTIVE.add("4242");
  const real = globalThis.fetch; let busy = 2;
  globalThis.fetch = async (url, opts) => (busy-- > 0 ? { ok: false, status: 429, json: async () => ({ error: "Exceeded per second rate limit" }) } : real(url, opts));
  await E.adminEtsy({ action: "publish", id: "brasil" }, ADMIN);
  assert.deepEqual(order(IMGS, 4242).map((x) => x.rank), [1, 2, 3, 4, 5, 6]);
});
