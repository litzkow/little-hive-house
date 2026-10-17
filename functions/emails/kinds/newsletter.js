// A campaign the owners write in Hive Admin (functions/newsletter.js) and send to the subscribers.
// data.campaign = {subject, preheader, eyebrow, title, body (paragraphs split by blank lines), gallery: "designs"|"photos"|"none",
//                  designs: ["col/slug" x3], promo: {code, text}|null, button: {label, href}}
"use strict";
const F = require("../format");
const Lay = require("../layout");
const O = require("../order-parts");

const PHOTO_SAMPLES = [["showcase/wedding-1", "Weddings"], ["showcase/family-1", "Family"], ["showcase/pets-2", "Pets"]];

module.exports = function newsletter(data, { L }) {
  const c = data.campaign && typeof data.campaign === "object" ? data.campaign : {};
  const paras = String(c.body || "").split(/\n\s*\n/).map((s) => F.line(s, 900)).filter(Boolean).slice(0, 8);
  const title = F.line(c.title, 120) || F.line(c.subject, 120) || "News from the hive";
  const promo = c.promo && F.line(c.promo.code, 30) ? c.promo : null;
  let gallery = null;
  if (c.gallery === "photos") {
    gallery = Lay.gallery(PHOTO_SAMPLES.map(([id, label]) => ({ src: L.designThumb(id), title: label, alt: `${label} photo magnet`, href: L.photos })));
  } else if (c.gallery !== "none") {
    const picks = (Array.isArray(c.designs) ? c.designs : []).filter((id) => /^[a-z0-9-]+\/[a-z0-9-]+$/.test(String(id))).slice(0, 3);
    gallery = Lay.gallery(O.featured(picks.length ? { featured: picks.map((id) => ({ id })) } : {}, L));
  }
  const btn = c.button && F.line(c.button.label, 40) ? { href: F.safeUrl(c.button.href, L.shop) || L.shop, label: F.line(c.button.label, 40), variant: "honey" } : { href: L.shop, label: "Visit the shop", variant: "honey" };
  return {
    subject: F.line(c.subject, 120) || title,
    preheader: F.line(c.preheader, 160) || (paras[0] || ""),
    blocks: [
      Lay.hero({ eyebrow: F.line(c.eyebrow, 40) || "From the hive", title, lead: paras.length ? [paras[0]] : [] }),
      ...paras.slice(1).map((s) => Lay.p([s])),
      promo ? Lay.code(F.line(promo.code, 30), [F.line(promo.text, 140) || "Enter it at checkout."]) : null,
      gallery,
      Lay.buttons([btn, { href: L.photos, label: "Photo magnets", variant: "ghost" }]),
      Lay.p(["With love, from our little hive to your fridge"], { muted: true }),
    ],
    reason: "You're getting this email because you signed up for news from Little Hive House.",
    marketing: true,
    unsubscribeUrl: data.unsubscribeUrl,
  };
};
