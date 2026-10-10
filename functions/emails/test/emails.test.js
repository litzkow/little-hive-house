// node --test functions/emails/test
"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const { render, KINDS, MARKETING, trackingUrl } = require("..");
const { SAMPLES, EVIL, order, small } = require("../sample-data");

const SPEC_KINDS = ["order_confirmation", "shipped", "delivered_review", "refund", "welcome", "password_reset",
  "abandoned_checkout", "admin_new_order", "admin_dispute", "admin_delivery_check", "contact_autoreply", "admin_contact",
  "quote_received", "payment_link", "newsletter_welcome", "out_for_delivery", "verify_email"];

function clean(kind, r) {
  assert.ok(r.subject && r.subject.length > 3, `${kind}: subject`);
  assert.ok(!/[\r\n]/.test(r.subject), `${kind}: subject is one line`);
  assert.ok(r.html.startsWith("<!doctype html>"), `${kind}: html`);
  assert.ok(r.text.length > 60, `${kind}: text`);
  for (const bad of ["undefined", "NaN", "[object", "null"]) {
    for (const part of ["subject", "html", "text"]) assert.ok(!r[part].includes(bad), `${kind}: "${bad}" in ${part}`);
  }
  assert.ok(r.html.includes("support@littlehivehouse.com") && r.text.includes("support@littlehivehouse.com") || /admin|quote|contact/.test(kind), `${kind}: footer support`);
}

test("every kind from the spec exists", () => {
  for (const k of SPEC_KINDS) assert.ok(KINDS.includes(k), k);
});

test("every kind renders sample data cleanly", () => {
  for (const k of KINDS) clean(k, render(k, SAMPLES[k]));
});

test("every kind survives empty data", () => {
  for (const k of KINDS) clean(k, render(k, {}));
  for (const k of KINDS) clean(k, render(k, undefined));
});

test("unknown kind throws", () => {
  assert.throws(() => render("nope", {}), /Unknown email kind/);
  assert.throws(() => render("__proto__", {}), /Unknown email kind/);
});

