"use strict";
/* Conteúdo: the edited videos put in by import-content (sent as "Claude") become Thiago's, and each keeps only the
   version with music (the copy without music is deleted from Storage too). Notes say which song it is. */
const { Firestore } = require("@google-cloud/firestore");
const { Storage } = require("@google-cloud/storage");
const PROJECT = process.env.PROJECT || "little-hive-house";
const db = new Firestore({ projectId: PROJECT, ignoreUndefinedProperties: true });
const bucket = new Storage({ projectId: PROJECT }).bucket(process.env.BUCKET || `${PROJECT}.firebasestorage.app`);
const say = (s) => console.log(`::warning title=conteudo::${String(s).replace(/\n/g, " | ").slice(0, 1800)}`);
const SONG = {
  "Papai Noel saindo da prensa": "All I Want for Christmas Is You (Mariah Carey)",
  "Cortador: oddly satisfying": "trilha original (feita para a loja, sem problema de direitos)",
  "Do celular para a geladeira": "Come Around and Love Me (Jalen Ngonda)",
  "Expectativa × realidade": "NISSAN ALTIMA (Doechii)",
  "Feito por nós dois": "Dark Red (Steve Lacy)",
  "Ideia de presente": "Lovewave",
};
(async () => {
  const q = await db.collection("content").where("byName", "==", "Claude").get();
  for (const d of q.docs) {
    const it = d.data();
    let files = it.files || [];
    const withMusic = files.filter((f) => /previa-com-musica|02-cortador/.test(f.name));
    for (const f of files.filter((x) => !withMusic.includes(x))) { try { await bucket.file(f.path).delete(); } catch (e) { /* gone */ } }
    files = (withMusic.length ? withMusic : files).map((f) => ({ ...f, by: "Thiago", byName: "Thiago",
      name: f.name.replace(/-(previa-com-musica|para-postar)/, "") }));
    const song = SONG[it.title];
    const notes = song ? `Música: ${song}.` + (/original/.test(song) ? "" : " Se o Instagram reclamar de direitos autorais, poste sem som e escolha a mesma música em Áudio.") : it.notes;
    await d.ref.set({ files, by: "Thiago", byName: "Thiago", notes }, { merge: true });
    say(`${it.title}: ${files.length} arquivo, de Thiago`);
  }
  if (!q.size) say("nada para mudar");
})().catch((e) => { say(`erro: ${e.message}`); process.exit(1); });
