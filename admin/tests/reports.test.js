/* Run: node --test admin/tests/ */
'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const R = require('../reports.js');

const at = (y, m, d, h = 12) => new Date(y, m - 1, d, h).getTime();
const ts = (ms) => ({ toDate: () => new Date(ms), toMillis: () => ms });   /* like a Firestore Timestamp */

const SETTINGS = { magnetUnitCost: 0.5, packagingCost: 1, defaultLabelCost: 4, stripePct: 3, stripeFixed: 0.30, monthlyFixedCosts: 10 };

const ORDERS = [
  { id: 'A', number: 'LHH-1001', email: 'a@x.com', name: 'Ann', status: 'delivered', createdAt: ts(at(2026, 9, 5)), paidAt: ts(at(2026, 9, 5)),
    items: [{ kind: 'design', id: 'places/new-york', title: 'New York', collection: 'places', qty: 3, unit: 5 },
            { kind: 'design', id: 'fall/cozy-season', title: 'Cozy Season', collection: 'fall', qty: 1, unit: 5 }],
    pricing: { subtotal: 20, bundleDiscount: 3, volumePct: 0, volumeDiscount: 0, promo: null, shipping: 4.95, total: 21.95 },
    stripe: { fee: 0.94 }, fulfillment: { carrier: 'usps', tracking: '9400', labelCost: 4.20, shippedAt: ts(at(2026, 9, 6)), deliveredAt: ts(at(2026, 9, 9)) } },
  /* free shipping, estimated fee, shipped without a label cost, partial refund paid back in the NEXT month */
  { id: 'B', number: 'LHH-1002', email: 'B@x.com', name: 'Bea', status: 'partially_refunded', createdAt: ts(at(2026, 9, 10)), paidAt: ts(at(2026, 9, 10)),
    items: [{ kind: 'photos', packSize: 16, price: 40, photos: [{ path: 'uploads/u/p/1.jpg', frame: 'instant', caption: 'Hi' }] }],
    pricing: { subtotal: 40, bundleDiscount: 0, volumePct: 0, volumeDiscount: 0, promo: null, shipping: 0, total: 40 },
    stripe: {}, fulfillment: { carrier: 'usps', tracking: '9401', shippedAt: ts(at(2026, 9, 11)) },
    refunds: [{ id: 're_1', amount: 10, reason: 'damaged', note: '2 cracked', at: ts(at(2026, 10, 3)), by: 'owner' }], refundedTotal: 10 },
  /* full refund the next day, never shipped; same customer as A (repeat inside the month) */
  { id: 'C', number: 'LHH-1003', email: 'a@x.com', status: 'refunded', createdAt: ts(at(2026, 9, 20)), paidAt: ts(at(2026, 9, 20)),
    items: [{ kind: 'design', id: 'halloween/boo', title: 'Boo', collection: 'halloween', qty: 1, unit: 5 }],
    pricing: { subtotal: 5, bundleDiscount: 0, volumeDiscount: 0, promo: null, shipping: 4.95, total: 9.95 },
    stripe: { fee: 0.59 }, refunds: [{ amount: 9.95, reason: 'changed_mind', at: ts(at(2026, 9, 21)) }], refundedTotal: 9.95 },
  /* abandoned checkout: not a sale */
  { id: 'D', email: 'z@x.com', status: 'pending', createdAt: ts(at(2026, 9, 25)),
    items: [{ kind: 'package', id: 'business-100', title: 'Business', size: 100, price: 160, qty: 1 }],
    pricing: { subtotal: 160, shipping: 0, total: 100 } },
  /* package, volume discount and a promo code */
  { id: 'E', number: 'LHH-1005', email: 'c@x.com', status: 'paid', createdAt: ts(at(2026, 10, 2)), paidAt: ts(at(2026, 10, 2)),
    items: [{ kind: 'package', id: 'weddings-50', title: 'Weddings', size: 50, price: 95, qty: 1 }],
    pricing: { subtotal: 95, bundleDiscount: 0, volumePct: 20, volumeDiscount: 19, promo: { code: 'HIVE5', amount: 5 }, shipping: 0, total: 71 },
    stripe: { fee: 2.36 } },
  /* an August order makes b@x a returning customer in September */
  { id: 'F', number: 'LHH-1000', email: 'b@x.com', status: 'delivered', createdAt: ts(at(2026, 8, 30)), paidAt: ts(at(2026, 8, 30)),
    items: [{ kind: 'design', id: 'places/chicago', title: 'Chicago', collection: 'places', qty: 1, unit: 5 }],
    pricing: { subtotal: 5, shipping: 4.95, total: 9.95 }, stripe: { fee: 0.59 }, fulfillment: { labelCost: 4.5, shippedAt: ts(at(2026, 8, 31)) } },
  /* canceled before payment: not a sale */
  { id: 'G', email: 'q@x.com', status: 'canceled', createdAt: ts(at(2026, 9, 15)), pricing: { subtotal: 5, total: 9.95 } },
  { id: 'H', number: 'LHH-1004', email: 'd@x.com', status: 'delivered', createdAt: ts(at(2026, 9, 28)), paidAt: ts(at(2026, 9, 28)),
    items: [{ kind: 'design', id: 'christmas/believe', title: 'Believe', collection: 'christmas', qty: 2, unit: 5 }],
    pricing: { subtotal: 10, shipping: 4.95, total: 14.95 }, stripe: { fee: 0.73 },
    fulfillment: { labelCost: 4.5, shippedAt: ts(at(2026, 9, 29)), deliveredAt: ts(at(2026, 10, 1)) } }
];

