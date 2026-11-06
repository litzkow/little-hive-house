"use strict";
/* Etsy: does what the Hive Admin's Etsy button does (functions/etsy.js, the same code), from here: every listing that
   is missing or has new photos to send, one at a time. VALUE = one listing key to do only that one (empty = all).
   Prints each result as an annotation on the run page. */
process.env.SITE_URL = process.env.SITE_URL || "https://littlehivehouse.com";
// the database through @google-cloud/firestore (it understands the workflow's keyless Google sign-in; firebase-admin doesn't)
const { Firestore } = require("@google-cloud/firestore");
require("../../functions/deps").set({ db: new Firestore({ projectId: process.env.PROJECT || "little-hive-house", ignoreUndefinedProperties: true }) });
const E = require("../../functions/etsy");
const say = (s) => console.log(`::warning title=etsy::${String(s).replace(/%/g, "%25").replace(/\n/g, " | ").slice(0, 1800)}`);
const AUTH = { uid: "maintenance", token: { admin: true, email: "maintenance" } };

(async () => {
  if (process.env.VALUE === "arrange") {          // the shop in the site's order: sections and featured listings
    const r = await E.adminEtsy({ action: "arrange" }, AUTH);
    say(`arranged: sections ${r.sections.join(" > ")}, ${r.renamed} renamed, ${r.listings.length} listings`);
    return;
  }
  if (process.env.VALUE === "texts") {   // only the texts (title, description, tags, section) of every listing on Etsy
    const L = require("../../functions/etsy-listings.json").listings;
    const db = require("../../functions/deps").db();
    const done = (await db.collection("etsy").doc("listings").get()).data() || {};
    const st = await E.adminEtsy({ action: "status" }, AUTH);
    let failed = 0;
    for (const l of L) {
      const d = done[l.id];
      if (!d || !d.listingId) continue;
      try { await E._internal.patchTexts(l, d.listingId); say(`${l.id}: texts ok`); } catch (e) { failed += 1; say(`${l.id}: FAILED ${e.message}`); }
    }
    process.exit(failed ? 1 : 0);
  }
  if (/^force:/.test(process.env.VALUE || "")) {   // force:<key>: send this listing's photos again (same photo version)
    const key = process.env.VALUE.slice(6);
    const ref = require("../../functions/deps").db().collection("etsy").doc("listings");
    const cur = ((await ref.get()).data() || {})[key];
    if (!cur) throw new Error("unknown listing " + key);
    await ref.set({ [key]: { ...cur, imagesV: 0 } }, { merge: true });
    process.env.VALUE = key;
  }
  const st = await E.adminEtsy({ action: "status" }, AUTH);
  const one = process.env.VALUE && process.env.VALUE !== "all" && st.listings.some((l) => l.id === process.env.VALUE) ? process.env.VALUE : "";   // VALUE = a listing key, or "all"
  const todo = st.listings.filter((l) => (one ? l.id === one : (l.state !== "active" || l.newPhotos)));
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
