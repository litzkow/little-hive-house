"use strict";
/* Read-only look at what customers ran into, without personal data: the latest problem reports (clientErrors),
   the photo uploads of the last HOURS hours grouped by pack (how many photos made it, sizes, types) and the orders of
   that window (number, status, payment state, photo count). Run by .github/workflows/maint.yml (task client-errors). */
const { Firestore } = require("@google-cloud/firestore");
const { Storage } = require("@google-cloud/storage");
const PROJECT = process.env.PROJECT || "little-hive-house";
const HOURS = Number(process.env.HOURS || 24);
const db = new Firestore({ projectId: PROJECT });
const since = Date.now() - HOURS * 3600e3;
const short = (ua) => String(ua || "").replace(/Mozilla\/5\.0 /, "").replace(/AppleWebKit\/[\d.]+ \(KHTML, like Gecko\) /, "").slice(0, 140);
(async () => {
  console.log(`== problem reports (last ${HOURS} h)`);
  const errs = await db.collection("clientErrors").orderBy("at", "desc").limit(40).get();
  errs.docs.map((d) => d.data()).filter((e) => Date.parse(e.at) >= since).forEach((e) =>
    console.log([e.at, e.kind, e.code, `photos=${e.photos}`, e.lang, (e.page || "").split("?")[0], `| ${e.msg}`, `| ${short(e.ua)}`].join("  ")));

  console.log(`\n== photo uploads (last ${HOURS} h), one line per pack`);
  const [bucketName] = [process.env.BUCKET || `${PROJECT}.firebasestorage.app`];
  const bucket = new Storage({ projectId: PROJECT }).bucket(bucketName);
  const [files] = await bucket.getFiles({ prefix: "uploads/" });
  const packs = {};
  for (const f of files) {
    const m = f.metadata, t = Date.parse(m.timeCreated);
    if (t < since) continue;
    const parts = f.name.split("/"), key = parts.slice(0, 3).join("/");
    const p = packs[key] || (packs[key] = { n: 0, bytes: 0, types: {}, first: t, last: t, names: [] });
    p.n++; p.bytes += Number(m.size); p.types[m.contentType] = (p.types[m.contentType] || 0) + 1;
    p.first = Math.min(p.first, t); p.last = Math.max(p.last, t); p.names.push(parts[3]);
  }
  Object.entries(packs).sort((a, b) => a[1].first - b[1].first).forEach(([k, p]) => {
    const anon = k.split("/")[1].slice(0, 6) + "…";
    console.log([new Date(p.first).toISOString(), `user ${anon}`, k.split("/")[2], `${p.n} photos`, `${(p.bytes / 1e6).toFixed(1)} MB`,
      JSON.stringify(p.types), `files ${p.names.sort((a, b) => parseInt(a) - parseInt(b)).join(",")}`, `${Math.round((p.last - p.first) / 1000)} s`].join("  "));
  });

  console.log(`\n== orders (last ${HOURS} h)`);
  const os = await db.collection("orders").orderBy("createdAt", "desc").limit(30).get().catch(() => ({ docs: [] }));
  os.docs.map((d) => d.data()).filter((o) => Date.parse(o.createdAt) >= since).forEach((o) => {
    const photos = (o.items || []).filter((i) => i.kind === "photos").reduce((n, i) => n + ((i.photos || []).length), 0);
    console.log([o.createdAt, o.number || "(no number yet)", o.status, o.payment && o.payment.state, `photos=${photos}`, o.lang || ""].join("  "));
  });
})().catch((e) => { console.error(e.message); process.exit(1); });
