"use strict";
/* Instagram & Facebook (social.js): products picked from captions, the automatic answers, and one full run against a
   fake Graph API (tags waiting for Meta's approval, comments, Direct, the owners' phones). */
const test = require("node:test");
const assert = require("node:assert/strict");
const { FakeDB, FakeAuth, FakeBucket } = require("./fakes");
const deps = require("../deps");
const S = require("../social");

const ok = (j) => ({ ok: true, status: 200, json: async () => j });
function net(meta) {
  const calls = [];
  globalThis.fetch = async (url, init = {}) => {
    const u = new URL(url);
    const path = u.pathname.replace(/^\/v\d+\.\d+\//, "");
    const params = init.method === "POST" ? Object.fromEntries(new URLSearchParams(init.body.toString())) : Object.fromEntries(u.searchParams);
    calls.push({ method: init.method, path, params });
    const key = `${init.method} ${path}`;
    const h = meta[key] || Object.entries(meta).find(([k]) => k.endsWith("*") && key.startsWith(k.slice(0, -1)))?.[1];
    if (!h) return { ok: false, status: 400, json: async () => ({ error: { message: `no fake for ${key}` } }) };
    const out = typeof h === "function" ? h(params, path) : h;
    if (out && out.error) return { ok: false, status: 400, json: async () => out };
    return ok(out);
  };
  return calls;
}
const META = { token: "EAAB" + "x".repeat(60), adAccountId: "act_1", pageId: "999", igUserId: "1784", igUsername: "littlehivehouse" };
const recent = (h) => new Date(Date.now() - h * 3600000).toISOString();

test("captions: a design's name, a collection, photo magnets; nothing for a post about us", () => {
  S._reset();
  const fall = S.productsFromCaption("Pumpkin spice or sweater weather? Comment 1 or 2");
  assert.ok(fall.some((r) => /pumpkin-spice/.test(r)), fall.join());
  assert.ok(fall.some((r) => /sweater-weather/.test(r)), fall.join());
  const xmas = S.productsFromCaption("Our Christmas Collection is here! Pick a festive favorite");
  assert.ok(xmas.length >= 3 && xmas.every((r) => r.startsWith("christmas-")), xmas.join());
  assert.deepEqual(S.productsFromCaption("Turn your own photos into custom magnets"), ["photo-pack-4", "photo-pack-9"]);
  assert.deepEqual(S.productsFromCaption("Meet the makers behind Little Hive House! Two Brazilians living in our little home on wheels"), []);
});

test("plans: up to 5 on a photo with places, none on a video, an album spread over its photos", () => {
  const rids = ["a-1", "a-2", "a-3", "a-4", "a-5", "a-6", "a-7"];
  const img = S.planFor({ id: "m1", media_type: "IMAGE" }, rids);
  assert.equal(img.length, 1); assert.equal(img[0].tags.length, 5); assert.ok(img[0].tags.every((t) => t.x > 0 && t.y > 0));
  const vid = S.planFor({ id: "m2", media_type: "VIDEO" }, rids.slice(0, 2));
  assert.deepEqual(vid[0].tags, [{ rid: "a-1" }, { rid: "a-2" }]);
  const alb = S.planFor({ id: "m3", media_type: "CAROUSEL_ALBUM", children: { data: [{ id: "c1", media_type: "IMAGE" }, { id: "c2", media_type: "IMAGE" }] } }, rids);
  assert.deepEqual(alb.map((p) => [p.target, p.tags.length]), [["c1", 5], ["c2", 2]]);
});

test("automatic answers: thanks, prices, photos, Portuguese; a real question waits for the owners", () => {
  S._reset();
  assert.equal(S.intentOf("So cute!! 😍"), "thanks");
  assert.equal(S.intentOf("🐝🐝"), "thanks");
  assert.equal(S.intentOf("2"), "pick");
  assert.equal(S.intentOf("How much is one?"), "price");
  assert.equal(S.intentOf("Can I send my own photo?"), "photo");
  assert.equal(S.intentOf("Do you ship to Canada?"), "shipping");
  assert.equal(S.intentOf("My order arrived broken, what do I do?"), null);
  assert.match(S.autoReply("How much is one?", { name: "ana" }), /^@ana .*\$5 each.*littlehivehouse\.com/);
  assert.match(S.autoReply("Quanto custa?", { name: "ana" }), /\$5 cada/);
  assert.match(S.autoReply("Amei demais!"), /Obrigada|carinho|gostou/);
  assert.equal(S.autoReply("Is the paper thick? I want to use it outside"), "");
  assert.ok(!/—/.test(S.autoReply("How much is one?") + S.autoReply("Can I send my own photo?") + S.autoReply("Do you ship to Canada?")), "no em-dashes");
});

test("socialSync: tags what Meta approved and waits for the rest; comments and Direct saved, simple ones answered, phones told", async () => {
  S._reset();
  process.env.ADMIN_EMAILS = "owner@lhh.com";
  const db = new FakeDB();
  deps.set({ db, auth: new FakeAuth(), bucket: new FakeBucket() });
  db.docs.set("ads/auth", { meta: META });
  const pushes = [];
  require("../push").setSender(async (sub, payload) => { pushes.push(JSON.parse(payload)); return { statusCode: 201 }; });
  db.docs.set("adminPush/p1", { subscription: { endpoint: "https://push/1", keys: { p256dh: "x", auth: "y" } }, prefs: { messages: true }, uid: "admin1" });
  let approved = false;
  const calls = net({
    "GET 1784/media": { data: [
      { id: "m1", media_type: "IMAGE", caption: "Our Christmas Collection is here! Turn your own photos into magnets too", timestamp: recent(5), permalink: "https://ig/p/1" },
      { id: "m2", media_type: "IMAGE", caption: "Meet the makers", timestamp: recent(8), permalink: "https://ig/p/2" },
    ] },
    "GET m1/product_tags": { data: [] }, "GET m2/product_tags": { data: [] },
    "GET 1784/available_catalogs": { data: [{ catalog_id: "cat1" }] },
    "GET cat1/products": (p) => {
      const rid = JSON.parse(p.filter).retailer_id.eq;
      const ok2 = !rid.startsWith("photo-pack") || approved;
      return { data: [{ id: `P-${rid}`, capability_to_review_status: [{ key: "MINI_SHOPS", value: ok2 ? "APPROVED" : "OUTDATED" }] }] };
    },
    "POST m1/product_tags": { success: true },
    "GET m1/comments": { data: [
      { id: "c1", text: "So cute!! 😍", username: "maria", timestamp: recent(1) },
      { id: "c2", text: "My order came broken, help", username: "joe", timestamp: recent(1) },
      { id: "c3", text: "love it", username: "littlehivehouse", timestamp: recent(1) },
      { id: "c4", text: "how much?", username: "ann", timestamp: recent(2), replies: { data: [{ id: "r", username: "littlehivehouse", text: "Hi!" }] } },
    ] },
    "GET m2/comments": { data: [] },
    "POST c1/replies": { id: "r1" },
    "GET 999": { access_token: "PAGETOKEN" + "y".repeat(40) },
    "GET 999/published_posts": { data: [{ id: "999_1", created_time: recent(3), permalink_url: "https://fb/1", comments: { data: [{ id: "f1", message: "Quanto custa?", from: { id: "55", name: "Rita" }, created_time: recent(2) }] } }] },
    "POST f1/comments": { id: "fr1" },
    "GET 999/conversations": { data: [{ id: "t1", messages: { data: [{ id: "d1", message: "Do you ship to Canada?", from: { id: "IGS1", username: "lee" }, created_time: recent(1) }] } }] },
    "POST 999/messages": { recipient_id: "IGS1", message_id: "mid" },
  });
  const r = await S.socialSync();
  // tags: Christmas designs went on now, the photo packs wait; the post about us gets nothing
  const t1 = db.get("socialTags/m1"), t2 = db.get("socialTags/m2");
  assert.equal(t1.status, "pending");
  assert.ok(t1.done.length >= 3 && t1.done.every((x) => /christmas-/.test(x)), t1.done.join());
  assert.equal(t2.status, "none");
  const tagPost = calls.find((c) => c.method === "POST" && c.path === "m1/product_tags");
  assert.ok(JSON.parse(tagPost.params.updated_tags).every((g) => g.product_id.startsWith("P-christmas-") && g.x > 0));
  // comments: thanks answered by itself, the broken order waits, our own and answered ones skipped
  assert.equal(db.get("social/ig-c-c1").status, "auto");
  assert.equal(db.get("social/ig-c-c2").status, "new");
  assert.equal(db.get("social/ig-c-c3"), undefined);
  assert.equal(db.get("social/ig-c-c4").status, "answered");
  assert.equal(db.get("social/fb-c-f1").status, "auto");
  assert.match(calls.find((c) => c.path === "f1/comments").params.message, /cada/);
  assert.equal(db.get("social/ig-dm-d1").status, "auto");
  assert.equal(JSON.parse(calls.find((c) => c.path === "999/messages").params.recipient).id, "IGS1");
  assert.ok(pushes.some((p) => /joe/.test(p.body)), "the owners hear about the one that waits");
  assert.equal(r.comments.new, 5);
  // next run: Meta approved the photo packs -> tagged, done; nothing new arrives twice
  approved = true;
  const before = pushes.length;
  await S.socialSync();
  assert.equal(db.get("socialTags/m1").status, "done");
  assert.ok(db.get("socialTags/m1").done.some((x) => /photo-pack-4/.test(x)));
  assert.equal(pushes.length, before);
  // the owners answer the one that waited, from the app
  await assert.rejects(S.adminSocial({ action: "reply", id: "ig-c-c2", text: "x" }, null));
  net({ "POST c2/replies": { id: "r2" } });
  await S.adminSocial({ action: "reply", id: "ig-c-c2", text: "So sorry! We're sending a new one today." }, { uid: "a", token: { admin: true, email: "owner@lhh.com" } });
  assert.equal(db.get("social/ig-c-c2").status, "answered");
  require("../push").setSender(null);
});
