"use strict";
/* Ideas box (public.suggest): saved for the admin, emailed to the owners (in Portuguese, reply goes to the customer)
   and pushed to their phones; name and email optional, spam trap and bad emails refused. */
const test = require("node:test");
const assert = require("node:assert/strict");
const { FakeDB, FakeAuth, FakeBucket, fakeNet } = require("./fakes");
const deps = require("../deps");
const push = require("../push");

function setup() {
  Object.assign(process.env, { STRIPE_SECRET_KEY: "sk_test_x", RESEND_API_KEY: "re_x", ADMIN_EMAILS: "owner@lhh.com", SITE_URL: "https://littlehivehouse.com",
    MAIL_ADMIN: "support@littlehivehouse.com" });
  const db = new FakeDB(), net = fakeNet();
  deps.set({ db, auth: new FakeAuth(), bucket: new FakeBucket(), getDownloadURL: async () => null });
  globalThis.fetch = net.fetch;
  push.resetCache();
  const pushed = [];
  push.setSender(async (sub, payload) => { pushed.push(JSON.parse(payload)); return { statusCode: 201 }; });
  return { db, net, pushed };
}
const req = { ip: "7.7.7.7", headers: {} };

test("an idea with an email: saved, emailed to the owners with reply-to, pushed to the phone", async () => {
  const { db, net, pushed } = setup();
  await db.collection("adminPush").doc("p1").set({ endpoint: "https://web.push.apple.com/x", keys: { p256dh: "B".repeat(87), auth: "a".repeat(22) }, uid: "admin1", prefs: {} });
  const pub = require("../public");
  const r = await pub.suggest({ kind: "place", idea: "A magnet of the Tybee Island lighthouse, please!", name: "Ana Souza", email: "Ana@Example.com" }, null, req);
  assert.equal(r.ok, true);
  const doc = db.get(`suggestions/${r.id}`);
  assert.equal(doc.kind, "place");
  assert.equal(doc.kindLabel, "A place to draw");
  assert.equal(doc.email, "ana@example.com");
  assert.equal(doc.status, "new");
  const mail = net.emails.at(-1);
  assert.deepEqual(mail.to, ["support@littlehivehouse.com"]);
  assert.equal(mail.reply_to, "ana@example.com");
  assert.match(mail.subject, /Um cliente mandou uma sugestão/);
  assert.match(mail.html, /Tybee Island lighthouse/);
  assert.match(mail.html, /Um lugar para desenhar/);
  assert.equal(pushed.length, 1);
  assert.equal(pushed[0].title, "💡 Um cliente mandou uma sugestão");
  assert.match(pushed[0].body, /^Ana: A magnet of the Tybee/);
  assert.match(pushed[0].url, /#messages\?tab=suggestions$/);
});

test("an anonymous idea works; unknown kinds become 'other'; empty ideas, bad emails and bots are refused", async () => {
  const { db, net } = setup();
  const pub = require("../public");
  const r = await pub.suggest({ kind: "hack", idea: "A cat in a hammock design" }, null, req);
  const doc = db.get(`suggestions/${r.id}`);
  assert.equal(doc.kind, "other");
  assert.equal(doc.name, "");
  assert.equal(doc.email, "");
  assert.equal(net.emails.at(-1).reply_to, undefined);
  assert.match(net.emails.at(-1).html, /Não informou/);
  await assert.rejects(pub.suggest({ idea: "  " }, null, req), (e) => e.code === "invalid-argument");
  await assert.rejects(pub.suggest({ idea: "Nice idea", email: "not-an-email" }, null, req), (e) => e.code === "invalid-argument");
  const before = [...db.docs.keys()].filter((k) => k.startsWith("suggestions/")).length;
  assert.deepEqual(await pub.suggest({ idea: "buy cheap pills", website: "http://spam" }, null, req), { ok: true });
  assert.equal([...db.docs.keys()].filter((k) => k.startsWith("suggestions/")).length, before, "the spam trap saves nothing");
});
