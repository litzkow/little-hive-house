"use strict";
/* Conteúdo (Hive Admin › Conteúdo): the videos, photos and post ideas the owners pass to each other, instead of WhatsApp.
   Each item is a post to make: title, kind (video / photo / idea), status (idea → to make → ready → scheduled → posted),
   day and time, the networks it goes to and which ones already got it, caption, script, notes, and its files.
   Files are the originals, never resized or recompressed: the app uploads them straight to Storage
   (content/{itemId}/{file}, storage.rules: owners only, images and videos up to 4 GB) and saves them on the phone the
   same way. The first time the page opens, the 6-month plan (content-plan.json, from the "Redes sociais (6 meses)" doc)
   comes in as the planned posts from that day on.
   Firestore: content/{id}; settings/content {seeded}. A new file or a post marked ready sends a push to the other owner. */

const { fail, nowIso } = require("./config");
const deps = require("./deps");
const U = require("./util");

const COL = "content";
const KINDS = ["video", "photo", "idea"];
const STATUSES = ["idea", "todo", "ready", "scheduled", "posted"];
const NETS = ["instagram", "facebook", "tiktok"];
const PATH_RE = /^content\/[A-Za-z0-9_-]{6,40}\/[A-Za-z0-9._ ()-]{1,140}$/;
const db = () => deps.db();
const col = () => db().collection(COL);

const TZ = "America/New_York";
const today = () => new Intl.DateTimeFormat("en-CA", { timeZone: TZ, year: "numeric", month: "2-digit", day: "2-digit" }).format(new Date());

function cleanItem(d, cur) {
  d = d || {}; cur = cur || {};
  const pick = (k, fn) => (d[k] !== undefined ? fn(d[k]) : cur[k]);
  const out = {
    title: pick("title", (v) => U.text(v, 140)) || "",
    kind: pick("kind", (v) => (KINDS.includes(v) ? v : "idea")) || "idea",
    status: pick("status", (v) => (STATUSES.includes(v) ? v : "idea")) || "idea",
    date: pick("date", (v) => (/^\d{4}-\d{2}-\d{2}$/.test(String(v || "")) ? String(v) : "")) || "",
    time: pick("time", (v) => (/^\d{2}:\d{2}$/.test(String(v || "")) ? String(v) : "")) || "",
    caption: pick("caption", (v) => U.text(v, 2200)) || "",
    script: pick("script", (v) => U.text(v, 1500)) || "",
    onScreen: pick("onScreen", (v) => U.text(v, 300)) || "",
    tip: pick("tip", (v) => U.text(v, 600)) || "",
    notes: pick("notes", (v) => U.text(v, 2000)) || "",
    planFile: pick("planFile", (v) => U.text(v, 120)) || "",
  };
  const nets = d.nets !== undefined ? d.nets : cur.nets;
  out.nets = {};
  NETS.forEach((n) => { out.nets[n] = !!(nets && nets[n]); });
  if (!NETS.some((n) => out.nets[n]) && out.kind !== "idea") NETS.forEach((n) => { out.nets[n] = n !== "tiktok" || out.kind === "video"; });
  return out;
}

/** Seeds the planned posts once (from today on), so the page starts with what is already on the calendar. */
async function seed() {
  const ref = db().collection("settings").doc("content");
  const s = (await ref.get()).data() || {};
  if (s.seeded) return 0;
  const plan = require("./content-plan.json").items || [];
  const t = today();
  let n = 0;
  for (const p of plan) {
    if (p.date < t) continue;
    const item = cleanItem({
      title: p.title, kind: p.kind === "video" ? "video" : "photo", status: "todo", date: p.date, time: p.time,
      caption: p.caption, script: p.script, onScreen: p.onScreen, tip: p.tip, planFile: p.file || p.planB || "",
      nets: { instagram: true, facebook: true, tiktok: p.kind === "video" },
    });
    await col().add({ ...item, files: [], posted: {}, source: "plan", by: "plano", at: nowIso(), updatedAt: nowIso() });
    n += 1;
  }
  await ref.set({ seeded: nowIso(), seededCount: n }, { merge: true });
  return n;
}

