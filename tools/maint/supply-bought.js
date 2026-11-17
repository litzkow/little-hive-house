"use strict";
/* Does what "Comprei" does in Hive Admin › Materiais for one or more purchases: adds what was bought to the material,
   logs the purchase (the money put into the shop) and keeps the link to buy it again.
   VALUE = JSON list [{"id":"mailers-4","qty":100,"cost":47.98,"store":"Amazon","date":"2026-11-16","item":"...","link":"https://..."}]
   The same date + store + item is never logged twice. Run by .github/workflows/maint.yml (task supply-bought). */
const { Firestore } = require("@google-cloud/firestore");
const deps = require("../../functions/deps");
const S = require("../../functions/supplies");

const db = new Firestore({ projectId: process.env.PROJECT || "little-hive-house", ignoreUndefinedProperties: true });
deps.set({ db });
const DRY = process.env.DRY_RUN === "1";
const ADMIN = { uid: "claude", token: { admin: true, email: "claude" } };

(async () => {
  let list = JSON.parse(process.env.VALUE || "[]");
  if (!Array.isArray(list)) list = [list];
  const v0 = await S.adminSupplies({ action: "list" }, ADMIN);
  for (const p of list) {
    const s = v0.supplies.find((x) => x.id === p.id);
    if (!s) throw new Error(`no material "${p.id}"`);
    const done = await db.collection("purchases").where("date", "==", p.date).get();
    if (done.docs.some((d) => d.data().store === p.store && d.data().item === p.item)) { console.log(`already logged: ${p.item}`); continue; }
    if (DRY) { console.log(`would add ${p.qty} ${s.unit} to "${s.name}" (now ≈${s.left}) and log $${p.cost}`); continue; }
    const v = await S.adminSupplies({ action: "bought", ...p }, ADMIN);
    const after = v.supplies.find((x) => x.id === p.id);
    console.log(`"${after.name}": ≈${after.left} ${after.unit}, link ${after.link ? "saved" : "none"}; logged $${p.cost}; total put in $${v.invested.total}`);
  }
})().catch((e) => { console.error(e.message); process.exit(1); });
