"use strict";
/* Automatic delivery tracking: parsers (realistic USPS v3 and Shippo answers), the pure planner, and the scheduled run
   end to end against an in-memory Firestore with fake USPS / Shippo / Resend endpoints. */
const test = require("node:test");
const assert = require("node:assert/strict");
const T = require("../tracking");
const { FakeDB, FakeAuth, FakeBucket, fakeNet, clone } = require("./fakes");
const deps = require("../deps");

/* ---------------------------------------------------------------- sample payloads */
const uspsEvent = (eventType, gmt, eventCode, city = "SHARPSBURG", state = "GA", zip = "30277") => ({
  eventType, eventTimestamp: gmt.replace(/\.000Z$|Z$/, ""), GMTTimestamp: gmt, GMTOffset: "-04:00", eventCountry: "", eventCity: city,
  eventState: state, eventZIP: zip, firm: null, name: null, authorizedAgent: false, eventCode, actionCode: null, reasonCode: null,
});
const USPS_EARLY = [
  uspsEvent("Arrived at USPS Regional Facility", "2026-10-13T02:10:00.000Z", "10", "ATLANTA GA DISTRIBUTION CENTER", "", ""),
  uspsEvent("USPS picked up item", "2026-10-12T21:30:00.000Z", "03", "NEWNAN", "GA", "30263"),
  uspsEvent("Shipping Label Created, USPS Awaiting Item", "2026-10-12T15:04:00.000Z", "GX", "NEWNAN", "GA", "30263"),
];
const uspsBase = {
  trackingNumber: "9400111899223344556677", mailClass: "USPS Ground Advantage", mailType: "DOMESTIC_MAIL",
  destinationCity: "SHARPSBURG", destinationState: "GA", destinationZIP: "30277", originCity: "NEWNAN", originState: "GA", originZIP: "30263",
  emailEnabled: true, proofOfDeliveryEnabled: false, redeliveryEnabled: false, itemShape: "PARCEL",
};
const USPS = {
  inTransit: { ...uspsBase, status: "Arrived at USPS Regional Facility", statusCategory: "In Transit",
    statusSummary: "Your item arrived at our ATLANTA GA DISTRIBUTION CENTER destination facility on October 12, 2026 at 10:10 pm.",
    expectedDeliveryTimeStamp: "2026-10-15T21:00:00Z", trackingEvents: USPS_EARLY },
  outForDelivery: { ...uspsBase, status: "Out for Delivery, Expected Delivery by 9:00pm", statusCategory: "Out for Delivery",
    statusSummary: "Your item is out for delivery on October 15, 2026 at 8:41 am in SHARPSBURG, GA 30277.",
    trackingEvents: [uspsEvent("Out for Delivery", "2026-10-15T12:41:00.000Z", "OF"), uspsEvent("Arrived at Post Office", "2026-10-15T10:02:00.000Z", "07"), ...USPS_EARLY] },
  delivered: { ...uspsBase, status: "Delivered, In/At Mailbox", statusCategory: "Delivered",
    statusSummary: "Your item was delivered in or at the mailbox at 1:12 pm on October 15, 2026 in SHARPSBURG, GA 30277.",
    trackingEvents: [uspsEvent("Delivered, In/At Mailbox", "2026-10-15T17:12:00.000Z", "01"), uspsEvent("Out for Delivery", "2026-10-15T12:41:00.000Z", "OF"),
      uspsEvent("Arrived at Post Office", "2026-10-15T10:02:00.000Z", "07"), ...USPS_EARLY] },
  alert: { ...uspsBase, status: "Notice Left (No Authorized Recipient Available)", statusCategory: "Alert",
    statusSummary: "We attempted to deliver your item at 2:05 pm on October 15, 2026 in SHARPSBURG, GA 30277 and a notice was left.",
    trackingEvents: [uspsEvent("Notice Left (No Authorized Recipient Available)", "2026-10-15T18:05:00.000Z", "53"), ...USPS_EARLY] },
  labelOnly: { ...uspsBase, status: "Shipping Label Created, USPS Awaiting Item", statusCategory: "Pre-Shipment",
    statusSummary: "A shipping label has been prepared for your item at 11:04 am on October 12, 2026 in NEWNAN, GA 30263.",
    trackingEvents: [USPS_EARLY[2]] },
};
const USPS_LEGACY = { TrackInfo: { ID: "9400111899223344556677",
  TrackSummary: { EventTime: "1:12 pm", EventDate: "October 15, 2026", Event: "Delivered, In/At Mailbox", EventCity: "SHARPSBURG", EventState: "GA", EventZIPCode: "30277" },
  TrackDetail: [{ EventTime: "8:41 am", EventDate: "October 15, 2026", Event: "Out for Delivery", EventCity: "SHARPSBURG", EventState: "GA" }] } };

