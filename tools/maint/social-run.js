"use strict";
/* Instagram & Facebook: roda o socialSync agora (o mesmo de 10 em 10 minutos) e mostra o que tem: marcações e comentários. */
const { Firestore } = require("@google-cloud/firestore");
require("../../functions/deps").set({ db: new Firestore({ projectId: process.env.PROJECT || "little-hive-house", ignoreUndefinedProperties: true }) });
const say = (s) => console.log(`::warning title=social::${String(s).replace(/\n/g, " ").slice(0, 900)}`);
(async () => {
  const db = require("../../functions/deps").db();
  const r = await require("../../functions/social").socialSync();
  say(`rodada: ${JSON.stringify(r)}`);
  for (const d of (await db.collection("socialTags").get()).docs) {
    const t = d.data();
    say(`marcação ${d.id} ${t.status} · ${t.source} · feitos ${(t.done || []).length}/${(t.plan || []).reduce((a, p) => a + p.tags.length, 0)}${t.error ? " · " + t.error : ""} · ${String(t.caption || "").slice(0, 50)}`);
  }
  for (const d of (await db.collection("social").get()).docs) {
    const m = d.data();
    say(`${m.net}/${m.kind} ${m.status} · ${m.user}: ${String(m.text).slice(0, 80)}${m.reply ? " → " + m.reply.text.slice(0, 80) : ""}${m.autoError ? " · erro " + m.autoError : ""}`);
  }
})().catch((e) => { say(`erro: ${e.message}`); process.exit(1); });
