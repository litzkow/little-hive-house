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
  delete st.interests;                       // look them up fresh
  const t = await A.audience(meta, st);
  say(`interesses: ${(st.interests || []).map((i) => i.name).join(", ") || "nenhum"}`);
  if (st.adsetId) {
    await A.graph(meta, "POST", st.adsetId, { targeting: t });
    st.targetV = A.TARGET_V;
    const now = await A.graph(meta, "GET", st.adsetId, { fields: "targeting,effective_status" });
    say(`no Meta agora: ${JSON.stringify(now).slice(0, 800)}`);
  }
  await sref.set({ interests: st.interests, targetV: st.targetV || null }, { merge: true });
})().catch((e) => { console.log(`::error::${e.message}`); process.exit(1); });
