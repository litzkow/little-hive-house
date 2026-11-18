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
  const show = (label, arr) => say(`${label}: ${arr.length} → ` + arr.slice(0, 8).map((x) => JSON.stringify({ id: x.id, pub: x.published ?? x.is_published,
    st: x.status && x.status.publishing_phase, sched: x.scheduled_publish_time, t: x.created_time || x.updated_time, d: (x.description || x.message || x.name || "").slice(0, 30) })).join(" | "));
  const tries = [
    ["video_reels", `${meta.pageId}/video_reels`, { fields: "id,description,published,status,scheduled_publish_time,created_time,updated_time", limit: 50 }],
    ["videos", `${meta.pageId}/videos`, { fields: "id,description,published,status,scheduled_publish_time,created_time", limit: 50 }],
    ["videos uploaded", `${meta.pageId}/videos`, { type: "uploaded", fields: "id,description,published,status,scheduled_publish_time,created_time", limit: 50 }],
    ["photos uploaded", `${meta.pageId}/photos`, { type: "uploaded", fields: "id,name,published,created_time", limit: 50 }],
    ["scheduled_posts", `${meta.pageId}/scheduled_posts`, { fields: "id,message,scheduled_publish_time,created_time" }],
    ["published_posts", `${meta.pageId}/published_posts`, { fields: "id,message,created_time,is_published", limit: 10 }],
    ["ads_posts", `${meta.pageId}/ads_posts`, { fields: "id,message,created_time,is_published,scheduled_publish_time", limit: 25, include_inline_create: true }],
  ];
  for (const [label, path, params] of tries) {
    try { const j = await G(page, "GET", path, params); show(label, j.data || []); } catch (e) { say(`${label}: erro ${e.message.slice(0, 160)}`); }
  }
  try { const j = await G(meta, "GET", `${meta.igUserId}/media`, { fields: "id,caption,timestamp,media_product_type", limit: 50 }); say(`instagram publicados: ${(j.data || []).length}`); } catch (e) { say(`ig: ${e.message}`); }
  try {
    const j = await G(meta, "GET", `${meta.igUserId}/content_publishing_limit`, { fields: "quota_usage,config" });
    say(`instagram limite de publicação: ${JSON.stringify(j.data || j)}`);
  } catch (e) { say(`instagram limite: erro ${e.message}`); }
})().catch((e) => { say(`erro: ${e.message}`); process.exit(1); });
