"use strict";
/* Deletes orders paid in Stripe TEST mode (session ids cs_test_..., or never paid), their print sheets, and resets the
   order counter so the first real order is LHH-1001. Run by .github/workflows/maint.yml (needs functions/node_modules).
   DRY_RUN=1 only lists what it would delete. */
const path = require("path");
const fnRequire = require("module").createRequire(path.join(__dirname, "../../functions/package.json"));
const { initializeApp } = fnRequire("firebase-admin/app");
const { getFirestore } = fnRequire("firebase-admin/firestore");
const { getStorage } = fnRequire("firebase-admin/storage");

const project = process.env.PROJECT || "little-hive-house";
initializeApp({ projectId: project, storageBucket: process.env.BUCKET || `${project}.firebasestorage.app` });
const db = getFirestore();
const dry = process.env.DRY_RUN === "1";

(async () => {
  const snap = await db.collection("orders").get();
  const test = snap.docs.filter((d) => {
    const o = d.data(), s = (o.stripe && o.stripe.sessionId) || "";
    return s.startsWith("cs_test_") || (o.stripe && o.stripe.livemode === false);
  });
  const real = snap.size - test.length;
  console.log(`orders: ${snap.size} total, ${test.length} test, ${real} real`);
  for (const d of test) {
    const o = d.data();
    console.log(`${dry ? "would delete" : "deleting"} ${o.number || "(pending)"} ${d.id} ${o.email || ""}`);
    if (dry) continue;
    await getStorage().bucket().deleteFiles({ prefix: `orders/${d.id}/` }).catch(() => {});
    await d.ref.delete();
  }
  if (!dry && real === 0) {
    await db.collection("meta").doc("counters").set({ orderNumber: 1000 }, { merge: true });
    console.log("order counter reset: the next order will be LHH-1001");
  } else if (real > 0) console.log("real orders exist, so the order counter was left as it is");
  console.log(`::notice title=Test orders::${dry ? "Would delete" : "Deleted"} ${test.length} test order(s); ${real} real order(s) kept`);
})().catch((e) => { console.error(e); console.log(`::error title=clear-test-orders::${String(e && (e.stack || e.message) || e).replace(/\n/g, "%0A").slice(0, 1500)}`); process.exit(1); });
