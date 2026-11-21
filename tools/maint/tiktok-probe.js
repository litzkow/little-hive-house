"use strict";
/* TikTok Shop: what the connected shop looks like to the API (read-only): the connection, warehouses and their
   delivery options, the category TikTok recommends for a fridge magnet, its attributes and rules, products already
   there. Prints no token or secret. VALUE = a category id to look at instead of the recommended one. */
process.env.SITE_URL = process.env.SITE_URL || "https://littlehivehouse.com";
const fs = require("fs");
const { Firestore } = require("@google-cloud/firestore");
require("../../functions/deps").set({ db: new Firestore({ projectId: process.env.PROJECT || "little-hive-house", ignoreUndefinedProperties: true }) });
const say = (s) => console.log(`::warning title=tiktok::${String(s).replace(/\n/g, " ").slice(0, 950)}`);
const out = {};
(async () => {
  const T = require("../../functions/tiktok")._internal;
  const a = (await T.readAuth()) || {};
  say(`conectado: ${!!(a.refresh && a.shopCipher)} · loja: ${a.shopName || "?"} (${a.shopRegion || "?"}) · permissões: ${(a.scopes || []).join(", ")}`);
  const tryCall = async (label, ...args) => {
    try { const d = await T.call(...args); out[label] = d; return d; } catch (e) { say(`${label}: ERRO ${e.message}`); out[label] = { error: e.message }; return null; }
  };
  const wh = await tryCall("warehouses", "GET", "/logistics/202309/warehouses");
  if (wh) {
    for (const w of wh.warehouses || []) {
      say(`armazém ${w.id} · ${w.name} · tipo ${w.type} · ${w.effect_status} · padrão ${w.is_default} · ${JSON.stringify(w.address || {}).slice(0, 200)}`);
      const d = await tryCall(`delivery-${w.id}`, "GET", `/logistics/202309/warehouses/${w.id}/delivery_options`);
      if (d) say(`entrega ${w.id}: ${JSON.stringify(d).slice(0, 900)}`);
    }
  }
  const rec = await tryCall("recommend", "POST", "/product/202309/categories/recommend", { json: {
    product_title: "Grand Canyon Fridge Magnet, 2x2 Inch Square Handmade Travel Poster Magnet", category_version: "v2" } });
  if (rec) say(`categoria recomendada: ${JSON.stringify(rec).slice(0, 900)}`);
  const cats = await tryCall("categories", "GET", "/product/202309/categories", { query: { locale: "en-US", category_version: "v2" } });
  if (cats) {
    const list = cats.categories || [];
    const mag = list.filter((c) => /magnet|fridge|refrigerator|souvenir|sticker/i.test(c.local_name || ""));
    say(`categorias: ${list.length} · com ímã/geladeira/souvenir: ${mag.map((c) => `${c.id} ${c.local_name}${c.is_leaf ? " (folha)" : ""} pai ${c.parent_id} ${c.permission_statuses || ""}`).join(" | ").slice(0, 850)}`);
  }
  const leaf = process.env.VALUE && /^\d+$/.test(process.env.VALUE) ? process.env.VALUE
    : rec && (rec.leaf_category_id || ((rec.categories || []).find((c) => c.is_leaf) || {}).id);
  if (leaf) {
    const at = await tryCall("attributes", "GET", `/product/202309/categories/${leaf}/attributes`, { query: { locale: "en-US", category_version: "v2" } });
    if (at) {
      for (const x of at.attributes || []) {
        say(`atributo ${x.id} · ${x.name} · ${x.type} · obrigatório ${!!(x.is_requried || x.is_required)} · vários ${!!x.is_multiple_selection} · personalizado ${!!x.is_customizable} · valores: ${(x.values || []).slice(0, 12).map((v) => `${v.id}:${v.name}`).join(", ")}`);
      }
    }
    const ru = await tryCall("rules", "GET", `/product/202309/categories/${leaf}/rules`, { query: { category_version: "v2" } });
    if (ru) say(`regras ${leaf}: ${JSON.stringify(ru).slice(0, 900)}`);
  }
  const pr = await tryCall("products", "POST", "/product/202309/products/search", { query: { page_size: "20" }, json: {} });
  if (pr) say(`produtos no TikTok: ${pr.total_count || (pr.products || []).length} · ${(pr.products || []).slice(0, 5).map((p) => `${p.id} ${p.title} ${p.status}`).join(" | ")}`);
  const brands = await tryCall("brands", "GET", "/product/202309/brands", { query: { page_size: "20", ...(leaf ? { category_id: String(leaf) } : {}), brand_name: "Little Hive House" } });
  if (brands) say(`marcas: ${JSON.stringify(brands).slice(0, 600)}`);
  fs.writeFileSync("tiktok-probe.json", JSON.stringify(out, null, 1));
})().catch((e) => { say(`erro: ${e.message}`); process.exit(1); });
