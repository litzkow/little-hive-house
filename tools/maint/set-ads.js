"use strict";
/* Changes the ads settings (ads/config, functions/ads.js) when the owners ask in chat. VALUE = JSON merged into the config:
   {"monthCap":50,"channels":{"meta":{"daily":1}},"rules":{"perPost":1}}. A new cap is logged as approved by the owners. */
const { Firestore } = require("@google-cloud/firestore");
const db = new Firestore({ projectId: process.env.PROJECT || "little-hive-house" });
(async () => {
  const v = JSON.parse(process.env.VALUE || "{}");
  const ref = db.collection("ads").doc("config");
  const cur = (await ref.get()).data() || {};
  const next = { ...cur, ...v, channels: { ...(cur.channels || {}), ...(v.channels || {}) }, rules: { ...(cur.rules || {}), ...(v.rules || {}) } };
  Object.keys(v.channels || {}).forEach((k) => { next.channels[k] = { ...((cur.channels || {})[k] || {}), ...v.channels[k] }; });
  const now = new Date().toISOString();
  if (v.monthCap != null && v.monthCap !== cur.monthCap) {
    next.capAt = now; next.capBy = "Thiago (pedido no chat)";
    const before = cur.monthCap == null ? 200 : cur.monthCap;
    await db.collection("adsLog").add({ at: now, channel: "all", kind: "cap", pt: `Teto do mês aprovado: $${Number(v.monthCap).toFixed(2)} (antes $${Number(before).toFixed(2)}).`,
      en: `Monthly cap approved: $${Number(v.monthCap).toFixed(2)} (was $${Number(before).toFixed(2)}).` });
  }
  await ref.set(next);
  console.log(JSON.stringify({ monthCap: next.monthCap, channels: next.channels, rules: next.rules }));
})().catch((e) => { console.error(e.message); process.exit(1); });
