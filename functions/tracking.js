"use strict";
/* Automatic delivery tracking: trackShipments (every 2 hours).
   Once the owner enters a tracking number (adminShip), this keeps the customer posted on its own:
     out for delivery -> one `out_for_delivery` email; delivered -> the order becomes delivered + one `delivered_review` email
     (the same path as adminMarkDelivered); a carrier problem, or 7+ days without a new scan -> one alert to the shop
     (admin_delivery_check). It stops after delivery or 30 days after shipping.
   Carriers: USPS through the free USPS APIs v3 (env USPS_CLIENT_ID / USPS_CLIENT_SECRET, OAuth2 client credentials);
   UPS / FedEx / DHL (and USPS without the USPS keys) through Shippo's tracking API when SHIPPO_API_KEY is set.
   Anything else stays manual (the daily deliveredFollowUp reminder covers it).
   The parsers and the planner are pure and unit-tested with sample payloads; an answer we don't understand changes
   nothing and is logged. */

const { env, nowIso, mailAdmin } = require("./config");
const deps = require("./deps");
const mail = require("./mail");
const O = require("./orders");

const MAX_EVENTS = 20;
const STALL_DAYS = 7;
const STOP_DAYS = 30;
const MAX_PER_RUN = 50;          // USPS gives new apps a small hourly quota; the oldest-checked orders go first
const DAY = 86400000;
const USPS_BASE = "https://apis.usps.com";
const SHIPPO_BASE = "https://api.goshippo.com";
const SHIPPO_CARRIERS = { usps: "usps", ups: "ups", fedex: "fedex", dhl: "dhl_express" };

/* ---------------------------------------------------------------- helpers */
/** Case-insensitive property read: get(obj, "statusCategory") also finds "StatusCategory". */
function get(obj, ...names) {
  if (!obj || typeof obj !== "object") return undefined;
  for (const n of names) {
    if (obj[n] !== undefined && obj[n] !== null) return obj[n];
    const k = Object.keys(obj).find((x) => x.toLowerCase() === n.toLowerCase());
    if (k && obj[k] !== undefined && obj[k] !== null) return obj[k];
  }
  return undefined;
}
const str = (v, max = 200) => (typeof v === "string" || typeof v === "number" ? String(v).replace(/\s+/g, " ").trim().slice(0, max) : "");
function iso(v) {
  if (!v || (typeof v !== "string" && typeof v !== "number")) return null;
  const t = Date.parse(v);
  return Number.isFinite(t) ? new Date(t).toISOString() : null;
}
const ms = (v) => { const t = Date.parse(v || ""); return Number.isFinite(t) ? t : null; };
const titleCase = (s) => str(s, 60).toLowerCase().replace(/\b[a-z]/g, (c) => c.toUpperCase());
function place(city, state, country) {
  const c = str(city, 60), s = str(state, 30), k = str(country, 40);
  return [c ? titleCase(c) : "", s.toUpperCase(), k && !/^(us|usa|united states)$/i.test(k) ? titleCase(k) : ""].filter(Boolean).join(", ");
}

/**
 * Carrier wording -> our status: pre_transit | in_transit | out_for_delivery | delivered | exception, or null (unknown).
 * USPS status categories: Pre-Shipment, Accepted, In Transit, Out for Delivery, Delivered, Available for Pickup,
 * Delivery Attempt, Alert (plus Return to Sender, Missing ...). Event codes: 01 delivered, OF out for delivery.
 */
function classify(text, code) {
  const t = str(text, 300).toLowerCase();
  const c = str(code, 10).toUpperCase();
  if (c === "OF") return "out_for_delivery";
  if (c === "01") return "delivered";
  if (!t) return null;
  if (/out for delivery|out-for-delivery|with delivery courier|on vehicle for delivery/.test(t)) return "out_for_delivery";
  if (/return(ed)? to (the )?sender|undeliverable|delivery attempt|attempted|notice left|available for pick ?up|held at|alert|missing|lost|damaged|seized|refused|exception|insufficient address|no access|unable to deliver|failure|failed/.test(t)) return "exception";
  if (/^delivered|\bdelivered\b/.test(t)) return "delivered";
  if (/pre-?shipment|label created|shipping label|awaiting item|information received|shipment information sent|order processed/.test(t)) return "pre_transit";
  if (/accept|in transit|transit|arriv|depart|processed|processing|picked up|pickup|origin|facility|on its way|moving|forwarded|enroute|en route|in route|delayed|in possession|redelivery/.test(t)) return "in_transit";
  return null;
}

