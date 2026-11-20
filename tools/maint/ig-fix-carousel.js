"use strict";
/* Instagram: o carrossel de Natal volta a ter só as marcações escolhidas à mão (tira as que o robô pôs a mais na 1ª foto). */
const { Firestore } = require("@google-cloud/firestore");
require("../../functions/deps").set({ db: new Firestore({ projectId: process.env.PROJECT || "little-hive-house", ignoreUndefinedProperties: true }) });
const say = (s) => console.log(`::warning title=ig::${String(s).replace(/\n/g, " ").slice(0, 900)}`);
const KEEP = { "18153139336482572": ["christmas-merry-and-bright-classic", "christmas-naughty-or-nice-classic", "christmas-merry-christmas", "christmas-home-for-christmas"],
  "18155286082545649": ["christmas-hung-with-care", "christmas-cookies-for-santa", "christmas-ho-ho-ho", "christmas-seasons-greetings", "christmas-north-pole-post-office"], "18159402397510284": [] };
(async () => {
  const db = require("../../functions/deps").db();
  const G = require("../../functions/ads")._internal.graph;
  const meta = ((await db.collection("ads").doc("auth").get()).data() || {}).meta;
  for (const [child, keep] of Object.entries(KEEP)) {
    const tags = ((await G(meta, "GET", `${child}/product_tags`)).data) || [];
    say(`${child} antes: ${tags.map((t) => t.product_name || t.product_id).join(" | ")}`);
    const extra = [];
    for (const t of tags) {
      const p = await G(meta, "GET", String(t.product_id), { fields: "retailer_id" });
      if (!keep.includes(p.retailer_id)) extra.push({ product_id: t.product_id, ...(t.x !== undefined ? { x: t.x, y: t.y } : {}) });
    }
    if (extra.length) {
      await G(meta, "DELETE", `${child}/product_tags`, { deleted_tags: extra });
      say(`${child}: ${extra.length} marcação(ões) a mais removida(s)`);
    }
    const after = ((await G(meta, "GET", `${child}/product_tags`)).data) || [];
    say(`${child} agora: ${after.map((t) => t.product_name || t.product_id).join(" | ")}`);
  }
  await db.collection("socialTags").doc("17913388521309037").set({ status: "done", source: "planner", plan: [], done: [], note: "marcado à mão" }, { merge: true });
})().catch((e) => { say(`erro: ${e.message}`); process.exit(1); });
