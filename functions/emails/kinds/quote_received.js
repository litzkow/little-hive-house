// Confirmation to the customer after the big-order form (callable `requestQuote`).
"use strict";
const F = require("../format");
const Lay = require("../layout");

module.exports = function quoteReceived(data, { L }) {
  const first = F.firstName(data.name);
  const qty = F.num(data.quantity);
  const occasion = F.line(data.occasion, 60);
  const msg = F.str(data.message).trim().slice(0, 2000);
  return {
    subject: "We got your big order request",
    preheader: `Thanks! We'll reply within 1 business day with ideas, a price${qty ? ` for ${qty} magnets` : ""} and next steps.`,
    blocks: [
      Lay.hero({ eyebrow: "Big order request", title: first ? `Thank you, ${first}!` : "Thank you!", lead: ["We love a big project. We'll look at your idea and reply within 1 business day with a price, ideas and next steps."] }),
      Lay.facts([
        ["Occasion", occasion],
        ["Magnets", qty ? String(qty) : ""],
        ["Needed by", data.date ? F.fmtDate(data.date) || F.line(data.date, 30) : "Flexible"],
        ["Your idea", msg ? F.line(msg, 600) : ""],
      ]),
      Lay.h2("How it works"),
      Lay.steps([
        { title: "We reply with a quote", body: "With your volume price, plus a secure payment link whenever you're ready." },
        { title: "You approve a proof", body: "We design it with your names, date, logo or photos. Nothing prints until you say yes." },
        { title: "We make and ship", body: "Printed and pressed by hand. Most big orders ship 7 to 10 business days after you approve the proof." },
      ]),
      Lay.p(["Have photos, a logo or a color palette? Reply to this email and attach them."], { muted: true, small: true }),
      Lay.buttons([{ href: L.big, label: "See packages and prices", variant: "ghost" }]),
    ],
    reason: "You're getting this email because you asked for a big order quote at littlehivehouse.com.",
  };
};
