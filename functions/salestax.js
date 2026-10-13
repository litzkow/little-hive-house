"use strict";
/* Monthly Georgia sales tax reminder (the owners file a Sales & Use Tax return every month, due the 20th).
   On the 12th it emails the shop (in Portuguese, for the owners) and pushes a notification with last month's numbers:
   sales, Georgia sales and the Georgia sales tax the customers paid, or "file a zero return" when there was none.
   A sale counts in the month the card was charged (cash basis; with charge on ship that is when the order shipped). */

const { mailAdmin } = require("./config");
const deps = require("./deps");
const mail = require("./mail");
const { cents, dollars } = require("./pricing");

const TZ = "America/New_York";
const MONTHS_PT = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"];

function nyParts(ms) {
  const p = new Intl.DateTimeFormat("en-US", { timeZone: TZ, year: "numeric", month: "numeric", day: "numeric", hour: "numeric", hourCycle: "h23" })
    .formatToParts(new Date(ms)).reduce((a, x) => ((a[x.type] = Number(x.value)), a), {});
  return { y: p.year, m: p.month - 1, d: p.day, h: p.hour };
}
/** UTC ms of midnight in New York on y-m-1 (m 0-based, may overflow into the next year). */
function nyMonthStart(y, m) {
  const yy = y + Math.floor(m / 12), mm = ((m % 12) + 12) % 12;
  let t = Date.UTC(yy, mm, 1, 4);
  for (let i = 0; i < 3 && nyParts(t).h !== 0; i++) t += 3600000;
  return t;
}
/** The month before `now`: {start, end (exclusive), label, year, month, due (ISO date of the 20th, moved past weekends)}. */
function previousMonth(now = Date.now()) {
  const n = nyParts(now);
  const start = nyMonthStart(n.y, n.m - 1), end = nyMonthStart(n.y, n.m);
  const p = nyParts(start);
  const due = new Date(Date.UTC(n.y, n.m, 20));
  while (due.getUTCDay() === 0 || due.getUTCDay() === 6) due.setUTCDate(due.getUTCDate() + 1);
  return { start, end, year: p.y, month: p.m, label: `${MONTHS_PT[p.m]} de ${p.y}`, due: due.toISOString().slice(0, 10),
    dueLabel: `${due.getUTCDate()} de ${MONTHS_PT[due.getUTCMonth()]}` };
}

/** When the money was actually charged, or null when it never was. */
function saleTime(o) {
  const p = o.payment || {};
  if (p.state === "authorized" || p.state === "released" || p.state === "expired") return p.capturedAt ? Date.parse(p.capturedAt) : null;
  if (p.capturedAt) return Date.parse(p.capturedAt);
  if (!o.paidAt || o.status === "pending") return null;
  return Date.parse(o.paidAt);
}
const isGA = (o) => {
  const a = (o.shipping && o.shipping.address) || {};
  return String((o.pricing && o.pricing.taxState) || a.state || "").toUpperCase() === "GA" && String(a.country || "US").toUpperCase() === "US";
};

/** Pure: the month's numbers from [{id, data}]. */
function summarize(docs, start, end) {
  const out = { orders: 0, sales: 0, gaOrders: 0, gaSales: 0, gaTax: 0, otherSales: 0, otherTax: 0, refunds: 0, gaRefundedTax: 0, list: [] };
  let sales = 0, gaSales = 0, gaTax = 0, otherSales = 0, otherTax = 0, refunds = 0, gaRefTax = 0;
  for (const { id, data: o } of docs) {
    const t = saleTime(o);
    const total = cents((o.pricing && o.pricing.total) || 0), tax = cents((o.pricing && o.pricing.tax) || 0);
    if (t !== null && t >= start && t < end) {
      out.orders += 1;
      sales += total - tax;
      if (isGA(o)) { out.gaOrders += 1; gaSales += total - tax; gaTax += tax; } else { otherSales += total - tax; otherTax += tax; }
      out.list.push({ id, number: o.number || "", ga: isGA(o), total: dollars(total), tax: dollars(tax) });
    }
    for (const r of Array.isArray(o.refunds) ? o.refunds : []) {
      const rt = Date.parse(r.at || "");
      if (!(rt >= start && rt < end) || (r.status && r.status !== "succeeded" && r.status !== "pending")) continue;
      const amt = cents(r.amount || 0);
      refunds += amt;
      if (isGA(o) && total > 0) gaRefTax += Math.round(amt * tax / total);
    }
  }
  return { ...out, sales: dollars(sales), gaSales: dollars(gaSales), gaTax: dollars(gaTax), otherSales: dollars(otherSales), otherTax: dollars(otherTax),
    refunds: dollars(refunds), gaRefundedTax: dollars(gaRefTax) };
}

async function salesTaxReminder(now = Date.now()) {
  const period = previousMonth(now);
  // orders are authorized at most ~7 days before they are charged, so look a little before the month
  const since = new Date(period.start - 40 * 86400000).toISOString();
  const q = await deps.db().collection("orders").where("paidAt", ">=", since).get();
  const sum = summarize(q.docs.map((d) => ({ id: d.id, data: d.data() })), period.start, period.end);
  await mail.send({ to: mailAdmin(), kind: "admin_sales_tax", data: { period, summary: sum } });
  return { period: period.label, ...sum, list: undefined };
}

module.exports = { salesTaxReminder, summarize, previousMonth, saleTime, nyMonthStart };