const shippoEv = (status, details, date, code, city = "Louisville", state = "KY") => ({
  object_created: date, object_updated: date, object_id: `ev_${date}`, status, status_details: details, status_date: date,
  substatus: code ? { code, text: details, action_required: false } : null, location: { city, state, zip: "", country: "US" },
});
const SHIPPO_HISTORY = [
  shippoEv("PRE_TRANSIT", "Shipper created a label, UPS has not received the package yet.", "2026-10-12T15:00:00Z", "information_received", "Newnan", "GA"),
  shippoEv("TRANSIT", "Origin Scan", "2026-10-12T23:10:00Z", "package_accepted", "Atlanta", "GA"),
  shippoEv("TRANSIT", "Departed from Facility", "2026-10-13T08:00:00Z", "package_departed"),
];
const shippo = (ts, hist = SHIPPO_HISTORY) => ({
  carrier: "ups", tracking_number: "1Z999AA10123456784", address_from: { city: "Newnan", state: "GA", zip: "30263", country: "US" },
  address_to: { city: "Sharpsburg", state: "GA", zip: "30277", country: "US" }, eta: "2026-10-15T23:00:00Z", original_eta: "2026-10-15T23:00:00Z",
  servicelevel: { token: "ups_ground", name: "Ground" }, metadata: null, tracking_status: ts, tracking_history: hist.concat(ts ? [ts] : []), messages: [],
});
const SHIPPO = {
  transit: shippo(SHIPPO_HISTORY[2], SHIPPO_HISTORY.slice(0, 2)),
  outForDelivery: shippo(shippoEv("TRANSIT", "Out For Delivery Today", "2026-10-15T12:00:00Z", "out_for_delivery", "Sharpsburg", "GA")),
  delivered: shippo(shippoEv("DELIVERED", "Delivered: Front Door", "2026-10-15T19:30:00Z", "delivered", "Sharpsburg", "GA")),
  failure: shippo(shippoEv("FAILURE", "The receiver was not available for delivery. We'll make a second attempt the next business day.", "2026-10-15T19:30:00Z", "delivery_attempted", "Sharpsburg", "GA")),
  unknown: { carrier: "ups", tracking_number: "1Z1", tracking_status: { status: "UNKNOWN", status_details: "", status_date: null, substatus: null, location: null }, tracking_history: [], messages: [] },
};

/* ---------------------------------------------------------------- parsers */
test("USPS v3: status category, newest-first events with places, delivered time", () => {
  const t = T.parseUsps(USPS.inTransit);
  assert.equal(t.status, "in_transit");
  assert.equal(t.events.length, 3);
  assert.deepEqual(t.events[0], { at: "2026-10-13T02:10:00.000Z", text: "Arrived at USPS Regional Facility", status: "in_transit", location: "Atlanta Ga Distribution Center" });
  assert.equal(t.events[2].status, "pre_transit");
  assert.equal(t.events[1].location, "Newnan, GA");
  assert.equal(t.estimatedDelivery, "2026-10-15T21:00:00.000Z");
  assert.equal(t.deliveredAt, null);
  assert.equal(T.parseUsps(USPS.outForDelivery).status, "out_for_delivery");
  const d = T.parseUsps(USPS.delivered);
  assert.equal(d.status, "delivered");
  assert.equal(d.deliveredAt, "2026-10-15T17:12:00.000Z");
  assert.match(d.detail, /delivered in or at the mailbox/);
  assert.equal(T.parseUsps(USPS.alert).status, "exception");
  assert.equal(T.parseUsps(USPS.labelOnly).status, "pre_transit");
  // the status words alone (no category) and event codes are enough
  assert.equal(T.parseUsps({ status: "Delivered, Front Door/Porch" }).status, "delivered");
  assert.equal(T.parseUsps({ trackingEvents: [uspsEvent("Some new USPS wording", "2026-10-15T12:41:00.000Z", "OF")] }).status, "out_for_delivery");
});

