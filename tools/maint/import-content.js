"use strict";
/* Conteúdo: puts edited videos into the Hive Admin's Content page (Compartilhados), as if sent in the app.
   DIR has manifest.json ([{title, notes, caption, order, files: [{file, w, h, dur, size}]}]) and the video files.
   Each file goes to Storage as it is (content/{id}/{time}-{name}); each entry becomes one post, status "ready".
   Prints one annotation per post. */
const fs = require("fs");
const crypto = require("crypto");
const path = require("path");
const { Firestore } = require("@google-cloud/firestore");
const { Storage } = require("@google-cloud/storage");
const PROJECT = process.env.PROJECT || "little-hive-house";
const db = new Firestore({ projectId: PROJECT, ignoreUndefinedProperties: true });
const bucket = new Storage({ projectId: PROJECT }).bucket(process.env.BUCKET || `${PROJECT}.firebasestorage.app`);
let DIR = process.env.DIR;
/* the files came locked (AES-256-GCM, the key itself locked with the public key of content-key.js) */
async function unlock() {
  if (!fs.existsSync(path.join(DIR, "key.enc"))) return DIR;
  const kref = db.collection("settings").doc("contentImportKey");
  const pem = ((await kref.get()).data() || {}).pem;
  if (!pem) throw new Error("no key (run content-key first)");
  const key = crypto.privateDecrypt({ key: pem, oaepHash: "sha256", padding: crypto.constants.RSA_PKCS1_OAEP_PADDING }, fs.readFileSync(path.join(DIR, "key.enc")));
  const out = "/tmp/import-plain"; fs.mkdirSync(out, { recursive: true });
  for (const f of fs.readdirSync(DIR).filter((x) => x.endsWith(".enc") && x !== "key.enc")) {
    const buf = fs.readFileSync(path.join(DIR, f));                 // iv (12) | tag (16) | data
    const d = crypto.createDecipheriv("aes-256-gcm", key, buf.subarray(0, 12)); d.setAuthTag(buf.subarray(12, 28));
    fs.writeFileSync(path.join(out, f.slice(0, -4)), Buffer.concat([d.update(buf.subarray(28)), d.final()]));
  }
  await kref.delete();
  return out;
}
const say = (s) => console.log(`::warning title=conteudo::${String(s).replace(/%/g, "%25").replace(/\n/g, " | ").slice(0, 1800)}`);
(async () => {
  DIR = await unlock();
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
