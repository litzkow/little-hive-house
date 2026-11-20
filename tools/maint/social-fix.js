"use strict";
/* Instagram & Facebook: desliga as respostas automáticas e apaga as que já foram publicadas (comentários). */
const { Firestore } = require("@google-cloud/firestore");
require("../../functions/deps").set({ db: new Firestore({ projectId: process.env.PROJECT || "little-hive-house", ignoreUndefinedProperties: true }) });
const say = (s) => console.log(`::warning title=social::${String(s).replace(/\n/g, " ").slice(0, 900)}`);
(async () => {
  const db = require("../../functions/deps").db();
  await db.collection("settings").doc("social").set({ autoReply: false }, { merge: true });
  say("respostas automáticas DESLIGADAS");
  const G = require("../../functions/ads")._internal.graph;
  const meta = ((await db.collection("ads").doc("auth").get()).data() || {}).meta;
  const me = String(meta.igUsername || "").toLowerCase();
  let page = null;
  const snap = await db.collection("social").where("status", "==", "auto").get();
  for (const d of snap.docs) {
    const m = d.data();
    try {
      if (m.kind === "dm") { say(`Direct para ${m.user}: a Meta não deixa apagar mensagem enviada (${m.reply && m.reply.text})`); await d.ref.update({ status: "new", reply: null }); continue; }
      let gone = 0;
      if (m.net === "facebook") {
        if (!page) { const p = await G(meta, "GET", meta.pageId, { fields: "access_token" }); page = { token: p.access_token, appSecret: meta.appSecret }; }
        const rs = ((await G(page, "GET", `${m.id}/comments`, { fields: "id,from,message" })).data) || [];
        for (const r of rs) if (r.from && String(r.from.id) === String(meta.pageId)) { await G(page, "DELETE", r.id); gone++; }
      } else {
        const rs = ((await G(meta, "GET", `${m.id}/replies`, { fields: "id,username,text" })).data) || [];
        for (const r of rs) if (String(r.username || "").toLowerCase() === me) { await G(meta, "DELETE", r.id); gone++; }
      }
      await d.ref.update({ status: "new", reply: null });
      say(`${m.net} · ${m.user}: ${gone} resposta(s) apagada(s)`);
    } catch (e) { say(`${m.net} · ${m.user}: não deu para apagar (${e.message})`); }
  }
  if (snap.empty) say("nenhuma resposta automática encontrada");
})().catch((e) => { say(`erro: ${e.message}`); process.exit(1); });