/* ---------------------------------------------------------------- parsers */
/** Newest first, deduped by time + text, at most MAX_EVENTS. */
function tidyEvents(list) {
  const seen = new Set();
  return list.filter((e) => e && (e.at || e.text))
    .filter((e) => { const k = `${e.at || ""}|${e.text.toLowerCase()}`; if (seen.has(k)) return false; seen.add(k); return true; })
    .sort((a, b) => (ms(b.at) || 0) - (ms(a.at) || 0))
    .slice(0, MAX_EVENTS);
}

/**
 * USPS Tracking API v3 (`GET /tracking/v3/tracking/{n}?expand=DETAIL`):
 *   {trackingNumber, statusCategory, status, statusSummary, expectedDeliveryTimeStamp, trackingEvents:[{eventType,
 *    eventTimestamp, GMTTimestamp, eventCity, eventState, eventZIP, eventCountry, eventCode}]}
 * The older TrackSummary / TrackDetail shape is understood too. Returns null for anything else.
 */
function parseUsps(json) {
  if (!json || typeof json !== "object" || Array.isArray(json)) return null;
  let root = json;
  const info = get(json, "TrackInfo", "trackInfo");
  if (info && typeof info === "object") root = Array.isArray(info) ? info[0] || {} : info;
  const event = (e) => {
    if (!e || typeof e !== "object") return null;
    const text = str(get(e, "eventType", "Event", "event", "description"), 160);
    const date = get(e, "EventDate"), time = get(e, "EventTime");
    const at = iso(get(e, "GMTTimestamp", "gmtTimestamp")) || iso(get(e, "eventTimestamp", "eventDateTime")) ||
      (date ? iso(`${date} ${time || ""}`.trim()) : null);
    if (!text && !at) return null;
    return { at, text, status: classify(text, get(e, "eventCode", "EventCode")),
      location: place(get(e, "eventCity", "EventCity"), get(e, "eventState", "EventState"), get(e, "eventCountry", "EventCountry")) };
  };
  let raw = get(root, "trackingEvents", "TrackDetail", "events");
  raw = Array.isArray(raw) ? raw : raw && typeof raw === "object" ? [raw] : [];
  const summary = get(root, "TrackSummary");
  const events = tidyEvents([...(summary ? [event(summary)] : []), ...raw.map(event)]);
  const category = str(get(root, "statusCategory"), 80);
  const statusText = str(get(root, "status"), 120);
  const summaryText = str(get(root, "statusSummary", "StatusSummary"), 300);
  if (!category && !statusText && !summaryText && !events.length) return null;
  const status = classify(category) || classify(statusText) || (events[0] && events[0].status) || classify(summaryText);
  const delivered = events.find((e) => e.status === "delivered");
  return {
    source: "usps",
    status: status || null,
    detail: summaryText || statusText || category || (events[0] && events[0].text) || "",
    events,
    deliveredAt: status === "delivered" ? (delivered && delivered.at) || null : null,
    estimatedDelivery: iso(get(root, "expectedDeliveryTimeStamp", "predictedDeliveryTimeStamp", "expectedDeliveryDate", "predictedDeliveryDate")),
  };
}

const SHIPPO_EXCEPTIONS = new Set(["address_issue", "contact_carrier", "delivery_attempted", "location_inaccessible", "notice_left",
  "package_damaged", "package_held", "pickup_available", "return_to_sender", "package_returned", "package_lost", "package_undeliverable",
  "package_disposed", "cancelled", "delivery_failed"]);
function shippoStatus(ts) {
  if (!ts || typeof ts !== "object") return null;
  const code = str(ts.substatus && typeof ts.substatus === "object" ? ts.substatus.code : "", 60).toLowerCase();
  const s = str(ts.status, 30).toUpperCase();
  if (s === "DELIVERED") return "delivered";
  if (s === "RETURNED" || s === "FAILURE") return "exception";
  if (code === "out_for_delivery") return "out_for_delivery";
  if (SHIPPO_EXCEPTIONS.has(code)) return "exception";
  if (s === "TRANSIT") return "in_transit";
  if (s === "PRE_TRANSIT") return "pre_transit";
  return classify(ts.status_details);
}
/** Shippo `GET /tracks/{carrier}/{number}`: {tracking_status:{status, status_details, status_date, substatus, location}, tracking_history:[...], eta}. */
function parseShippo(json) {
  if (!json || typeof json !== "object" || Array.isArray(json)) return null;
  const ts = json.tracking_status;
  const hist = Array.isArray(json.tracking_history) ? json.tracking_history : [];
  if ((!ts || typeof ts !== "object") && !hist.length) return null;
  const event = (e) => {
    if (!e || typeof e !== "object") return null;
    const text = str(e.status_details || (e.substatus && e.substatus.text), 160);
    const loc = e.location && typeof e.location === "object" ? e.location : {};
    const at = iso(e.status_date || e.object_updated);
    if (!text && !at) return null;      // e.g. {status: "UNKNOWN"}: the carrier has nothing yet
    return { at, text, status: shippoStatus(e), location: place(loc.city, loc.state, loc.country) };
  };
  const events = tidyEvents([ts, ...hist].map(event));
  const status = ts ? shippoStatus(ts) : events[0] && events[0].status;
  if (!status && !events.length) return null;
  const delivered = events.find((e) => e.status === "delivered");
  return {
    source: "shippo",
    status: status || null,
    detail: str(ts && ts.status_details, 300) || (events[0] && events[0].text) || "",
    events,
    deliveredAt: status === "delivered" ? (delivered && delivered.at) || (ts && iso(ts.status_date)) || null : null,
    estimatedDelivery: iso(json.eta),
  };
}