test('September: sales, refunds, costs, profit, margin, ROI, AOV, repeat rate', () => {
  const m = R.monthMetrics(ORDERS, SETTINGS, '2026-09');
  assert.equal(m.orders, 4);
  assert.equal(m.magnets, 23);
  assert.equal(m.grossSales, 75);
  assert.equal(m.discounts, 3);
  assert.equal(m.shippingCharged, 14.85);
  assert.equal(m.totalCollected, 86.85);
  assert.equal(m.refunds, 9.95);          // only C; B's refund happened in October
  assert.equal(m.refundCount, 1);
  assert.equal(m.netSales, 76.90);
  assert.equal(m.stripeFees, 3.76);       // 0.94 + 1.50 (estimated) + 0.59 + 0.73
  assert.equal(m.feesEstimated, 1);
  assert.equal(m.labels, 12.70);          // 4.20 + 4.00 (default) + 0 + 4.50
  assert.equal(m.labelsEstimated, 1);
  assert.equal(m.productCosts, 15.5);     // 23 x 0.50 + 4 x 1.00
  assert.equal(m.fixedCosts, 10);
  assert.equal(m.costs, 41.96);
  assert.equal(m.profit, 34.94);
  assert.equal(m.margin, 45.44);
  assert.equal(m.roi, 83.27);
  assert.equal(m.aov, 21.71);
  assert.equal(m.customers, 3);
  assert.equal(m.returningCustomers, 2);  // a@ ordered twice, b@ ordered in August
  assert.equal(m.repeatRate, 66.67);
});

test('October: the partial refund of a September order lands in October', () => {
  const m = R.monthMetrics(ORDERS, SETTINGS, '2026-10');
  assert.equal(m.orders, 1);
  assert.equal(m.magnets, 50);
  assert.equal(m.grossSales, 95);
  assert.equal(m.discounts, 24);          // 19 volume + 5 promo
  assert.equal(m.refunds, 10);
  assert.equal(m.netSales, 61);
  assert.equal(m.productCosts, 26);
  assert.equal(m.costs, 38.36);
  assert.equal(m.profit, 22.64);
  assert.equal(m.margin, 37.11);
  assert.equal(m.roi, 59.02);
  assert.equal(m.aov, 71);
  assert.equal(m.repeatRate, 0);
});

test('monthly() returns 12 months oldest first and totals add up', () => {
  const rows = R.monthly(ORDERS, SETTINGS, '2026-10', 12);
  assert.equal(rows.length, 12);
  assert.equal(rows[0].key, '2025-11');
  assert.equal(rows[11].key, '2026-10');
  const aug = rows.find((r) => r.key === '2026-08');
  assert.equal(aug.orders, 1);
  assert.equal(aug.profit, R.round2(9.95 - (0.59 + 4.5 + 0.5 + 1 + 10)));
  const empty = rows[0];
  assert.equal(empty.orders, 0);
  assert.equal(empty.profit, 0);          // before the first sale: no fixed costs yet
  assert.equal(empty.margin, null);
  assert.equal(rows.find((r) => r.key === '2026-07').fixedCosts, 0);
  assert.equal(rows.find((r) => r.key === '2026-08').fixedCosts, 10);
  const t = R.totalsOf(rows);
  assert.equal(t.orders, 6);
  assert.equal(t.fixedCosts, 30);         // August, September, October
  const year = R.summarize(ORDERS, SETTINGS, { from: R.monthRange('2025-11').from, to: R.monthRange('2026-10').to }, { months: 12 });
  assert.equal(year.fixedCosts, 30);
  assert.equal(t.refunds, 19.95);
  assert.equal(t.netSales, R.round2(rows.reduce((a, r) => a + r.netSales, 0)));
});

test('refunds by reason', () => {
  const sep = R.refundsByReason(ORDERS, R.monthRange('2026-09'));
  assert.deepEqual(sep, [{ reason: 'changed_mind', label: 'Changed their mind', count: 1, amount: 9.95 }]);
  const both = R.refundsByReason(ORDERS, { from: R.monthRange('2026-09').from, to: R.monthRange('2026-10').to });
  assert.deepEqual(both.map((r) => r.reason), ['damaged', 'changed_mind']);
});