test("USPS: the older TrackSummary / TrackDetail shape works too", () => {
  const t = T.parseUsps(USPS_LEGACY);
  assert.equal(t.status, "delivered");
  assert.equal(t.events.length, 2);
  assert.equal(t.events[0].text, "Delivered, In/At Mailbox");
  assert.ok(t.deliveredAt && t.deliveredAt.startsWith("2026-10-15"));
});

test("unknown shapes give null (no change) and odd wording gives status null", () => {
  for (const bad of [null, undefined, "", "Delivered", 42, [], [USPS.delivered], {}, { foo: 1 }, { error: { code: "404", message: "Not found" } }, { apiVersion: "3.0" }]) {
    assert.equal(T.parseUsps(bad), null, JSON.stringify(bad));
    assert.equal(T.parseShippo(bad), null, JSON.stringify(bad));
  }
  const odd = T.parseUsps({ status: "Zorbled at the quantum hub", trackingEvents: [] });
  assert.equal(odd.status, null);
  assert.equal(T.parseShippo(SHIPPO.unknown), null, "UNKNOWN with no history is not news");
  // junk inside an otherwise good answer is dropped, not crashed on
  const j = T.parseUsps({ statusCategory: "In Transit", trackingEvents: [null, 5, "x", { eventType: "" }, uspsEvent("Departed Post Office", "2026-10-13T01:00:00Z", "EF")] });
  assert.equal(j.events.length, 1);
});

test("Shippo: transit, out for delivery (substatus), delivered, failure", () => {
  const t = T.parseShippo(SHIPPO.transit);
  assert.equal(t.status, "in_transit");
  assert.equal(t.events.length, 3);
  assert.equal(t.events[0].text, "Departed from Facility");
  assert.equal(t.events[0].location, "Louisville, KY");
  assert.equal(t.events[2].status, "pre_transit");
  assert.equal(t.estimatedDelivery, "2026-10-15T23:00:00.000Z");
  assert.equal(T.parseShippo(SHIPPO.outForDelivery).status, "out_for_delivery");
  const d = T.parseShippo(SHIPPO.delivered);
  assert.equal(d.status, "delivered");
  assert.equal(d.deliveredAt, "2026-10-15T19:30:00.000Z");
  assert.equal(d.events.length, 4, "tracking_status is not counted twice");
  assert.equal(T.parseShippo(SHIPPO.failure).status, "exception");
});

test("classify: carrier words", () => {
  const cases = {
    "Out for Delivery, Expected Delivery by 9:00pm": "out_for_delivery", "Delivered, Left with Individual": "delivered",
    "Delivered, Individual Picked Up at Postal Facility": "delivered", "Delivery Attempted - No Access to Delivery Location": "exception",
    "Available for Pickup": "exception", "Return to Sender": "exception", "Insufficient Address": "exception",
    "In Transit to Next Facility": "in_transit", "Departed Post Office": "in_transit", "USPS in possession of item": "in_transit",
    "Pre-Shipment Info Sent to USPS, USPS Awaiting Item": "pre_transit", "": null, "Something brand new": null,
  };
  for (const [k, v] of Object.entries(cases)) assert.equal(T.classify(k), v, k);
});

/* ---------------------------------------------------------------- planner */
const NOW = Date.parse("2026-10-15T20:00:00Z");
const shippedOrder = (f = {}, emails = {}) => ({
  status: "shipped", number: "LHH-1042", email: "karina@example.com", emails,
  fulfillment: { carrier: "usps", tracking: "9400111899223344556677", shippedAt: "2026-10-12T15:00:00Z", deliveredAt: null, ...f },
});

