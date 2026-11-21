"use strict";
/* TikTok Shop: uploads the shop page pictures (tiktok/shop/*.jpg) to TikTok's own image storage and prints their
   TikTok links, so the Seller Center's shop designer can take them (it won't load pictures from other sites). */
process.env.SITE_URL = process.env.SITE_URL || "https://littlehivehouse.com";
const fs = require("fs");
const path = require("path");
const { Firestore } = require("@google-cloud/firestore");
require("../../functions/deps").set({ db: new Firestore({ projectId: process.env.PROJECT || "little-hive-house", ignoreUndefinedProperties: true }) });
const say = (s) => console.log(`::warning title=tiktok::${String(s).replace(/\n/g, " ").slice(0, 950)}`);
(async () => {
  const T = require("../../functions/tiktok")._internal;
  const dir = path.join(__dirname, "..", "..", "tiktok", "shop");
  for (const f of fs.readdirSync(dir).filter((x) => x.endsWith(".jpg"))) {
    const fd = new FormData();
    fd.append("data", new Blob([fs.readFileSync(path.join(dir, f))], { type: "image/jpeg" }), f);
    fd.append("use_case", "MAIN_IMAGE");
    try { const d = await T.call("POST", "/product/202309/images/upload", { form: fd, shop: false }); say(`${f} ${d.url || ""} ${d.uri || ""}`); }
    catch (e) { say(`${f} ERRO ${e.message}`); }
  }
})().catch((e) => { say(`erro: ${e.message}`); process.exit(1); });
