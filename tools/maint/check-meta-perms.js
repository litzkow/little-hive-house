"use strict";
/* Meta: which permissions the connection (ads/auth.meta, the system-user token) has. Publishing Reels and posts from
   the app needs instagram_content_publish and pages_manage_posts. Prints only permission names (never the token). */
const { Firestore } = require("@google-cloud/firestore");
require("../../functions/deps").set({ db: new Firestore({ projectId: process.env.PROJECT || "little-hive-house", ignoreUndefinedProperties: true }) });
const G = require("../../functions/ads")._internal.graph;
const say = (s) => console.log(`::warning title=meta::${String(s).slice(0, 1800)}`);
(async () => {
  const db = require("../../functions/deps").db();
  const meta = ((await db.collection("ads").doc("auth").get()).data() || {}).meta;
  if (!meta) return say("Meta não está conectado");
  const d = await G(meta, "GET", "debug_token", { input_token: meta.token });
  const x = d.data || {};
  say(`válido: ${x.is_valid} · tipo: ${x.type} · expira: ${x.expires_at ? new Date(x.expires_at * 1000).toISOString() : "nunca"}`);
  say(`permissões: ${(x.scopes || []).join(", ")}`);
  const need = ["instagram_content_publish", "pages_manage_posts", "instagram_basic", "pages_read_engagement"];
  say(`faltam para publicar: ${need.filter((s) => !(x.scopes || []).includes(s)).join(", ") || "nenhuma"}`);
})().catch((e) => { say(`erro: ${e.message}`); process.exit(1); });
