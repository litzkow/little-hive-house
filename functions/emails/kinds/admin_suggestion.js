// A customer's idea from the Ideas box (suggestions.html), sent to MAIL_ADMIN. In Portuguese, for the owners.
// replyTo is the customer when they left an email.
"use strict";
const F = require("../format");
const Lay = require("../layout");

const KIND_PT = { design: "Ideia de design novo", place: "Um lugar para desenhar", site: "O site", other: "Outra coisa" };

module.exports = function adminSuggestion(data, { L }) {
  const s = data.suggestion || data;
  const name = F.line(s.name, 80);
  const email = F.line(s.email, 120);
  const kind = KIND_PT[s.kind] || KIND_PT.other;
  const idea = F.str(s.idea).trim().slice(0, 3000);
  const reply = F.isEmail(email) ? `mailto:${encodeURIComponent(email).replace(/%40/g, "@")}?subject=${encodeURIComponent("Your idea for Little Hive House")}` : "";
  return {
    subject: `💡 Um cliente mandou uma sugestão: ${F.line(idea, 60)}`,
    preheader: `${kind} · ${F.line(idea, 100)}`,
    audience: "admin",
    replyTo: F.isEmail(email) ? email : undefined,
    blocks: [
      Lay.hero({ eyebrow: "Caixa de ideias do site", title: `${name ? F.firstName(name) : "Um cliente"} mandou uma sugestão`, lead: null }),
      Lay.box(Lay.bodyText(F.esc(idea || "(vazia)").replace(/\r?\n/g, "<br>"), { size: 16, lh: 25 }), idea || "(vazia)", "cream"),
      Lay.facts([
        ["Tipo", kind],
        ["Nome", name || "Não informou"],
        ["E-mail", F.isEmail(email) ? { a: email, href: `mailto:${email}` } : "Não informou"],
        ["Enviada", F.fmtDate(s.at || new Date(), true)],
      ]),
      Lay.buttons([
        reply ? { href: reply, label: `Responder ${F.firstName(name) || "o cliente"}`, variant: "ink" } : null,
        { href: `${L.adminHome}#messages?tab=suggestions`, label: "Ver no Hive Admin", variant: "ghost" },
      ]),
      Lay.p([reply ? "Responder este e-mail também vai direto para o cliente (escreva em inglês)." : "O cliente não deixou e-mail, então não dá para responder."], { muted: true, small: true }),
    ],
  };
};
