"use strict";
/* Emails to the subscribers, written in Hive Admin (Subscribers › Write an email).

   adminNewsletter({action, campaign, campaignId, confirm})
     preview  -> {subject, html, count}                    the email as a subscriber sees it, and how many would get it
     test     -> {sent: true, to}                          one copy to the admin who asks
     send     -> {sent, failed, total, campaignId}         everyone subscribed and not unsubscribed, in batches of 100
     list     -> {campaigns: [...]}                        the last 20 sends

   Every email carries its own unsubscribe link (List-Unsubscribe header too) and the shop's postal address
   (MAIL_POSTAL_ADDRESS), as the CAN-SPAM Act asks. A campaign is sent once: campaigns/{campaignId} is created before the
   first email goes out, so a second tap on "Send" (or a retry) can't send it twice. */

const { fail, env, nowIso, mailAdmin } = require("./config");
const deps = require("./deps");
const mail = require("./mail");
const stripe = require("./stripe");
const U = require("./util");

const BATCH = 100;
const MAX_RECIPIENTS = 5000;
const GALLERIES = new Set(["designs", "photos", "none"]);

function clean(raw) {
  const c = raw && typeof raw === "object" ? raw : {};
  const out = {
    subject: U.text(c.subject, 120, { required: true, field: "the subject" }),
    preheader: U.text(c.preheader, 160),
    eyebrow: U.text(c.eyebrow, 40),
    title: U.text(c.title, 120, { required: true, field: "the title" }),
    body: typeof c.body === "string" ? c.body.trim().slice(0, 4000) : "",
    gallery: GALLERIES.has(c.gallery) ? c.gallery : "designs",
    designs: (Array.isArray(c.designs) ? c.designs : []).map((d) => String(d)).filter((d) => /^[a-z0-9-]+\/[a-z0-9-]+$/.test(d)).slice(0, 3),
    promo: null,
    button: null,
  };
  if (!out.body) fail("invalid-argument", "Please write the message.");
  const code = U.text(c.promo && c.promo.code, 40).toUpperCase();
  if (code) {
    if (!/^[A-Z0-9_-]{3,40}$/.test(code)) fail("invalid-argument", "The discount code uses letters, numbers, - or _.");
    out.promo = { code, text: U.text(c.promo.text, 140) };
  }
  const label = U.text(c.button && c.button.label, 40);
  if (label) {
    let href = U.text(c.button.href, 300);
    if (href.startsWith("/")) href = `https://littlehivehouse.com${href}`;
    if (!/^https:\/\/(www\.)?littlehivehouse\.com(\/|$)/.test(href)) fail("invalid-argument", "The button must link to a page of littlehivehouse.com.");
    out.button = { label, href };
  }
  return out;
}

async function recipients() {
  const q = await deps.db().collection("subscribers").get();
  const seen = new Set();
  const list = [];
  for (const d of q.docs) {
    const s = d.data() || {};
    const email = String(s.email || "").trim();
    if (!email || s.unsubscribed === true || !U.EMAIL_RE.test(email)) continue;
    const k = email.toLowerCase();
    if (seen.has(k)) continue;
    seen.add(k);
    list.push(email);
  }
  return list;
}

/** The discount code must exist and be active in Stripe, or customers would get a code that doesn't work. */
async function checkPromo(promo) {
  if (!promo) return;
  let res = null;
  try { res = await stripe.request("GET", "/promotion_codes", { code: promo.code, active: true, limit: 1 }); } catch (err) { res = null; }
  if (!res || !Array.isArray(res.data) || !res.data.length) fail("failed-precondition", `The code ${promo.code} isn't an active discount. Create it in Discounts first, or leave the code empty.`);
}

