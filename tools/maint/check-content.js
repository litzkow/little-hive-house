"use strict";
/* Conteúdo: what the Hive Admin's Content page has right now, after a forced Meta sync (functions/content.js, the same code).
   Prints the sync result and every post that came from Meta or is scheduled/posted, as annotations on the run page. */
const { Firestore } = require("@google-cloud/firestore");
require("../../functions/deps").set({ db: new Firestore({ projectId: process.env.PROJECT || "little-hive-house", ignoreUndefinedProperties: true }) });
const C = require("../../functions/content");
const say = (s) => console.log(`::warning title=conteudo::${String(s).replace(/%/g, "%25").replace(/\n/g, " | ").slice(0, 1800)}`);
(async () => {
  const sync = await C.syncMeta({ force: true });
  say(`sync: ${JSON.stringify(sync)}`);
  const q = await require("../../functions/deps").db().collection("content").get();
  const all = q.docs.map((d) => ({ id: d.id, ...d.data() }));
  const by = {};
  for (const i of all) { const k = `${i.source}/${i.status}/${(i.files || []).length ? "arquivo" : "sem-arquivo"}`; by[k] = (by[k] || 0) + 1; }
  say(`total ${all.length}: ${JSON.stringify(by)}`);
  all.filter((i) => process.env.ALL || i.source !== "plan" || ["scheduled", "posted"].includes(i.status) || (i.files || []).length)
    .sort((a, b) => String(a.date).localeCompare(String(b.date)))
    .forEach((i) => say(`${i.id} ${i.date} ${i.time || ""} [${i.source}/${i.status}/${i.kind}] por ${i.byName || i.by || "-"} em ${String(i.at || "").slice(0, 10)} (${(i.files || []).length} arq) ${i.title} | nets ${JSON.stringify(i.nets)} posted ${JSON.stringify(i.posted)} | ig ${i.igId || "-"} fbSched ${i.fbScheduledId || "-"} fbPost ${i.fbPostId || "-"} | prev ${i.preview ? "sim" : "não"} | ${String(i.caption || "").slice(0, 90)}`));
})().catch((e) => { say(`erro: ${e.message}`); process.exit(1); });
