"use strict";
/* Meta: where Business Suite keeps scheduled posts that the API can see (Page posts, videos, Reels). Prints counts and
   the first caption words of each, never tokens. */
const { Firestore } = require("@google-cloud/firestore");
require("../../functions/deps").set({ db: new Firestore({ projectId: process.env.PROJECT || "little-hive-house", ignoreUndefinedProperties: true }) });
const G = require("../../functions/ads")._internal.graph;
const say = (s) => console.log(`::warning title=meta::${String(s).replace(/\n/g, " ").slice(0, 900)}`);
(async () => {
  const db = require("../../functions/deps").db();
  const meta = ((await db.collection("ads").doc("auth").get()).data() || {}).meta;
  const pg = await G(meta, "GET", meta.pageId, { fields: "access_token" });
  const page = { token: pg.access_token, appSecret: meta.appSecret };
  const tries = [
    ["scheduled_posts", `${meta.pageId}/scheduled_posts`, { fields: "id,message,scheduled_publish_time" }],
    ["promotable_posts não publicados", `${meta.pageId}/promotable_posts`, { is_published: false, fields: "id,message,scheduled_publish_time,is_published" }],
    ["videos", `${meta.pageId}/videos`, { fields: "id,description,published,scheduled_publish_time,created_time", limit: 50 }],
    ["video_reels", `${meta.pageId}/video_reels`, { fields: "id,description,published,scheduled_publish_time,created_time", limit: 50 }],
    ["feed", `${meta.pageId}/feed`, { fields: "id,message,is_published,scheduled_publish_time,created_time", limit: 50 }],
  ];
  for (const [label, path, params] of tries) {
    try {
      const j = await G(page, "GET", path, params);
      const d = j.data || [];
      const sched = d.filter((x) => x.scheduled_publish_time || x.published === false || x.is_published === false);
      say(`${label}: ${d.length} itens, ${sched.length} não publicados/agendados` + (sched.length ? " → " + sched.slice(0, 6).map((x) => `${x.scheduled_publish_time || "?"} ${(x.message || x.description || "").slice(0, 40)}`).join(" | ") : ""));
    } catch (e) { say(`${label}: erro ${e.message}`); }
  }
  try {
    const j = await G(page, "GET", `${meta.pageId}/videos`, { fields: "id,description,published,status,scheduled_publish_time,length,picture,source,permalink_url,created_time", limit: 50 });
    for (const v of (j.data || []).filter((x) => x.published === false)) {
      say(`vídeo não publicado ${v.id}: ${JSON.stringify({ desc: (v.description || "").slice(0, 60), status: v.status, sched: v.scheduled_publish_time, len: v.length, temSource: !!v.source, temPicture: !!v.picture, criado: v.created_time })}`);
    }
  } catch (e) { say(`videos detalhe: erro ${e.message}`); }
  try {
    const j = await G(meta, "GET", `${meta.igUserId}/content_publishing_limit`, { fields: "quota_usage,config" });
    say(`instagram limite de publicação: ${JSON.stringify(j.data || j)}`);
  } catch (e) { say(`instagram limite: erro ${e.message}`); }
})().catch((e) => { say(`erro: ${e.message}`); process.exit(1); });
