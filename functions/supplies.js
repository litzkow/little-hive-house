"use strict";
/* Materials (Hive Admin › Materiais): everything the shop uses to make and ship orders, and what was bought.
   Nobody counts stock: each material keeps how many there were when it was last bought or checked (qty at `since`), and
   the orders made after that use it up, by a simple rule:
     per: "magnet"   rate units for each magnet made (magnet kits, paper sleeves)
          "sheet"    for each printed sheet of 9 (photo paper, ink as % of a refill)
          "order"    for each order made (thank-you card, business card, sticker, kraft envelope, filler)
          "shipment" for each order shipped (bubble mailer, label sheet: 0.5, two labels per sheet)
          "manual"   not tied to orders (tape, spare parts): only what the owners mark
   "Comprei" adds what was bought (and logs the purchase: the money put into the shop), "Acabou" sets it to 0,
   "Contei" sets the real count, "Usei" takes some away (magnets made for themselves, tests).
   supplies/{id}, purchases/{id}; every day checkSupplies() sends one push when something gets low. */

const { fail, nowIso } = require("./config");
const deps = require("./deps");
const U = require("./util");

const PER = ["magnet", "sheet", "order", "small_order", "big_order", "shipment", "manual"];
const SHEET = 9;   // magnets on one printed sheet (printsheet.js 3 x 3)
const SALE = new Set(["paid", "in_production", "shipped", "delivered", "refunded", "partially_refunded"]);

/** What the shop starts with (the owners change quantities, rules and add more in the app).
   `after`: starts being used only when that one runs out (the paper wrapping replaces the plastic bags). */
const DEFAULTS = [
  { id: "magnet-kits", name: "Kits de ímã 2x2 (ímã + capa)", unit: "jogos", per: "magnet", rate: 1, low: 40, group: "Ímãs" },
  { id: "photo-paper", name: "Papel fotográfico brilhante", unit: "folhas", per: "sheet", rate: 1, low: 15, group: "Ímãs" },
  { id: "ink", name: "Tinta da impressora", unit: "% da carga", per: "sheet", rate: 0.4, low: 20, group: "Ímãs" },
  { id: "plastic-bags", name: "Saquinhos transparentes 3x3 (1 por ímã)", unit: "saquinhos", per: "magnet", rate: 1, low: 30, group: "Embalagem" },
  { id: "tissue", name: "Papel de seda creme 14x20", unit: "folhas", per: "order", rate: 1, low: 15, group: "Embalagem", after: "plastic-bags" },
  { id: "filler", name: "Enchimento de papel picado", unit: "% do pacote", per: "order", rate: 2.5, low: 20, group: "Embalagem", after: "plastic-bags" },
  { id: "cardstock", name: "Papel cartão Neenah (cartões de agradecimento)", unit: "folhas", per: "order", rate: 0.25, low: 10, group: "Embalagem" },
  { id: "business-cards", name: "Cartões de visita Avery", unit: "cartões", per: "order", rate: 1, low: 15, group: "Embalagem" },
  { id: "stickers", name: "Adesivos redondos (selo)", unit: "adesivos", per: "order", rate: 1, low: 10, group: "Embalagem" },
  { id: "copy-paper", name: "Papel sulfite (lista do pacote)", unit: "folhas", per: "order", rate: 1, low: 50, group: "Embalagem" },
  { id: "kraft-envelopes", name: "Envelopes kraft A7", unit: "envelopes", per: "small_order", rate: 1, low: 15, group: "Envio" },
  { id: "mailer-boxes", name: "Caixinhas kraft 9x6x2 (pedidos grandes)", unit: "caixas", per: "big_order", rate: 1, low: 5, group: "Envio" },
  { id: "label-sheets", name: "Folhas de etiqueta LabelMore (2 por folha)", unit: "folhas", per: "shipment", rate: 0.5, low: 20, group: "Envio" },
  { id: "tape", name: "Fita adesiva", unit: "rolos", per: "manual", rate: 0, low: 1, group: "Envio" },
];

const num = (v) => (Number.isFinite(Number(v)) ? Number(v) : 0);
const r2 = (n) => Math.round(n * 100) / 100;

