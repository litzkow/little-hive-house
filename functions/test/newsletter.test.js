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
