"use strict";
/* Conteúdo: puts edited videos into the Hive Admin's Content page (Compartilhados), as if sent in the app.
   DIR has manifest.json ([{title, notes, caption, order, files: [{file, w, h, dur, size}]}]) and the video files.
   Each file goes to Storage as it is (content/{id}/{time}-{name}); each entry becomes one post, status "ready".
   Prints one annotation per post. */
const fs = require("fs");
const path = require("path");
const { Firestore } = require("@google-cloud/firestore");
const { Storage } = require("@google-cloud/storage");
const PROJECT = process.env.PROJECT || "little-hive-house";
const db = new Firestore({ projectId: PROJECT, ignoreUndefinedProperties: true });
const bucket = new Storage({ projectId: PROJECT }).bucket(process.env.BUCKET || `${PROJECT}.firebasestorage.app`);
const DIR = process.env.DIR;
const say = (s) => console.log(`::warning title=conteudo::${String(s).replace(/%/g, "%25").replace(/\n/g, " | ").slice(0, 1800)}`);
(async () => {
  const man = JSON.parse(fs.readFileSync(path.join(DIR, "manifest.json"), "utf8"));
  const base = Date.now();
  for (const m of man) {
    const ref = db.collection("content").doc();
    const at = new Date(base - (m.order || 0) * 60000).toISOString();     // the first one shows on top
    const files = [];
    for (const f of m.files) {
      const dest = `content/${ref.id}/${base}-${f.file}`;
      await bucket.upload(path.join(DIR, f.file), { destination: dest, resumable: true, metadata: { contentType: "video/mp4", metadata: { name: f.file, firebaseStorageDownloadTokens: require("crypto").randomUUID() } } });
      files.push({ path: dest, name: f.file, type: "video/mp4", size: f.size, w: f.w, h: f.h, dur: f.dur, at, by: "Claude", byName: "Claude" });
    }
    await ref.set({
      title: m.title, kind: "video", status: "ready", date: "", time: "", caption: m.caption || "", script: "", onScreen: "", tip: "",
      notes: m.notes || "", planFile: "", nets: { instagram: true, facebook: true, tiktok: true }, files, posted: {},
      source: "app", by: "Claude", byName: "Claude", at, updatedAt: at, lastFileAt: at,
    });
    say(`${m.title}: ${files.length} arquivo(s), post ${ref.id}`);
  }
})().catch((e) => { say(`erro: ${e.message}`); process.exit(1); });