test("plan: out for delivery emails once, delivered marks delivered with the carrier's time", () => {
  const p1 = T.plan(shippedOrder(), T.parseUsps(USPS.outForDelivery), NOW);
  assert.equal(p1.outForDelivery, true);
  assert.equal(p1.deliveredAt, null);
  assert.equal(p1.fulfillment.trackingStatus, "out_for_delivery");
  assert.equal(p1.fulfillment.lastCheckedAt, new Date(NOW).toISOString());
  assert.equal(p1.fulfillment.lastMovementAt, "2026-10-15T12:41:00.000Z");
  assert.equal(p1.fulfillment.trackingSource, "usps");
  assert.deepEqual(p1.alerts, []);
  const p2 = T.plan(shippedOrder(p1.fulfillment, { outForDelivery: "x" }), T.parseUsps(USPS.outForDelivery), NOW);
  assert.equal(p2.outForDelivery, false, "already sent");
  const p3 = T.plan(shippedOrder(p1.fulfillment), T.parseUsps(USPS.delivered), NOW);
  assert.equal(p3.deliveredAt, "2026-10-15T17:12:00.000Z");
  assert.equal(p3.outForDelivery, false, "no out-for-delivery email once it's delivered");
  assert.equal(p3.fulfillment.events.length, 6, "merged + deduped with the stored scans");
});

test("plan: events capped at 20, newest first", () => {
  const many = Array.from({ length: 30 }, (_, i) => ({ at: new Date(NOW - i * 3600000).toISOString(), text: `Scan ${i}`, status: "in_transit", location: "" }));
  const p = T.plan(shippedOrder({ events: many.slice(10) }), { source: "usps", status: "in_transit", detail: "", events: many.slice(0, 12) }, NOW);
  assert.equal(p.fulfillment.events.length, 20);
  assert.equal(p.fulfillment.events[0].text, "Scan 0");
  assert.equal(p.fulfillment.events[19].text, "Scan 19");
});

test("plan: a carrier problem alerts the shop once per new problem", () => {
  const a = T.parseUsps(USPS.alert);
  const p1 = T.plan(shippedOrder(), a, NOW);
  assert.equal(p1.alerts.length, 1);
  assert.equal(p1.alerts[0].kind, "exception");
  assert.match(p1.alerts[0].text, /Notice Left/);
  const p2 = T.plan(shippedOrder(p1.fulfillment), a, NOW + 7200000);
  assert.equal(p2.alerts.length, 0, "same scan: no second alert");
  const newer = { ...a, events: [{ at: "2026-10-16T18:00:00.000Z", text: "Return to Sender", status: "exception", location: "Sharpsburg, GA" }, ...a.events] };
  assert.equal(T.plan(shippedOrder(p2.fulfillment), newer, NOW + 86400000).alerts.length, 1, "a new problem alerts again");
});

test("plan: 7 days without a new scan alerts once; 30 days stops", () => {
  const quiet = T.parseUsps(USPS.inTransit);           // last scan Oct 13 02:10
  const day = 86400000;
  assert.equal(T.plan(shippedOrder(), quiet, Date.parse("2026-10-19T00:00:00Z")).alerts.length, 0, "6 days: fine");
  const p = T.plan(shippedOrder(), quiet, Date.parse("2026-10-20T03:00:00Z"));
  assert.equal(p.alerts.length, 1);
  assert.equal(p.alerts[0].kind, "stalled");
  assert.match(p.alerts[0].text, /No new scan for 7 days/);
  assert.equal(T.plan(shippedOrder(p.fulfillment), quiet, Date.parse("2026-10-21T03:00:00Z")).alerts.length, 0, "once per quiet spell");
  // never scanned at all: counts from shipping
  const label = T.plan(shippedOrder(), { source: "usps", status: "pre_transit", detail: "Label created", events: [] }, Date.parse("2026-10-19T16:00:00Z"));
  assert.match(label.alerts[0].text, /No carrier scan in the 7 days since it shipped/);
  // 30 days after shipping: stop, even when the check failed
  const stop = T.plan(shippedOrder(), null, Date.parse("2026-10-12T15:00:00Z") + 30 * day + 1000);
  assert.equal(stop.stop, true);
  assert.ok(stop.fulfillment.trackingStoppedAt);
  assert.equal(stop.alerts[0].kind, "stopped");
  // nothing understood and not 30 days yet: nothing changes
  const none = T.plan(shippedOrder(), null, NOW);
  assert.deepEqual(none, { fulfillment: null, outForDelivery: false, deliveredAt: null, alerts: [], stop: false });
  // a delivered answer never alerts
  assert.equal(T.plan(shippedOrder(), T.parseUsps(USPS.delivered), Date.parse("2026-11-20T00:00:00Z")).alerts.length, 0);
});

