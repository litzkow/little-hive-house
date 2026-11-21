"use strict";
/* TikTok Shop: puts the site's current sale on TikTok (functions/tiktok-promotions.js) and shows what TikTok has. */
process.env.SITE_URL = process.env.SITE_URL || "https://littlehivehouse.com";
const { Firestore } = require("@google-cloud/firestore");
require("../../functions/deps").set({ db: new Firestore({ projectId: process.env.PROJECT || "little-hive-house", ignoreUndefinedProperties: true }) });
const say = (s) => console.log(`::warning title=tiktok::${String(s).replace(/\n/g, " ").slice(0, 950)}`);
(async () => {
  await require("../../functions/tiktok-products").refresh({ onlyPending: true });
  say(`partes: ${JSON.stringify(require("../../functions/tiktok-promotions").parts(require("../../functions/catalog.json").rules.sale, Date.now()))}`);
  const r = await require("../../functions/tiktok-promotions").sync();
  say(`resultado: ${JSON.stringify(r)}`);
  const T = require("../../functions/tiktok")._internal;
  const db = require("../../functions/deps").db();
  const promos = (await db.collection("tiktok").doc("promos").get()).data() || {};
  for (const [k, p] of Object.entries(promos)) {
    try { const d = await T.call("GET", `/promotion/202309/activities/${p.activityId}`); say(`${k}: ${JSON.stringify(d).slice(0, 700)}`); }
    catch (e) { say(`${k}: erro ${e.message}`); }
  }
})().catch((e) => { say(`erro: ${e.message}`); process.exit(1); });
