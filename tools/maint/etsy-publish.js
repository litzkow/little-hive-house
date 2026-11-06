"use strict";
/* Etsy: does what the Hive Admin's Etsy button does (functions/etsy.js, the same code), from here: every listing that
   is missing or has new photos to send, one at a time. VALUE = one listing key to do only that one (empty = all).
   Prints each result as an annotation on the run page. */
process.env.SITE_URL = process.env.SITE_URL || "https://littlehivehouse.com";
const E = require("../../functions/etsy");
const say = (s) => console.log(`::warning title=etsy::${String(s).replace(/%/g, "%25").replace(/\n/g, " | ").slice(0, 1800)}`);
const AUTH = { uid: "maintenance", token: { admin: true, email: "maintenance" } };

(async () => {
  const st = await E.adminEtsy({ action: "status" }, AUTH);
  const todo = st.listings.filter((l) => (process.env.VALUE ? l.id === process.env.VALUE : (l.state !== "active" || l.newPhotos)));
  say(`to do: ${todo.map((l) => l.id).join(", ") || "nothing"}`);
  let failed = 0;
  for (const l of todo) {
    const t = Date.now();
    try {
      const r = await E.adminEtsy({ action: "publish", id: l.id }, AUTH);
      say(`${l.id}: ok ${r.listing.state} imagesV=${r.listing.imagesV} (${Math.round((Date.now() - t) / 1000)}s)`);
    } catch (e) { failed += 1; say(`${l.id}: FAILED ${e.message} (${Math.round((Date.now() - t) / 1000)}s)`); }
  }
  process.exit(failed ? 1 : 0);
})().catch((e) => { say("failed: " + e.message); process.exit(1); });
