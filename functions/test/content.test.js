"use strict";
/* Conteúdo (content.js): the 6-month plan comes in once, posts are made and edited, the original files are recorded as
   uploaded (no resizing), the other owner gets a push, posted networks finish a post, and deleting removes the files. */
const test = require("node:test");
const assert = require("node:assert/strict");
const { FakeDB, FakeAuth, FakeBucket } = require("./fakes");
const deps = require("../deps");

const THIAGO = { uid: "u-thiago", token: { admin: true, email: "thiago@lhh.com" } };
const KARINA = { uid: "u-karina", token: { admin: true, email: "karina@lhh.com" } };

function setup() {
  Object.assign(process.env, { ADMIN_EMAILS: "thiago@lhh.com,karina@lhh.com" });
  const db = new FakeDB(), bucket = new FakeBucket();
  deps.set({ db, auth: new FakeAuth(), bucket });
  const pushes = [];
  require("../push").setSender(async (sub, payload) => { pushes.push({ to: sub.endpoint, ...JSON.parse(payload) }); return { statusCode: 201 }; });
  db.docs.set("adminPush/a", { endpoint: "https://push/thiago", keys: { p256dh: "k", auth: "a" }, uid: "u-thiago" });
  db.docs.set("adminPush/b", { endpoint: "https://push/karina", keys: { p256dh: "k", auth: "a" }, uid: "u-karina" });
  return { db, bucket, pushes, C: require("../content") };
}

test("the old 6-month plan goes away once (only untouched planned posts); nothing new is seeded", async () => {
  const { db, C } = setup();
  db.docs.set("settings/content", { fix1: "x" });
  db.docs.set("content/p1", { title: "Gift guide", kind: "photo", status: "todo", source: "plan", date: "2026-12-01", files: [], posted: {} });
  db.docs.set("content/p2", { title: "Made it", kind: "video", status: "ready", source: "plan", date: "2026-12-02", files: [{ path: "content/p2/x.mov" }], posted: {} });
  db.docs.set("content/p3", { title: "On Meta", kind: "photo", status: "scheduled", source: "plan", date: "2026-12-03", files: [], posted: {} });
  db.docs.set("content/a1", { title: "Ours", kind: "idea", status: "idea", source: "app", files: [], posted: {} });
  let v = await C.adminContent({ action: "list" }, THIAGO);
  assert.deepEqual(v.items.map((i) => i.id).sort(), ["a1", "p2", "p3"]);
  db.docs.set("content/p4", { title: "Later", kind: "photo", status: "todo", source: "plan", files: [], posted: {} });
  v = await C.adminContent({ action: "list" }, KARINA);
  assert.ok(v.items.some((i) => i.id === "p4"));                 // only once
  await assert.rejects(C.adminContent({ action: "list" }, { uid: "x", token: {} }), /admins/);
});