/* ---------------------------------------------------------------- planner (pure) */
/** Which tracker can follow this carrier: "usps" | "shippo" | null (manual). */
function trackerFor(carrier, e = env) {
  const c = String(carrier || "").toLowerCase();
  if (c === "usps" && e("USPS_CLIENT_ID") && e("USPS_CLIENT_SECRET")) return "usps";
  if (SHIPPO_CARRIERS[c] && e("SHIPPO_API_KEY")) return "shippo";
  return null;
}

/** Shipped orders that are worth a look now, oldest-checked first. docs: [{id, data}] */
function dueForCheck(docs, e = env) {
  return docs
    .filter(({ data }) => {
      const f = data.fulfillment || {};
      return data.status === "shipped" && f.tracking && !f.deliveredAt && !f.trackingStoppedAt && trackerFor(f.carrier, e);
    })
    .sort((a, b) => (ms(a.data.fulfillment.lastCheckedAt) || 0) - (ms(b.data.fulfillment.lastCheckedAt) || 0))
    .slice(0, MAX_PER_RUN);
}

/**
 * What one tracking answer means for an order. Pure.
 * parsed: parseUsps/parseShippo output, or null when the check failed / the answer was not understood.
 * Returns {fulfillment (the new fulfillment object, or null for no change), outForDelivery:bool, deliveredAt:iso|null,
 *          alerts:[{kind:"exception"|"stalled"|"stopped", key, text, days}], stop:bool}
 */
function plan(order, parsed, now = Date.now()) {
  const f = { ...(order.fulfillment || {}) };
  const emails = order.emails || {};
  const at = new Date(now).toISOString();
  const shippedMs = ms(f.shippedAt);
  const out = { fulfillment: null, outForDelivery: false, deliveredAt: null, alerts: [], stop: false };
  const alerts = { ...(f.alerts || {}) };

  if (parsed) {
    const events = tidyEvents([...(parsed.events || []), ...(Array.isArray(f.events) ? f.events : [])]);
    const status = parsed.status || f.trackingStatus || null;
    const newest = events.find((e) => ms(e.at));
    const lastMove = Math.max(ms(f.lastMovementAt) || 0, newest ? ms(newest.at) : 0) || null;
    Object.assign(f, {
      trackingStatus: status, trackingDetail: parsed.detail || f.trackingDetail || "", events,
      trackingSource: parsed.source || f.trackingSource || null, lastCheckedAt: at,
      lastMovementAt: lastMove ? new Date(lastMove).toISOString() : f.lastMovementAt || null,
      estimatedDelivery: parsed.estimatedDelivery || f.estimatedDelivery || null,
    });
    if (status === "delivered") {
      const d = parsed.deliveredAt || (events.find((e) => e.status === "delivered") || {}).at || at;
      out.deliveredAt = ms(d) && ms(d) <= now + DAY ? d : at;
    } else if (status === "out_for_delivery" && !emails.outForDelivery) {
      out.outForDelivery = true;
    }
    if (status === "exception") {
      const top = events[0];
      const key = top ? `${top.at || ""}|${top.text}` : parsed.detail;
      if (alerts.exception !== key) {
        alerts.exception = key;
        out.alerts.push({ kind: "exception", key, text: (top && top.text) || parsed.detail || "The carrier reported a problem." });
      }
    }
    // 7+ days without a new scan (or since shipping when there are none): one alert per quiet spell
    const quietSince = lastMove || shippedMs;
    if (!out.deliveredAt && quietSince && now - quietSince >= STALL_DAYS * DAY) {
      const key = new Date(quietSince).toISOString();
      if (alerts.stalled !== key) {
        alerts.stalled = key;
        out.alerts.push({ kind: "stalled", key, days: Math.floor((now - quietSince) / DAY),
          text: lastMove ? `No new scan for ${Math.floor((now - quietSince) / DAY)} days.` : `No carrier scan in the ${Math.floor((now - quietSince) / DAY)} days since it shipped.` });
      }
    }
  }
  if (!out.deliveredAt && shippedMs && now - shippedMs >= STOP_DAYS * DAY) {
    out.stop = true;
    f.trackingStoppedAt = at;
    f.trackingStopReason = `Not delivered ${STOP_DAYS} days after shipping`;
    out.alerts.push({ kind: "stopped", key: at, text: `Still not delivered ${STOP_DAYS} days after shipping. Automatic checks stopped; please look into it.` });
  }
  if (out.alerts.length) f.alerts = alerts;
  if (parsed || out.stop) out.fulfillment = f;
  return out;
}

