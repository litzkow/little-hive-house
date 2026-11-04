"use strict";
/* One time (4 Nov 2026): the shop's materials as they really are, and the Amazon purchases of 1 and 2 Nov 2026
   (the cat things left out). The 7 Oct purchases (printer, materials, the magnet machine kit) are already in
   settings/store.startupInvestment ($1,112.92). Runs once: settings/supplies.seededBy says it was done.
   Run by .github/workflows/maint.yml (task seed-supplies). DRY_RUN=1 only says what it would write. */
const { Firestore } = require("@google-cloud/firestore");
const db = new Firestore({ projectId: process.env.PROJECT || "little-hive-house" });
const DRY = process.env.DRY_RUN === "1";
const MARK = "amazon-2026-11-04";

const OCT7 = "2026-10-07T12:00:00.000Z", NOV1 = "2026-11-01T12:00:00.000Z", NOV2 = "2026-11-02T12:00:00.000Z";
// qty = how many there were at `since`; the orders after that are taken off automatically
const SUPPLIES = [
  // the machine kit came with 200; about 20 went on test sheets and magnets for home (usedExtra)
  { id: "magnet-kits", name: "Kits de ímã 2x2 (ímã + capa)", unit: "jogos", per: "magnet", rate: 1, low: 40, group: "Ímãs", qty: 200, since: OCT7, usedExtra: 20 },
  { id: "photo-paper", name: "Papel fotográfico brilhante", unit: "folhas", per: "sheet", rate: 1, low: 15, group: "Ímãs" },
  { id: "ink", name: "Tinta da impressora", unit: "% da carga", per: "sheet", rate: 0.4, low: 20, group: "Ímãs", qty: 100, since: OCT7, usedExtra: 5 },
  { id: "plastic-bags", name: "Saquinhos transparentes 3x3 (1 por ímã)", unit: "saquinhos", per: "magnet", rate: 1, low: 30, group: "Embalagem", qty: 200, since: NOV1 },
  { id: "tissue", name: "Papel de seda creme 14x20", unit: "folhas", per: "order", rate: 1, low: 15, group: "Embalagem", after: "plastic-bags", qty: 120, since: NOV2 },
  { id: "filler", name: "Enchimento de papel picado (300 g)", unit: "% do pacote", per: "order", rate: 2.5, low: 20, group: "Embalagem", after: "plastic-bags", qty: 100, since: NOV2 },
  { id: "cardstock", name: "Papel cartão Neenah (4 cartões de agradecimento por folha)", unit: "folhas", per: "order", rate: 0.25, low: 10, group: "Embalagem", qty: 250, since: NOV2 },
  { id: "business-cards", name: "Cartões de visita Avery", unit: "cartões", per: "order", rate: 1, low: 15, group: "Embalagem", qty: 90, since: NOV2 },
  { id: "stickers", name: "Adesivos redondos (selo)", unit: "adesivos", per: "order", rate: 1, low: 10, group: "Embalagem" },
  { id: "copy-paper", name: "Papel sulfite Amazon Basics (lista do pacote)", unit: "folhas", per: "order", rate: 1, low: 50, group: "Embalagem", qty: 500, since: NOV2 },
  { id: "kraft-envelopes", name: "Envelopes kraft A7 imprimíveis", unit: "envelopes", per: "small_order", rate: 1, low: 15, group: "Envio", qty: 100, since: NOV2 },
  { id: "mailer-boxes", name: "Caixinhas kraft 9x6x2 (pedidos grandes)", unit: "caixas", per: "big_order", rate: 1, low: 5, group: "Envio", qty: 60, since: NOV2 },
  { id: "label-sheets", name: "Folhas de etiqueta LabelMore (2 por folha)", unit: "folhas", per: "shipment", rate: 0.5, low: 20, group: "Envio", qty: 500, since: NOV2 },
  { id: "tape", name: "Fita adesiva", unit: "rolos", per: "manual", rate: 0, low: 1, group: "Envio" },
];
const PURCHASES = [
  { date: "2026-11-01", store: "Amazon", item: "Saquinhos transparentes 3x3 (200)", cost: 6.94 },
  { date: "2026-11-02", store: "Amazon", item: "Papel sulfite Amazon Basics", cost: 7.46 },
  { date: "2026-11-02", store: "Amazon", item: "Etiquetas LabelMore, caixinhas kraft (60), envelopes kraft A7 (100), papel de seda creme (120) e papel picado", cost: 98.39 },
  // the same order had cat toys: the shop's part is the two items with their share of the tax and the delivery fee
  { date: "2026-11-02", store: "Amazon", item: "Cartões de visita Avery e papel cartão Neenah", cost: 25.85 },
];

(async () => {
  const cfgRef = db.collection("settings").doc("supplies");
  const cfg = (await cfgRef.get()).data() || {};
  if (cfg.seededBy === MARK) { console.log("already done"); return; }
  const at = new Date().toISOString();
  const batch = db.batch();
  for (const s of SUPPLIES) {
    const known = s.qty != null;
    batch.set(db.collection("supplies").doc(s.id), { after: "", note: "", link: "", usedExtra: 0, ...s, qty: s.qty || 0, since: s.since || at,
      active: true, createdAt: at, ...(known ? { setAt: at } : {}) });
  }
  for (const p of PURCHASES) batch.set(db.collection("purchases").doc(), { ...p, supplyId: "", qty: 0, by: "claude", createdAt: at });
  batch.set(cfgRef, { seeded: cfg.seeded || at, seededBy: MARK, giftMagnets: cfg.giftMagnets == null ? 1 : cfg.giftMagnets }, { merge: true });
  const total = Math.round(PURCHASES.reduce((t, p) => t + p.cost, 0) * 100) / 100;
  batch.set(db.collection("settings").doc("store"), { purchasesTotal: total }, { merge: true });
  if (DRY) { console.log(`would write ${SUPPLIES.length} materials, ${PURCHASES.length} purchases ($${total})`); return; }
  await batch.commit();
  console.log(`wrote ${SUPPLIES.length} materials, ${PURCHASES.length} purchases ($${total})`);
})().catch((e) => { console.error(e.message); process.exit(1); });
