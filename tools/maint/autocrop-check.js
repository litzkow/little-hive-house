"use strict";
/* Turns on Cloud Vision for the project (done by the workflow step) and tries functions/autocrop.js on one order
   WITHOUT saving: prints, per photo, the faces Vision found and the crop the automatic framing would pick, next to
   the crop the order has now. Numbers only. ORDER = LHH-1003. Run by .github/workflows/maint.yml (task autocrop-check). */
const path = require("path");
const { Firestore } = require("@google-cloud/firestore");
const { Storage } = require("@google-cloud/storage");
const sharp = require("sharp");
const A = require(path.join(__dirname, "../../functions/autocrop.js"));
const catalog = require(path.join(__dirname, "../../functions/catalog.json"));
const PROJECT = process.env.PROJECT || "little-hive-house";
const db = new Firestore({ projectId: PROJECT });
const bucket = new Storage({ projectId: PROJECT }).bucket(process.env.BUCKET || `${PROJECT}.firebasestorage.app`);
(async () => {
  const num = (process.env.ORDER || "").trim();
  const snap = await db.collection("orders").where("number", "==", num).limit(1).get();
  if (snap.empty) throw new Error(`order ${num} not found`);
  const o = snap.docs[0].data();
  let n = 0;
  for (const it of o.items || []) {
    if (it.kind !== "photos") continue;
    for (const p of it.photos || []) {
      n++;
      const [buf] = await bucket.file(p.path).download();
      const { data, info } = await sharp(buf, { failOn: "none" }).rotate().resize({ width: 1600, height: 1600, fit: "inside", withoutEnlargement: true })
        .jpeg({ quality: 85 }).toBuffer({ resolveWithObject: true });
      const faces = await A.findFaces({ buffer: data, width: info.width, height: info.height }, process.env.TOKEN);
      const win = (catalog.frames[p.frame] || {}).window || [0, 0, 600, 600];
      const auto = A.pick(info.width, info.height, win, faces);
      console.log(`photo ${n}: ${info.width}x${info.height}, ${faces.length} face(s) ${faces.map((f) => `[${f.x.toFixed(2)},${f.y.toFixed(2)} ${f.w.toFixed(2)}x${f.h.toFixed(2)}]`).join(" ")}; now ${JSON.stringify(p.crop || null)}; automatic ${JSON.stringify(auto)}`);
    }
  }
})().catch((e) => { console.error(e.message); process.exit(1); });
