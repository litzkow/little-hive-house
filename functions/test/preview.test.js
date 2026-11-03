"use strict";
/* Hive Admin › order › Emails to the customer: tapping one shows it (adminPreviewEmail), nothing is sent. */
const test = require("node:test");
const assert = require("node:assert/strict");
const { FakeDB, FakeAuth, FakeBucket, fakeNet } = require("./fakes");
const deps = require("../deps");

const ADMIN = { uid: "admin1", token: { admin: true, email: "owner@lhh.com" } };

test("every customer email can be previewed for an order, without sending it", async () => {
  Object.assign(process.env, { RESEND_API_KEY: "re_x", ADMIN_EMAILS: "owner@lhh.com", SITE_URL: "https://littlehivehouse.com",
    MAIL_FROM: "Little Hive House <hello@littlehivehouse.com>", MAIL_ADMIN: "support@littlehivehouse.com" });
  const db = new FakeDB(), net = fakeNet();
  deps.set({ db, auth: new FakeAuth(), bucket: new FakeBucket() });
  globalThis.fetch = net.fetch;
  db.docs.set("orders/o1", { status: "shipped", number: "LHH-1002", email: "randy@example.com", name: "Randy",
    items: [{ kind: "design", id: "places/savannah", title: "Savannah", qty: 2, price: 5 }],
    shipping: { name: "Randy", address: { line1: "1 Main St", city: "Mundelein", state: "IL", postal_code: "60060", country: "US" } },
    pricing: { subtotal: 10, shipping: 5.49, total: 15.49 }, paidAt: "2026-11-03T06:30:00Z",
    fulfillment: { carrier: "usps", tracking: "9400111899223344556677", shippedAt: "2026-11-03T06:30:00Z" } });
  const admin = require("../admin");
  for (const kind of ["order_confirmation", "shipped", "out_for_delivery", "delivered_review", "refund"]) {
    const r = await admin.adminPreviewEmail({ orderId: "o1", kind }, ADMIN);
    assert.ok(r.subject, `${kind} has a subject`);
    assert.match(r.html, /<html|<table|<div/i, `${kind} has a body`);
  }
  const shipped = await admin.adminPreviewEmail({ orderId: "o1", kind: "shipped" }, ADMIN);
  assert.match(shipped.html, /9400111899223344556677/);
  const refund = await admin.adminPreviewEmail({ orderId: "o1", kind: "refund" }, ADMIN);
  assert.equal(refund.sample, true);
  assert.equal(net.emails.length, 0, "nothing was sent");
  await assert.rejects(admin.adminPreviewEmail({ orderId: "o1", kind: "spam" }, ADMIN), (e) => e.code === "invalid-argument");
  // the Google review button shows only once the link is saved in Settings
  let d = await admin.adminPreviewEmail({ orderId: "o1", kind: "delivered_review" }, ADMIN);
  assert.doesNotMatch(d.html, /Review us on Google/);
  await assert.rejects(admin.adminSaveSettings({ settings: { googleReviewUrl: "https://evil.example/review" } }, ADMIN), (e) => e.code === "invalid-argument");
  await admin.adminSaveSettings({ settings: { googleReviewUrl: "https://g.page/r/CabcdEFG123/review" } }, ADMIN);
  d = await admin.adminPreviewEmail({ orderId: "o1", kind: "delivered_review" }, ADMIN);
  assert.match(d.html, /Review us on Google/);
  assert.match(d.html, /g\.page\/r\/CabcdEFG123\/review/);
  await assert.rejects(admin.adminPreviewEmail({ orderId: "o1", kind: "shipped" }, { uid: "x", token: {} }));
});
