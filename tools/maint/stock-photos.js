/* Fotos de banco gratuito para os exemplos do site (licença Unsplash ou CC0, uso comercial livre).
   QUERIES (JSON: {"pasta": "busca", ...}) e PER (quantas por busca). Salva em OUT/<pasta>/<id>.jpg e OUT/credits.json.
   Só fotos grátis: pula Unsplash+ (premium/plus). Se o Unsplash recusar, usa o Openverse (só CC0 e domínio público). */
"use strict";
const fs = require("fs"), path = require("path");
const OUT = process.env.OUT || "/tmp/stock";
const PER = +(process.env.PER || 12);
const Q = JSON.parse(process.env.QUERIES);
const KEY = process.env.PEXELS_API_KEY || "";
const PIX = process.env.PIXABAY_API_KEY || "";
const UA = { "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36", Accept: "application/json" };
const credits = [];
async function json(u) { const r = await fetch(u, { headers: UA }); if (!r.ok) throw new Error(r.status + " " + u); return r.json(); }
async function save(file, url) {
  const r = await fetch(url, { headers: { "User-Agent": UA["User-Agent"] } });
  if (!r.ok) throw new Error(r.status);
  fs.writeFileSync(file, Buffer.from(await r.arrayBuffer()));
}
(async () => {
  for (const [dir, q] of Object.entries(Q)) {
    fs.mkdirSync(path.join(OUT, dir), { recursive: true });
    let got = 0, src = "pexels";
    /* a list of Pexels photo ids: straight from the Pexels image server (Pexels License, free for commercial use) */
    if (Array.isArray(q)) {
      for (const id of q) {
        try { await save(path.join(OUT, dir, "p-" + id + ".jpg"), `https://images.pexels.com/photos/${id}/pexels-photo-${id}.jpeg?auto=compress&cs=tinysrgb&w=1400`); got++;
          credits.push({ dir, file: "p-" + id + ".jpg", source: "Pexels", license: "Pexels License", link: `https://www.pexels.com/photo/${id}/` }); } catch (e) { console.log(`::warning::${id}: ${e.message}`); }
      }
      console.log(`::notice::${dir}: ${got} fotos (pexels ids)`);
      continue;
    }
    /* a search on Pixabay (secret PIXABAY_API_KEY; Pixabay Content License, free for commercial use) */
    if (PIX) {
      try {
        const j = await json(`https://pixabay.com/api/?key=${PIX}&q=${encodeURIComponent(q)}&image_type=photo&safesearch=true&per_page=${Math.min(200, Math.max(PER * 2, 20))}&order=popular`);
        for (const p of j.hits || []) {
          if (got >= PER) break;
          if ((p.imageWidth || 0) < 1200) continue;
          const id = "x-" + p.id, file = path.join(OUT, dir, id + ".jpg");
          try { await save(file, p.largeImageURL); } catch (e) { continue; }
          credits.push({ dir, file: id + ".jpg", source: "Pixabay", license: "Pixabay Content License", by: p.user, link: p.pageURL, alt: p.tags });
          got++;
        }
      } catch (e) { console.log(`::warning::Pixabay ${q}: ${e.message}`); }
      if (got >= PER) { console.log(`::notice::${dir}: ${got} fotos (pixabay)`); continue; }
    }
    /* a search, with the Pexels key (secret PEXELS_API_KEY) */
    if (KEY) {
      try {
        const r = await fetch(`https://api.pexels.com/v1/search?query=${encodeURIComponent(q)}&per_page=${Math.min(80, PER * 2)}`, { headers: { Authorization: KEY } });
        const j = await r.json();
        for (const p of j.photos || []) {
          if (got >= PER) break;
          const id = "p-" + p.id, file = path.join(OUT, dir, id + ".jpg");
          try { await save(file, p.src.large2x || p.src.original); } catch (e) { continue; }
          credits.push({ dir, file: id + ".jpg", source: "Pexels", license: "Pexels License", by: p.photographer, link: p.url, alt: p.alt });
          got++;
        }
      } catch (e) { console.log(`::warning::Pexels ${q}: ${e.message}`); }
      if (got >= PER) { console.log(`::notice::${dir}: ${got} fotos (pexels)`); continue; }
    }
    src = "unsplash";
    try {
      for (let page = 1; page <= 3 && got < PER; page++) {
        const j = await json(`https://unsplash.com/napi/search/photos?query=${encodeURIComponent(q)}&per_page=30&page=${page}`);
        for (const p of j.results || []) {
          if (got >= PER) break;
          if (p.premium || p.plus || (p.sponsorship) ) continue;
          const id = "u-" + p.id, file = path.join(OUT, dir, id + ".jpg");
          try { await save(file, p.urls.raw + "&w=1400&q=82&fm=jpg&fit=max"); } catch (e) { continue; }
          credits.push({ dir, file: id + ".jpg", source: "Unsplash", license: "Unsplash License", by: p.user && p.user.name, link: p.links && p.links.html, alt: p.alt_description });
          got++;
        }
      }
    } catch (e) { console.log(`::warning::Unsplash ${q}: ${e.message}`); }
    if (got < PER) {
      src = "openverse";
      try {
        const j = await json(`https://api.openverse.org/v1/images/?q=${encodeURIComponent(q)}&license=cc0,pdm&page_size=40&mature=false`);
        for (const p of j.results || []) {
          if (got >= PER) break;
          if ((p.width || 0) < 900) continue;
          const id = "o-" + p.id.slice(0, 8), file = path.join(OUT, dir, id + ".jpg");
          try { await save(file, p.url); } catch (e) { continue; }
          credits.push({ dir, file: id + ".jpg", source: p.source, license: p.license, by: p.creator, link: p.foreign_landing_url, alt: p.title });
          got++;
        }
      } catch (e) { console.log(`::warning::Openverse ${q}: ${e.message}`); }
    }
    console.log(`::notice::${dir}: ${got} fotos (${src})`);
  }
  fs.writeFileSync(path.join(OUT, "credits.json"), JSON.stringify(credits, null, 1));
})();
