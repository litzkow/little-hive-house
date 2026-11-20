"use strict";
/* Loja do Meta: catálogo, arquivo de produtos, conjuntos de produtos e a configuração da loja (para organizar as categorias). */
const { Firestore } = require("@google-cloud/firestore");
const db = new Firestore({ projectId: process.env.PROJECT || "little-hive-house" });
const say = (s) => console.log(`::warning title=loja::${String(s).replace(/\n/g, " ").slice(0, 950)}`);
(async () => {
  const meta = ((await db.collection("ads").doc("auth").get()).data() || {}).meta;
  const V = "v26.0";
  const get = async (path, q = "") => { const r = await fetch(`https://graph.facebook.com/${V}/${path}${path.includes("?") ? "&" : "?"}${q}&access_token=${encodeURIComponent(meta.token)}`); return r.json(); };
  const page = await get(meta.pageId, "fields=name,commerce_merchant_settings{id,display_name,shops,cta,commerce_store}");
  say(`página: ${JSON.stringify(page).slice(0, 900)}`);
  const biz = await get("me", "fields=id,name");
  say(`token: ${JSON.stringify(biz)}`);
  const ig = await get(meta.igUserId, "fields=username,shopping_product_tag_eligibility,shopping_review_status");
  say(`ig: ${JSON.stringify(ig)}`);
  const cats = await get(`${meta.igUserId}/available_catalogs`, "fields=catalog_id,catalog_name,product_count");
  say(`catálogos do ig: ${JSON.stringify(cats).slice(0, 600)}`);
  const bizs = await get("me/businesses", "fields=id,name,owned_product_catalogs{id,name,product_count,vertical}");
  say(`empresas: ${JSON.stringify(bizs).slice(0, 900)}`);
  const acc = await get(meta.adAccountId, "fields=business{id,name}");
  say(`conta: ${JSON.stringify(acc)}`);
  const bid = acc.business && acc.business.id;
  let cid = (((cats.data || [])[0]) || {}).catalog_id || (process.env.VALUE || "").trim();
  if (bid) {
    const own = await get(`${bid}/owned_product_catalogs`, "fields=id,name,product_count,vertical");
    say(`catálogos da empresa: ${JSON.stringify(own).slice(0, 600)}`);
    cid = cid || (((own.data || [])[0]) || {}).id;
    const shops = await get(`${bid}/commerce_merchant_settings`, "fields=id,display_name");
    say(`lojas da empresa: ${JSON.stringify(shops).slice(0, 400)}`);
  }
  if (cid) {
    say(`feeds: ${JSON.stringify(await get(`${cid}/product_feeds`, "fields=id,name,schedule,latest_upload{end_time,error_count,warning_count},product_count")).slice(0, 900)}`);
    say(`conjuntos: ${JSON.stringify(await get(`${cid}/product_sets`, "fields=id,name,product_count,filter&limit=50")).slice(0, 950)}`);
    const p = await get(`${cid}/products`, "fields=retailer_id,name,product_type,custom_label_0,image_url,review_status,visibility&limit=5");
    say(`produtos: ${JSON.stringify(p).slice(0, 950)}`);
  }
  const cms = page.commerce_merchant_settings && page.commerce_merchant_settings.id;
  if (cms) {
    for (const e of ["shops", "product_catalogs", "onsite_conflicts", "setup_status", "shop_setup_status"]) say(`cms ${e}: ${JSON.stringify(await get(`${cms}/${e}`)).slice(0, 600)}`);
  }
})().catch((e) => { console.log(`::error::${e.message}`); process.exit(1); });