/* ---------- what is already on Instagram / Facebook, and what is scheduled in Meta Business Suite ----------
   With the Meta connection of the Ads page (ads/auth.meta: a system-user token), every 20 minutes when the page opens
   (or on "Atualizar do Meta"): Instagram posts, the Facebook Page's posts and its scheduled posts. Each one is matched
   to a post here (same Meta id, or same day ±2 and the same start of caption), or comes in as a new one. Instagram
   scheduled posts aren't readable by apps; scheduled together with Facebook (as the guide says), the Facebook one shows. */
const fmtNY = new Intl.DateTimeFormat("en-CA", { timeZone: TZ, year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit", hourCycle: "h23" });
function nyParts(ms) {
  const p = Object.fromEntries(fmtNY.formatToParts(new Date(ms)).map((x) => [x.type, x.value]));
  return { date: `${p.year}-${p.month}-${p.day}`, time: `${p.hour}:${p.minute}` };
}
const norm = (s) => String(s || "").toLowerCase().normalize("NFD").replace(/[^a-z0-9]+/g, " ").trim().slice(0, 32);
/** Same post: the captions start the same way (24 letters, after dropping punctuation and accents). */
const same = (a, b) => { const x = norm(a).slice(0, 24); return x.length >= 12 && (b === "" || x === norm(b).slice(0, 24)); };
const dayDiff = (a, b) => Math.abs(Date.parse(`${a}T12:00:00Z`) - Date.parse(`${b}T12:00:00Z`)) / 86400000;
const firstLine = (s) => String(s || "").split("\n").map((x) => x.trim()).find(Boolean) || "";
function done(it) { const chosen = NETS.filter((n) => it.nets && it.nets[n]); return chosen.length > 0 && chosen.every((n) => it.posted && it.posted[n]); }

async function syncMeta({ force = false } = {}) {
  const sref = db().collection("settings").doc("content");
  const s = (await sref.get()).data() || {};
  const meta = (((await db().collection("ads").doc("auth").get()).data()) || {}).meta;
  if (!meta || !meta.token) return { connected: false };
  if (!force && s.sync && Date.now() - Date.parse(s.sync.at) < 20 * 60000) return s.sync;
  const G = require("./ads")._internal.graph;
  const q = await col().get();
  const items = q.docs.map((d) => ({ id: d.id, ...d.data() }));
  const changed = new Map();
  const touch = (it, patch) => { Object.assign(it, patch); changed.set(it.id || it, it); };
  // the same Meta id; or the same start of caption within 2 days; or, when the caption was changed in Meta, the one post
  // the owners marked "scheduled in Meta" for that same day
  const match = (key, id, caption, date) => items.find((i) => i[key] === id)
    || (same(caption, "") && items.find((i) => !i[key] && (i.source === "meta-pending" || i.source === "bs-manual" || (i.date && dayDiff(i.date, date) <= 2)) && same(i.caption, caption)))
    || (() => { const c = items.filter((i) => !i[key] && i.status === "scheduled" && i.date === date); return c.length === 1 ? c[0] : null; })();
  const add = (it) => { it.id = null; items.push(it); changed.set(it, it); return it; };
  const counts = { instagram: 0, facebook: 0, scheduled: 0 }, errors = {}, gone = [];

  // Instagram: what is already posted
  if (meta.igUserId) {
    try {
      const j = await G(meta, "GET", `${meta.igUserId}/media`, { fields: "id,caption,media_type,media_product_type,permalink,timestamp,thumbnail_url,media_url,like_count,comments_count", limit: 50 });
      ((j && j.data) || []).forEach((m) => {
        const at = Date.parse(m.timestamp || 0); if (!at) return;
        const { date, time } = nyParts(at);
        const kind = m.media_type === "VIDEO" || m.media_product_type === "REELS" ? "video" : "photo";
        const preview = m.thumbnail_url || (m.media_type === "VIDEO" ? "" : m.media_url) || "";
        const stats = { likes: Number(m.like_count) || 0, comments: Number(m.comments_count) || 0 };
        let it = match("igId", String(m.id), m.caption, date);
        if (!it) it = add({ ...cleanItem({ title: firstLine(m.caption).slice(0, 80) || "Post do Instagram", kind, status: "posted", date, time, caption: m.caption || "", nets: { instagram: true } }),
          files: [], posted: {}, source: "instagram", by: "Instagram", at: nowIso() });
        // a video's own file on Instagram (its link expires in a few days; refreshed on every sync) to play it in the app
        touch(it, { igId: String(m.id), igLink: m.permalink || "", preview: preview || it.preview || "", igStats: stats, mediaUrl: kind === "video" ? m.media_url || "" : "", posted: { ...(it.posted || {}), instagram: it.posted && it.posted.instagram || new Date(at).toISOString() },
          nets: { ...(it.nets || {}), instagram: true }, date, time });     // the real day and time it went out
        counts.instagram += 1;
      });
    } catch (e) { errors.instagram = e.message; }
  }
  // Facebook Page: posted and scheduled (needs the Page's own token)
  if (meta.pageId) {
    let page = null;
    try { const p = await G(meta, "GET", meta.pageId, { fields: "access_token" }); page = p.access_token ? { token: p.access_token, appSecret: meta.appSecret } : null; } catch (e) { errors.facebook = e.message; }
    if (page) {
      try {
        const j = await G(page, "GET", `${meta.pageId}/scheduled_posts`, { fields: "id,message,scheduled_publish_time,full_picture,permalink_url", limit: 50 });
        ((j && j.data) || []).forEach((m) => {
          const at = Number(m.scheduled_publish_time) * 1000 || Date.parse(m.scheduled_publish_time || 0); if (!at) return;
          const { date, time } = nyParts(at);
          let it = match("fbScheduledId", String(m.id), m.message, date);
          if (!it) it = add({ ...cleanItem({ title: firstLine(m.message).slice(0, 80) || "Post agendado", kind: "photo", status: "scheduled", date, time, caption: m.message || "", nets: { facebook: true } }),
            files: [], posted: {}, source: "facebook", by: "Meta Business Suite", at: nowIso() });
          touch(it, { fbScheduledId: String(m.id), preview: it.preview || m.full_picture || "", date, time, nets: { ...(it.nets || {}), facebook: true },
            status: it.status === "posted" ? "posted" : "scheduled" });
          counts.scheduled += 1;
        });
      } catch (e) { errors.scheduled = e.message; }
      try {
        const j = await G(page, "GET", `${meta.pageId}/posts`, { fields: "id,message,created_time,permalink_url,full_picture", limit: 40 });
        ((j && j.data) || []).forEach((m) => {
          const at = Date.parse(m.created_time || 0); if (!at) return;
          if (!String(m.message || "").trim()) return;   // a new cover or profile photo, not a post
          const { date, time } = nyParts(at);
          let it = match("fbPostId", String(m.id), m.message, date);
          if (!it) it = add({ ...cleanItem({ title: firstLine(m.message).slice(0, 80) || "Post do Facebook", kind: "photo", status: "posted", date, time, caption: m.message || "", nets: { facebook: true } }),
            files: [], posted: {}, source: "facebook", by: "Facebook", at: nowIso() });
          touch(it, { fbPostId: String(m.id), fbLink: m.permalink_url || "", preview: it.preview || m.full_picture || "",
            ...(it.igId ? {} : { date, time }),
            posted: { ...(it.posted || {}), facebook: it.posted && it.posted.facebook || new Date(at).toISOString() }, nets: { ...(it.nets || {}), facebook: true } });
          counts.facebook += 1;
        });
      } catch (e) { errors.facebook = errors.facebook || e.message; }
      // Business Suite keeps what is scheduled as an unpublished Page video (no time is given): it shows as scheduled
      try {
        const j = await G(page, "GET", `${meta.pageId}/videos`, { fields: "id,description,published,picture,source,created_time", limit: 50 });
        const seen = new Set();
        ((j && j.data) || []).filter((v) => v.published === false).forEach((v) => {
          seen.add(String(v.id));
          let it = items.find((i) => i.fbPendingId === String(v.id))
            || (same(v.description, "") && items.find((i) => !i.fbPendingId && i.status !== "posted" && same(i.caption, v.description)));
          if (it && it.status === "posted") return;
          if (!it) it = add({ ...cleanItem({ title: firstLine(v.description).slice(0, 80) || "Vídeo agendado", kind: "video", status: "scheduled", caption: v.description || "",
            nets: { instagram: true, facebook: true } }), files: [], posted: {}, source: "meta-pending", by: "Meta Business Suite", at: nowIso() });
          touch(it, { fbPendingId: String(v.id), preview: v.picture || it.preview || "", mediaUrl: v.source || it.mediaUrl || "", pendingSince: v.created_time || "",
            status: it.sched || it.status === "posted" ? it.status : "scheduled" });
          counts.scheduled += 1;
        });
        // a pending one that is gone from Meta (deleted there) goes away here too
        items.filter((i) => i.id && i.source === "meta-pending" && i.status === "scheduled" && !seen.has(i.fbPendingId)
          && !(i.posted && (i.posted.instagram || i.posted.facebook))).forEach((i) => gone.push(i.id));
      } catch (e) { errors.pending = e.message; }
    }
  }
  for (const it of changed.values()) {
    // out on Instagram or Facebook = posted (TikTok, which Meta can't see, is ticked by hand on the card)
    if (done(it) || (it.posted && (it.posted.instagram || it.posted.facebook))) it.status = "posted";
    const { id, ...data } = it;
    data.updatedAt = nowIso();
    if (id) await col().doc(id).set(data, { merge: true }); else await col().add(data);
  }
  for (const id of gone) await col().doc(id).delete();
  const out = { at: nowIso(), connected: true, counts, errors, ig: meta.igUsername || "" };
  await sref.set({ sync: out }, { merge: true });
  return out;
}

/* Once: the calendar posts came in as "ready" with no file (only the plan existed), and the Page's cover/profile photo
   changes came in as posts. Plan posts with no file go back to "to make"; posts with no text from Facebook go away. */
async function fixOnce() {
  const ref = db().collection("settings").doc("content");
  if (((await ref.get()).data() || {}).fix1) return;
  const q = await col().get();
  for (const d of q.docs) {
    const i = d.data();
    if (i.source === "plan" && i.status === "ready" && !(i.files || []).length) await d.ref.set({ status: "todo", updatedAt: nowIso() }, { merge: true });
    if (i.source === "facebook" && !String(i.caption || "").trim() && !i.igId) await d.ref.delete();
  }
  await ref.set({ fix1: nowIso() }, { merge: true });
}

/* Once: the 6-month calendar that came in as planned posts isn't what the owners are doing (they changed dates and
   ideas), so the planned posts nobody touched (no file, not scheduled or posted) go away. The page is now for passing
   videos to each other and seeing what is on Meta; anything with a date is made by them. */
async function fixOnce2() {
  const ref = db().collection("settings").doc("content");
  if (((await ref.get()).data() || {}).fix2) return;
  const q = await col().get();
  for (const d of q.docs) {
    const i = d.data();
    if (i.source === "plan" && !(i.files || []).length && !["scheduled", "posted"].includes(i.status)) await d.ref.delete();
  }
  await ref.set({ fix2: nowIso(), seeded: true }, { merge: true });
}


/* ---------- scheduling from the app: at the time, the server publishes it on Instagram and/or Facebook ----------
   Meta doesn't let apps read what is scheduled in Business Suite, so posts scheduled here are the ones the app knows.
   The file goes as it is, by a signed link to Storage (3 hours). Instagram: a Reel (video) or a photo is created,
   Meta processes it, then it's published; Facebook: a Page video or photo. Every 5 minutes (contentPublish). */
const NEED = { instagram: "instagram_content_publish", facebook: "pages_manage_posts" };
let WAIT_MS = 10000;
function nyToUtc(date, time) {
  const [y, m, d] = date.split("-").map(Number), [hh, mi] = time.split(":").map(Number);
  const guess = Date.UTC(y, m - 1, d, hh, mi), p = nyParts(guess);
  const [py, pm, pd] = p.date.split("-").map(Number), [ph, pmi] = p.time.split(":").map(Number);
  return guess + (guess - Date.UTC(py, pm - 1, pd, ph, pmi));
}
const ptWhen = (date, time) => `${date.slice(8, 10)}/${date.slice(5, 7)} às ${time.replace(":00", "h").replace(":", "h")}`;
async function metaAuth() { return (((await db().collection("ads").doc("auth").get()).data()) || {}).meta || null; }
async function missingScopes(meta, nets) {
  const G = require("./ads")._internal.graph;
  const d = await G(meta, "GET", "debug_token", { input_token: meta.token });
  const have = (d.data && d.data.scopes) || [];
  return Object.keys(NEED).filter((n) => nets[n] && !have.includes(NEED[n])).map((n) => NEED[n]);
}
async function fileLink(path) {
  const [url] = await deps.bucket().file(path).getSignedUrl({ version: "v4", action: "read", expires: Date.now() + 3 * 3600000 });
  return url;
}

async function publishOne(doc, it) {
  const G = require("./ads")._internal.graph;
  const meta = await metaAuth();
  const sc = { ...it.sched }, done = { ...(sc.done || {}) }, patch = {};
  const isVideo = /^video\//.test(sc.type || "");
  try {
    if (!meta || !meta.token) throw new Error("O Meta não está conectado (Anúncios › Conectar Meta).");
    const url = await fileLink(sc.path);
    if (sc.nets.instagram && !done.instagram) {
      if (!meta.igUserId) throw new Error("A conta do Instagram não está ligada à conexão do Meta.");
      if (!sc.igCreation) {
        const r = await G(meta, "POST", `${meta.igUserId}/media`, isVideo ? { media_type: "REELS", video_url: url, caption: it.caption || "", share_to_feed: true } : { image_url: url, caption: it.caption || "" });
        sc.igCreation = String(r.id);
      }
      let status = "";
      for (let k = 0; k < 9; k++) {                    // a Reel takes a minute or two to be processed by Meta
        const s = await G(meta, "GET", sc.igCreation, { fields: "status_code,status" });
        status = s.status_code || "";
        if (status === "FINISHED" || status === "ERROR" || status === "EXPIRED" || !isVideo) break;
        await new Promise((r) => setTimeout(r, WAIT_MS));
      }
      if (status === "ERROR" || status === "EXPIRED") { sc.igCreation = ""; throw new Error("O Instagram não aceitou o arquivo (formato ou tamanho)."); }
      if (status === "FINISHED" || !isVideo) {
        const pbl = await G(meta, "POST", `${meta.igUserId}/media_publish`, { creation_id: sc.igCreation });
        done.instagram = nowIso(); patch.igId = String(pbl.id);
        try { const pm = await G(meta, "GET", String(pbl.id), { fields: "permalink" }); patch.igLink = pm.permalink || ""; } catch (e) { /* link comes with the next sync */ }
      }
    }
    if (sc.nets.facebook && !done.facebook) {
      const pg = await G(meta, "GET", meta.pageId, { fields: "access_token" });
      const page = { token: pg.access_token, appSecret: meta.appSecret };
      if (isVideo) {
        const r = await G(page, "POST", `${meta.pageId}/videos`, { file_url: url, description: it.caption || "", title: it.title || "" }, "graph-video.facebook.com");
        patch.fbVideoId = String(r.id);
      } else {
        const r = await G(page, "POST", `${meta.pageId}/photos`, { url, caption: it.caption || "" });
        patch.fbPostId = String(r.post_id || r.id);
      }
      done.facebook = nowIso();
    }
    sc.done = done;
    const all = ["instagram", "facebook"].filter((n) => sc.nets[n]).every((n) => done[n]);
    sc.state = all ? "done" : "processing"; sc.err = "";
    const posted = { ...(it.posted || {}) };
    Object.keys(done).forEach((n) => { posted[n] = posted[n] || done[n]; });
    await doc.ref.set({ ...patch, sched: sc, posted, ...(all ? { status: "posted" } : {}), updatedAt: nowIso() }, { merge: true });
    if (all) {
      const nets = ["instagram", "facebook"].filter((n) => sc.nets[n]).map((n) => (n === "instagram" ? "Instagram" : "Facebook")).join(" e ");
      try { await require("./push").notifyAdmins("admin_content", { text: `Saiu no ${nets} ✓ ${it.title || ""}`, tag: `content-${doc.id}` }); } catch (e) { /* never blocks */ }
    }
    return all ? "done" : "processing";
  } catch (e) {
    sc.state = "error"; sc.err = String(e.message || e).replace(/^Meta: /, "").slice(0, 300); sc.done = done;
    const posted = { ...(it.posted || {}) };
    Object.keys(done).forEach((n) => { posted[n] = posted[n] || done[n]; });
    await doc.ref.set({ ...patch, sched: sc, posted, updatedAt: nowIso() }, { merge: true });
    try { await require("./push").notifyAdmins("admin_content", { text: `Não deu para publicar “${it.title || ""}”: ${sc.err}`, tag: `content-${doc.id}` }); } catch (x) { /* never blocks */ }
    return "error";
  }
}

/** contentPublish (every 5 minutes): what is due goes out. */
async function publishDue(now = Date.now()) {
  const q = await col().get();
  const out = { done: 0, processing: 0, error: 0 };
  for (const d of q.docs) {
    const it = d.data(), sc = it.sched;
    if (!sc || !["waiting", "processing"].includes(sc.state) || Date.parse(sc.at) > now) continue;
    out[await publishOne(d, it)] += 1;
  }
  return out;
}

async function list(opts) {
  await fixOnce();
  await fixOnce2();
  let sync = null;
  try { sync = await syncMeta(opts || {}); } catch (e) { sync = { at: nowIso(), errors: { meta: e.message } }; }
  const q = await col().get();
  const items = q.docs.map((d) => ({ id: d.id, ...d.data() }));
  items.sort((a, b) => (a.date || "9999").localeCompare(b.date || "9999") || String(a.time).localeCompare(String(b.time)) || String(a.at).localeCompare(String(b.at)));
  return { items, today: today(), sync };
}

/** The first name of who did it: "Thiago", "Karina". */
const name = (auth) => {
  const e = String((auth && auth.token && auth.token.email) || "");
  const n = String((auth && auth.token && auth.token.name) || e.split("@")[0].replace(/[._\d-]+/g, " ") || "Alguém").trim().split(/\s+/)[0];
  return n.charAt(0).toUpperCase() + n.slice(1).toLowerCase();
};
async function tellOther(auth, text, tag) {
  try { await require("./push").notifyAdmins("admin_content", { text, tag }, { exceptUid: auth && auth.uid }); } catch (e) { /* never blocks */ }
}

/** adminContent({action: "list" | "save" | "addFile" | "removeFile" | "remove" | "posted", ...}) */
async function adminContent(data, auth) {
  U.requireAdmin(auth);
  data = data || {};
  const id = data.id ? U.text(data.id, 40) : "";
  const ref = id ? col().doc(id) : null;
  const read = async () => { const s = await ref.get(); if (!s.exists) fail("not-found", "This post was deleted."); return s.data(); };
  switch (data.action) {
    case "list":
    case undefined:
      return list();
    case "sync":
      await U.rateLimit("contentSync", auth.uid, 20, 3600);
      return list({ force: true });
    case "save": {
      if (ref) {
        const cur = await read();
        const next = cleanItem(data.item, cur);
        await ref.set({ ...next, updatedAt: nowIso(), updatedBy: U.who(auth) }, { merge: true });
        if (next.status === "ready" && cur.status !== "ready") await tellOther(auth, `${name(auth)} marcou como pronto: ${next.title || "um post"}`, `content-${id}`);
        return { ...(await list()), id };
      }
      const item = cleanItem(data.item);
      if (!item.title && item.kind === "idea") fail("invalid-argument", "Write the idea.");
      if (!item.title) item.title = item.kind === "photo" ? "Foto nova" : "Vídeo novo";
      const r = await col().add({ ...item, files: [], posted: {}, source: "app", by: U.who(auth), byName: name(auth), at: nowIso(), updatedAt: nowIso() });
      // a written idea tells the other one too (a video idea tells when its file arrives)
      if (item.status === "idea" && !data.withFile) await tellOther(auth, `${name(auth)} anotou uma ideia: ${item.title}`, `content-${r.id}`);
      return { ...(await list()), id: r.id };
    }
    case "addFile": {
      // the app already uploaded the original to Storage; this records it on the post
      const cur = await read();
      const path = U.text(data.path, 220);
      if (!PATH_RE.test(path) || !path.startsWith(`${COL}/${id}/`)) fail("invalid-argument", "That file isn't in this post's folder.");
      let meta = null;
      try { const f = deps.bucket().file(path); if ((await f.exists())[0]) [meta] = await f.getMetadata(); } catch (e) { meta = null; }
      if (!meta) fail("not-found", "The upload didn't finish. Try again.");
      const type = String(meta.contentType || data.type || "");
      if (!/^(image|video)\//.test(type)) fail("invalid-argument", "Only photos and videos.");
      const files = (cur.files || []).filter((f) => f.path !== path);
      files.push({ path, name: U.text(data.name, 140) || path.split("/").pop(), type, size: Number(meta.size) || Number(data.size) || 0,
        w: Number(data.w) || 0, h: Number(data.h) || 0, dur: Number(data.dur) || 0, at: nowIso(), by: U.who(auth), byName: name(auth) });
      const upd = { files, updatedAt: nowIso(), lastFileAt: nowIso() };
      if (cur.status === "todo") upd.status = "ready";      // an idea stays an idea, with its video
      await ref.set(upd, { merge: true });
      const kind = /^video\//.test(type) ? "um vídeo novo" : "uma foto nova";
      const where = cur.status === "idea" ? " nas Ideias" : "";
      // a file sent only to be scheduled doesn't tell twice (the schedule tells)
      if (!data.quiet) await tellOther(auth, `${name(auth)} mandou ${kind}${where}: ${cur.title || "sem nome"}. Toque para ver.`, `content-${id}`);
      return list();
    }
    case "removeFile": {
      const cur = await read();
      const path = U.text(data.path, 220);
      if (!(cur.files || []).some((f) => f.path === path)) fail("not-found", "That file isn't here anymore.");
      try { await deps.bucket().file(path).delete(); } catch (e) { /* already gone */ }
      await ref.set({ files: (cur.files || []).filter((f) => f.path !== path), updatedAt: nowIso() }, { merge: true });
      return list();
    }
    case "remove": {
      const cur = await read();
      for (const f of cur.files || []) { try { await deps.bucket().file(f.path).delete(); } catch (e) { /* already gone */ } }
      await ref.delete();
      return list();
    }
    case "schedule": {
      // the app publishes it at that day and time (New York time)
      const cur = await read();
      const date = /^\d{4}-\d{2}-\d{2}$/.test(String(data.date || "")) ? String(data.date) : "";
      const time = /^\d{2}:\d{2}$/.test(String(data.time || "")) ? String(data.time) : "";
      if (!date || !time) fail("invalid-argument", "Pick the day and the time.");
      const at = nyToUtc(date, time);
      if (at < Date.now() + 60000) fail("invalid-argument", "Pick a time in the future.");
      const nets = { instagram: !!(data.nets && data.nets.instagram), facebook: !!(data.nets && data.nets.facebook) };
      if (!nets.instagram && !nets.facebook) fail("invalid-argument", "Choose Instagram, Facebook or both.");
      const file = (cur.files || []).find((f) => f.path === data.path) || (cur.files || [])[0];
      if (!file) fail("failed-precondition", "Send the video or photo first.");
      const meta = await metaAuth();
      if (!meta || !meta.token) fail("failed-precondition", "Connect Meta first (Ads › Connect Meta).");
      const missing = await missingScopes(meta, nets);
      if (missing.length) fail("failed-precondition", `The Meta connection can't publish yet (missing ${missing.join(", ")}). Make a new token in Meta Business with those permissions and paste it in Ads › Connect Meta.`);
      const caption = data.caption !== undefined ? U.text(data.caption, 2200) : cur.caption || "";
      await ref.set({ status: "scheduled", date, time, caption, nets: { ...(cur.nets || {}), ...nets },
        sched: { at: new Date(at).toISOString(), nets, path: file.path, type: file.type, state: "waiting", err: "", done: {}, igCreation: "", by: name(auth) },
        updatedAt: nowIso() }, { merge: true });
      await tellOther(auth, `${name(auth)} agendou pelo app: ${cur.title || "um post"} · sai ${ptWhen(date, time)}`, `content-${id}`);
      return list();
    }
    case "unschedule": {
      const cur = await read();
      if (cur.sched && cur.sched.state === "done") fail("failed-precondition", "It already went out.");
      await ref.update({ sched: null, status: (cur.files || []).length ? "ready" : "idea", updatedAt: nowIso() });
      return list();
    }
    case "retry": {
      const cur = await read();
      if (!cur.sched || cur.sched.state !== "error") fail("failed-precondition", "Nothing to retry.");
      await ref.set({ sched: { ...cur.sched, state: "waiting", err: "", at: new Date(Math.max(Date.parse(cur.sched.at), Date.now())).toISOString() }, updatedAt: nowIso() }, { merge: true });
      await publishOne(await ref.get(), (await ref.get()).data());
      return list();
    }
    case "posted": {
      // which networks got it; when every chosen network has it, the post is done
      const cur = await read();
      const posted = { ...(cur.posted || {}) };
      NETS.forEach((n) => {
        if (!data.nets || data.nets[n] === undefined) return;
        if (data.nets[n]) posted[n] = posted[n] || nowIso(); else delete posted[n];
      });
      const chosen = NETS.filter((n) => cur.nets && cur.nets[n]);
      // out on any network = posted (the card still shows which networks are missing)
      const done = chosen.some((n) => posted[n]) || Object.keys(posted).length > 0;
      const status = done ? "posted" : cur.status === "posted" ? ((cur.files || []).length ? "ready" : "todo") : cur.status;
      await ref.update({ posted, status, updatedAt: nowIso() });   // update: the whole map, so an unticked network goes away
      return list();
    }
    default:
      fail("invalid-argument", "Unknown action.");
  }
}

module.exports = { adminContent, cleanItem, seed, syncMeta, publishDue, PATH_RE, _today: today, _nyParts: nyParts, _nyToUtc: nyToUtc,
  _setWait: (ms) => { WAIT_MS = ms; } };
