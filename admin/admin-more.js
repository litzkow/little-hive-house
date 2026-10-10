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
    ['Profit', 'profit', 'money'], ['Margin', 'margin', 'pct'], ['ROI', 'roi', 'pct'], ['Avg order', 'aov', 'money'], ['Repeat customers', 'repeatRate', 'pct']
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
      ['Shipping labels', -m.labels, ''],
      ['Product costs', -m.productCosts, h.int(m.magnets) + ' magnets × ' + money(S.settings.magnetUnitCost) + ' + ' + money(S.settings.packagingCost) + ' packaging per order'],
      ['Fixed costs', -m.fixedCosts, money(S.settings.monthlyFixedCosts) + ' a month'],
      ['Profit', m.profit, (m.margin == null ? '' : h.pct(m.margin) + ' margin') + (m.roi == null ? '' : ' · ' + h.pct(m.roi) + ' return on costs'), 'sum big']
    ];
    var topReason = reasons[0];
    var html = head('Reports', 'Reports', esc(period),
      '<label><span class="sr">Month</span><select class="input" id="r-month" style="width:auto">' + months.map(function (k) {
        return '<option value="' + k + '"' + (k === u.month ? ' selected' : '') + '>' + esc(R.monthLabel(k, true)) + '</option>';
      }).join('') + '</select></label>' +
      '<div class="seg" role="group" aria-label="Period"><button type="button" data-act="rscope" data-scope="month" aria-pressed="' + (u.scope === 'month') + '">Month</button>' +
      '<button type="button" data-act="rscope" data-scope="year" aria-pressed="' + (u.scope === 'year') + '">12 months</button></div>' +
      '<button class="btn btn-ghost btn-sm" data-act="reportCsv">' + icon('download') + 'CSV</button>') +
      '<div class="tiles">' +
      h.tile('Net sales', h.signedMoney(m.netSales), delta(m.netSales, prev && prev.netSales, true) || h.plural(m.orders, 'order'), true) +
      h.tile('Profit', '<span class="' + (m.profit < 0 ? 'neg' : '') + '">' + h.signedMoney(m.profit) + '</span>', m.margin == null ? 'No sales' : h.pct(m.margin) + ' margin · ROI ' + h.pct(m.roi)) +
      h.tile('Orders', h.int(m.orders), 'Avg order ' + money(m.aov)) +
      h.tile('Magnets sold', h.int(m.magnets), m.orders ? (m.magnets / m.orders).toFixed(1) + ' per order' : '') +
      h.tile('Refunds', '<span class="' + (m.refunds ? 'neg' : '') + '">' + money(m.refunds) + '</span>', h.plural(m.refundCount, 'refund')) +
      h.tile('Repeat customers', h.pct(m.repeatRate), h.int(m.returningCustomers || 0) + ' of ' + h.plural(m.customers || 0, 'customer')) +
      '</div>' + estNote +
      '<div class="two"><section class="card"><div class="card-head"><div><h2>Where the money went</h2><p class="sub">' + esc(period) + '</p></div></div><table class="pl">' + pl.map(function (x) {
        return '<tr class="' + (x[3] || '') + '"><td>' + esc(x[0]) + (x[2] ? '<span class="why">' + esc(x[2]) + '</span>' : '') + '</td><td class="' + (x[1] < 0 && /sum/.test(x[3] || '') ? 'neg' : '') + '">' + h.signedMoney(x[1]) + '</td></tr>';
      }).join('') + '</table></section>' +
      '<section class="card"><div class="card-head"><div><h2>Refunds by reason</h2><p class="sub">' + esc(period) + '</p></div></div>' +
      (reasons.length ? (topReason ? '<div class="callout">' + icon('info') + '<p class="small"><b>Top reason: ' + esc(topReason.label) + '</b> · ' + h.plural(topReason.count, 'refund') + ', ' + money(topReason.amount) +
        (m.orders ? ' (' + h.pct(topReason.count / Math.max(1, m.orders) * 100) + ' of orders)' : '') + '.' + adviceFor(topReason.reason) + '</p></div>' : '') +
        h.hbars(reasons.map(function (x) { return { label: x.label, sub: h.plural(x.count, 'refund'), value: x.amount, valueText: money(x.amount) }; }))
        : '<div class="empty">' + icon('check') + '<b>No refunds</b>Nothing went back to customers in this period.</div>') + '</section></div>' +
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
      '<section class="card flush gap-top"><div class="card-head"><div><h2>Month by month</h2><p class="sub">Swipe sideways on a phone</p></div><button class="btn btn-ghost btn-sm" data-act="reportCsv">' + icon('download') + 'CSV</button></div>' +
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
    var html = head('Customers', 'Customers', 'Everyone who has paid for an order', '<button class="btn btn-ghost btn-sm" data-act="custCsv">' + icon('download') + 'Export CSV</button>') +
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

  /* ====================================================================== MESSAGES (contact form + quote requests) */
  var QUOTE_SKIP = { id: 1, name: 1, email: 1, createdAt: 1, at: 1, message: 1, details: 1, status: 1, uid: 1 };
  function prettyKey(k) { return k.replace(/([a-z])([A-Z])/g, '$1 $2').replace(/[_-]/g, ' ').replace(/^\w/, function (c) { return c.toUpperCase(); }); }
  V.messages = function () {
    var a = need('messages'), b = need('quotes');
    if (!a || !b) return { title: 'Messages', html: head('Inbox', 'Messages') + loading('Loading messages…') };
    var tab = S.ui.messages;
    var list = tab === 'quotes' ? S.quotes : S.messages;
    var html = head('Inbox', 'Messages', 'From the contact form and the big-order quote form. Reply by email.') + errBox('messages') + errBox('quotes') +
      '<nav class="tabs">' + [['messages', 'Contact form', S.messages.length], ['quotes', 'Quote requests', S.quotes.length]].map(function (t) {
        return '<button type="button" data-act="msgTab" data-tab="' + t[0] + '"' + (tab === t[0] ? ' aria-current="true"' : '') + '>' + t[1] + '<span class="n">' + t[2] + '</span></button>';
      }).join('') + '</nav>' +
      (list.length ? '<div class="feed">' + list.map(function (m) {
        var when = m.createdAt || m.at;
        var subj = tab === 'quotes' ? 'Your Little Hive House quote' : 'Re: your message to Little Hive House';
        var extra = Object.keys(m).filter(function (k) { return !QUOTE_SKIP[k] && k !== 'topic' && m[k] != null && m[k] !== '' && typeof m[k] !== 'object'; });
        var body = m.message || m.details || '';
        var qty = m.quantity || m.qty;
        var linkQ = tab === 'quotes' ? h.qs({ email: m.email, magnets: qty || '', title: [(qty ? qty + ' ' : '') + (m.package || m.occasion || 'custom') + ' magnets', m.name ? '— ' + m.name : ''].join(' ') }) : '';
        return '<article class="msg"><header><b>' + esc(m.name || m.email || 'Someone') + '</b><time title="' + esc(h.fmtDT(when)) + '">' + esc(h.ago(when)) + '</time></header>' +
          '<p class="meta">' + (m.email ? '<a href="mailto:' + esc(m.email) + '">' + esc(m.email) + '</a>' : '') + (m.topic ? '<span class="badge quiet">' + esc(m.topic) + '</span>' : '') + '</p>' +
          (body ? '<p class="body">' + esc(body) + '</p>' : '') +
          (extra.length ? '<dl class="kv small">' + extra.map(function (k) { return '<dt>' + esc(prettyKey(k)) + '</dt><dd>' + esc(m[k]) + '</dd>'; }).join('') + '</dl>' : '') +
          '<div class="acts">' + (m.email ? '<a class="btn btn-ghost btn-sm" href="mailto:' + esc(m.email) + '?subject=' + encodeURIComponent(subj) + '">' + icon('mail') + 'Reply</a>' : '') +
          (tab === 'quotes' ? '<a class="btn btn-ghost btn-sm" href="#links' + linkQ + '">' + icon('links') + 'Send payment link</a>' : '') + '</div></article>';
      }).join('') + '</div>' : '<div class="card"><div class="empty">' + icon('messages') + '<b>Inbox zero</b>' + (tab === 'quotes' ? 'Quote requests from the Big orders page land here.' : 'Messages from the contact form land here.') + '</div></div>');
    return { title: 'Messages', html: html };
  };
  ACT.msgTab = function (el) { S.ui.messages = el.getAttribute('data-tab'); h.route(); };

  /* ====================================================================== SUBSCRIBERS */
  V.subscribers = function () {
    if (!need('subscribers')) return { title: 'Subscribers', html: head('Subscribers', 'Subscribers') + loading('Loading subscribers…') };
    var all = S.subscribers.filter(function (s) { return s.email && !s.unsubscribed; }), u = S.ui.subscribers;
    var gone = S.subscribers.filter(function (s) { return s.email && s.unsubscribed; }).length;
    var mk = R.monthRange(R.monthKey(Date.now()));
    var month = all.filter(function (s) { var t = R.toMs(s.at || s.createdAt); return t >= mk.from && t < mk.to; }).length;
    var sources = {};
    all.forEach(function (s) { var k = s.source || 'site'; sources[k] = (sources[k] || 0) + 1; });
    var html = head('Subscribers', 'Subscribers', 'People who asked for news and deals', '<button class="btn btn-ghost btn-sm" data-act="subCsv">' + icon('download') + 'Export CSV</button>') + errBox('subscribers') +
      '<div class="tiles">' + h.tile('Subscribers', h.int(all.length), gone ? h.int(gone) + ' unsubscribed (not listed)' : '', true) + h.tile('New this month', h.int(month), '') +
      h.tile('Top source', esc(Object.keys(sources).sort(function (a, b) { return sources[b] - sources[a]; })[0] || '—'), '') + '</div>' +
      '<div class="filters"><label class="search"><span class="sr">Search</span>' + icon('search') + '<input class="input" type="search" id="s-q" placeholder="Search emails" value="' + esc(u.q) + '"></label></div>' +
      '<section class="card flush" id="s-list"></section>' +
      '<p class="tiny faint gap-top">Export the CSV and import it in your email tool (Mailchimp, Kit…). Every marketing email must include the unsubscribe link.</p>';
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

  /* ====================================================================== SETTINGS */
  var FIELDS = [
    ['magnetUnitCost', 'Cost of one magnet', 'money', 'Paper, ink, magnet sheet and lamination for one 2 × 2 in magnet. Add up a pack of supplies and divide by how many magnets it makes.'],
    ['packagingCost', 'Packaging per order', 'money', 'Envelope or mailer, backing card, thank-you card and tape for one order.'],
    ['defaultLabelCost', 'Usual shipping label', 'money', 'Pre-filled when you ship, and used in reports for shipped orders without a label cost.'],
    ['stripePct', 'Stripe fee (percent)', 'pct', 'Stripe’s standard US card fee is 2.9% + 30¢. Only used when Stripe didn’t send the real fee.'],
    ['stripeFixed', 'Stripe fee (fixed)', 'money', 'The fixed part of the Stripe fee per payment.'],
    ['monthlyFixedCosts', 'Monthly fixed costs', 'money', 'Things you pay every month no matter how much you sell: website, Etsy plan, printer lease, software. Subtracted from each month’s profit.']
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
      installCard() +
      '<section class="card"><div class="card-head"><h2>Printing</h2></div><p class="small muted">Print sheets are made on the computer with <code>python3 tools/print_sheet.py</code>. Every order page shows the exact command, and its photo ZIP includes the frame list the tool reads.</p></section></div></div>';
    return {
      title: 'Settings', html: html, after: function () {
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
            S.settings = R.settingsWithDefaults(out); h.busy(btn, false); h.toast('Saved. Reports are updated.');
          }).catch(function (e) { h.busy(btn, false); err.textContent = h.friendlyError(e); err.hidden = false; });
        });
      }
    };
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