/* ---------------------------------------------------------------- carriers (network) */
let uspsToken = null;   // {token, exp}: reused across runs while the instance is warm
function resetTokenCache() { uspsToken = null; }

async function readJson(res) { try { return await res.json(); } catch (e) { return null; } }

async function uspsAccessToken(fetchImpl, force = false) {
  if (!force && uspsToken && uspsToken.exp > Date.now() + 60000) return uspsToken.token;
  const res = await fetchImpl(`${USPS_BASE}/oauth2/v3/token`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ client_id: env("USPS_CLIENT_ID"), client_secret: env("USPS_CLIENT_SECRET"), grant_type: "client_credentials" }),
  });
  const json = await readJson(res) || {};
  if (!res.ok || !json.access_token) {
    throw new Error(`USPS sign-in failed (${res.status}): ${json.error_description || json.error || "check USPS_CLIENT_ID / USPS_CLIENT_SECRET"}`);
  }
  uspsToken = { token: json.access_token, exp: Date.now() + (Number(json.expires_in) || 3600) * 1000 };
  return uspsToken.token;
}

async function fetchUsps(number, fetchImpl) {
  const url = `${USPS_BASE}/tracking/v3/tracking/${encodeURIComponent(number)}?expand=DETAIL`;
  for (let attempt = 0; attempt < 2; attempt++) {
    const token = await uspsAccessToken(fetchImpl, attempt > 0);
    const res = await fetchImpl(url, { headers: { Authorization: `Bearer ${token}`, Accept: "application/json" } });
    if (res.status === 401 && attempt === 0) continue;      // token expired early: sign in again once
    const json = await readJson(res);
    if (!res.ok) {
      const msg = json && (json.error && (json.error.message || json.error) || json.message);
      const err = new Error(`USPS tracking ${res.status}${msg ? `: ${typeof msg === "string" ? msg : JSON.stringify(msg)}` : ""}`);
      err.status = res.status;
      throw err;
    }
    return json;
  }
  throw new Error("USPS tracking: not authorized");
}

async function fetchShippo(carrier, number, fetchImpl) {
  const c = SHIPPO_CARRIERS[String(carrier || "").toLowerCase()];
  const res = await fetchImpl(`${SHIPPO_BASE}/tracks/${c}/${encodeURIComponent(number)}`, {
    headers: { Authorization: `ShippoToken ${env("SHIPPO_API_KEY")}`, Accept: "application/json" },
  });
  const json = await readJson(res);
  if (!res.ok) {
    const err = new Error(`Shippo tracking ${res.status}${json && json.detail ? `: ${json.detail}` : ""}`);
    err.status = res.status;
    throw err;
  }
  return json;
}

/** Asks the right carrier API. Returns {parsed, raw} (parsed null when the answer wasn't understood). Throws on network/API errors. */
async function check(order, fetchImpl = fetch) {
  const f = order.fulfillment || {};
  const who = trackerFor(f.carrier);
  if (who === "usps") { const raw = await fetchUsps(f.tracking, fetchImpl); return { parsed: parseUsps(raw), raw }; }
  if (who === "shippo") { const raw = await fetchShippo(f.carrier, f.tracking, fetchImpl); return { parsed: parseShippo(raw), raw }; }
  return { parsed: null, raw: null };
}

