// Auto-reply to the contact form (callable `contact`).
"use strict";
const F = require("../format");
const Lay = require("../layout");

module.exports = function contactAutoreply(data, { L }) {
  const first = F.firstName(data.name);
  const msg = F.str(data.message).trim().slice(0, 2000);
  return {
    subject: "We got your message",
    preheader: "Thanks for writing! A real person will reply within 1 to 2 business days.",
    blocks: [
      Lay.hero({ eyebrow: "Message received", title: first ? `Thanks for writing, ${first}!` : "Thanks for writing!", lead: ["Your message landed safely in our inbox. One of us will read it and reply personally, usually within 1 to 2 business days."] }),
      msg ? Lay.box(`${Lay.label(data.topic ? `You wrote · ${F.line(data.topic, 60)}` : "You wrote")}${Lay.bodyText(F.esc(msg).replace(/\r?\n/g, "<br>"), { size: 15, lh: 23 })}`, `YOU WROTE${data.topic ? ` (${F.line(data.topic, 60)})` : ""}\n${msg}`, "cream") : null,
      Lay.p(["Want to add something? Just reply to this email, it comes straight to us."], { muted: true, small: true }),
      Lay.h2("While you wait"),
      Lay.buttons([
        { href: L.shop, label: "Browse designs", variant: "honey" },
        { href: L.track(""), label: "Track an order", variant: "ghost" },
      ]),
    ],
    reason: "You're getting this email because you sent us a message at littlehivehouse.com.",
  };
};