function magnetsOf(o) {
  return (o.items || []).reduce((t, it) => {
    const q = it.qty == null ? 1 : num(it.qty);
    if (it.kind === "design") return t + q;
    if (it.kind === "photos") return t + num(it.packSize) * q;
    if (it.kind === "package") return t + num(it.size) * q;
    return t + num(it.magnets) * q;
  }, 0);
}
/** Was this order really made (paid, not a card hold that was let go)? */
function made(o) {
  if (!o || !SALE.has(o.status)) return o && o.status === "canceled" && !!(o.fulfillment && o.fulfillment.shippedAt);
  return !(o.payment && (o.payment.state === "released" || o.payment.state === "expired"));
}

/** Pure: what each order used, as {at, shippedAt, magnets, sheets, big} (the logo magnet gift counts as a magnet).
   big: the order has cfg.bigOrder magnets or more (it goes in a box, not an envelope); until the owners set that
   number, every order is small. */
function usageList(orders, cfg = {}) {
  const gift = num(cfg.giftMagnets == null ? 1 : cfg.giftMagnets), bigAt = num(cfg.bigOrder);
  return (orders || []).filter(made).map((o) => {
    const own = magnetsOf(o);
    return { at: Date.parse(o.paidAt || o.createdAt || ""), shippedAt: Date.parse((o.fulfillment || {}).shippedAt || ""), magnets: own + gift,
      sheets: Math.ceil(own / SHEET) + gift / SHEET, big: bigAt > 0 && own >= bigAt };
  }).sort((a, b) => a.at - b.at);
}
function useOf(s, u) {
  const rate = num(s.rate);
  switch (s.per) {
    case "magnet": return rate * u.magnets;
    case "sheet": return rate * u.sheets;
    case "order": return rate;
    case "small_order": return u.big ? 0 : rate;
    case "big_order": return u.big ? rate : 0;
    default: return 0;
  }
}
/** When a material runs out by the estimate (ms), or Infinity: the one that replaces it starts then. */
function runsOutAt(s, uses) {
  const since = Date.parse(s.since || "") || 0;
  let left = num(s.qty) - num(s.usedExtra);
  if (left <= 0) return since;
  for (const u of uses) {
    const t = s.per === "shipment" ? u.shippedAt : u.at;
    if (!(t >= since)) continue;
    left -= s.per === "shipment" ? num(s.rate) : useOf(s, u);
    if (left <= 0) return t;
  }
  return Infinity;
}

/** Pure: one material's estimate: {left, used, status: ok | low | out, pct} */
function estimate(s, uses, from = 0) {
  const since = Math.max(Date.parse(s.since || "") || 0, from);
  const rate = num(s.rate);
  let used = 0;
  if (s.per !== "manual" && from !== Infinity) {
    for (const u of uses) {
      if (s.per === "shipment") { if (u.shippedAt >= since) used += rate; continue; }
      if (!(u.at >= since)) continue;
      used += useOf(s, u);
    }
  }
  used += num(s.usedExtra);
  const left = Math.max(0, num(s.qty) - used);
  // never counted or bought yet: the page asks how many there are
  const status = !s.setAt ? "unset" : left <= 0 ? "out" : left <= num(s.low) ? "low" : "ok";
  const full = Math.max(num(s.qty), num(s.low) * 2, 1);
  // how many more orders it lasts at this shop's average order (magnets per order from these orders)
  let perOrder = null;
  if (uses.length && s.per !== "manual") {
    const avgM = uses.reduce((t, u) => t + u.magnets, 0) / uses.length, avgS = uses.reduce((t, u) => t + u.sheets, 0) / uses.length;
    perOrder = s.per === "magnet" ? rate * avgM : s.per === "sheet" ? rate * avgS : s.per === "big_order" ? null : rate;
  }
  return { left: r2(left), used: r2(used), status, pct: Math.round(Math.min(100, (left / full) * 100)), ordersLeft: perOrder ? Math.floor(left / perOrder) : null,
    waiting: from === Infinity };
}

/** The estimate of `s` in its list: one that comes `after` another starts when that one runs out. */
function estimateIn(s, list, uses) {
  const prev = s.after && list.find((x) => x.id === s.after && x.active !== false);
  return estimate(s, uses, prev ? runsOutAt(prev, uses) : 0);
}

