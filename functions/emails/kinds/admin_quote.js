// Big-order request forwarded to MAIL_ADMIN (send with replyTo = the customer). Not in the original list; handy for requestQuote.
"use strict";
const F = require("../format");
const Lay = require("../layout");

module.exports = function adminQuote(data, { L }) {
  const name = F.line(data.name, 80) || "Someone";
  const email = F.line(data.email, 120);
  const qty = F.num(data.quantity);
  const occasion = F.line(data.occasion, 60) || "Big order";
  const msg = F.str(data.message).trim().slice(0, 5000);
  return {
    subject: `New quote request: ${occasion}${qty ? `, ${qty} magnets` : ""}`,
    preheader: `${name}${data.date ? ` · needed by ${F.fmtDate(data.date)}` : ""} · ${F.line(msg, 80)}`,
    audience: "admin",
    replyTo: F.isEmail(email) ? email : undefined,
    blocks: [
      Lay.hero({ eyebrow: "Quote request", title: `${occasion}${qty ? ` · ${qty} magnets` : ""}`, lead: [`From ${name}. Promised reply: within 1 business day.`] }),
      Lay.facts([
        ["Name", name],
        ["Email", F.isEmail(email) ? [{ a: email, href: `mailto:${email}` }] : email],
        ["Phone", F.line(data.phone, 30)],
        ["Occasion", occasion],
        ["Magnets", qty ? String(qty) : ""],
        ["Needed by", data.date ? F.fmtDate(data.date) || F.line(data.date, 30) : "Flexible"],
      ]),
      msg ? Lay.box(`${Lay.label("Their idea")}${Lay.bodyText(F.esc(msg).replace(/\r?\n/g, "<br>"), { size: 15, lh: 23 })}`, `THEIR IDEA\n${msg}`, "cream") : null,
      Lay.buttons([{ href: `${L.adminHome}`, label: "Create a payment link", variant: "ink" }]),
    ],
  };
};