test("which carriers are followed, and which orders are due", () => {
  const env = (vals) => (k) => vals[k] || "";
  const usps = env({ USPS_CLIENT_ID: "id", USPS_CLIENT_SECRET: "s" });
  const both = env({ USPS_CLIENT_ID: "id", USPS_CLIENT_SECRET: "s", SHIPPO_API_KEY: "shippo_test" });
  assert.equal(T.trackerFor("usps", usps), "usps");
  assert.equal(T.trackerFor("ups", usps), null);
  assert.equal(T.trackerFor("ups", both), "shippo");
  assert.equal(T.trackerFor("dhl", both), "shippo");
  assert.equal(T.trackerFor("other", both), null);
  assert.equal(T.trackerFor("usps", env({ SHIPPO_API_KEY: "k" })), "shippo");
  assert.equal(T.trackerFor("usps", env({})), null);
  const docs = [
    { id: "a", data: shippedOrder({ lastCheckedAt: "2026-10-15T10:00:00Z" }) },
    { id: "b", data: shippedOrder() },
    { id: "c", data: shippedOrder({ carrier: "ups" }) },
    { id: "d", data: shippedOrder({ trackingStoppedAt: "x" }) },
    { id: "e", data: { ...shippedOrder(), status: "delivered" } },
    { id: "f", data: shippedOrder({ tracking: "" }) },
  ];
  assert.deepEqual(T.dueForCheck(docs, usps).map((d) => d.id), ["b", "a"]);
  assert.deepEqual(T.dueForCheck(docs, both).map((d) => d.id), ["b", "c", "a"]);
});

/* ---------------------------------------------------------------- the scheduled run */
const ENV = { RESEND_API_KEY: "re_x", SITE_URL: "https://littlehivehouse.com", MAIL_ADMIN: "support@littlehivehouse.com", USPS_CLIENT_ID: "usps_id", USPS_CLIENT_SECRET: "usps_secret" };

function world() {
  for (const k of ["USPS_CLIENT_ID", "USPS_CLIENT_SECRET", "SHIPPO_API_KEY"]) delete process.env[k];
  Object.assign(process.env, ENV);
  T.resetTokenCache();
  const db = new FakeDB(), net = fakeNet();
  deps.set({ db, auth: new FakeAuth(), bucket: new FakeBucket() });
  globalThis.fetch = net.fetch;
  const answers = {};               // tracking number -> USPS payload, a function returning one, or {httpStatus, message}
  let tokens = 0;
  net.handlers["POST /oauth2/v3/token"] = () => ({ access_token: `tok${++tokens}`, token_type: "Bearer", expires_in: 28800 });
  net.handlers["GET /tracking/v3/tracking/*"] = (p, u) => {
    const n = decodeURIComponent(u.pathname.split("/").pop());
    const a = answers[n];
    if (!a) { const e = new Error("Tracking number not found"); e.status = 404; throw e; }
    if (a.httpStatus) { const e = new Error(a.message || "error"); e.status = a.httpStatus; throw e; }
    return typeof a === "function" ? a() : a;
  };
  const seed = (id, f = {}, extra = {}) => db._set(`orders/${id}`, {
    ...clone(shippedOrder(f)), name: "Karina Vargas", items: [{ kind: "design", id: "places/new-york", title: "New York", collection: "places", qty: 1, unit: 5 }],
    pricing: { total: 9.95 }, timeline: [{ at: "2026-10-12T15:00:00Z", status: "shipped", text: "Your order is on its way." }], emails: { shipped: "x" }, ...extra,
  });
  return { db, net, answers, seed, tokens: () => tokens };
}