async function load() {
  const db = deps.db();
  const [sq, cfgSnap] = await Promise.all([db.collection("supplies").get(), db.collection("settings").doc("supplies").get()]);
  const cfg = cfgSnap.exists ? cfgSnap.data() : {};
  let list = sq.docs.map((d) => ({ id: d.id, ...d.data() }));
  if (!list.length && !cfg.seeded) {
    // first time: the standard list, starting empty (the owners tell what they have, or tap "Comprei")
    const at = nowIso();
    list = DEFAULTS.map((d) => ({ ...d, qty: 0, since: at, usedExtra: 0, active: true, createdAt: at }));
    await Promise.all(list.map((s) => db.collection("supplies").doc(s.id).set(s)));
    await db.collection("settings").doc("supplies").set({ seeded: at, giftMagnets: 1 }, { merge: true });
    cfg.seeded = at; cfg.giftMagnets = 1;
  }
  return { list, cfg };
}
async function ordersSince(since) {
  const q = await deps.db().collection("orders").where("createdAt", ">=", since).get();
  return q.docs.map((d) => d.data());
}

/** Everything the page shows: materials with their estimate, purchases and the total put into the shop. */
async function view() {
  const db = deps.db();
  const { list, cfg } = await load();
  const oldest = list.reduce((m, s) => (s.since && s.since < m ? s.since : m), nowIso());
  // orders paid a little before `since` can ship after it: look 60 days further back
  const orders = await ordersSince(new Date(Date.parse(oldest) - 60 * 86400000).toISOString());
  const uses = usageList(orders, cfg);
  const pq = await db.collection("purchases").get();
  const purchases = pq.docs.map((d) => ({ id: d.id, ...d.data() })).sort((a, b) => String(b.date).localeCompare(String(a.date)));
  const st = await db.collection("settings").doc("store").get();
  const before = num((st.exists && st.data().startupInvestment) != null ? st.data().startupInvestment : 1112.92);
  const logged = r2(purchases.reduce((t, p) => t + num(p.cost), 0));
  return {
    ok: true, cfg: { giftMagnets: num(cfg.giftMagnets == null ? 1 : cfg.giftMagnets), bigOrder: num(cfg.bigOrder) },
    supplies: list.filter((s) => s.active !== false).map((s) => ({ ...s, ...estimateIn(s, list, uses) }))
      .sort((a, b) => (["out", "low", "unset", "ok"].indexOf(a.status) - ["out", "low", "unset", "ok"].indexOf(b.status)) || String(a.group).localeCompare(String(b.group)) || String(a.name).localeCompare(String(b.name))),
    purchases, invested: { before, logged, total: r2(before + logged) },
  };
}

