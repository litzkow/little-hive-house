// Sent to MAIL_ADMIN on the 12th of each month by salestax.js: last month's Georgia Sales & Use Tax return.
// Written in Portuguese on purpose: it is a how-to for the owners, not a customer email.
"use strict";
const F = require("../format");
const Lay = require("../layout");

module.exports = function adminSalesTax(data, { L }) {
  const p = data.period || {};
  const s = data.summary || {};
  const label = F.line(p.label, 40) || "o mês passado";
  const due = F.line(p.dueLabel, 40) || "dia 20";
  const zero = !(Number(s.gaSales) > 0) && !(Number(s.gaTax) > 0);
  const money = (n) => F.money(n, "usd");

  const steps = zero ? [
    { title: "Entre no Georgia Tax Center", body: "gtc.dor.ga.gov, login litzkow." },
    { title: "Abra a declaração", body: `Na caixa Sales & Use Tax, toque em View Returns e depois em File Return do período de ${label}.` },
    { title: "Declare zero", body: "Coloque 0 nas vendas (Gross Sales) e envie. Não há nada a pagar." },
    { title: "Pronto", body: "Guarde o número de confirmação que aparece no final." },
  ] : [
    { title: "Pegue os valores por condado no Stripe", body: `Stripe › Tax › Reports › exporte o relatório de ${label} para Georgia. Ele mostra as vendas e o imposto separados por condado (cada condado tem uma taxa).` },
    { title: "Entre no Georgia Tax Center", body: `gtc.dor.ga.gov, login litzkow. Na caixa Sales & Use Tax, toque em View Returns e depois em File Return do período de ${label}.` },
    { title: "Preencha", body: `Gross Sales: ${money(s.sales)} (todas as vendas do mês, sem o imposto). Vendas para fora da Georgia (${money(s.otherSales)}) entram como dedução (out-of-state sales). Depois digite as vendas da Georgia por condado, como no relatório do Stripe.` },
    { title: "Confira e pague", body: `O imposto da Georgia deve dar perto de ${money(s.gaTax)}${Number(s.gaRefundedTax) > 0 ? ` (menos ${money(s.gaRefundedTax)} de imposto devolvido em reembolsos)` : ""}. O site calcula, mostra o desconto por declarar no prazo (vendor's compensation) e debita da conta do banco.` },
  ];

  return {
    subject: zero ? `Sales tax de ${label}: declarar zerado até ${due}` : `Sales tax de ${label}: declarar ${money(s.gaTax)} até ${due}`,
    preheader: zero ? "Sem vendas na Georgia no mês: é só enviar a declaração com zero." : `${s.gaOrders || 0} pedido(s) na Georgia, ${money(s.gaTax)} de imposto cobrado dos clientes.`,
    audience: "admin",
    blocks: [
      Lay.hero({ eyebrow: "Sales & Use Tax · Georgia", title: `Declaração de ${label}`, lead: [`Prazo: ${due}. ${zero ? "Não houve vendas na Georgia, então a declaração vai zerada, mas precisa ser enviada para não ter multa." : "O imposto já foi pago pelos clientes no checkout e está no saldo do Stripe: é só repassar."}`] }),
      Lay.facts([
        ["Pedidos no mês", String(s.orders || 0)],
        ["Vendas (sem imposto)", money(s.sales)],
        ["Vendas na Georgia", money(s.gaSales)],
        ["Imposto da Georgia cobrado", money(s.gaTax)],
        ["Vendas para outros estados", money(s.otherSales)],
        ["Reembolsos no mês", money(s.refunds)],
      ]),
      Lay.h2("Como declarar"),
      Lay.steps(steps),
      Lay.buttons([
        { href: "https://gtc.dor.ga.gov/", label: "Abrir o Georgia Tax Center", variant: "ink" },
        zero ? null : { href: "https://dashboard.stripe.com/tax/reports", label: "Relatórios do Stripe Tax", variant: "ghost" },
        { href: `${L.adminHome}#reports`, label: "Reports no Hive Admin", variant: "ghost" },
      ]),
      Lay.p(["Uma venda conta no mês em que o cartão foi cobrado (quando o pedido foi enviado)."], { small: true, muted: true }),
    ],
  };
};
