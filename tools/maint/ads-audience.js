"use strict";
/* Anúncios: aplica agora o público do robô (só quem mora nos EUA + interesses de presentes, casa e fotos) no conjunto que
   está no ar, em vez de esperar a rodada da manhã. Mostra os interesses encontrados e o público que ficou no Meta. */
const { Firestore } = require("@google-cloud/firestore");
require("../../functions/deps").set({ db: new Firestore({ projectId: process.env.PROJECT || "little-hive-house", ignoreUndefinedProperties: true }) });
const A = require("../../functions/ads")._internal;
const say = (s) => console.log(`::warning title=publico::${String(s).replace(/\n/g, " ").slice(0, 900)}`);
(async () => {
  const db = require("../../functions/deps").db();
  const meta = ((await db.collection("ads").doc("auth").get()).data() || {}).meta;
  const sref = db.collection("ads").doc("state"), st = (await sref.get()).data() || {};
  const th = [...new Set(Object.values(st.boosts || {}).filter((b) => b.status === "active" && b.shared).flatMap((b) => A.themesOf(b.caption)))].sort();
  const t = await A.audience(meta, st, th);
  say(`grupos: ${st.audience.join(", ")} · ${JSON.stringify(t.flexible_spec || []).slice(0, 700)}`);
  if (st.adsetId) {
    await A.graph(meta, "POST", st.adsetId, { targeting: t });
    st.targetV = A.AUDIENCE_V; st.targetKey = st.audience.join(",");
    const now = await A.graph(meta, "GET", st.adsetId, { fields: "targeting,effective_status" });
    say(`no Meta agora: ${JSON.stringify(now).slice(0, 800)}`);
  }
  await sref.set({ audIds: st.audIds || {}, audience: st.audience, targetV: st.targetV || null, targetKey: st.targetKey || null }, { merge: true });
})().catch((e) => { console.log(`::error::${e.message}`); process.exit(1); });
