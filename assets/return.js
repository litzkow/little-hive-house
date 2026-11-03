/* Little Hive House: return.html, start a return (functions/returns.js). Needs site.js and store.js first.
   1. Find the order (number + email). 2. "Something's wrong" (photos, reprint or refund) or "I changed my mind"
   (ready-made designs: a prepaid USPS label with a QR code, the refund goes out when it reaches us).
   Everything is built with textContent (no HTML injection). */
(function () {
  var S = window.LHHStore, L = window.LHH;
  var $ = function (id) { return document.getElementById(id); };
  if (!S || !document.querySelector('[data-page="return"]')) return;
  if (!S.configured) { $('st-soon').hidden = false; return; }
  $('st-content').hidden = false;

  function h(tag, attrs) {
    var el = document.createElement(tag);
    if (attrs) for (var k in attrs) {
      if (attrs[k] == null || attrs[k] === false) continue;
      if (k === 'text') el.textContent = attrs[k];
      else if (k === 'class') el.className = attrs[k];
      else if (k.slice(0, 2) === 'on') el.addEventListener(k.slice(2), attrs[k]);
      else el.setAttribute(k, attrs[k] === true ? '' : attrs[k]);
    }
    (function add(list) { for (var i = 0; i < list.length; i++) { var c = list[i]; if (c == null || c === false) continue; if (Array.isArray(c)) add(c); else el.append(c); } })(Array.prototype.slice.call(arguments, 2));
    return el;
  }
  var money = function (n) { return '$' + (Number(n) || 0).toFixed(2); };
  function day(v) { var d = S.toDate(v); return d ? d.toLocaleDateString('en-US', { month: 'long', day: 'numeric' }) : ''; }
  function errText(e) {
    var c = String((e && e.code) || '').replace(/^functions\//, '');
    if (c === 'not-found') return 'We couldn’t find an order with that number and email. Check your confirmation email for both, or contact us and we’ll look it up.';
    return (e && e.message && !/^internal$/i.test(e.message)) ? e.message : S.message(e);
  }

  var form = $('ret-find'), msg = $('ret-msg'), out = $('ret-out');
  var who = null, data = null;
  var q = new URLSearchParams(location.search);
  if (q.get('number')) form.elements.number.value = q.get('number');
  if (q.get('email')) form.elements.email.value = q.get('email');
  function say(t) { msg.textContent = t || ''; msg.hidden = !t; }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var num = form.elements.number.value.trim().toUpperCase().replace(/\s+/g, ''), email = form.elements.email.value.trim();
    if (/^\d+$/.test(num)) num = 'LHH-' + num;
    if (!/^LHH-?\d{3,}$/.test(num)) { say('Order numbers look like LHH-1042. You’ll find yours in your confirmation email.'); return; }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) { say('Please enter the email you used for the order.'); return; }
    say('');
    who = { number: num.replace(/^LHH-?/, 'LHH-'), email: email };
    var b = form.querySelector('button'); b.disabled = true; b.textContent = 'Looking…';
    S.call('returnLookup', who).then(function (r) {
      b.disabled = false; b.textContent = 'Find my order';
      data = r; form.hidden = true;
      if (history.replaceState) history.replaceState(null, '', location.pathname);
      home();
    }).catch(function (er) { b.disabled = false; b.textContent = 'Find my order'; say(errText(er)); });
  });

  function show(nodes) { out.replaceChildren.apply(out, [].concat(nodes)); out.hidden = false; window.scrollTo({ top: out.getBoundingClientRect().top + scrollY - 90, behavior: 'smooth' }); }
  function back(to) { return h('button', { type: 'button', class: 'ret-back', onclick: to || home }, '‹ Back'); }

  /* ---------- the order: returns already started, and the two ways to start one ---------- */
  var STATUS = {
    requested: ['We’re looking at it', 'We reply within one business day.'],
    label_sent: ['Label ready', 'Drop it off with USPS. Your refund goes out when it reaches us.'],
    in_transit: ['On its way back', 'Your refund goes out as soon as it reaches us.'],
    refunded: ['Refunded', ''], reprinting: ['Reprint on the way', 'We email you the tracking when it ships.'],
    received: ['Received', ''], declined: ['Not accepted', 'We emailed you why.'], expired: ['Label not used', 'Nothing was charged.']
  };
  function returnCard(r) {
    var st = STATUS[r.status] || [r.status, ''];
    var what = r.lines.map(function (l) { return l.title + (l.qty > 1 ? ' × ' + l.qty : ''); }).join(', ');
    return h('div', { class: 'panel ret-card' },
      h('div', { class: 'ret-card-top' }, h('strong', { text: st[0] }), h('span', { class: 'muted', text: day(r.createdAt) })),
      h('p', { text: what }),
      st[1] ? h('p', { class: 'muted', text: r.refund ? 'Refunded ' + money(r.refund.amount) + ' on ' + day(r.refund.at) + '.' : st[1] }) : (r.refund ? h('p', { class: 'muted', text: money(r.refund.amount) + ' back to your card on ' + day(r.refund.at) + '.' }) : null),
      r.label && (r.status === 'label_sent') ? labelBox(r.label, r.estimate) : null);
  }
  function labelBox(lb, est) {
    return h('div', { class: 'ret-label' },
      lb.qr ? h('figure', { class: 'ret-qr' }, h('img', { src: lb.qr, alt: 'USPS return QR code', width: 200, height: 200 }),
        h('figcaption', { text: 'No printer? Show this at the Post Office counter or kiosk and they print the label for you. Most Post Offices can.' })) : null,
      h('div', { class: 'row' }, h('a', { class: 'btn ' + (lb.qr ? 'btn-ghost' : 'btn-honey') + ' btn-small', href: lb.url, target: '_blank', rel: 'noopener' }, lb.qr ? 'Or print the label' : 'Print your return label'),
        lb.trackUrl ? h('a', { class: 'btn btn-ghost btn-small', href: lb.trackUrl, target: '_blank', rel: 'noopener' }, 'Track it') : null),
      est ? h('p', { class: 'muted small', text: 'Your refund: ' + money(est.refund) + ' (' + money(est.value) + ' for the magnets − ' + money(est.labelCost) + ' return shipping).' }) : null);
  }
  function home() {
    var o = data.order, ls = data.lines.filter(function (l) { return l.left > 0; });
    var anyMind = ls.some(function (l) { return l.changeMind; });
    var nodes = [h('div', { class: 'ret-head' }, h('h2', { text: 'Order ' + o.number }), o.firstName ? h('span', { class: 'muted', text: 'Hi ' + o.firstName + '!' }) : null)];
    if (data.returns.length) nodes.push(h('h3', { class: 'ret-h3', text: 'Your returns' }), data.returns.map(returnCard));
    if (!data.window.shipped) nodes.push(h('div', { class: 'panel' }, h('p', { text: 'This order hasn’t shipped yet. To change or cancel it, write to us and we’ll take care of it.' }), h('div', { class: 'row' }, h('a', { class: 'btn btn-small', href: 'contact.html' }, 'Contact us'))));
    else if (!data.window.open) nodes.push(h('div', { class: 'panel' }, h('p', { text: 'The 30 days to start a return for this order have passed. If something is wrong, write to us and we’ll see what we can do.' }), h('div', { class: 'row' }, h('a', { class: 'btn btn-small', href: 'contact.html' }, 'Contact us'))));
    else if (!ls.length) nodes.push(h('p', { class: 'muted', text: 'Everything in this order is already in a return.' }));
    else {
      nodes.push(h('h3', { class: 'ret-h3', text: data.returns.length ? 'Start another return' : 'What happened?' }));
      nodes.push(h('div', { class: 'ret-choices' },
        h('button', { type: 'button', class: 'ret-choice', onclick: problem },
          h('strong', { text: 'Something’s wrong' }), h('span', { text: 'Arrived damaged, a printing problem or the wrong magnet. We reprint or refund it, and you keep the old one.' })),
        anyMind ? h('button', { type: 'button', class: 'ret-choice', onclick: mind },
          h('strong', { text: 'I changed my mind' }), h('span', { text: 'Send back unused ready-made designs with a prepaid USPS label. Return shipping comes out of the refund.' })) : null),
        h('p', { class: 'muted small', text: 'You can start a return until ' + day(data.window.endsAt) + '.' }));
    }
    show(nodes);
  }

  /* ---------- choosing magnets ---------- */
  function picker(list, onChange) {
    var qty = {};
    var box = h('div', { class: 'ret-pick' }, list.map(function (l) {
      qty[l.index] = 0;
      var n = h('output', { class: 'ret-n', text: '0' });
      function set(v) { qty[l.index] = Math.max(0, Math.min(l.left, v)); n.textContent = qty[l.index]; minus.disabled = !qty[l.index]; plus.disabled = qty[l.index] >= l.left; onChange(); }
      var minus = h('button', { type: 'button', class: 'ret-step', 'aria-label': 'One less ' + l.title, onclick: function () { set(qty[l.index] - 1); } }, '−');
      var plus = h('button', { type: 'button', class: 'ret-step', 'aria-label': 'One more ' + l.title, onclick: function () { set(qty[l.index] + 1); } }, '+');
      minus.disabled = true;
      var thumb = l.designId ? h('img', { class: 'ret-thumb', src: 'assets/email/thumbs/' + l.designId + '.jpg', alt: '', width: 48, height: 48, loading: 'lazy' }) : h('span', { class: 'ret-thumb ret-thumb-photo', 'aria-hidden': 'true' });
      return h('div', { class: 'ret-line' }, thumb,
        h('div', { class: 'ret-line-t' }, h('strong', { text: l.title }), h('span', { class: 'muted', text: (l.kind === 'design' ? '' : l.left + ' magnets · ') + money(l.valueEach) + ' each' })),
        h('div', { class: 'ret-qty' }, minus, n, plus));
    }));
    return { el: box, lines: function () { return list.filter(function (l) { return qty[l.index] > 0; }).map(function (l) { return { index: l.index, qty: qty[l.index] }; }); } };
  }

  /* ---------- something's wrong ---------- */
  function problem() {
    var ls = data.lines.filter(function (l) { return l.left > 0; });
    var photos = [], err = h('p', { class: 'msg err', role: 'alert', hidden: true });
    var send = h('button', { type: 'submit', class: 'btn btn-honey', disabled: true }, 'Send');
    var pk = picker(ls, ready);
    var thumbs = h('div', { class: 'ret-photos' });
    var file = h('input', { type: 'file', accept: 'image/*', id: 'ret-file', class: 'sr-only', multiple: true, onchange: function () {
      Array.prototype.slice.call(file.files).forEach(function (f) { if (photos.length < 3) photos.push(f); });
      file.value = ''; drawPhotos(); ready();
    } });
    function drawPhotos() {
      thumbs.replaceChildren.apply(thumbs, photos.map(function (f, i) {
        var u = URL.createObjectURL(f);
        return h('div', { class: 'ret-ph' }, h('img', { src: u, alt: 'Photo ' + (i + 1) }), h('button', { type: 'button', 'aria-label': 'Remove photo ' + (i + 1), onclick: function () { photos.splice(i, 1); drawPhotos(); ready(); } }, '×'));
      }).concat(photos.length < 3 ? [h('label', { class: 'ret-add', for: 'ret-file' }, h('span', { text: '+' }), photos.length ? 'Add another' : 'Add a photo')] : []));
    }
    drawPhotos();
    function ready() { send.disabled = !pk.lines().length || !photos.length; }
    var reason = h('select', { id: 'ret-reason', name: 'reason' },
      [['damaged', 'Arrived damaged'], ['misprint', 'Printing problem'], ['wrong_item', 'Wrong magnet'], ['missing', 'Something missing'], ['other', 'Something else']].map(function (r) { return h('option', { value: r[0], text: r[1] }); }));
    var note = h('textarea', { id: 'ret-note', name: 'note', maxlength: 1000, placeholder: 'Tell us what happened (optional)' });
    var wants = h('div', { class: 'ret-wants', role: 'radiogroup', 'aria-label': 'What would you like?' },
      h('label', { class: 'ret-radio' }, h('input', { type: 'radio', name: 'wants', value: 'reprint', checked: true }), h('span', null, h('strong', { text: 'A free reprint' }), h('small', { text: 'New magnets, shipped free' }))),
      h('label', { class: 'ret-radio' }, h('input', { type: 'radio', name: 'wants', value: 'refund' }), h('span', null, h('strong', { text: 'A refund' }), h('small', { text: 'Back to your card' }))));
    var f = h('form', { class: 'panel ret-form', novalidate: true, onsubmit: function (e) {
      e.preventDefault();
      err.hidden = true; send.disabled = true; send.textContent = 'Uploading photos…';
      var key = 'r' + Date.now().toString(36);
      S.ensureUser().then(function (u) {
        return Promise.all(photos.map(function (ph, i) { return small(ph).then(function (blob) { return S.upload('returns/' + u.uid + '/' + key + '/' + (i + 1) + '.jpg', blob, { contentType: 'image/jpeg' }); }); }));
      }).then(function (paths) {
        send.textContent = 'Sending…';
        return S.call('returnStart', { number: who.number, email: who.email, kind: 'problem', reason: reason.value, note: note.value,
          wants: f.querySelector('input[name="wants"]:checked').value, lines: pk.lines(), photos: paths });
      }).then(function (r) { done(r, 'problem'); })
        .catch(function (er) { err.textContent = errText(er); err.hidden = false; send.disabled = false; send.textContent = 'Send'; });
    } },
      h('h2', { text: 'Something’s wrong' }),
      h('div', { class: 'field' }, h('label', { for: 'ret-reason', text: 'What happened?' }), reason),
      h('div', { class: 'field' }, h('span', { class: 'field-label', text: 'Which magnets?' }), pk.el),
      h('div', { class: 'field' }, h('span', { class: 'field-label', text: 'Photos of the problem' }), file, thumbs, h('span', { class: 'field-hint', text: '1 to 3 photos. You keep the magnets, no need to send them back.' })),
      h('div', { class: 'field' }, h('span', { class: 'field-label', text: 'What would you like?' }), wants),
      h('div', { class: 'field' }, h('label', { for: 'ret-note', text: 'Anything else?' }), note),
      err, h('div', { class: 'row' }, send, back()));
    show(f);
  }
  /* phone photos are big: a 1600 px JPEG is plenty to see the problem */
  function small(file) {
    return new Promise(function (res) {
      var img = new Image(), u = URL.createObjectURL(file);
      img.onload = function () {
        var k = Math.min(1, 1600 / Math.max(img.naturalWidth, img.naturalHeight)), c = document.createElement('canvas');
        c.width = Math.round(img.naturalWidth * k); c.height = Math.round(img.naturalHeight * k);
        c.getContext('2d').drawImage(img, 0, 0, c.width, c.height);
        c.toBlob(function (b) { URL.revokeObjectURL(u); res(b || file); }, 'image/jpeg', 0.85);
      };
      img.onerror = function () { URL.revokeObjectURL(u); res(file); };
      img.src = u;
    });
  }

  /* ---------- changed my mind ---------- */
  function mind() {
    var ls = data.lines.filter(function (l) { return l.left > 0 && l.changeMind; });
    var err = h('p', { class: 'msg err', role: 'alert', hidden: true });
    var go = h('button', { type: 'submit', class: 'btn btn-honey', disabled: true }, 'See my refund');
    var sum = h('div', { class: 'ret-sum', hidden: true });
    var quoted = null;
    var unused = h('input', { type: 'checkbox', id: 'ret-unused', onchange: ready });
    var pk = picker(ls, function () { quoted = null; sum.hidden = true; go.textContent = 'See my refund'; ready(); });
    function ready() { go.disabled = !pk.lines().length || !unused.checked; }
    var f = h('form', { class: 'panel ret-form', novalidate: true, onsubmit: function (e) {
      e.preventDefault();
      err.hidden = true; go.disabled = true;
      if (!quoted) {
        go.textContent = 'Checking the return shipping…';
        S.call('returnQuote', { number: who.number, email: who.email, lines: pk.lines() }).then(function (qr) {
          quoted = qr;
          sum.replaceChildren.apply(sum, [
            h('div', null, h('span', { text: 'Magnets' }), h('span', { text: money(qr.value) })),
            h('div', null, h('span', { text: 'USPS return shipping' }), h('span', { text: '− ' + money(qr.labelCost) })),
            h('div', { class: 'ret-sum-total' }, h('span', { text: 'Your refund' }), h('span', { text: money(qr.refund) })),
            qr.refund <= 0 ? h('p', { class: 'muted small', text: 'Return shipping costs as much as these magnets, so there would be nothing left to refund.' }) : null].filter(Boolean));
          sum.hidden = false;
          go.textContent = 'Get my return label'; go.disabled = qr.refund <= 0;
        }).catch(function (er) { err.textContent = errText(er); err.hidden = false; go.textContent = 'See my refund'; ready(); });
        return;
      }
      go.textContent = 'Making your label…';
      S.call('returnStart', { number: who.number, email: who.email, kind: 'changed_mind', lines: pk.lines(), unused: true })
        .then(function (r) { done(r, 'mind'); })
        .catch(function (er) { err.textContent = errText(er); err.hidden = false; go.textContent = 'Get my return label'; go.disabled = false; });
    } },
      h('h2', { text: 'Send back ready-made designs' }),
      h('p', { class: 'muted', text: 'Photo magnets and custom packages are made just for you, so they can’t come back for a change of mind.' }),
      h('div', { class: 'field' }, h('span', { class: 'field-label', text: 'Which magnets?' }), pk.el),
      h('label', { class: 'check' }, unused, h('span', { text: 'They’re unused and still in their packaging.' })),
      sum, err, h('div', { class: 'row' }, go, back()));
    show(f);
  }

  function done(r, kind) {
    var nodes = [];
    if (kind === 'mind') {
      nodes.push(h('div', { class: 'panel ret-done' }, h('h2', { text: 'Your return label is ready' }),
        h('p', { text: 'We also emailed it to you. Pack the magnets in any envelope and drop it off with USPS.' }),
        labelBox(r.label, r.estimate),
        h('ol', { class: 'ret-steps' }, h('li', { text: 'Pack the magnets and seal the envelope.' }),
          h('li', { text: r.label && r.label.qr ? 'Show the QR code at a Post Office, or tape the printed label on and drop it in any USPS mailbox.' : 'Tape the label on and drop it at a Post Office or in any USPS mailbox.' }),
          h('li', { text: 'When it reaches us, your refund goes back to your card by itself. We email you when it does.' }))));
    } else {
      nodes.push(h('div', { class: 'panel ret-done' }, h('h2', { text: 'Thanks, we got it' }),
        h('p', { text: 'We’ll look at your photos and reply by email within one business day. You don’t need to send anything back.' })));
    }
    nodes.push(h('div', { class: 'row' }, h('a', { class: 'btn btn-ghost btn-small', href: 'shop.html' }, 'Back to the shop')));
    show(nodes);
  }
})();
