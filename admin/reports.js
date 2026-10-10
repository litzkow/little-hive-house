/* Little Hive House admin: the numbers. Pure functions only (no DOM, no Firebase) so they can be tested with
   `node --test admin/tests/`. Every money value is in US dollars (numbers like 24.95), like the orders.

   How the reports count things (written for the owners):
   - A sale is any order that was paid: paid, in production, shipped, delivered, refunded or partly refunded
     (and canceled orders that had been paid). "Checkout started" orders that were never paid are not sales.
   - An order belongs to the month it was paid. A refund belongs to the month the money went back, so a
     September order refunded in October lowers October.
   - Gross sales = the price of everything sold, before discounts and shipping.
   - Net sales = what customers paid (gross - discounts + shipping charged) minus refunds.
   - Stripe fees: the real fee saved on the order when Stripe sent it, otherwise an estimate
     (total x Stripe % + fixed fee from Settings).
   - Shipping labels: the label cost typed when shipping, or the default label cost for shipped orders without one.
   - Product costs: magnet cost x magnets + packaging cost per order.
   - Profit = net sales - (Stripe fees + labels + product costs + monthly fixed costs).
   - Margin = profit / net sales. ROI = profit / costs. */
(function (root, factory) {
  var api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.LHHReports = api;
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  var DEFAULT_SETTINGS = { magnetUnitCost: 0.55, packagingCost: 0.60, defaultLabelCost: 4.50, stripePct: 2.9, stripeFixed: 0.30, monthlyFixedCosts: 0 };
  var SALE_STATUSES = ['paid', 'in_production', 'shipped', 'delivered', 'refunded', 'partially_refunded'];
  var REASONS = [
    ['not_delivered', 'Never arrived'],
    ['damaged', 'Arrived damaged'],
    ['wrong_item', 'Wrong item sent'],
    ['print_quality', 'Print quality issue'],
    ['late', 'Arrived too late'],
    ['changed_mind', 'Changed their mind'],
    ['duplicate', 'Duplicate order'],
    ['other', 'Other']
  ];
  var REASON_LABEL = {};
  REASONS.forEach(function (r) { REASON_LABEL[r[0]] = r[1]; });
  var HOUR = 3600 * 1000, DAY = 24 * HOUR;

  /* ---------- small helpers ---------- */
  function num(v) { v = Number(v); return isFinite(v) ? v : 0; }
  function round2(v) { return Math.round((v + Number.EPSILON) * 100) / 100; }
  /* Firestore Timestamp, {seconds}, Date, ISO string, ms or s number -> milliseconds (or 0) */
  function toMs(v) {
    if (v == null || v === '') return 0;
    if (typeof v === 'number') return v > 1e11 ? v : v * 1000;
    if (v instanceof Date) return v.getTime();
    if (typeof v.toMillis === 'function') return v.toMillis();
    if (typeof v.toDate === 'function') return v.toDate().getTime();
    if (typeof v.seconds === 'number') return v.seconds * 1000 + Math.round(num(v.nanoseconds) / 1e6);
    if (typeof v._seconds === 'number') return v._seconds * 1000;
    if (typeof v === 'string') { var t = Date.parse(v); return isNaN(t) ? 0 : t; }
    return 0;
  }
  function settingsWithDefaults(s) {
    var out = {};
    for (var k in DEFAULT_SETTINGS) out[k] = (s && s[k] != null && s[k] !== '' && isFinite(Number(s[k]))) ? Number(s[k]) : DEFAULT_SETTINGS[k];
    return out;
  }
  function monthKey(ms) { var d = new Date(ms); return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0'); }
  function monthRange(key) {
    var p = key.split('-'), y = Number(p[0]), m = Number(p[1]) - 1;
    return { from: new Date(y, m, 1).getTime(), to: new Date(y, m + 1, 1).getTime() };
  }
  function shiftMonth(key, n) {
    var p = key.split('-'), d = new Date(Number(p[0]), Number(p[1]) - 1 + n, 1);
    return monthKey(d.getTime());
  }
  function monthLabel(key, long) {
    var p = key.split('-'), d = new Date(Number(p[0]), Number(p[1]) - 1, 1);
    return d.toLocaleString('en-US', long ? { month: 'long', year: 'numeric' } : { month: 'short', year: '2-digit' }).replace(' ', long ? ' ' : " '");
  }
  function monthsBetween(from, to) {   /* calendar months touched by [from, to) */
    var a = new Date(from), b = new Date(to - 1);
    return (b.getFullYear() - a.getFullYear()) * 12 + b.getMonth() - a.getMonth() + 1;
  }
  function startOfDay(ms) { var d = new Date(ms); d.setHours(0, 0, 0, 0); return d.getTime(); }

  /* ---------- one order ---------- */
  function orderDate(o) { return toMs(o.paidAt) || toMs(o.createdAt); }
  function isSale(o) {
    if (!o) return false;
    if (SALE_STATUSES.indexOf(o.status) >= 0) return true;
    return o.status === 'canceled' && !!toMs(o.paidAt);
  }
  function isPaymentLink(o) { return o.source === 'payment_link' || (o.items || []).some(function (it) { return it.kind === 'custom'; }); }
  /* a checkout started more than an hour ago and never paid (payment links you sent are not "abandoned") */
  function isAbandoned(o, now) {
    return o.status === 'pending' && !isPaymentLink(o) && toMs(o.createdAt) > 0 && (now || Date.now()) - toMs(o.createdAt) > HOUR;
  }
  function qtyOf(it) { return it.qty == null ? 1 : num(it.qty); }
  function itemMagnets(it) {
    if (it.kind === 'design') return qtyOf(it);
    if (it.kind === 'photos') return num(it.packSize) * qtyOf(it);
    if (it.kind === 'package') return num(it.size) * qtyOf(it);
    return num(it.magnets) * qtyOf(it);   /* custom quotes: only if the quote says how many */
  }
  function itemPrice(it) {
    if (it.kind === 'design') return num(it.unit) * qtyOf(it);
    if (it.kind === 'photos' || it.kind === 'package') return num(it.price) * qtyOf(it);
    if (it.kind === 'custom') return num(it.amount);
    return num(it.price || it.amount) * qtyOf(it);
  }
  function magnetsOf(o) { return (o.items || []).reduce(function (a, it) { return a + itemMagnets(it); }, 0); }
  function pricing(o) {
    var p = o.pricing || {};
    var subtotal = p.subtotal != null ? num(p.subtotal) : (o.items || []).reduce(function (a, it) { return a + itemPrice(it); }, 0);
    var promo = p.promo && p.promo.amount ? num(p.promo.amount) : 0;
    var discounts = num(p.bundleDiscount) + num(p.volumeDiscount) + promo;
    var shipping = num(p.shipping);
    var total = p.total != null ? num(p.total) : round2(subtotal - discounts + shipping);
    return { subtotal: subtotal, discounts: discounts, promo: promo, shipping: shipping, total: total };
  }
  function refundsOf(o) {
    /* failed or canceled Stripe refunds never reached the customer */
    var list = Array.isArray(o.refunds) ? o.refunds.filter(function (r) { return r && num(r.amount) > 0 && (!r.status || r.status === 'succeeded' || r.status === 'pending'); }) : [];
    var listed = list.reduce(function (a, r) { return a + num(r.amount); }, 0);
    var total = num(o.refundedTotal);
    var out = list.map(function (r) { return { amount: num(r.amount), reason: r.reason || 'other', note: r.note || '', at: toMs(r.at) || orderDate(o), by: r.by || '' }; });
    /* refunds made in the Stripe dashboard may only show up in refundedTotal */
    if (total - listed > 0.004) out.push({ amount: round2(total - listed), reason: 'other', note: '', at: toMs(o.updatedAt) || orderDate(o), by: 'stripe' });
    return out;
  }
  function refundedTotal(o) { return round2(refundsOf(o).reduce(function (a, r) { return a + r.amount; }, 0)); }
  function refundable(o) { return Math.max(0, round2(pricing(o).total - refundedTotal(o))); }
  function stripeFee(o, s) {
    var f = o.stripe && o.stripe.fee;
    if (f != null && f !== '' && isFinite(Number(f))) return { amount: num(f), estimated: false };
    s = settingsWithDefaults(s);
    var t = pricing(o).total;
    return { amount: t > 0 ? round2(t * s.stripePct / 100 + s.stripeFixed) : 0, estimated: true };
  }
  function wasShipped(o) {
    var f = o.fulfillment || {};
    return !!(toMs(f.shippedAt) || f.tracking || o.status === 'shipped' || o.status === 'delivered' || toMs(f.deliveredAt));
  }
  function labelCost(o, s) {
    var f = o.fulfillment || {};
    if (f.labelCost != null && f.labelCost !== '' && isFinite(Number(f.labelCost))) return { amount: num(f.labelCost), estimated: false };
    if (wasShipped(o)) return { amount: settingsWithDefaults(s).defaultLabelCost, estimated: true };
    return { amount: 0, estimated: false };
  }
  function hadStatus(o, st) { return (o.timeline || []).some(function (t) { return t && t.status === st; }); }
  /* Where the order is in the work: to_fulfil, in_production, shipped, delivered, refunded, canceled, pending */
  function stage(o) {
    var f = o.fulfillment || {};
    if (o.status === 'pending') return 'pending';
    if (o.status === 'canceled') return 'canceled';
    if (o.status === 'refunded') return 'refunded';
    if (o.status === 'delivered' || toMs(f.deliveredAt)) return 'delivered';
    if (o.status === 'shipped' || toMs(f.shippedAt) || f.tracking) return 'shipped';
    if (o.status === 'in_production' || (o.status === 'partially_refunded' && hadStatus(o, 'in_production'))) return 'in_production';
    return 'to_fulfil';
  }
  function matchesTab(o, tab, now) {
    var st = stage(o);
    switch (tab) {
      case 'to_fulfil': return st === 'to_fulfil';
      case 'in_production': return st === 'in_production';
      case 'shipped': return st === 'shipped';
      case 'delivered': return st === 'delivered';
      case 'refunded': return isSale(o) && refundedTotal(o) > 0;
      case 'abandoned': return isAbandoned(o, now);
      case 'all': return o.status !== 'pending';
      default: return true;
    }
  }
  function customerKey(o) { return String(o.email || (o.shipping && o.shipping.name) || o.uid || '').trim().toLowerCase(); }

  /* ---------- a period ---------- */
  function emptyMetrics() {
    return { orders: 0, magnets: 0, grossSales: 0, discounts: 0, shippingCharged: 0, refunds: 0, refundCount: 0, netSales: 0,
             stripeFees: 0, feesEstimated: 0, labels: 0, labelsEstimated: 0, productCosts: 0, fixedCosts: 0, costs: 0,
             profit: 0, margin: null, roi: null, aov: 0, customers: 0, returningCustomers: 0, repeatRate: null, totalCollected: 0 };
  }
  /* range = {from, to} in ms (to exclusive); opts.months = how many months of fixed costs to count (default 1) */
  function summarize(orders, settings, range, opts) {
    var s = settingsWithDefaults(settings);
    opts = opts || {};
    var m = emptyMetrics();
    var inRange = function (t) { return t >= range.from && t < range.to; };
    var sales = (orders || []).filter(isSale);
    var firstSeen = {};   /* customer -> earliest sale date ever */
    sales.forEach(function (o) {
      var k = customerKey(o), t = orderDate(o);
      if (k && (!firstSeen[k] || t < firstSeen[k])) firstSeen[k] = t;
    });
    var perCustomer = {};
    sales.forEach(function (o) {
      var t = orderDate(o);
      if (inRange(t)) {
        var p = pricing(o), fee = stripeFee(o, s), lab = labelCost(o, s), mags = magnetsOf(o);
        m.orders += 1;
        m.magnets += mags;
        m.grossSales += p.subtotal;
        m.discounts += p.discounts;
        m.shippingCharged += p.shipping;
        m.totalCollected += p.total;
        m.stripeFees += fee.amount;
        if (fee.estimated && fee.amount) m.feesEstimated += 1;
        m.labels += lab.amount;
        if (lab.estimated) m.labelsEstimated += 1;
        m.productCosts += mags * s.magnetUnitCost + s.packagingCost;
        var k = customerKey(o);
        if (k) perCustomer[k] = (perCustomer[k] || 0) + 1;
      }
      refundsOf(o).forEach(function (r) { if (inRange(r.at)) { m.refunds += r.amount; m.refundCount += 1; } });
    });
    Object.keys(perCustomer).forEach(function (k) {
      m.customers += 1;
      if (perCustomer[k] > 1 || firstSeen[k] < range.from) m.returningCustomers += 1;
    });
    /* fixed costs count from the shop's first sale on, so months before opening don't show a loss */
    var first = sales.reduce(function (a, o) { var t = orderDate(o); return t && (!a || t < a) ? t : a; }, 0);
    var months = opts.months == null ? 1 : opts.months;
    if (!first || range.to <= first) months = 0;
    else if (first > range.from) months = Math.max(1, Math.min(months, monthsBetween(first, range.to)));
    m.fixedCosts = s.monthlyFixedCosts * months;
    ['grossSales', 'discounts', 'shippingCharged', 'refunds', 'stripeFees', 'labels', 'productCosts', 'fixedCosts', 'totalCollected'].forEach(function (k) { m[k] = round2(m[k]); });
    m.netSales = round2(m.grossSales - m.discounts + m.shippingCharged - m.refunds);
    m.costs = round2(m.stripeFees + m.labels + m.productCosts + m.fixedCosts);
    m.profit = round2(m.netSales - m.costs);
    m.margin = m.netSales > 0 ? round2(m.profit / m.netSales * 100) : null;
    m.roi = m.costs > 0 ? round2(m.profit / m.costs * 100) : null;
    m.aov = m.orders ? round2(m.totalCollected / m.orders) : 0;
    m.repeatRate = m.customers ? round2(m.returningCustomers / m.customers * 100) : null;
    return m;
  }
  function monthMetrics(orders, settings, key) {
    var m = summarize(orders, settings, monthRange(key));
    m.key = key;
    m.label = monthLabel(key);
    return m;
  }
  /* the n months ending with endKey, oldest first */
  function monthly(orders, settings, endKey, n) {
    n = n || 12;
    var out = [];
    for (var i = n - 1; i >= 0; i--) out.push(monthMetrics(orders, settings, shiftMonth(endKey, -i)));
    return out;
  }
  function totalsOf(rows) {
    var t = emptyMetrics();
    ['orders', 'magnets', 'grossSales', 'discounts', 'shippingCharged', 'refunds', 'refundCount', 'stripeFees', 'feesEstimated', 'labels',
     'labelsEstimated', 'productCosts', 'fixedCosts', 'totalCollected'].forEach(function (k) {
      t[k] = round2(rows.reduce(function (a, r) { return a + num(r[k]); }, 0));
    });
    t.netSales = round2(t.grossSales - t.discounts + t.shippingCharged - t.refunds);
    t.costs = round2(t.stripeFees + t.labels + t.productCosts + t.fixedCosts);
    t.profit = round2(t.netSales - t.costs);
    t.margin = t.netSales > 0 ? round2(t.profit / t.netSales * 100) : null;
    t.roi = t.costs > 0 ? round2(t.profit / t.costs * 100) : null;
    t.aov = t.orders ? round2(t.totalCollected / t.orders) : 0;
    return t;
  }

  function refundsByReason(orders, range) {
    var by = {};
    (orders || []).filter(isSale).forEach(function (o) {
      refundsOf(o).forEach(function (r) {
        if (r.at < range.from || r.at >= range.to) return;
        var k = REASON_LABEL[r.reason] ? r.reason : 'other';
        by[k] = by[k] || { reason: k, label: REASON_LABEL[k], count: 0, amount: 0 };
        by[k].count += 1;
        by[k].amount = round2(by[k].amount + r.amount);
      });
    });
    return Object.keys(by).map(function (k) { return by[k]; }).sort(function (a, b) { return b.amount - a.amount || b.count - a.count; });
  }

  function collectionOf(it) {
    if (it.id && String(it.id).indexOf('/') > 0) return String(it.id).split('/')[0];
    return it.collection || 'other';
  }
  function topItems(orders, range, n) {
    n = n || 10;
    var designs = {}, cols = {};
    var add = function (map, key, title, extra, qty, revenue) {
      var r = map[key] || (map[key] = Object.assign({ key: key, title: title, qty: 0, revenue: 0, orders: 0 }, extra));
      r.qty += qty; r.revenue = round2(r.revenue + revenue); r.orders += 1;
    };
    (orders || []).filter(isSale).forEach(function (o) {
      var t = orderDate(o);
      if (t < range.from || t >= range.to) return;
      (o.items || []).forEach(function (it) {
        if (it.kind === 'design') {
          var c = collectionOf(it);
          add(designs, it.id || it.title, it.title || it.id, { collection: c, id: it.id }, qtyOf(it), itemPrice(it));
          add(cols, c, it.collection || c, {}, qtyOf(it), itemPrice(it));
        } else if (it.kind === 'photos') {
          add(cols, '_photos', 'Photo magnets', { special: true }, itemMagnets(it), itemPrice(it));
        } else if (it.kind === 'package') {
          add(cols, '_packages', 'Big-order packages', { special: true }, itemMagnets(it), itemPrice(it));
        } else if (it.kind === 'custom') {
          add(cols, '_custom', 'Custom quotes', { special: true }, itemMagnets(it), itemPrice(it));
        }
      });
    });
    var sort = function (a, b) { return b.qty - a.qty || b.revenue - a.revenue || String(a.title).localeCompare(String(b.title)); };
    var list = function (m) { return Object.keys(m).map(function (k) { return m[k]; }).sort(sort).slice(0, n); };
    return { designs: list(designs), collections: list(cols) };
  }

  /* ---------- home ---------- */
  function salesBetween(orders, from, to) {
    var r = { total: 0, orders: 0 };
    (orders || []).filter(isSale).forEach(function (o) {
      var t = orderDate(o);
      if (t >= from && t < to) { r.total += pricing(o).total; r.orders += 1; }
    });
    r.total = round2(r.total);
    return r;
  }
  function refundsBetween(orders, from, to) {
    var r = { total: 0, count: 0 };
    (orders || []).filter(isSale).forEach(function (o) {
      refundsOf(o).forEach(function (x) { if (x.at >= from && x.at < to) { r.total += x.amount; r.count += 1; } });
    });
    r.total = round2(r.total);
    return r;
  }
  /* sales per day for the `days` days ending today (oldest first) */
  function dailySales(orders, now, days) {
    var end = startOfDay(now) + DAY, out = [];
    for (var i = days - 1; i >= 0; i--) {
      var from = new Date(startOfDay(now)); from.setDate(from.getDate() - i);
      var f = from.getTime(), to = new Date(f); to.setDate(to.getDate() + 1);
      var s = salesBetween(orders, f, Math.min(to.getTime(), end));
      out.push({ day: f, total: s.total, orders: s.orders });
    }
    return out;
  }
  function home(orders, now) {
    now = now || Date.now();
    var today = startOfDay(now);
    var d7 = new Date(today); d7.setDate(d7.getDate() - 6);
    var d30 = new Date(today); d30.setDate(d30.getDate() - 29);
    var end = now + 1;
    var stages = { to_fulfil: 0, in_production: 0 };
    (orders || []).forEach(function (o) { var st = stage(o); if (st in stages) stages[st] += 1; });
    var mk = monthRange(monthKey(now));
    return {
      today: salesBetween(orders, today, end),
      week: salesBetween(orders, d7.getTime(), end),
      month30: salesBetween(orders, d30.getTime(), end),
      toFulfil: stages.to_fulfil + stages.in_production,
      newToFulfil: stages.to_fulfil,
      inProduction: stages.in_production,
      refundsThisMonth: refundsBetween(orders, mk.from, mk.to),
      daily: dailySales(orders, now, 30)
    };
  }

  /* ---------- customers ---------- */
  function customers(orders) {
    var by = {};
    (orders || []).filter(isSale).forEach(function (o) {
      var k = customerKey(o); if (!k) return;
      var c = by[k] || (by[k] = { key: k, email: o.email || '', name: '', orders: 0, spent: 0, refunded: 0, first: 0, last: 0, lastOrderId: '', lastNumber: '', city: '' });
      var t = orderDate(o);
      c.orders += 1;
      c.spent = round2(c.spent + pricing(o).total - refundedTotal(o));
      c.refunded = round2(c.refunded + refundedTotal(o));
      if (!c.first || t < c.first) c.first = t;
      if (t >= c.last) {
        c.last = t; c.lastOrderId = o.id || ''; c.lastNumber = o.number || '';
        c.name = o.name || (o.shipping && o.shipping.name) || c.name;
        var a = o.shipping && o.shipping.address;
        if (a) c.city = [a.city, a.state].filter(Boolean).join(', ');
      }
    });
    return Object.keys(by).map(function (k) { var c = by[k]; c.repeat = c.orders > 1; return c; })
      .sort(function (a, b) { return b.last - a.last; });
  }

  /* ---------- CSV ---------- */
  function csvCell(v) {
    if (v == null) return '';
    var s = String(v);
    if (/^[=+\-@\t\r]/.test(s) && !/^-?\d+(\.\d+)?$/.test(s)) s = "'" + s;   /* keep spreadsheets from running formulas */
    return /[",\n\r]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
  }
  function toCSV(rows, columns) {
    var head = columns.map(function (c) { return csvCell(c[0]); }).join(',');
    var body = rows.map(function (r) { return columns.map(function (c) { return csvCell(typeof c[1] === 'function' ? c[1](r) : r[c[1]]); }).join(','); });
    return [head].concat(body).join('\r\n') + '\r\n';
  }

  return {
    DEFAULT_SETTINGS: DEFAULT_SETTINGS, REASONS: REASONS, REASON_LABEL: REASON_LABEL, HOUR: HOUR, DAY: DAY,
    num: num, round2: round2, toMs: toMs, settingsWithDefaults: settingsWithDefaults,
    monthKey: monthKey, monthRange: monthRange, shiftMonth: shiftMonth, monthLabel: monthLabel, startOfDay: startOfDay,
    orderDate: orderDate, isSale: isSale, isAbandoned: isAbandoned, isPaymentLink: isPaymentLink, itemMagnets: itemMagnets, itemPrice: itemPrice, magnetsOf: magnetsOf,
    pricing: pricing, refundsOf: refundsOf, refundedTotal: refundedTotal, refundable: refundable, stripeFee: stripeFee, labelCost: labelCost,
    wasShipped: wasShipped, stage: stage, matchesTab: matchesTab, customerKey: customerKey, collectionOf: collectionOf,
    summarize: summarize, monthMetrics: monthMetrics, monthly: monthly, totalsOf: totalsOf, refundsByReason: refundsByReason, topItems: topItems,
    salesBetween: salesBetween, refundsBetween: refundsBetween, dailySales: dailySales, home: home, customers: customers,
    csvCell: csvCell, toCSV: toCSV
  };
});
