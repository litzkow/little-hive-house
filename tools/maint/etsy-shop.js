"use strict";
/* Etsy: the shop's headline and announcement (what shows under the shop name and at the top of the shop), so custom
   photo magnets get the same weight as the ready-made collections, like on the website. Run from Actions (etsy-shop).
   The banner and the shop icon can't be changed through Etsy's API: the owners upload those in Shop Manager. */
const { Firestore } = require("@google-cloud/firestore");
const db = new Firestore({ projectId: process.env.PROJECT || "little-hive-house" });
const API = "https://api.etsy.com/v3/application";
const K = process.env.ETSY_KEYSTRING, S = process.env.ETSY_SHARED_SECRET;
const say = (s) => console.log(`::warning title=etsy::${String(s).replace(/%/g, "%25").replace(/\n/g, " | ").slice(0, 1800)}`);

const TITLE = "Your photos or our designs, as 2x2 fridge magnets";
const ANNOUNCEMENT = [
  "Welcome to Little Hive House!",
  "",
  "Two ways to fill your fridge:",
  "• Your own photos: upload any picture (family, pets, trips, weddings) and we turn it into a 2 x 2 inch magnet, with a frame and caption if you like. See the Photo Magnets section.",
  "• Our designs: hundreds of original, hand-painted magnets, from travel posters and heritage collections to seasonal, sayings and storybook classics.",
  "",
  "Every magnet is printed, pressed and packed by hand in our small studio and ships in 1 to 2 business days. Free US shipping on orders of $35 or more.",
].join("\n");

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
  const res = await fetch(`${API}/shops/${a.shopId}`, { method: "PUT",
    headers: { "x-api-key": `${K}:${S}`, Authorization: `Bearer ${a.access}`, "Content-Type": "application/x-www-form-urlencoded", Accept: "application/json" },
    body: new URLSearchParams({ title: TITLE, announcement: ANNOUNCEMENT }).toString() });
  const j = await res.json().catch(() => ({}));
  say(`shop update ${res.status}: title=${j.title || ""} | ${res.ok ? "announcement saved" : JSON.stringify(j).slice(0, 400)}`);
  if (!res.ok) process.exit(1);
})().catch((e) => { say("failed: " + e.message); process.exit(1); });
