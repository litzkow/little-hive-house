"use strict";
/* Etsy: the shop's headline and announcement (what shows under the shop name and at the top of the shop), so custom
   photo magnets get the same weight as the ready-made collections, like on the website. Run from Actions (etsy-shop).
   The banner and the shop icon can't be changed through Etsy's API: the owners upload those in Shop Manager. */
const { Firestore } = require("@google-cloud/firestore");
const db = new Firestore({ projectId: process.env.PROJECT || "little-hive-house" });
const API = "https://api.etsy.com/v3/application";
const K = process.env.ETSY_KEYSTRING, S = process.env.ETSY_SHARED_SECRET;
const say = (s) => console.log(`::warning title=etsy::${String(s).replace(/%/g, "%25").replace(/\n/g, " | ").slice(0, 1800)}`);

const TITLE = "Photo, personalized and business 2x2 fridge magnets";
/* while the Black Friday sale runs on Etsy (our own sale 20-22 Nov, then Etsy's Cyber Specials event 23 Nov - 1 Dec,
   25% off everything), the announcement opens with it; run this again after it ends and the lines go away by themselves */
const SALE_END = Date.parse("2026-12-02T05:00:00Z");
const SALE = Date.now() < SALE_END ? [
  "BLACK FRIDAY: 25% off the whole shop, already in the price, through Cyber Monday (December 1).",
  "Christmas gifts, personalized magnets, photo magnets and business magnets, all on sale.",
  "",
] : [];
const ANNOUNCEMENT = [...SALE,
  "Welcome to Little Hive House!",
  "",
  "NEW: magnets made just for you. Pick a design, tell us your words, and we send you a proof before we print.",
  "• Business Magnets: your logo, phone and offer on your customers' fridge. Designs for 60 kinds of business: restaurants, dentists, cleaning, realtors, salons, churches and more, from 50 magnets.",
  "• Personalized Magnets: your family name, your pet, your baby, grandma's kitchen, your trip, or your photo with a few words. From 1 magnet.",
  "",
  "Also:",
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
