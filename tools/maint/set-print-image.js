"use strict";
/* Muda o tamanho da imagem impressa nos ímãs (settings/store printImageIn) e, com CUT, o tamanho do pedaço que o furador
   corta (printCutIn), em polegadas, sem precisar abrir o Hive Admin. VALUE=2.02 (padrão). DRY_RUN=1 só mostra o que mudaria. Rodado por .github/workflows/maint.yml (task set-print-image). */
process.on("uncaughtException", (e) => { console.log(`::error title=set-print-image::${String(e && (e.stack || e.message) || e).replace(/\n/g, "%0A").slice(0, 1500)}`); process.exit(1); });
const { Firestore } = require("@google-cloud/firestore");

const project = process.env.PROJECT || "little-hive-house";
const db = new Firestore({ projectId: project });
const dry = process.env.DRY_RUN === "1";
const value = Number(process.env.VALUE || "2.02");
const cut = process.env.CUT ? Number(process.env.CUT) : null;

(async () => {
  if (!Number.isFinite(value) || value < 2 || value > 2.3) throw new Error(`VALUE ${process.env.VALUE} fora de 2.00 a 2.30`);
  if (cut !== null && (!Number.isFinite(cut) || cut < 2.1 || cut > 2.95)) throw new Error(`CUT ${process.env.CUT} fora de 2.10 a 2.95`);
  const ref = db.collection("settings").doc("store");
  const snap = await ref.get();
  const before = snap.exists ? snap.data().printImageIn : undefined;
  console.log(`printImageIn: ${before === undefined ? "(não salvo)" : before} -> ${value}${dry ? " (dry run)" : ""}`);
  const patch = { printImageIn: value, updatedAt: new Date().toISOString() };
  if (cut !== null) { console.log(`printCutIn: ${snap.exists ? snap.data().printCutIn : "(não salvo)"} -> ${cut}`); patch.printCutIn = cut; }
  if (!dry) await ref.set(patch, { merge: true });
  // os PDFs de pedidos já feitos são refeitos com o tamanho novo quando abertos
  const orders = await db.collection("orders").where("printSheet.v", "==", 3).get();
  let n = 0;
  for (const d of orders.docs) {
    const ps = d.data().printSheet || {};
    if (ps.image === value && (cut === null || ps.cut === cut)) continue;
    n++;
    if (!dry) await d.ref.update({ "printSheet.v": 2 });
  }
  console.log(`${n} pedido(s) com PDF antigo ${dry ? "seriam" : "serão"} refeitos quando abertos`);
})();
