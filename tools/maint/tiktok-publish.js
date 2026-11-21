"use strict";
/* TikTok Shop: publishes one design collection (VALUE = its id, e.g. birth-flowers), then asks TikTok where each
   published product stands. VALUE=check only asks; DRAFT=1 saves it as a draft (not for sale). Prints no token or secret. */
process.env.SITE_URL = process.env.SITE_URL || "https://littlehivehouse.com";
const { Firestore } = require("@google-cloud/firestore");
require("../../functions/deps").set({ db: new Firestore({ projectId: process.env.PROJECT || "little-hive-house", ignoreUndefinedProperties: true }) });
const say = (s) => console.log(`::warning title=tiktok::${String(s).replace(/\n/g, " ").slice(0, 950)}`);
(async () => {
  const P = require("../../functions/tiktok-products");
  const id = (process.env.VALUE || "").trim();
  if (id && id !== "check") {
    try { const r = await P.publish(id, { draft: process.env.DRAFT === "1" }); say(`publicado ${id}: ${JSON.stringify(r).slice(0, 600)}`); }
    catch (e) {
      say(`ERRO ao publicar ${id}: ${e.message}`);
      if (process.env.DUMP === "1") say(JSON.stringify(P._internal.body(require("../../functions/etsy-listings.json").listings.find((l) => l.id === id), ["uri"], [], "wh")).slice(0, 900));
    }
  }
  await new Promise((r) => setTimeout(r, 4000));
  await P.refresh();
  for (const p of await P.status()) if (p.productId || p.error) say(`${p.id}: ${p.state} ${p.productId || ""} ${p.error || ""}`);
})().catch((e) => { say(`erro: ${e.message}`); process.exit(1); });