test("trackShipments: out for delivery -> one email; delivered -> delivered + one review email; token reused", async () => {
  const { db, net, answers, seed, tokens } = world();
  seed("o1");
  seed("o2", { carrier: "other", tracking: "LM1CA" });                  // manual carrier: never checked
  seed("o3", { tracking: "9400NOTYET" });                               // not in USPS yet (404): nothing changes
  answers["9400111899223344556677"] = USPS.outForDelivery;
  let r = await T.trackShipments({ now: NOW });
  assert.equal(r.checked, 1);
  assert.equal(r.failed, 1);
  assert.equal(r.outForDelivery, 1);
  let o = db.get("orders/o1");
  assert.equal(o.status, "shipped");
  assert.equal(o.fulfillment.trackingStatus, "out_for_delivery");
  assert.equal(o.fulfillment.events[0].text, "Out for Delivery");
  assert.ok(o.emails.outForDelivery);
  assert.equal(o.timeline.at(-1).status, "out_for_delivery");
  assert.equal(net.emails.length, 1);
  assert.equal(net.emails[0].to[0], "karina@example.com");
  assert.match(net.emails[0].subject, /arrive today/);
  assert.ok(!/^<pre/.test(net.emails[0].html), "branded template, not the fallback");
  assert.equal(db.get("orders/o3").fulfillment.lastCheckedAt, undefined);
  assert.equal(db.get("orders/o2").fulfillment.lastCheckedAt, undefined);
  const trackCall = net.calls.find((c) => c.path.startsWith("/tracking/v3/tracking/9400111899223344556677"));
  assert.equal(trackCall.headers.Authorization, "Bearer tok1");
  assert.ok(net.calls.some((c) => c.path === "/tracking/v3/tracking/9400111899223344556677") );

  // two hours later: same answer, no second email
  r = await T.trackShipments({ now: NOW + 7200000 });
  assert.equal(net.emails.length, 1);
  // then delivered
  answers["9400111899223344556677"] = USPS.delivered;
  r = await T.trackShipments({ now: NOW + 4 * 3600000 });
  assert.equal(r.delivered, 1);
  o = db.get("orders/o1");
  assert.equal(o.status, "delivered");
  assert.equal(o.fulfillment.deliveredAt, "2026-10-15T17:12:00.000Z");
  assert.ok(o.emails.delivered);
  assert.equal(o.timeline.at(-1).status, "delivered");
  assert.match(o.adminNotes.at(-1).text, /automatically \(usps tracking\)/);
  assert.equal(net.emails.length, 2);
  assert.match(net.emails[1].subject, /how do they look on your fridge/i);
  // delivered orders are no longer polled
  const before = net.calls.length;
  await T.trackShipments({ now: NOW + 6 * 3600000 });
  assert.ok(!net.calls.slice(before).some((c) => c.path.endsWith("9400111899223344556677")));
  assert.equal(tokens(), 1, "one USPS sign-in for all runs");
  assert.equal(net.calls.filter((c) => c.path === "/oauth2/v3/token").length, 1);
});

test("trackShipments: expired token is refreshed once; a strange answer changes nothing", async () => {
  const { db, net, answers, seed, tokens } = world();
  seed("o1");
  let first = true;
  answers["9400111899223344556677"] = () => {
    if (first) { first = false; const e = new Error("expired"); e.status = 401; throw e; }
    return USPS.inTransit;
  };
  await T.trackShipments({ now: NOW });
  assert.equal(tokens(), 2);
  assert.equal(db.get("orders/o1").fulfillment.trackingStatus, "in_transit");
  answers["9400111899223344556677"] = { surprise: "new format" };
  const snapshot = JSON.stringify(db.get("orders/o1"));
  const r = await T.trackShipments({ now: NOW + 7200000 });
  assert.equal(r.unknown, 1);
  assert.equal(JSON.stringify(db.get("orders/o1")), snapshot, "unknown shape: no change");
  assert.equal(net.emails.length, 0);
});

