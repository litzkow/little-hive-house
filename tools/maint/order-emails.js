"use strict";
/* Pedido: quais e-mails o cliente recebeu (VALUE = número, ex. 1003). Mostra as datas gravadas no pedido e, se a chave do
   Resend estiver aqui, o que o Resend diz de cada e-mail mandado para o cliente (entregue, aberto, devolvido). O e-mail
   do cliente aparece mascarado. */
const { Firestore } = require("@google-cloud/firestore");
const db = new Firestore({ projectId: process.env.PROJECT || "little-hive-house" });
const say = (s) => console.log(`::warning title=emails::${String(s).replace(/\n/g, " ").slice(0, 900)}`);
const mask = (e) => String(e || "").replace(/^(.).*?(.)@/, "$1***$2@");
(async () => {
  const n = Number(String(process.env.VALUE || "").replace(/\D/g, ""));
  const q = await db.collection("orders").where("number", "==", n).limit(1).get();
  if (q.empty) return say(`pedido ${n} não encontrado`);
  const o = q.docs[0].data();
  say(`pedido LHH-${n}: status ${o.status} · e-mail ${mask(o.email)} · marketing ${!!o.marketing} · emails ${JSON.stringify(o.emails || {})}`);
  say(`rastreio: ${JSON.stringify(o.tracking ? { status: o.tracking.status, at: o.tracking.updatedAt || o.tracking.at } : o.shipment || {}).slice(0, 300)}`);
  const key = process.env.RESEND_API_KEY;
  if (!key) return say("sem chave do Resend aqui");
  const r = await fetch("https://api.resend.com/emails?limit=100", { headers: { Authorization: `Bearer ${key}` } });
  const j = await r.json().catch(() => ({}));
  if (!r.ok) return say(`Resend: ${r.status} ${JSON.stringify(j).slice(0, 300)}`);
  const mine = (j.data || []).filter((m) => [].concat(m.to || []).some((t) => String(t).toLowerCase() === String(o.email).toLowerCase()));
  say(`Resend: ${mine.length} e-mails para esse cliente nos últimos 100`);
  mine.forEach((m) => say(`${m.created_at} · ${m.subject} · ${m.last_event || ""}`));
})().catch((e) => { console.log(`::error::${e.message}`); process.exit(1); });
