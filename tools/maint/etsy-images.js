"use strict";
/* Etsy: shows how the photos of each listing are arranged on Etsy (id and rank of each), for the listings whose last
   publish left an error (or all of them with VALUE=all). Read-only on Etsy: it only asks. If the Etsy access has
   expired it renews it and saves it back, exactly like functions/etsy.js does. Output as annotations on the run page. */
const { Firestore } = require("@google-cloud/firestore");
const db = new Firestore({ projectId: process.env.PROJECT || "little-hive-house" });
const API = "https://api.etsy.com/v3/application";
const K = process.env.ETSY_KEYSTRING, S = process.env.ETSY_SHARED_SECRET;
const say = (s) => console.log(`::warning title=etsy::${String(s).replace(/%/g, "%25").replace(/\n/g, " | ").slice(0, 1800)}`);

async function token() {
  const ref = db.collection("etsy").doc("auth");
  const a = (await ref.get()).data() || {};
  if (a.access && Number(a.expiresAt) > Date.now() + 60000) return { a, access: a.access };
  const res = await fetch("https://api.etsy.com/v3/public/oauth/token", {
    method: "POST", headers: { "Content-Type": "application/x-www-form-urlencoded", Accept: "application/json" },
    body: new URLSearchParams({ client_id: K, grant_type: "refresh_token", refresh_token: a.refresh }).toString(),
  });
  const j = await res.json();
  if (!j.access_token) throw new Error("refresh failed: " + JSON.stringify(j));
  await ref.set({ access: j.access_token, refresh: j.refresh_token, expiresAt: Date.now() + (Number(j.expires_in) || 3600) * 1000, at: new Date().toISOString() }, { merge: true });
  return { a, access: j.access_token };
}

(async () => {
  const { a, access } = await token();
  const listings = (await db.collection("etsy").doc("listings").get()).data() || {};
  const all = process.env.VALUE === "all" || process.env.VALUE === "urls";
  for (const [key, d] of Object.entries(listings)) {
    const pick = !all && process.env.VALUE ? process.env.VALUE.split(",").includes(key) : null;   // VALUE = some keys (GitHub shows only 10 notes per step)
    if (!d.listingId || (pick === false) || (pick === null && !all && !d.error)) continue;
    await new Promise((r) => setTimeout(r, 1500));   // Etsy allows only a few requests per second
    const res = await fetch(`${API}/listings/${d.listingId}/images`, { headers: { "x-api-key": `${K}:${S}`, Authorization: `Bearer ${access}`, Accept: "application/json" } });
    const j = await res.json().catch(() => ({}));
    const imgs = (j.results || []).map((im) => `${im.listing_image_id}@r${im.rank}${process.env.VALUE === "urls" ? "=" + String(im.url_570xN || "").split("/").slice(-2).join("/") : ""}`).join(" ");
    say(`${key} listing=${d.listingId} state=${d.state} imagesV=${d.imagesV || 1} status=${res.status} count=${(j.results || []).length} :: ${imgs || JSON.stringify(j).slice(0, 300)} :: err=${d.error || ""}`);
  }
  say(`shop=${a.shopId} scope=${a.scope}`);
})().catch((e) => { say("failed: " + e.message); process.exit(1); });
