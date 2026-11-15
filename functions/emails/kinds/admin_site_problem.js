// A customer hit a problem on the site (functions/clientlog.js). For the owners only, in Portuguese.
"use strict";
const F = require("../format");
const Lay = require("../layout");

module.exports = function adminSiteProblem(data) {
  const p = data.problem || data;
  const title = F.line(p.title, 120) || "Problema no site";
  const n = Number(p.count) > 1 ? Number(p.count) : 1;
  return {
    subject: `⚠️ ${title}${n > 1 ? ` (${n} vezes)` : ""}`,
    preheader: F.line(p.msg, 120),
    audience: "admin",
    blocks: [
      Lay.hero({ eyebrow: "Aviso automático do site", title, lead: n > 1 ? `Aconteceu ${n} vezes desde o último aviso.` : null }),
      Lay.facts([
        ["Página", F.line(p.page, 200)],
        ["Mensagem", F.line(p.msg, 300)],
        ["Código", F.line(p.code, 80)],
        ["Fotos", p.photos != null ? String(p.photos) : ""],
        ["Idioma do site", p.lang === "pt" ? "Português" : "Inglês"],
        ["Aparelho", F.line(p.ua, 200)],
        ["Quando", F.fmtDate(p.at || new Date(), true)],
      ]),
      Lay.p(["Vocês recebem no máximo um aviso deste tipo a cada 3 horas. A lista completa fica guardada por 90 dias no Firebase (clientErrors)."], { muted: true, small: true }),
    ],
  };
};
