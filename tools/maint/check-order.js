"use strict";
/* Answers yes/no about one order without showing customer data: ORDER = number (LHH-1002), CHECK = found|label|shipped|charged|shippo.
   Exit 0 = yes. Run by .github/workflows/maint.yml (task check-order). */
const { Firestore } = require("@google-cloud/firestore");
const db = new Firestore({ projectId: process.env.PROJECT || "little-hive-house" });
(async () => {
  const num = (process.env.ORDER || "").trim(), check = process.env.CHECK;
  if (check === "shippo") {
    const r = await fetch("https://api.goshippo.com/transactions/?results=10", { headers: { Authorization: `ShippoToken ${(process.env.SHIPPO_API_KEY || "").trim()}` } });
    const j = await r.json().catch(() => ({}));
    const ok = (j.results || []).filter((t) => t.status === "SUCCESS");
    console.log(`Shippo transactions: ${ok.length}`);
    process.exit(ok.length ? 0 : 1);
  }
  let snap = await db.collection("orders").where("number", "==", num).limit(1).get();
  if (snap.empty && /^\d+$/.test(num.replace(/\D/g, ""))) snap = await db.collection("orders").where("number", "==", Number(num.replace(/\D/g, ""))).limit(1).get();
  if (snap.empty) process.exit(check === "found" ? 1 : 1);
  const o = snap.docs[0].data(), f = o.fulfillment || {};
  const yes = { found: true, label: !!(f.label && f.label.tracking), shipped: o.status === "shipped", charged: !!(o.payment && o.payment.state === "captured") }[check];
  process.exit(yes ? 0 : 1);
})().catch((e) => { console.error(e.message); process.exit(1); });