test("a new post, its original file, a push to the other owner only, posted networks and deleting", async () => {
  const { db, bucket, pushes, C } = setup();
  db.docs.set("settings/content", { seeded: "x", fix1: "x", fix2: "x" });
  await assert.rejects(C.adminContent({ action: "save", item: { title: "", kind: "idea", status: "idea" } }, THIAGO), /idea/);
  let v = await C.adminContent({ action: "save", item: { title: "Packing an order", kind: "video", status: "todo", date: "2026-11-20", time: "19:00", caption: "Pack with me #smallbusiness" } }, THIAGO);
  const id = v.id;
  let it = v.items.find((i) => i.id === id);
  assert.deepEqual(it.nets, { instagram: true, facebook: true, tiktok: true });
  // the phone uploaded the original (12 MB stays 12 MB)
  const path = `content/${id}/1763430000000-IMG_5280.MOV`;
  await assert.rejects(C.adminContent({ action: "addFile", id, path, name: "IMG_5280.MOV" }, THIAGO), /didn't finish/);
  bucket.files.set(path, { data: Buffer.alloc(12 * 1024 * 1024), contentType: "video/quicktime" });
  await assert.rejects(C.adminContent({ action: "addFile", id, path: "content/other/x.mov" }, THIAGO), /folder/);
  v = await C.adminContent({ action: "addFile", id, path, name: "IMG_5280.MOV", w: 1080, h: 1920, dur: 14 }, THIAGO);
  it = v.items.find((i) => i.id === id);
  assert.equal(it.files.length, 1);
  assert.equal(it.files[0].size, 12 * 1024 * 1024);
  assert.equal(it.files[0].type, "video/quicktime");
  assert.equal(it.status, "ready");
  assert.equal(pushes.length, 1);
  assert.equal(pushes[0].to, "https://push/karina");                 // only the other owner
  assert.match(pushes[0].body, /Thiago mandou um vídeo novo: Packing an order/);
  assert.equal(it.files[0].byName, "Thiago");
  // a video sent as an idea stays an idea and says so; a written idea tells the other one too
  v = await C.adminContent({ action: "save", item: { title: "Cat on the fridge", kind: "idea", status: "idea" } }, KARINA);
  assert.match(pushes[1].body, /Karina anotou uma ideia: Cat on the fridge/);
  assert.equal(pushes[1].to, "https://push/thiago");
  const idea = v.id, ipath = `content/${idea}/1-cat.mov`;
  bucket.files.set(ipath, { data: Buffer.alloc(100), contentType: "video/quicktime" });
  v = await C.adminContent({ action: "addFile", id: idea, path: ipath, name: "cat.mov" }, KARINA);
  assert.equal(v.items.find((i) => i.id === idea).status, "idea");
  assert.match(pushes[2].body, /Karina mandou um vídeo novo nas Ideias: Cat on the fridge/);
  await C.adminContent({ action: "remove", id: idea }, KARINA);
  // with no title, a video gets one
  v = await C.adminContent({ action: "save", item: { kind: "video", status: "ready" }, withFile: true }, THIAGO);
  assert.equal(v.items.find((i) => i.id === v.id).title, "Vídeo novo");
  await C.adminContent({ action: "remove", id: v.id }, THIAGO);
  // out on Instagram and Facebook: posted (TikTok still unticked); unticking everything takes it back
  v = await C.adminContent({ action: "posted", id, nets: { instagram: true, facebook: true } }, KARINA);
  assert.equal(v.items.find((i) => i.id === id).status, "posted");
  assert.ok(!v.items.find((i) => i.id === id).posted.tiktok);
  v = await C.adminContent({ action: "posted", id, nets: { instagram: false, facebook: false, tiktok: false } }, KARINA);
  assert.equal(v.items.find((i) => i.id === id).status, "ready");
  v = await C.adminContent({ action: "posted", id, nets: { instagram: true, facebook: true, tiktok: true } }, KARINA);
  it = v.items.find((i) => i.id === id);
  assert.equal(it.status, "posted");
  assert.ok(it.posted.instagram && it.posted.tiktok);
  // editing keeps what isn't sent
  v = await C.adminContent({ action: "save", id, item: { notes: "Use the trending sound" } }, KARINA);
  it = v.items.find((i) => i.id === id);
  assert.equal(it.caption, "Pack with me #smallbusiness");
  assert.equal(it.notes, "Use the trending sound");
  // deleting the post deletes its files
  v = await C.adminContent({ action: "remove", id }, THIAGO);
  assert.equal(v.items.length, 0);
  assert.equal(bucket.files.has(path), false);
});

test("Meta: Instagram posts and Facebook scheduled/published posts come in and match the planned ones", async () => {
  const { db, C } = setup();
  require("../ads")._internal.setPause(1);
  db.docs.set("settings/content", { seeded: "x", fix1: "x", fix2: "x" });
  db.docs.set("ads/auth", { meta: { token: "EAAB" + "x".repeat(60), adAccountId: "act_1", pageId: "999", igUserId: "1784" } });
  const now = Date.now(), day = C._nyParts(now).date, tomorrow = C._nyParts(now + 86400000);
  db.docs.set("content/plan1", { title: "Packing", kind: "video", status: "todo", date: day, time: "19:00", caption: "Grandma's fridge, upgraded.\nThe whole family", nets: { instagram: true, facebook: true, tiktok: false }, posted: {}, files: [] });
  db.docs.set("content/plan2", { title: "Gift guide", kind: "photo", status: "ready", date: tomorrow.date, time: "11:30", caption: "Holiday gift guide, fridge edition:", nets: { instagram: true, facebook: true }, posted: {}, files: [] });
  globalThis.fetch = async (url, init = {}) => {
    const u = new URL(url), path = u.pathname.replace(/^\/v\d+\.\d+\//, "");
    const ok = (j) => ({ ok: true, status: 200, json: async () => j });
    if (path === "1784/media") return ok({ data: [
      { id: "1801", caption: "Grandma's fridge, upgraded.\nThe whole family in photo magnets", media_type: "VIDEO", media_product_type: "REELS", permalink: "https://instagram.com/reel/a", timestamp: new Date(now - 3600000).toISOString(), thumbnail_url: "https://cdn/a.jpg", like_count: 12, comments_count: 2 },
      { id: "1802", caption: "Who we are", media_type: "IMAGE", permalink: "https://instagram.com/p/b", timestamp: "2026-11-05T15:00:00Z", media_url: "https://cdn/b.jpg" },
    ] });
    if (path === "999" && u.searchParams.get("fields") === "access_token") return ok({ access_token: "PAGE" + "y".repeat(40) });
    if (path === "999/scheduled_posts") { assert.match(u.searchParams.get("access_token"), /^PAGE/); return ok({ data: [{ id: "999_5", message: "Holiday gift guide, fridge edition:\nFor grandma", scheduled_publish_time: Math.floor((now + 86400000) / 1000), full_picture: "https://cdn/c.jpg" }] }); }
    if (path === "999/posts") return ok({ data: [{ id: "999_4", message: "Grandma's fridge, upgraded.", created_time: new Date(now - 3500000).toISOString(), permalink_url: "https://fb.com/p/4" }] });
    throw new Error("unexpected " + url);
  };
  const v = await C.adminContent({ action: "list" }, THIAGO);
  assert.deepEqual(v.sync.errors, {});
  const p1 = v.items.find((i) => i.id === "plan1"), p2 = v.items.find((i) => i.id === "plan2");
  assert.equal(p1.igId, "1801");
  assert.equal(p1.status, "posted");                                  // Instagram + Facebook, both chosen networks
  assert.equal(p1.igStats.likes, 12);
  assert.equal(p2.status, "scheduled");
  assert.equal(p2.fbScheduledId, "999_5");
  const old = v.items.find((i) => i.igId === "1802");
  assert.equal(old.status, "posted");
  assert.equal(old.source, "instagram");
  assert.equal(old.title, "Who we are");
  // the next open within 20 minutes doesn't ask Meta again; "sync" does
  let calls = 0; const f0 = globalThis.fetch; globalThis.fetch = async (...a) => { calls += 1; return f0(...a); };
  await C.adminContent({ action: "list" }, THIAGO);
  assert.equal(calls, 0);
  await C.adminContent({ action: "sync" }, THIAGO);
  assert.ok(calls >= 4);
  assert.equal((await C.adminContent({ action: "list" }, THIAGO)).items.length, 3);    // nothing doubled
});

test("fixes once: plan posts with no file back to to-make; cover photos out; same-day scheduled post matched; video plays", async () => {
  const { db, C } = setup();
  require("../ads")._internal.setPause(1);
  db.docs.set("settings/content", { seeded: "x", fix2: "x", sync: { at: new Date().toISOString() } });
  db.docs.set("content/a", { title: "Gift guide", kind: "photo", status: "ready", source: "plan", date: "2026-12-01", files: [], posted: {} });
  db.docs.set("content/b", { title: "Mine", kind: "video", status: "ready", source: "plan", date: "2026-12-02", files: [{ path: "content/b/x.mov" }], posted: {} });
  db.docs.set("content/c", { title: "Post do Facebook", kind: "photo", status: "posted", source: "facebook", caption: "", posted: { facebook: "x" } });
  let v = await C.adminContent({ action: "list" }, THIAGO);
  assert.equal(v.items.find((i) => i.id === "a").status, "todo");
  assert.equal(v.items.find((i) => i.id === "b").status, "ready");
  assert.equal(v.items.find((i) => i.id === "c"), undefined);
  db.docs.set("content/a", { title: "Gift guide", kind: "photo", status: "todo", source: "plan", date: "2026-12-01", files: [], posted: {} });
  await C.adminContent({ action: "list" }, THIAGO);
  assert.equal(db.get("content/a").status, "todo");                    // only once
  // marked "scheduled in Meta" for today; Meta posts it with another caption: the same post, now posted, video playable
  const now = Date.now(), day = C._nyParts(now).date;
  db.docs.set("content/s", { title: "Pack with me", kind: "video", status: "scheduled", source: "app", date: day, time: "19:00", caption: "Pack with me", nets: { instagram: true, facebook: true, tiktok: true }, posted: {}, files: [] });
  db.docs.set("ads/auth", { meta: { token: "EAAB" + "x".repeat(60), adAccountId: "act_1", pageId: "999", igUserId: "1784" } });
  globalThis.fetch = async (url) => {
    const u = new URL(url), path = u.pathname.replace(/^\/v\d+\.\d+\//, "");
    const ok = (j) => ({ ok: true, status: 200, json: async () => j });
    if (path === "1784/media") return ok({ data: [{ id: "1901", caption: "A totally new caption", media_type: "VIDEO", media_product_type: "REELS", permalink: "https://instagram.com/reel/z", timestamp: new Date(now - 60000).toISOString(), thumbnail_url: "https://cdn/z.jpg", media_url: "https://cdn/z.mp4" }] });
    if (path === "999") return ok({ access_token: "PAGE" + "y".repeat(40) });
    if (path === "999/scheduled_posts") return ok({ data: [] });
    if (path === "999/posts") return ok({ data: [{ id: "999_9", created_time: new Date(now - 86400000 * 3).toISOString(), full_picture: "https://cdn/cover.jpg" }] });
    throw new Error("unexpected " + url);
  };
  v = await C.adminContent({ action: "sync" }, THIAGO);
  const s = v.items.find((i) => i.id === "s");
  assert.equal(s.igId, "1901");
  assert.equal(s.status, "posted");
  assert.equal(s.mediaUrl, "https://cdn/z.mp4");
  assert.equal(v.items.filter((i) => i.source === "facebook").length, 0);   // the cover photo didn't come in
});
