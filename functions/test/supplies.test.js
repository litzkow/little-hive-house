"use strict";
/* Materiais (supplies.js): orders use the materials up by their rules; bought / out / counted / used; purchases add to the
   money put into the shop; one push when something gets low. */
const test = require("node:test");
const assert = require("node:assert/strict");
const { FakeDB, FakeAuth, FakeBucket } = require("./fakes");
const deps = require("../deps");

const ADMIN = { uid: "admin1", token: { admin: true, email: "owner@lhh.com" } };
const DAY = 86400000;

function setup() {
  Object.assign(process.env, { ADMIN_EMAILS: "owner@lhh.com", RESEND_API_KEY: "re_x", SITE_URL: "https://littlehivehouse.com", MAIL_ADMIN: "support@littlehivehouse.com" });
  const db = new FakeDB();
  deps.set({ db, auth: new FakeAuth(), bucket: new FakeBucket() });
  db.docs.set("settings/store", { startupInvestment: 1112.92 });
  const pushes = [];
  require("../push").setSender(async (sub, payload) => { pushes.push(JSON.parse(payload)); return { statusCode: 201 }; });
  return { db, pushes, S: require("../supplies") };
}
const iso = (msAgo) => new Date(Date.now() - msAgo).toISOString();
function order(db, id, { magnets = 3, kind = "design", status = "delivered", shipped = true, ago = DAY } = {}) {
  const items = kind === "photos" ? [{ kind: "photos", packSize: magnets, qty: 1, price: 30 }] : [{ kind: "design", id: "fall/x", qty: magnets, unit: 5 }];
  db.docs.set(`orders/${id}`, { status, items, createdAt: iso(ago), paidAt: iso(ago), payment: { state: "captured" },
    fulfillment: shipped ? { shippedAt: iso(ago - 3600000) } : null });
}

test("the first look makes the standard list; orders use magnets, sheets, cards and mailers", async () => {
  const { db, S } = setup();
  let v = await S.adminSupplies({ action: "list" }, ADMIN);
  assert.ok(v.supplies.length >= 10);
  assert.equal(v.invested.total, 1112.92);
  await S.adminSupplies({ action: "counted", id: "magnet-kits", qty: 200 }, ADMIN);
  await S.adminSupplies({ action: "counted", id: "photo-paper", qty: 50 }, ADMIN);
  await S.adminSupplies({ action: "counted", id: "mailers", qty: 25 }, ADMIN);
  await S.adminSupplies({ action: "counted", id: "label-sheets", qty: 10 }, ADMIN);
  // after counting: a 9-photo pack (shipped) and 3 designs (not shipped yet), each with the logo magnet gift
  order(db, "a", { magnets: 9, kind: "photos", ago: -60000 });
  order(db, "b", { magnets: 3, status: "paid", shipped: false, ago: -60000 });
  order(db, "c", { magnets: 5, status: "canceled", shipped: false, ago: -60000 });   // never made
  v = await S.adminSupplies({ action: "list" }, ADMIN);
  const by = Object.fromEntries(v.supplies.map((s) => [s.id, s]));
  assert.equal(by["magnet-kits"].left, 200 - (9 + 1) - (3 + 1));
  assert.equal(by["photo-paper"].left, Math.round((50 - (1 + 1 / 9) - (1 + 1 / 9)) * 100) / 100);
  assert.equal(by.mailers.left, 24);              // only the shipped one
  assert.equal(by["label-sheets"].left, 9.5);     // half a sheet per label
  assert.equal(by["magnet-kits"].status, "ok");
  assert.ok(by["magnet-kits"].ordersLeft > 20);
});

test("bought adds and logs the purchase; out, used; low items push once", async () => {
  const { db, pushes, S } = setup();
  db.docs.set("adminPush/s1", { subscription: { endpoint: "https://push/1", keys: { p256dh: "x", auth: "y" } }, prefs: { orders: true }, uid: "admin1" });
  await S.adminSupplies({ action: "list" }, ADMIN);
  let v = await S.adminSupplies({ action: "bought", id: "mailers", qty: 50, cost: 18.99, store: "Amazon", item: "Bubble mailers 50" }, ADMIN);
  assert.equal(v.supplies.find((s) => s.id === "mailers").left, 50);
  assert.equal(v.invested.logged, 18.99);
  assert.equal(v.invested.total, 1131.91);
  assert.equal(db.get("settings/store").purchasesTotal, 18.99);
  v = await S.adminSupplies({ action: "used", id: "mailers", qty: 45 }, ADMIN);
  assert.equal(v.supplies.find((s) => s.id === "mailers").status, "low");
  await S.checkSupplies();
  await S.checkSupplies();
  const sent = pushes.filter((p) => /material/i.test(p.title));
  assert.equal(sent.length, 1, "one push, not one a day");
  assert.match(sent[0].body, /bolha/);
  v = await S.adminSupplies({ action: "out", id: "mailers" }, ADMIN);
  assert.equal(v.supplies[0].id, "mailers");      // what ran out comes first (the rest were never counted)
  assert.equal(v.supplies[0].status, "out");
  assert.equal(v.supplies.find((s) => s.id === "stickers").status, "unset");
  // a purchase that isn't a material (a new machine), and taking it back
  v = await S.adminSupplies({ action: "purchase", item: "Round magnet machine", cost: 120, date: "2026-11-04" }, ADMIN);
  assert.equal(v.invested.logged, 138.99);
  v = await S.adminSupplies({ action: "removePurchase", id: v.purchases.find((p) => p.cost === 120).id }, ADMIN);
  assert.equal(v.invested.logged, 18.99);
  await assert.rejects(S.adminSupplies({ action: "list" }, { uid: "x", token: {} }));
});

test("new materials can be added, changed and removed", async () => {
  const { S } = setup();
  let v = await S.adminSupplies({ action: "save", supply: { name: "Caixinhas de presente", unit: "caixas", per: "manual", low: 5, qty: 20, group: "Presentes" } }, ADMIN);
  const box = v.supplies.find((s) => s.name === "Caixinhas de presente");
  assert.equal(box.left, 20);
  v = await S.adminSupplies({ action: "save", id: box.id, supply: { name: "Caixinhas de presente", unit: "caixas", per: "order", rate: 1, low: 5, group: "Presentes" } }, ADMIN);
  assert.equal(v.supplies.find((s) => s.id === box.id).per, "order");
  v = await S.adminSupplies({ action: "remove", id: box.id }, ADMIN);
  assert.ok(!v.supplies.some((s) => s.id === box.id));
});
