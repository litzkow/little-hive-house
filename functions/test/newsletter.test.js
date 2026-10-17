"use strict";
/* Emails to the subscribers (newsletter.js): preview, test, the one-time send in batches, unsubscribed people left out. */
const test = require("node:test");
const assert = require("node:assert/strict");
const { FakeDB, FakeAuth, FakeBucket, fakeNet } = require("./fakes");
const deps = require("../deps");
const N = require("../newsletter");

const ADMIN = { uid: "admin1", token: { admin: true, email: "owner@lhh.com" } };
const CAMPAIGN = { subject: "Fresh from the hive", title: "New magnets this week", body: "We painted new places.\n\nCome take a look.",
  gallery: "designs", designs: ["places/las-vegas"], button: { label: "See them", href: "/collections/places.html" } };

function setup() {
  Object.assign(process.env, { STRIPE_SECRET_KEY: "sk_test_x", RESEND_API_KEY: "re_x", ADMIN_EMAILS: "owner@lhh.com", SITE_URL: "https://littlehivehouse.com",
    MAIL_ADMIN: "support@littlehivehouse.com", UNSUBSCRIBE_SECRET: "s3cret", MAIL_POSTAL_ADDRESS: "PO Box 1, Carrollton, GA 30117" });
  const db = new FakeDB(), net = fakeNet();
  deps.set({ db, auth: new FakeAuth(), bucket: new FakeBucket(), getDownloadURL: async () => null });
  globalThis.fetch = net.fetch;
  return { db, net };
}

test("clean: required fields, links only to the shop, codes upper-cased", () => {
  setup();
  assert.throws(() => N.clean({ ...CAMPAIGN, subject: "" }), (e) => e.code === "invalid-argument");
  assert.throws(() => N.clean({ ...CAMPAIGN, body: "  " }), (e) => e.code === "invalid-argument");
  assert.throws(() => N.clean({ ...CAMPAIGN, button: { label: "Go", href: "https://evil.example" } }), /littlehivehouse\.com/);
  const c = N.clean({ ...CAMPAIGN, promo: { code: "hive10", text: "10% off" }, gallery: "weird", designs: ["places/x", "../../etc", "a/b", "c/d", "e/f"] });
  assert.equal(c.button.href, "https://littlehivehouse.com/collections/places.html");
  assert.deepEqual(c.promo, { code: "HIVE10", text: "10% off" });
  assert.equal(c.gallery, "designs");
  assert.deepEqual(c.designs, ["places/x", "a/b", "c/d"]);
});

test("admins only; preview shows the email and how many subscribers would get it", async () => {
  const { db } = setup();
  await db.collection("subscribers").doc("a").set({ email: "ana@example.com" });
  await db.collection("subscribers").doc("b").set({ email: "bo@example.com", unsubscribed: true });
  await db.collection("subscribers").doc("c").set({ email: "ANA@example.com" });
  await assert.rejects(N.adminNewsletter({ action: "preview", campaign: CAMPAIGN }, null), (e) => e.code === "unauthenticated");
  const p = await N.adminNewsletter({ action: "preview", campaign: CAMPAIGN }, ADMIN);
  assert.equal(p.subject, "Fresh from the hive");
  assert.equal(p.count, 1, "unsubscribed and duplicate emails are left out");
  assert.match(p.html, /New magnets this week/);
  assert.match(p.html, /unsubscribe/i);
  assert.match(p.html, /assets\/email\/thumbs\/places\/las-vegas\.jpg/);
});

test("send: once per campaign, batches of 100, each email with its own unsubscribe link; a test goes to the admin only", async () => {
  const { db, net } = setup();
  for (let i = 0; i < 230; i++) await db.collection("subscribers").doc(`s${i}`).set({ email: `p${i}@example.com` });
  await db.collection("subscribers").doc("gone").set({ email: "gone@example.com", unsubscribed: true });
  const t = await N.adminNewsletter({ action: "test", campaign: CAMPAIGN }, ADMIN);
  assert.deepEqual(t, { sent: true, to: "owner@lhh.com" });
  assert.equal(net.emails.length, 1);
  await assert.rejects(N.adminNewsletter({ action: "send", campaign: CAMPAIGN, campaignId: "camp-0001" }, ADMIN), /confirm/);
  process.env.MAIL_POSTAL_ADDRESS = "";
  await assert.rejects(N.adminNewsletter({ action: "send", campaign: CAMPAIGN, campaignId: "camp-0001", confirm: "SEND" }, ADMIN), /mailing address/);
  process.env.MAIL_POSTAL_ADDRESS = "PO Box 1, Carrollton, GA 30117";
  const r = await N.adminNewsletter({ action: "send", campaign: CAMPAIGN, campaignId: "camp-0001", confirm: "SEND" }, ADMIN, null, { pause: 0 });
  assert.equal(r.total, 230);
  const batches = net.emails.slice(1);
  assert.deepEqual(batches.map((b) => b.length), [100, 100, 30]);
  const first = batches[0][0];
  assert.deepEqual(first.to, ["p0@example.com"]);
  assert.match(first.headers["List-Unsubscribe"], /unsubscribe\.html\?e=p0%40example\.com&t=/);
  assert.ok(!batches.flat().some((m) => m.to[0] === "gone@example.com"));
  const doc = db.get("campaigns/camp-0001");
  assert.equal(doc.status, "sent");
  assert.equal(doc.total, 230);
  await assert.rejects(N.adminNewsletter({ action: "send", campaign: CAMPAIGN, campaignId: "camp-0001", confirm: "SEND" }, ADMIN, null, { pause: 0 }),
    (e) => e.code === "already-exists");
  const list = await N.adminNewsletter({ action: "list" }, ADMIN);
  assert.equal(list.campaigns[0].id, "camp-0001");
});

