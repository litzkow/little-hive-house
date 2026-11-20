"use strict";
/* Loja do Instagram/Facebook: as categorias (coleções) iguais às do site, na ordem certa, com capa, publicadas na loja.
   Lê google-products.xml (o mesmo arquivo que o catálogo do Meta busca todo dia), agrupa pelo product_type e cria ou
   atualiza um conjunto de produtos por categoria, com filtro (os produtos novos entram sozinhos). A ordem: ímãs de foto,
   depois o que é da estação, depois a ordem do site. Pode rodar quantas vezes quiser: atualiza, não duplica.
   VALUE=dry só mostra o que faria. */
const fs = require("fs");
const { Firestore } = require("@google-cloud/firestore");
const db = new Firestore({ projectId: process.env.PROJECT || "little-hive-house" });
const say = (s) => console.log(`::warning title=categorias::${String(s).replace(/\n/g, " ").slice(0, 950)}`);
const V = "v26.0", SITE = "https://littlehivehouse.com";
const DESC = {
  "Photo Magnets": "Your own photos as 2x2 in fridge magnets, in packs of 4 to 50.",
  "Heritage": "Culture and home, from Brasil and México to Ireland, Italia, Japan and more.",
};
const PAGE = { "Photo Magnets": "photo-magnets.html" };
/** What leads the shop now: the season's collections, by month. */
function seasonFirst(month) {          // getMonth(): 0 = January ... 10 = November, 11 = December
  if (month >= 10) return ["Christmas", "Holidays & Dates"];
  if (month >= 8) return ["Fall", "Halloween"];
  if (month >= 5) return ["Summer"];
  return ["Holidays & Dates"];
}
const unxml = (s) => String(s).replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&quot;/g, '"').replace(/&#39;/g, "'").replace(/&amp;/g, "&");
function groups(xml) {
  const out = new Map();
  for (const it of xml.split("<item>").slice(1)) {
    const pt = unxml((it.match(/<g:product_type>([\s\S]*?)<\/g:product_type>/) || [])[1] || "");
    const img = unxml((it.match(/<g:image_link>([\s\S]*?)<\/g:image_link>/) || [])[1] || "");
    const link = unxml((it.match(/<g:link>([\s\S]*?)<\/g:link>/) || [])[1] || "");
    const parts = pt.split(" > ");
    if (parts.length < 2) continue;
    const name = parts[1] === "Photo magnets" ? "Photo Magnets" : parts[1];
    if (!out.has(name)) out.set(name, { name, count: 0, cover: img, match: `${parts[0]} > ${parts[1]}`, link });
    out.get(name).count += 1;
  }
  return [...out.values()];
}
(async () => {
  const dry = /dry/i.test(process.env.VALUE || "");
  const meta = ((await db.collection("ads").doc("auth").get()).data() || {}).meta;
  const call = async (method, path, params = {}, token = meta.token) => {
    const body = new URLSearchParams({ access_token: token });
    Object.entries(params).forEach(([k, v]) => body.set(k, typeof v === "string" ? v : JSON.stringify(v)));
    const r = method === "GET" ? await fetch(`https://graph.facebook.com/${V}/${path}?${body}`) : await fetch(`https://graph.facebook.com/${V}/${path}`, { method, body });
    const j = await r.json();
    if (j.error) throw new Error(`${path}: ${j.error.message}`);
    return j;
  };
  const acc = await call("GET", meta.adAccountId, { fields: "business{id}" });
  const cat = ((await call("GET", `${acc.business.id}/owned_product_catalogs`, { fields: "id,name" })).data || [])[0];
  say(`catálogo ${cat.name} (${cat.id})`);
  // the catalog reads the product file now, not only at 3 AM (new photos, new designs)
  if (!dry) for (const f of (await call("GET", `${cat.id}/product_feeds`, { fields: "id,schedule" })).data || []) {
    try { const u = f.schedule && f.schedule.url; if (u) { await call("POST", `${f.id}/uploads`, { url: u }); say(`catálogo relendo ${u}`); } } catch (e) { say(`releitura: ${e.message}`); }
  }
  // the shop(s) to publish in: through the Page (a Page token is needed for the Page's commerce settings)
  let shops = [];
  // the shop id: VALUE (from the Commerce Manager address) or saved before, else looked up through the Page
  const saved = ((await db.collection("shop").doc("metaCollections").get()).data() || {}).shops || [];
  const given = String(process.env.VALUE || "").match(/\d{10,}/g) || [];
  let pt = "";
  try { pt = (await call("GET", meta.pageId, { fields: "access_token" })).access_token; } catch (e) { say(`token da página: ${e.message}`); }
  const tries = [];
  for (const id of given) {
    tries.push(async () => [{ shop_id: (await call("GET", `${id}/shops`, { fields: "id" }, pt || meta.token)).data[0].id }]);
    tries.push(async () => { const r = await call("GET", id, { fields: "id,commerce_merchant_settings" }, pt || meta.token); return [{ shop_id: r.id }]; });
  }
  tries.push(async () => saved.length ? saved : null);
  tries.push(async () => { const r = await call("GET", meta.pageId, { fields: "commerce_merchant_settings" }, pt); return [{ shop_id: (await call("GET", `${r.commerce_merchant_settings.id}/shops`, {}, pt)).data[0].id }]; });
  tries.push(async () => { const r = await call("GET", `${meta.pageId}/commerce_merchant_settings`, {}, pt); return [{ shop_id: (await call("GET", `${r.data[0].id}/shops`, {}, pt)).data[0].id }]; });
  for (const t of tries) { try { const r = await t(); if (r && r.length && r[0].shop_id) { shops = r; break; } } catch (e) { say(`loja: ${e.message.slice(0, 200)}`); } }
  say(shops.length ? `loja: ${JSON.stringify(shops)}` : "não achei a loja para publicar; as categorias ficam prontas no catálogo");
  const G = groups(fs.readFileSync("google-products.xml", "utf8"));
  const first = ["Photo Magnets", ...seasonFirst(new Date().getMonth())];
  const ordered = [...first.map((n) => G.find((g) => g.name === n)).filter(Boolean), ...G.filter((g) => !first.includes(g.name))];
  const existing = (await call("GET", `${cat.id}/product_sets`, { fields: "id,name", limit: "200" })).data || [];
  const done = [];
  for (const g of ordered) {
    const params = {
      name: g.name,
      filter: { product_type: { i_contains: g.match } },
      metadata: { cover_image_url: g.cover, description: DESC[g.name] || `${g.name} fridge magnets, handmade 2x2 in.`, external_url: `${SITE}/${PAGE[g.name] || "shop.html"}` },
    };
    if (shops.length) params.publish_to_shops = shops;
    const old = existing.find((x) => x.name === g.name);
    if (dry) { say(`faria: ${old ? "atualizar" : "criar"} ${g.name} (${g.count})`); continue; }
    try {
      const r = old ? await call("POST", old.id, params) : await call("POST", `${cat.id}/product_sets`, params);
      done.push(`${g.name} (${g.count})`);
      if (!old && r.id) existing.push({ id: r.id, name: g.name });
    } catch (e) { say(`${g.name}: ${e.message}`); }
  }
  say(`${done.length} categorias: ${done.join(", ")}`);
  await db.collection("shop").doc("metaCollections").set({ at: new Date().toISOString(), names: ordered.map((g) => g.name), shops }, { merge: true });
})().catch((e) => { console.log(`::error::${e.message}`); process.exit(1); });
