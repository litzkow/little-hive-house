"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const O = require("../orders");
const { lateShipments } = require("../scheduled");

test("order numbers: first is LHH-1001, then +1; formatting and parsing", () => {
  assert.equal(O.nextOrderNumber(undefined), 1001);
  assert.equal(O.nextOrderNumber(null), 1001);
  assert.equal(O.nextOrderNumber(0), 1001);
  assert.equal(O.nextOrderNumber(1001), 1002);
  assert.equal(O.nextOrderNumber(99999), 100000);
  assert.equal(O.formatOrderNumber(1001), "LHH-1001");
  assert.throws(() => O.formatOrderNumber(0));
  assert.throws(() => O.formatOrderNumber(1.5));
  for (const s of ["LHH-1001", "lhh-1001", "LHH1001", "#1001", "1001", " lhh - 1001 "]) assert.equal(O.normalizeOrderNumber(s), "LHH-1001", s);
  for (const s of ["", "abc", "LHH-", "12", null, "LHH-1001x"]) assert.equal(O.normalizeOrderNumber(s), null, String(s));
});

test("status transitions", () => {
  assert.ok(O.canTransition("pending", "paid"));
  assert.ok(O.canTransition("paid", "in_production"));
  assert.ok(O.canTransition("in_production", "shipped"));
  assert.ok(O.canTransition("shipped", "delivered"));
  assert.ok(O.canTransition("delivered", "refunded"));
  assert.ok(O.canTransition("partially_refunded", "shipped"));
  assert.ok(!O.canTransition("pending", "shipped"));
  assert.ok(!O.canTransition("refunded", "paid"));
  assert.ok(!O.canTransition("canceled", "paid"));
  assert.ok(!O.canTransition("delivered", "pending"));
  for (const s of O.STATUSES) assert.ok(O.TRANSITIONS[s], s);

  const paid = { status: "paid", pricing: { total: 20 }, refundedTotal: 0, refunds: [] };
  assert.equal(O.manualStatusError(paid, "in_production"), null);
  assert.match(O.manualStatusError(paid, "canceled"), /Refund this order first/);
  assert.match(O.manualStatusError(paid, "refunded"), /Refund button/);
  assert.match(O.manualStatusError(paid, "paid"), /already/);
  assert.match(O.manualStatusError(paid, "bogus"), /Unknown/);
  assert.match(O.manualStatusError({ status: "pending" }, "paid"), /Stripe/);
  assert.equal(O.manualStatusError({ status: "pending", pricing: { total: 20 } }, "canceled"), null);
  assert.match(O.manualStatusError({ status: "refunded", pricing: { total: 20 }, refundedTotal: 20 }, "in_production"), /can't be changed/);
  assert.equal(O.manualStatusError({ status: "partially_refunded", pricing: { total: 20 }, refunds: [{ amount: 20 }] }, "canceled"), null);
});

test("refund math: never more than paid minus refunded", () => {
  const o = { status: "delivered", pricing: { total: 30.95 }, refunds: [{ id: "re_1", amount: 10 }], refundedTotal: 10 };
  assert.equal(O.refundableCents(o), 2095);
  assert.deepEqual(O.checkRefund(o, 5, "damaged"), { amountCents: 500, full: false });
  assert.deepEqual(O.checkRefund(o, 20.95, "damaged"), { amountCents: 2095, full: true });
  assert.throws(() => O.checkRefund(o, 20.96, "damaged"), /at most \$20\.95/);
  assert.throws(() => O.checkRefund(o, 0, "damaged"), /more than/);
  assert.throws(() => O.checkRefund(o, -1, "damaged"), /more than/);
  assert.throws(() => O.checkRefund(o, "abc", "damaged"), /more than/);
  assert.throws(() => O.checkRefund(o, 1.005, "damaged"), /2 decimals/);
  assert.throws(() => O.checkRefund(o, 1, "because"), /reason/);
  assert.throws(() => O.checkRefund({ ...o, status: "pending" }, 1, "damaged"), /can't be refunded/);
  assert.throws(() => O.checkRefund({ ...o, status: "refunded" }, 1, "damaged"), /can't be refunded/);
  const done = { status: "partially_refunded", pricing: { total: 10 }, refunds: [{ amount: 10 }] };
  assert.throws(() => O.checkRefund(done, 1, "other"), /already been fully refunded/);
  // failed refunds don't count
  assert.equal(O.refundableCents({ pricing: { total: 10 }, refunds: [{ amount: 10, status: "failed" }] }), 1000);
  // floating point: 0.1 + 0.2 style amounts
  const fp = { status: "paid", pricing: { total: 0.3 }, refunds: [{ amount: 0.1 }, { amount: 0.2 }] };
  assert.equal(O.refundableCents(fp), 0);
  assert.equal(O.statusAfterRefund({ status: "paid", pricing: { total: 10 } }, 500), "partially_refunded");
  assert.equal(O.statusAfterRefund({ status: "paid", pricing: { total: 10 } }, 1000), "refunded");
});

test("mergeRefunds dedups by id and keeps admin metadata", () => {
  const existing = [{ id: "re_1", amount: 5, reason: "damaged", note: "one cracked", at: "2026-10-01T00:00:00.000Z", by: "me", status: "succeeded" }];
  const m = O.mergeRefunds(existing, [
    { id: "re_1", amount: 500, status: "succeeded", metadata: {} },
    { id: "re_2", amount: 250, status: "succeeded", created: 1760000000, metadata: {} },
    { id: "re_3", amount: 100, status: "succeeded", metadata: { reason: "late", note: "sorry", by: "karina@x.com" } },
  ], "2026-10-10T00:00:00.000Z");
  assert.equal(m.refunds.length, 3);
  assert.equal(m.added.length, 2);
  assert.equal(m.refundedTotal, 8.5);
  assert.equal(m.refunds[0].note, "one cracked");
  assert.equal(m.refunds[1].reason, "other");
  assert.equal(m.refunds[1].by, "stripe-dashboard");
  assert.equal(m.refunds[2].reason, "late");
  assert.equal(m.refunds[2].by, "karina@x.com");
  assert.equal(O.mergeRefunds(m.refunds, [{ id: "re_2", amount: 250 }]).added.length, 0);
});

test("tracking links per carrier", () => {
  assert.match(O.trackingUrl("usps", "9400 1"), /usps\.com.*9400%201/);
  assert.match(O.trackingUrl("ups", "1Z"), /ups\.com/);
  assert.match(O.trackingUrl("fedex", "1"), /fedex\.com/);
  assert.match(O.trackingUrl("dhl", "1"), /dhl\.com/);
  assert.equal(O.trackingUrl("other", "1"), "");
  assert.equal(O.trackingUrl("other", "1", "https://track.example/1"), "https://track.example/1");
  assert.equal(O.trackingUrl("usps", "1", "javascript:alert(1)").startsWith("https://tools.usps.com"), true);
});

const fullOrder = () => ({
  number: "LHH-1001", uid: "uid_secret", guestUid: "anon_secret", email: "buyer@example.com", name: "Ana Souza", status: "shipped",
  items: [
    { kind: "design", id: "places/new-york", title: "New York", collection: "places", qty: 2, unit: 5 },
    { kind: "photos", title: "Custom photo magnets (pack of 4)", packSize: 4, price: 14, qty: 1, notes: "crop grandma in",
      photos: [{ path: "uploads/anon_secret/p/1.jpg", frame: "instant", caption: "Summer" }] },
    { kind: "package", id: "teams-12", title: "Teams & schools, 12 magnets", size: 12, price: 30, qty: 1 },
    { kind: "custom", title: "Quote", amount: 99 },
  ],
  pricing: { subtotal: 54, bundleDiscount: 0, volumePct: 10, volumeDiscount: 5.4, promo: { code: "HI", amount: 1 }, shipping: 0, total: 47.6, currency: "usd" },
  shipping: { name: "Ana Souza", phone: "+1 555 0100", address: { line1: "1 Secret St", line2: "Apt 2", city: "Atlanta", state: "GA", postal_code: "30301", country: "US" } },
  giftMessage: "Happy birthday", notes: "leave at door", marketing: true,
  stripe: { sessionId: "cs_secret", paymentIntent: "pi_secret", customer: "cus_secret", fee: 1.68 },
  fulfillment: { carrier: "usps", tracking: "9400", url: "https://tools.usps.com/x", labelCost: 4.5, shippedAt: "2026-10-02T00:00:00.000Z", deliveredAt: null },
  refunds: [{ id: "re_secret", amount: 2, reason: "damaged", note: "INTERNAL NOTE", at: "2026-10-03T00:00:00.000Z", by: "owner@x.com", status: "succeeded" }],
  refundedTotal: 2,
  adminNotes: [{ at: "2026-10-01T00:00:00.000Z", by: "owner@x.com", text: "INTERNAL ADMIN NOTE" }],
  timeline: [{ at: "2026-10-01T00:00:00.000Z", status: "paid", text: "Payment received. Thank you!" }],
  emails: { confirmation: "2026-10-01T00:00:00.000Z" }, dispute: { id: "dp_secret" },
  createdAt: "2026-10-01T00:00:00.000Z", paidAt: "2026-10-01T00:00:00.000Z", updatedAt: "x", abandonedAt: null,
});

test("public order view leaks no internal fields", () => {
  const v = O.publicOrderView("ord1", fullOrder());
  const json = JSON.stringify(v);
  for (const secret of ["uid_secret", "anon_secret", "buyer@example.com", "cs_secret", "pi_secret", "cus_secret", "re_secret", "dp_secret",
    "INTERNAL", "owner@x.com", "1 Secret St", "Apt 2", "30301", "+1 555", "leave at door", "Happy birthday", "crop grandma", "uploads/"]) {
    assert.ok(!json.includes(secret), `leaked ${secret}`);
  }
  for (const k of ["uid", "guestUid", "email", "stripe", "adminNotes", "emails", "notes", "giftMessage", "marketing", "dispute", "shipping", "updatedAt"]) {
    assert.ok(!(k in v), `key ${k}`);
  }
  assert.ok(!("labelCost" in v.fulfillment));
  assert.ok(!("fee" in v.pricing));
  assert.ok(!("note" in v.refunds[0]) && !("by" in v.refunds[0]) && !("id" in v.refunds[0]));
  // what the customer does need
  assert.equal(v.number, "LHH-1001");
  assert.equal(v.status, "shipped");
  assert.equal(v.firstName, "Ana");
  assert.equal(v.items.length, 4);
  assert.equal(v.items[1].photoCount, 1);
  assert.equal(v.items[1].frames[0].frame, "instant");
  assert.equal(v.fulfillment.tracking, "9400");
  assert.equal(v.fulfillment.carrierName, "USPS");
  assert.deepEqual(v.shipTo, { city: "Atlanta", state: "GA", country: "US" });
  assert.equal(v.refunds[0].reasonLabel, "Arrived damaged");
  assert.equal(v.pricing.total, 47.6);
});

test("owner view adds only the buyer's own address and gift message; tracking scans are public-safe", () => {
  const o = fullOrder();
  o.fulfillment = { ...o.fulfillment, trackingStatus: "in_transit", trackingDetail: "Arrived at facility", lastCheckedAt: "2026-10-03T00:00:00.000Z",
    events: [{ at: "2026-10-03T00:00:00.000Z", status: "in_transit", text: "Arrived at USPS Regional Facility", location: "Atlanta, GA", raw: "SECRETRAW" }],
    alerts: { exception: "ALERTKEY" }, trackingSource: "usps" };
  const v = O.publicOrderView("ord1", o, { owner: true });
  const json = JSON.stringify(v);
  for (const secret of ["uid_secret", "anon_secret", "buyer@example.com", "cs_secret", "pi_secret", "re_secret", "dp_secret", "INTERNAL", "owner@x.com",
    "leave at door", "crop grandma", "uploads/", "SECRETRAW", "ALERTKEY", "+1 555"]) {
    assert.ok(!json.includes(secret), `leaked ${secret}`);
  }
  assert.equal(v.shipping.address.line1, "1 Secret St");
  assert.equal(v.giftMessage, "Happy birthday");
  assert.equal(v.fulfillment.trackingStatus, "in_transit");
  assert.equal(v.fulfillment.trackingStatusLabel, "In transit");
  assert.deepEqual(v.fulfillment.events, [{ at: "2026-10-03T00:00:00.000Z", status: "in_transit", text: "Arrived at USPS Regional Facility", location: "Atlanta, GA" }]);
  assert.ok(!("alerts" in v.fulfillment) && !("trackingSource" in v.fulfillment));
  const guest = O.publicOrderView("ord1", o);
  assert.ok(!("shipping" in guest) && !("giftMessage" in guest));
  assert.equal(guest.fulfillment.events.length, 1);
});

test("email data has links and thumbnails", () => {
  const e = O.emailOrder("ord1", fullOrder());
  assert.equal(e.firstName, "Ana");
  assert.match(e.items[0].thumb, /\/assets\/email\/thumbs\/places\/new-york\.jpg$/);
  assert.match(e.items[1].thumb, /\/assets\/email\/thumbs\/frames\/instant\.jpg$/);
  assert.equal(e.items[0].lineTotal, 10);
  assert.match(e.links.order, /order\.html\?id=ord1$/);
  assert.match(e.links.track, /track\.html\?number=LHH-1001&email=buyer%40example\.com$/);
  assert.equal(e.links.admin, "https://littlehivehouse.com/admin/#order/ord1", "the admin router's own format");
  // photo packs: [{frame, caption}] reach the emails (frame strip), storage paths don't
  assert.deepEqual(e.items[1].photos, [{ frame: "instant", caption: "Summer" }]);
  assert.ok(!JSON.stringify(e.items).includes("uploads/"));
});

test("delivery follow-up picks shipped orders 10+ days old only", () => {
  const now = Date.parse("2026-10-20T12:00:00Z");
  const docs = [
    { id: "a", data: { status: "shipped", number: "LHH-1", fulfillment: { shippedAt: "2026-10-01T00:00:00Z" } } },
    { id: "b", data: { status: "shipped", number: "LHH-2", fulfillment: { shippedAt: "2026-10-15T00:00:00Z" } } },
    { id: "c", data: { status: "delivered", number: "LHH-3", fulfillment: { shippedAt: "2026-09-01T00:00:00Z" } } },
    { id: "d", data: { status: "shipped", number: "LHH-4", fulfillment: { shippedAt: "2026-10-10T12:00:00Z" } } },
    { id: "e", data: { status: "shipped", number: "LHH-5", fulfillment: {} } },
  ];
  const late = lateShipments(docs, now);
  assert.deepEqual(late.map((o) => o.number), ["LHH-1", "LHH-4"]);
  assert.equal(late[0].days, 19);
});
