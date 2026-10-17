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
  return sendCampaign(campaign, id, U.who(auth), { fetchImpl, pause });
}

/** Sends a checked campaign once (campaigns/{id} guards against a second send) to every subscriber, in batches. */
async function sendCampaign(campaign, id, by, { fetchImpl, pause = 600, list } = {}) {
  const db = deps.db();
  list = list || await recipients();
  if (!list.length) fail("failed-precondition", "There are no subscribers yet.");
  if (list.length > MAX_RECIPIENTS) fail("failed-precondition", `There are ${list.length} subscribers, more than this tool sends at once (${MAX_RECIPIENTS}). Use an email tool with the CSV.`);
  const ref = db.collection("campaigns").doc(id);
  await db.runTransaction(async (tx) => {
    const snap = await tx.get(ref);
    if (snap.exists) fail("already-exists", "This email was already sent. Write a new one to send again.");
    tx.set(ref, { ...campaign, status: "sending", total: list.length, sent: 0, failed: 0, createdAt: nowIso(), by });
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

/* ================================================================ automatic emails (the 1st and the 15th)
   The 1st: the designs of the season (the same calendar as the home page spotlight, catalog.json seasons), with three
   of its designs not shown in the last automatic emails. The 15th: photo magnets, with an idea that fits the month.
   Owners can turn it off in Hive Admin (settings/store autoNewsletter = 0). Nothing goes out without the shop's
   postal address (CAN-SPAM); the owners get one note a month when that blocks it. */
const TZ = "America/New_York";
const PHOTO_IDEAS = [
  /* Jan */ { frame: "instant", subject: "New year, new fridge", title: "Start the year with your favorite faces", body: "The holidays gave you a phone full of photos. Pick the best ones and we turn them into glossy magnets, with a frame and a caption if you like." },
  /* Feb */ { frame: "hearts", subject: "A little love on the fridge", title: "Your favorite photo, for Valentine's Day", body: "A sweet gift that stays: your favorite photo of the two of you, on a magnet with a little caption. Ready in a few days, made by hand." },
  /* Mar */ { frame: "arch", subject: "Spring is for new photos", title: "Fresh photos for a fresh season", body: "Kids growing, gardens blooming, a new pet at home: put the moments you love where you see them every day." },
  /* Apr */ { frame: "botanical", subject: "Photo magnets for Easter and spring", title: "Little gifts for the whole family", body: "Grandparents love a set of photo magnets of the grandkids. Upload your pictures, pick a frame and we do the rest." },
  /* May */ { frame: "gold-cream", subject: "For mom, from your camera roll", title: "The sweetest Mother's Day gift", body: "Her favorite people, on her fridge. Turn your photos into a set of magnets with a frame and a little caption, made by hand." },
  /* Jun */ { frame: "wedding", subject: "Weddings, graduations and big days", title: "Keep the big days close", body: "Wedding photos, a graduation, a new baby: a set of photo magnets is a sweet keepsake and a gift people actually use." },
  /* Jul */ { frame: "postcard", subject: "Your summer, on the fridge", title: "Postcards from your own trips", body: "Beach days, road trips and family visits: turn your summer photos into magnets with a little postcard frame and the name of the place." },
  /* Aug */ { frame: "datestamp", subject: "Before summer ends", title: "Save your summer before it's gone", body: "Pick ten photos from this summer and we turn them into magnets, with an old-camera date in the corner if you like." },
  /* Sep */ { frame: "circle", subject: "For the pets who rule the house", title: "Your pet, on the fridge", body: "Dogs, cats and every other little boss: a set of magnets of your pet, with their name in a little caption." },
  /* Oct */ { frame: "fall", subject: "Cozy season photos", title: "Fall photos, pumpkin patches and costumes", body: "Pumpkin patches, first costumes and cozy sweaters: turn this season's photos into magnets before the holidays arrive." },
  /* Nov */ { frame: "instant", subject: "The gift grandparents love", title: "A gift for the people you're thankful for", body: "Photo magnets of the grandkids are the gift grandparents keep on the fridge all year. Order early for the holidays." },
  /* Dec */ { frame: "holly", subject: "Last call for Christmas photo magnets", title: "A merry little gift, from your photos", body: "Photo magnets fit in any stocking and on every fridge in the family. Order by December 12 so they arrive before Christmas." },
];

function nyDate(now) {
  const p = new Intl.DateTimeFormat("en-US", { timeZone: TZ, year: "numeric", month: "2-digit", day: "2-digit" }).formatToParts(new Date(now))
    .reduce((a, x) => ((a[x.type] = x.value), a), {});
  return { y: Number(p.year), m: Number(p.month), d: Number(p.day), ymd: `${p.year}-${p.month}-${p.day}`, md: `${p.month}-${p.day}` };
}

/** The season of the home page calendar for MM-DD (ranges may wrap the new year). */
function seasonFor(md, seasons) {
  return (seasons || []).find((s) => (s.start <= s.end ? md >= s.start && md <= s.end : md >= s.start || md <= s.end)) || null;
}

/** Pure: the automatic campaign for a day. recentDesigns: designs used in the last automatic emails (avoided). */
function autoCampaign(now, { seasons = [], recentDesigns = [] } = {}) {
  const t = nyDate(now);
  if (t.d >= 10) {
    const idea = PHOTO_IDEAS[t.m - 1];
    return { subject: idea.subject, preheader: "", eyebrow: "Photo magnets", title: idea.title,
      body: `${idea.body}\n\nPacks start at 4 magnets for $14, and you can mix them with our designs in the same order.`,
      gallery: "photos", designs: [], promo: null,
      button: { label: "Make photo magnets", href: `https://littlehivehouse.com/photo-magnets.html?frame=${idea.frame}#custom` } };
  }
  const s = seasonFor(t.md, seasons) || { title: "New little things for your fridge", label: "From the hive", blurb: "Fresh designs, made by hand in our little house.", collection: "", picks: [] };
  const fresh = s.picks.filter((id) => !recentDesigns.includes(id));
  const designs = fresh.concat(s.picks.filter((id) => !fresh.includes(id))).slice(0, 3);
  const deadline = t.m === 11 && t.d >= 15 || t.m === 12 && t.d <= 12;
  return { subject: s.title, preheader: s.blurb, eyebrow: s.label, title: s.title,
    body: `${s.blurb}\n\nMix any 3 designs for $12. Every magnet is printed, pressed and packed by hand in our little house.` +
      (deadline ? "\n\nShopping for Christmas? Please order by December 12 so your magnets arrive in time." : ""),
    gallery: "designs", designs, promo: null,
    button: { label: s.collection ? `Shop ${s.label}` : "Visit the shop", href: s.collection ? `https://littlehivehouse.com/collections/${s.collection}.html` : "https://littlehivehouse.com/shop.html" } };
}

async function autoNewsletter(now = Date.now(), opts = {}) {
  const db = deps.db();
  const settings = await db.collection("settings").doc("store").get().then((s) => (s.exists ? s.data() : {})).catch(() => ({}));
  if (settings.autoNewsletter !== undefined && Number(settings.autoNewsletter) === 0) return { skipped: "turned off" };
  if (!env("RESEND_API_KEY")) return { skipped: "no email key" };
  const t = nyDate(now);
  if (!env("MAIL_POSTAL_ADDRESS")) {
    const note = db.collection("campaigns").doc(`auto-blocked-${t.y}-${String(t.m).padStart(2, "0")}`);
    const first = await db.runTransaction(async (tx) => { const s = await tx.get(note); if (s.exists) return false; tx.set(note, { status: "blocked", reason: "no postal address", createdAt: nowIso(), by: "automatic" }); return true; });
    if (first) await mail.send({ to: mailAdmin(), kind: "admin_newsletter", data: { mode: "blocked" } });
    return { skipped: "no postal address" };
  }
  const list = await recipients();
  if (!list.length) return { skipped: "no subscribers" };
  const recent = await db.collection("campaigns").orderBy("createdAt", "desc").limit(6).get()
    .then((q) => q.docs.map((d) => d.data()).filter((c) => c.by === "automatic").flatMap((c) => c.designs || [])).catch(() => []);
  const catalog = opts.catalog || require("./catalog.json");
  const campaign = clean(autoCampaign(now, { seasons: catalog.seasons, recentDesigns: recent }));
  let res;
  try {
    res = await sendCampaign(campaign, `auto-${t.ymd}`, "automatic", { list, fetchImpl: opts.fetchImpl, pause: opts.pause });
  } catch (err) {
    if (err && err.code === "already-exists") return { skipped: "already sent" };
    throw err;
  }
  await mail.send({ to: mailAdmin(), kind: "admin_newsletter", data: { mode: "sent", subject: campaign.subject, sent: res.sent, failed: res.failed, total: res.total } });
  return res;
}

module.exports = { adminNewsletter, sendCampaign, autoNewsletter, autoCampaign, seasonFor, clean, recipients, PHOTO_IDEAS };
