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
    if (path === "999/videos") return ok({ data: [] });
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
    if (path === "999/videos") return ok({ data: [] });
    throw new Error("unexpected " + url);
  };
  v = await C.adminContent({ action: "sync" }, THIAGO);
  const s = v.items.find((i) => i.id === "s");
  assert.equal(s.igId, "1901");
  assert.equal(s.status, "posted");
  assert.equal(s.mediaUrl, "https://cdn/z.mp4");
  assert.equal(v.items.filter((i) => i.source === "facebook").length, 0);   // the cover photo didn't come in
});

test("scheduled in the app: needs publish permission, goes out at its time on Instagram (Reel) and Facebook, tells both", async () => {
  const { db, bucket, pushes, C } = setup();
  require("../ads")._internal.setPause(1); C._setWait(1);
  assert.equal(new Date(C._nyToUtc("2026-11-20", "19:00")).toISOString(), "2026-11-21T00:00:00.000Z");
  assert.equal(new Date(C._nyToUtc("2026-07-04", "09:30")).toISOString(), "2026-07-04T13:30:00.000Z");
  db.docs.set("settings/content", { seeded: "x", fix1: "x", fix2: "x", sync: { at: new Date().toISOString() } });
  db.docs.set("ads/auth", { meta: { token: "EAAB" + "x".repeat(60), adAccountId: "act_1", pageId: "999", igUserId: "1784" } });
  bucket.files.set("content/v1/1-santa.mp4", { data: Buffer.alloc(50), contentType: "video/mp4" });
  db.docs.set("content/v1", { title: "Santa", kind: "video", status: "ready", source: "app", caption: "Santa, but a magnet", nets: {}, posted: {},
    files: [{ path: "content/v1/1-santa.mp4", name: "santa.mp4", type: "video/mp4", size: 50 }] });
  let scopes = ["ads_management", "instagram_basic"], igPolls = 0;
  const calls = [];
  globalThis.fetch = async (url, init = {}) => {
    const u = new URL(url), path = u.pathname.replace(/^\/v\d+\.\d+\//, ""), body = init.body ? Object.fromEntries(new URLSearchParams(String(init.body))) : {};
    calls.push({ host: u.host, path, method: init.method, body });
    const ok = (j) => ({ ok: true, status: 200, json: async () => j });
    if (path === "debug_token") return ok({ data: { scopes } });
    if (path === "1784/media" && init.method === "POST") { assert.equal(body.media_type, "REELS"); assert.match(body.video_url, /santa\.mp4/); return ok({ id: "c1" }); }
    if (path === "c1") { igPolls += 1; return ok({ status_code: igPolls < 2 ? "IN_PROGRESS" : "FINISHED" }); }
    if (path === "1784/media_publish") return ok({ id: "ig77" });
    if (path === "ig77") return ok({ permalink: "https://instagram.com/reel/77" });
    if (path === "999" && u.searchParams.get("fields") === "access_token") return ok({ access_token: "PAGE" + "y".repeat(40) });
    if (path === "999/videos") { assert.equal(u.host, "graph-video.facebook.com"); assert.match(body.access_token, /^PAGE/); return ok({ id: "fbv1" }); }
    throw new Error("unexpected " + url);
  };
  const when = C._nyParts(Date.now() + 2 * 3600000);
  // without the publish permission it says what is missing
  await assert.rejects(C.adminContent({ action: "schedule", id: "v1", date: when.date, time: when.time, nets: { instagram: true, facebook: true } }, THIAGO),
    /instagram_content_publish, pages_manage_posts/);
  scopes = ["instagram_basic", "instagram_content_publish", "pages_manage_posts"];
  await assert.rejects(C.adminContent({ action: "schedule", id: "v1", date: "2020-01-01", time: "10:00", nets: { instagram: true } }, THIAGO), /future/);
  let v = await C.adminContent({ action: "schedule", id: "v1", date: when.date, time: when.time, nets: { instagram: true, facebook: true } }, THIAGO);
  let it = v.items.find((i) => i.id === "v1");
  assert.equal(it.status, "scheduled");
  assert.equal(it.sched.state, "waiting");
  assert.match(pushes.at(-1).body, /Thiago agendou pelo app: Santa · sai/);
  assert.equal(pushes.at(-1).to, "https://push/karina");
  // not yet
  assert.deepEqual(await C.publishDue(Date.now()), { done: 0, processing: 0, error: 0 });
  // at its time: Reel processed, published; Facebook video; posted, both told
  const n0 = pushes.length;
  assert.deepEqual(await C.publishDue(Date.now() + 3 * 3600000), { done: 1, processing: 0, error: 0 });
  it = db.get("content/v1");
  assert.equal(it.status, "posted");
  assert.equal(it.sched.state, "done");
  assert.equal(it.igId, "ig77");
  assert.equal(it.igLink, "https://instagram.com/reel/77");
  assert.equal(it.fbVideoId, "fbv1");
  assert.ok(it.posted.instagram && it.posted.facebook);
  assert.equal(pushes.length - n0, 2);                                   // both phones
  assert.match(pushes.at(-1).body, /Saiu no Instagram e Facebook ✓ Santa/);
  assert.deepEqual(await C.publishDue(Date.now() + 4 * 3600000), { done: 0, processing: 0, error: 0 });   // never twice
  await assert.rejects(C.adminContent({ action: "unschedule", id: "v1" }, THIAGO), /already/);
});

test("scheduled in the app: when Instagram refuses the file it says why, and it can be tried again or cancelled", async () => {
  const { db, bucket, pushes, C } = setup();
  require("../ads")._internal.setPause(1); C._setWait(1);
  db.docs.set("settings/content", { seeded: "x", fix1: "x", fix2: "x", sync: { at: new Date().toISOString() } });
  db.docs.set("ads/auth", { meta: { token: "EAAB" + "x".repeat(60), adAccountId: "act_1", pageId: "999", igUserId: "1784" } });
  bucket.files.set("content/v2/1-a.mov", { data: Buffer.alloc(50), contentType: "video/quicktime" });
  db.docs.set("content/v2", { title: "Packing", kind: "video", status: "ready", source: "app", nets: {}, posted: {},
    files: [{ path: "content/v2/1-a.mov", name: "a.mov", type: "video/quicktime", size: 50 }] });
  let bad = true;
  globalThis.fetch = async (url, init = {}) => {
    const u = new URL(url), path = u.pathname.replace(/^\/v\d+\.\d+\//, "");
    const ok = (j) => ({ ok: true, status: 200, json: async () => j });
    if (path === "debug_token") return ok({ data: { scopes: ["instagram_content_publish", "pages_manage_posts"] } });
    if (path === "1784/media") return ok({ id: bad ? "cbad" : "cgood" });
    if (path === "cbad") return ok({ status_code: "ERROR" });
    if (path === "cgood") return ok({ status_code: "FINISHED" });
    if (path === "1784/media_publish") return ok({ id: "ig9" });
    if (path === "ig9") return ok({ permalink: "https://instagram.com/reel/9" });
    throw new Error("unexpected " + url);
  };
  const when = C._nyParts(Date.now() + 2 * 3600000);
  await C.adminContent({ action: "schedule", id: "v2", date: when.date, time: when.time, nets: { instagram: true } }, KARINA);
  assert.deepEqual(await C.publishDue(Date.now() + 3 * 3600000), { done: 0, processing: 0, error: 1 });
  let it = db.get("content/v2");
  assert.equal(it.sched.state, "error");
  assert.match(it.sched.err, /não aceitou/);
  assert.match(pushes.at(-1).body, /Não deu para publicar “Packing”/);
  bad = false;
  const v = await C.adminContent({ action: "retry", id: "v2" }, KARINA);
  it = v.items.find((i) => i.id === "v2");
  assert.equal(it.status, "posted");
  assert.equal(it.igId, "ig9");
  // cancelling a waiting one puts it back in Shared
  db.docs.set("content/v3", { title: "Later", kind: "video", status: "scheduled", source: "app", nets: {}, posted: {}, files: [{ path: "x", type: "video/mp4" }],
    sched: { at: new Date(Date.now() + 9e6).toISOString(), state: "waiting", nets: { instagram: true }, path: "x", type: "video/mp4" } });
  const v2 = await C.adminContent({ action: "unschedule", id: "v3" }, KARINA);
  const c3 = v2.items.find((i) => i.id === "v3");
  assert.equal(c3.status, "ready");
  assert.equal(c3.sched, null);
});

test("scheduled in Business Suite: the unpublished Page video shows as scheduled (video and caption), then becomes posted", async () => {
  const { db, C } = setup();
  require("../ads")._internal.setPause(1);
  db.docs.set("settings/content", { seeded: "x", fix1: "x", fix2: "x" });
  db.docs.set("ads/auth", { meta: { token: "EAAB" + "x".repeat(60), adAccountId: "act_1", pageId: "999", igUserId: "1784" } });
  let out = false, pend = [{ id: "v55", published: false, description: "Packing this one with a whole lot of love\nThis order is going to Ohio", source: "https://video.fb/v55.mp4", picture: "https://pic/v55.jpg", created_time: new Date().toISOString() },
    { id: "v56", published: true, description: "old" }];
  const now = Date.now();
  globalThis.fetch = async (url) => {
    const u = new URL(url), path = u.pathname.replace(/^\/v\d+\.\d+\//, "");
    const ok = (j) => ({ ok: true, status: 200, json: async () => j });
    if (path === "1784/media") return ok({ data: out ? [{ id: "1901", caption: "Packing this one with a whole lot of love\nThis order is going to Ohio", media_type: "VIDEO", media_product_type: "REELS",
      permalink: "https://instagram.com/reel/z", timestamp: new Date(now + 5 * 86400000).toISOString(), thumbnail_url: "https://cdn/z.jpg", media_url: "https://cdn/z.mp4" }] : [] });
    if (path === "999") return ok({ access_token: "PAGE" + "y".repeat(40) });
    if (path === "999/scheduled_posts" || path === "999/posts") return ok({ data: [] });
    if (path === "999/videos") return ok({ data: out ? [] : pend });
    throw new Error("unexpected " + url);
  };
  let v = await C.adminContent({ action: "sync" }, THIAGO);
  let p = v.items.filter((i) => i.fbPendingId === "v55");
  assert.equal(p.length, 1);
  assert.equal(p[0].status, "scheduled");
  assert.equal(p[0].mediaUrl, "https://video.fb/v55.mp4");
  assert.equal(p[0].source, "meta-pending");
  assert.equal(v.sync.counts.scheduled, 1);
  v = await C.adminContent({ action: "sync" }, THIAGO);
  assert.equal(v.items.filter((i) => i.fbPendingId === "v55").length, 1);            // not twice
  out = true;                                                                         // five days later it goes out
  v = await C.adminContent({ action: "sync" }, THIAGO);
  assert.equal(v.items.length, 1);
  assert.equal(v.items[0].status, "posted");
  assert.equal(v.items[0].igId, "1901");
});

/* ---------- the schedule options (what Business Suite lets them choose) ---------- */
function metaMock(handlers) {
  const calls = [];
  globalThis.fetch = async (url, init = {}) => {
    const u = new URL(url), path = u.pathname.replace(/^\/(video-upload\/)?v\d+\.\d+\//, "");
    const body = init.body instanceof FormData ? Object.fromEntries(init.body.entries()) : init.body ? Object.fromEntries(new URLSearchParams(String(init.body))) : Object.fromEntries(u.searchParams);
    const c = { host: u.host, path, method: init.method || "GET", body, headers: init.headers || {} };
    calls.push(c);
    const ok = (j) => ({ ok: true, status: 200, json: async () => j });
    if (path === "debug_token") return ok({ data: { scopes: ["instagram_content_publish", "pages_manage_posts"] } });
    if (path === "999" && u.searchParams.get("fields") === "access_token") return ok({ access_token: "PAGE" + "y".repeat(40) });
    for (const [test, reply] of handlers) {
      if (test(c)) { const r = typeof reply === "function" ? reply(c) : reply; return r && r.__err ? { ok: false, status: 400, json: async () => ({ error: { message: r.__err } }) } : ok(r); }
    }
    throw new Error("unexpected " + c.method + " " + url);
  };
  return calls;
}
function optsSetup(files) {
  const s = setup();
  require("../ads")._internal.setPause(1); s.C._setWait(1);
  s.db.docs.set("settings/content", { seeded: "x", fix1: "x", fix2: "x", sync: { at: new Date().toISOString() } });
  s.db.docs.set("ads/auth", { meta: { token: "EAAB" + "x".repeat(60), adAccountId: "act_1", pageId: "999", igUserId: "1784" } });
  files.forEach((f) => s.bucket.files.set(f.path, { data: Buffer.alloc(40), contentType: f.type }));
  s.db.docs.set("content/k1", { title: "Brasil", kind: "photo", status: "ready", source: "app", caption: "Honoring our roots", nets: {}, posted: {}, files });
  return { ...s, when: s.C._nyParts(Date.now() + 2 * 3600000) };
}
const F3 = [{ path: "content/k1/1-a.jpg", name: "a.jpg", type: "image/jpeg" }, { path: "content/k1/2-b.mp4", name: "b.mp4", type: "video/mp4" }, { path: "content/k1/3-c.jpg", name: "c.jpg", type: "image/jpeg" }];

test("options: an Instagram carousel (photos and a video) with alt text, tags, collaborators, first comment and comments off", async () => {
  const { db, pushes, C, when } = optsSetup(F3);
  let kid = 0, vpoll = 0;
  const calls = metaMock([
    [(c) => c.path === "1784/media" && c.body.is_carousel_item === "true", () => ({ id: "ch" + (++kid) })],
    [(c) => c.path === "ch2" && c.method === "GET", () => ({ status_code: ++vpoll < 2 ? "IN_PROGRESS" : "FINISHED" })],
    [(c) => c.path === "1784/media" && c.body.media_type === "CAROUSEL", { id: "car1" }],
    [(c) => c.path === "car1", { status_code: "FINISHED" }],
    [(c) => c.path === "1784/media_publish", { id: "ig5" }],
    [(c) => c.path === "ig5" && c.method === "GET", { permalink: "https://instagram.com/p/5" }],
    [(c) => c.path === "ig5/comments", { id: "cm1" }],
    [(c) => c.path === "ig5" && c.method === "POST", { success: true }],
  ]);
  // Facebook can't take a carousel with a video
  await assert.rejects(C.adminContent({ action: "schedule", id: "k1", files: F3.map((f) => f.path), date: when.date, time: when.time, nets: { instagram: true, facebook: true } }, THIAGO), /carousel with videos/);
  await C.adminContent({ action: "schedule", id: "k1", files: F3.map((f) => f.path), date: when.date, time: when.time, nets: { instagram: true },
    alts: { "content/k1/1-a.jpg": "A green saudade magnet" },
    opts: { collaborators: "@karina.lhh, bad!name, @Shop_2", tags: [{ u: "@vo.maria", x: 0.2, y: 0.8 }, "tio_ze"], firstComment: "Which one is yours?", commentsOff: true } }, THIAGO);
  let it = db.get("content/k1");
  assert.equal(it.sched.format, "post");
  assert.deepEqual(it.sched.opts.collaborators, ["karina.lhh", "shop_2"]);
  assert.deepEqual(it.sched.opts.tags, [{ u: "vo.maria", x: 0.2, y: 0.8 }, { u: "tio_ze" }]);
  assert.deepEqual(await C.publishDue(Date.now() + 3 * 3600000), { done: 1, processing: 0, error: 0 });
  const kids = calls.filter((c) => c.body.is_carousel_item === "true");
  assert.equal(kids.length, 3);
  assert.equal(kids[0].body.alt_text, "A green saudade magnet");
  assert.deepEqual(JSON.parse(kids[0].body.user_tags), [{ username: "vo.maria", x: 0.2, y: 0.8 }, { username: "tio_ze", x: 0.3, y: 0.35 }]);
  assert.equal(kids[1].body.media_type, "VIDEO");
  assert.equal(kids[2].body.user_tags, undefined);                     // tags go on the first photo
  const parent = calls.find((c) => c.body.media_type === "CAROUSEL");
  assert.equal(parent.body.children, "ch1,ch2,ch3");
  assert.deepEqual(JSON.parse(parent.body.collaborators), ["karina.lhh", "shop_2"]);
  assert.equal(calls.find((c) => c.path === "ig5/comments").body.message, "Which one is yours?");
  assert.equal(calls.find((c) => c.path === "ig5" && c.method === "POST").body.comment_enabled, "false");
  it = db.get("content/k1");
  assert.equal(it.status, "posted"); assert.equal(it.igLink, "https://instagram.com/p/5");
  assert.match(pushes.at(-1).body, /Saiu no Instagram ✓ Brasil$/);
});

test("options: a Reel with a cover photo, test Reel, audio name, not on the feed; Facebook Reel with its own caption and the cover", async () => {
  const files = [{ path: "content/k1/1-r.mp4", name: "r.mp4", type: "video/mp4" }];
  const { db, bucket, pushes, C, when } = optsSetup(files);
  bucket.files.set("content/k1/9-cover.jpg", { data: Buffer.from("jpegbytes"), contentType: "image/jpeg" });
  let first = true;
  const calls = metaMock([
    [(c) => c.path === "1784/media" && c.method === "POST", (c) => { if (first && c.body.collaborators) { first = false; return { __err: "Invalid user id" }; } return { id: "r1" }; }],
    [(c) => c.path === "r1", { status_code: "FINISHED" }],
    [(c) => c.path === "1784/media_publish", { id: "ig6" }],
    [(c) => c.path === "ig6", { permalink: "https://instagram.com/reel/6" }],
    [(c) => c.path === "999/video_reels" && c.body.upload_phase === "start", { video_id: "fbr1", upload_url: "https://rupload.facebook.com/video-upload/v26.0/fbr1" }],
    [(c) => c.host === "rupload.facebook.com", { success: true }],
    [(c) => c.path === "999/video_reels" && c.body.upload_phase === "finish", { success: true }],
    [(c) => c.path === "fbr1/thumbnails", { success: true }],
    [(c) => c.path === "fbr1/comments", { id: "fc1" }],
  ]);
  await assert.rejects(C.adminContent({ action: "schedule", id: "k1", date: when.date, time: when.time, nets: { instagram: true }, cover: "content/zz9999/9-cover.jpg" }, THIAGO), /cover isn't from this post/);
  await C.adminContent({ action: "schedule", id: "k1", date: when.date, time: when.time, nets: { instagram: true, facebook: true }, caption: "IG words #magnets",
    cover: "content/k1/9-cover.jpg",
    opts: { shareToFeed: false, trial: "SS_PERFORMANCE", audioName: "Saudade (original)", collaborators: ["nobody.here"], firstComment: "Link in bio!", fbCaption: "FB words", fbTitle: "Saudade" } }, KARINA);
  assert.equal(db.get("content/k1").sched.format, "reel");
  assert.deepEqual(await C.publishDue(Date.now() + 3 * 3600000), { done: 1, processing: 0, error: 0 });
  const reel = calls.filter((c) => c.path === "1784/media").at(-1).body;
  assert.equal(reel.media_type, "REELS"); assert.equal(reel.share_to_feed, "false"); assert.equal(reel.audio_name, "Saudade (original)");
  assert.deepEqual(JSON.parse(reel.trial_params), { graduation_strategy: "SS_PERFORMANCE" });
  assert.match(reel.cover_url, /9-cover\.jpg/); assert.equal(reel.thumb_offset, undefined); assert.equal(reel.collaborators, undefined);
  assert.equal(reel.caption, "IG words #magnets");
  const up = calls.find((c) => c.host === "rupload.facebook.com");
  assert.match(up.headers.file_url, /1-r\.mp4/); assert.match(up.headers.Authorization, /^OAuth PAGE/);
  const fin = calls.find((c) => c.body.upload_phase === "finish");
  assert.equal(fin.body.description, "FB words"); assert.equal(fin.body.video_state, "PUBLISHED"); assert.equal(fin.body.title, "Saudade");
  const th = calls.find((c) => c.path === "fbr1/thumbnails");
  assert.equal(th.body.is_preferred, "true"); assert.equal(Buffer.from(await th.body.source.arrayBuffer()).toString(), "jpegbytes");
  assert.equal(calls.find((c) => c.path === "fbr1/comments").body.message, "Link in bio!");
  const it = db.get("content/k1");
  assert.equal(it.status, "posted"); assert.equal(it.fbVideoId, "fbr1");
  assert.match(pushes.at(-1).body, /Saiu no Instagram e Facebook ✓ Brasil \(atenção: o Instagram não aceitou os colaboradores/);
});

test("options: a moment of the video as the cover; Facebook Pages without Reels get a normal video", async () => {
  const files = [{ path: "content/k1/1-r.mp4", name: "r.mp4", type: "video/mp4" }];
  const { db, bucket, C, when } = optsSetup(files);
  bucket.files.set("content/k1/9-frame.jpg", { data: Buffer.from("frame"), contentType: "image/jpeg" });
  const calls = metaMock([
    [(c) => c.path === "1784/media" && c.method === "POST", { id: "r2" }],
    [(c) => c.path === "r2", { status_code: "FINISHED" }],
    [(c) => c.path === "1784/media_publish", { id: "ig7" }],
    [(c) => c.path === "ig7", { permalink: "x" }],
    [(c) => c.path === "999/video_reels", { __err: "Reels not available" }],
    [(c) => c.path === "999/videos", { id: "fbv9" }],
    [(c) => c.path === "fbv9/thumbnails", { success: true }],
  ]);
  await C.adminContent({ action: "schedule", id: "k1", date: when.date, time: when.time, nets: { instagram: true, facebook: true }, cover: "content/k1/9-frame.jpg", offsetMs: 2350.4 }, THIAGO);
  assert.deepEqual(await C.publishDue(Date.now() + 3 * 3600000), { done: 1, processing: 0, error: 0 });
  const reel = calls.find((c) => c.path === "1784/media").body;
  assert.equal(reel.thumb_offset, "2350"); assert.equal(reel.cover_url, undefined);     // Instagram picks the same moment itself
  assert.equal(reel.share_to_feed, "true");
  assert.equal(calls.find((c) => c.path === "999/videos").host, "graph-video.facebook.com");
  assert.ok(calls.find((c) => c.path === "fbv9/thumbnails"));
  assert.equal(db.get("content/k1").fbVideoId, "fbv9");
});

test("options: several photos on Facebook become one post; a Story goes to both; editing a schedule keeps the options", async () => {
  const F2 = [{ path: "content/k1/1-a.jpg", name: "a.jpg", type: "image/jpeg" }, { path: "content/k1/2-b.jpg", name: "b.jpg", type: "image/jpeg" }];
  const { db, bucket, pushes, C, when } = optsSetup(F2);
  let ph = 0;
  const calls = metaMock([
    [(c) => c.path === "999/photos" && c.body.published === "false", () => ({ id: "ph" + (++ph) })],
    [(c) => c.path === "999/feed", { id: "999_77" }],
    [(c) => c.path === "999_77/comments", { id: "c" }],
    [(c) => c.path === "1784/media" && c.body.media_type === "STORIES", { id: "st1" }],
    [(c) => c.path === "st1", { status_code: "FINISHED" }],
    [(c) => c.path === "1784/media_publish", { id: "ig8" }],
    [(c) => c.path === "ig8", { permalink: "x" }],
    [(c) => c.path === "999/photo_stories", { post_id: "999_88" }],
  ]);
  await C.adminContent({ action: "schedule", id: "k1", files: F2.map((f) => f.path), date: when.date, time: when.time, nets: { facebook: true },
    alts: { "content/k1/2-b.jpg": "Pão de queijo magnet" }, opts: { firstComment: "Tem mais!", fbCaption: "Para o Facebook" } }, THIAGO);
  // edited before it goes out: another time, same options; the other one is told it changed
  const later = C._nyParts(Date.now() + 5 * 3600000);
  await C.adminContent({ action: "schedule", id: "k1", files: F2.map((f) => f.path), date: later.date, time: later.time, nets: { facebook: true } }, KARINA);
  let it = db.get("content/k1");
  assert.equal(it.sched.opts.firstComment, "Tem mais!"); assert.equal(it.sched.opts.fbCaption, "Para o Facebook");
  assert.match(pushes.at(-1).body, /Karina mudou o agendamento de Brasil/);
  assert.deepEqual(await C.publishDue(Date.now() + 3 * 3600000), { done: 0, processing: 0, error: 0 });   // the new time
  assert.deepEqual(await C.publishDue(Date.now() + 6 * 3600000), { done: 1, processing: 0, error: 0 });
  const photos = calls.filter((c) => c.path === "999/photos");
  assert.equal(photos.length, 2); assert.equal(photos[1].body.alt_text_custom, "Pão de queijo magnet");
  const feed = calls.find((c) => c.path === "999/feed").body;
  assert.equal(feed.message, "Para o Facebook");
  assert.deepEqual(JSON.parse(feed.attached_media), [{ media_fbid: "ph1" }, { media_fbid: "ph2" }]);
  assert.equal(db.get("content/k1").fbPostId, "999_77");
  // a Story: one file only; goes to Instagram and Facebook stories
  db.docs.set("content/k2", { title: "Story", kind: "photo", status: "ready", source: "app", caption: "", nets: {}, posted: {}, files: [F2[0]] });
  db.docs.set("content/k3", { title: "Two", kind: "photo", status: "ready", source: "app", caption: "", nets: {}, posted: {}, files: F2 });
  await assert.rejects(C.adminContent({ action: "schedule", id: "k3", format: "story", files: F2.map((f) => f.path), date: when.date, time: when.time, nets: { instagram: true } }, THIAGO), /one photo or one video/);
  await assert.rejects(C.adminContent({ action: "schedule", id: "k1", date: later.date, time: later.time, nets: { facebook: true } }, THIAGO), /already going out/);
  await C.adminContent({ action: "schedule", id: "k2", format: "story", date: when.date, time: when.time, nets: { instagram: true, facebook: true }, opts: { firstComment: "ignored on stories" } }, THIAGO);
  assert.deepEqual(await C.publishDue(Date.now() + 3 * 3600000), { done: 1, processing: 0, error: 0 });
  assert.match(calls.find((c) => c.body.media_type === "STORIES").body.image_url, /1-a\.jpg/);
  assert.ok(calls.find((c) => c.path === "999/photo_stories"));
  assert.ok(!calls.some((c) => c.path === "ig8/comments"));
  assert.equal(db.get("content/k2").status, "posted");
});
