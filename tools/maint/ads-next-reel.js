"use strict";
/* Anúncios: liga o robô (escolhe e troca sozinho) e marca o próximo Reel que sair depois de VALUE (ISO; vazio = agora)
   como o primeiro a impulsionar. O agendador de 5 minutos impulsiona assim que o Reel aparecer no Instagram. */
const { Firestore } = require("@google-cloud/firestore");
const db = new Firestore({ projectId: process.env.PROJECT || "little-hive-house" });
const say = (s) => console.log(`::warning title=anuncios::${String(s).replace(/\n/g, " ").slice(0, 900)}`);
(async () => {
  const v = String(process.env.VALUE || "").trim();
  const after = v && !isNaN(Date.parse(v)) ? new Date(Date.parse(v)).toISOString() : new Date().toISOString();
  const at = new Date().toISOString();
  await db.collection("ads").doc("config").set({ auto: true }, { merge: true });
  await db.collection("ads").doc("state").set({ nextReel: { after, by: "Thiago", at } }, { merge: true });
  await db.collection("adsLog").add({ at, channel: "meta", kind: "next", by: "Thiago",
    pt: "O robô voltou a escolher sozinho, e o próximo Reel que sair vai ser impulsionado primeiro, assim que sair.",
    en: "The robot chooses again by itself, and the next Reel is boosted first, as soon as it's out." });
  const st = (await db.collection("ads").doc("state").get()).data() || {};
  say(`automático ligado · próximo Reel depois de ${after}`);
  Object.entries(st.boosts || {}).forEach(([id, b]) => say(`impulso ${id}: ${b.status || ""} · ${b.why || ""} · ${b.caption ? String(b.caption).slice(0, 30) : ""}`));
})().catch((e) => { console.log(`::error::${e.message}`); process.exit(1); });
