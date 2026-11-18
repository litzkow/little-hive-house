"use strict";
/* Anúncios: pauses every active boost now and turns the robot's own choosing off (the owners choose). Prints what it did. */
const { Firestore } = require("@google-cloud/firestore");
require("../../functions/deps").set({ db: new Firestore({ projectId: process.env.PROJECT || "little-hive-house", ignoreUndefinedProperties: true }) });
const G = require("../../functions/ads")._internal.graph;
const say = (s) => console.log(`::warning title=anuncios::${String(s).replace(/\n/g, " ").slice(0, 900)}`);
(async () => {
  const db = require("../../functions/deps").db();
  const meta = ((await db.collection("ads").doc("auth").get()).data() || {}).meta;
  const sref = db.collection("ads").doc("state"), st = (await sref.get()).data() || {};
  for (const b of Object.values(st.boosts || {})) {
    if (b.status !== "active") continue;
    await G(meta, "POST", b.adsetId, { status: "PAUSED" });
    b.status = "paused"; b.why = "owner"; b.pausedAt = new Date().toISOString();
    say(`pausado: ${b.id} (${String(b.caption || "").slice(0, 40)})`);
  }
  await sref.set(st);
  await db.collection("ads").doc("config").set({ auto: false }, { merge: true });
  await db.collection("adsLog").add({ at: new Date().toISOString(), channel: "meta", kind: "pause", pt: "Impulso pausado a pedido de vocês; nada novo começa sozinho.", en: "Boost paused at your request; nothing new starts by itself." });
  say("escolha automática desligada");
})().catch((e) => { say(`erro: ${e.message}`); process.exit(1); });