test("trackShipments: problems are batched into one shop alert, once", async () => {
  const { db, net, answers, seed } = world();
  seed("o1");
  seed("o2", { tracking: "9400STALLED" }, { number: "LHH-1043", name: "Sam Lee" });
  answers["9400111899223344556677"] = USPS.alert;
  answers["9400STALLED"] = USPS.inTransit;            // last scan Oct 13
  const later = Date.parse("2026-10-21T12:00:00Z");
  const r = await T.trackShipments({ now: later });
  assert.equal(r.alerts, 2);
  assert.equal(net.emails.length, 1);
  const e = net.emails[0];
  assert.equal(e.to[0], "support@littlehivehouse.com");
  assert.match(e.subject, /2 shipments need a look/);
  assert.match(e.text, /Notice Left/);
  assert.match(e.text, /No new scan for 8 days/);
  assert.match(e.html, /admin\/#order\/o1/);
  assert.ok(db.get("orders/o1").fulfillment.alerts.exception);
  await T.trackShipments({ now: later + 7200000 });
  assert.equal(net.emails.length, 1, "no repeat alert");
  assert.equal(db.get("orders/o1").status, "shipped", "a problem never changes the status");
});

test("trackShipments: UPS through Shippo when SHIPPO_API_KEY is set; off without keys", async () => {
  const { db, net, seed } = world();
  delete process.env.USPS_CLIENT_ID; delete process.env.USPS_CLIENT_SECRET;
  seed("o1", { carrier: "ups", tracking: "1Z999AA10123456784" });
  let r = await T.trackShipments({ now: NOW });
  assert.equal(r.off, true);
  assert.equal(net.calls.length, 0);
  process.env.SHIPPO_API_KEY = "shippo_test_123";
  net.handlers["GET /tracks/*"] = () => SHIPPO.delivered;
  r = await T.trackShipments({ now: NOW });
  const call = net.calls.find((c) => c.path.startsWith("/tracks/"));
  assert.equal(call.path, "/tracks/ups/1Z999AA10123456784");
  assert.equal(call.headers.Authorization, "ShippoToken shippo_test_123");
  const o = db.get("orders/o1");
  assert.equal(o.status, "delivered");
  assert.equal(o.fulfillment.trackingSource, "shippo");
  assert.equal(o.fulfillment.deliveredAt, "2026-10-15T19:30:00.000Z");
  assert.equal(net.emails.length, 1);
  delete process.env.SHIPPO_API_KEY;
});

test("adminShip with a new tracking number restarts tracking; the daily reminder skips orders tracking watches", async () => {
  const { db, seed } = world();
  const admin = require("../admin");
  const { lateShipments } = require("../scheduled");
  seed("o1", { trackingStatus: "exception", events: [{ at: "x", text: "Notice Left" }], lastCheckedAt: "2026-10-15T10:00:00Z", alerts: { exception: "k" } }, { emails: { outForDelivery: "y" } });
  const res = await admin.adminShip({ orderId: "o1", carrier: "usps", tracking: "9400 0000 1111", labelCost: 5 }, { uid: "a", token: { admin: true, email: "o@x.com" } });
  assert.equal(res.autoTracking, true);
  const f = db.get("orders/o1").fulfillment;
  assert.equal(f.tracking, "940000001111");
  assert.equal(f.trackingStatus, null);
  assert.deepEqual(f.events, []);
  assert.deepEqual(f.alerts, {});
  assert.equal(db.get("orders/o1").emails.outForDelivery, null);
  const now = Date.parse("2026-10-30T12:00:00Z");
  const docs = [
    { id: "w", data: shippedOrder({ lastCheckedAt: "2026-10-30T10:00:00Z" }) },
    { id: "m", data: shippedOrder({ carrier: "other" }) },
    { id: "s", data: shippedOrder({ lastCheckedAt: "2026-10-30T10:00:00Z", trackingStoppedAt: "2026-10-30T10:00:00Z" }) },
    { id: "old", data: shippedOrder({ lastCheckedAt: "2026-10-20T10:00:00Z" }) },
  ];
  assert.deepEqual(lateShipments(docs, now).map((x) => x.id).sort(), ["m", "old", "s"]);
  assert.match(lateShipments(docs, now)[0].adminUrl, /\/admin\/#order\//);
});
