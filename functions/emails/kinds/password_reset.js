// Sent by sendPasswordReset with the link from getAuth().generatePasswordResetLink.
"use strict";
const F = require("../format");
const Lay = require("../layout");

module.exports = function passwordReset(data, { L }) {
  const link = F.safeUrl(data.link);
  const first = F.firstName(data.name);
  const mins = F.num(data.expiresMinutes) || 60;
  const expires = mins % 60 === 0 ? F.plural(mins / 60, "hour") : F.plural(mins, "minute");
  return {
    subject: "Reset your Little Hive House password",
    preheader: `Tap the button to choose a new password. The link works for ${expires}.`,
    blocks: [
      Lay.hero({
        eyebrow: "Password reset",
        title: "Let's get you back in",
        lead: [first ? `Hi ${first}! ` : "Hi! ", "Someone (hopefully you) asked to reset the password for ", { b: F.line(data.email, 120) || "your account" }, ". Tap below to choose a new one."],
      }),
      Lay.buttons([{ href: link || L.account, label: "Choose a new password", variant: "honey" }], { full: true }),
      Lay.p([`For your security this link expires in ${expires} and works only once. If it has expired, you can `, { a: "ask for a new one", href: L.account }, "."], { muted: true, small: true }),
      link ? Lay.p(["Button not working? Copy this link into your browser:"], { muted: true, small: true, pad: "0 0 6px" }) : null,
      link ? Lay.raw(`<p class="lh-m" style="margin:0;font-family:Menlo,Consolas,monospace;font-size:12px;line-height:18px;color:${Lay.C.muted};word-break:break-all"><a class="lh-a" href="${F.esc(link)}" style="color:${Lay.C.link}">${F.esc(link)}</a></p>`, "", "0 0 22px") : null,
      Lay.box(Lay.bodyText("<strong style=\"font-weight:600\">Didn't ask for this?</strong> You can ignore this email. Your password stays the same and nobody can change it without this link.", { size: 14, lh: 21 }),
        "Didn't ask for this? You can ignore this email. Your password stays the same.", "cream"),
    ],
    reason: "You're getting this email because a password reset was requested for your account.",
  };
};
