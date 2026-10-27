/* Little Hive House admin: Reports, Customers, Discounts, Payment links, Reviews, Messages, Subscribers, Settings. */
(function () {
  'use strict';
  var A = window.LHHAdmin, S = A.S, R = A.R, h = A.h, ACT = A.ACT, V = A.VIEWS;
  var esc = h.esc, money = h.money, icon = h.icon;
  function $(sel) { return document.querySelector(sel); }
  function head(eyebrow, title, sub, actions) {
    return '<div class="page-head"><div><p class="eyebrow">' + esc(eyebrow) + '</p><h1>' + esc(title) + '</h1>' + (sub ? '<p class="sub">' + sub + '</p>' : '') + '</div>' +
      (actions ? '<div class="actions">' + actions + '</div>' : '') + '</div>';
  }
  function loading(text) { return '<div class="loading"><svg class="spin" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3a9 9 0 1 0 9 9" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/></svg><span>' + esc(text || 'Loading…') + '</span></div>'; }
  /* load a collection once, then re-render the current view */
  function need(key, collection) {
    if (S[key]) return true;
    if (!need.pending[key]) {
      need.pending[key] = h.loadCol(collection || key, key).then(function () { need.pending[key] = null; h.updateBadges(); h.route(); })
        .catch(function (e) { need.pending[key] = null; S[key] = []; S[key + 'Error'] = h.friendlyError(e); h.route(); });
    }
    return false;
  }
  need.pending = {};
  function errBox(key) { return S[key + 'Error'] ? '<p class="err" style="margin-bottom:14px">Couldn’t load this list: ' + esc(S[key + 'Error']) + '</p>' : ''; }

  /* ====================================================================== REPORTS */
  function monthOptions() {
    var now = R.monthKey(Date.now()), first = now;
    S.orders.forEach(function (o) { if (R.isSale(o)) { var k = R.monthKey(R.orderDate(o)); if (k < first) first = k; } });
    var list = [], k = now;
    for (var i = 0; i < 60 && (k >= first || i < 12); i++) { list.push(k); k = R.shiftMonth(k, -1); }
    return list;
  }
  var REPORT_COLS = [
    ['Orders', 'orders', 'int'], ['Magnets sold', 'magnets', 'int'], ['Gross sales', 'grossSales', 'money'], ['Discounts', 'discounts', 'money'],
    ['Shipping charged', 'shippingCharged', 'money'], ['Refunds', 'refunds', 'money'], ['Net sales', 'netSales', 'money'], ['Stripe fees', 'stripeFees', 'money'],
    ['Shipping labels', 'labels', 'money'], ['Product costs', 'productCosts', 'money'], ['Fixed costs', 'fixedCosts', 'money'], ['Total costs', 'costs', 'money'],
    ['Profit', 'profit', 'money'], ['Margin', 'margin', 'pct'], ['ROI', 'roi', 'pct'], ['Avg order', 'aov', 'money'], ['Repeat customers', 'repeatRate', 'pct'],
    ['Stripe Tax fees', 'stripeTaxFees', 'money'], ['Income tax reserve', 'incomeTaxReserve', 'money'], ['Profit after tax reserve', 'profitAfterTax', 'money'],
    ['Sales tax collected', 'salesTax', 'money'], ['Sales tax refunded', 'taxRefunded', 'money'], ['Sales tax owed', 'taxOwed', 'money']
  ];
  function fmtCell(v, kind) { return kind === 'int' ? h.int(v) : kind === 'pct' ? h.pct(v) : h.signedMoney(v); }
  V.reports = function (r) {
    var u = S.ui.reports, months = monthOptions();
    if (r.q.get('month')) u.month = r.q.get('month');
    if (!u.month || months.indexOf(u.month) < 0) u.month = months[0];
    var rows = R.monthly(S.orders, S.settings, u.month, 12);
    var range = u.scope === 'year' ? { from: R.monthRange(R.shiftMonth(u.month, -11)).from, to: R.monthRange(u.month).to } : R.monthRange(u.month);
    var m = u.scope === 'year' ? R.totalsOf(rows) : rows[rows.length - 1];
    if (u.scope === 'year') {   /* repeat rate needs the real customer list, not a sum */
      var yr = R.summarize(S.orders, S.settings, range, { months: 12 });
      m.customers = yr.customers; m.returningCustomers = yr.returningCustomers; m.repeatRate = yr.repeatRate;
    }
    var prev = u.scope === 'month' ? R.monthMetrics(S.orders, S.settings, R.shiftMonth(u.month, -1)) : null;
    var period = u.scope === 'year' ? R.monthLabel(R.shiftMonth(u.month, -11), true) + ' – ' + R.monthLabel(u.month, true) : R.monthLabel(u.month, true);
    var reasons = R.refundsByReason(S.orders, range);
    var top = R.topItems(S.orders, range, 10);
    var delta = function (cur, before, goodUp) {
      if (!prev || before == null) return '';
      var d = cur - before; if (Math.abs(d) < 0.005) return 'Same as last month';
      var up = d > 0, good = goodUp ? up : !up;
      return '<span class="' + (good ? 'pos' : 'neg') + '">' + (up ? '▲ ' : '▼ ') + h.moneyShort(Math.abs(d)).replace('−', '') + '</span> vs last month';
    };
    var estNote = m.feesEstimated || m.labelsEstimated ? '<div class="callout calm">' + icon('info') + '<p class="small">' +
      (m.feesEstimated ? h.plural(m.feesEstimated, 'order') + ' had no Stripe fee saved, so the fee is estimated (' + S.settings.stripePct + '% + ' + money(S.settings.stripeFixed) + '). ' : '') +
      (m.labelsEstimated ? h.plural(m.labelsEstimated, 'shipped order') + ' had no label cost, so ' + money(S.settings.defaultLabelCost) + ' each is used. ' : '') +
      'Change these in <a href="#settings">Settings</a>.</p></div>' : '';
    var pl = [
      ['Gross sales', m.grossSales, 'Price of everything sold, before discounts'],
      ['Discounts', -m.discounts, 'Bundles, volume discounts and codes'],
      ['Shipping charged', m.shippingCharged, 'What customers paid for shipping'],
      ['Refunds', -m.refunds, h.plural(m.refundCount, 'refund') + ' paid back in this period'],
      ['Net sales', m.netSales, 'What you really took in', 'sum'],
      ['Stripe fees', -m.stripeFees, m.feesEstimated ? 'Some estimated' : 'From Stripe'],
      ['Stripe Tax fees', -m.stripeTaxFees, S.settings.stripeTaxPct + '% of orders with sales tax (estimate)'],
      ['Shipping labels', -m.labels, ''],
      ['Product costs', -m.productCosts, h.int(m.magnets) + ' magnets × ' + money(S.settings.magnetUnitCost) + ' + ' + money(S.settings.packagingCost) + ' packaging per order'],
      ['Fixed costs', -m.fixedCosts, money(S.settings.monthlyFixedCosts) + ' a month'],
      ['Profit', m.profit, (m.margin == null ? '' : h.pct(m.margin) + ' margin') + (m.roi == null ? '' : ' · ' + h.pct(m.roi) + ' return on costs'), 'sum big'],
      ['Set aside for income tax', -m.incomeTaxReserve, m.incomeTaxPct + '% of profit (change it in Settings)'],
      ['Yours to keep', m.profitAfterTax, 'Profit after the income tax reserve', 'sum']
    ];
    var states = Object.keys(m.taxByState || {}).filter(function (k) { return Math.abs(m.taxByState[k]) >= 0.005; })
      .sort(function (a, b) { return m.taxByState[b] - m.taxByState[a]; });
    var taxCard = '<section class="card gap-top"><div class="card-head"><div><h2>Sales tax · not your money</h2><p class="sub">' + esc(period) +
      ' · kept apart from sales and profit</p></div></div><table class="pl">' +
      '<tr><td>Collected from customers<span class="why">Added on top of prices at checkout</span></td><td>' + money(m.salesTax) + '</td></tr>' +
      '<tr><td>Given back in refunds<span class="why">The tax part of refunds</span></td><td>' + h.signedMoney(-m.taxRefunded) + '</td></tr>' +
      '<tr class="sum big"><td>Owed to the state<span class="why">Pay this when you file sales tax</span></td><td>' + money(m.taxOwed) + '</td></tr>' +
      states.map(function (k) { return '<tr><td>' + esc(k === '?' ? 'Unknown state' : k) + '</td><td>' + money(m.taxByState[k]) + '</td></tr>'; }).join('') +
      '</table>' + (m.salesTax ? '' : '<p class="small muted" style="margin-top:10px">No sales tax collected in this period.</p>') + '</section>';
    var topReason = reasons[0];
    var html = head('Reports', 'Reports', esc(period),
      '<label><span class="sr">Month</span><select class="input" id="r-month" style="width:auto">' + months.map(function (k) {
        return '<option value="' + k + '"' + (k === u.month ? ' selected' : '') + '>' + esc(R.monthLabel(k, true)) + '</option>';
      }).join('') + '</select></label>' +
      '<div class="seg" role="group" aria-label="Period"><button type="button" data-act="rscope" data-scope="month" aria-pressed="' + (u.scope === 'month') + '">Month</button>' +
      '<button type="button" data-act="rscope" data-scope="year" aria-pressed="' + (u.scope === 'year') + '">12 months</button></div>' +
      '<button class="btn btn-ghost btn-sm" data-act="reportPdf">' + icon('download') + 'PDF</button>') +
      '<div class="tiles">' +
      h.tile('Net sales', h.signedMoney(m.netSales), delta(m.netSales, prev && prev.netSales, true) || h.plural(m.orders, 'order'), true) +
      h.tile('Profit', '<span class="' + (m.profit < 0 ? 'neg' : '') + '">' + h.signedMoney(m.profit) + '</span>', m.margin == null ? 'No sales' : h.pct(m.margin) + ' margin · ROI ' + h.pct(m.roi)) +
      h.tile('Orders', h.int(m.orders), 'Avg order ' + money(m.aov)) +
      h.tile('Magnets sold', h.int(m.magnets), m.orders ? (m.magnets / m.orders).toFixed(1) + ' per order' : '') +
      h.tile('Refunds', '<span class="' + (m.refunds ? 'neg' : '') + '">' + money(m.refunds) + '</span>', h.plural(m.refundCount, 'refund')) +
      h.tile('Repeat customers', h.pct(m.repeatRate), h.int(m.returningCustomers || 0) + ' of ' + h.plural(m.customers || 0, 'customer')) +
      h.tile('Sales tax to pay', money(m.taxOwed), 'Collected for the state, not yours') +
      h.tile('Income tax reserve', money(m.incomeTaxReserve), m.incomeTaxPct + '% of profit · keep ' + h.signedMoney(m.profitAfterTax)) +
      '</div>' + estNote +
      '<div class="two"><section class="card"><div class="card-head"><div><h2>Where the money went</h2><p class="sub">' + esc(period) + '</p></div></div><table class="pl">' + pl.map(function (x) {
        return '<tr class="' + (x[3] || '') + '"><td>' + esc(x[0]) + (x[2] ? '<span class="why">' + esc(x[2]) + '</span>' : '') + '</td><td class="' + (x[1] < 0 && /sum/.test(x[3] || '') ? 'neg' : '') + '">' + h.signedMoney(x[1]) + '</td></tr>';
      }).join('') + '</table></section>' +
      '<section class="card"><div class="card-head"><div><h2>Refunds by reason</h2><p class="sub">' + esc(period) + '</p></div></div>' +
      (reasons.length ? (topReason ? '<div class="callout">' + icon('info') + '<p class="small"><b>Top reason: ' + esc(topReason.label) + '</b> · ' + h.plural(topReason.count, 'refund') + ', ' + money(topReason.amount) +
        (m.orders ? ' (' + h.pct(topReason.count / Math.max(1, m.orders) * 100) + ' of orders)' : '') + '.' + adviceFor(topReason.reason) + '</p></div>' : '') +
        h.hbars(reasons.map(function (x) { return { label: x.label, sub: h.plural(x.count, 'refund'), value: x.amount, valueText: money(x.amount) }; }))
        : '<div class="empty">' + icon('check') + '<b>No refunds</b>Nothing went back to customers in this period.</div>') + '</section></div>' +
      taxCard +
      '<div class="two gap-top"><section class="card"><div class="card-head"><div><h2>Net sales by month</h2><p class="sub">12 months to ' + esc(R.monthLabel(u.month, true)) + '</p></div></div>' +
      h.chart('ch-net', { data: rows.map(function (x) { return { label: R.monthLabel(x.key, true), tick: R.monthLabel(x.key).split(' ')[0], value: x.netSales, tip: R.monthLabel(x.key, true) + ' · ' + h.plural(x.orders, 'order') }; }), height: 220, aria: 'Net sales by month' }) + '</section>' +
      '<section class="card"><div class="card-head"><div><h2>Profit by month</h2><p class="sub">After fees, labels, product and fixed costs</p></div></div>' +
      h.chart('ch-profit', { data: rows.map(function (x) { return { label: R.monthLabel(x.key, true), tick: R.monthLabel(x.key).split(' ')[0], value: x.profit, tip: R.monthLabel(x.key, true) + (x.margin == null ? '' : ' · ' + h.pct(x.margin) + ' margin') }; }), height: 220, aria: 'Profit by month' }) +
      '<p class="legend"><span><i></i>Profit</span><span><i class="neg"></i>Loss</span></p></section></div>' +
      '<div class="two gap-top"><section class="card"><div class="card-head"><div><h2>Top designs</h2><p class="sub">Ready-made designs by magnets sold</p></div></div>' +
      (top.designs.length ? h.hbars(top.designs.map(function (d) {
        return { label: d.title, sub: h.colName(d.collection) + ' · ' + money(d.revenue), value: d.qty, valueText: h.int(d.qty),
                 thumb: d.id ? '<img src="' + h.ART_URL + esc(d.id) + '.webp" alt="" width="36" height="36" loading="lazy" data-fallback>' : '' };
      })) : '<div class="empty">No designs sold in this period.</div>') + '</section>' +
      '<section class="card"><div class="card-head"><div><h2>Top collections</h2><p class="sub">Magnets sold, photo packs and big orders included</p></div></div>' +
      (top.collections.length ? h.hbars(top.collections.map(function (c) {
        return { label: c.special ? c.title : h.colName(c.key), sub: money(c.revenue) + ' before discounts', value: c.qty, valueText: h.int(c.qty) };
      })) : '<div class="empty">Nothing sold in this period.</div>') + '</section></div>' +
      '<section class="card flush gap-top"><div class="card-head"><div><h2>Month by month</h2><p class="sub">Swipe sideways on a phone</p></div><button class="btn btn-ghost btn-sm" data-act="reportPdf">' + icon('download') + 'PDF</button></div>' +
      '<div class="table-wrap"><table class="t compact sticky-first"><thead><tr><th>Month</th>' + REPORT_COLS.map(function (c) { return '<th class="num">' + esc(c[0]) + '</th>'; }).join('') + '</tr></thead><tbody>' +
      rows.slice().reverse().map(function (x) {
        return '<tr' + (x.key === u.month ? ' class="sel"' : '') + '><td><a class="ord" href="#reports?month=' + x.key + '">' + esc(R.monthLabel(x.key, true)) + '</a></td>' + REPORT_COLS.map(function (c) {
          var v = x[c[1]]; return '<td class="num' + ((c[1] === 'profit' && v < 0) ? ' neg' : '') + '">' + fmtCell(v, c[2]) + '</td>';
        }).join('') + '</tr>';
      }).join('') + '</tbody><tfoot><tr><td>12 months</td>' + (function () {
        var t = R.totalsOf(rows), yr = R.summarize(S.orders, S.settings, { from: R.monthRange(R.shiftMonth(u.month, -11)).from, to: R.monthRange(u.month).to }, { months: 12 });
        t.repeatRate = yr.repeatRate;
        return REPORT_COLS.map(function (c) { return '<td class="num">' + fmtCell(t[c[1]], c[2]) + '</td>'; }).join('');
      })() + '</tr></tfoot></table></div></section>' +
      '<p class="tiny faint gap-top">How it’s counted: an order belongs to the month it was paid; a refund to the month the money went back. Profit = net sales − (Stripe fees + labels + product costs + fixed costs). ROI = profit ÷ costs.</p>';
    return {
      title: 'Reports', html: html, after: function () {
        $('#r-month').addEventListener('change', function () { u.month = this.value; history.replaceState(null, '', '#reports'); h.route(); });
      }
    };
  };
  function adviceFor(reason) {
    return {
      damaged: ' Try a stiffer mailer or a cardboard backer.', not_delivered: ' Consider tracking on every order and photos of the packed parcel.',
      print_quality: ' Check the printer settings and paper; compare with a test sheet.', wrong_item: ' Use the packing slip checkboxes when packing.',
      late: ' Ship faster or update the shipping times on the site.', duplicate: ' Duplicates usually come from double checkouts: check the abandoned list.'
    }[reason] || '';
  }
  ACT.rscope = function (el) { S.ui.reports.scope = el.getAttribute('data-scope') === 'year' ? 'year' : 'month'; var y = scrollY; h.route(); scrollTo(0, y); };
  ACT.reportPdf = function () {
    var u = S.ui.reports, rows = R.monthly(S.orders, S.settings, u.month, 12);
    var m = u.scope === 'year' ? R.totalsOf(rows) : rows[rows.length - 1];
    var period = u.scope === 'year' ? R.monthLabel(R.shiftMonth(u.month, -11), true) + ' – ' + R.monthLabel(u.month, true) : R.monthLabel(u.month, true);
    var range = u.scope === 'year' ? { from: R.monthRange(R.shiftMonth(u.month, -11)).from, to: R.monthRange(u.month).to } : R.monthRange(u.month);
    var pl = [
      ['Gross sales', m.grossSales], ['Discounts', -m.discounts], ['Shipping charged', m.shippingCharged], ['Refunds', -m.refunds],
      ['Net sales', m.netSales, 'sum'], ['Stripe fees', -m.stripeFees], ['Stripe Tax fees', -m.stripeTaxFees], ['Shipping labels', -m.labels],
      ['Product costs', -m.productCosts], ['Fixed costs', -m.fixedCosts], ['Profit', m.profit, 'sum'],
      ['Set aside for income tax (' + m.incomeTaxPct + '%)', -m.incomeTaxReserve], ['Yours to keep', m.profitAfterTax, 'sum']
    ];
    var plHtml = '<table><tbody>' + pl.map(function (x) { return '<tr' + (x[2] ? ' class="sum"' : '') + '><td>' + h.esc(x[0]) + '</td><td class="n' + (x[1] < 0 ? ' neg' : '') + '">' + h.signedMoney(x[1]) + '</td></tr>'; }).join('') + '</tbody></table>';
    var states = Object.keys(m.taxByState || {}).filter(function (k) { return Math.abs(m.taxByState[k]) >= 0.005; }).map(function (k) { return { st: k === '?' ? 'Unknown' : k, amt: m.taxByState[k] }; });
    var reasons = R.refundsByReason(S.orders, range);
    var body = '<p><b>' + h.int(m.orders) + '</b> orders · <b>' + h.int(m.magnets) + '</b> magnets · margin ' + h.pct(m.margin) + ' · ROI ' + h.pct(m.roi) + '</p>' +
      '<h2>Where the money went</h2>' + plHtml +
      '<h2>Sales tax (not your money)</h2>' + h.pdfTable(states, [['State', 'st'], ['Owed', 'amt', 'money']], { st: 'Total owed to the state', amt: m.taxOwed }) +
      '<h2>Refunds by reason</h2>' + h.pdfTable(reasons, [['Reason', 'label'], ['Refunds', 'count', 'int'], ['Amount', 'amount', 'money']]) +
      '<h2>Month by month</h2>' + h.pdfTable(rows, [['Month', function (r) { return R.monthLabel(r.key, true); }], ['Orders', 'orders', 'int'], ['Net sales', 'netSales', 'money'],
        ['Costs', 'costs', 'money'], ['Profit', 'profit', 'signed'], ['Margin', 'margin', 'pct'], ['Sales tax owed', 'taxOwed', 'money'], ['Refunds', 'refunds', 'money']]);
    h.printDoc('Sales report', period, body);
  };
  ACT.custPdf = function () {
    h.printDoc('Customers', h.plural(R.customers(S.orders).length, 'customer'), h.pdfTable(R.customers(S.orders), [['Name', 'name'], ['Email', 'email'], ['City', 'city'],
      ['Orders', 'orders', 'int'], ['Spent', 'spent', 'money'], ['Refunded', 'refunded', 'money'], ['Last order', function (c) { return h.fmtDate(c.last); }], ['Repeat', function (c) { return c.repeat ? 'yes' : ''; }]]));
  };
  ACT.subPdf = function () {
    var list = (S.subscribers || []).filter(function (s) { return s.email && !s.unsubscribed; });
    h.printDoc('Subscribers', h.plural(list.length, 'subscriber'), h.pdfTable(list, [['Email', 'email'], ['Source', 'source'], ['Joined', function (s) { return h.fmtDate(R.toMs(s.at || s.createdAt)); }]]));
  };
  ACT.reportCsv = function () {
    var u = S.ui.reports, rows = R.monthly(S.orders, S.settings, u.month, 12);
    var cols = [['Month', 'key']].concat(REPORT_COLS.map(function (c) { return [c[0] + (c[2] === 'pct' ? ' %' : ''), c[1]]; }));
    cols.push(['Refund count', 'refundCount'], ['Customers', 'customers'], ['Returning customers', 'returningCustomers'], ['Fees estimated (orders)', 'feesEstimated']);
    h.downloadCSV(rows, cols, 'little-hive-report-' + u.month + '.csv');
  };

  /* ====================================================================== CUSTOMERS */
  V.customers = function () {
    var all = R.customers(S.orders), u = S.ui.customers;
    var repeat = all.filter(function (c) { return c.repeat; }).length;
    var spent = all.reduce(function (a, c) { return a + c.spent; }, 0);
    var html = head('Customers', 'Customers', 'Everyone who has paid for an order', '<button class="btn btn-ghost btn-sm" data-act="custPdf">' + icon('download') + 'PDF</button>') +
      '<div class="tiles">' + h.tile('Customers', h.int(all.length), '', true) + h.tile('Came back', h.int(repeat), all.length ? h.pct(repeat / all.length * 100) + ' ordered more than once' : '') +
      h.tile('Average spent', money(all.length ? spent / all.length : 0), 'per customer, after refunds') + '</div>' +
      '<div class="filters"><label class="search"><span class="sr">Search customers</span>' + icon('search') + '<input class="input" type="search" id="c-q" placeholder="Search by name, email or city" value="' + esc(u.q) + '"></label></div>' +
      '<section class="card flush" id="c-list"></section>';
    return {
      title: 'Customers', html: html, after: function () {
        var draw = function () {
          var q = u.q.trim().toLowerCase();
          var list = all.filter(function (c) { return !q || (c.name + ' ' + c.email + ' ' + c.city).toLowerCase().indexOf(q) >= 0; });
          $('#c-list').innerHTML = list.length ? '<div class="table-wrap"><table class="t"><thead><tr><th>Customer</th><th class="only-wide">City</th><th class="num only-wide">Orders</th><th class="num">Spent</th><th class="num only-wide">Last order</th></tr></thead><tbody>' +
            list.slice(0, 500).map(function (c) {
              var href = '#orders?tab=all&q=' + encodeURIComponent(c.email || c.name);
              return '<tr class="click" data-href="' + esc(href) + '" tabindex="0"><td class="who"><b>' + esc(c.name || c.email) + (c.repeat ? ' <span class="badge">Repeat</span>' : '') + '</b><span>' + esc(c.email) + '</span></td>' +
                '<td class="only-wide muted">' + esc(c.city) + '</td><td class="num only-wide">' + h.int(c.orders) + '</td><td class="num">' + money(c.spent) + '<div class="tiny muted only-phone">' + h.plural(c.orders, 'order') + '</div>' + (c.refunded ? '<div class="tiny neg">' + money(c.refunded) + ' refunded</div>' : '') + '</td>' +
                '<td class="num muted only-wide">' + esc(h.fmtDate(c.last)) + '</td></tr>';
            }).join('') + '</tbody></table></div>' : '<div class="empty">' + icon('customers') + '<b>' + (q ? 'No matches' : 'No customers yet') + '</b>' + (q ? 'Try another name or email.' : 'Your first customer will show up here.') + '</div>';
        };
        draw();
        $('#c-q').addEventListener('input', function () { u.q = this.value; draw(); });
      }
    };
  };
  ACT.custCsv = function () {
    h.downloadCSV(R.customers(S.orders), [['Name', 'name'], ['Email', 'email'], ['City', 'city'], ['Orders', 'orders'], ['Spent', 'spent'], ['Refunded', 'refunded'],
      ['First order', function (c) { return new Date(c.first).toISOString().slice(0, 10); }], ['Last order', function (c) { return new Date(c.last).toISOString().slice(0, 10); }],
      ['Repeat', function (c) { return c.repeat ? 'yes' : 'no'; }]], 'customers-' + h.today() + '.csv');
  };

  /* ====================================================================== DISCOUNTS */
  function normPromos(res) {
    var d = res && (res.promos || res.codes || res.data || res.items || res);
    if (!Array.isArray(d)) return [];
    return d.map(function (p) {
      var c = p.coupon || {};
      var cents = function (v) { return v == null ? null : v / 100; };
      return {
        code: p.code || p.id, active: p.active !== false,
        percentOff: p.percentOff != null ? p.percentOff : p.percent_off != null ? p.percent_off : c.percent_off != null ? c.percent_off : null,
        amountOff: p.amountOff != null ? p.amountOff : p.amount_off != null ? cents(p.amount_off) : c.amount_off != null ? cents(c.amount_off) : null,
        used: p.timesRedeemed != null ? p.timesRedeemed : p.times_redeemed != null ? p.times_redeemed : c.times_redeemed || 0,
        max: p.maxRedemptions != null ? p.maxRedemptions : p.max_redemptions != null ? p.max_redemptions : null,
        expires: p.expiresAt || p.expires_at || null, created: p.createdAt || p.created || null
      };
    });
  }
  V.discounts = function () {
    if (!S.promos && !S.promosLoading) {
      S.promosLoading = h.call('adminListPromos', {}).then(function (res) { S.promos = normPromos(res); })
        .catch(function (e) { S.promos = []; S.promosError = h.friendlyError(e); })
        .then(function () { S.promosLoading = null; if (location.hash.indexOf('#discounts') === 0) h.route(); });
    }
    var list = S.promos || [];
    var html = head('Discounts', 'Discount codes', 'Codes customers type at checkout. They work on top of the automatic bundle and volume discounts.') +
      '<div class="cols"><div><section class="card flush"><div class="card-head"><h2>Your codes</h2><button class="btn btn-ghost btn-sm" data-act="reloadPromos">' + icon('refresh') + 'Refresh</button></div>' +
      (S.promosError ? '<p class="err" style="margin:0 20px 14px">' + esc(S.promosError) + '</p>' : '') +
      (!S.promos ? loading('Asking Stripe…') : list.length ? '<div class="table-wrap"><table class="t"><thead><tr><th>Code</th><th>Discount</th><th class="num only-wide">Used</th><th class="only-wide">Expires</th><th>Status</th></tr></thead><tbody>' +
        list.map(function (p) {
          var exp = R.toMs(p.expires), expired = exp && exp < Date.now(), full = p.max != null && p.used >= p.max;
          return '<tr><td><b>' + esc(p.code) + '</b> <button class="icon-btn" data-act="copy" data-copy="' + esc(p.code) + '" aria-label="Copy code">' + icon('copy') + '</button></td>' +
            '<td>' + (p.percentOff != null ? esc(p.percentOff) + '% off' : p.amountOff != null ? money(p.amountOff) + ' off' : '—') +
              '<div class="tiny muted only-phone">Used ' + h.int(p.used) + (p.max != null ? ' / ' + h.int(p.max) : '') + (exp ? ' · ends ' + esc(h.fmtDate(exp)) : '') + '</div></td>' +
            '<td class="num only-wide">' + h.int(p.used) + (p.max != null ? ' / ' + h.int(p.max) : '') + '</td><td class="muted only-wide">' + (exp ? esc(h.fmtDate(exp, { year: true })) : 'Never') + '</td>' +
            '<td>' + (!p.active || expired || full ? '<span class="chip">' + (expired ? 'Expired' : full ? 'Used up' : 'Off') + '</span>' : '<span class="chip delivered">Active</span>') + '</td></tr>';
        }).join('') + '</tbody></table></div>' : '<div class="empty">' + icon('discounts') + '<b>No codes yet</b>Create one on the right, e.g. WELCOME10 for new customers.</div>') + '</section></div>' +
      '<div><section class="card"><div class="card-head"><h2>New code</h2></div><form class="stack" id="promo-form" novalidate>' +
      '<label class="field"><span>Code</span><input class="input" name="code" autocapitalize="characters" autocomplete="off" spellcheck="false" placeholder="WELCOME10" maxlength="30" style="text-transform:uppercase"><span class="hint">Letters and numbers, no spaces.</span></label>' +
      '<div class="seg" role="group" aria-label="Discount type"><button type="button" aria-pressed="true" data-act="promoType" data-type="percent">% off</button><button type="button" aria-pressed="false" data-act="promoType" data-type="amount">$ off</button></div>' +
      '<label class="field"><span id="promo-vlabel">Percent off</span><span class="input-pct" id="promo-vwrap"><input class="input" name="value" type="number" inputmode="decimal" min="1" max="100" step="1" placeholder="10"></span></label>' +
      '<div class="grid-2"><label class="field"><span>Max uses <span class="hint">(optional)</span></span><input class="input" name="max" type="number" min="1" step="1" placeholder="No limit"></label>' +
      '<label class="field"><span>Expires <span class="hint">(optional)</span></span><input class="input" name="expires" type="date" min="' + h.today() + '"></label></div>' +
      '<p class="err" id="promo-err" hidden></p><button class="btn btn-honey" type="submit">Create code</button></form></section>' +
      '<section class="card"><p class="small muted">Codes live in your Stripe account, so you can also pause them there. Customers enter them on the Stripe checkout page.</p></section></div></div>';
    return {
      title: 'Discounts', html: html, after: function () {
        var f = $('#promo-form');
        f.addEventListener('submit', function (ev) {
          ev.preventDefault();
          var err = $('#promo-err'), type = f.dataset.type || 'percent';
          var code = f.code.value.trim().toUpperCase(), value = Number(f.value.value), max = f.max.value ? Math.floor(Number(f.max.value)) : null;
          err.hidden = true;
          var fail = function (m, el) { err.textContent = m; err.hidden = false; if (el) el.focus(); };
          if (!/^[A-Z0-9_-]{3,30}$/.test(code)) return fail('Use 3 to 30 letters or numbers, no spaces.', f.code);
          if (!(value > 0) || (type === 'percent' && value > 100)) return fail(type === 'percent' ? 'Percent should be between 1 and 100.' : 'Type how many dollars off.', f.value);
          if (max != null && !(max >= 1)) return fail('Max uses should be 1 or more.', f.max);
          var data = { code: code, maxRedemptions: max };
          if (type === 'percent') data.percentOff = value; else data.amountOff = Math.round(value * 100) / 100;
          if (f.expires.value) data.expiresAt = new Date(f.expires.value + 'T23:59:59').toISOString();
          var btn = f.querySelector('button[type=submit]');
          h.busy(btn, true, 'Creating…');
          h.call('adminCreatePromo', data).then(function () {
            h.toast('Code ' + code + ' is ready'); S.promos = null; S.promosError = null; h.route();
          }).catch(function (e) { h.busy(btn, false); fail(h.friendlyError(e)); });
        });
      }
    };
  };
  ACT.reloadPromos = function () { S.promos = null; S.promosError = null; h.route(); };
  ACT.promoType = function (el) {
    var f = $('#promo-form'), t = el.getAttribute('data-type');
    f.dataset.type = t;
    Array.prototype.forEach.call(el.parentNode.children, function (b) { b.setAttribute('aria-pressed', String(b === el)); });
    $('#promo-vlabel').textContent = t === 'percent' ? 'Percent off' : 'Dollars off';
    $('#promo-vwrap').className = t === 'percent' ? 'input-pct' : 'input-money';
    f.value.max = t === 'percent' ? '100' : ''; f.value.step = t === 'percent' ? '1' : '0.01'; f.value.placeholder = t === 'percent' ? '10' : '5.00';
  };

  /* ====================================================================== PAYMENT LINKS */
  function customList() {
    var customs = S.orders.filter(function (o) { return (o.items || []).some(function (it) { return it.kind === 'custom'; }); });
    return '<div class="card-head"><h2>Custom orders</h2><span class="sub">' + h.plural(customs.length, 'link') + '</span></div>' +
      (customs.length ? '<ul class="olist" style="display:block">' + customs.map(function (o) {
        var it = o.items.find(function (x) { return x.kind === 'custom'; });
        return '<li><a href="#order/' + encodeURIComponent(o.id) + '"><span class="top"><b>' + esc(it.title || h.orderNo(o)) + '</b></span><span class="amt">' + money(it.amount) + '</span>' +
          '<span class="who">' + esc(o.email || '') + ' · ' + esc(h.fmtDate(o.createdAt)) + '</span><span class="st">' + (o.status === 'pending' ? '<span class="chip pending">Waiting for payment</span>' : h.chip(o, true)) + '</span></a></li>';
      }).join('') + '</ul>' : '<div class="empty">' + icon('links') + '<b>No custom orders yet</b>Links you send show up here, and turn into normal orders when paid.</div>');
  }
  V.links = function (r) {
    var pre = { title: r.q.get('title') || '', amount: r.q.get('amount') || '', email: r.q.get('email') || '', note: r.q.get('note') || '', magnets: r.q.get('magnets') || '' };
    var html = head('Payment links', 'Payment links', 'For quotes and custom jobs: send a Stripe checkout link for any amount.') +
      '<div class="cols"><div><section class="card"><div class="card-head"><h2>New payment link</h2></div><form class="stack" id="link-form" novalidate>' +
      '<label class="field"><span>What it’s for</span><input class="input" name="title" maxlength="120" placeholder="100 wedding favor magnets — Ana &amp; João" value="' + esc(pre.title) + '"><span class="hint">The customer sees this on the checkout page and in the email.</span></label>' +
      '<div class="grid-2"><label class="field"><span>Amount</span><span class="input-money"><input class="input" name="amount" type="number" inputmode="decimal" min="1" step="0.01" placeholder="175.00" value="' + esc(pre.amount) + '"></span></label>' +
      '<label class="field"><span>Magnets <span class="hint">(optional, for reports)</span></span><input class="input" name="magnets" type="number" inputmode="numeric" min="1" step="1" placeholder="100" value="' + esc(pre.magnets) + '"></label></div>' +
      '<label class="field"><span>Customer email <span class="hint">(we email them the link)</span></span><input class="input" name="email" type="email" placeholder="ana@example.com" value="' + esc(pre.email) + '"><span class="hint">Leave empty to just copy the link and send it yourself (WhatsApp, Instagram…).</span></label>' +
      '<label class="field"><span>Note to the customer <span class="hint">(optional)</span></span><textarea class="input" name="note" rows="3" placeholder="Includes design proof, printing and shipping.">' + esc(pre.note) + '</textarea></label>' +
      '<p class="err" id="link-err" hidden></p><div id="link-out"></div>' +
      '<button class="btn btn-honey" type="submit">' + icon('links') + 'Create payment link</button></form></section></div>' +
      '<div><section class="card flush" id="links-list">' + customList() + '</section></div></div>';
    return {
      title: 'Payment links', html: html, after: function () {
        var f = $('#link-form');
        f.addEventListener('submit', function (ev) {
          ev.preventDefault();
          var err = $('#link-err'), amount = Math.round(Number(f.amount.value) * 100) / 100, email = f.email.value.trim();
          err.hidden = true;
          var fail = function (m, el) { err.textContent = m; err.hidden = false; if (el) el.focus(); };
          if (f.title.value.trim().length < 3) return fail('Say what the link is for.', f.title);
          if (!(amount >= 0.5)) return fail('Type the amount (at least $0.50).', f.amount);
          if (email && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) return fail('That email doesn’t look right.', f.email);
          var mags = f.magnets.value ? Math.floor(Number(f.magnets.value)) : null;
          if (mags != null && !(mags > 0)) return fail('Magnets should be a whole number.', f.magnets);
          var btn = f.querySelector('button[type=submit]');
          var payload = { title: f.title.value.trim(), amount: amount, email: email, note: f.note.value.trim() };
          if (mags) payload.magnets = mags;
          h.busy(btn, true, 'Creating…');
          h.call('adminCreatePaymentLink', payload).then(function (res) {
            h.busy(btn, false);
            var url = (res && (res.url || res.link)) || '';
            $('#link-out').innerHTML = '<div class="ok-msg"><b>' + (email && (!res || res.emailed !== false) ? 'Link emailed to ' + esc(email) + '.' : 'Link ready.') + '</b> Copy it to send it yourself:<code class="code" style="background:var(--surface);color:var(--ink);border:1px solid var(--line)">' + esc(url) +
              '<button class="icon-btn" type="button" data-act="copy" data-copy="' + esc(url) + '" aria-label="Copy link">' + icon('copy') + '</button></code></div>';
            h.toast('Payment link created');
            f.reset();
            return h.loadOrders().then(function () { var l = $('#links-list'); if (l) l.innerHTML = customList(); });
          }).catch(function (e) { h.busy(btn, false); fail(h.friendlyError(e)); });
        });
      }
    };
  };

  /* ====================================================================== REVIEWS */
  function stars(n) { n = Math.round(R.num(n)); var s = ''; for (var i = 1; i <= 5; i++) s += i <= n ? '★' : '<span class="off">★</span>'; return '<span class="stars" aria-label="' + n + ' out of 5 stars">' + s + '</span>'; }
  V.reviews = function () {
    if (!need('reviews')) return { title: 'Reviews', html: head('Reviews', 'Reviews') + loading('Loading reviews…') };
    var tab = S.ui.reviews, all = S.reviews;
    var counts = { pending: 0, published: 0 };
    all.forEach(function (x) { var st = x.status === 'published' ? 'published' : 'pending'; counts[st]++; });
    var list = all.filter(function (x) { return (x.status === 'published' ? 'published' : 'pending') === tab; });
    var html = head('Reviews', 'Reviews', 'From verified buyers. Publish the ones you want on the shop.') + errBox('reviews') +
      '<nav class="tabs">' + [['pending', 'Waiting'], ['published', 'Published']].map(function (t) {
        return '<button type="button" data-act="revTab" data-tab="' + t[0] + '"' + (tab === t[0] ? ' aria-current="true"' : '') + '>' + t[1] + '<span class="n">' + counts[t[0]] + '</span></button>';
      }).join('') + '</nav>' +
      (list.length ? '<div class="feed">' + list.map(function (x) {
        var o = S.orders.find(function (y) { return y.id === x.orderId; });
        return '<article class="msg review"><img src="' + h.ART_URL + esc(x.designId || '') + '.webp" alt="" width="72" height="72" loading="lazy" data-fallback><div class="stack" style="gap:6px">' +
          '<header><b>' + stars(x.rating) + ' ' + esc(x.name || 'Customer') + '</b><time>' + esc(h.fmtDate(x.createdAt || x.at)) + '</time></header>' +
          '<p class="body">' + esc(x.text || '') + '</p><p class="meta"><span>' + esc(designTitle(x.designId, o)) + '</span>' + (o ? '<a href="#order/' + encodeURIComponent(o.id) + '">' + esc(h.orderNo(o)) + '</a>' : '') + '</p>' +
          '<div class="acts">' + (tab === 'pending' ? '<button class="btn btn-honey btn-sm" data-act="moderate" data-id="' + esc(x.id) + '" data-status="published">' + icon('check') + 'Publish</button>'
            : '<button class="btn btn-ghost btn-sm" data-act="moderate" data-id="' + esc(x.id) + '" data-status="pending">Unpublish</button>') +
          '<button class="btn btn-ghost btn-sm" data-act="moderate" data-id="' + esc(x.id) + '" data-status="deleted">Delete</button></div></div></article>';
      }).join('') + '</div>' : '<div class="card"><div class="empty">' + icon('reviews') + '<b>' + (tab === 'pending' ? 'No reviews waiting' : 'Nothing published yet') + '</b>' +
        (tab === 'pending' ? 'Customers are asked for a review when you mark their order delivered.' : 'Publish a review from the Waiting tab.') + '</div></div>');
    return { title: 'Reviews', html: html };
  };
  function designTitle(id, o) {
    var it = o && (o.items || []).find(function (i) { return i.id === id; });
    if (it && it.title) return it.title;
    return String(id || '').split('/').pop().replace(/-/g, ' ').replace(/\b\w/g, function (c) { return c.toUpperCase(); });
  }
  ACT.revTab = function (el) { S.ui.reviews = el.getAttribute('data-tab'); h.route(); };
  ACT.moderate = function (el) {
    var id = el.getAttribute('data-id'), st = el.getAttribute('data-status');
    var go = function () {
      h.busy(el, true);
      h.call('adminModerateReview', { id: id, status: st }).then(function () {
        if (st === 'deleted') S.reviews = S.reviews.filter(function (y) { return y.id !== id; });
        else { var x = S.reviews.find(function (y) { return y.id === id; }); if (x) x.status = st; }
        h.updateBadges(); h.toast(st === 'published' ? 'Published on the shop' : st === 'deleted' ? 'Review deleted' : 'Hidden from the shop'); h.route();
      }).catch(function (e) { h.busy(el, false); h.toast(h.friendlyError(e), true); });
    };
    if (st !== 'deleted') return go();
    h.dialog({ title: 'Delete this review?', html: '<p>Use this for spam or abuse. It can’t be undone. To just hide it, use Unpublish.</p>', ok: 'Delete review', danger: true })
      .then(function (ok) { if (ok) go(); });
  };

  /* ====================================================================== MESSAGES (contact form, ideas box, quote requests) */
  var QUOTE_SKIP = { id: 1, name: 1, email: 1, createdAt: 1, at: 1, message: 1, details: 1, status: 1, uid: 1, idea: 1, kind: 1, kindLabel: 1 };
  var MSG_TABS = [['messages', 'Contact form'], ['suggestions', 'Ideas'], ['quotes', 'Quote requests']];
  function prettyKey(k) { return k.replace(/([a-z])([A-Z])/g, '$1 $2').replace(/[_-]/g, ' ').replace(/^\w/, function (c) { return c.toUpperCase(); }); }
  V.messages = function (r) {
    var want = r && r.q && r.q.get('tab');
    if (want && MSG_TABS.some(function (t) { return t[0] === want; })) S.ui.messages = want;
    var a = need('messages'), b = need('quotes'), c = need('suggestions');
    if (!a || !b || !c) return { title: 'Messages', html: head('Inbox', 'Messages') + loading('Loading messages…') };
    var tab = S.ui.messages;
    var list = S[tab] || [];
    var html = head('Inbox', 'Messages', 'From the contact form, the ideas box and the big-order quote form. Reply by email.') + errBox('messages') + errBox('suggestions') + errBox('quotes') +
      '<nav class="tabs">' + MSG_TABS.map(function (t) {
        return '<button type="button" data-act="msgTab" data-tab="' + t[0] + '"' + (tab === t[0] ? ' aria-current="true"' : '') + '>' + t[1] + '<span class="n">' + (S[t[0]] || []).length + '</span></button>';
      }).join('') + '</nav>' +
      (list.length ? '<div class="feed">' + list.map(function (m) {
        var when = m.createdAt || m.at;
        var subj = tab === 'quotes' ? 'Your Little Hive House quote' : tab === 'suggestions' ? 'Your idea for Little Hive House' : 'Re: your message to Little Hive House';
        var extra = Object.keys(m).filter(function (k) { return !QUOTE_SKIP[k] && k !== 'topic' && m[k] != null && m[k] !== '' && typeof m[k] !== 'object'; });
        var body = m.message || m.details || m.idea || '';
        var badge = m.topic || m.kindLabel;
        var qty = m.quantity || m.qty;
        var linkQ = tab === 'quotes' ? h.qs({ email: m.email, magnets: qty || '', title: [(qty ? qty + ' ' : '') + (m.package || m.occasion || 'custom') + ' magnets', m.name ? '— ' + m.name : ''].join(' ') }) : '';
        return '<article class="msg"><header><b>' + esc(m.name || m.email || (tab === 'suggestions' ? 'A visitor' : 'Someone')) + '</b><time title="' + esc(h.fmtDT(when)) + '">' + esc(h.ago(when)) + '</time></header>' +
          '<p class="meta">' + (m.email ? '<a href="mailto:' + esc(m.email) + '">' + esc(m.email) + '</a>' : (tab === 'suggestions' ? '<span class="muted">No email left</span>' : '')) + (badge ? '<span class="badge quiet">' + esc(badge) + '</span>' : '') + '</p>' +
          (body ? '<p class="body">' + esc(body) + '</p>' : '') +
          (extra.length ? '<dl class="kv small">' + extra.map(function (k) { return '<dt>' + esc(prettyKey(k)) + '</dt><dd>' + esc(m[k]) + '</dd>'; }).join('') + '</dl>' : '') +
          '<div class="acts">' + (m.email ? '<a class="btn btn-ghost btn-sm" href="mailto:' + esc(m.email) + '?subject=' + encodeURIComponent(subj) + '">' + icon('mail') + 'Reply</a>' : '') +
          (tab === 'quotes' ? '<a class="btn btn-ghost btn-sm" href="#links' + linkQ + '">' + icon('links') + 'Send payment link</a>' : '') + '</div></article>';
      }).join('') + '</div>' : '<div class="card"><div class="empty">' + icon('messages') + '<b>Inbox zero</b>' +
        (tab === 'quotes' ? 'Quote requests from the Big orders page land here.' : tab === 'suggestions' ? 'Ideas from the “Share an idea” page land here.' : 'Messages from the contact form land here.') + '</div></div>');
    return { title: 'Messages', html: html };
  };
  ACT.msgTab = function (el) { S.ui.messages = el.getAttribute('data-tab'); location.hash = '#messages?tab=' + S.ui.messages; };

  /* ====================================================================== SUBSCRIBERS */
  V.subscribers = function () {
    if (!need('subscribers')) return { title: 'Subscribers', html: head('Subscribers', 'Subscribers') + loading('Loading subscribers…') };
    var all = S.subscribers.filter(function (s) { return s.email && !s.unsubscribed; }), u = S.ui.subscribers;
    var gone = S.subscribers.filter(function (s) { return s.email && s.unsubscribed; }).length;
    var mk = R.monthRange(R.monthKey(Date.now()));
    var month = all.filter(function (s) { var t = R.toMs(s.at || s.createdAt); return t >= mk.from && t < mk.to; }).length;
    var sources = {};
    all.forEach(function (s) { var k = s.source || 'site'; sources[k] = (sources[k] || 0) + 1; });
    var html = head('Subscribers', 'Subscribers', 'People who asked for news and deals', '<a class="btn btn-honey btn-sm" href="#newsletter">' + icon('mail') + 'Write an email</a> <button class="btn btn-ghost btn-sm" data-act="subPdf">' + icon('download') + 'PDF</button> <button class="btn btn-ghost btn-sm" data-act="subCsv">' + icon('download') + 'For email tools (CSV)</button>') + errBox('subscribers') +
      '<div class="tiles">' + h.tile('Subscribers', h.int(all.length), gone ? h.int(gone) + ' unsubscribed (not listed)' : '', true) + h.tile('New this month', h.int(month), '') +
      h.tile('Top source', esc(Object.keys(sources).sort(function (a, b) { return sources[b] - sources[a]; })[0] || '—'), '') + '</div>' +
      '<div class="filters"><label class="search"><span class="sr">Search</span>' + icon('search') + '<input class="input" type="search" id="s-q" placeholder="Search emails" value="' + esc(u.q) + '"></label></div>' +
      '<section class="card flush" id="s-list"></section>' +
      '<p class="tiny faint gap-top">PDF is a list to read or print. The CSV file is only for importing these emails into an email tool (Mailchimp, Kit…). Every marketing email must include the unsubscribe link.</p>';
    return {
      title: 'Subscribers', html: html, after: function () {
        var draw = function () {
          var q = u.q.trim().toLowerCase(), list = all.filter(function (s) { return !q || s.email.toLowerCase().indexOf(q) >= 0; });
          $('#s-list').innerHTML = list.length ? '<div class="table-wrap"><table class="t compact"><thead><tr><th>Email</th><th>Source</th><th class="num">Joined</th></tr></thead><tbody>' +
            list.slice(0, 1000).map(function (s) { return '<tr><td>' + esc(s.email) + '</td><td class="muted">' + esc(s.source || '') + '</td><td class="num muted">' + esc(h.fmtDate(s.at || s.createdAt)) + '</td></tr>'; }).join('') +
            '</tbody></table></div>' : '<div class="empty">' + icon('subscribers') + '<b>' + (q ? 'No matches' : 'No subscribers yet') + '</b></div>';
        };
        draw();
        $('#s-q').addEventListener('input', function () { u.q = this.value; draw(); });
      }
    };
  };
  ACT.subCsv = function () {
    h.downloadCSV((S.subscribers || []).filter(function (s) { return s.email && !s.unsubscribed; }), [['Email', 'email'], ['Source', 'source'],
      ['Joined', function (s) { var t = R.toMs(s.at || s.createdAt); return t ? new Date(t).toISOString().slice(0, 10) : ''; }]], 'subscribers-' + h.today() + '.csv');
  };

  /* ====================================================================== EMAIL SUBSCRIBERS (functions/newsletter.js) */
  var NL_TEMPLATES = [
    { key: 'hello', name: 'Still here', subject: 'A little hello from the hive', eyebrow: 'From the hive', title: 'Still pressing magnets, one by one',
      body: 'It has been a little while, so we wanted to say hi! We are still here, printing, pressing and packing every magnet by hand.\n\nThere are new designs in the shop, and you can turn your own photos into magnets now, with a frame and a caption if you like.',
      gallery: 'designs', button: { label: 'Visit the shop', href: 'https://littlehivehouse.com/shop.html' } },
    { key: 'new', name: 'New designs', subject: 'Fresh from the hive: new magnets', eyebrow: 'New this month', title: 'New designs for your fridge',
      body: 'We have been busy painting! Here are a few of the newest magnets in the shop.\n\nMix any 3 designs for $12, and add photo magnets to the same order.',
      gallery: 'designs', button: { label: 'See the new designs', href: 'https://littlehivehouse.com/shop.html' } },
    { key: 'photos', name: 'Photo magnets', subject: 'Your favorite photos, on the fridge', eyebrow: 'Photo magnets', title: 'Turn your photos into magnets',
      body: 'Weddings, grandkids, pets, trips: upload your favorite pictures, pick a frame, add a caption, and we print and press them by hand.\n\nPacks start at 4 magnets for $14.',
      gallery: 'photos', button: { label: 'Make photo magnets', href: 'https://littlehivehouse.com/photo-magnets.html' } },
    { key: 'deadline', name: 'Holiday deadline', subject: 'Order by December 12 for Christmas', eyebrow: 'Holiday shipping', title: 'Magnets in time for Christmas',
      body: 'Every magnet is made by hand, so we need a few days for each order. To get yours before Christmas, please order by December 12.\n\nPhoto magnets make a sweet gift for grandparents, and they fit in any stocking.',
      gallery: 'photos', button: { label: 'Shop holiday gifts', href: 'https://littlehivehouse.com/shop.html' } },
    { key: 'promo', name: 'Discount code', subject: 'A little thank-you: a discount this week', eyebrow: 'Just for our list', title: 'A little thank-you for being here',
      body: 'Thank you for being part of our little hive. Here is a discount code for this week, on everything in the shop.',
      gallery: 'designs', promo: { code: '', text: 'Enter it at checkout. Valid this week.' }, button: { label: 'Shop now', href: 'https://littlehivehouse.com/shop.html' } }
  ];
  function nlNewId() { return 'c' + Date.now().toString(36) + Math.random().toString(36).slice(2, 8); }
  function nlFrom(t) {
    return { id: nlNewId(), subject: t.subject, preheader: '', eyebrow: t.eyebrow, title: t.title, body: t.body, gallery: t.gallery,
      designs: [], promo: t.promo ? { code: t.promo.code, text: t.promo.text } : { code: '', text: '' }, button: { label: t.button.label, href: t.button.href } };
  }
  function nlCampaign(c) {
    return { subject: c.subject, preheader: c.preheader, eyebrow: c.eyebrow, title: c.title, body: c.body, gallery: c.gallery,
      designs: String(c.designsText || '').split(/[\s,]+/).filter(Boolean), promo: c.promo && c.promo.code ? c.promo : null, button: c.button };
  }
  V.newsletter = function () {
    if (!S.ui.newsletter) S.ui.newsletter = nlFrom(NL_TEMPLATES[0]);
    var c = S.ui.newsletter;
    var field = function (name, label, value, hint, attrs) {
      return '<label class="field"><span>' + esc(label) + '</span><input class="input" name="' + name + '" value="' + esc(value || '') + '"' + (attrs || '') + '>' + (hint ? '<span class="hint">' + esc(hint) + '</span>' : '') + '</label>';
    };
    var auto = Number(S.settings.autoNewsletter) !== 0;
    var html = head('Subscribers', 'Email subscribers', 'Automatic emails to everyone on your list, and extra ones when you want') +
      '<section class="card tint"><div class="card-head"><h2>Automatic emails</h2></div>' +
      '<label class="check"><input type="checkbox" id="nl-auto"' + (auto ? ' checked' : '') + '> <span><b>Send by themselves, twice a month</b></span></label>' +
      '<p class="small muted" style="margin-top:6px">The 1st: the designs of the season (Halloween, Christmas, Valentine’s…). The 15th: photo magnet ideas for the month. ' +
      'You get a note on your phone when one goes out. Nothing to do. The form below is only for an extra email, if you ever want one.</p></section>' +
      '<div class="cols"><div><section class="card"><div class="card-head"><h2>Start from</h2></div><div class="row wrap" style="gap:8px">' +
      NL_TEMPLATES.map(function (t) { return '<button class="btn btn-ghost btn-sm" data-act="nlTemplate" data-key="' + t.key + '">' + esc(t.name) + '</button>'; }).join('') + '</div></section>' +
      '<section class="card"><form class="stack" id="nl-form" novalidate>' +
      field('subject', 'Subject', c.subject, 'What people see in their inbox. Short and friendly.', ' maxlength="120"') +
      field('preheader', 'Preview line (optional)', c.preheader, 'The grey line next to the subject in most inboxes.', ' maxlength="160"') +
      field('eyebrow', 'Small label above the title', c.eyebrow, '', ' maxlength="40"') +
      field('nltitle', 'Title', c.title, '', ' maxlength="120"') +
      '<label class="field"><span>Message</span><textarea class="input" name="body" rows="7" maxlength="4000">' + esc(c.body) + '</textarea><span class="hint">Leave an empty line between paragraphs.</span></label>' +
      '<label class="field"><span>Pictures</span><select class="input" name="gallery">' +
      [['designs', 'Three of our designs'], ['photos', 'Photo magnet examples'], ['none', 'No pictures']].map(function (o) { return '<option value="' + o[0] + '"' + (c.gallery === o[0] ? ' selected' : '') + '>' + o[1] + '</option>'; }).join('') + '</select></label>' +
      field('designsText', 'Which designs (optional)', c.designsText, 'Up to 3, like places/las-vegas, fall/apple-picking. Empty = our favorites.') +
      field('promoCode', 'Discount code (optional)', c.promo && c.promo.code, 'Must already exist in Discounts. Leave empty for none.', ' maxlength="40" style="text-transform:uppercase"') +
      field('promoText', 'Line under the code', c.promo && c.promo.text, '', ' maxlength="140"') +
      field('btnLabel', 'Button', c.button && c.button.label, '', ' maxlength="40"') +
      field('btnHref', 'Button link', c.button && c.button.href, 'A page of littlehivehouse.com.', ' maxlength="300"') +
      '<p class="err" id="nl-err" hidden></p>' +
      '<div class="row wrap end" style="gap:8px"><button class="btn btn-ghost" type="button" data-act="nlPreview">Preview</button>' +
      '<button class="btn btn-ghost" type="button" data-act="nlTest">Send a test to me</button>' +
      '<button class="btn btn-honey" type="button" data-act="nlSend">Send to subscribers</button></div></form></section></div>' +
      '<div><section class="card"><div class="card-head"><h2>Preview</h2><span class="small muted" id="nl-count"></span></div><div id="nl-preview"><p class="small muted">Tap Preview to see the email as subscribers will.</p></div></section>' +
      '<section class="card"><div class="card-head"><h2>Sent before</h2></div><div id="nl-history"><p class="small muted">Loading…</p></div></section>' +
      '<p class="tiny faint">Every email includes an unsubscribe link and the shop’s mailing address, as US law (CAN-SPAM) requires. Once or twice a month is plenty.</p></div></div>';
    return {
      title: 'Email subscribers', html: html, after: function () {
        var t = $('#nl-auto');
        t.addEventListener('change', function () {
          var v = t.checked ? 1 : 0;
          h.call('adminSaveSettings', { autoNewsletter: v }).then(function () {
            S.settings = R.settingsWithDefaults(Object.assign({}, S.settings, { autoNewsletter: v }));
            h.toast(v ? 'Automatic emails are on.' : 'Automatic emails are off.');
          }).catch(function (e) { t.checked = !t.checked; h.toast(h.friendlyError(e), true); });
        });
        var f = $('#nl-form');
        f.addEventListener('input', function () {
          c.subject = f.subject.value; c.preheader = f.preheader.value; c.eyebrow = f.eyebrow.value; c.title = f.nltitle.value; c.body = f.body.value;
          c.gallery = f.gallery.value; c.designsText = f.designsText.value; c.promo = { code: f.promoCode.value.trim().toUpperCase(), text: f.promoText.value };
          c.button = { label: f.btnLabel.value, href: f.btnHref.value };
        });
        h.call('adminNewsletter', { action: 'list' }).then(function (res) {
          var list = (res && res.campaigns) || [];
          $('#nl-history').innerHTML = list.length ? '<ul class="plain">' + list.map(function (x) {
            return '<li class="small"><b>' + esc(x.subject) + '</b><br><span class="muted">' + esc(h.fmtDate(x.sentAt || x.createdAt)) + ' · ' + h.plural(R.num(x.sent), 'email') + (x.failed ? ' · ' + x.failed + ' failed' : '') + '</span></li>';
          }).join('') + '</ul>' : '<p class="small muted">Nothing sent yet.</p>';
        }).catch(function (e) { $('#nl-history').innerHTML = '<p class="small err">' + esc(h.friendlyError(e)) + '</p>'; });
      }
    };
  };
  function nlErr(msg) { var e = $('#nl-err'); if (!e) return; e.textContent = msg || ''; e.hidden = !msg; }
  ACT.nlTemplate = function (btn) {
    var t = NL_TEMPLATES.find(function (x) { return x.key === btn.getAttribute('data-key'); });
    if (t) { S.ui.newsletter = nlFrom(t); h.route(); }
  };
  ACT.nlPreview = function (btn) {
    nlErr(''); h.busy(btn, true, 'Loading…');
    h.call('adminNewsletter', { action: 'preview', campaign: nlCampaign(S.ui.newsletter) }).then(function (res) {
      h.busy(btn, false);
      var fr = document.createElement('iframe');
      fr.className = 'mail-preview'; fr.setAttribute('title', 'Email preview'); fr.setAttribute('sandbox', '');
      fr.srcdoc = res.html;
      var box = $('#nl-preview'); box.innerHTML = ''; box.appendChild(fr);
      $('#nl-count').textContent = h.plural(R.num(res.count), 'subscriber') + ' will get it';
      if (!res.postal) nlErr('Before sending to subscribers, the shop’s mailing address must be set (MAIL_POSTAL_ADDRESS in GitHub). US law asks for it in every marketing email; a PO Box works. Tests to yourself work now.');
      if (window.innerWidth < 900) box.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }).catch(function (e) { h.busy(btn, false); nlErr(h.friendlyError(e)); });
  };
  ACT.nlTest = function (btn) {
    nlErr(''); h.busy(btn, true, 'Sending…');
    h.call('adminNewsletter', { action: 'test', campaign: nlCampaign(S.ui.newsletter) }).then(function (res) {
      h.busy(btn, false); h.toast('Test sent to ' + res.to);
    }).catch(function (e) { h.busy(btn, false); nlErr(h.friendlyError(e)); });
  };
  ACT.nlSend = function (btn) {
    nlErr('');
    var c = S.ui.newsletter;
    h.call('adminNewsletter', { action: 'preview', campaign: nlCampaign(c) }).then(function (res) {
      return h.dialog({ title: 'Send this email?', ok: 'Send to ' + h.plural(R.num(res.count), 'subscriber'),
        html: '<p><b>' + esc(res.subject) + '</b></p><p class="small muted">It goes out right away and can’t be undone. Did you send yourself a test first?</p>' });
    }).then(function (ok) {
      if (!ok) return;
      h.busy(btn, true, 'Sending…');
      return h.call('adminNewsletter', { action: 'send', campaign: nlCampaign(c), campaignId: c.id, confirm: 'SEND' }).then(function (res) {
        h.busy(btn, false);
        h.toast('Sent to ' + h.plural(R.num(res.sent), 'subscriber') + (res.failed ? ' (' + res.failed + ' failed)' : ''));
        S.ui.newsletter = null; h.route();
      });
    }).catch(function (e) { h.busy(btn, false); nlErr(h.friendlyError(e)); });
  };

  /* ====================================================================== TEST PRINT (functions/admin.js adminTestSheet) */
  function tpDefaultBorder() { return (S.settings && S.settings.printBorderColor) || '#FFFFFF'; }
  function tpState() { return S.ui.testprint || (S.ui.testprint = { col: '', designs: [], photos: [], border: tpDefaultBorder(), perItem: false }); }
  function tpLoadDesigns() {
    if (S.shopDesigns) return Promise.resolve(S.shopDesigns);
    return fetch('../shop.html', { cache: 'no-cache' }).then(function (r) { return r.text(); }).then(function (txt) {
      var doc = new DOMParser().parseFromString(txt, 'text/html'), seen = {};
      S.shopDesigns = Array.prototype.slice.call(doc.querySelectorAll('[data-add]')).map(function (b) {
        return { id: b.getAttribute('data-add'), name: b.getAttribute('data-name') || b.getAttribute('data-add'), col: b.getAttribute('data-collection') || '' };
      }).filter(function (d) { if (seen[d.id]) return false; seen[d.id] = 1; return /^[a-z0-9-]+\/[a-z0-9-]+$/.test(d.id); });
      return S.shopDesigns;
    });
  }
  function tpCount(st) {
    return st.designs.reduce(function (n, d) { return n + d.qty; }, 0) + st.photos.reduce(function (n, p) { return n + p.qty; }, 0);
  }
  V.testprint = function () {
    var st = tpState();
    var html = head('Printing', 'Test print', 'Make a magnets PDF without an order: to test the printer, the paper, the punch, or a new design') +
      '<div class="cols"><div>' +
      '<section class="card"><div class="card-head"><h2>Designs</h2></div><label class="field"><span>Collection</span><select class="input" id="tp-col"><option value="">Choose a collection…</option></select></label>' +
      '<div class="tp-grid" id="tp-grid"></div></section>' +
      '<section class="card"><div class="card-head"><h2>Photos</h2></div><label class="btn btn-ghost btn-sm" style="cursor:pointer">' + icon('image') + 'Add photos<input type="file" id="tp-files" accept="image/*" multiple hidden></label>' +
      '<p class="tiny faint" style="margin-top:6px">Each photo is printed with the frame and caption you pick, exactly like a customer’s.</p><div id="tp-photos" class="stack gap-top"></div></section>' +
      '</div><div>' +
      '<section class="card tint"><div class="card-head"><h2>Your test sheet</h2><span class="small muted" id="tp-count"></span></div><p class="small muted" id="tp-last" hidden></p><div id="tp-list"></div>' +
      '<div class="field gap-top"><span>Border around each picture</span>' + h.borderPicker(st.border, { id: 'tp-border' }) + '</div>' +
      '<label class="check"><input type="checkbox" id="tp-peritem"' + (st.perItem ? ' checked' : '') + '> <span>A different border for some magnets<span class="hint">Each design or photo gets its own choice: the border above, Photo colour, or any colour.</span></span></label>' +
      '<p class="err" id="tp-err" hidden></p><div class="row end gap-top"><button class="btn btn-ghost btn-sm" data-act="tpClear">Clear</button><button class="btn btn-honey" data-act="tpMake">' + icon('print') + 'Make test PDF</button></div></section>' +
      '<section class="card"><div class="card-head"><h2>Print it well</h2></div><ol class="small" style="padding-left:18px;margin:0;display:grid;gap:6px">' +
      '<li>Print from the <b>Canon PRINT</b> app (Wi-Fi Direct works), not the iPhone’s own Print button.</li>' +
      '<li>Paper: <b>Letter</b>, media type <b>Photo Paper Plus Glossy II</b>, quality <b>High</b>, borderless <b>off</b>, Auto Photo Fix <b>off</b>.</li>' +
      '<li>Glossy side up toward you in the rear tray. Let the sheet dry 10 minutes before cutting.</li>' +
      '<li>Colours odd or stripes? In the app: Maintenance › Nozzle Check, then Cleaning if a colour is missing.</li></ol></section>' +
      '</div></div>';
    return {
      title: 'Test print', html: html, after: function () {
        var sel = $('#tp-col');
        tpLoadDesigns().then(function (list) {
          var cols = [];
          list.forEach(function (d) { if (cols.indexOf(d.col) < 0) cols.push(d.col); });
          sel.innerHTML = '<option value="">Choose a collection…</option>' + cols.map(function (c) { return '<option' + (c === st.col ? ' selected' : '') + '>' + esc(c) + '</option>'; }).join('');
          tpGrid();
        }).catch(function (e) { $('#tp-grid').innerHTML = '<p class="small err">Couldn’t load the designs: ' + esc(e.message) + '</p>'; });
        sel.addEventListener('change', function () { st.col = sel.value; tpGrid(); });
        $('#tp-border').addEventListener('bpick', function (ev) { st.border = ev.detail || '#FFFFFF'; });
        $('#tp-peritem').addEventListener('change', function (ev) { st.perItem = ev.target.checked; tpList(); });
        $('#tp-files').addEventListener('change', function (ev) { tpAddFiles(ev.target.files); ev.target.value = ''; });
        A.h.loadFrames().then(function () { tpPhotos(); });
        tpList();
        tpRestore();
      }
    };
  };
  /* the last test sheet is saved on the server (functions/admin.js adminLastTestSheet): it comes back on its own when
     this page opens with nothing picked, so it can be made again after a change without picking everything again */
  function tpLastNote(res) {
    var el = $('#tp-last'); if (!el) return;
    var bits = [];
    if (res.sheet && res.sheet.at) bits.push('Your last test sheet (' + esc(h.ago(res.sheet.at)) + ') is saved here.');
    if (res.pdfUrl) bits.push('<a href="' + esc(res.pdfUrl) + '" target="_blank" rel="noopener">Open the last test PDF</a>');
    el.innerHTML = bits.join(' '); el.hidden = !bits.length;
  }
  function tpRestore() {
    h.call('adminLastTestSheet', {}).then(function (res) {
      var st = tpState();
      if (res.sheet && !tpCount(st) && !S.ui.testprintRestored) {
        S.ui.testprintRestored = true;
        st.designs = (res.sheet.designs || []).map(function (d) { return { id: d.id, name: d.name || d.id, qty: Math.max(1, Number(d.qty) || 1), border: d.border || '' }; });
        if (res.sheet.border) st.border = res.sheet.border === 'black' ? '#000000' : res.sheet.border === 'white' ? '#FFFFFF' : res.sheet.border;
        st.photos = (res.sheet.photos || []).map(function (p) { return { name: p.name || 'Photo', data: p.url || '', saved: p.saved, frame: p.frame || 'none', caption: p.caption || '', capStyle: p.capStyle || '', qty: Math.max(1, Number(p.qty) || 1), border: p.border || '' }; });
        st.perItem = st.designs.concat(st.photos).some(function (x) { return x.border; });
        h.route();
        return;
      }
      tpLastNote(res);
    }).catch(function () { /* nothing saved yet, or offline: start empty */ });
  }
  function tpGrid() {
    var st = tpState(), box = $('#tp-grid'); if (!box) return;
    var list = (S.shopDesigns || []).filter(function (d) { return st.col && d.col === st.col; });
    box.innerHTML = list.map(function (d) {
      return '<button type="button" class="tp-d" data-act="tpAdd" data-id="' + esc(d.id) + '" title="' + esc(d.name) + '"><img src="' + h.ART_URL + esc(d.id) + '.webp" alt="" loading="lazy"><span>' + esc(d.name) + '</span></button>';
    }).join('') || (st.col ? '<p class="small muted">No designs.</p>' : '<p class="small muted">Pick a collection, then tap the designs to add them.</p>');
  }
  function tpList() {
    var st = tpState(), box = $('#tp-list'); if (!box) return;
    var n = tpCount(st);
    $('#tp-count').textContent = n ? h.plural(n, 'magnet') + ' · ' + h.plural(Math.ceil(n / R.perSheet(S.settings && S.settings.printCutIn)), 'sheet') : '';
    var pick = function (it, kind, i) { return st.perItem ? h.borderPicker(it.border || '', { def: 'Same as above', small: true, attrs: ' data-kind="' + kind + '" data-i="' + i + '"' }) : ''; };
    var rows = st.designs.map(function (d, i) {
      return '<li class="tp-item"><div class="tp-row"><img src="' + h.ART_URL + esc(d.id) + '.webp" alt=""><span>' + esc(d.name) + '</span>' +
        '<input class="input tp-qty" type="number" min="1" max="27" value="' + d.qty + '" data-kind="d" data-i="' + i + '" aria-label="How many">' +
        '<button type="button" class="icon-btn" data-act="tpDel" data-kind="d" data-i="' + i + '" aria-label="Remove">×</button></div>' + pick(d, 'd', i) + '</li>';
    }).concat(st.photos.map(function (p, i) {
      return '<li class="tp-item"><div class="tp-row"><img src="' + p.data + '" alt=""><span>' + esc(p.name) + '</span>' +
        '<input class="input tp-qty" type="number" min="1" max="27" value="' + p.qty + '" data-kind="p" data-i="' + i + '" aria-label="How many">' +
        '<button type="button" class="icon-btn" data-act="tpDel" data-kind="p" data-i="' + i + '" aria-label="Remove">×</button></div>' + pick(p, 'p', i) + '</li>';
    }));
    box.innerHTML = rows.length ? '<ul class="plain">' + rows.join('') + '</ul>' : '<p class="small muted">Nothing yet. Add designs or photos.</p>';
    Array.prototype.forEach.call(box.querySelectorAll('.bpick[data-kind]'), function (bp) {
      bp.addEventListener('bpick', function (ev) {
        var arr = bp.getAttribute('data-kind') === 'd' ? st.designs : st.photos, it = arr[Number(bp.getAttribute('data-i'))];
        if (it) it.border = ev.detail || '';
      });
    });
    Array.prototype.forEach.call(box.querySelectorAll('.tp-qty'), function (inp) {
      inp.addEventListener('change', function () {
        var arr = inp.getAttribute('data-kind') === 'd' ? st.designs : st.photos, it = arr[Number(inp.getAttribute('data-i'))];
        it.qty = Math.max(1, Math.min(27, Math.floor(Number(inp.value) || 1))); inp.value = it.qty; tpList();
      });
    });
  }
  function tpPhotos() {
    var st = tpState(), box = $('#tp-photos'); if (!box) return;
    var frames = Object.keys(S.frames || {}).map(function (k) { return S.frames[k]; }).filter(function (f) { return !f.hidden; });
    box.innerHTML = st.photos.map(function (p, i) {
      var f = S.frames && S.frames[p.frame], c = f && f.caption, styles = c && c.styles ? Object.keys(c.styles) : [];
      return '<div class="tp-photo"><img src="' + p.data + '" alt=""><div class="stack" style="gap:6px;flex:1;min-width:0">' +
        '<select class="input" data-tp="frame" data-i="' + i + '">' + frames.map(function (x) { return '<option value="' + esc(x.id) + '"' + (x.id === p.frame ? ' selected' : '') + '>' + esc(x.name) + '</option>'; }).join('') + '</select>' +
        (c ? '<input class="input" data-tp="caption" data-i="' + i + '" maxlength="' + (c.max || 24) + '" placeholder="Caption, e.g. ' + esc(c.placeholder || '') + '" value="' + esc(p.caption) + '">' : '') +
        (styles.length > 1 ? '<select class="input" data-tp="capStyle" data-i="' + i + '">' + styles.map(function (k) { return '<option value="' + k + '"' + ((p.capStyle || c.default) === k ? ' selected' : '') + '>' + esc(c.styles[k].name || k) + '</option>'; }).join('') + '</select>' : '') +
        '</div></div>';
    }).join('');
    Array.prototype.forEach.call(box.querySelectorAll('[data-tp]'), function (el) {
      el.addEventListener(el.tagName === 'INPUT' ? 'input' : 'change', function () {
        var p = st.photos[Number(el.getAttribute('data-i'))], k = el.getAttribute('data-tp');
        p[k] = el.value;
        if (k === 'frame') { p.capStyle = ''; tpPhotos(); }
      });
    });
  }
  function tpAddFiles(files) {
    var st = tpState();
    Array.prototype.slice.call(files, 0, Math.max(0, 9 - st.photos.length)).forEach(function (file) {
      var url = URL.createObjectURL(file), im = new Image();
      im.onload = function () {
        var k = Math.min(1, 2000 / Math.max(im.naturalWidth, im.naturalHeight)), c = document.createElement('canvas');
        c.width = Math.round(im.naturalWidth * k); c.height = Math.round(im.naturalHeight * k);
        var g = c.getContext('2d'); g.fillStyle = '#fff'; g.fillRect(0, 0, c.width, c.height); g.drawImage(im, 0, 0, c.width, c.height);
        URL.revokeObjectURL(url);
        st.photos.push({ name: file.name || 'Photo', data: c.toDataURL('image/jpeg', 0.9), frame: 'none', caption: '', capStyle: '', qty: 1 });
        tpPhotos(); tpList();
      };
      im.onerror = function () { URL.revokeObjectURL(url); h.toast('Couldn’t open ' + (file.name || 'that photo') + '. Try a JPG.', true); };
      im.src = url;
    });
  }
  ACT.tpAdd = function (btn) {
    var st = tpState(), id = btn.getAttribute('data-id');
    var d = (S.shopDesigns || []).find(function (x) { return x.id === id; });
    var have = st.designs.find(function (x) { return x.id === id; });
    if (have) have.qty += 1; else st.designs.push({ id: id, name: d ? d.name : id, qty: 1 });
    tpList(); h.toast((d ? d.name : id) + ' added');
  };
  ACT.tpDel = function (btn) {
    var st = tpState(), arr = btn.getAttribute('data-kind') === 'd' ? st.designs : st.photos;
    arr.splice(Number(btn.getAttribute('data-i')), 1); tpList(); tpPhotos();
  };
  ACT.tpClear = function () { var o = tpState(); S.ui.testprint = { col: o.col, designs: [], photos: [], border: o.border, perItem: o.perItem }; h.route(); };
  ACT.tpMake = function (btn) {
    var st = tpState(), err = $('#tp-err'); err.hidden = true;
    var n = tpCount(st);
    if (!n) { err.textContent = 'Add at least one design or photo.'; err.hidden = false; return; }
    if (n > 27) { err.textContent = 'A test sheet holds up to 27 magnets (3 sheets). Remove a few.'; err.hidden = false; return; }
    var tab = null;
    try { tab = window.open('about:blank', '_blank'); if (tab && tab.document) tab.document.body.innerHTML = '<p style="font:16px -apple-system,system-ui,sans-serif;padding:24px">Making the test sheet… about a minute.</p>'; } catch (e) { tab = null; }
    h.busy(btn, true, 'Making…');
    h.call('adminTestSheet', {
      border: st.border || '#FFFFFF',
      designs: st.designs.map(function (d) { return { id: d.id, qty: d.qty, border: st.perItem && d.border ? d.border : null }; }),
      photos: st.photos.map(function (p) {
        var o = { name: p.name, frame: p.frame, caption: p.caption, capStyle: p.capStyle || null, qty: p.qty, border: st.perItem && p.border ? p.border : null };
        if (p.saved) o.saved = p.saved; else o.data = p.data;
        return o;
      })
    }).then(function (res) {
      h.busy(btn, false);
      if (res.saved) h.toast('Test sheet saved. It will be here next time.');
      if (res.url) tpLastNote({ sheet: { at: new Date().toISOString() }, pdfUrl: res.url });
      if (tab && !tab.closed) tab.location.href = res.url;
      else h.dialog({ title: 'Test sheet ready', ok: false, cancel: 'Close', html: '<p><a class="btn btn-honey" href="' + esc(res.url) + '" target="_blank" rel="noopener">' + icon('external') + 'Open the PDF</a></p>' });
    }).catch(function (e) {
      h.busy(btn, false);
      if (tab && !tab.closed) { try { tab.close(); } catch (x) { /* ignore */ } }
      err.textContent = h.friendlyError(e); err.hidden = false;
    });
  };

  /* ====================================================================== SETTINGS */
  var FIELDS = [
    ['magnetUnitCost', 'Cost of one magnet', 'money', 'Paper, ink, magnet sheet and lamination for one 2 × 2 in magnet. Add up a pack of supplies and divide by how many magnets it makes.'],
    ['packagingCost', 'Packaging per order', 'money', 'Envelope or mailer, backing card, thank-you card and tape for one order.'],
    ['defaultLabelCost', 'Usual shipping label', 'money', 'Pre-filled when you ship, and used in reports for shipped orders without a label cost.'],
    ['stripePct', 'Stripe fee (percent)', 'pct', 'Stripe’s standard US card fee is 2.9% + 30¢. Only used when Stripe didn’t send the real fee.'],
    ['stripeFixed', 'Stripe fee (fixed)', 'money', 'The fixed part of the Stripe fee per payment.'],
    ['monthlyFixedCosts', 'Monthly fixed costs', 'money', 'Things you pay every month no matter how much you sell: website, Etsy plan, printer lease, software. Subtracted from each month’s profit.'],
    ['stripeTaxPct', 'Stripe Tax fee (percent)', 'pct', 'Stripe charges this on each order where it calculates sales tax. Counted as a cost in reports.'],
    ['incomeTaxPct', 'Set aside for income tax', 'pct', 'Share of each month’s profit to put aside for federal, state and self-employment tax. Ask your accountant for the right number; 25% to 30% is a common starting point.']
  ];
  V.settings = function () {
    var s = S.settings;
    var ex = 9 * s.magnetUnitCost + s.packagingCost;
    var html = head('Settings', 'Settings', 'Your costs. Reports use them to work out profit.') +
      '<div class="cols"><div><section class="card"><div class="card-head"><h2>Costs</h2></div><form class="stack" id="set-form" novalidate>' +
      FIELDS.map(function (f) {
        return '<label class="field"><span>' + esc(f[1]) + '</span><span class="' + (f[2] === 'pct' ? 'input-pct' : 'input-money') + '"><input class="input" name="' + f[0] + '" type="number" inputmode="decimal" min="0" step="0.01" value="' + esc(f[2] === 'money' ? Number(s[f[0]]).toFixed(2) : s[f[0]]) + '"></span>' +
          '<span class="hint">' + esc(f[3]) + '</span></label>';
      }).join('') +
      '<div class="callout calm">' + icon('info') + '<p class="small" id="set-example">Example: a 9-photo pack costs you <b>' + money(ex) + '</b> to make (9 × ' + money(s.magnetUnitCost) + ' + ' + money(s.packagingCost) + ' packaging), plus the label and Stripe fee.</p></div>' +
      '<p class="err" id="set-err" hidden></p><div class="row end"><button class="btn btn-honey" type="submit">Save costs</button></div></form></section></div>' +
      '<div><section class="card"><div class="card-head"><h2>Admin access</h2></div><p class="small">Signed in as <b>' + esc(S.user.email) + '</b>.</p>' +
      '<p class="small muted" style="margin-top:8px">Admins are the emails in <code>ADMIN_EMAILS</code> (see SETUP.md). A new admin signs up on the shop’s account page, opens this page and taps “Activate admin access”.</p>' +
      '<div class="row gap-top"><button class="btn btn-ghost btn-sm" data-act="theme">' + esc(themeText()) + '</button><button class="btn btn-ghost btn-sm" data-act="signout">' + icon('logout') + 'Sign out</button></div></section>' +
      notifCard() + installCard() +
      printCard(s) + '</div></div>';
    return {
      title: 'Settings', html: html, after: function () {
        loadNotif();
        wirePrint();
        var f = $('#set-form');
        f.addEventListener('input', function () {
          var mc = Number(f.magnetUnitCost.value) || 0, pk = Number(f.packagingCost.value) || 0;
          $('#set-example').innerHTML = 'Example: a 9-photo pack costs you <b>' + money(9 * mc + pk) + '</b> to make (9 × ' + money(mc) + ' + ' + money(pk) + ' packaging), plus the label and Stripe fee.';
        });
        f.addEventListener('submit', function (ev) {
          ev.preventDefault();
          var err = $('#set-err'), out = {};
          err.hidden = true;
          for (var i = 0; i < FIELDS.length; i++) {
            var k = FIELDS[i][0], v = f[k].value;
            if (v === '' || isNaN(Number(v)) || Number(v) < 0) { err.textContent = FIELDS[i][1] + ' should be a number (0 or more).'; err.hidden = false; f[k].focus(); return; }
            if (k === 'stripePct' && Number(v) > 20) { err.textContent = 'The Stripe percent looks too high.'; err.hidden = false; f[k].focus(); return; }
            out[k] = Math.round(Number(v) * 100) / 100;
          }
          var btn = f.querySelector('button[type=submit]');
          h.busy(btn, true, 'Saving…');
          h.call('adminSaveSettings', out).then(function () {
            S.settings = R.settingsWithDefaults(Object.assign({}, S.settings, out)); h.busy(btn, false); h.toast('Saved. Reports are updated.');
          }).catch(function (e) { h.busy(btn, false); err.textContent = h.friendlyError(e); err.hidden = false; });
        });
      }
    };
  };
  /* ---------- printing (functions/printsheet.js reads these when it makes the PDFs) ---------- */
  function printCard(s) {
    return '<section class="card"><div class="card-head"><h2>Printing</h2></div><form class="stack" id="print-form" novalidate>' +
      '<label class="field"><span>Size of the paper piece the punch cuts</span><span class="input-unit"><input class="input" name="printCutIn" type="number" inputmode="decimal" min="2.1" max="2.95" step="0.01" value="' + esc(Number(s.printCutIn).toFixed(2)) + '"> in</span>' +
      '<span class="hint">Cut a scrap of paper with the punch and measure it from one straight side to the opposite one. The magnet face stays 2 in; the rest wraps around the edge. Between 2.10 and 2.95. Up to 2.55 in, 9 magnets fit on a sheet; bigger pieces, 6.</span></label>' +
      '<label class="field"><span>Size of each printed picture</span><span class="input-unit"><input class="input" name="printImageIn" type="number" inputmode="decimal" min="2" max="2.3" step="0.01" value="' + esc(Number(s.printImageIn).toFixed(2)) + '"> in</span>' +
      '<span class="hint">The photo or design, with white paper around it. A little over 2 in covers the rounded edge of the magnet face. If white shows on the front, make it bigger; if the picture runs too far down the sides, smaller. Between 2.00 and 2.30.</span></label>' +
      '<div class="field"><span>Default border around each picture</span>' + h.borderPicker(s.printBorderColor || '#FFFFFF', { id: 'print-border' }) +
      '<span class="hint">The paper around the picture that wraps over the edge of the magnet. Photo colour takes the colour of each picture’s own edge. An order or a test sheet can change it for some magnets. Try them with Test print.</span></div>' +
      '<label class="check"><input type="checkbox" name="printEnhance"' + (Number(s.printEnhance) ? ' checked' : '') + '> <span>Touch up customer photos for paper<span class="hint">Fixes washed-out or too-bright photos and adds a little colour and contrast, because prints come out flatter than a screen.</span></span></label>' +
      '<p class="err" id="print-err" hidden></p><div class="row end"><button class="btn btn-honey" type="submit">Save printing</button></div>' +
      '<p class="small muted">New orders use these right away. For an order already made, tap Rebuild on its page.</p></form></section>';
  }
  function wirePrint() {
    var f = $('#print-form'); if (!f) return;
    f.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var err = $('#print-err'), cut = Number(f.printCutIn.value), img = Number(f.printImageIn.value);
      err.hidden = true;
      if (!isFinite(cut) || cut < 2.1 || cut > 2.95) { err.textContent = 'The piece should be between 2.10 and 2.95 inches.'; err.hidden = false; f.printCutIn.focus(); return; }
      if (!isFinite(img) || img < 2 || img > 2.3) { err.textContent = 'The picture should be between 2.00 and 2.30 inches.'; err.hidden = false; f.printImageIn.focus(); return; }
      var out = { printCutIn: Math.round(cut * 100) / 100, printImageIn: Math.round(img * 100) / 100, printEnhance: f.printEnhance.checked ? 1 : 0, printBorderColor: h.bpickValue($('#print-border')) || '#FFFFFF' };
      var btn = f.querySelector('button[type=submit]');
      h.busy(btn, true, 'Saving…');
      h.call('adminSaveSettings', out).then(function () {
        S.settings = R.settingsWithDefaults(Object.assign({}, S.settings, out)); h.busy(btn, false); h.toast('Saved. New print sheets use it.');
      }).catch(function (e) { h.busy(btn, false); err.textContent = h.friendlyError(e); err.hidden = false; });
    });
  }
  /* ---------- phone notifications (Web Push: functions/push.js -> sw.js) ---------- */
  var NOTIF_KINDS = [
    ['orders', 'New orders', 'Every paid order, with the total.'],
    ['payments', 'Card holds', 'A card hold ends in 2 days, or ended before it was charged.'],
    ['messages', 'Customer messages', 'The contact form and the ideas box.'],
    ['quotes', 'Big order requests', 'Weddings, businesses, parties.'],
    ['disputes', 'Payment disputes', 'A customer disputed a charge (there is a deadline).'],
    ['delivery', 'Delivery checks', 'Parcels that look stuck or late.'],
    ['taxes', 'Sales tax reminder', 'On the 12th: last month’s Georgia return, due the 20th.']
  ];
  var notif = { state: 'loading', prefs: null, sub: null, key: null, err: '' };
  function pushSupported() { return 'serviceWorker' in navigator && 'PushManager' in window && 'Notification' in window; }
  function isIOS() { return /iPhone|iPad|iPod/.test(navigator.userAgent) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1); }
  function deviceName() {
    var ua = navigator.userAgent;
    return /iPhone/.test(ua) ? 'iPhone' : /iPad/.test(ua) ? 'iPad' : /Android/.test(ua) ? 'Android' : /Mac/.test(ua) ? 'Mac' : /Windows/.test(ua) ? 'Windows' : 'Browser';
  }
  function b64ToBytes(s) {
    var b = atob(String(s).replace(/-/g, '+').replace(/_/g, '/') + '==='.slice((s.length + 3) % 4));
    var out = new Uint8Array(b.length);
    for (var i = 0; i < b.length; i++) out[i] = b.charCodeAt(i);
    return out;
  }
  function notifBody() {
    if (!pushSupported()) {
      if (isIOS() && !isInstalled()) return '<p class="small">On iPhone, notifications work in the <b>Hive Admin app</b>. Add it to your home screen first (steps below), open it from there, sign in and come back to Settings.</p>';
      return '<p class="small muted">This browser can’t show notifications. Use the Hive Admin app on your phone, or Chrome / Safari on a computer.</p>';
    }
    if (notif.state === 'loading') return '<p class="small muted">Checking this device…</p>';
    if (Notification.permission === 'denied') {
      return '<p class="small">Notifications are blocked for Hive Admin on this device. ' + (isIOS() ? 'Open the iPhone <b>Settings › Notifications › Hive Admin</b> and turn on <b>Allow Notifications</b>, then come back here.' : 'Allow them in the browser’s site settings, then come back here.') + '</p>';
    }
    if (notif.state !== 'on') {
      return '<p class="small">Get a notification on this ' + esc(deviceName()) + ' when an order comes in, a customer writes, a card hold is ending and more. Each phone turns it on once.</p>' +
        (notif.err ? '<p class="err">' + esc(notif.err) + '</p>' : '') +
        '<div class="row gap-top"><button class="btn btn-honey btn-sm" data-act="notifOn">' + icon('check') + 'Turn on notifications</button></div>';
    }
    return '<p class="small">' + icon('check') + ' Notifications are on for this ' + esc(deviceName()) + '. Choose what you want to hear about:</p>' +
      '<div class="stack gap-top" id="notif-kinds">' + NOTIF_KINDS.map(function (k) {
        return '<label class="row" style="gap:10px;align-items:flex-start"><input type="checkbox" data-notif="' + k[0] + '"' + (!notif.prefs || notif.prefs[k[0]] !== false ? ' checked' : '') + ' style="margin-top:3px">' +
          '<span><b>' + esc(k[1]) + '</b><br><span class="small muted">' + esc(k[2]) + '</span></span></label>';
      }).join('') + '</div>' +
      (notif.err ? '<p class="err">' + esc(notif.err) + '</p>' : '') +
      '<div class="row gap-top"><button class="btn btn-ghost btn-sm" data-act="notifTest">Send a test</button><button class="btn btn-ghost btn-sm" data-act="notifOff">Turn off on this device</button></div>';
  }
  function notifCard() { return '<section class="card" id="notif-card"><div class="card-head"><h2>Notifications</h2></div><div id="notif-body">' + notifBody() + '</div></section>'; }
  function paintNotif() {
    var b = document.getElementById('notif-body');
    if (!b) return;
    b.innerHTML = notifBody();
    Array.prototype.forEach.call(b.querySelectorAll('input[data-notif]'), function (cb) {
      cb.addEventListener('change', function () {
        var prefs = {};
        Array.prototype.forEach.call(b.querySelectorAll('input[data-notif]'), function (x) { prefs[x.getAttribute('data-notif')] = x.checked; });
        h.call('adminPush', { action: 'subscribe', subscription: notif.sub.toJSON(), prefs: prefs, device: deviceName() })
          .then(function (r) { notif.prefs = r.prefs; h.toast('Saved.'); })
          .catch(function (e) { cb.checked = !cb.checked; h.toast(h.friendlyError(e), true); });
      });
    });
  }
  function loadNotif() {
    if (!pushSupported()) return;
    navigator.serviceWorker.ready.then(function (reg) {
      return Promise.all([reg.pushManager.getSubscription(), notif.key ? notif.key : h.call('adminPush', { action: 'key' }).then(function (r) { return r.publicKey; })]);
    }).then(function (got) {
      notif.sub = got[0]; notif.key = got[1];
      if (!notif.sub) { notif.state = 'off'; paintNotif(); return; }
      return h.call('adminPush', { action: 'status', endpoint: notif.sub.endpoint }).then(function (r) {
        notif.state = r.subscribed && Notification.permission === 'granted' ? 'on' : 'off'; notif.prefs = r.prefs; paintNotif();
      });
    }).catch(function (e) { notif.state = 'off'; notif.err = h.friendlyError(e); paintNotif(); });
  }
  ACT.notifOn = function (btn) {
    notif.err = '';
    /* iPhone asks for permission only straight from the tap, so this comes first */
    var ask = Notification.requestPermission();
    h.busy(btn, true, 'Turning on…');
    Promise.resolve(ask).then(function (perm) {
      if (perm !== 'granted') throw new Error(perm === 'denied' ? 'Notifications were not allowed.' : 'Tap Allow when the phone asks.');
      return navigator.serviceWorker.ready;
    }).then(function (reg) {
      var key = notif.key ? Promise.resolve(notif.key) : h.call('adminPush', { action: 'key' }).then(function (r) { return (notif.key = r.publicKey); });
      return key.then(function (k) {
        return reg.pushManager.getSubscription().then(function (old) {
          return old || reg.pushManager.subscribe({ userVisibleOnly: true, applicationServerKey: b64ToBytes(k) });
        });
      });
    }).then(function (sub) {
      notif.sub = sub;
      return h.call('adminPush', { action: 'subscribe', subscription: sub.toJSON(), device: deviceName() });
    }).then(function (r) {
      notif.state = 'on'; notif.prefs = r.prefs; paintNotif();
      return h.call('adminPush', { action: 'test', endpoint: notif.sub.endpoint }).then(function () { h.toast('Notifications are on. A test is on its way.'); }, function () { h.toast('Notifications are on.'); });
    }).catch(function (e) {
      h.busy(btn, false); notif.err = e && e.message && !e.code ? e.message : h.friendlyError(e); paintNotif();
    });
  };
  ACT.notifTest = function (btn) {
    h.busy(btn, true, 'Sending…');
    h.call('adminPush', { action: 'test', endpoint: notif.sub && notif.sub.endpoint })
      .then(function () { h.busy(btn, false); h.toast('Sent. It should pop up in a few seconds.'); })
      .catch(function (e) { h.busy(btn, false); h.toast(h.friendlyError(e), true); });
  };
  ACT.notifOff = function (btn) {
    h.busy(btn, true, 'Turning off…');
    var sub = notif.sub;
    h.call('adminPush', { action: 'unsubscribe', endpoint: sub && sub.endpoint })
      .then(function () { return sub ? sub.unsubscribe() : null; })
      .then(function () { notif.state = 'off'; notif.sub = null; paintNotif(); h.toast('Notifications are off on this device.'); })
      .catch(function (e) { h.busy(btn, false); h.toast(h.friendlyError(e), true); });
  };

  /* "Install on your phone": the admin is a PWA (manifest.webmanifest + sw.js) */
  function isInstalled() {
    try { return window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone === true; } catch (e) { return false; }
  }
  function installCard() {
    var head = '<section class="card" id="install-card"><div class="card-head"><h2>Install on your phone</h2></div>';
    if (isInstalled()) return head + '<p class="small">' + icon('check') + ' You’re using the Hive Admin app. Orders, shipping and refunds work the same as on the computer.</p></section>';
    return head + '<p class="small">Put Hive Admin on your home screen and open it like an app: one tap to check new orders and add tracking numbers.</p>' +
      '<div class="row gap-top" id="install-now"' + (window.__hiveInstall ? '' : ' hidden') + '><button class="btn btn-honey btn-sm" data-act="installApp">' + icon('download') + 'Install Hive Admin</button></div>' +
      '<p class="small gap-top"><b>iPhone or iPad</b> (Safari)</p><ol class="install-steps"><li>Open this page in <b>Safari</b>.</li><li>Tap the <b>Share</b> button (square with an arrow).</li><li>Tap <b>Add to Home Screen</b>, then <b>Add</b>.</li></ol>' +
      '<p class="small gap-top"><b>Android</b> (Chrome)</p><ol class="install-steps"><li>Open this page in <b>Chrome</b>.</li><li>Tap the <b>⋮</b> menu.</li><li>Tap <b>Install app</b> (or <b>Add to Home screen</b>).</li></ol>' +
      '<p class="tiny muted gap-top">Sign in once in the app. It keeps only the screens on the phone; order details always load fresh and stay private.</p></section>';
  }
  ACT.installApp = function () {
    var ev = window.__hiveInstall;
    if (!ev) { h.toast('Use the steps below to add it to your home screen.'); return; }
    ev.prompt();
    (ev.userChoice || Promise.resolve({})).then(function (c) {
      window.__hiveInstall = null;
      if (c && c.outcome === 'accepted') h.toast('Installed! Look for Hive Admin on your home screen.');
      var b = document.getElementById('install-now'); if (b) b.hidden = true;
    });
  };
  document.addEventListener('hive-installable', function () { var b = document.getElementById('install-now'); if (b) b.hidden = false; });
  function themeText() { try { var t = localStorage.getItem('lhh-admin-theme') || 'auto'; return 'Theme: ' + t; } catch (e) { return 'Theme: auto'; } }
})();
