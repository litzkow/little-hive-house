"use strict";
/* Did the store's own server read Google Analytics? Reads analyticsCache/status, written by analyticsWarm (functions/analytics.js).
   CHECK = fresh (written in the last 10 minutes) | ok | access (the error is missing access) | api (the API is off). Exit 0 = yes. */
const { Firestore } = require("@google-cloud/firestore");
const db = new Firestore({ projectId: process.env.PROJECT || "little-hive-house" });
(async () => {
  const d = await db.collection("analyticsCache").doc("status").get();
  const s = d.exists ? d.data() : {};
  const yes = {
    fresh: !!s.at && Date.now() - Date.parse(s.at) < 10 * 60 * 1000,
    ok: s.ok === true,
    access: /access|Viewer/i.test(s.error || ""),
    api: /Data API is off/i.test(s.error || ""),
  }[process.env.CHECK];
  process.exit(yes ? 0 : 1);
})().catch((e) => { console.error(e.message); process.exit(1); });
