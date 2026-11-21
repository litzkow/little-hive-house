"use strict";
/* The site's store-wide sale on TikTok Shop too (owners, Nov 2026: the Black Friday / holiday promotions of the site and
   Etsy also go on the other stores). Reads the sale from catalog.json (rules.sale: the % off for the whole sale, and a
   bigger % on its special "days", e.g. 30% on Black Friday itself) and keeps one TikTok "Product discount"
   (DIRECT_DISCOUNT) activity per part, with every TikTok product that is on sale in it. TikTok applies only the highest
   discount when a product is in two activities, so the special day simply sits on top of the long sale and nothing ever
   combines (the owners' rule). The "buy X, get Y free" deals of the site have no TikTok equivalent through the API and
   would combine with the % off, so they stay on the site.
   Runs with the orders every 15 minutes: makes what's missing, adds products approved since, never twice.
   tiktok/promos: {<key>: {activityId, products: [ids], begin, end}}. */

const { nowIso } = require("./config");
const deps = require("./deps");
const T = () => require("./tiktok")._internal;

const col = () => deps.db().collection("tiktok");

/** The parts of the sale still to come or running: [{key, title, pct, begin, end}] (seconds), pure. */
function parts(sale, nowMs) {
  if (!sale) return [];
  const sec = (iso) => Math.floor(Date.parse(iso) / 1000);
  const now = Math.floor(nowMs / 1000);
  const out = [{ key: `${sale.name}-${sale.start}`, title: `${sale.name} ${Math.round(sale.pct)}% off`, pct: Number(sale.pct) || 0, begin: sec(sale.start), end: sec(sale.end) }];
  for (const d of sale.days || []) {
    if (d.pct) out.push({ key: `${d.name}-${d.start}`, title: `${d.name} ${Math.round(d.pct)}% off`, pct: Number(d.pct), begin: sec(d.start), end: sec(d.end) });
  }
  // TikTok can't start an activity in the past: a running part starts a couple of minutes from now
  return out.filter((p) => p.pct > 0 && p.end > now + 600).map((p) => ({ ...p, begin: Math.max(p.begin, now + 120) }));
}

async function sync({ now = Date.now() } = {}) {
  const a = await T().readAuth();
  if (!a || !a.shopCipher) return { connected: false };
  const sale = (require("./catalog.json").rules || {}).sale;
  const want = parts(sale, now);
  if (!want.length) return { parts: 0 };
  const done = (await col().doc("products").get()).data() || {};
  const active = Object.values(done).filter((r) => r && r.productId && r.state === "active").map((r) => String(r.productId));
  const promos = (await col().doc("promos").get()).data() || {};
  const sum = { made: 0, added: 0, errors: [] };
  for (const p of want) {
    let row = promos[p.key];
    try {
      if (!row || !row.activityId) {
        const d = await T().call("POST", "/promotion/202309/activities", { json: {
          title: p.title.slice(0, 50), activity_type: "DIRECT_DISCOUNT", begin_time: p.begin, end_time: p.end, product_level: "PRODUCT" } });
        row = { activityId: String(d.activity_id), products: [], begin: p.begin, end: p.end, pct: p.pct, at: nowIso() };
        await col().doc("promos").set({ [p.key]: row }, { merge: true });
        sum.made++;
      }
      const missing = active.filter((id) => !(row.products || []).includes(id));
      for (let i = 0; i < missing.length; i += 20) {
        const batch = missing.slice(i, i + 20);
        await T().call("PUT", `/promotion/202309/activities/${row.activityId}/products`, { json: {
          products: batch.map((id) => ({ id, discount: String(p.pct) })) } });
        row.products = (row.products || []).concat(batch);
        await col().doc("promos").set({ [p.key]: { products: row.products, at: nowIso() } }, { merge: true });
        sum.added += batch.length;
      }
    } catch (e) {
      sum.errors.push(`${p.title}: ${String(e.message).slice(0, 200)}`);
    }
  }
  console.log("[tiktokPromos]", JSON.stringify(sum));
  return sum;
}

module.exports = { sync, parts };
