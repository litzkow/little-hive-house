"use strict";
/* Instagram and Facebook, looked after by the server (socialSync, every 10 minutes). Uses the Meta connection in
   ads/auth.meta (the system-user token the owners pasted in Hive Admin › Anúncios).

   1. Products tagged on every Instagram post (socialTags/{mediaId}):
      - a post from the app's planner (content item) uses the products listed on it (item.products: [{rid, x, y, child}]);
      - any other post (made in the Instagram app or Meta Business Suite): products picked from its caption (design
        names, a collection's name, or photo magnets);
      - a product Meta has not approved yet for the Instagram shop is tagged on a later run, when it is; after 30 days of
        waiting the owners get one notice. A post that already has tags, or that shows no product, is left alone.
   2. Comments (Instagram and the Facebook Page) and Instagram Direct messages (social/{key}):
      - each new one is saved for the inbox in Hive Admin (Mensagens › Instagram & Facebook) and pushed to the phones;
      - simple ones get an automatic, friendly answer (thanks, prices, how to order, photo magnets, shipping), in English
        or Portuguese like the customer wrote; everything else waits for the owners, who answer from the app
        (adminSocial reply). answering by itself happens only when settings/social {autoReply:true}; the owners asked it OFF (20 Nov 2026), so it stays off.
   Never throws out of socialSync: one failing part is logged and the rest goes on. */

const { nowIso } = require("./config");
const deps = require("./deps");
const U = require("./util");
const { fail } = require("./config");

const DAY = 86400000;
const TAG_DAYS = 30;              // posts this recent get their products tagged
const COMMENT_DAYS = 30;          // comments are read on posts this recent
const MAX_TAGS = 5;               // Instagram: at most 5 products on one photo or video
const SPOTS = [[0.3, 0.3], [0.7, 0.3], [0.3, 0.68], [0.7, 0.68], [0.5, 0.5]];   // where the tags sit when nobody chose

const db = () => deps.db();
const G = (...a) => require("./ads")._internal.graph(...a);
async function metaAuth() { return (((await db().collection("ads").doc("auth").get()).data()) || {}).meta || null; }

