"use strict";
/* Etsy, one listing (VALUE = its key in etsy-listings.json, e.g. brasil): tries, step by step, how Etsy lets a listing's
   photos be put back in order and swapped for the new set, printing every answer. Used to find the safe way before
   changing functions/etsy.js. Touches only that one listing's photos. */
const { Firestore } = require("@google-cloud/firestore");
const db = new Firestore({ projectId: process.env.PROJECT || "little-hive-house" });
const API = "https://api.etsy.com/v3/application";
const K = process.env.ETSY_KEYSTRING, S = process.env.ETSY_SHARED_SECRET;
const SITE = "https://littlehivehouse.com";
const LISTINGS = require("../../functions/etsy-listings.json");
const say = (s) => console.log(`::warning title=etsy::${String(s).replace(/%/g, "%25").replace(/\n/g, " | ").slice(0, 1800)}`);
const pause = () => new Promise((r) => setTimeout(r, 1500));

(async () => {
  const a = (await db.collection("etsy").doc("auth").get()).data() || {};
  if (!(a.access && Number(a.expiresAt) > Date.now() + 120000)) throw new Error("access expired: run etsy-images first");
  const H = { "x-api-key": `${K}:${S}`, Authorization: `Bearer ${a.access}`, Accept: "application/json" };
  const key = process.env.VALUE, l = LISTINGS.listings.find((x) => x.id === key);
  const id = (((await db.collection("etsy").doc("listings").get()).data() || {})[key] || {}).listingId;
  const shop = a.shopId;
  async function req(label, method, path, body) {
    await pause();
    const res = await fetch(`${API}${path}`, { method, headers: H, body });
    const t = await res.text();
    say(`${label}: ${res.status} ${t.slice(0, 600)}`);
    try { return { ok: res.ok, j: JSON.parse(t) }; } catch (e) { return { ok: res.ok, j: {} }; }
  }
  const list = async (label) => {
    const r = await req(label, "GET", `/listings/${id}/images`);
    return (r.j.results || []).map((im) => ({ id: im.listing_image_id, rank: im.rank }));
  };
  const photo = async (n) => new Blob([Buffer.from(await (await fetch(`${SITE}/etsy/img/${key}/${n}.jpg?v=${LISTINGS.imagesVersion}`)).arrayBuffer())], { type: "image/jpeg" });

  let old = await list("1 before");
  // A: put the existing photo(s) back at ranks 1..k (re-attach by id)
  for (let i = 0; i < old.length; i++) {
    const fd = new FormData(); fd.append("listing_image_id", String(old[i].id)); fd.append("rank", String(i + 1));
    await req(`2 re-rank ${old[i].id} -> ${i + 1}`, "POST", `/shops/${shop}/listings/${id}/images`, fd);
  }
  old = await list("3 after re-rank");
  // B: one new photo in at rank 1 (no overwrite)
  const fd = new FormData(); fd.append("image", await photo(1), `${key}-1.jpg`); fd.append("rank", "1"); fd.append("alt_text", String(l.alt || l.title).slice(0, 250));
  await req("4 new photo 1 at rank 1", "POST", `/shops/${shop}/listings/${id}/images`, fd);
  await list("5 after");
})().catch((e) => { say("failed: " + e.message); process.exit(1); });