test("a discount code must be an active Stripe promotion code", async () => {
  const { net } = setup();
  net.handlers["GET /v1/promotion_codes"] = (q) => ({ data: q.code === "HIVE10" ? [{ id: "promo_1", code: "HIVE10", active: true }] : [] });
  await assert.rejects(N.adminNewsletter({ action: "test", campaign: { ...CAMPAIGN, promo: { code: "NOPE1" } } }, ADMIN), /isn't an active discount/);
  const ok = await N.adminNewsletter({ action: "test", campaign: { ...CAMPAIGN, promo: { code: "hive10" } } }, ADMIN);
  assert.equal(ok.sent, true);
  assert.match(net.emails[0].html, /HIVE10/);
});

test("automatic campaign: the 1st shows the season's designs (fresh ones first), the 15th photo magnet ideas; Christmas deadline in time", () => {
  const seasons = require("../catalog.json").seasons;
  const oct1 = N.autoCampaign(Date.parse("2026-10-01T14:00:00Z"), { seasons, recentDesigns: [] });
  assert.equal(oct1.gallery, "designs");
  assert.equal(oct1.eyebrow, "Fall");
  assert.equal(oct1.designs.length, 3);
  assert.match(oct1.button.href, /collections\/fall\.html$/);
  const again = N.autoCampaign(Date.parse("2026-10-01T14:00:00Z"), { seasons, recentDesigns: oct1.designs.slice(0, 2) });
  assert.ok(!again.designs.slice(0, 1).some((d) => oct1.designs.slice(0, 2).includes(d)), "designs sent lately go last");
  const oct15 = N.autoCampaign(Date.parse("2026-10-15T14:00:00Z"), { seasons });
  assert.equal(oct15.gallery, "photos");
  assert.match(oct15.button.href, /photo-magnets\.html\?frame=fall#custom$/);
  const dec1 = N.autoCampaign(Date.parse("2026-12-01T15:00:00Z"), { seasons });
  assert.equal(dec1.eyebrow, "Christmas");
  assert.match(dec1.body, /order by December 12/);
  const jan1 = N.autoCampaign(Date.parse("2027-01-01T15:00:00Z"), { seasons });
  assert.equal(jan1.eyebrow, "New Year", "a season across the new year");
  for (const c of [oct1, oct15, dec1, jan1]) assert.doesNotThrow(() => N.clean(c));
});

test("autoNewsletter: sends once a day, tells the owners, respects off and the postal address", async () => {
  const { db, net } = setup();
  for (let i = 0; i < 3; i++) await db.collection("subscribers").doc(`s${i}`).set({ email: `p${i}@example.com` });
  const when = Date.parse("2026-11-01T14:00:00Z");
  const r = await N.autoNewsletter(when, { pause: 0 });
  assert.equal(r.sent, 3);
  assert.equal(db.get("campaigns/auto-2026-11-01").by, "automatic");
  const note = net.emails.find((m) => !Array.isArray(m) && m.to[0] === "support@littlehivehouse.com");
  assert.match(note.subject, /enviado para 3 inscritos/);
  assert.deepEqual(await N.autoNewsletter(when, { pause: 0 }), { skipped: "already sent" });
  await db.collection("settings").doc("store").set({ autoNewsletter: 0 });
  assert.deepEqual(await N.autoNewsletter(Date.parse("2026-11-15T15:00:00Z"), { pause: 0 }), { skipped: "turned off" });
  await db.collection("settings").doc("store").set({ autoNewsletter: 1 });
  process.env.MAIL_POSTAL_ADDRESS = "";
  const before = net.emails.length;
  assert.deepEqual(await N.autoNewsletter(Date.parse("2026-11-15T15:00:00Z"), { pause: 0 }), { skipped: "no postal address" });
  assert.deepEqual(await N.autoNewsletter(Date.parse("2026-11-16T15:00:00Z"), { pause: 0 }), { skipped: "no postal address" });
  assert.equal(net.emails.length, before + 1, "the owners hear about it once a month");
  assert.match(net.emails[net.emails.length - 1].subject, /não foi enviado/);
  process.env.MAIL_POSTAL_ADDRESS = "PO Box 1, Carrollton, GA 30117";
});

test("opting out: the account switch and the unsubscribe link both keep someone off the list", async () => {
  const { db } = setup();
  const pub = require("../public");
  const mail = require("../mail");
  const user = { uid: "u1", token: { email: "ana@example.com", firebase: { sign_in_provider: "password" } } };
  await pub.setMarketing({ on: true }, user);
  assert.deepEqual(await N.recipients(), ["ana@example.com"]);
  await pub.setMarketing({ on: false }, user);
  assert.deepEqual(await N.recipients(), []);
  assert.equal(db.get("users/u1").marketing, false);
  await assert.rejects(pub.setMarketing({ on: true }, { uid: "anon", token: { firebase: { sign_in_provider: "anonymous" } } }), (e) => e.code === "unauthenticated");
  await pub.setMarketing({ on: true }, user);
  await pub.unsubscribe({ e: "ana@example.com", t: mail.unsubscribeToken("ana@example.com") });
  assert.deepEqual(await N.recipients(), []);
});
