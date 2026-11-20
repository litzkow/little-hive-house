"use strict";
/* Etsy: which permissions the connection has, and the orders brought in now (functions/etsy-orders.js). */
process.env.SITE_URL = process.env.SITE_URL || "https://littlehivehouse.com";
const { Firestore } = require("@google-cloud/firestore");
require("../../functions/deps").set({ db: new Firestore({ projectId: process.env.PROJECT || "little-hive-house", ignoreUndefinedProperties: true }) });
const say = (s) => console.log(`::warning title=etsy::${String(s).replace(/\n/g, " ").slice(0, 900)}`);
(async () => {
  const db = require("../../functions/deps").db();
  const a = (await db.collection("etsy").doc("auth").get()).data() || {};
  say(`conectado: ${!!a.refresh} · loja ${a.shopId || "?"} · permissões: ${a.scope || "?"}`);
  say(`rastreio para o Etsy: ${/transactions_w/.test(a.scope || "") ? "SIM" : "NÃO"}`);
  const r = await require("../../functions/etsy-orders").importOrders({ days: 30 });
  say(`pedidos: ${JSON.stringify(r)}`);
})().catch((e) => { say(`erro: ${e.message}`); process.exit(1); });
