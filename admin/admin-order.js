/* Little Hive House admin: one order. Fulfil (production → ship → delivered), refunds, status, emails, notes,
   the customer's photos drawn inside their frames, the photo ZIP for tools/print_sheet.py and the packing slip. */
(function () {
  'use strict';
  var A = window.LHHAdmin, S = A.S, R = A.R, h = A.h, ACT = A.ACT;
  var esc = h.esc, money = h.money, icon = h.icon;
  var current = null;   /* the order on screen */

  function rerender() { var y = window.scrollY; h.route(); window.scrollTo(0, y); }
  function run(btn, name, data, okMsg) {
    h.busy(btn, true);
    return h.call(name, data)
      .then(function (res) { return h.refreshOrder(data.orderId).then(function () { return res; }); })
      .then(function (res) { h.updateBadges(); h.toast(okMsg); rerender(); return res; })
      .catch(function (e) { h.busy(btn, false); h.toast(h.friendlyError(e), true); throw e; });
  }

  /* ---------------------------------------------------------------- frames + photos */
  function frameOf(id) {
    id = h.FRAME_ALIASES[id] || id || 'none';
    return (S.frames && S.frames[id]) || (S.frames && S.frames.none) || { id: 'none', name: 'No border', window: [0, 0, 600, 600], caption: null };
  }
  function capText(f, s) {
    if (!f.caption || !s) return '';
    s = String(s).trim().slice(0, f.caption.max || 40);
    return f.caption.upper ? s.toUpperCase() : s;
  }
  function textEl(c, s, y, size, ls, fam, style, weight, color, rot, fit) {
    return '<text x="' + (c.x + (ls ? ls / 2 : 0)) + '" y="' + y + '" text-anchor="middle" font-family="' + esc(fam) + '" font-style="' + esc(style || 'normal') +
      '" font-weight="' + esc(weight || 400) + '" font-size="' + size + '" fill="' + esc(color) + '"' + (ls ? ' letter-spacing="' + ls + '"' : '') +
      (rot ? ' transform="rotate(' + rot + ' ' + c.x + ' ' + y + ')"' : '') + (fit ? ' data-fit="1"' : '') + '>' + esc(s) + '</text>';
  }
  /* same drawing as the shop's photo builder (assets/custom.js) and tools/print_sheet.py: photo in the window, frame on top, caption last */
  function magnetSVG(url, f, caption) {
    var w = f.window, c = f.caption, s = capText(f, caption);
    var out = '<svg viewBox="0 0 600 600" data-frame="' + esc(f.id) + '" aria-hidden="true" focusable="false">';
    if (f.id !== 'none') out += '<rect width="600" height="600" fill="#FFFFFF"/>';
    out += url ? '<image href="' + esc(url) + '" x="' + w[0] + '" y="' + w[1] + '" width="' + w[2] + '" height="' + w[3] + '" preserveAspectRatio="xMidYMid slice"/>'
               : '<rect x="' + w[0] + '" y="' + w[1] + '" width="' + w[2] + '" height="' + w[3] + '" fill="#EDE3D1"/>';
    if (f.id !== 'none') out += '<image href="' + h.FRAMES_URL + esc(f.id) + '.svg" x="0" y="0" width="600" height="600"/>';
    if (c && s) {
      if (c.kicker) { var k = c.kicker; out += textEl({ x: c.x }, k.text, k.y, k.size, k.ls || 0, k.family, k.style, k.weight, k.color, 0, false); }
      out += textEl(c, s, c.y, c.size, c.ls, c.family, c.style, c.weight, c.color, c.rot, true);
    }
    return out + '</svg>';
  }
  function fitCaptions(root) {
    $$('text[data-fit]', root).forEach(function (t) {
      var svg = t.ownerSVGElement, f = svg && S.frames && S.frames[svg.getAttribute('data-frame')];
      if (!f || !f.caption) return;
      var c = f.caption, size = c.size;
      t.setAttribute('font-size', size);
      for (var i = 0; i < 4; i++) {
        var L; try { L = t.getComputedTextLength(); } catch (e) { return; }
        if (!L || L <= c.w) break;
        size = Math.max(c.min, Math.floor(size * c.w / L));
        t.setAttribute('font-size', size);
        if (size === c.min) break;
      }
    });
  }
  function $$(sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); }
  function photoItems(o) { return (o.items || []).filter(function (it) { return it.kind === 'photos'; }); }
  function normUrls(res) {
    var map = {}, list = [];
    /* adminPhotoUrls answers {packs: [{photos: [{n, path, frame, caption, url}]}]}; older shapes kept just in case */
    if (res && Array.isArray(res.packs)) { res = res.packs.reduce(function (a, pk) { return a.concat(pk.photos || []); }, []); }
    var d = res && (res.urls || res.photos || res.files || res);
    var take = function (x, key) {
      if (!x) return;
      var u = typeof x === 'string' ? x : (x.url || x.signedUrl || x.downloadUrl || x.href);
      if (!u) return;
      var p = typeof x === 'object' ? (x.path || x.name) : key;
      if (p) map[p] = u;
      list.push(u);
    };
    if (Array.isArray(d)) d.forEach(function (x) { take(x); });
    else if (d && typeof d === 'object') Object.keys(d).forEach(function (k) { take(d[k], k); });
    return { map: map, list: list };
  }
  function getUrls(o) {
    if (S.photoUrls[o.id] && Date.now() - S.photoUrls[o.id].at < 50 * 60 * 1000) return Promise.resolve(S.photoUrls[o.id]);
    return h.call('adminPhotoUrls', { orderId: o.id }).then(function (res) {
      var u = normUrls(res); u.at = Date.now(); S.photoUrls[o.id] = u; return u;
    });
  }
  function urlFor(u, p, globalIndex) { return (p.path && u.map[p.path]) || u.list[globalIndex] || ''; }
  function repeats(size, n, i) { if (!n || !size || size <= n) return 1; return Math.floor(size / n) + (i < size % n ? 1 : 0); }
  function fillPhotos() {
    var o = current; if (!o || !photoItems(o).length) return;
    var box = document.getElementById('photos-status');
    getUrls(o).then(function (u) {
      if (current !== o) return;
      $$('.mag[data-gi]').forEach(function (m) {
        var gi = Number(m.getAttribute('data-gi')), it = photoItems(o)[Number(m.getAttribute('data-pack'))];
        var p = it.photos[Number(m.getAttribute('data-j'))], url = urlFor(u, p, gi);
        var badge = m.querySelector('.n');
        m.innerHTML = url ? magnetSVG(url, frameOf(p.frame), p.caption) : '<div class="missing">Photo file not found</div>';
        if (badge) m.appendChild(badge);
      });
      if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { fitCaptions(document.getElementById('main')); });
      if (box) box.hidden = true;
    }).catch(function (e) {
      if (box) { box.hidden = false; box.className = 'err small'; box.textContent = 'Couldn’t load the photos: ' + h.friendlyError(e); }
    });
  }

  /* ---------------------------------------------------------------- the photo ZIP (photos + the frame list for print_sheet.py) */
  function folderOf(o) { return String(o.number || o.id).replace(/[^\w-]+/g, '-'); }
  function extOf(s) { var m = /\.(jpe?g|png|webp|heic|heif|gif)(?:$|[?#])/i.exec(String(s || '')); return m ? m[1].toLowerCase().replace('jpeg', 'jpg') : 'jpg'; }
  function pad(n) { return n < 10 ? '0' + n : String(n); }
  function photoPlan(o, u) {
    var packs = photoItems(o), entries = [], gi = 0;
    packs.forEach(function (it, pi) {
      (it.photos || []).forEach(function (p, j) {
        var url = urlFor(u, p, gi++);
        entries.push({ pack: pi, file: (packs.length > 1 ? 'pack' + (pi + 1) + '-' : '') + pad(j + 1) + '.' + extOf(p.path || url), url: url,
                       frame: frameOf(p.frame).id, caption: capText(frameOf(p.frame), p.caption) ? String(p.caption).trim() : '' });
      });
    });
    var json = { order: o.number || o.id, count: 0, photos: [] };
    packs.forEach(function (it, pi) {
      var es = entries.filter(function (e) { return e.pack === pi; });
      var size = R.num(it.packSize) * (it.qty == null ? 1 : R.num(it.qty)) || es.length;
      for (var k = 0; k < size && es.length; k++) { var e = es[k % es.length]; json.photos.push({ file: e.file, frame: e.frame, caption: e.caption }); }
    });
    json.count = json.photos.length;
    return { entries: entries, json: json };
  }
  function designArgs(o) {
    var out = [];
    (o.items || []).forEach(function (it) {
      if (it.kind !== 'design' || !it.id) return;
      for (var i = 0; i < Math.min(200, R.num(it.qty || 1)); i++) out.push(it.id);
    });
    return out;
  }
  function printCommand(o) {
    var f = folderOf(o), parts = ['python3 tools/print_sheet.py -o ~/Desktop/' + f + '.pdf'];
    if (photoItems(o).length) parts.push('--order ~/Downloads/' + f + '/' + f + '.json');
    var d = designArgs(o);
    for (var i = 0; i < d.length; i += 3) parts.push(d.slice(i, i + 3).join(' '));
    if (!photoItems(o).length && !d.length) {
      /* a package or custom quote: one artwork printed for every magnet */
      parts.push('--copies ' + Math.max(1, R.magnetsOf(o)) + ' ~/Downloads/' + f + '-art.png@none');
    }
    return parts.join(' \\\n  ');
  }
  ACT.zipPhotos = function (btn) {
    var o = current; if (!o) return;
    h.busy(btn, true, 'Preparing…');
    var folder = folderOf(o);
    getUrls(o).then(function (u) {
      var plan = photoPlan(o, u), n = 0;
      return Promise.all(plan.entries.map(function (e) {
        return fetch(e.url).then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.arrayBuffer(); })
          .then(function (b) { n++; btn.textContent = 'Downloading ' + n + '/' + plan.entries.length + '…'; return { e: e, b: b }; });
      })).then(function (got) {
        var files = got.map(function (g) { return { name: folder + '/' + g.e.file, data: new Uint8Array(g.b) }; });
        files.push({ name: folder + '/' + folder + '.json', data: JSON.stringify(plan.json, null, 2) + '\n' });
        files.push({ name: folder + '/HOW-TO-PRINT.txt', data: readme(o) });
        h.downloadBlob(new Blob([A.h.Z.zip(files)], { type: 'application/zip' }), folder + '-photos.zip');
        h.busy(btn, false);
        h.toast('Saved ' + folder + '-photos.zip (' + h.plural(plan.entries.length, 'photo') + ')');
      }, function () {
        /* the browser couldn't read the files (usually Storage CORS): offer them one by one */
        h.busy(btn, false);
        return h.dialog({
          title: 'Download the photos one by one',
          html: '<p class="muted small">Your browser couldn’t bundle the photos into a ZIP (the photo storage doesn’t allow it yet — see SETUP.md, “Storage CORS”). ' +
            'Open each photo and save it with the name shown, into a folder called <b>' + esc(folder) + '</b> in Downloads.</p>' +
            '<ol class="small" style="max-height:40vh;overflow:auto;margin:0;padding-left:22px">' + plan.entries.map(function (e) {
              return '<li><a href="' + esc(e.url) + '" target="_blank" rel="noopener" download="' + esc(e.file) + '">' + esc(e.file) + '</a> <span class="muted">· ' + esc(frameOf(e.frame).name) + '</span></li>';
            }).join('') + '</ol>',
          ok: 'Save the frame list (.json)', cancel: 'Close'
        }).then(function (ok) {
          if (ok) h.downloadBlob(new Blob([JSON.stringify(plan.json, null, 2) + '\n'], { type: 'application/json' }), folder + '.json');
        });
      });
    }).catch(function (e) { h.busy(btn, false); h.toast('Couldn’t get the photos: ' + h.friendlyError(e), true); });
  };
  function readme(o) {
    var f = folderOf(o);
    return 'Order ' + (o.number || o.id) + ' - ' + R.magnetsOf(o) + ' magnets\r\n\r\n' +
      '1. Unzip this file into your Downloads folder, so you have Downloads/' + f + '/' + f + '.json\r\n' +
      '2. Open Terminal in the little-hive-house folder and run:\r\n\r\n   ' + printCommand(o).replace(/\n/g, '\r\n   ') + '\r\n\r\n' +
      '3. Open ~/Desktop/' + f + '.pdf and print on US Letter at 100% ("Actual size", not "Fit to page").\r\n' +
      '   12 magnets per sheet. Cut on the crop marks: each tile is 2.5 in (2 in face + the wrap).\r\n\r\n' +
      f + '.json lists every magnet in print order with its frame and caption. Packs with fewer photos than magnets\r\n' +
      'repeat the photos in order to fill the pack (as promised on the shop).\r\n';
  }

  /* ---------------------------------------------------------------- packing slip */
  function addressLines(sh) {
    sh = sh || {}; var a = sh.address || {};
    return [sh.name, a.line1, a.line2, [a.city, [a.state, a.postal_code].filter(Boolean).join(' ')].filter(Boolean).join(', '),
      a.country && a.country !== 'US' ? a.country : ''].filter(Boolean);
  }
  ACT.slip = function () {
    var o = current; if (!o) return;
    var rows = (o.items || []).map(function (it) {
      if (it.kind === 'design') return [R.num(it.qty || 1), esc(it.title || it.id), esc(h.colName(R.collectionOf(it))) + ' · 2 × 2 in magnet'];
      if (it.kind === 'photos') {
        var ph = it.photos || [], size = R.num(it.packSize) * R.num(it.qty || 1);
        return [R.num(it.qty || 1), 'Photo magnets, ' + R.num(it.packSize) + '-pack', '<ol class="slip-photos">' + ph.map(function (p, j) {
          var f = frameOf(p.frame), c = capText(f, p.caption), rep = repeats(size, ph.length, j);
          return '<li>' + esc(f.name) + (c ? ' · “' + esc(c) + '”' : '') + (rep > 1 ? ' <b>×' + rep + '</b>' : '') + '</li>';
        }).join('') + '</ol>'];
      }
      if (it.kind === 'package') return [R.num(it.qty || 1), esc(it.title || it.id), R.num(it.size) + ' custom magnets'];
      return [1, esc(it.title || 'Custom order'), 'Made to order'];
    });
    var sh = addressLines(o.shipping);
    $('#slip').innerHTML =
      '<header><div class="brandline"><img src="../assets/favicon.svg" alt=""><div><b>Little Hive House</b>Handmade fridge magnets · littlehivehouse.com</div></div>' +
      '<div><h1>Packing slip</h1><div class="meta">Order <b>' + esc(o.number || o.id) + '</b><br>' + esc(h.fmtDate(R.orderDate(o), { year: true })) + '</div></div></header>' +
      '<div class="addrs"><div><h2>Ship to</h2>' + sh.map(esc).join('<br>') + '</div><div><h2>Questions?</h2>support@littlehivehouse.com<br>Reply to your order email any time.</div></div>' +
      '<table><thead><tr><th></th><th>Qty</th><th>Item</th></tr></thead><tbody>' + rows.map(function (r) {
        return '<tr><td class="box"><span></span></td><td class="q">' + r[0] + '</td><td><b>' + r[1] + '</b><div class="sub">' + r[2] + '</div></td></tr>';
      }).join('') + '</tbody></table>' +
      '<p style="margin-top:10px">' + h.plural(R.magnetsOf(o), 'magnet') + ' in this order.</p>' +
      (o.giftMessage ? '<div class="gift">' + esc(o.giftMessage) + '</div>' : '') +
      '<div class="thanks"><b>Thank you for shopping small!</b>Made by hand with love by Karina &amp; Thiago. Tag us when your fridge looks sweet.</div>';
    document.body.classList.add('printing-slip');
    var done = function () { document.body.classList.remove('printing-slip'); window.removeEventListener('afterprint', done); };
    window.addEventListener('afterprint', done);
    setTimeout(function () { window.print(); setTimeout(done, 1500); }, 50);
  };
  function $(sel) { return document.querySelector(sel); }

  /* ---------------------------------------------------------------- cards */
  function trackingLink(f) {
    if (f.url) return f.url;
    var base = A.h.TRACK_URL[f.carrier];
    return base && f.tracking ? base + encodeURIComponent(String(f.tracking).replace(/\s+/g, '')) : '';
  }
  function trackBox(o) {
    var f = o.fulfillment || {}, link = trackingLink(f);
    return '<div class="track">' + icon('truck') + '<div style="flex:1;min-width:0"><b>' + esc(h.carrierName(f.carrier) || 'Shipped') + (f.tracking ? ' · ' + esc(f.tracking) : '') + '</b>' +
      '<span>Shipped ' + esc(h.fmtDT(f.shippedAt)) + (f.labelCost != null && f.labelCost !== '' ? ' · label ' + money(f.labelCost) : '') +
      (R.toMs(f.deliveredAt) ? ' · delivered ' + esc(h.fmtDT(f.deliveredAt)) : '') + '</span></div>' +
      (link ? '<a class="btn btn-ghost btn-sm" href="' + esc(link) + '" target="_blank" rel="noopener">Track ' + icon('external') + '</a>' : '') + '</div>';
  }
  /* automatic tracking (functions/tracking.js fills these every 2 hours) */
  var LIVE = { pre_transit: ['Label created', 'chip'], in_transit: ['In transit', 'chip shipped'], out_for_delivery: ['Out for delivery', 'chip to_fulfil'],
    delivered: ['Delivered', 'chip delivered'], exception: ['Needs attention', 'chip refunded'] };
  var AUTO_CARRIERS = { usps: 1, ups: 1, fedex: 1, dhl: 1 };
  function liveBox(o) {
    var f = o.fulfillment || {}, ev = (f.events || []).filter(function (e) { return e && (e.text || e.at); });
    var st = LIVE[f.trackingStatus];
    var html = '';
    if (st || f.lastCheckedAt) {
      html += '<div class="live"><div class="row wrap">' + (st ? '<span class="' + st[1] + '">' + esc(st[0]) + '</span>' : '') +
        (f.trackingDetail ? '<span class="small">' + esc(f.trackingDetail) + '</span>' : '') + '</div>' +
        '<p class="tiny muted">' + (f.lastCheckedAt ? 'Checked automatically ' + esc(h.ago(f.lastCheckedAt)) : '') +
        (f.estimatedDelivery && f.trackingStatus !== 'delivered' ? ' · carrier expects ' + esc(h.fmtDate(f.estimatedDelivery)) : '') + '</p></div>';
    }
    if (f.trackingStoppedAt) {
      html += '<div class="callout">' + icon('info') + '<p class="small"><b>Automatic checks stopped</b> ' + esc(h.fmtDate(f.trackingStoppedAt)) + ': ' + esc(f.trackingStopReason || '') + '. Check the tracking link and mark it delivered, or contact the customer.</p></div>';
    } else if (!f.lastCheckedAt && R.stage(o) === 'shipped') {
      html += '<p class="tiny muted gap-top">' + (AUTO_CARRIERS[f.carrier] && f.tracking
        ? 'Automatic tracking checks every 2 hours and emails the customer “out for delivery” and “delivered” for you (USPS needs the USPS keys, UPS/FedEx/DHL the Shippo key; see SETUP).'
        : 'This carrier isn’t tracked automatically: mark it delivered when it arrives.') + '</p>';
    }
    if (ev.length) {
      html += '<details class="panel scans"><summary>Tracking history (' + ev.length + ')</summary><ol class="timeline">' + ev.map(function (e) {
        return '<li>' + esc(e.text || '') + (e.location ? ' <span class="muted">· ' + esc(e.location) + '</span>' : '') + '<time>' + esc(h.fmtDT(e.at)) + '</time></li>';
      }).join('') + '</ol></details>';
    }
    return html;
  }
  function shipForm(o, again) {
    var f = o.fulfillment || {};
    var carrier = again ? f.carrier || 'usps' : 'usps';
    return '<form class="stack" id="ship-form" novalidate>' +
      '<div class="grid-2"><label class="field"><span>Carrier</span><select class="input" name="carrier">' + A.h.CARRIERS.map(function (c) {
        return '<option value="' + c[0] + '"' + (c[0] === carrier ? ' selected' : '') + '>' + c[1] + '</option>';
      }).join('') + '</select></label>' +
      '<label class="field"><span>Label cost</span><span class="input-money"><input class="input" name="labelCost" type="number" inputmode="decimal" min="0" step="0.01" value="' +
        esc(again && f.labelCost != null ? f.labelCost : S.settings.defaultLabelCost.toFixed(2)) + '"></span></label></div>' +
      '<label class="field"><span>Tracking number</span><input class="input" name="tracking" autocomplete="off" autocapitalize="characters" spellcheck="false" placeholder="9400 1000 0000 0000 0000 00" value="' + esc(again ? f.tracking || '' : '') + '"></label>' +
      '<label class="field" id="ship-url"' + (carrier === 'other' ? '' : ' hidden') + '><span>Tracking link</span><input class="input" name="url" type="url" placeholder="https://" value="' + esc(again ? f.url || '' : '') + '"></label>' +
      '<p class="err" id="ship-err" hidden></p>' +
      '<div class="row between"><span class="small muted">' + (again ? 'Saving sends the shipped email again with the new tracking.' : 'The customer gets the “Your order shipped” email with tracking.') + '</span>' +
      '<button class="btn btn-honey" type="submit">' + icon('truck') + (again ? 'Update tracking' : 'Mark as shipped') + '</button></div></form>';
  }
  function fulfilCard(o) {
    var st = R.stage(o), f = o.fulfillment || {};
    var head = function (t, sub) { return '<div class="card-head"><div><h2>' + t + '</h2>' + (sub ? '<p class="sub">' + sub + '</p>' : '') + '</div></div>'; };
    if (st === 'pending' && R.isPaymentLink(o)) {
      var pl = o.stripe && o.stripe.paymentLinkUrl;
      return '<section class="card tint">' + head('Waiting for payment', 'Payment link created ' + esc(h.ago(o.createdAt)) + (o.email ? ' and emailed to ' + esc(o.email) : '') + '.') +
        (pl ? '<code class="code">' + esc(pl) + '<button class="icon-btn" type="button" data-act="copy" data-copy="' + esc(pl) + '" aria-label="Copy link">' + icon('copy') + '</button></code>' : '') +
        '<p class="small muted gap-top">When they pay, this becomes a normal order with their shipping address.</p></section>';
    }
    if (st === 'pending') {
      return '<section class="card tint">' + head('Not paid', 'Checkout started ' + esc(h.ago(o.createdAt)) + ' but the payment never went through.') +
        '<p class="small">Nothing to make. If they write to you, you can send them a <a href="#links' + h.qs({ email: o.email, title: 'Order ' + h.orderNo(o), amount: R.pricing(o).total }) + '">payment link</a>.</p>' +
        (o.email ? '<div class="row gap-top"><a class="btn btn-ghost btn-sm" href="mailto:' + esc(o.email) + '">' + icon('mail') + 'Email ' + esc(o.email) + '</a></div>' : '') + '</section>';
    }
    if (st === 'canceled') return '<section class="card">' + head('Canceled', 'This order was canceled. Nothing to make or ship.') + '</section>';
    if (st === 'refunded') return '<section class="card">' + head('Fully refunded', 'Nothing left to do.') + (R.wasShipped(o) ? trackBox(o) : '') + '</section>';
    if (st === 'to_fulfil') {
      return '<section class="card tint"><div class="card-head"><div><h2>Make &amp; ship</h2><p class="sub">Paid ' + esc(h.ago(R.orderDate(o))) + ' · ' + h.plural(R.magnetsOf(o), 'magnet') + '</p></div>' +
        '<button class="btn btn-sm" data-act="startProd">Start production</button></div>' +
        '<details class="panel" open><summary>Ready to ship? Add tracking</summary><div>' + shipForm(o) + '</div></details></section>';
    }
    if (st === 'in_production') {
      var since = (o.timeline || []).filter(function (t) { return t.status === 'in_production'; }).pop();
      return '<section class="card tint">' + head('Ship it', 'In production' + (since ? ' since ' + esc(h.fmtDate(since.at)) : '') + '. Add the tracking number when the parcel is ready.') + shipForm(o) + '</section>';
    }
    if (st === 'shipped') {
      return '<section class="card">' + head('On its way', R.toMs(f.shippedAt) ? 'Shipped ' + esc(h.ago(f.shippedAt)) : '') + trackBox(o) + liveBox(o) +
        '<div class="row between gap-top"><span class="small muted">' + (f.lastCheckedAt ? 'Delivered already? You can mark it yourself: the customer gets a short note asking for a review.' : 'When tracking says delivered, mark it: the customer gets a short note asking for a review.') + '</span>' +
        '<button class="btn btn-honey btn-sm" data-act="delivered">' + icon('check') + 'Mark delivered</button></div>' +
        '<details class="panel"><summary>Fix the tracking number</summary><div>' + shipForm(o, true) + '</div></details></section>';
    }
    return '<section class="card">' + head('Delivered', R.toMs(f.deliveredAt) ? esc(h.fmtDT(f.deliveredAt)) : '') + trackBox(o) + liveBox(o) + '</section>';
  }
  function thumb(it) {
    if (it.kind === 'design' && it.id) return '<img class="thumb" src="' + h.ART_URL + esc(it.id) + '.webp" alt="" loading="lazy" width="64" height="64" data-fallback>';
    return '<span class="thumb">' + icon(it.kind === 'photos' ? 'image' : it.kind === 'package' ? 'orders' : 'hex') + '</span>';
  }
  function itemsCard(o) {
    var p = R.pricing(o), pr = o.pricing || {}, gi = 0, packs = photoItems(o), pi = -1;
    var lis = (o.items || []).map(function (it) {
      var qty = it.qty == null ? 1 : R.num(it.qty);
      if (it.kind === 'design') {
        return '<li>' + thumb(it) + '<div><h3>' + esc(it.title || it.id) + '</h3><p class="d">' + esc(h.colName(R.collectionOf(it))) + ' · <span class="faint">' + esc(it.id || '') + '</span></p></div>' +
          '<div class="p"><b>' + qty + ' × ' + money(it.unit) + '</b><span>' + money(R.itemPrice(it)) + '</span></div></li>';
      }
      if (it.kind === 'photos') {
        pi++;
        var photos = it.photos || [], size = R.num(it.packSize) * qty;
        var grid = photos.map(function (ph, j) {
          var f = frameOf(ph.frame), c = capText(f, ph.caption), rep = repeats(size, photos.length, j);
          var html = '<figure class="photo"><div class="mag" data-gi="' + (gi++) + '" data-pack="' + pi + '" data-j="' + j + '">' + magnetSVG('', f, ph.caption) +
            '<span class="n">' + (j + 1) + (rep > 1 ? ' ×' + rep : '') + '</span></div>' +
            '<figcaption><b>' + esc(f.name) + '</b>' + (c ? '“' + esc(c) + '”' : (f.caption ? '<span class="faint">No caption</span>' : '')) + '</figcaption></figure>';
          return html;
        }).join('');
        var fillNote = photos.length && size > photos.length ? h.plural(photos.length, 'photo') + ' for ' + size + ' magnets: they repeat in order to fill the pack.' : h.plural(photos.length, 'photo') + '.';
        return '<li>' + thumb(it) + '<div><h3>Photo magnets · ' + R.num(it.packSize) + '-pack' + (qty > 1 ? ' × ' + qty : '') + '</h3><p class="d">' + esc(fillNote) + '</p></div>' +
          '<div class="p"><b>' + money(R.itemPrice(it)) + '</b></div>' +
          '<div class="pack"><div class="pack-head"><span class="small muted">' + (packs.length > 1 ? 'Pack ' + (pi + 1) + ' · ' : '') + 'Each photo with the frame the customer picked</span>' +
          (pi === 0 ? '<button class="btn btn-ghost btn-sm" data-act="zipPhotos">' + icon('download') + 'Download all (.zip)</button>' : '') + '</div>' +
          (it.notes ? '<p class="quote small" style="margin-bottom:12px">' + esc(it.notes) + '</p>' : '') +
          '<div class="photos">' + grid + '</div></div></li>';
      }
      if (it.kind === 'package') {
        return '<li>' + thumb(it) + '<div><h3>' + esc(it.title || it.id) + '</h3><p class="d">Big-order package · ' + R.num(it.size) + ' magnets · artwork by email</p></div>' +
          '<div class="p"><b>' + qty + ' × ' + money(it.price) + '</b><span>' + money(R.itemPrice(it)) + '</span></div></li>';
      }
      return '<li>' + thumb(it) + '<div><h3>' + esc(it.title || 'Custom order') + '</h3><p class="d">Custom quote</p></div><div class="p"><b>' + money(R.itemPrice(it)) + '</b></div></li>';
    }).join('');
    var rows = [['Subtotal', money(p.subtotal)]];
    if (R.num(pr.bundleDiscount)) rows.push(['Bundle discount (3 for $12)', '−' + money(pr.bundleDiscount)]);
    if (R.num(pr.volumeDiscount)) rows.push(['Volume discount' + (pr.volumePct ? ' (' + pr.volumePct + '%)' : ''), '−' + money(pr.volumeDiscount)]);
    if (pr.promo && R.num(pr.promo.amount)) rows.push(['Code ' + (pr.promo.code || ''), '−' + money(pr.promo.amount)]);
    rows.push(['Shipping', p.shipping ? money(p.shipping) : 'Free']);
    var refunded = R.refundedTotal(o);
    return '<section class="card"><div class="card-head"><h2>Items</h2><span class="sub">' + h.plural(R.magnetsOf(o), 'magnet') + '</span></div>' +
      '<p class="small" id="photos-status" hidden></p><ul class="items">' + lis + '</ul>' +
      '<table class="totals">' + rows.map(function (r) { return '<tr><td>' + esc(r[0]) + '</td><td>' + r[1] + '</td></tr>'; }).join('') +
      '<tr class="total"><td>Total paid</td><td>' + money(p.total) + '</td></tr>' +
      (refunded ? '<tr class="ref"><td>Refunded</td><td>−' + money(refunded) + '</td></tr><tr><td><b>Net</b></td><td><b>' + money(p.total - refunded) + '</b></td></tr>' : '') + '</table></section>';
  }
  function printCard(o) {
    var mags = R.magnetsOf(o), sheets = Math.max(1, Math.ceil(mags / 12)), hasPhotos = photoItems(o).length > 0;
    var designs = designArgs(o).length, special = (o.items || []).filter(function (it) { return it.kind === 'package' || it.kind === 'custom'; });
    var cmd = printCommand(o);
    var steps = [];
    if (hasPhotos) steps.push('<b>Download the photos.</b> <button class="linkish" data-act="zipPhotos">Download all (.zip)</button> and unzip it in <b>Downloads</b>. It has every photo plus <code>' + esc(folderOf(o)) + '.json</code>, the frame and caption for each magnet.');
    if (special.length) steps.push('<b>Design the custom artwork.</b> ' + special.map(function (it) { return esc(it.title || 'Custom order'); }).join(', ') +
      ' — made from the details the customer emails you. ' + (hasPhotos || designs ? 'Save each design as an image and add it to the command below with <code>@none</code> (e.g. <code>~/Downloads/art.png@none</code>).'
        : 'Export it as <b>' + esc(folderOf(o)) + '-art.png</b> (square, 600 px or bigger) into Downloads.'));
    if (true) steps.push('<b>Make the print sheet.</b> Open Terminal in the <b>little-hive-house</b> folder and paste:<code class="code">' + esc(cmd) +
      '<button class="icon-btn" type="button" data-act="copy" data-copy="' + esc(cmd.replace(/ \\\n {2}/g, ' ')) + '" aria-label="Copy command">' + icon('copy') + '</button></code>' +
      '<span class="small muted">It saves <b>' + esc(folderOf(o)) + '.pdf</b> on your Desktop: about ' + h.plural(sheets, 'sheet') + ', 12 magnets per sheet.' +
      (!hasPhotos && !designs ? ' <code>--copies</code> prints the artwork once per magnet; change it if the order mixes designs.' : '') + '</span>');
    steps.push('<b>Print at 100%.</b> US Letter, “Actual size” (not “Fit to page”). Cut on the crop marks: each tile is 2.5 in, the 2 in face plus the paper that wraps the edge.');
    steps.push('<b>Pack it.</b> <button class="linkish" data-act="slip">Print the packing slip</button>' + (o.giftMessage ? ' (it includes the gift message)' : '') + ' and pop it in the envelope.');
    return '<section class="card"><div class="card-head"><div><h2>Print this order</h2><p class="sub">' + h.plural(mags, 'magnet') + ' · about ' + h.plural(sheets, 'sheet') + '</p></div>' +
      '<button class="btn btn-ghost btn-sm" data-act="slip">' + icon('print') + 'Packing slip</button></div><ol class="steps-n">' +
      steps.map(function (s) { return '<li><div>' + s + '</div></li>'; }).join('') + '</ol></section>';
  }
  function customerCard(o) {
    var lines = addressLines(o.shipping), ph = o.shipping && o.shipping.phone;
    var others = S.orders.filter(function (x) { return R.isSale(x) && R.customerKey(x) === R.customerKey(o); });
    var spent = others.reduce(function (a, x) { return a + R.pricing(x).total - R.refundedTotal(x); }, 0);
    var addr = lines.join('\n');
    return '<section class="card"><div class="card-head"><h2>Customer</h2>' + (others.length > 1 ? '<span class="badge">Repeat customer</span>' : '') + '</div>' +
      '<div class="sect"><b>' + esc(h.custName(o)) + '</b>' + (o.email ? '<br><a href="mailto:' + esc(o.email) + '">' + esc(o.email) + '</a>' : '') + (ph ? '<br><a href="tel:' + esc(ph) + '">' + esc(ph) + '</a>' : '') +
      '<p class="small muted" style="margin-top:6px"><a href="#orders?tab=all&q=' + encodeURIComponent(o.email || '') + '">' + h.plural(others.length, 'order') + '</a> · ' + money(spent) + ' spent' + (o.uid ? ' · has an account' : ' · guest checkout') + '</p></div>' +
      '<div class="sect"><div class="row between"><h3>Ship to</h3>' + (lines.length ? '<button class="btn btn-ghost btn-sm" data-act="copy" data-copy="' + esc(addr) + '">' + icon('copy') + 'Copy</button>' : '') + '</div>' +
      (lines.length ? '<address class="addr">' + esc(addr) + '</address>' : '<p class="muted">No address yet (not paid).</p>') + '</div>' +
      (o.giftMessage ? '<div class="sect"><h3>Gift message</h3><p class="quote">' + esc(o.giftMessage) + '</p></div>' : '') +
      (o.notes ? '<div class="sect"><h3>Note from the customer</h3><p class="quote">' + esc(o.notes) + '</p></div>' : '') + '</section>';
  }
  function paymentCard(o) {
    var p = R.pricing(o), fee = R.stripeFee(o, S.settings), refunded = R.refundedTotal(o), left = R.refundable(o);
    var st = o.stripe || {};
    var link = st.paymentIntent ? 'https://dashboard.stripe.com/payments/' + encodeURIComponent(st.paymentIntent) : '';
    var refunds = R.refundsOf(o);
    var html = '<section class="card"><div class="card-head"><h2>Payment</h2>' + (link ? '<a class="btn btn-ghost btn-sm" href="' + esc(link) + '" target="_blank" rel="noopener">Stripe ' + icon('external') + '</a>' : '') + '</div>' +
      '<dl class="kv"><dt>Paid</dt><dd>' + money(p.total) + (R.toMs(o.paidAt) ? ' <span class="muted small">· ' + esc(h.fmtDT(o.paidAt)) + '</span>' : '') + '</dd>' +
      (o.status !== 'pending' ? '<dt>Stripe fee</dt><dd>' + money(fee.amount) + (fee.estimated ? ' <span class="muted small">(estimate)</span>' : '') + '</dd>' : '') +
      (refunded ? '<dt>Refunded</dt><dd class="neg">−' + money(refunded) + '</dd>' : '') +
      (o.pricing && o.pricing.promo && o.pricing.promo.code ? '<dt>Code</dt><dd><span class="badge quiet">' + esc(o.pricing.promo.code) + '</span></dd>' : '') +
      (o.dispute || st.dispute ? '<dt>Dispute</dt><dd class="neg"><b>Customer opened a dispute.</b> Answer it in Stripe.</dd>' : '') + '</dl>';
    if (refunds.length) {
      html += '<div class="sect"><h3>Refunds</h3><ul class="notes">' + refunds.map(function (r) {
        return '<li><b class="neg">−' + money(r.amount) + '</b> · ' + esc(R.REASON_LABEL[r.reason] || r.reason) + (r.note ? '<br>' + esc(r.note) : '') +
          '<small>' + esc(h.fmtDT(r.at)) + (r.by ? ' · ' + esc(r.by) : '') + '</small></li>';
      }).join('') + '</ul></div>';
    }
    if (left > 0 && R.isSale(o)) {
      html += '<details class="panel" id="refund-panel"><summary>Refund…</summary><div><form class="stack" id="refund-form" novalidate>' +
        '<div class="seg" role="group" aria-label="Refund type"><button type="button" aria-pressed="true" data-act="refundMode" data-mode="full">Full · ' + money(left) + '</button>' +
        '<button type="button" aria-pressed="false" data-act="refundMode" data-mode="partial">Partial</button></div>' +
        '<label class="field"><span>Amount</span><span class="input-money"><input class="input" name="amount" type="number" inputmode="decimal" min="0.01" step="0.01" max="' + left.toFixed(2) + '" value="' + left.toFixed(2) + '" readonly></span>' +
        '<span class="hint">Up to ' + money(left) + (refunded ? ' (' + money(refunded) + ' already refunded)' : '') + '</span></label>' +
        '<label class="field"><span>Reason</span><select class="input" name="reason"><option value="">Choose a reason…</option>' +
        R.REASONS.map(function (r) { return '<option value="' + r[0] + '">' + esc(r[1]) + '</option>'; }).join('') + '</select><span class="hint">Used in Reports to see what goes wrong most.</span></label>' +
        '<label class="field"><span>Note <span class="hint">(only you see this)</span></span><textarea class="input" name="note" rows="2" placeholder="e.g. 2 magnets arrived cracked, sent photos"></textarea></label>' +
        '<p class="err" id="refund-err" hidden></p>' +
        '<button class="btn btn-danger" type="submit">' + icon('refund') + 'Review refund</button></form></div></details>';
    }
    return html + '</section>';
  }
  function statusCard(o) {
    return '<section class="card"><details class="panel" style="border:0;margin:0;padding:0"><summary>Change status by hand</summary><div><form class="stack" id="status-form">' +
      '<p class="small muted">For fixing mistakes. It doesn’t move money or email anyone: use Ship, Mark delivered or Refund for that.</p>' +
      '<label class="field"><span>New status</span><select class="input" name="status">' + A.h.STATUSES.filter(function (s) { return s[0] !== o.status; }).map(function (s) {
        return '<option value="' + s[0] + '">' + esc(s[1]) + '</option>';
      }).join('') + '</select><span class="hint">Refunded / partly refunded come from the Refund button. To cancel a paid order, refund it first.</span></label>' +
      '<label class="field"><span>Why? <span class="hint">(saved in the timeline)</span></span><input class="input" name="note" placeholder="e.g. Customer picked it up in person"></label>' +
      '<button class="btn btn-ghost" type="submit">Update status</button></form></div></details></section>';
  }
  function emailWhen(v) {
    if (!v) return '';
    if (Array.isArray(v)) {
      if (!v.length) return '';
      var last = v[v.length - 1], t = last && typeof last === 'object' && last.at ? last.at : last;
      return 'Sent ' + (v.length > 1 ? v.length + ' times, last ' : '') + (R.toMs(t) ? h.fmtDT(t) : '');
    }
    if (v === true) return 'Sent';
    if (typeof v === 'object' && v.at) return 'Sent ' + h.fmtDT(v.at);
    return R.toMs(v) ? 'Sent ' + h.fmtDT(v) : 'Sent';
  }
  function emailsCard(o) {
    var e = o.emails || {}, st = R.stage(o);
    var allowed = { confirmation: R.isSale(o), shipped: R.wasShipped(o), outForDelivery: !!e.outForDelivery, delivered: st === 'delivered', refund: R.refundedTotal(o) > 0 };
    if (o.status === 'pending') {
      var plink = o.stripe && o.stripe.paymentLinkUrl;
      if (!plink || !o.email) return '';
      return '<section class="card"><div class="card-head"><h2>Emails to the customer</h2></div><ul class="emails"><li><span><b>Payment link</b><small>Sent when you created the link</small></span>' +
        '<button class="btn btn-ghost btn-sm" data-act="resend" data-kind="payment_link" data-label="Payment link">Resend</button></li></ul></section>';
    }
    return '<section class="card"><div class="card-head"><h2>Emails to the customer</h2></div><ul class="emails">' + A.h.EMAIL_KINDS.map(function (k) {
      var when = emailWhen(e[k[0]]);
      return '<li><span><b>' + esc(k[2]) + '</b><small>' + esc(when || (allowed[k[0]] ? 'Not sent' : k[3])) + '</small></span>' +
        (allowed[k[0]] && o.email ? '<button class="btn btn-ghost btn-sm" data-act="resend" data-kind="' + k[1] + '" data-label="' + esc(k[2]) + '">Resend</button>' : '') + '</li>';
    }).join('') + '</ul></section>';
  }
  function notesCard(o) {
    var notes = (o.adminNotes || []).slice().sort(function (a, b) { return R.toMs(b.at) - R.toMs(a.at); });
    return '<section class="card"><div class="card-head"><h2>Notes</h2><span class="sub">Only you two see these</span></div>' +
      (notes.length ? '<ul class="notes">' + notes.map(function (n) { return '<li>' + esc(n.text) + '<small>' + esc(h.fmtDT(n.at)) + (n.by ? ' · ' + esc(n.by) : '') + '</small></li>'; }).join('') + '</ul>' : '') +
      '<form class="stack" id="note-form"><label class="field"><span class="sr">New note</span><textarea class="input" name="text" rows="2" placeholder="e.g. Reprinted photo 3, the first was too dark"></textarea></label>' +
      '<div class="row end"><button class="btn btn-ghost btn-sm" type="submit">Add note</button></div></form></section>';
  }
  function timelineCard(o) {
    var ev = (o.timeline || []).map(function (t) { return { at: R.toMs(t.at), text: t.text || A.h.STAGE_LABEL[t.status] || t.status, status: t.status }; });
    if (!ev.length) {
      if (R.toMs(o.createdAt)) ev.push({ at: R.toMs(o.createdAt), text: 'Checkout started' });
      if (R.toMs(o.paidAt)) ev.push({ at: R.toMs(o.paidAt), text: 'Paid ' + money(R.pricing(o).total) });
    }
    (o.adminNotes || []).forEach(function (n) { ev.push({ at: R.toMs(n.at), text: 'Note: ' + n.text, note: true }); });
    ev.sort(function (a, b) { return b.at - a.at; });
    return '<section class="card"><div class="card-head"><h2>Timeline</h2></div><ol class="timeline">' + ev.map(function (e) {
      return '<li' + (e.note ? ' class="note"' : '') + '>' + esc(e.text) + '<time>' + esc(h.fmtDT(e.at)) + '</time></li>';
    }).join('') + '</ol></section>';
  }

  /* ---------------------------------------------------------------- the view */
  A.VIEWS.order = function (r) {
    var o = h.findOrder(r.arg);
    if (!o) {
      current = null;
      if (r.arg && !A.VIEWS.order.tried) {
        A.VIEWS.order.tried = r.arg;
        h.refreshOrder(r.arg).then(function (x) { if (x) h.route(); else h.route(); }).catch(function () { h.route(); });
        return { title: 'Order', html: '<div class="loading"><span>Looking for that order…</span></div>' };
      }
      A.VIEWS.order.tried = null;
      return { title: 'Order not found', html: '<a class="back" href="#orders">' + icon('back') + 'Orders</a><div class="empty">' + icon('orders') + '<b>Order not found</b>It may have been removed, or the link is wrong.</div>' };
    }
    A.VIEWS.order.tried = null;
    current = o;
    var p = R.pricing(o), link = o.stripe && o.stripe.paymentIntent;
    var html = '<a class="back" href="#orders">' + icon('back') + 'Orders</a>' +
      '<div class="ohead"><h1>' + esc(h.orderNo(o)) + '</h1>' + h.chip(o) + '</div>' +
      '<div class="ometa"><span>' + (R.toMs(o.paidAt) ? 'Paid' : 'Started') + ' <b>' + esc(h.fmtDT(o.paidAt || o.createdAt)) + '</b></span><span>Total <b>' + money(p.total) + '</b></span>' +
      '<span><b>' + h.plural(R.magnetsOf(o), 'magnet') + '</b></span>' + (o.uid ? '' : '<span>Guest</span>') + '</div>' +
      '<div class="cols"><div>' + fulfilCard(o) + itemsCard(o) + (R.isSale(o) && R.stage(o) !== 'refunded' && R.stage(o) !== 'canceled' ? printCard(o) : '') + timelineCard(o) + '</div>' +
      '<div>' + customerCard(o) + paymentCard(o) + emailsCard(o) + notesCard(o) + statusCard(o) + '</div></div>';
    return { title: h.orderNo(o), html: html, after: function () { bindOrder(o); fillPhotos(); } };
  };

  function bindOrder(o) {
    var sf = document.getElementById('ship-form');
    if (sf) {
      sf.carrier.addEventListener('change', function () { document.getElementById('ship-url').hidden = sf.carrier.value !== 'other'; });
      sf.addEventListener('submit', function (ev) {
        ev.preventDefault();
        var err = document.getElementById('ship-err'), tracking = sf.tracking.value.trim(), url = sf.url.value.trim(), cost = sf.labelCost.value;
        err.hidden = true;
        if (!tracking && sf.carrier.value !== 'other') { err.textContent = 'Type the tracking number from the label.'; err.hidden = false; sf.tracking.focus(); return; }
        if (sf.carrier.value === 'other' && url && !/^https?:\/\//i.test(url)) { err.textContent = 'The tracking link should start with https://'; err.hidden = false; return; }
        if (cost === '' || isNaN(Number(cost)) || Number(cost) < 0) { err.textContent = 'Type what the label cost (0 if it was free).'; err.hidden = false; return; }
        var data = { orderId: o.id, carrier: sf.carrier.value, tracking: tracking, labelCost: Math.round(Number(cost) * 100) / 100 };
        if (sf.carrier.value === 'other') data.url = url;
        run(sf.querySelector('button[type=submit]'), 'adminShip', data, 'Marked shipped. The customer got the tracking email.').catch(function () {});
      });
    }
    var rf = document.getElementById('refund-form');
    if (rf) {
      rf.addEventListener('submit', function (ev) {
        ev.preventDefault();
        var err = document.getElementById('refund-err'), left = R.refundable(o);
        var amount = Math.round(Number(rf.amount.value) * 100) / 100;
        err.hidden = true;
        if (!(amount > 0)) { err.textContent = 'Type how much to refund.'; err.hidden = false; return; }
        if (amount > left + 0.001) { err.textContent = 'That’s more than what’s left to refund (' + money(left) + ').'; err.hidden = false; return; }
        if (!rf.reason.value) { err.textContent = 'Pick a reason.'; err.hidden = false; rf.reason.focus(); return; }
        var full = Math.abs(amount - left) < 0.005;
        h.dialog({
          title: full ? 'Refund the whole order?' : 'Refund part of the order?', danger: true, ok: 'Yes, refund ' + money(amount),
          html: '<p class="big">' + money(amount) + '</p><p>to <b>' + esc(h.custName(o)) + '</b> (' + esc(o.email || '') + ') for ' + esc(h.orderNo(o)) + '. Reason: <b>' + esc(R.REASON_LABEL[rf.reason.value]) + '</b>.</p>' +
            '<p class="small muted">The money goes back to their card through Stripe (5–10 business days) and they get a refund email. Stripe keeps its fee. This can’t be undone.</p>'
        }).then(function (ok) {
          if (!ok) return;
          run(rf.querySelector('button[type=submit]'), 'adminRefund', { orderId: o.id, amount: amount, reason: rf.reason.value, note: rf.note.value.trim() },
            'Refunded ' + money(amount) + '. The customer was emailed.').catch(function () {});
        });
      });
    }
    var nf = document.getElementById('note-form');
    if (nf) nf.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var text = nf.text.value.trim(); if (!text) { nf.text.focus(); return; }
      run(nf.querySelector('button[type=submit]'), 'adminAddNote', { orderId: o.id, text: text }, 'Note saved').catch(function () {});
    });
    var stf = document.getElementById('status-form');
    if (stf) stf.addEventListener('submit', function (ev) {
      ev.preventDefault();
      if (stf.status.value === o.status) { h.toast('That’s already the status.'); return; }
      var label = (A.h.STATUSES.find(function (s) { return s[0] === stf.status.value; }) || [0, stf.status.value])[1];
      h.dialog({ title: 'Change the status?', html: '<p>Set ' + esc(h.orderNo(o)) + ' to <b>' + esc(label) + '</b>. No email is sent and no money moves.</p>', ok: 'Change status' }).then(function (ok) {
        if (ok) run(stf.querySelector('button[type=submit]'), 'adminSetStatus', { orderId: o.id, status: stf.status.value, note: stf.note.value.trim() }, 'Status updated').catch(function () {});
      });
    });
  }
  ACT.refundMode = function (el) {
    var f = document.getElementById('refund-form'), full = el.getAttribute('data-mode') === 'full';
    Array.prototype.forEach.call(el.parentNode.children, function (b) { b.setAttribute('aria-pressed', String(b === el)); });
    f.amount.readOnly = full;
    if (full) f.amount.value = R.refundable(current).toFixed(2); else { f.amount.value = ''; f.amount.focus(); }
  };
  ACT.startProd = function (el) {
    run(el, 'adminSetStatus', { orderId: current.id, status: 'in_production', note: 'Started production' }, 'Moved to In production').catch(function () {});
  };
  ACT.delivered = function (el) {
    var o = current;
    h.dialog({ title: 'Mark as delivered?', html: '<p>' + esc(h.custName(o)) + ' gets a short “delivered” email that asks for a review.</p>', ok: 'Mark delivered' }).then(function (ok) {
      if (ok) run(el, 'adminMarkDelivered', { orderId: o.id }, 'Marked delivered').catch(function () {});
    });
  };
  ACT.resend = function (el) {
    var o = current, kind = el.getAttribute('data-kind');
    h.dialog({ title: 'Send it again?', html: '<p>Send the <b>' + esc(el.getAttribute('data-label')) + '</b> email to ' + esc(o.email) + ' again.</p>', ok: 'Send email' }).then(function (ok) {
      if (ok) run(el, 'adminResendEmail', { orderId: o.id, kind: kind }, 'Email sent to ' + o.email).catch(function () {});
    });
  };

  /* exported for tests */
  A.order = { magnetSVG: magnetSVG, photoPlan: photoPlan, printCommand: printCommand, normUrls: normUrls, frameOf: frameOf };
})();
