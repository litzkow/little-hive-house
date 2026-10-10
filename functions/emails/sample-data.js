// Realistic sample data for every email kind (used by the tests and by the preview renderer).
"use strict";

const order = {
  id: "Xq7Lp2mN4vR8",
  number: "LHH-1042",
  uid: "u_abc123",
  email: "karina@example.com",
  name: "Karina Vargas",
  status: "paid",
  items: [
    { kind: "design", id: "fall/apple-picking", title: "Apple Picking", collection: "fall", qty: 2, unit: 5 },
    { kind: "design", id: "places/new-york", title: "New York", collection: "places", qty: 1, unit: 5 },
    { kind: "design", id: "bee-kind/bee-happy", title: "Bee Happy", collection: "bee-kind", qty: 1, unit: 5 },
    {
      kind: "photos", packSize: 9, price: 25, notes: "Please make the beach one extra bright!",
      photos: [
        { path: "uploads/u_abc123/p1/0.jpg", frame: "instant", caption: "Summer 2026" },
        { path: "uploads/u_abc123/p1/1.jpg", frame: "instant", caption: "" },
        { path: "uploads/u_abc123/p1/2.jpg", frame: "floral", caption: "" },
        { path: "uploads/u_abc123/p1/3.jpg", frame: "stamp", caption: "With love" },
        { path: "uploads/u_abc123/p1/4.jpg", frame: "honeycomb", caption: "" },
        { path: "uploads/u_abc123/p1/5.jpg", frame: "none", caption: "" },
      ],
    },
    { kind: "package", id: "weddings-50", title: "Weddings & save the dates", size: 50, price: 95, qty: 1 },
  ],
  pricing: {
    subtotal: 140, bundleDiscount: 3, volumePct: 20, volumeDiscount: 27.4, promo: { code: "WELCOME10", amount: 10.96 },
    shipping: 0, total: 98.64, currency: "usd",
  },
  shipping: {
    name: "Karina Vargas", phone: "(404) 555-0182",
    address: { line1: "125 Peachtree Lane", line2: "Apt 4B", city: "Sharpsburg", state: "GA", postal_code: "30277", country: "US" },
  },
  giftMessage: "Happy birthday, Mom! For your fridge full of memories. Love, K",
  notes: "Ring the bell, the dog is friendly.",
  stripe: { sessionId: "cs_test_123", paymentIntent: "pi_123", customer: "cus_123", fee: 3.27 },
  fulfillment: { carrier: "usps", tracking: "9400 1118 9922 3344 5566 77", url: "", labelCost: 4.5, shippedAt: "2026-10-12T15:00:00Z", deliveredAt: null },
  refunds: [],
  refundedTotal: 0,
  createdAt: "2026-10-10T14:20:00Z",
  paidAt: "2026-10-10T14:22:00Z",
};

const small = {
  id: "Zt9", number: "LHH-1043", uid: null, email: "sam@example.com", name: "Sam Lee",
  items: [{ kind: "design", id: "halloween/boo", title: "Boo", collection: "halloween", qty: 1, unit: 5 }],
  pricing: { subtotal: 5, bundleDiscount: 0, volumePct: 0, volumeDiscount: 0, promo: null, shipping: 4.95, total: 9.95, currency: "usd" },
  shipping: { name: "Sam Lee", address: { line1: "9 King St W", city: "Toronto", state: "ON", postal_code: "M5H 1A1", country: "CA" } },
  createdAt: "2026-10-10T14:20:00Z", paidAt: "2026-10-10T14:22:00Z",
};

const unsub = "https://littlehivehouse.com/unsubscribe.html?e=karina%40example.com&t=3f9a0c";

