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
      title: p.title, kind: p.kind === "video" ? "video" : "photo", status: p.kind === "video" ? "todo" : "ready", date: p.date, time: p.time,
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
  const match = (key, id, caption, date) => items.find((i) => i[key] === id)
    || (same(caption, "") && items.find((i) => !i[key] && i.date && dayDiff(i.date, date) <= 2 && same(i.caption, caption)));
  const add = (it) => { it.id = null; items.push(it); changed.set(it, it); return it; };
  const counts = { instagram: 0, facebook: 0, scheduled: 0 }, errors = {};

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
        touch(it, { igId: String(m.id), igLink: m.permalink || "", preview: preview || it.preview || "", igStats: stats, posted: { ...(it.posted || {}), instagram: it.posted && it.posted.instagram || new Date(at).toISOString() },
          nets: { ...(it.nets || {}), instagram: true }, date: it.date || date, time: it.time || time });
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
          const { date, time } = nyParts(at);
          let it = match("fbPostId", String(m.id), m.message, date);
          if (!it) it = add({ ...cleanItem({ title: firstLine(m.message).slice(0, 80) || "Post do Facebook", kind: "photo", status: "posted", date, time, caption: m.message || "", nets: { facebook: true } }),
            files: [], posted: {}, source: "facebook", by: "Facebook", at: nowIso() });
          touch(it, { fbPostId: String(m.id), fbLink: m.permalink_url || "", preview: it.preview || m.full_picture || "",
            posted: { ...(it.posted || {}), facebook: it.posted && it.posted.facebook || new Date(at).toISOString() }, nets: { ...(it.nets || {}), facebook: true } });
          counts.facebook += 1;
        });
      } catch (e) { errors.facebook = errors.facebook || e.message; }
    }
  }
  for (const it of changed.values()) {
    if (done(it)) it.status = "posted";
    const { id, ...data } = it;
    data.updatedAt = nowIso();
    if (id) await col().doc(id).set(data, { merge: true }); else await col().add(data);
  }
  const out = { at: nowIso(), connected: true, counts, errors, ig: meta.igUsername || "" };
  await sref.set({ sync: out }, { merge: true });
  return out;
}

async function list(opts) {
  await seed();
  let sync = null;
  try { sync = await syncMeta(opts || {}); } catch (e) { sync = { at: nowIso(), errors: { meta: e.message } }; }
  const q = await col().get();
  const items = q.docs.map((d) => ({ id: d.id, ...d.data() }));
  items.sort((a, b) => (a.date || "9999").localeCompare(b.date || "9999") || String(a.time).localeCompare(String(b.time)) || String(a.at).localeCompare(String(b.at)));
  return { items, today: today(), sync };
}

const name = (auth) => {
  const e = String((auth && auth.token && auth.token.email) || "");
  return (auth && auth.token && auth.token.name) || e.split("@")[0] || "Alguém";
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
      if (!item.title) fail("invalid-argument", "Give it a title.");
      const r = await col().add({ ...item, files: [], posted: {}, source: "app", by: U.who(auth), at: nowIso(), updatedAt: nowIso() });
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
        w: Number(data.w) || 0, h: Number(data.h) || 0, dur: Number(data.dur) || 0, at: nowIso(), by: U.who(auth) });
      const upd = { files, updatedAt: nowIso() };
      if (cur.status === "todo" || cur.status === "idea") upd.status = "ready";
      await ref.set(upd, { merge: true });
      const kind = /^video\//.test(type) ? "um vídeo" : "uma foto";
      await tellOther(auth, `${name(auth)} mandou ${kind}: ${cur.title || "post novo"}. Toque para baixar.`, `content-${id}`);
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
    case "posted": {
      // which networks got it; when every chosen network has it, the post is done
      const cur = await read();
      const posted = { ...(cur.posted || {}) };
      NETS.forEach((n) => {
        if (!data.nets || data.nets[n] === undefined) return;
        if (data.nets[n]) posted[n] = posted[n] || nowIso(); else delete posted[n];
      });
      const chosen = NETS.filter((n) => cur.nets && cur.nets[n]);
      const done = chosen.length > 0 && chosen.every((n) => posted[n]);
      const status = done ? "posted" : cur.status === "posted" ? "ready" : cur.status;
      await ref.set({ posted, status, updatedAt: nowIso() }, { merge: true });
      return list();
    }
    default:
      fail("invalid-argument", "Unknown action.");
  }
}

module.exports = { adminContent, cleanItem, seed, syncMeta, PATH_RE, _today: today, _nyParts: nyParts };
