"use strict";
/* Conteúdo: tudo nos Compartilhados fica em nome do Thiago. VALUE "owner" = troca o autor "Claude" pelo do Thiago (copiado de
   um envio dele); VALUE "export:<id>,<id>" = copia os arquivos desses posts para /tmp/content-out (o job põe no ramo content-out);
   VALUE "delete:<id>,<id>" = apaga esses posts e os arquivos (só posts que nunca saíram no Meta). */
const fs = require("fs");
const { Firestore } = require("@google-cloud/firestore");
const { Storage } = require("@google-cloud/storage");
const PROJECT = process.env.PROJECT || "little-hive-house";
const db = new Firestore({ projectId: PROJECT, ignoreUndefinedProperties: true });
const bucket = new Storage({ projectId: PROJECT }).bucket(`${PROJECT}.firebasestorage.app`);
const say = (s) => console.log(`::warning title=conteudo::${String(s).replace(/%/g, "%25").replace(/\n/g, " | ").slice(0, 1800)}`);
const isMe = (by, name) => /claude/i.test(`${by || ""} ${name || ""}`);
(async () => {
  const v = process.env.VALUE || "owner";
  const all = (await db.collection("content").get()).docs;
  if (v === "owner") {
    let owner = null;
    for (const d of all) { const it = d.data(); for (const f of [it, ...(it.files || [])]) if (!owner && f.by && /thiago/i.test(`${f.byName} ${f.by}`)) owner = { by: f.by, byName: f.byName }; }
    if (!owner) throw new Error("não achei envio do Thiago");
    let n = 0;
    for (const d of all) {
      const it = d.data(); const patch = {};
      if (isMe(it.by, it.byName)) Object.assign(patch, owner);
      if ((it.files || []).some((f) => isMe(f.by, f.byName))) patch.files = it.files.map((f) => (isMe(f.by, f.byName) ? { ...f, ...owner } : f));
      if (isMe(it.updatedBy)) patch.updatedBy = owner.by;
      if (Object.keys(patch).length) { await d.ref.set(patch, { merge: true }); n++; say(`${it.title}: agora em nome de ${owner.byName}`); }
    }
    say(`${n} posts passados para ${owner.byName}`);
  } else if (v.startsWith("export:")) {
    const ids = v.slice(7).split(","); fs.mkdirSync("/tmp/content-out", { recursive: true }); const man = [];
    for (const d of all.filter((x) => ids.includes(x.id))) {
      const it = d.data(); const files = [];
      for (const [i, f] of (it.files || []).entries()) { const out = `${d.id}-${i}-${f.name}`; await bucket.file(f.path).download({ destination: `/tmp/content-out/${out}` }); files.push(out); }
      man.push({ id: d.id, title: it.title, kind: it.kind, caption: it.caption, notes: it.notes, files });
    }
    fs.writeFileSync("/tmp/content-out/manifest.json", JSON.stringify(man, null, 1)); say(`${man.length} posts exportados`);
  } else if (v.startsWith("notes:")) {
    const map = JSON.parse(Buffer.from(v.slice(6), "base64").toString("utf8"));
    for (const d of all.filter((x) => map[x.id])) { await d.ref.set({ notes: map[d.id] }, { merge: true }); say(`${d.data().title}: ${map[d.id]}`); }
  } else if (v.startsWith("order:")) {
    /* posting order: [{id, notes}], the first one goes on top of Compartilhados (the list is sorted by when it was sent) */
    const list = JSON.parse(Buffer.from(v.slice(6), "base64").toString("utf8")); const base = Date.now();
    for (const [i, o] of list.entries()) {
      const d = all.find((x) => x.id === o.id); if (!d) { say(`${o.id}: não achei`); continue; }
      const it = d.data(); const at = new Date(base - i * 60000).toISOString();
      const files = (it.files || []).map((f, j, arr) => (j === arr.length - 1 ? { ...f, at } : f));
      await d.ref.set({ at, lastFileAt: at, files, ...(o.notes ? { notes: o.notes } : {}) }, { merge: true });
      say(`${i + 1}. ${it.title}${o.notes ? " · " + o.notes : ""}`);
    }
  } else if (v.startsWith("delete:")) {
    const ids = v.slice(7).split(",");
    for (const d of all.filter((x) => ids.includes(x.id))) {
      const it = d.data();
      if (it.status === "posted" || it.status === "scheduled" || Object.keys(it.posted || {}).length) { say(`${it.title}: já saiu ou está agendado, não apaguei`); continue; }
      for (const f of it.files || []) { try { await bucket.file(f.path).delete(); } catch (e) {} }
      await d.ref.delete(); say(`${it.title}: apagado`);
    }
  }
})().catch((e) => { say(`erro: ${e.message}`); process.exit(1); });