test('top designs and collections', () => {
  const top = R.topItems(ORDERS, R.monthRange('2026-09'));
  assert.deepEqual(top.designs.map((d) => [d.key, d.qty, d.revenue]),
    [['places/new-york', 3, 15], ['christmas/believe', 2, 10], ['halloween/boo', 1, 5], ['fall/cozy-season', 1, 5]]);
  assert.deepEqual(top.collections.map((c) => [c.key, c.qty]),
    [['_photos', 16], ['places', 3], ['christmas', 2], ['fall', 1], ['halloween', 1]]);
});

test('stages and tabs', () => {
  const by = Object.fromEntries(ORDERS.map((o) => [o.id, o]));
  assert.equal(R.stage(by.A), 'delivered');
  assert.equal(R.stage(by.B), 'shipped');         // partly refunded but already shipped
  assert.equal(R.stage(by.C), 'refunded');
  assert.equal(R.stage(by.E), 'to_fulfil');
  assert.equal(R.stage({ status: 'partially_refunded', timeline: [{ status: 'in_production' }] }), 'in_production');
  const now = at(2026, 10, 5);
  assert.deepEqual(ORDERS.filter((o) => R.matchesTab(o, 'refunded', now)).map((o) => o.id), ['B', 'C']);
  assert.deepEqual(ORDERS.filter((o) => R.matchesTab(o, 'abandoned', now)).map((o) => o.id), ['D']);
  assert.equal(R.isAbandoned({ status: 'pending', createdAt: now - 30 * 60 * 1000 }, now), false);
  assert.equal(R.refundable(by.B), 30);
  assert.equal(R.refundable(by.C), 0);
});

test('refunds made in Stripe that only show in refundedTotal still count', () => {
  const o = { status: 'partially_refunded', paidAt: at(2026, 9, 1), pricing: { total: 20 }, refunds: [{ amount: 5, reason: 'late', at: at(2026, 9, 2) }], refundedTotal: 8 };
  assert.equal(R.refundedTotal(o), 8);
  assert.equal(R.refundsOf(o).length, 2);
  assert.equal(R.refundable(o), 12);
});

test('home: today, 7 days, 30 days, to fulfil, refunds this month, daily chart', () => {
  const h = R.home(ORDERS, at(2026, 10, 5, 12));
  assert.deepEqual(h.today, { total: 0, orders: 0 });
  assert.deepEqual(h.week, { total: 71, orders: 1 });
  assert.deepEqual(h.month30, { total: 135.9, orders: 4 });
  assert.equal(h.toFulfil, 1);
  assert.equal(h.refundsThisMonth.total, 10);
  assert.equal(h.daily.length, 30);
  assert.equal(R.round2(h.daily.reduce((a, d) => a + d.total, 0)), 135.9);
});

test('customers aggregate by email (case-insensitive) and subtract refunds', () => {
  const list = R.customers(ORDERS);
  const a = list.find((c) => c.key === 'a@x.com');
  const b = list.find((c) => c.key === 'b@x.com');
  assert.equal(a.orders, 2); assert.equal(a.spent, 21.95); assert.equal(a.repeat, true);
  assert.equal(b.orders, 2); assert.equal(b.spent, 39.95); assert.equal(b.lastNumber, 'LHH-1002');
  assert.equal(list.length, 4);
});

test('failed refunds do not count; payment links are not abandoned checkouts', () => {
  const o = { status: 'partially_refunded', paidAt: at(2026, 9, 1), pricing: { total: 30 }, refundedTotal: 5,
    refunds: [{ id: 'r1', amount: 5, reason: 'late', at: at(2026, 9, 2), status: 'succeeded' }, { id: 'r2', amount: 9, reason: 'other', at: at(2026, 9, 3), status: 'failed' }] };
  assert.equal(R.refundedTotal(o), 5);
  assert.equal(R.refundable(o), 25);
  const now = at(2026, 10, 5);
  assert.equal(R.isAbandoned({ status: 'pending', source: 'payment_link', createdAt: at(2026, 10, 1), items: [{ kind: 'custom', title: 'Quote', amount: 90 }] }, now), false);
  assert.equal(R.isAbandoned({ status: 'pending', createdAt: new Date(at(2026, 10, 1)).toISOString(), items: [] }, now), true);
});

test('timestamps in every shape', () => {
  const ms = at(2026, 1, 2);
  assert.equal(R.toMs(ms), ms);
  assert.equal(R.toMs(ms / 1000), ms);
  assert.equal(R.toMs({ seconds: ms / 1000, nanoseconds: 0 }), ms);
  assert.equal(R.toMs(new Date(ms).toISOString()), ms);
  assert.equal(R.toMs(ts(ms)), ms);
  assert.equal(R.toMs(null), 0);
});

test('CSV quoting and formula guard', () => {
  const csv = R.toCSV([{ a: 'x, "y"', b: '=SUM(A1)', c: -5 }], [['A', 'a'], ['B', 'b'], ['C', 'c']]);
  assert.equal(csv, 'A,B,C\r\n"x, ""y""",\'=SUM(A1),-5\r\n');
});