async function sendBatch(payloads, fetchImpl) {
  const res = await (fetchImpl || fetch)("https://api.resend.com/emails/batch", {
    method: "POST",
    headers: { Authorization: `Bearer ${env("RESEND_API_KEY")}`, "Content-Type": "application/json" },
    body: JSON.stringify(payloads),
  });
  const json = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(`Resend ${res.status}: ${json.message || json.name || "error"}`);
  return Array.isArray(json.data) ? json.data.length : payloads.length;
}

async function adminNewsletter(data, auth, _raw, { fetchImpl, pause = 600 } = {}) {
  U.requireAdmin(auth);
  const action = String((data && data.action) || "preview");
  const db = deps.db();
  if (action === "list") {
    const q = await db.collection("campaigns").orderBy("createdAt", "desc").limit(20).get();
    return { campaigns: q.docs.map((d) => ({ id: d.id, ...d.data() })) };
  }
  const campaign = clean(data && data.campaign);
  if (action === "preview") {
    const msg = mail.compose({ to: "subscriber@example.com", kind: "newsletter", data: { campaign } });
    return { subject: msg.subject, html: msg.html, count: (await recipients()).length, postal: !!env("MAIL_POSTAL_ADDRESS") };
  }
  if (!env("RESEND_API_KEY")) fail("failed-precondition", "Email is not set up yet (RESEND_API_KEY is missing).");
  await checkPromo(campaign.promo);
  if (action === "test") {
    const to = (auth.token && auth.token.email) || mailAdmin();
    await mail.send({ to, kind: "newsletter", data: { campaign }, required: true });
    return { sent: true, to };
  }
  if (action !== "send") fail("invalid-argument", "Unknown action.");
  // the CAN-SPAM Act asks for a valid postal address in every marketing email (a PO Box works)
  if (!env("MAIL_POSTAL_ADDRESS")) fail("failed-precondition", "Marketing emails need the shop's mailing address at the bottom (US law). Add it as MAIL_POSTAL_ADDRESS in GitHub (Settings › Variables), then send.");
  const id = U.text(data && data.campaignId, 64);
  if (!/^[A-Za-z0-9_-]{8,64}$/.test(id)) fail("invalid-argument", "Missing campaign id. Reload the page and try again.");
  if (U.text(data && data.confirm, 20).toUpperCase() !== "SEND") fail("failed-precondition", "Please confirm the send.");
  const list = await recipients();
  if (!list.length) fail("failed-precondition", "There are no subscribers yet.");
  if (list.length > MAX_RECIPIENTS) fail("failed-precondition", `There are ${list.length} subscribers, more than this tool sends at once (${MAX_RECIPIENTS}). Use an email tool with the CSV.`);
  const ref = db.collection("campaigns").doc(id);
  await db.runTransaction(async (tx) => {
    const snap = await tx.get(ref);
    if (snap.exists) fail("already-exists", "This email was already sent. Write a new one to send again.");
    tx.set(ref, { ...campaign, status: "sending", total: list.length, sent: 0, failed: 0, createdAt: nowIso(), by: U.who(auth) });
  });
  let sent = 0, failed = 0;
  const errors = [];
  for (let i = 0; i < list.length; i += BATCH) {
    const chunk = list.slice(i, i + BATCH);
    const payloads = [];
    for (const to of chunk) {
      try { payloads.push(mail.compose({ to, kind: "newsletter", data: { campaign } })); } catch (err) { failed += 1; errors.push(`${to}: ${err.message}`); }
    }
    try {
      sent += await sendBatch(payloads, fetchImpl);
    } catch (err) {
      failed += payloads.length;
      errors.push(err.message);
    }
    if (i + BATCH < list.length && pause) await new Promise((r) => setTimeout(r, pause));   // Resend allows a couple of requests a second
  }
  await ref.update({ status: failed && !sent ? "failed" : "sent", sent, failed, errors: errors.slice(0, 5), sentAt: nowIso() });
  return { sent, failed, total: list.length, campaignId: id };
}

module.exports = { adminNewsletter, clean, recipients };
