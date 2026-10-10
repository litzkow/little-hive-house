// Sent after sign-up (welcome callable) and by sendVerifyEmail, with the link from getAuth().generateEmailVerificationLink.
"use strict";
const F = require("../format");
const Lay = require("../layout");

module.exports = function verifyEmail(data, { L }) {
  const link = F.safeUrl(data.link);
  const first = F.firstName(data.name);
  const email = F.line(data.email, 120);
  return {
    subject: "Please confirm your email for Little Hive House",
    preheader: "One tap to confirm it's you. Then every order you place with this email shows up in your account.",
    blocks: [
      Lay.hero({
        eyebrow: "Confirm your email",
        title: first ? `One quick tap, ${first}!` : "One quick tap!",
        lead: ["Please confirm that ", { b: email || "this address" }, " is yours, so your account is safe and your order updates reach you."],
      }),
      Lay.buttons([{ href: link || L.account, label: "Confirm my email", variant: "honey" }], { full: true }),
      Lay.h2("Once it's confirmed"),
      Lay.steps([
        { title: "Your orders, all in one place", body: "Orders you placed as a guest with this email show up in your account, with their tracking." },
        { title: "Leave reviews", body: "Tell us how your magnets turned out, right from the order page." },
      ]),
      link ? Lay.p(["Button not working? Copy this link into your browser:"], { muted: true, small: true, pad: "0 0 6px" }) : null,
      link ? Lay.raw(`<p class="lh-m" style="margin:0;font-family:Menlo,Consolas,monospace;font-size:12px;line-height:18px;color:${Lay.C.muted};word-break:break-all"><a class="lh-a" href="${F.esc(link)}" style="color:${Lay.C.link}">${F.esc(link)}</a></p>`, "", "0 0 22px") : null,
      Lay.box(Lay.bodyText("<strong style=\"font-weight:600\">Didn't create an account?</strong> You can ignore this email. Nothing happens unless the link is tapped.", { size: 14, lh: 21 }),
        "Didn't create an account? You can ignore this email. Nothing happens unless the link is tapped.", "cream"),
    ],
    reason: "You're getting this email because an account was created at littlehivehouse.com with this address.",
  };
};