/* ---------------------------------------------------------------- the scheduled run */
async function trackShipments({ now = Date.now(), fetchImpl } = {}) {
  const doFetch = fetchImpl || fetch;
  if (!trackerFor("usps") && !trackerFor("ups")) {
    console.log("[trackShipments] no USPS or Shippo keys: automatic tracking is off (see SETUP.md)");
    return { checked: 0, off: true };
  }
  const db = deps.db();
  const q = await db.collection("orders").where("status", "==", "shipped").get();
  const due = dueForCheck(q.docs.map((d) => ({ id: d.id, data: d.data() })));
  const sum = { checked: 0, failed: 0, unknown: 0, outForDelivery: 0, delivered: 0, alerts: 0 };
  const alerts = [];
  const { deliverOrder } = require("./admin");

  for (const { id, data } of due) {
    const ref = db.collection("orders").doc(id);
    let parsed = null;
    try {
      const r = await check(data, doFetch);
      parsed = r.parsed;
      if (!parsed) {
        sum.unknown++;
        console.warn(`[trackShipments] ${data.number || id}: answer not understood, nothing changed`, JSON.stringify(r.raw).slice(0, 800));
      }
      sum.checked++;
    } catch (err) {
      sum.failed++;
      // e.g. 404 = not in the carrier's system yet; nothing changes and the next run tries again
      console.warn(`[trackShipments] ${data.number || id}: check failed`, err && err.message);
    }

    // apply in a transaction against the fresh order (the owner may have changed it meanwhile)
    let p = null, after = null;
    await db.runTransaction(async (tx) => {
      const snap = await tx.get(ref);
      if (!snap.exists) return;
      const o = snap.data();
      const f = o.fulfillment || {};
      if (o.status !== "shipped" || f.tracking !== (data.fulfillment || {}).tracking) return;
      p = plan(o, parsed, now);
      if (!p.fulfillment && !p.outForDelivery) return;
      const t = nowIso();
      const upd = { updatedAt: t };
      if (p.fulfillment) upd.fulfillment = p.fulfillment;
      if (p.outForDelivery) upd["emails.outForDelivery"] = t;     // claimed before sending, so it goes out once
      if (p.fulfillment && p.fulfillment.trackingStatus === "out_for_delivery" && f.trackingStatus !== "out_for_delivery") {
        upd.timeline = (o.timeline || []).concat([{ at: t, status: "out_for_delivery", text: "Out for delivery." }]);
      }
      tx.update(ref, upd);
      after = { ...o, fulfillment: upd.fulfillment || o.fulfillment, timeline: upd.timeline || o.timeline,
        emails: { ...(o.emails || {}), ...(p.outForDelivery ? { outForDelivery: t } : {}) } };
    });
    if (!p || !after) continue;

    if (p.outForDelivery && after.email) {
      const sent = await mail.send({ to: after.email, kind: "out_for_delivery", data: { order: O.emailOrder(id, after) } });
      if (sent.skipped) await ref.update({ "emails.outForDelivery": null }).catch(() => {});   // try again next run
      else sum.outForDelivery++;
    }
    if (p.deliveredAt) {
      try {
        const res = await deliverOrder(ref, id, { at: p.deliveredAt, by: `${(after.fulfillment || {}).trackingSource || "carrier"} tracking`, onlyOnceEmail: true });
        if (res.delivered) sum.delivered++;
      } catch (err) {
        console.warn(`[trackShipments] ${data.number || id}: could not mark delivered`, err && err.message);
      }
    }
    for (const a of p.alerts) {
      const f = after.fulfillment || {};
      const days = Math.floor((now - (ms(f.shippedAt) || now)) / DAY);
      alerts.push({
        id, number: after.number || "", name: after.name || "", email: after.email || "", carrier: f.carrier || "",
        carrierName: (O.CARRIERS[f.carrier] || O.CARRIERS.other).name, tracking: f.tracking || "", url: f.url || "",
        shippedAt: f.shippedAt || null, days, adminUrl: O.adminOrderUrl(id), issue: a.text, issueKind: a.kind,
        trackingStatus: f.trackingStatus || null,
      });
    }
  }
  if (alerts.length) {
    sum.alerts = alerts.length;
    await mail.send({ to: mailAdmin(), kind: "admin_delivery_check", data: { mode: "tracking", orders: alerts, now: new Date(now).toISOString() } });
  }
  console.log("[trackShipments]", JSON.stringify({ due: due.length, ...sum }));
  return { due: due.length, ...sum };
}

module.exports = {
  trackShipments, parseUsps, parseShippo, classify, plan, trackerFor, dueForCheck, check, fetchUsps, fetchShippo,
  resetTokenCache, MAX_EVENTS, STALL_DAYS, STOP_DAYS, MAX_PER_RUN,
};
