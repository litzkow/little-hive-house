"use strict";
/* Did the ads robot (functions/ads.js, scheduled job adsDaily) run, and could it read each channel?
   Reads ads/state.lastRun. CHECK = fresh (ran in the last 10 minutes) | site (read Google Analytics) | etsy (read Etsy)
   | meta (read Meta, or Meta isn't connected). Exit 0 = yes. Prints only the error text (no customer data). */
const { Firestore } = require("@google-cloud/firestore");
const db = new Firestore({ projectId: process.env.PROJECT || "little-hive-house" });
(async () => {
  const d = await db.collection("ads").doc("state").get();
  const r = (d.exists && d.data().lastRun) || {};
  const errs = r.errors || {};
  const k = process.env.CHECK;
  if (errs[k]) console.log(`${k}: ${String(errs[k]).slice(0, 300)}`);
  const yes = k === "fresh" ? !!r.at && Date.now() - Date.parse(r.at) < 10 * 60 * 1000 : !!r.at && !errs[k];
  if (k === "fresh") console.log(`total this month: ${r.total}, allowed a day: ${r.allowed}`);
  process.exit(yes ? 0 : 1);
})().catch((e) => { console.error(e.message); process.exit(1); });
