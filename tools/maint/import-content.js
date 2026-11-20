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
/* {replace: "post title", files: [{file}]}: the post keeps everything; its video is swapped for the new one and the old
   file is deleted from Storage (a schedule that pointed at it points at the new one) */
async function replaceFile(m, base) {
  const q = await db.collection("content").where("title", "==", m.replace).get();
  if (q.size !== 1) { say(`${m.replace}: achei ${q.size} posts com esse nome, não troquei nada`); return; }
  const doc = q.docs[0], it = doc.data();
  const old = (it.files || []).filter((f) => /^video\//.test(f.type || ""));
  if (old.length !== 1) { say(`${m.replace}: o post tem ${old.length} vídeos, não troquei nada`); return; }
  const f = m.files[0], o = old[0];
  const dest = `content/${doc.id}/${base}-${f.file}`;
  await bucket.upload(path.join(DIR, f.file), { destination: dest, resumable: true, metadata: { contentType: "video/mp4", metadata: { name: o.name, firebaseStorageDownloadTokens: crypto.randomUUID() } } });
  const nf = { ...o, path: dest, size: f.size, w: f.w || o.w, h: f.h || o.h, dur: f.dur || o.dur };
  const patch = { files: (it.files || []).map((x) => (x.path === o.path ? nf : x)), updatedAt: new Date().toISOString() };
  if (it.sched && it.sched.path === o.path) patch.sched = { ...it.sched, path: dest };
  await doc.ref.set(patch, { merge: true });
  try { await bucket.file(o.path).delete(); } catch (e) { say(`${m.replace}: o arquivo antigo já não existia`); }
  const where = it.status === "posted" ? " (este já saiu no Meta: lá continua o vídeo antigo)" : it.sched ? " (agendado: vai sair o vídeo novo)" : "";
  say(`${m.replace}: vídeo trocado (${o.name}), o antigo foi apagado${where}`);
}
(async () => {
  DIR = await unlock();
  const man = JSON.parse(fs.readFileSync(path.join(DIR, "manifest.json"), "utf8"));
  const base = Date.now();
  /* by: "owner" = sent as the owner would (his e-mail and name, from his own last upload in the app) */
  let owner = null;
  if (man.some((m) => m.by === "owner")) {
    const q = await db.collection("content").orderBy("at", "desc").limit(200).get();
    for (const d of q.docs) {
      const it = d.data(); const fs_ = (it.files || []).slice().reverse();
      const f = fs_.find((x) => x.by && x.by !== "Claude" && x.by !== "system" && /thiago|litzkow/i.test(`${x.by} ${x.byName}`));
      if (f) { owner = { by: f.by, byName: f.byName || f.by }; break; }
      if (it.by && it.by !== "Claude" && it.by !== "system" && /thiago|litzkow/i.test(`${it.by} ${it.byName}`)) { owner = { by: it.by, byName: it.byName || it.by }; break; }
    }
    if (!owner) throw new Error("não achei um envio do Thiago para copiar o nome");
    say(`enviando como ${owner.byName}`);
  }
  for (const m of man) {
    const by = m.by === "owner" ? owner.by : m.by || "Claude", byName = m.by === "owner" ? owner.byName : m.by || "Claude";
    if (m.replace) { await replaceFile(m, base); continue; }
    const ref = db.collection("content").doc();
    const at = new Date(base - (m.order || 0) * 60000).toISOString();     // the first one shows on top
    const files = [];
    for (const f of m.files) {
      const dest = `content/${ref.id}/${base}-${f.file}`;
      await bucket.upload(path.join(DIR, f.file), { destination: dest, resumable: true, metadata: { contentType: f.type || "video/mp4", metadata: { name: f.file, firebaseStorageDownloadTokens: require("crypto").randomUUID() } } });
      files.push({ path: dest, name: f.file, type: f.type || "video/mp4", size: f.size, w: f.w, h: f.h, dur: f.dur || 0, at, by, byName });
    }
    await ref.set({
      title: m.title, kind: m.kind || "video", status: m.status || "ready", date: m.date || "", time: m.time || "", caption: m.caption || "", script: "", onScreen: "", tip: "",
      notes: m.notes || "", planFile: "", nets: m.nets || { instagram: true, facebook: true, tiktok: true }, files, posted: {},
      source: m.source || "app", by, byName, at, updatedAt: at, lastFileAt: at,
    });
    say(`${m.title}: ${files.length} arquivo(s), post ${ref.id}`);
  }
})().catch((e) => { say(`erro: ${e.message}`); process.exit(1); });