test("user data is escaped everywhere", () => {
  const evilOrder = {
    ...order, name: EVIL, email: EVIL, giftMessage: EVIL, notes: EVIL, number: EVIL,
    shipping: { name: EVIL, phone: EVIL, address: { line1: EVIL, line2: EVIL, city: EVIL, state: EVIL, postal_code: EVIL, country: EVIL } },
    items: [
      { kind: "design", id: `x/"><script>`, title: EVIL, collection: EVIL, qty: 1, unit: 5 },
      { kind: "photos", packSize: 4, price: 14, notes: EVIL, photos: [{ frame: EVIL, caption: EVIL }] },
      { kind: "package", id: "x", title: EVIL, size: 25, price: 55, qty: 1 },
      { kind: "custom", title: EVIL, amount: 10 },
    ],
    pricing: { ...order.pricing, promo: { code: EVIL, amount: 1 } },
    fulfillment: { carrier: EVIL, carrierName: EVIL, tracking: EVIL, url: "javascript:alert(1)" },
  };
  const data = {
    order: evilOrder, refund: { amount: 5, reason: EVIL, note: EVIL }, name: EVIL, email: EVIL, message: EVIL, topic: EVIL,
    occasion: EVIL, quantity: EVIL, date: EVIL, title: EVIL, amount: 20, url: "javascript:alert(1)", note: EVIL, link: "javascript:alert(1)",
    dispute: { id: EVIL, reason: EVIL, status: EVIL, amount: 3 }, orders: [{ ...evilOrder, id: EVIL, tracking: EVIL, carrier: EVIL }],
    thankYouCode: { code: EVIL, percentOff: 10 }, promo: { code: EVIL, percentOff: 10 }, unsubscribeUrl: "javascript:alert(1)",
    instagram: EVIL, featured: [{ id: EVIL, title: EVIL }],
  };
  for (const k of KINDS) {
    const r = render(k, data);
    assert.ok(!r.html.includes("<script>"), `${k}: raw <script>`);
    assert.ok(!/<img src=x/i.test(r.html), `${k}: raw injected img`);
    // With quoted attribute values blanked out, no tag may carry an injected onerror attribute.
    assert.ok(!/<[^>]*\sonerror\s*=/i.test(r.html.replace(/"[^"]*"/g, '""')), `${k}: injected onerror attribute`);
    assert.ok(!/href="javascript:/i.test(r.html), `${k}: javascript: link`);
    assert.ok(!r.subject.includes("\n"), `${k}: subject newline`);
  }
});

test("marketing kinds carry the unsubscribe link and header", () => {
  for (const k of MARKETING) {
    const r = render(k, SAMPLES[k]);
    const u = SAMPLES[k].unsubscribeUrl;
    assert.ok(r.html.includes(u.replace(/&/g, "&amp;")), `${k}: unsubscribe in html`);
    assert.ok(r.text.includes(u), `${k}: unsubscribe in text`);
    assert.ok(r.headers && r.headers["List-Unsubscribe"].includes(u), `${k}: List-Unsubscribe`);
  }
});

test("order confirmation shows totals, links and thumbnails", () => {
  const r = render("order_confirmation", { order, siteUrl: "https://example.test/" });
  assert.match(r.html, /\$98\.64/);
  assert.match(r.html, /−\$27\.40/);
  assert.match(r.html, /https:\/\/example\.test\/order\.html\?id=Xq7Lp2mN4vR8/);
  assert.match(r.html, /https:\/\/example\.test\/track\.html/);
  assert.match(r.html, /https:\/\/example\.test\/assets\/email\/thumbs\/fall\/apple-picking\.jpg/);
  assert.match(r.html, /https:\/\/example\.test\/assets\/email\/thumbs\/frames\/instant\.jpg/);
  assert.match(r.html, /https:\/\/example\.test\/assets\/email\/logo\.png/);
  assert.match(r.text, /Happy birthday, Mom!/);
  assert.match(r.text, /3 to 5 business days|1 business day/);
  const g = render("order_confirmation", { order: small });
  assert.match(g.text, /Shipping: \$4\.95/);
  assert.match(g.text, /3 to 5 business days/);
  assert.match(g.text, /Canada/);
});

test("shipped uses the carrier tracking url", () => {
  const r = render("shipped", SAMPLES.shipped);
  assert.match(r.html, /tools\.usps\.com\/go\/TrackConfirmAction\?tLabels=9400/);
  assert.match(r.text, /Track your package: https:\/\/tools\.usps\.com/);
  assert.equal(trackingUrl("ups", "1Z 1"), "https://www.ups.com/track?tracknum=1Z%201");
  assert.equal(trackingUrl("other", "x", "https://carrier.test/x"), "https://carrier.test/x");
});

test("review stars link to the order page #review", () => {
  const r = render("delivered_review", SAMPLES.delivered_review);
  for (let n = 1; n <= 5; n++) assert.ok(r.html.includes(`order.html?id=Xq7Lp2mN4vR8&amp;rating=${n}#review`), `star ${n}`);
  assert.match(r.html, /THANKS15/);
  assert.ok(!render("delivered_review", { order }).html.includes("Your code"));
});

test("refund: full vs partial and friendly reason", () => {
  const partial = render("refund", SAMPLES.refund);
  assert.match(partial.subject, /partial refund of \$10\.00/);
  assert.match(partial.text, /arrived damaged/);
  assert.match(partial.text, /5 to 10 business days/);
  const full = render("refund", { order: { ...order, refundedTotal: order.pricing.total }, refund: { amount: order.pricing.total, reason: "not_delivered" } });
  assert.match(full.subject, /refund for LHH-1042 is on its way/);
  assert.match(full.text, /didn't arrive/);
});

test("welcome mentions a code only when a promo is passed", () => {
  assert.match(render("welcome", SAMPLES.welcome).text, /WELCOME10/);
  assert.ok(!render("welcome", { name: "Kim" }).text.includes("WELCOME10"));
});

test("password reset button and expiry", () => {
  const r = render("password_reset", SAMPLES.password_reset);
  assert.ok(r.html.includes(SAMPLES.password_reset.link.replace(/&/g, "&amp;")));
  assert.match(r.text, /expires in 1 hour/);
});

test("admin emails link to the admin and set replyTo where useful", () => {
  assert.match(render("admin_new_order", SAMPLES.admin_new_order).html, /\/admin\/#order\/Xq7Lp2mN4vR8/);
  assert.match(render("admin_new_order", SAMPLES.admin_new_order).text, /6 customer photos/);
  assert.equal(render("admin_contact", SAMPLES.admin_contact).replyTo, "karina@example.com");
  assert.equal(render("admin_contact", { email: "bad\nBcc: x@y" }).replyTo, undefined);
  const d = render("admin_delivery_check", SAMPLES.admin_delivery_check);
  assert.match(d.subject, /^3 shipments/);
  assert.match(d.text, /17 days/);
  assert.match(render("admin_dispute", SAMPLES.admin_dispute).html, /dashboard\.stripe\.com\/disputes\/dp_1Abc/);
});

test("payment link button", () => {
  const r = render("payment_link", SAMPLES.payment_link);
  assert.match(r.html, /checkout\.stripe\.com\/c\/pay\/cs_test_abc/);
  assert.match(r.text, /\$198\.00/);
  assert.match(r.text, /Pay securely: https:\/\/checkout\.stripe\.com/);
});

test("out for delivery: today, latest scan, tracking button, never a marketing email", () => {
  const r = render("out_for_delivery", SAMPLES.out_for_delivery);
  assert.match(r.subject, /^Karina, your magnets arrive today!$/);
  assert.match(r.html, /tools\.usps\.com\/go\/TrackConfirmAction\?tLabels=9400/);
  assert.match(r.text, /Latest scan: Out for Delivery, Expected Delivery by 9:00pm \(Sharpsburg, GA, Oct 15, 2026/);
  assert.match(r.text, /Follow your package: https:\/\/tools\.usps\.com/);
  assert.match(r.text, /125 Peachtree Lane/);
  assert.ok(!r.headers, "transactional: no List-Unsubscribe");
  assert.ok(!MARKETING.includes("out_for_delivery"));
  // no scans yet: still a clean email
  const bare = render("out_for_delivery", { order: { number: "LHH-1", fulfillment: { carrier: "ups", tracking: "1Z1" } } });
  assert.match(bare.text, /UPS has your package out for delivery/);
  assert.ok(!bare.text.includes("Latest scan"));
});

test("verify email: confirm button with the Firebase link, explains guest orders", () => {
  const r = render("verify_email", SAMPLES.verify_email);
  assert.ok(r.html.includes(SAMPLES.verify_email.link.replace(/&/g, "&amp;")), "link in html");
  assert.match(r.text, /Confirm my email: https:\/\/little-hive-house\.firebaseapp\.com\/__\/auth\/action\?mode=verifyEmail/);
  assert.match(r.text, /karina@example\.com/);
  assert.match(r.text, /placed as a guest/);
  assert.match(r.subject, /confirm your email/i);
  assert.ok(!render("verify_email", { link: "javascript:alert(1)" }).html.includes("javascript:"));
});

test("shipped mentions the automatic updates only when tracking follows the carrier", () => {
  assert.match(render("shipped", SAMPLES.shipped).text, /out for delivery, and when it arrives/);
  assert.ok(!/out for delivery, and when it arrives/.test(render("shipped", { order }).text));
});

test("automatic-tracking alert lists each problem for the shop", () => {
  const d = render("admin_delivery_check", SAMPLES.admin_delivery_check_tracking);
  assert.match(d.subject, /^2 shipments need a look \(automatic tracking\)$/);
  assert.match(d.text, /Notice Left \(No Authorized Recipient Available\)/);
  assert.match(d.text, /No new scan for 8 days\./);
  assert.match(d.html, /\/admin\/#order\/Xq7Lp2mN4vR8/);
  assert.match(d.text, /customers were not emailed/i);
});

test("photo packs: frames from emailOrder-style photos show the frame strip", () => {
  const photos = [{ frame: "instant", caption: "Summer" }, { frame: "floral", caption: "" }, { frame: "stamp", caption: "" }];
  const r = render("order_confirmation", { order: { ...small, items: [{ kind: "photos", packSize: 4, price: 14, qty: 1, photos }] } });
  for (const f of ["instant", "floral", "stamp"]) assert.match(r.html, new RegExp(`thumbs/frames/${f}\\.jpg`), f);
  assert.match(r.text, /captions: Summer/);
});
