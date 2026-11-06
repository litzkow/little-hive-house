"use strict";
/* Logs one purchase in Hive Admin › Materiais › Compras (the money put into the shop), like the "purchase" action there.
   VALUE = JSON {"date":"2026-11-05","store":"Etsy","item":"Taxa de abertura da loja no Etsy","cost":29}.
   The same date + store + item is never logged twice. Run by .github/workflows/maint.yml (task add-purchase). */
const { Firestore } = require("@google-cloud/firestore");
const db = new Firestore({ projectId: process.env.PROJECT || "little-hive-house" });
const DRY = process.env.DRY_RUN === "1";

(async () => {
  const p = JSON.parse(process.env.VALUE || "{}");
  const cost = Math.round(Number(p.cost) * 100) / 100;
  if (!/^\d{4}-\d{2}-\d{2}$/.test(p.date || "") || !p.item || !(cost > 0)) throw new Error('VALUE must be {"date":"YYYY-MM-DD","store":"...","item":"...","cost":12.34}');
  const row = { date: p.date, store: String(p.store || "").slice(0, 60), item: String(p.item).slice(0, 200), cost, supplyId: "", qty: 0, by: "claude", createdAt: new Date().toISOString() };
  const all = await db.collection("purchases").get();
  if (all.docs.some((d) => { const x = d.data(); return x.date === row.date && x.store === row.store && x.item === row.item; })) { console.log("already logged"); return; }
  const total = Math.round((all.docs.reduce((t, d) => t + (Number(d.data().cost) || 0), 0) + cost) * 100) / 100;
  if (DRY) { console.log(`would log $${cost}; total would be $${total}`); return; }
  await db.collection("purchases").add(row);
  await db.collection("settings").doc("store").set({ purchasesTotal: total }, { merge: true });
  console.log(`logged $${cost}; purchases total $${total}`);
})().catch((e) => { console.error(e.message); process.exit(1); });
