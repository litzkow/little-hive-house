// Sent to MAIL_ADMIN after each automatic email to the subscribers (newsletter.js autoNewsletter), or once a month when
// it could not go out because the shop's postal address (MAIL_POSTAL_ADDRESS) is missing. In Portuguese, for the owners.
"use strict";
const F = require("../format");
const Lay = require("../layout");

module.exports = function adminNewsletter(data, { L }) {
  if (data.mode === "blocked") {
    return {
      subject: "E-mail automático não foi enviado: falta o endereço",
      preheader: "A lei americana pede um endereço postal no rodapé dos e-mails de propaganda.",
      audience: "admin",
      blocks: [
        Lay.hero({ eyebrow: "E-mails para os inscritos", title: "Falta o endereço postal", lead: ["O e-mail automático para os inscritos não saiu porque a loja ainda não tem um endereço postal configurado. A lei americana (CAN-SPAM) pede esse endereço no rodapé de todo e-mail de propaganda. Pode ser uma PO Box."] }),
        Lay.p(["Quando tiver o endereço, peça ao Claude para colocá-lo no site. Os próximos e-mails automáticos saem sozinhos depois disso."], { muted: true, small: true }),
      ],
    };
  }
  const sent = Number(data.sent) || 0, failed = Number(data.failed) || 0;
  return {
    subject: `E-mail automático enviado para ${sent} ${sent === 1 ? "inscrito" : "inscritos"}`,
    preheader: F.line(data.subject, 120),
    audience: "admin",
    blocks: [
      Lay.hero({ eyebrow: "E-mails para os inscritos", title: F.line(data.subject, 120) || "E-mail enviado", lead: [`Enviado para ${sent} de ${Number(data.total) || sent} inscritos${failed ? ` (${failed} falharam)` : ""}. Vocês não precisam fazer nada.`] }),
      Lay.buttons([{ href: `${L.adminHome}#newsletter`, label: "Ver no Hive Admin", variant: "ghost" }]),
      Lay.p(["Para desligar os e-mails automáticos: Hive Admin › Email subscribers."], { muted: true, small: true }),
    ],
  };
};
