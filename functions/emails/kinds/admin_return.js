// To the shop when a customer reports a problem on return.html (functions/returns.js). data: {ret, order}
"use strict";
const F = require("../format");
const Lay = require("../layout");

module.exports = function adminReturn(data, { L }) {
  const ret = data.ret || {};
  const num = F.line(ret.number, 30);
  const name = F.line(ret.name, 80) || "A customer";
  const ls = (ret.lines || []).map((l) => `${F.line(l.title, 80)} × ${Number(l.qty) || 1}`);
  return {
    subject: `Return request ${num}: ${F.line(ret.reasonLabel, 40) || "problem"}`,
    preheader: `${name} wants a ${ret.wants === "reprint" ? "reprint" : "refund"} for ${ret.magnets || ls.length} magnet(s).`,
    audience: "admin",
    blocks: [
      Lay.hero({ eyebrow: "Return", title: `${name}: ${F.line(ret.reasonLabel, 40) || "a problem"}`, lead: null }),
      Lay.facts([
        ["Order", num],
        ["Wants", ret.wants === "reprint" ? "A free reprint" : `A refund of ${F.money(ret.value)}`],
        ["Magnets", ls.join(", ")],
        ["Note", F.line(ret.note, 600)],
        ["Photos", `${(ret.photos || []).length} in the Hive Admin`],
      ]),
      Lay.buttons([{ href: `${L.site}/admin/#returns`, label: "See the photos and decide", variant: "ink" }]),
    ],
  };
};
