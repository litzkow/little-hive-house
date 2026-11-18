"use strict";
/* Meta: the ad account's Pixel (made once if there is none, as the owners approved), the connection's permissions, and
   whether Reel insights (shares, saves, watch time) can be read. Saves the Pixel id in ads/auth.meta.pixelId.
   Prints ids and permission names only, never the token. */
const { Firestore } = require("@google-cloud/firestore");
require("../../functions/deps").set({ db: new Firestore({ projectId: process.env.PROJECT || "little-hive-house", ignoreUndefinedProperties: true }) });
const G = require("../../functions/ads")._internal.graph;
const say = (s) => console.log(`::warning title=pixel::${String(s).replace(/\n/g, " ").slice(0, 900)}`);
(async () => {
  const db = require("../../functions/deps").db();
  const aref = db.collection("ads").doc("auth"), meta = ((await aref.get()).data() || {}).meta;
  const d = await G(meta, "GET", "debug_token", { input_token: meta.token });
  say(`permissões: ${((d.data || {}).scopes || []).join(", ")}`);
  let px = ((await G(meta, "GET", `${meta.adAccountId}/adspixels`, { fields: "id,name,last_fired_time,creation_time" })).data || []);
  say(`pixels na conta: ${px.map((p) => `${p.id} ${p.name} (último disparo ${p.last_fired_time || "nunca"})`).join(" | ") || "nenhum"}`);
  if (!px.length && process.env.CREATE === "1") {
    const r = await G(meta, "POST", `${meta.adAccountId}/adspixels`, { name: "Little Hive House" });
    px = [{ id: String(r.id), name: "Little Hive House" }];
    say(`pixel criado: ${r.id}`);
  }
  if (px[0]) {
    await aref.set({ meta: { ...meta, pixelId: String(px[0].id) } }, { merge: true });
    try {
      const t = await G(meta, "POST", `${px[0].id}/events`, { data: [{ event_name: "PageView", event_time: Math.floor(Date.now() / 1000), action_source: "website",
        event_source_url: "https://littlehivehouse.com/", user_data: { client_user_agent: "hive-admin-check", client_ip_address: "8.8.8.8" } }], test_event_code: "TEST00000" });
      say(`API de Conversões: aceita (${JSON.stringify(t).slice(0, 120)})`);
    } catch (e) { say(`API de Conversões: erro ${e.message.slice(0, 200)}`); }
  }
  try {
    const m = ((await G(meta, "GET", `${meta.igUserId}/media`, { fields: "id,media_product_type,timestamp", limit: 10 })).data || []).find((x) => x.media_product_type === "REELS");
    if (m) {
      const ins = await G(meta, "GET", `${m.id}/insights`, { metric: "reach,shares,saved,ig_reels_avg_watch_time,views" });
      say(`métricas do Reel ${m.id}: ${((ins.data || []).map((x) => `${x.name}=${(x.values && x.values[0] && x.values[0].value) ?? x.total_value?.value}`)).join(", ")}`);
    } else say("nenhum Reel recente para testar as métricas");
  } catch (e) { say(`métricas: erro ${e.message.slice(0, 200)}`); }
})().catch((e) => { say(`erro: ${e.message}`); process.exit(1); });
