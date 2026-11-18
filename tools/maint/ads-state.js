"use strict";
/* Anúncios: the robot's last run, its boosts and the newest lines of its log (no customer data). */
const { Firestore } = require("@google-cloud/firestore");
const db = new Firestore({ projectId: process.env.PROJECT || "little-hive-house" });
const say = (s) => console.log(`::warning title=anuncios::${String(s).replace(/\n/g, " ").slice(0, 900)}`);
(async () => {
  const st = (await db.collection("ads").doc("state").get()).data() || {};
  const r = st.lastRun || {};
  say(`última rodada: ${r.at} por ${r.by} · erros: ${JSON.stringify(r.errors || {})}`);
  Object.entries(st.boosts || {}).forEach(([id, b]) => say(`impulso ${id}: ${b.status || ""} · $${b.daily || 0}/dia · gasto $${b.spend || 0} · ${b.why || ""} ${b.err || ""}`));
  const log = (st.log || []).slice(-6);
  log.forEach((l) => say(`${l.at} · ${l.pt || l.en || ""}`));
})().catch((e) => { console.log(`::error::${e.message}`); process.exit(1); });