/* ---------------------------------------------------------------- the catalog, as Meta knows it (google-products.xml) */
let CAT = null;
function catalog() {
  if (CAT) return CAT;
  const c = require("./catalog.json");
  const designs = Object.entries(c.designs || {}).map(([k, d]) => ({ rid: k.replace("/", "-"), title: d.title, collection: d.collection, collectionName: d.collectionName }));
  const packs = Object.keys(c.packs || {}).map((n) => ({ rid: `photo-pack-${n}`, size: Number(n), price: c.packs[n].price }));
  CAT = { designs, packs, rules: c.rules || {} };
  return CAT;
}
const plain = (s) => String(s || "").toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/[’']/g, "'");

/** The products a caption talks about: design names first, then a collection's first designs, then photo magnets. */
function productsFromCaption(caption) {
  const t = plain(caption);
  if (!t.trim()) return [];
  const { designs, packs } = catalog();
  const out = [];
  const add = (rid) => { if (!out.includes(rid) && out.length < MAX_TAGS * 4) out.push(rid); };
  // a design named in the caption ("Pumpkin Spice", "Merry & Bright"): longest names first, whole words only
  const seen = new Set();
  const esc = (x) => x.replace(/[.*+?^${}()|[\]\\]/g, "\\$&").replace(/&/g, "(&|and)");
  const said = (x) => new RegExp(`(^|[^a-z])${esc(x)}([^a-z]|$)`).test(t);
  [...designs].filter((d) => plain(d.title).length >= 6).sort((a, b) => b.title.length - a.title.length).forEach((d) => {
    const full = plain(d.title), head = full.split(/\s+(?:&|and)\s+|,\s*/)[0].trim();   // "Pumpkin Spice & Everything Nice" -> "pumpkin spice"
    if (seen.has(full)) return;
    if (said(full) || (head !== full && head.length >= 10 && head.includes(" ") && said(head))) { seen.add(full); add(d.rid); }
  });
  // a collection ("our Christmas collection", "the fall collection", "Bee Kind"): its first designs
  const cols = [];
  designs.forEach((d) => { if (!cols.find((c) => c.id === d.collection)) cols.push({ id: d.collection, name: d.collectionName }); });
  cols.forEach((c) => {
    const n = plain(c.name), short = n.split(/\s+/)[0];
    const hit = t.includes(`${n} collection`) || t.includes(`${short} collection`) || (n.length > 5 && t.includes(n) && /collection|designs|magnets/.test(t));
    if (hit) designs.filter((d) => d.collection === c.id).slice(0, MAX_TAGS).forEach((d) => add(d.rid));
  });
  // their own photos
  if (/\b(your (own )?(photos?|pictures?|pics)|photo magnets?|custom magnets?|personali[sz]ed|upload your|camera roll)\b/.test(t)) {
    const two = packs.filter((p) => p.size === 4 || p.size === 9).map((p) => p.rid);
    // the photo packs keep a place among the first 5 (one photo or video takes 5 tags)
    const rest = out.filter((r) => !two.includes(r));
    return rest.slice(0, MAX_TAGS - two.length).concat(two, rest.slice(MAX_TAGS - two.length));
  }
  return out;
}

/** Where the tags go: one photo or video gets up to 5; an album spreads them over its photos (5 each). */
function planFor(media, rids, chosen) {
  const kids = ((media.children && media.children.data) || []).filter((c) => c.media_type === "IMAGE");
  const isVideo = media.media_type === "VIDEO";
  if (chosen && chosen.length) {   // the planner's own choice, with places
    const by = {};
    chosen.forEach((p, i) => {
      const target = p.child || (media.media_type === "CAROUSEL_ALBUM" ? (kids[0] || {}).id : media.id);
      if (!target) return;
      (by[target] = by[target] || []).push({ rid: p.rid, ...(isVideo ? {} : { x: num01(p.x, SPOTS[i % 5][0]), y: num01(p.y, SPOTS[i % 5][1]) }) });
    });
    return Object.entries(by).map(([target, tags]) => ({ target, tags: tags.slice(0, MAX_TAGS) }));
  }
  if (!rids.length) return [];
  if (media.media_type === "CAROUSEL_ALBUM") {
    if (!kids.length) return [];
    const plan = [];
    for (let i = 0; i < kids.length && i * MAX_TAGS < rids.length; i++) {
      plan.push({ target: kids[i].id, tags: rids.slice(i * MAX_TAGS, (i + 1) * MAX_TAGS).map((rid, k) => ({ rid, x: SPOTS[k][0], y: SPOTS[k][1] })) });
    }
    return plan;
  }
  return [{ target: media.id, tags: rids.slice(0, MAX_TAGS).map((rid, k) => (isVideo ? { rid } : { rid, x: SPOTS[k][0], y: SPOTS[k][1] })) }];
}
function num01(v, d) { const n = Number(v); return Number.isFinite(n) && n >= 0 && n <= 1 ? n : d; }

/* ---------------------------------------------------------------- 1. tagging */
async function syncTags(meta, media, items) {
  const col = db().collection("socialTags");
  const sum = { planned: 0, tagged: 0, waiting: 0 };
  const since = Date.now() - TAG_DAYS * DAY;
  // new posts: a plan each (or "none")
  for (const m of media) {
    if (Date.parse(m.timestamp || 0) < since) continue;
    const ref = col.doc(String(m.id));
    if ((await ref.get()).exists) continue;
    let existing = [];
    try { existing = ((await G(meta, "GET", `${m.id}/product_tags`)).data) || []; } catch (e) { existing = []; }
    const item = items.find((i) => i.igId === String(m.id));
    const chosen = item && Array.isArray(item.products) ? item.products.filter((p) => p && /^[a-z0-9-]{3,80}$/.test(String(p.rid || ""))) : null;
    const rids = chosen && chosen.length ? [] : productsFromCaption(m.caption);
    const plan = existing.length ? [] : planFor(m, rids, chosen);
    await ref.set({
      mediaId: String(m.id), type: m.media_type, link: m.permalink || "", postedAt: m.timestamp || null, caption: String(m.caption || "").slice(0, 160),
      source: existing.length ? "already" : chosen && chosen.length ? "planner" : "caption", plan, done: [],
      status: existing.length ? "done" : plan.length ? "pending" : "none", createdAt: nowIso(),
    });
    if (plan.length && !existing.length) sum.planned++;
  }
  // what is waiting: tag what Meta has approved
  const waiting = await col.where("status", "==", "pending").get();
  if (waiting.empty) return sum;
  const cat = await catalogId(meta);
  const status = {};
  for (const d of waiting.docs) {
    const t = d.data();
    const done = new Set(t.done || []);
    let left = 0, err = "";
    for (const step of t.plan || []) {
      const want = step.tags.filter((g) => !done.has(`${step.target}:${g.rid}`));
      if (!want.length) continue;
      const ok = [];
      for (const g of want) {
        if (!status[g.rid]) status[g.rid] = await productStatus(meta, cat, g.rid);
        if (status[g.rid].approved) ok.push(g); else left++;
      }
      if (!ok.length) continue;
      // Instagram keeps the tags already there and adds these (updated_tags)
      const tags = ok.map((g) => ({ product_id: status[g.rid].id, ...(g.x !== undefined ? { x: g.x, y: g.y } : {}) }));
      try {
        await G(meta, "POST", `${step.target}/product_tags`, { updated_tags: tags });
        ok.forEach((g) => done.add(`${step.target}:${g.rid}`));
        sum.tagged += ok.length;
      } catch (e) { err = e.message; left += ok.length; }
    }
    const old = Date.now() - Date.parse(t.postedAt || t.createdAt) > TAG_DAYS * DAY;
    const patch = { done: [...done], lastTry: nowIso(), error: err || null };
    if (!left) patch.status = "done";
    else if (old) {
      patch.status = "stopped";
      await notify(`Não deu para marcar ${left} produto(s) num post do Instagram: a Meta ainda não aprovou. Veja em Mensagens.`, `tags-${t.mediaId}`);
    } else sum.waiting++;
    await d.ref.update(patch);
  }
  return sum;
}
async function catalogId(meta) {
  const j = await G(meta, "GET", `${meta.igUserId}/available_catalogs`, { fields: "catalog_id" });
  const id = ((j.data || [])[0] || {}).catalog_id;
  if (!id) throw new Error("no catalog on the Instagram account");
  return id;
}
/** A product's id in Meta and whether the Instagram shop approved it (capability MINI_SHOPS). */
async function productStatus(meta, cat, rid) {
  try {
    const j = await G(meta, "GET", `${cat}/products`, { filter: { retailer_id: { eq: rid } }, fields: "id,capability_to_review_status,visibility" });
    const p = (j.data || [])[0];
    if (!p) return { id: null, approved: false };
    const cap = (p.capability_to_review_status || []).find((c) => c.key === "MINI_SHOPS");
    return { id: p.id, approved: !cap || cap.value === "APPROVED" };
  } catch (e) { return { id: null, approved: false }; }
}

/* ---------------------------------------------------------------- 2. comments and Direct messages */
/** What kind of comment it is, for the automatic answer: thanks | price | order | photo | shipping | pick | null. */
function intentOf(text) {
  const t = plain(text).trim();
  if (!t) return null;
  if (/^[12](\s|[!.]|$)/.test(t) && t.length <= 6) return "pick";
  if (/(how much|price|cost|\$\s*\?|quanto (custa|e|sai)|preco|valor)/.test(t)) return "price";
  if (/(ship|shipping|deliver|envia|entrega|frete|canada|outside the us)/.test(t)) return "shipping";
  if (/(my (own )?(photo|picture|pic)s?|custom|personali|minha foto|minhas fotos|foto)/.test(t)) return "photo";
  if (/((where|how) (can|do) (i|we) (buy|get|order)|where to (buy|order)|do you sell|can i (buy|order)|link\?|website\?|onde (compro|compra|vende)|como (compro|compra|faco para comprar|peco)|quero (comprar|um|uma))/.test(t)) return "order";
  const short = t.replace(/[^\p{L}\p{N}\s]/gu, "").trim();
  const loving = /(love|lindo|linda|lindos|amei|amo|beautiful|cute|gorgeous|adorable|perfect|perfeito|amazing|so good|incredible|maravilh|fofo|fofa|wow|congrat|parabens|sucesso|great|nice|awesome|❤|💛|🧡|😍|🥰|🔥|👏|🙌)/u.test(t) || /(❤|💛|🧡|😍|🥰|🔥|👏|🙌|🐝)/u.test(text);
  if (loving && !/\?/.test(t) && short.split(/\s+/).length <= 14) return "thanks";
  if (!short && /\p{Extended_Pictographic}/u.test(text)) return "thanks";
  return null;
}
const isPt = (text) => /\b(voce|vc|que|lindo|linda|amei|quanto|onde|como|obrigad|parabens|muito|minha|meu|quero|foto|frete|tem)\b/.test(plain(text));

/** The automatic answer for a comment or message, or "" when it should wait for the owners. */
function autoReply(text, { name = "", dm = false } = {}) {
  const kind = intentOf(text);
  if (!kind) return "";
  const r = catalog().rules, pack4 = (catalog().packs.find((p) => p.size === 4) || {}).price;
  const pt = isPt(text);
  const hi = name && !dm ? `@${name} ` : "";
  const each = r.designPrice || 5, b = r.bundle || {}, free = r.freeShippingAt || 35;
  const A = {
    thanks: pt ? ["Obrigada! 💛🐝", "Que bom que você gostou! 🐝💛", "Muito obrigada pelo carinho! 💛"] : ["Thank you so much! 💛🐝", "That made our day, thank you! 🐝", "Aww, thank you! 💛"],
    pick: pt ? ["Ótima escolha! 💛"] : ["Great pick! 💛", "Good choice! 🐝"],
    price: pt
      ? [`Oi! Nossos ímãs custam $${each} cada (${b.size || 3} por $${b.price || 12}), e os de foto começam em 4 por $${pack4 || 14}. Frete grátis nos EUA acima de $${free}. Tudo no littlehivehouse.com 🐝`]
      : [`Hi! Our designs are $${each} each (any ${b.size || 3} for $${b.price || 12}), and photo magnets start at 4 for $${pack4 || 14}. Free US shipping over $${free}. Everything is at littlehivehouse.com 🐝`],
    order: pt ? ["Você pode comprar no littlehivehouse.com (link na bio) 🐝 Enviamos para todos os EUA."] : ["You can order at littlehivehouse.com (link in our bio) 🐝 We ship anywhere in the US."],
    photo: pt
      ? [`Sim! Você manda suas fotos no littlehivehouse.com/photo-magnets e a gente faz os ímãs à mão. A partir de 4 por $${pack4 || 14} 🐝`]
      : [`Yes! Upload your photos at littlehivehouse.com/photo-magnets and we make them into magnets by hand. From 4 for $${pack4 || 14} 🐝`],
    shipping: pt
      ? [`Enviamos para todos os EUA, grátis acima de $${free}, e saem em 1 a 2 dias úteis 🐝`]
      : [`We ship anywhere in the US, free over $${free}, and orders go out in 1 to 2 business days 🐝`],
  }[kind];
  const pick = A[Math.abs(hash(text)) % A.length];
  return (dm || kind === "thanks" || kind === "pick" ? "" : hi) + pick;
}
function hash(s) { let h = 0; for (const c of String(s)) h = (h * 31 + c.codePointAt(0)) | 0; return h; }

async function settings() { return ((await db().collection("settings").doc("social").get()).data()) || {}; }

/** Saves one new comment or message; answers it when it is simple; tells the phones. */
async function arrive(doc, meta, opts) {
  const col = db().collection("social");
  const ref = col.doc(doc.key);
  if ((await ref.get()).exists) return false;
  const row = { ...doc, status: doc.answered ? "answered" : "new", createdAt: nowIso() };
  delete row.key; delete row.answered;
  let replied = "";
  if (!doc.answered && opts.auto && Date.now() - Date.parse(doc.at || 0) < 3 * DAY) {
    const text = autoReply(doc.text, { name: doc.user, dm: doc.kind === "dm" });
    if (text) {
      try {
        await send(meta, opts, { ...doc, ...row }, text);
        row.status = "auto"; row.reply = { text, at: nowIso(), by: "auto" }; replied = text;
      } catch (e) { row.autoError = e.message.slice(0, 200); }
    }
  }
  await ref.set(row);
  const where = doc.net === "facebook" ? "Facebook" : doc.kind === "dm" ? "Direct" : "Instagram";
  await notify(`${replied ? "✓ Respondido sozinho · " : ""}${where} · ${doc.user || "alguém"}: ${String(doc.text || "").slice(0, 110)}`, `social-${doc.key}`, { title: doc.kind === "dm" ? "✉️ Mensagem no Direct" : `💬 Comentário no ${where}` });
  return true;
}

/** Sends an answer: a public reply under the comment, or a Direct message. */
async function send(meta, opts, item, text) {
  if (item.kind === "dm") {
    const page = opts.page || (opts.page = await pageAuth(meta));
    return G(page, "POST", `${meta.pageId}/messages`, { recipient: { id: item.userId }, message: { text }, messaging_type: "RESPONSE" });
  }
  if (item.net === "facebook") {
    const page = opts.page || (opts.page = await pageAuth(meta));
    return G(page, "POST", `${item.id}/comments`, { message: text });
  }
  return G(meta, "POST", `${item.id}/replies`, { message: text });
}
async function pageAuth(meta) {
  const p = await G(meta, "GET", meta.pageId, { fields: "access_token" });
  if (!p.access_token) throw new Error("no Page token");
  return { token: p.access_token, appSecret: meta.appSecret };
}

async function syncComments(meta, media, opts) {
  const sum = { new: 0 };
  const since = Date.now() - COMMENT_DAYS * DAY;
  const me = String(meta.igUsername || "").toLowerCase();
  // Instagram comments
  for (const m of media) {
    if (Date.parse(m.timestamp || 0) < since) continue;
    let list = [];
    try { list = ((await G(meta, "GET", `${m.id}/comments`, { fields: "id,text,username,timestamp,from{id,username},replies{id,username,text,timestamp}", limit: 50 })).data) || []; } catch (e) { continue; }
    for (const c of list) {
      if (String(c.username || "").toLowerCase() === me) continue;
      const answered = ((c.replies && c.replies.data) || []).some((r) => String(r.username || "").toLowerCase() === me);
      if (await arrive({ key: `ig-c-${c.id}`, net: "instagram", kind: "comment", id: String(c.id), postId: String(m.id), link: m.permalink || "",
        user: c.username || "", userId: (c.from && c.from.id) || "", text: String(c.text || "").slice(0, 2000), at: c.timestamp || nowIso(), answered }, meta, opts)) sum.new++;
    }
  }
  // Facebook Page comments
  try {
    const page = opts.page || (opts.page = await pageAuth(meta));
    const posts = ((await G(page, "GET", `${meta.pageId}/published_posts`, { fields: "id,permalink_url,created_time,comments.limit(50){id,message,from,created_time,comments.limit(10){from}}", limit: 15 })).data) || [];
    for (const p of posts) {
      if (Date.parse(p.created_time || 0) < since) continue;
      for (const c of ((p.comments && p.comments.data) || [])) {
        if (c.from && String(c.from.id) === String(meta.pageId)) continue;
        const answered = ((c.comments && c.comments.data) || []).some((r) => r.from && String(r.from.id) === String(meta.pageId));
        if (await arrive({ key: `fb-c-${c.id}`, net: "facebook", kind: "comment", id: String(c.id), postId: String(p.id), link: p.permalink_url || "",
          user: (c.from && c.from.name) || "", userId: (c.from && c.from.id) || "", text: String(c.message || "").slice(0, 2000), at: c.created_time || nowIso(), answered }, meta, opts)) sum.new++;
      }
    }
  } catch (e) { sum.facebookError = e.message.slice(0, 200); }
  // Instagram Direct
  try {
    const page = opts.page || (opts.page = await pageAuth(meta));
    const convs = ((await G(page, "GET", `${meta.pageId}/conversations`, { platform: "instagram", fields: "id,updated_time,messages.limit(10){id,message,from,created_time}", limit: 20 })).data) || [];
    for (const cv of convs) {
      const msgs = ((cv.messages && cv.messages.data) || []).slice().reverse();   // oldest first
      msgs.forEach((x, i) => { x.later = msgs.slice(i + 1); });
      for (const x of msgs) {
        const fromMe = x.from && (String(x.from.id) === String(meta.igUserId) || String(x.from.username || "").toLowerCase() === me);
        if (fromMe || !x.message || Date.parse(x.created_time || 0) < since) continue;
        const answered = x.later.some((y) => y.from && (String(y.from.id) === String(meta.igUserId) || String(y.from.username || "").toLowerCase() === me));
        if (await arrive({ key: `ig-dm-${x.id}`, net: "instagram", kind: "dm", id: String(x.id), thread: String(cv.id), link: "",
          user: (x.from && (x.from.username || x.from.name)) || "", userId: (x.from && x.from.id) || "", text: String(x.message).slice(0, 2000), at: x.created_time || nowIso(), answered }, meta, opts)) sum.new++;
      }
    }
  } catch (e) { sum.directError = e.message.slice(0, 200); }
  return sum;
}

async function notify(body, tag, { title = "📣 Instagram & Facebook" } = {}) {
  try { await require("./push").notifyAdmins("admin_social", { title, body, tag }); } catch (e) { /* never blocks */ }
}

/* ---------------------------------------------------------------- the scheduled run and the app's actions */
async function socialSync() {
  const meta = await metaAuth();
  if (!meta || !meta.token || !meta.igUserId) return { connected: false };
  const out = {};
  let media = [];
  try {
    media = ((await G(meta, "GET", `${meta.igUserId}/media`, { fields: "id,media_type,media_product_type,caption,timestamp,permalink,children{id,media_type}", limit: 30 })).data) || [];
  } catch (e) { out.mediaError = e.message; }
  let items = [];
  try { items = (await db().collection("content").get()).docs.map((d) => d.data()).filter((i) => i.igId); } catch (e) { items = []; }
  const s = await settings();
  try { out.tags = await syncTags(meta, media, items); } catch (e) { out.tagsError = e.message; console.warn("[social] tags", e.message); }
  try { out.comments = await syncComments(meta, media, { auto: s.autoReply === true }); } catch (e) { out.commentsError = e.message; console.warn("[social] comments", e.message); }
  await db().collection("settings").doc("social").set({ lastRun: { at: nowIso(), ...out } }, { merge: true });
  console.log("[socialSync]", JSON.stringify(out));
  return out;
}

/** Hive Admin: answer, mark done, hide a comment, turn the automatic answers on or off. */
async function adminSocial(data, auth) {
  U.requireAdmin(auth);
  const action = String((data && data.action) || "");
  if (action === "auto") {
    await db().collection("settings").doc("social").set({ autoReply: !!data.on }, { merge: true });
    return { ok: true, autoReply: !!data.on };
  }
  if (action === "run") return socialSync();
  const id = U.text(data && data.id, 120, { required: true, field: "the message" });
  const ref = db().collection("social").doc(id);
  const snap = await ref.get();
  if (!snap.exists) fail("not-found", "That comment isn't here anymore.");
  const item = { key: id, ...snap.data() };
  const meta = await metaAuth();
  if (action === "reply") {
    const text = U.text(data.text, 1000, { required: true, field: "the answer" });
    try { await send(meta, {}, item, text); } catch (e) { fail("failed-precondition", `Meta didn't take the answer: ${e.message.replace(/^Meta: /, "")}`); }
    await ref.update({ status: "answered", reply: { text, at: nowIso(), by: U.who(auth) } });
    return { ok: true };
  }
  if (action === "hide") {
    if (item.kind === "dm") fail("invalid-argument", "Messages can't be hidden.");
    try {
      if (item.net === "facebook") await G(await pageAuth(meta), "POST", item.id, { is_hidden: true });
      else await G(meta, "POST", item.id, { hide: true });
    } catch (e) { fail("failed-precondition", `Meta didn't hide it: ${e.message.replace(/^Meta: /, "")}`); }
    await ref.update({ status: "hidden", hiddenAt: nowIso() });
    return { ok: true };
  }
  if (action === "done") { await ref.update({ status: "done", doneAt: nowIso() }); return { ok: true }; }
  fail("invalid-argument", "Unknown action.");
}

module.exports = { socialSync, adminSocial, productsFromCaption, planFor, intentOf, autoReply, _reset: () => { CAT = null; } };
