"use strict";
/* Etsy personalization questions (the new kind: file upload + text box). VALUE=read: shows how the Pet photo magnets
   listing is set up (several API shapes are tried, all read-only). VALUE=copy: copies the Pet listing's questions to
   the Custom and Family photo magnet listings. */
const { Firestore } = require("@google-cloud/firestore");
const db = new Firestore({ projectId: process.env.PROJECT || "little-hive-house" });
const API = "https://api.etsy.com/v3/application";
const K = process.env.ETSY_KEYSTRING, S = process.env.ETSY_SHARED_SECRET;
const say = (s) => console.log(`::warning title=etsy::${String(s).replace(/%/g, "%25").replace(/\n/g, " | ").slice(0, 3000)}`);

(async () => {
  const ref = db.collection("etsy").doc("auth");
  let a = (await ref.get()).data() || {};
  if (!(a.access && Number(a.expiresAt) > Date.now() + 60000)) {
    const res = await fetch("https://api.etsy.com/v3/public/oauth/token", { method: "POST", headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({ client_id: K, grant_type: "refresh_token", refresh_token: a.refresh }).toString() });
    const j = await res.json();
    if (!j.access_token) throw new Error("refresh failed");
    await ref.set({ access: j.access_token, refresh: j.refresh_token, expiresAt: Date.now() + (Number(j.expires_in) || 3600) * 1000 }, { merge: true });
    a = { ...a, access: j.access_token };
  }
  const H = { "x-api-key": `${K}:${S}`, Authorization: `Bearer ${a.access}`, Accept: "application/json" };
  const L = (await db.collection("etsy").doc("listings").get()).data() || {};
  const id = (k) => L[k].listingId;
  const get = async (path) => { const r = await fetch(API + path, { headers: H }); return { s: r.status, t: await r.text() }; };
  if (process.env.VALUE === "read") {
    for (const p of [`/listings/${id("pet-photo-magnets")}/personalization`, `/shops/${a.shopId}/listings/${id("pet-photo-magnets")}/personalization`,
      `/listings/${id("pet-photo-magnets")}?includes=Personalization`, `/listings/${id("pet-photo-magnets")}`]) {
      const r = await get(p);
      const t = r.t.replace(/"description":"(?:[^"\\]|\\.)*"/, '"description":"…"').replace(/"tags":\[[^\]]*\]/, "");
      say(`${p} -> ${r.s} ${t.slice(0, 2500)}`);
      await new Promise((ok) => setTimeout(ok, 800));
    }
    return;
  }
})().catch((e) => { say("failed: " + e.message); process.exit(1); });