function cleanSupply(d) {
  const per = PER.includes(d.per) ? d.per : "manual";
  const name = U.text(d.name, 80, { required: true, field: "o nome" });
  return { name, unit: U.text(d.unit, 30) || "unidades", per, after: U.text(d.after, 64) || "", rate: Math.max(0, num(d.rate)), low: Math.max(0, num(d.low)), group: U.text(d.group, 30) || "Outros",
    note: U.text(d.note, 300), link: /^https:\/\//.test(String(d.link || "")) ? String(d.link).slice(0, 500) : "" };
}

/** Writes the current estimate down as the new starting point, then applies `fn` to the quantity. */
async function rebase(id, fn, extra = {}) {
  const { list, cfg } = await load();
  const s = list.find((x) => x.id === id);
  if (!s) fail("not-found", "Material não encontrado.");
  const uses = usageList(await ordersSince(new Date(Date.parse(s.since || nowIso()) - 60 * 86400000).toISOString()), cfg);
  const left = estimateIn(s, list, uses).left;
  const at = nowIso();
  const upd = { qty: r2(Math.max(0, fn(left))), since: at, usedExtra: 0, alertedAt: null, setAt: at, updatedAt: at, ...extra };
  await deps.db().collection("supplies").doc(id).set(upd, { merge: true });
  return upd;
}

/** The purchases logged here add up in settings/store.purchasesTotal (the Growth plan adds it to the money put in). */
async function syncTotal() {
  const pq = await deps.db().collection("purchases").get();
  const total = r2(pq.docs.reduce((t, d) => t + num(d.data().cost), 0));
  await deps.db().collection("settings").doc("store").set({ purchasesTotal: total }, { merge: true });
}

/** adminSupplies({action, ...}): list | bought | out | counted | used | save | remove | purchase | removePurchase | config */
async function adminSupplies(data, auth) {
  U.requireAdmin(auth);
  data = data || {};
  const db = deps.db(), who = U.who(auth), at = nowIso();
  const id = data.id ? U.text(data.id, 64) : "";
  if (id && !/^[A-Za-z0-9_-]+$/.test(id)) fail("invalid-argument", "Id inválido.");
  const q = num(data.qty);
  switch (data.action) {
    case "list": return view();
    case "bought": {
      if (!(q > 0)) fail("invalid-argument", "Quanto vocês compraram?");
      await rebase(id, (left) => left + q, { lastBought: at });
      if (num(data.cost) > 0) {
        await db.collection("purchases").add({ date: U.text(data.date, 10) || at.slice(0, 10), item: U.text(data.item, 120) || "", supplyId: id, qty: q,
          cost: r2(num(data.cost)), store: U.text(data.store, 40) || "", by: who, createdAt: at });
        await syncTotal();
      }
      return view();
    }
    case "out": await rebase(id, () => 0); return view();
    case "counted": if (q < 0) fail("invalid-argument", "Quantidade inválida."); await rebase(id, () => q); return view();
    case "used": if (!(q > 0)) fail("invalid-argument", "Quanto foi usado?"); await rebase(id, (left) => left - q); return view();
    case "save": {
      const s = cleanSupply(data.supply || {});
      if (id) await db.collection("supplies").doc(id).set({ ...s, updatedAt: at }, { merge: true });
      else {
        const nid = s.name.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 40) || `item-${Date.now()}`;
        await db.collection("supplies").doc(nid).set({ ...s, qty: Math.max(0, num(data.supply && data.supply.qty)), since: at, usedExtra: 0, active: true, createdAt: at, setAt: at });
      }
      return view();
    }
    case "remove": await db.collection("supplies").doc(id).set({ active: false, updatedAt: at }, { merge: true }); return view();
    case "purchase": {
      const cost = r2(num(data.cost));
      if (!(cost > 0)) fail("invalid-argument", "Qual foi o valor?");
      await db.collection("purchases").add({ date: U.text(data.date, 10) || at.slice(0, 10), item: U.text(data.item, 120, { required: true, field: "o que foi comprado" }),
        cost, store: U.text(data.store, 40) || "", supplyId: "", qty: 0, by: who, createdAt: at });
      await syncTotal();
      return view();
    }
    case "removePurchase": await db.collection("purchases").doc(id).delete(); await syncTotal(); return view();
    case "config": {
      const upd = {};
      if (data.giftMagnets !== undefined) upd.giftMagnets = Math.max(0, Math.min(5, num(data.giftMagnets)));
      if (data.bigOrder !== undefined) upd.bigOrder = Math.max(0, Math.min(10000, Math.round(num(data.bigOrder))));
      await db.collection("settings").doc("supplies").set(upd, { merge: true });
      return view();
    }
    default: fail("invalid-argument", "Ação desconhecida.");
  }
}

/** Daily: one push for the materials that just got low or ran out (again only after the next "Comprei"). */
async function checkSupplies() {
  const v = await view();
  const fresh = v.supplies.filter((s) => (s.status === "low" || s.status === "out") && !s.alertedAt);
  if (!fresh.length) return { alerted: 0 };
  await Promise.all(fresh.map((s) => deps.db().collection("supplies").doc(s.id).set({ alertedAt: nowIso() }, { merge: true })));
  await require("./push").notifyAdmins("admin_supplies", { items: fresh.map((s) => ({ name: s.name, status: s.status, left: s.left, unit: s.unit })) }).catch(() => {});
  return { alerted: fresh.length };
}

module.exports = { adminSupplies, checkSupplies, estimate, estimateIn, runsOutAt, usageList, magnetsOf, made, DEFAULTS, PER };
