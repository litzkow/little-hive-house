// Returns started on return.html (functions/returns.js). data: {mode, ret, order, reprintNumber?}
//   received : a problem was reported, we'll look at the photos within a business day
//   label    : change of mind, the prepaid USPS return label (QR code + printable label)
//   reprint  : the problem was approved as a free reprint
//   declined : we couldn't accept it (with the owners' note)
// The refund itself goes out with the "refund" email.
"use strict";
const F = require("../format");
const Lay = require("../layout");

function list(ret) {
  const ls = (ret.lines || []).map((l) => `${F.line(l.title, 80)}${Number(l.qty) > 1 ? ` × ${Number(l.qty)}` : ""}`);
  return Lay.box(`${Lay.label("In this return")}${Lay.bodyText(ls.map(F.esc).join("<br>"), { size: 15, lh: 23 })}`, `In this return:\n${ls.join("\n")}`, "cream");
}

module.exports = function returnUpdate(data, { L }) {
  const ret = data.ret || {};
  const order = data.order || {};
  const num = F.line(ret.number || order.number, 30);
  const first = F.firstName(ret.name || order.name);
  const hi = first ? `Hi ${first}. ` : "";
  const mode = data.mode;
  const returnPage = `${L.site}/return.html${num ? `?number=${encodeURIComponent(num)}` : ""}`;
  const reason = "You're getting this email because you started a return at littlehivehouse.com.";

  if (mode === "label") {
    const lb = ret.label || {};
    const est = ret.estimate || {};
    const qr = F.safeUrl(lb.qr);
    const trackUrl = F.trackingUrl("usps", lb.tracking);
    return {
      subject: `Your return label for ${num || "your order"}`,
      preheader: "Show the QR code at any Post Office, or print the label. Your refund goes out as soon as it reaches us.",
      blocks: [
        Lay.hero({ eyebrow: num ? `Return · ${num}` : "Return", title: "Here's your return label", lead: [hi, "Pack the magnets in any envelope and drop it off with USPS. Your refund goes out by itself as soon as the package reaches us."] }),
        qr ? Lay.box(
          `${Lay.label("No printer? Show this at the Post Office")}<img src="${F.esc(qr)}" width="200" height="200" alt="USPS return QR code" style="display:block;margin:10px auto 8px;width:200px;height:200px;border-radius:8px;background:#fff">` +
          Lay.bodyText("At the counter or a self-service kiosk, they scan it and print the label for you.", { muted: true, size: 14, lh: 20 }),
          `No printer? Show this QR code at the Post Office: ${qr}`, "honey", { center: true, pad: "20px 22px" }) : null,
        Lay.buttons([{ href: lb.url, label: qr ? "Or print the label" : "Print your return label", variant: qr ? "ghost" : "honey" }], { full: true, pad: "0 0 26px" }),
        Lay.steps([
          { title: "Pack it", body: "Put the magnets in an envelope or a small box and seal it." },
          { title: "Drop it off", body: qr ? "Show the QR code at a Post Office, or tape the printed label on and drop it in any USPS mailbox." : "Tape the label on and drop it at a Post Office or in any USPS mailbox." },
          { title: "Get your refund", body: "When USPS shows it delivered to us, the refund goes back to your card automatically. We email you when it does." },
        ]),
        list(ret),
        Lay.facts([
          ["Magnets", F.money(est.value)],
          ["Return shipping", est.labelCost ? `− ${F.money(est.labelCost)}` : ""],
          ["Your refund", F.money(est.refund)],
          ["Tracking", lb.tracking && trackUrl ? { a: lb.tracking, href: trackUrl } : F.line(lb.tracking, 40)],
        ]),
        Lay.p(["Changed your mind again? Just don't send it. An unused label costs nothing."], { muted: true, small: true }),
      ],
      reason,
    };
  }

  if (mode === "reprint") {
    return {
      subject: `We're reprinting your magnets (${num || "your order"})`,
      preheader: "New ones are on the way, free. Nothing to send back.",
      blocks: [
        Lay.hero({ eyebrow: num ? `Order ${num}` : "Reprint", title: "New ones are on the way", lead: [hi, "Thanks for the photos and sorry about that. We're printing new magnets for you, free, and you don't need to send anything back."] }),
        list(ret),
        Lay.p(["They ship within 3 to 5 business days", data.reprintNumber ? [" as order ", { b: F.line(data.reprintNumber, 30) }] : "", ", and we email you the tracking link when they do."].flat()),
        Lay.buttons([{ href: returnPage, label: "See your return", variant: "honey" }]),
      ],
      reason,
    };
  }

  if (mode === "declined") {
    const note = F.line(ret.declineNote, 600);
    return {
      subject: `About your return for ${num || "your order"}`,
      preheader: "We looked at your request.",
      blocks: [
        Lay.hero({ eyebrow: num ? `Return · ${num}` : "Return", title: "About your return", lead: [hi, "We looked at your request and couldn't accept this one."] }),
        note ? Lay.box(`${Lay.label("A note from us")}${Lay.bodyText(F.esc(note), { size: 15, lh: 23 })}`, `A note from us: ${note}`, "cream") : null,
        list(ret),
        Lay.p(["If we got something wrong, just reply to this email. A real person reads every message."]),
        Lay.buttons([{ href: L.returns, label: "Returns policy", variant: "ghost" }]),
      ],
      reason,
    };
  }

  // received
  return {
    subject: `We got your return request (${num || "your order"})`,
    preheader: "We'll look at your photos and reply within one business day.",
    blocks: [
      Lay.hero({ eyebrow: num ? `Return · ${num}` : "Return", title: "We got your request", lead: [hi, "Sorry something wasn't right. We'll look at your photos and get back to you within one business day with your ", { b: ret.wants === "reprint" ? "free reprint" : "refund" }, "."] }),
      list(ret),
      Lay.p(["You don't need to send anything back."]),
      Lay.buttons([{ href: returnPage, label: "See your return", variant: "honey" }]),
    ],
    reason,
  };
};
