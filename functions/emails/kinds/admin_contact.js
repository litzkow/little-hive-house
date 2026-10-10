// Contact form message forwarded to MAIL_ADMIN (send with replyTo = the customer).
"use strict";
const F = require("../format");
const Lay = require("../layout");

module.exports = function adminContact(data, { L }) {
  const name = F.line(data.name, 80) || "Someone";
  const email = F.line(data.email, 120);
  const topic = F.line(data.topic, 60);
  const msg = F.str(data.message).trim().slice(0, 5000);
  const reply = F.isEmail(email) ? `mailto:${encodeURIComponent(email).replace(/%40/g, "@")}?subject=${encodeURIComponent("Re: " + (topic || "your message to Little Hive House"))}` : "";
  return {
    subject: `New message from ${name}${topic ? `: ${topic}` : ""}`,
    preheader: F.line(msg, 120),
    audience: "admin",
    replyTo: F.isEmail(email) ? email : undefined,
    blocks: [
      Lay.hero({ eyebrow: "Contact form", title: `Message from ${name}`, lead: null }),
      Lay.box(Lay.bodyText(F.esc(msg || "(empty message)").replace(/\r?\n/g, "<br>"), { size: 16, lh: 25 }), msg || "(empty message)", "cream"),
      Lay.facts([
        ["From", [name, email ? " · " : "", F.isEmail(email) ? { a: email, href: `mailto:${email}` } : email]],
        ["Topic", topic],
        ["Order", F.line(data.orderNumber, 30)],
        ["Occasion", data.quote && F.line(data.quote.occasion, 60)],
        ["Magnets", data.quote && F.num(data.quote.quantity) ? String(F.num(data.quote.quantity)) : ""],
        ["Needed by", data.quote && data.quote.date ? F.fmtDate(data.quote.date) || F.line(data.quote.date, 30) : ""],
        ["Sent", F.fmtDate(data.at || new Date(), true)],
      ]),
      Lay.buttons([reply ? { href: reply, label: `Reply to ${F.firstName(name) || "them"}`, variant: "ink" } : null]),
      Lay.p(["Tip: replying to this email also goes straight to the customer."], { muted: true, small: true }),
    ],
  };
};
