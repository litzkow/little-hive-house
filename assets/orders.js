/* Little Hive House: order pages. Needs site.js and store.js first.
   orders.html (my orders), order.html?id= (detail), track.html (guest tracking), thank-you.html (after Stripe).
   Also exposes window.LHHOrders.card(order) for the account page. Everything is built with textContent (no HTML injection). */
(function () {
  var S = window.LHHStore, L = window.LHH;
  var $ = function (id) { return document.getElementById(id); };
  var main = document.querySelector('[data-page]');
  var PAGE = main ? main.getAttribute('data-page') : '';
  var BASE = S.base;
  var SUPPORT = S.support;
  var COLS = window.LHH_COLS || {};   /* collection slug → name (written by tools/store_pages.py) */
  function colName(c) { return COLS[c] || c || ''; }
  function frameName(id) { return !id || id === 'none' ? 'No border' : String(id).replace(/-/g, ' ').replace(/^./, function (c) { return c.toUpperCase(); }); }

  /* ---------- tiny DOM helper ---------- */
  function h(tag, attrs) {
    var el = document.createElement(tag);
    if (attrs) for (var k in attrs) {
      if (attrs[k] == null || attrs[k] === false) continue;
      if (k === 'text') el.textContent = attrs[k];
      else if (k === 'class') el.className = attrs[k];
      else if (k.slice(0, 2) === 'on') el.addEventListener(k.slice(2), attrs[k]);
      else el.setAttribute(k, attrs[k] === true ? '' : attrs[k]);
    }
    (function add(list) {
      for (var i = 0; i < list.length; i++) {
        var c = list[i];
        if (c == null || c === false) continue;
        if (Array.isArray(c)) add(c); else el.append(c);
      }
    })(Array.prototype.slice.call(arguments, 2));
    return el;
  }
  function svg(markup) { var t = document.createElement('span'); t.className = 'othumb-art'; t.innerHTML = markup; return t; }
  var money = function (n) { n = Number(n) || 0; return (n < 0 ? '−' : '') + '$' + Math.abs(n).toFixed(2); };
  function day(v, opts) { var d = S.toDate(v); return d ? d.toLocaleDateString('en-US', opts || { month: 'short', day: 'numeric', year: 'numeric' }) : ''; }
  function dayShort(v) { return day(v, { month: 'short', day: 'numeric' }); }

  /* ---------- statuses ---------- */
  var STATUS = {
    pending: ['Awaiting payment', 'wait'], paid: ['Order received', 'new'], in_production: ['Being made', 'make'],
    shipped: ['On its way', 'ship'], delivered: ['Delivered', 'done'], canceled: ['Canceled', 'off'],
    refunded: ['Refunded', 'off'], partially_refunded: ['Partly refunded', 'part']
  };
  function chip(status) { var s = STATUS[status] || [status || 'Unknown', 'wait']; return h('span', { class: 'ost ost-' + s[1], text: s[0] }); }
  var STEPS = [['paid', 'Order received'], ['in_production', 'Being made'], ['shipped', 'Shipped'], ['delivered', 'Delivered']];
  function stepOf(o) {
    var f = o.fulfillment || {};
    if (o.status === 'delivered' || f.deliveredAt) return 3;
    if (o.status === 'shipped' || f.shippedAt) return 2;
    if (o.status === 'in_production' || (o.timeline || []).some(function (t) { return t.status === 'in_production'; })) return 1;
    return 0;
  }
  function stepDate(o, k) {
    var f = o.fulfillment || {};
    var hit = (o.timeline || []).filter(function (t) { return t.status === STEPS[k][0]; })[0];
    if (hit) return hit.at;
    return [o.paidAt || o.createdAt, null, f.shippedAt, f.deliveredAt][k];
  }

  /* ---------- items ---------- */
  var PHOTO_ART = '<svg viewBox="0 0 60 60" aria-hidden="true"><rect width="60" height="60" fill="#C9DDE8"/><circle cx="42" cy="18" r="7" fill="#5C8FB0" opacity=".7"/><path d="M0 50 L18 30 L30 42 L40 34 L60 52 L60 60 L0 60 Z" fill="#5C8FB0"/></svg>';
  var HIVE_ART = '<svg viewBox="0 0 60 60" aria-hidden="true"><rect width="60" height="60" fill="#F9D88A"/><g fill="#F2A81D" stroke="#2B2118" stroke-width="1.6"><path d="M30 10l8.7 5v10L30 30l-8.7-5V15z"/><path d="M20.5 26l8.7 5v10l-8.7 5-8.7-5V31z" fill="#FFF6E5"/><path d="M39.5 26l8.7 5v10l-8.7 5-8.7-5V31z"/></g></svg>';
  function magnets(it) {
    var q = it.qty || 1;
    if (it.kind === 'photos') return (it.packSize || 0) * q;
    if (it.kind === 'package') return (it.size || 0) * q;
    if (it.kind === 'design') return q;
    return 0;
  }
  function itemInfo(it) {
    var q = it.qty || 1;
    if (it.kind === 'design') {
      return { title: (it.title || it.id) + ' magnet', detail: [colName(it.collection), '2 × 2 in'].filter(Boolean).join(' · '),
               qty: q, amount: (it.unit != null ? it.unit : 5) * q, art: 'img', src: BASE + 'assets/art/' + it.id + '.webp' };
    }
    if (it.kind === 'photos') {
      var n = it.photoCount || (it.photos || it.frames || []).length;
      return { title: 'Custom photo magnets', detail: it.packSize + ' magnets' + (n ? ' · ' + n + ' photo' + (n > 1 ? 's' : '') : ''), qty: q,
               amount: (it.price || 0) * q, art: PHOTO_ART };
    }
    if (it.kind === 'package') {
      return { title: it.title || 'Big order package', detail: 'Custom design, with a proof before we print', qty: q, amount: (it.price || 0) * q, art: HIVE_ART };
    }
    return { title: it.title || 'Custom order', detail: 'Made for you', qty: 1, amount: it.amount || it.price || 0, art: HIVE_ART };
  }
  function thumb(it, cls) {
    var i = itemInfo(it);
    if (i.art === 'img') {
      var img = h('img', { src: i.src, alt: '', width: 120, height: 120, loading: 'lazy', decoding: 'async' });
      img.addEventListener('error', function () { img.replaceWith(svg(HIVE_ART)); });
      return h('span', { class: cls || 'othumb' }, img);
    }
    return h('span', { class: cls || 'othumb' }, svg(i.art));
  }
  function itemsList(o) {
    return h('ul', { class: 'oitems' }, (o.items || []).map(function (it) {
      var i = itemInfo(it);
      return h('li', { class: 'oitem' },
        thumb(it),
        h('div', { class: 'oitem-main' }, h('strong', { text: i.title }), h('span', { text: i.detail + (i.qty > 1 ? ' · Qty ' + i.qty : '') }),
          it.kind === 'photos' && (it.photos || it.frames) ? h('span', { class: 'oitem-sub', text: framesSummary(it.photos || it.frames) }) : null),
        h('span', { class: 'oitem-amt', text: money(i.amount) }));
    }));
  }
  function framesSummary(photos) {
    var names = [];
    photos.forEach(function (p) { var n = p.frameName || frameName(p.frame); if (n && names.indexOf(n) < 0) names.push(n); });
    if (!names.length) return '';
    return names.length === 1 ? 'Frame: ' + names[0] : names.length + ' different frames';
  }
  function count(o) { var n = (o.items || []).reduce(function (a, it) { return a + magnets(it); }, 0); return n ? n + (n === 1 ? ' magnet' : ' magnets') : ''; }

  /* ---------- list card (orders.html + account page) ---------- */
  function card(o) {
    var thumbs = (o.items || []).slice(0, 3).map(function (it) { return thumb(it, 'othumb sm'); });
    return h('li', null, h('a', { class: 'ocard', href: BASE + 'order.html?id=' + encodeURIComponent(o.id) },
      h('span', { class: 'ocard-thumbs', 'aria-hidden': 'true' }, thumbs),
      h('span', { class: 'ocard-main' },
        h('strong', { text: 'Order ' + (o.number || '') }),
        h('span', { text: [day(o.paidAt || o.createdAt), count(o)].filter(Boolean).join(' · ') })),
      h('span', { class: 'ocard-side' }, chip(o.status), h('strong', { class: 'ocard-total', text: money((o.pricing || {}).total) })),
      h('span', { class: 'ocard-go', 'aria-hidden': 'true', text: '›' })));
  }

  /* ---------- detail ---------- */
  function carrierName(c, f) { if (f && f.carrierName && f.carrierName !== 'Other') return f.carrierName; return { usps: 'USPS', ups: 'UPS', fedex: 'FedEx', dhl: 'DHL' }[String(c || '').toLowerCase()] || (c && c !== 'other' ? c : 'the carrier'); }
  /* automatic carrier tracking (trackShipments fills fulfillment.trackingStatus + events every 2 hours) */
  var LIVE = { pre_transit: ['Label created', 'wait'], in_transit: ['In transit', 'ship'], out_for_delivery: ['Out for delivery today', 'ofd'],
               delivered: ['Delivered', 'done'], exception: ['Delivery update', 'alert'] };
  function whenShort(v) { var d = S.toDate(v); return d ? d.toLocaleString('en-US', { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' }) : ''; }
  function liveTracking(o) {
    var f = o.fulfillment || {}, ev = (f.events || []).filter(function (e) { return e && (e.text || e.at); });
    var st = LIVE[f.trackingStatus];
    if (!st && !ev.length) return null;
    var box = h('div', { class: 'olive' });
    if (st) {
      box.append(h('p', { class: 'olive-status' }, h('span', { class: 'olive-dot is-' + st[1], 'aria-hidden': 'true' }), h('strong', { text: st[0] }),
        f.trackingDetail && o.status !== 'delivered' ? h('span', { class: 'olive-detail', text: f.trackingDetail }) : null));
    }
    var eta = f.estimatedDelivery && f.trackingStatus !== 'delivered' ? day(f.estimatedDelivery, { weekday: 'long', month: 'long', day: 'numeric' }) : '';
    var note = [eta ? 'Expected ' + eta : '', f.lastCheckedAt && o.status === 'shipped' ? 'Updated automatically, last checked ' + whenShort(f.lastCheckedAt) : ''].filter(Boolean).join(' · ');
    if (note) box.append(h('p', { class: 'olive-note', text: note }));
    if (ev.length) {
      var list = h('ol', { class: 'ohist oscans' }, ev.map(function (e) {
        var d = S.toDate(e.at);
        return h('li', null, h('time', { datetime: d ? d.toISOString() : null, text: d ? whenShort(d) : '' }),
          h('span', { text: e.text || '' }), e.location ? h('small', { class: 'muted', text: e.location }) : null);
      }));
      box.append(h('details', { class: 'oscans-wrap' }, h('summary', { text: 'Tracking history (' + ev.length + (ev.length === 1 ? ' scan)' : ' scans)') }), list));
    }
    return box;
  }
  function progressPanel(o) {
    var st = o.status, f = o.fulfillment || {};
    var panel = h('section', { class: 'panel oprog', 'aria-labelledby': 'oprog-h' });
    var ofd = st === 'shipped' && f.trackingStatus === 'out_for_delivery';
    var head = { paid: 'We have your order', in_production: 'We’re making your magnets', shipped: ofd ? 'Out for delivery today!' : 'Your order is on its way',
                 delivered: 'Delivered', canceled: 'This order was canceled', refunded: 'This order was refunded',
                 partially_refunded: 'Part of this order was refunded', pending: 'Waiting for payment' }[st] || 'Order status';
    var lead = {
      paid: 'We’ll start printing soon. Most orders ship within 3 to 5 business days, and we email you the tracking link when it ships.',
      in_production: 'Your magnets are being printed, pressed and packed by hand. We email you the tracking link when it ships.',
      shipped: ofd ? carrierName(f.carrier, f) + ' has your package out for delivery. Keep an eye on the porch!'
        : 'Your package is with ' + carrierName(f.carrier, f) + '.' + (f.shippedAt ? ' It shipped on ' + day(f.shippedAt, { month: 'long', day: 'numeric' }) + '.' : '') +
          (f.lastCheckedAt ? ' We’ll email you when it’s out for delivery and when it arrives.' : ''),
      delivered: (f.deliveredAt ? 'Delivered on ' + day(f.deliveredAt, { month: 'long', day: 'numeric' }) + '. ' : '') + 'We hope you love them!',
      canceled: 'Nothing was charged, or the full amount was refunded. Questions? We’re happy to help.',
      refunded: 'We refunded ' + money(o.refundedTotal || (o.pricing || {}).total) + '. Refunds take 5 to 10 business days to show on your statement.',
      partially_refunded: 'We refunded ' + money(o.refundedTotal) + '. Refunds take 5 to 10 business days to show on your statement.',
      pending: 'We haven’t received the payment for this order yet.'
    }[st] || '';
    panel.append(h('h2', { id: 'oprog-h', text: head }), lead ? h('p', { class: 'oprog-lead', text: lead }) : null);
    if (st !== 'canceled' && st !== 'pending' && st !== 'refunded') {
      var cur = stepOf(o);
      panel.append(h('ol', { class: 'ostep', 'aria-label': 'Order progress' }, STEPS.map(function (s, k) {
        var d = k <= cur ? dayShort(stepDate(o, k)) : '';
        var doneK = k < cur || (k === 3 && cur === 3);   /* delivered: the last step is done, not "in progress" */
        return h('li', { class: doneK ? 'is-done' : k === cur ? 'is-current' : '', 'aria-current': k === cur ? 'step' : null },
          h('span', { class: 'ostep-hex', 'aria-hidden': 'true' }),
          h('strong', { text: s[1] }),
          h('small', { text: d || (k > cur ? 'Coming up' : '') }),
          h('span', { class: 'visually-hidden', text: doneK ? ' (done)' : k === cur ? ' (current step)' : ' (not yet)' }));
      })));
    }
    if (f.tracking || f.url) {
      var box = h('div', { class: 'otrack' },
        h('div', null, h('span', { class: 'otrack-label', text: carrierName(f.carrier, f) + ' tracking number' }), h('strong', { class: 'otrack-num', text: f.tracking || '' })));
      if (f.url && /^https:\/\//.test(f.url)) box.append(h('a', { class: 'btn btn-honey btn-small', href: f.url, target: '_blank', rel: 'noopener' }, 'Track package', h('span', { class: 'visually-hidden', text: ' (opens ' + carrierName(f.carrier, f) + ' in a new tab)' })));
      panel.append(box);
      var live = liveTracking(o); if (live) panel.append(live);
    }
    return panel;
  }
  function summary(o) {
    var p = o.pricing || {};
    var rows = [['Subtotal', money(p.subtotal)]];
    if (p.bundleDiscount) rows.push(['3 designs for $12', money(-p.bundleDiscount), 'disc']);
    if (p.volumeDiscount) rows.push(['Big order' + (p.volumePct ? ', ' + p.volumePct + '% off' : ''), money(-p.volumeDiscount), 'disc']);
    if (p.promo && p.promo.amount) rows.push(['Code ' + (p.promo.code || ''), money(-p.promo.amount), 'disc']);
    rows.push(['Shipping', p.shipping ? money(p.shipping) : 'Free']);
    var dl = h('dl', { class: 'osum' }, rows.map(function (r) { return h('div', { class: r[2] || null }, h('dt', { text: r[0] }), h('dd', { text: r[1] })); }),
      h('div', { class: 'grand' }, h('dt', { text: 'Total' }), h('dd', { text: money(p.total) })));
    if (o.refundedTotal) dl.append(h('div', { class: 'disc' }, h('dt', { text: 'Refunded' }), h('dd', { text: money(-o.refundedTotal) })));
    return h('section', { class: 'panel', 'aria-labelledby': 'osum-h' }, h('h2', { id: 'osum-h', text: 'Summary' }), dl);
  }
  function shipTo(o) {
    var s = o.shipping || {}, a = s.address || o.shipTo || {};   /* shipTo: the public view only has city / state */
    var lines = [s.name, a.line1, a.line2, [a.city, [a.state, a.postal_code].filter(Boolean).join(' ')].filter(Boolean).join(', '), a.country && a.country !== 'US' ? a.country : '']
      .filter(Boolean);
    if (!lines.length && !o.giftMessage) return null;
    return h('section', { class: 'panel', 'aria-labelledby': 'oship-h' },
      h('h2', { id: 'oship-h', text: 'Shipping to' }),
      lines.length ? h('address', { class: 'oaddr' }, lines.map(function (l, i) { return [i ? h('br') : null, l]; })) : null,
      o.giftMessage ? h('div', { class: 'ogift' }, h('span', { class: 'otrack-label', text: 'Gift message' }), h('p', { text: '“' + o.giftMessage + '”' })) : null);
  }
  function history_(o) {
    var t = (o.timeline || []).slice().sort(function (a, b) { return (S.toDate(b.at) || 0) - (S.toDate(a.at) || 0); });
    if (!t.length) return null;
    return h('section', { class: 'panel', 'aria-labelledby': 'ohist-h' }, h('h2', { id: 'ohist-h', text: 'Order history' }),
      h('ol', { class: 'ohist' }, t.map(function (e) {
        var d = S.toDate(e.at);
        return h('li', null, h('time', { datetime: d ? d.toISOString() : null, text: d ? d.toLocaleString('en-US', { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' }) : '' }),
          h('span', { text: e.text || (STATUS[e.status] || [e.status])[0] }));
      })));
  }
  function buyAgain(o) {
    var added = 0, photos = false;
    (o.items || []).forEach(function (it) {
      if (it.kind === 'design') { L.addLine({ id: it.id, kind: 'design', name: (it.title || it.id) + ' magnet', detail: '2 × 2 in' + (it.collection ? ' · ' + colName(it.collection) : ''), price: 5, qty: it.qty || 1 }, true); added++; }
      else if (it.kind === 'package') { L.addLine({ id: it.id, kind: 'package', name: String(it.title || 'Big order package').replace(/, \d+ magnets$/, ''), count: it.size, price: it.price, qty: it.qty || 1, detail: it.size + ' magnets · we plan the design with you by email after checkout' }, true); added++; }
      else if (it.kind === 'photos') photos = true;
    });
    if (added) L.openCart();
    if (photos) L.toast(added ? 'Added to your cart. For photo magnets, add your photos again on the photo page.' : 'Photo magnets need your photos again. Opening the photo page…');
    if (photos && !added) setTimeout(function () { location.href = BASE + 'photo-magnets.html'; }, 1400);
  }
  function actions(o, mode) {
    var box = h('section', { class: 'panel oacts', 'aria-label': 'Order actions' });
    var canBuy = (o.items || []).some(function (it) { return it.kind === 'design' || it.kind === 'package' || it.kind === 'photos'; });
    if (canBuy) box.append(h('button', { type: 'button', class: 'btn btn-small', onclick: function () { buyAgain(o); } }, 'Buy again'));
    var reviewable = mode === 'account' && (o.status === 'delivered' || (o.status === 'partially_refunded' && (o.fulfillment || {}).deliveredAt)) &&
      (o.items || []).some(function (it) { return it.kind === 'design' || it.kind === 'package' || it.kind === 'photos'; });
    if (reviewable) box.append(h('button', { type: 'button', class: 'btn btn-ghost btn-small', onclick: function () { var r = $('oreview'); r.hidden = false; r.scrollIntoView({ behavior: 'smooth', block: 'start' }); var f = r.querySelector('input'); if (f) setTimeout(function () { f.focus({ preventScroll: true }); }, 350); } }, 'Leave a review'));
    box.append(h('a', { class: 'btn btn-ghost btn-small', href: BASE + 'contact.html?order=' + encodeURIComponent(o.number || '') + '&topic=order' }, 'Need help?'));
    return box;
  }
  function reviews(o) {
    var items = (o.items || []).filter(function (it) { return it.kind === 'design' || it.kind === 'package' || it.kind === 'photos'; });
    var sec = h('section', { class: 'panel', id: 'oreview', hidden: true, 'aria-labelledby': 'orev-h' },
      h('h2', { id: 'orev-h', text: 'How did we do?' }),
      h('p', { class: 'muted', text: 'Your review helps other shoppers and helps us make better magnets. We read every one.' }));
    items.forEach(function (it, n) {
      var i = itemInfo(it), id = 'rv' + n;
      var stars = h('fieldset', { class: 'stars' }, h('legend', { class: 'visually-hidden', text: 'Rating for ' + i.title }));
      [5, 4, 3, 2, 1].forEach(function (v) {
        stars.append(h('input', { type: 'radio', name: id, id: id + '-' + v, value: v }),
          h('label', { for: id + '-' + v, title: v + ' star' + (v > 1 ? 's' : '') }, h('span', { class: 'visually-hidden', text: v + ' star' + (v > 1 ? 's' : '') })));
      });
      var ta = h('textarea', { id: id + '-t', rows: 3, maxlength: 1000, placeholder: 'What did you like? How does it look on your fridge?' });
      var msg = h('p', { class: 'msg', role: 'status', hidden: true });
      var form = h('form', { class: 'rvform', novalidate: true },
        h('div', { class: 'rvhead' }, thumb(it, 'othumb sm'), h('strong', { text: i.title })),
        stars, h('label', { class: 'visually-hidden', for: id + '-t', text: 'Your review of ' + i.title }), ta,
        h('button', { type: 'submit', class: 'btn btn-small' }, 'Send review'), msg);
      form.addEventListener('submit', function (e) {
        e.preventDefault();
        var r = form.querySelector('input:checked');
        if (!r) { msg.className = 'msg err'; msg.textContent = 'Please choose 1 to 5 stars.'; msg.hidden = false; return; }
        var b = form.querySelector('button'); b.disabled = true; b.textContent = 'Sending…';
        S.call('submitReview', { orderId: o.id, designId: it.kind === 'photos' ? 'photo-magnets' : it.id, rating: Number(r.value), text: ta.value.trim() })
          .then(function () { form.replaceChildren(h('div', { class: 'rvhead' }, thumb(it, 'othumb sm'), h('strong', { text: i.title })), h('p', { class: 'msg ok', text: 'Thank you! Your review will appear on the site after a quick check.' })); })
          .catch(function (er) { b.disabled = false; b.textContent = 'Send review'; msg.className = 'msg err'; msg.textContent = S.message(er); msg.hidden = false; });
      });
      sec.append(form);
    });
    return sec;
  }
  function detail(o, mode) {
    var wrap = h('div', { class: 'odetail' });
    var mainCol = h('div', { class: 'ocol' }, progressPanel(o),
      h('section', { class: 'panel', 'aria-labelledby': 'oitems-h' }, h('h2', { id: 'oitems-h', text: 'Items' }), itemsList(o)));
    if (mode === 'account') mainCol.append(reviews(o));
    var side = h('div', { class: 'ocol side' }, summary(o), shipTo(o), actions(o, mode));
    wrap.append(mainCol, side);
    /* history: under the items on wide screens, after the summary on phones (see .odetail in site.css) */
    var hist = history_(o); if (hist) wrap.append(h('div', { class: 'ocol hist' }, hist));
    return wrap;
  }
  function headline(o) {
    var t = $('page-title'); if (t) t.textContent = 'Order ' + (o.number || '');
    var meta = $('order-meta');
    if (meta) { meta.replaceChildren(chip(o.status), h('span', { text: 'Placed ' + day(o.paidAt || o.createdAt, { month: 'long', day: 'numeric', year: 'numeric' }) })); meta.hidden = false; }
    var c = $('crumb-order'); if (c) c.textContent = o.number || 'Order';
    document.title = 'Order ' + (o.number || '') + ' · Little Hive House';
  }

  /* ---------- page states ---------- */
  function show(id) {
    ['st-loading', 'st-soon', 'st-signin', 'st-error', 'st-content'].forEach(function (k) { var el = $(k); if (el) el.hidden = k !== id; });
  }
  function fail(msg) { var el = $('st-error-msg'); if (el) el.textContent = msg; show('st-error'); }

  function pageOrders() {
    S.ready().then(function (r) {
      if (!S.isMember(r.user)) return show('st-signin');
      return S.myOrders().then(function (list) {
        var box = $('st-content'); box.replaceChildren();
        if (!list.length) {
          box.append(h('div', { class: 'panel empty-panel' }, h('h2', { text: 'No orders yet' }),
            h('p', { text: 'When you place an order while signed in, it shows up here with its tracking.' }),
            h('div', { class: 'row' }, h('a', { class: 'btn', href: BASE + 'shop.html' }, 'Shop all designs'), h('a', { class: 'btn btn-ghost', href: BASE + 'track.html' }, 'Track a guest order'))));
        } else box.append(h('ul', { class: 'olist' }, list.map(card)));
        show('st-content');
      });
    }).catch(function (e) { fail(S.message(e)); });
  }
  function pageOrder() {
    var id = new URLSearchParams(location.search).get('id');
    if (!id) return fail('This link is missing the order. Open it from your orders list.');
    S.ready().then(function (r) {
      if (!S.isMember(r.user)) { var a = $('signin-link'); if (a) a.href = BASE + 'account.html?next=' + encodeURIComponent('order.html?id=' + id); return show('st-signin'); }
      return S.getOrder(id).then(function (o) {
        if (!o || o.status === 'pending') return fail('We couldn’t find this order in your account. If you ordered as a guest, track it with your order number and email.');
        headline(o);
        $('st-content').replaceChildren(detail(o, 'account'));
        show('st-content');
      });
    }).catch(function (e) { fail(S.message(e, 'order')); });
  }
  function pageTrack() {
    var form = $('track-form'), msg = $('track-msg'), out = $('track-result');
    var q = new URLSearchParams(location.search);
    /* thank-you page links use ?n=&e=, the order emails ?number=&email= */
    var qn = q.get('n') || q.get('number'), qe = q.get('e') || q.get('email');
    if (qn) form.elements.number.value = qn;
    if (qe) form.elements.email.value = qe;
    function say(t) { msg.textContent = t || ''; msg.hidden = !t; }
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var num = form.elements.number.value.trim().toUpperCase().replace(/\s+/g, ''), email = form.elements.email.value.trim();
      if (/^\d+$/.test(num)) num = 'LHH-' + num;
      if (!/^LHH-?\d{3,}$/.test(num)) { say('Order numbers look like LHH-1042. You’ll find yours in your confirmation email.'); form.elements.number.focus(); return; }
      num = num.replace(/^LHH-?/, 'LHH-');
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) { say('Please enter the email you used for the order.'); form.elements.email.focus(); return; }
      say('');
      var b = form.querySelector('button[type="submit"]'); b.disabled = true; b.textContent = 'Looking…';
      S.call('trackOrder', { number: num, email: email }).then(function (o) {
        b.disabled = false; b.textContent = 'Track order';
        if (!o) throw Object.assign(new Error('nf'), { code: 'not-found-plain' });
        out.replaceChildren(h('div', { class: 'otrack-head' }, h('h2', { text: 'Order ' + (o.number || num) }), chip(o.status),
          h('span', { class: 'muted', text: 'Placed ' + day(o.paidAt || o.createdAt, { month: 'long', day: 'numeric', year: 'numeric' }) })), detail(o, 'track'));
        out.hidden = false;
        if (history.replaceState) history.replaceState(null, '', location.pathname);   /* keep the email out of the address bar */
        out.querySelector('h2').setAttribute('tabindex', '-1'); out.querySelector('h2').focus();
      }).catch(function (er) {
        b.disabled = false; b.textContent = 'Track order';
        var c = String(er.code || '').replace(/^functions\//, '');
        say(c === 'not-found' || c === 'not-found-plain' || c === 'invalid-argument'
          ? 'We couldn’t find an order with that number and email. Check your confirmation email for both, or contact us and we’ll look it up.'
          : S.message(er));
        out.hidden = true;
      });
    });
  }
  function autoTrack() {
    var form = $('track-form');
    if (form && form.elements.number.value && form.elements.email.value && form.requestSubmit) form.requestSubmit();
  }
  function pageThanks() {
    var q = new URLSearchParams(location.search), orderId = q.get('order'), session = q.get('session');
    if (orderId) L.clear();   /* paid: the cart has become an order */
    if (!orderId || !session) { show('st-content'); return; }
    var tries = 0;
    function load() {
      return S.call('orderBySession', { orderId: orderId, sessionId: session }).then(function (o) {
        if (o && o.status === 'pending' && tries++ < 6) return new Promise(function (r) { setTimeout(r, 2500); }).then(load);
        return o;
      });
    }
    S.ready().then(load).then(function (o) {
      if (!o) { show('st-content'); return; }
      var first = o.firstName || String((o.shipping && o.shipping.name) || o.name || '').trim().split(/\s+/)[0];
      $('page-title').textContent = first ? 'Thank you, ' + first + '!' : 'Thank you!';
      var lede = $('thanks-lede');
      lede.textContent = o.status === 'pending' || !o.number
        ? 'Your payment went through and we’re finishing up your order. A confirmation email with your order number is on its way.'
        : 'Order ' + o.number + ' is confirmed. We emailed you a receipt, so keep it handy for tracking.';
      var hasPkg = (o.items || []).some(function (it) { return it.kind === 'package'; });
      if (hasPkg) $('thanks-pkg').hidden = false;
      var box = $('thanks-order');
      box.replaceChildren(h('section', { class: 'panel', 'aria-labelledby': 'oitems-h' },
        h('h2', { id: 'oitems-h', text: o.number ? 'Order ' + o.number : 'Your order' }), itemsList(o)), summary(o));
      box.hidden = false;
      S.onUser(function (u) {
        var cta = $('thanks-account');
        if (S.isMember(u)) { cta.hidden = true; var mine = $('thanks-mine'); if (mine && o.id) { mine.href = BASE + 'order.html?id=' + encodeURIComponent(o.id); } return; }
        cta.hidden = false;
        var mineBtn = $('thanks-mine'); if (mineBtn) mineBtn.hidden = true;   /* guests have no orders list */
        var a = $('thanks-create'); if (a && o.email) a.href = BASE + 'account.html?tab=create&email=' + encodeURIComponent(o.email);
        var t = $('thanks-track'); if (t && o.number) t.href = BASE + 'track.html?n=' + encodeURIComponent(o.number) + (o.email ? '&e=' + encodeURIComponent(o.email) : '');
      });
      show('st-content');
    }).catch(function () { show('st-content'); });
  }

  window.LHHOrders = { card: card, chip: chip };

  if (!PAGE || ['orders', 'order', 'track', 'thanks'].indexOf(PAGE) < 0) return;
  if (!S.configured) { if (PAGE === 'thanks') { if (new URLSearchParams(location.search).get('order')) L.clear(); show('st-content'); } else show('st-soon'); return; }
  if (PAGE === 'orders') pageOrders();
  else if (PAGE === 'order') pageOrder();
  else if (PAGE === 'track') { show('st-content'); pageTrack(); S.ready().then(autoTrack).catch(function () {}); }
  else if (PAGE === 'thanks') pageThanks();
})();