const SAMPLES = {
  order_confirmation: { order },
  shipped: { order: { ...order, status: "shipped", fulfillment: { ...order.fulfillment, autoUpdates: true } } },
  out_for_delivery: {
    order: {
      ...order, status: "shipped",
      fulfillment: {
        ...order.fulfillment, trackingStatus: "out_for_delivery",
        events: [
          { at: "2026-10-15T12:41:00Z", status: "out_for_delivery", text: "Out for Delivery, Expected Delivery by 9:00pm", location: "Sharpsburg, GA" },
          { at: "2026-10-15T10:02:00Z", status: "in_transit", text: "Arrived at Post Office", location: "Sharpsburg, GA" },
        ],
      },
    },
  },
  delivered_review: { order: { ...order, status: "delivered" }, thankYouCode: { code: "THANKS15", percentOff: 15, expiresAt: "2026-12-31T00:00:00Z" } },
  refund: { order: { ...order, refundedTotal: 10 }, refund: { amount: 10, reason: "damaged", note: "So sorry the New York magnet cracked in the mail. We're also sending a fresh one, on us." } },
  welcome: { name: "Karina Vargas", email: "karina@example.com", promo: { code: "WELCOME10", percentOff: 10 } },
  verify_email: { email: "karina@example.com", name: "Karina Vargas", link: "https://little-hive-house.firebaseapp.com/__/auth/action?mode=verifyEmail&oobCode=xyz789&apiKey=key&continueUrl=https%3A%2F%2Flittlehivehouse.com%2Faccount.html%3Fverified%3D1&lang=en" },
  password_reset: { email: "karina@example.com", name: "Karina", link: "https://little-hive-house.firebaseapp.com/__/auth/action?mode=resetPassword&oobCode=abc123XYZ&apiKey=key&lang=en", expiresMinutes: 60 },
  abandoned_checkout: { order: { ...small, status: "pending", items: order.items.slice(0, 3), pricing: { subtotal: 20, bundleDiscount: 3, shipping: 4.95, total: 21.95, currency: "usd" } }, unsubscribeUrl: unsub },
  admin_new_order: { order },
  admin_dispute: { order: { ...order, status: "shipped" }, dispute: { id: "dp_1Abc", amount: 98.64, reason: "product_not_received", status: "needs_response", evidenceDueBy: "2026-10-28T23:59:00Z" } },
  admin_delivery_check: {
    now: "2026-10-30T12:00:00Z",
    orders: [
      { id: "Xq7Lp2mN4vR8", number: "LHH-1042", name: "Karina Vargas", email: "karina@example.com", carrier: "usps", tracking: "9400111899223344556677", shippedAt: "2026-10-12T15:00:00Z" },
      { id: "Ab12", number: "LHH-1038", name: "Sam Lee", email: "sam@example.com", carrier: "ups", tracking: "1Z999AA10123456784", shippedAt: "2026-10-08T15:00:00Z" },
      { id: "Cd34", number: "LHH-1035", name: "Ana Souza", email: "ana@example.com", carrier: "other", carrierName: "Canada Post", tracking: "LM123456789CA", url: "https://www.canadapost-postescanada.ca/track-reperage/en#/details/LM123456789CA", shippedAt: "2026-10-05T15:00:00Z" },
    ],
  },
  admin_delivery_check_tracking: {
    mode: "tracking",
    now: "2026-10-20T14:00:00Z",
    orders: [
      { id: "Xq7Lp2mN4vR8", number: "LHH-1042", name: "Karina Vargas", email: "karina@example.com", carrier: "usps", tracking: "9400111899223344556677", shippedAt: "2026-10-12T15:00:00Z", issue: "Notice Left (No Authorized Recipient Available)", issueKind: "exception" },
      { id: "Ab12", number: "LHH-1038", name: "Sam Lee", email: "sam@example.com", carrier: "ups", tracking: "1Z999AA10123456784", shippedAt: "2026-10-08T15:00:00Z", issue: "No new scan for 8 days.", issueKind: "stalled" },
    ],
  },
  contact_autoreply: { name: "Karina Vargas", email: "karina@example.com", topic: "Photo magnets", message: "Hi! Can I mix two frames in one pack?\nThanks!" },
  admin_contact: { name: "Karina Vargas", email: "karina@example.com", topic: "Photo magnets", message: "Hi! Can I mix two frames in one pack?\nThanks!", orderNumber: "LHH-1042", at: "2026-10-10T18:05:00Z" },
  quote_received: { name: "Ana Souza", email: "ana@example.com", occasion: "Weddings", quantity: 120, date: "2027-05-14", message: "Save the dates with our engagement photo, sage green and gold." },
  admin_quote: { name: "Ana Souza", email: "ana@example.com", occasion: "Weddings", quantity: 120, date: "2027-05-14", message: "Save the dates with our engagement photo, sage green and gold." },
  payment_link: { name: "Ana Souza", email: "ana@example.com", title: "120 wedding save-the-date magnets", amount: 198, url: "https://checkout.stripe.com/c/pay/cs_test_abc", note: "Includes custom design, one proof round and free shipping.", expiresAt: "2026-10-31T00:00:00Z" },
  newsletter_welcome: { email: "karina@example.com", unsubscribeUrl: unsub, promo: { code: "HELLO10", percentOff: 10 } },
};

// Nasty input for escaping tests: every user-controlled string carries markup.
const EVIL = '<script>alert("x")</script><img src=x onerror=alert(1)>&';

module.exports = { SAMPLES, EVIL, order, small };
