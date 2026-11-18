"use strict";
/* Conteúdo: puts the day and time from the Business Suite Planner on the scheduled posts (Meta doesn't give them).
   VALUE = "start of caption=YYYY-MM-DD HH:MM;start of caption=YYYY-MM-DD HH:MM" (New York time). */
const { Firestore } = require("@google-cloud/firestore");
const db = new Firestore({ projectId: process.env.PROJECT || "little-hive-house", ignoreUndefinedProperties: true });
const say = (s) => console.log(`::warning title=conteudo::${String(s).replace(/\n/g, " | ").slice(0, 1800)}`);
const norm = (s) => String(s || "").toLowerCase().replace(/\s+/g, " ").trim();
(async () => {
  const pairs = String(process.env.VALUE || "").split(";").map((x) => x.split("=")).filter((p) => p.length === 2);
  if (!pairs.length) { console.log("::error::VALUE vazio"); process.exit(1); }
  const q = await db.collection("content").get();
  const docs = q.docs.filter((d) => d.data().status === "scheduled");
  for (const [start, when] of pairs) {
    const m = when.trim().match(/^(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2})$/);
    if (!m) { say(`${start}: data inválida (${when})`); continue; }
    const hit = docs.filter((d) => norm(d.data().caption).startsWith(norm(start)));
    if (hit.length !== 1) { say(`${start}: achei ${hit.length} posts, não mudei nada`); continue; }
    await hit[0].ref.set({ date: m[1], time: m[2], updatedAt: new Date().toISOString(), updatedBy: "Thiago" }, { merge: true });
    say(`${hit[0].data().title}: sai ${m[1]} às ${m[2]}`);
  }
})().catch((e) => { console.log(`::error::${e.message}`); process.exit(1); });
