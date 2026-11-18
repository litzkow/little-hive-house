"use strict";
/* Meta: what the scheduling options can use with this connection (place search for "Location", checking an Instagram
   username for collaborators and tags). Read-only; prints results, never tokens. */
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
    ["pages/search (usuário)", meta, "pages/search", { q: "Atlanta Georgia", fields: "id,name,location,link", limit: 5 }],
    ["pages/search (página)", page, "pages/search", { q: "Atlanta Georgia", fields: "id,name,location,link", limit: 5 }],
    ["search type=place (usuário)", meta, "search", { type: "place", q: "Atlanta", fields: "id,name,location", limit: 5 }],
    ["search type=place (página)", page, "search", { type: "place", q: "Atlanta", fields: "id,name,location", limit: 5 }],
    ["usuário do Instagram (instagram)", meta, meta.igUserId, { fields: "business_discovery.username(instagram){username,name,profile_picture_url}" }],
    ["página: local da própria loja", page, meta.pageId, { fields: "name,location,single_line_address" }],
  ];
  for (const [label, who, path, params] of tries) {
    try { const j = await G(who, "GET", path, params); say(`${label}: OK ${JSON.stringify(j).slice(0, 400)}`); } catch (e) { say(`${label}: erro ${e.message.slice(0, 220)}`); }
  }
})().catch((e) => { say(`erro: ${e.message}`); process.exit(1); });
