"use strict";
/* Grava o endereço de remetente das etiquetas (settings/store shipFrom) sem abrir o Hive Admin.
   VALUE = JSON {name, street1, street2, city, state, zip}. DRY_RUN=1 só mostra. Rodado por .github/workflows/maint.yml (task set-ship-from). */
process.on("uncaughtException", (e) => { console.log(`::error title=set-ship-from::${String(e && (e.stack || e.message) || e).replace(/\n/g, "%0A").slice(0, 1500)}`); process.exit(1); });
const { Firestore } = require("@google-cloud/firestore");

const db = new Firestore({ projectId: process.env.PROJECT || "little-hive-house" });
const dry = process.env.DRY_RUN === "1";
const t = (v, n) => (typeof v === "string" ? v.trim().slice(0, n) : "");

(async () => {
  const a = JSON.parse(process.env.VALUE || "{}");
  const sf = { name: t(a.name, 60) || "Little Hive House", company: t(a.company, 60), street1: t(a.street1, 80), street2: t(a.street2, 80),
    city: t(a.city, 50), state: t(a.state, 20).toUpperCase(), zip: t(a.zip, 10), phone: t(a.phone, 20) };
  if (!sf.street1 || !sf.city || !/^[A-Z]{2}$/.test(sf.state) || !/^\d{5}(-\d{4})?$/.test(sf.zip)) throw new Error("endereço incompleto");
  console.log(`shipFrom -> ${sf.city}, ${sf.state} ${sf.zip}${dry ? " (dry run)" : ""}`);
  if (!dry) await db.collection("settings").doc("store").set({ shipFrom: sf, updatedAt: new Date().toISOString() }, { merge: true });
})();
