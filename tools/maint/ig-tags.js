"use strict";
/* Instagram: marcar produtos do catálogo nos posts.
   VALUE vazio ou "list": a conta pode marcar? os posts (tipo, data, legenda, marcações que já têm) e as fotos de cada um em
   ig-out/ (o passo seguinte do workflow as guarda como artefato, para escolher os produtos olhando a foto).
   VALUE "apply": lê tools/maint/ig-tags.json [{media, child?, tags:[{retailer_id, x?, y?}]}] e marca (x/y de 0 a 1, só em fotos).
   Nunca mostra o token. */
const fs = require("fs");
const path = require("path");
const { Firestore } = require("@google-cloud/firestore");
const db = new Firestore({ projectId: process.env.PROJECT || "little-hive-house" });
const say = (s) => console.log(`::warning title=ig::${String(s).replace(/\n/g, " ").slice(0, 950)}`);
const V = "v26.0";
(async () => {
  const meta = ((await db.collection("ads").doc("auth").get()).data() || {}).meta;
  if (!meta || !meta.token) return say("Meta não está conectado");
  const q = (o) => Object.entries(o || {}).map(([k, v]) => `${k}=${encodeURIComponent(typeof v === "string" ? v : JSON.stringify(v))}`).join("&");
  const call = async (method, p, o = {}) => {
    const url = `https://graph.facebook.com/${V}/${p}`;
    const body = q({ ...o, access_token: meta.token });
    const r = method === "GET" ? await fetch(`${url}?${body}`) : await fetch(url, { method, headers: { "content-type": "application/x-www-form-urlencoded" }, body });
    return r.json();
  };
  const mode = (process.env.VALUE || "list").trim();
  const elig = await call("GET", meta.igUserId, { fields: "username,shopping_product_tag_eligibility" });
  say(`conta: ${JSON.stringify(elig)}`);
  const cats = await call("GET", `${meta.igUserId}/available_catalogs`, { fields: "catalog_id,catalog_name,product_count" });
  const catalog = ((cats.data || [])[0] || {}).catalog_id;
  say(`catálogo: ${catalog || "nenhum"}`);

  if (mode === "list") {
    fs.mkdirSync("ig-out", { recursive: true });
    const media = await call("GET", `${meta.igUserId}/media`, { fields: "id,media_type,media_product_type,caption,timestamp,permalink,media_url,thumbnail_url,children{id,media_type,media_url,thumbnail_url}", limit: 50 });
    if (media.error) return say(`erro: ${JSON.stringify(media.error)}`);
    const out = [];
    for (const m of media.data || []) {
      const tags = await call("GET", `${m.id}/product_tags`);
      const kids = (m.children && m.children.data) || [];
      const pics = kids.length ? kids.map((c) => ({ id: c.id, type: c.media_type, url: c.media_url || c.thumbnail_url })) : [{ id: m.id, type: m.media_type, url: m.media_type === "VIDEO" ? m.thumbnail_url : m.media_url }];
      for (const [i, p] of pics.entries()) {
        if (!p.url) continue;
        try { const r = await fetch(p.url); fs.writeFileSync(path.join("ig-out", `${m.id}-${i}.jpg`), Buffer.from(await r.arrayBuffer())); } catch (e) { /* sem foto */ }
      }
      const row = { id: m.id, type: m.media_type, product: m.media_product_type, at: m.timestamp, link: m.permalink, caption: String(m.caption || "").slice(0, 300),
        children: pics.map((p) => ({ id: p.id, type: p.type })), tags: tags.error ? `erro: ${tags.error.message}` : (tags.data || []).map((t) => t.product_name || t.product_id) };
      out.push(row);
      say(`${m.timestamp.slice(0, 10)} ${m.media_type}/${m.media_product_type} ${m.id} · ${pics.length} foto(s) · marcados: ${JSON.stringify(row.tags)} · ${row.caption.slice(0, 120)}`);
    }
    fs.writeFileSync(path.join("ig-out", "posts.json"), JSON.stringify(out, null, 1));
    return;
  }

  if (mode === "apply") {
    const plan = JSON.parse(fs.readFileSync(path.join(__dirname, "ig-tags.json"), "utf8"));
    const ids = {};
    const productId = async (rid) => {
      if (ids[rid]) return ids[rid];
      const r = await call("GET", `${catalog}/products`, { filter: { retailer_id: { eq: rid } }, fields: "id,retailer_id,name" });
      const p = (r.data || [])[0];
      if (!p) throw new Error(`produto ${rid} não está no catálogo`);
      return (ids[rid] = p.id);
    };
    for (const rid of ["photo-pack-4", "christmas-merry-christmas"]) {   // como a Meta vê um produto que falha e um que funciona
      const r = await call("GET", `${catalog}/products`, { filter: { retailer_id: { eq: rid } }, fields: "id,retailer_id,review_status,review_rejection_reasons,visibility,availability,errors,capability_to_review_status,product_type" });
      say(`produto ${rid}: ${JSON.stringify(r.data || r.error).slice(0, 700)}`);
    }
    for (const it of plan) {
      try {
        const tags = [];
        for (const t of it.tags) tags.push({ product_id: await productId(t.retailer_id), ...(t.x !== undefined ? { x: t.x, y: t.y } : {}) });
        const r = await call("POST", `${it.child || it.media}/product_tags`, { updated_tags: tags });
        say(`${it.media}${it.child ? " › " + it.child : ""}: ${r.error ? "ERRO " + JSON.stringify(r.error).slice(0, 600) : "marcado ✓ " + it.tags.map((t) => t.retailer_id).join(", ")}`);
      } catch (e) { say(`${it.media}: ERRO ${e.message}`); }
    }
  }
})().catch((e) => { console.log(`::error::${e.message}`); process.exit(1); });
