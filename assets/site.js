/* Little Hive House: cart, menu, quick view and shop filters, shared by every page. */
window.LHH_LOCALE = { en: 'en-US', es: 'es-US', pt: 'pt-BR', zh: 'zh-CN', fil: 'fil-PH', vi: 'vi-VN', fr: 'fr-FR', ko: 'ko-KR', ru: 'ru-RU', ar: 'ar' }[window.LHH_LANG || 'en'] || 'en-US';
(function () {
  var PRICE = 5, BUNDLE_N = 3, BUNDLE_PRICE = 12;
  var SHIPPING = 5.49, FREE_SHIP_AT = 35;
  var VOLUME = [[100, 25], [50, 20], [20, 10]];
  var SALE = {"name":"Black Friday","start":"2026-11-20T05:00:00Z","end":"2026-12-01T05:00:00Z","pct":20,"free":[[10,6],[6,3],[3,1]],"days":[{"name":"Black Friday","start":"2026-11-27T05:00:00Z","end":"2026-11-28T05:00:00Z","pct":30,"freeShipping":true}]};   /* the store-wide sale (tools/catalog.py SALE = catalog.json rules.sale): the server prices it the same way */
  /* when an order placed today arrives (assets/delivery.js), shown in the quick view, the cart and the shipping page */
  var ETA = '';
  try { if (window.LHHDelivery) ETA = LHHDelivery.arrival(); } catch (e) { ETA = ''; }
  if (ETA) document.querySelectorAll('[data-eta]').forEach(function (el) { el.textContent = 'about ' + ETA; });
  var KEY = 'lhh-cart';
  /* ---- problems customers hit, sent to the shop (functions/clientlog.js) so the owners hear about them right away ----
     No personal data: the kind of problem, the message, the page and the browser. At most 6 reports per page. */
  var LOG_URL = 'https://us-east1-little-hive-house.cloudfunctions.net/clientLog', logged = 0;
  function report(kind, info) {
    try {
      var url = window.LHH_LOG_URL || LOG_URL;   /* LHH_LOG_URL: the shop's own browser tests */
      if ((!window.LHH_LOG_URL && !/(^|\.)littlehivehouse\.com$/.test(location.hostname)) || logged >= 6) return;
      logged++;
      info = info || {};
      var body = JSON.stringify({ kind: kind, msg: String(info.msg || '').slice(0, 500), code: String(info.code || '').slice(0, 80), src: info.src || '',
        photos: info.photos, page: location.href, lang: window.LHH_LANG || 'en', ua: navigator.userAgent });
      if (navigator.sendBeacon && navigator.sendBeacon(url, new Blob([body], { type: 'text/plain' }))) return;
      fetch(url, { method: 'POST', body: body, mode: 'no-cors', keepalive: true }).catch(function () {});
    } catch (e) { /* never let reporting break the page */ }
  }
  window.addEventListener('error', function (e) {
    var src = String(e.filename || '');
    if (!src || src.indexOf(location.origin) !== 0 || /^Script error/.test(e.message || '')) return;   /* only our own scripts */
    report('js_error', { msg: e.message + (e.lineno ? ' (line ' + e.lineno + ')' : ''), src: src.replace(location.origin, '') });
  });
  /* store: a package line, or a photo pack (its photos wait in this browser, see PB, or are already uploaded to the store) */
  function keep(l) { return l && (l.kind === 'package' || (l.kind === 'custom' && Array.isArray(l.photos) && l.photos.length > 0)); }
  /* The photos of a photo pack, kept in this browser (IndexedDB) until the order is placed, so the pack stays in the cart
     when the customer goes to other pages (to add designs for free shipping, say) or the phone reloads the page.
     Key: "<line id>/<photo n>". Anything failing here (private browsing, old browser) only means nothing is kept. */
  var PB = (function () {
    var dbp = null;
    function db() {
      if (dbp) return dbp;
      dbp = new Promise(function (res) {
        try {
          var r = indexedDB.open('lhh-cart-photos', 1);
          r.onupgradeneeded = function () { r.result.createObjectStore('blobs'); };
          r.onsuccess = function () { res(r.result); };
          r.onerror = r.onblocked = function () { res(null); };
        } catch (e) { res(null); }
      });
      return dbp;
    }
    function run(mode, fn) {
      return db().then(function (d) {
        if (!d) return null;
        return new Promise(function (res) {
          try {
            var t = d.transaction('blobs', mode), q = fn(t.objectStore('blobs'));
            t.oncomplete = function () { res(q && q.result !== undefined ? q.result : null); };
            t.onerror = t.onabort = function () { res(null); };
          } catch (e) { res(null); }
        });
      });
    }
    return {
      /* Safari's private browsing won't keep a File in IndexedDB: then the photo is kept as raw bytes instead */
      put: function (k, b) {
        return run('readwrite', function (s) { return s.put(b, k); }).then(function (ok) {
          if (ok !== null || !b.arrayBuffer) return ok;
          return b.arrayBuffer().then(function (buf) { return run('readwrite', function (s) { return s.put({ buf: buf, type: b.type || '', name: b.name || '' }, k); }); }, function () { return null; });
        });
      },
      get: function (k) {
        return run('readonly', function (s) { return s.get(k); }).then(function (v) {
          if (v && !(v instanceof Blob) && v.buf) { try { return new File([v.buf], v.name || 'photo.jpg', { type: v.type || '' }); } catch (e) { return new Blob([v.buf], { type: v.type || '' }); } }
          return v;
        });
      },
      /* forget photos of packs no longer in the saved cart (read from storage: another tab may hold newer packs) */
      prune: function () {
        var lines = readSaved();
        var live = {};
        lines.forEach(function (l) { if (l.kind === 'custom') live[l.id] = 1; });
        return run('readonly', function (s) { return s.getAllKeys ? s.getAllKeys() : null; }).then(function (keys) {
          var dead = (keys || []).filter(function (k) { return !live[String(k).split('/')[0]]; });
          if (dead.length) return run('readwrite', function (s) { dead.forEach(function (k) { s.delete(k); }); return null; });
        });
      },
    };
  })();
  var $ = function (id) { return document.getElementById(id); };
  var money = function (n) { return '$' + (Math.round(n * 100) / 100).toFixed(n % 1 ? 2 : 0); };

  // The cart lives in localStorage (designs, packages, photo packs; the photos themselves in IndexedDB, see PB).
  function readSaved() {
    try {
      var saved = JSON.parse(localStorage.getItem(KEY) || '[]');
      if (!Array.isArray(saved)) return [];
      return saved.filter(function (l) { return l && (l.kind === 'design' || l.kind === 'place' || keep(l)) && l.qty > 0; })
        .map(function (l) {
          if (l.kind === 'place') { l.kind = 'design'; if (l.id.indexOf('/') < 0) l.id = 'places/' + l.id; }
          return l;
        });
    } catch (e) { return []; }
  }
  var cart = readSaved();
  /* Another tab changed the cart, or Safari brought this page back from its back/forward cache with an old cart in
     memory: take the saved cart again (keeping the photos already in memory), so this page never writes an old cart
     over items added elsewhere. */
  function resync() {
    var fresh = readSaved();
    fresh.forEach(function (l) {
      if (l.kind !== 'custom' || !l.photos) return;
      var mine = cart.find(function (m) { return m.kind === 'custom' && m.id === l.id && m.photos; });
      if (mine) l.photos.forEach(function (ph, i) { var o = mine.photos[i]; if (o && o.blob && !ph.blob) ph.blob = o.blob; });
    });
    cart = fresh;
    render();
    if (window.LHH) window.LHH.photosReady = loadPhotos(false);
  }
  window.addEventListener('storage', function (e) { if (e.key === KEY || e.key === null) resync(); });
  window.addEventListener('pageshow', function (e) { if (e.persisted) resync(); });

  var pruneTimer;
  function save() {
    clearTimeout(pruneTimer); pruneTimer = setTimeout(function () { PB.prune(); }, 1500);
    try {
      localStorage.setItem(KEY, JSON.stringify(cart.filter(function (l) { return l.kind === 'design' || keep(l); }).map(function (l) {
        if (!l.photos) return l;
        var c = {}; for (var k in l) c[k] = l[k];   /* Blobs and blob: URLs only live on this page */
        c.photos = l.photos.map(function (ph) { return { n: ph.n, file: ph.file, frame: ph.frame, frameName: ph.frameName, caption: ph.caption, path: ph.path, pathUid: ph.pathUid || null, crop: ph.crop || null, w: ph.w || 0, h: ph.h || 0, capStyle: ph.capStyle || null }; });
        return c;
      })));
    } catch (e) {}
  }

  var toastTimer;
  function toast(msg) {
    var t = $('toast'); if (!t) return;
    t.textContent = msg; t.hidden = false;
    clearTimeout(toastTimer); toastTimer = setTimeout(function () { t.hidden = true; }, Math.max(2200, Math.min(7000, String(msg).length * 55)));   /* long messages stay long enough to read */
  }

  function totals(now) {
    var sub = 0, designs = 0, pkg = 0;
    cart.forEach(function (l) { sub += l.price * l.qty; if (l.kind === 'design') designs += l.qty; if (l.kind === 'package') pkg += l.price * l.qty; });
    var bundleOf = function (n) { return Math.floor(n / BUNDLE_N) * (BUNDLE_N * PRICE - BUNDLE_PRICE); };
    var disc = bundleOf(designs);
    /* packages already have their quantity price (a service like mailing is count 0): the volume discount is on the rest */
    var magnets = cart.reduce(function (a, l) { return a + l.qty * (l.count == null ? 1 : l.count); }, 0);
    var tier = VOLUME.find(function (v) { return magnets >= v[0]; });
    var pct = tier ? tier[1] : 0;
    var vol = Math.round((sub - disc - pkg) * pct) / 100;
    var goods = sub - disc - vol;
    /* the sale (same as functions/pricing.js): % off what they pay, or some designs free; the better one, never both */
    var t = now == null ? Date.now() : now, sale = null;
    if (SALE && t >= Date.parse(SALE.start) && t < Date.parse(SALE.end)) {
      var day = (SALE.days || []).find(function (d) { return t >= Date.parse(d.start) && t < Date.parse(d.end); });
      sale = { name: (day && day.name) || SALE.name, pct: (day && day.pct) || SALE.pct || 0, freeShipping: !!(day && day.freeShipping) };
    }
    var promoC = 0, kind = '', free = 0, goodsC = Math.round(goods * 100);
    if (sale) {
      var byPct = Math.round(goodsC * sale.pct / 100), byFree = 0, left = designs, f = 0;
      (SALE.free || []).slice().sort(function (a, b) { return (b[0] + b[1]) - (a[0] + a[1]); }).forEach(function (tr) {
        var g = tr[0] + tr[1]; while (g > 0 && left >= g) { f += tr[1]; left -= g; }
      });
      if (f > 0) {
        var subF = sub - f * PRICE, bundleF = bundleOf(designs - f), volF = Math.round((subF - bundleF - pkg) * pct) / 100;
        byFree = goodsC - Math.round((subF - bundleF - volF) * 100);
      }
      if (byFree > byPct) { promoC = byFree; kind = 'free'; free = f; } else if (byPct > 0) { promoC = byPct; kind = 'pct'; }
    }
    var promo = promoC / 100;
    var ship = cart.length && cart.every(function (l) { return l.digital; }) ? 0 : sale && sale.freeShipping ? 0 : goods >= FREE_SHIP_AT ? 0 : SHIPPING;   /* design files only: nothing to ship */
    var next = VOLUME.slice().reverse().find(function (v) { return magnets < v[0]; });
    var paid = (goodsC - promoC) / 100;
    return { sub: sub, disc: disc, vol: vol, pct: pct, magnets: magnets, next: next, goods: paid, before: goods, ship: ship, total: (goodsC - promoC + Math.round(ship * 100)) / 100,
      promo: promo, sale: sale, saleKind: kind, free: free, count: cart.reduce(function (a, l) { return a + l.qty; }, 0) };
  }

  /* small picture of each cart line: the design itself, the frame of the first photo, or the honeycomb for packages */
  var ROOT = (function () { var me = document.querySelector('script[src*="site.js"]'); return me ? me.src.replace(/assets\/site\.js.*$/, '') : '/'; })();
  function lineThumb(l) {
    var src = '';
    if (l.kind === 'design' && /^[a-z0-9-]+\/[a-z0-9-]+$/.test(l.id || '')) src = ROOT + 'assets/art/' + l.id + '.webp';
    else if (l.photos && l.photos.length && /^[a-z0-9-]+$/.test(l.photos[0].frame || '')) src = ROOT + 'assets/email/thumbs/frames/' + l.photos[0].frame + '.jpg';
    else if (l.kind === 'package' && /^[a-z0-9-]{2,40}$/.test(l.style || '') && l.style !== 'own' && l.style !== 'qr') src = ROOT + 'assets/occasions/' + l.style + '.webp';
    else src = ROOT + 'assets/favicon.svg';
    var img = document.createElement('img');
    img.className = 'line-thumb' + (l.kind === 'design' || /occasions/.test(src) ? '' : ' line-thumb-icon');
    img.src = src; img.alt = ''; img.width = 56; img.height = 56; img.loading = 'lazy'; img.decoding = 'async';
    img.onerror = function () { img.remove(); };
    return img;
  }

  function render() {
    var t = totals();
    document.querySelectorAll('[data-cart-count]').forEach(function (el) { el.textContent = t.count; });
    var ul = $('lines'); if (!ul) return;
    ul.innerHTML = '';
    cart.forEach(function (l, i) {
      var li = document.createElement('li'); li.className = 'line';
      var left = document.createElement('div'); left.className = 'line-main';
      var thumb = lineThumb(l);
      if (thumb) left.appendChild(thumb);
      var txt = document.createElement('div'); left.appendChild(txt);
      var h = document.createElement('h3'); h.textContent = l.name; txt.appendChild(h);
      var d = document.createElement('p'); d.className = 'detail'; d.textContent = l.detail; txt.appendChild(d);
      if (l.photos && l.photos.length) {  /* photo packs: the frame (and caption) chosen for each photo */
        var det = document.createElement('details'); det.className = 'line-photos';
        var sm = document.createElement('summary'); sm.textContent = 'Frame for each photo'; det.appendChild(sm);
        var ol = document.createElement('ol');
        l.photos.forEach(function (ph) {
          var it = document.createElement('li');
          it.textContent = ph.frameName + (ph.caption ? ' · “' + ph.caption + '”' : '');
          ol.appendChild(it);
        });
        det.appendChild(ol); left.appendChild(det);
      }
      var amt = document.createElement('div'); amt.className = 'amt'; amt.textContent = money(l.price * l.qty);
      var qty = document.createElement('div'); qty.className = 'qty';
      var minus = document.createElement('button'); minus.type = 'button'; minus.textContent = '−'; minus.setAttribute('aria-label', 'One less ' + l.name);
      var out = document.createElement('output'); out.textContent = l.qty;
      var plus = document.createElement('button'); plus.type = 'button'; plus.textContent = '+'; plus.setAttribute('aria-label', 'One more ' + l.name);
      minus.onclick = function () { l.qty -= 1; if (l.qty < 1) cart.splice(i, 1); save(); render(); };
      plus.onclick = function () { l.qty += 1; save(); render(); };
      qty.append(minus, out, plus);
      var rm = document.createElement('button'); rm.type = 'button'; rm.className = 'remove'; rm.textContent = 'Remove';
      rm.onclick = function () { cart.splice(i, 1); save(); render(); };
      li.append(left, amt, qty, rm);
      ul.appendChild(li);
    });
    var empty = cart.length === 0;
    $('empty-cart').hidden = !empty;
    $('totals').hidden = empty;
    $('t-sub').textContent = money(t.sub);
    $('t-disc-row').hidden = t.disc === 0;
    $('t-disc').textContent = '−' + money(t.disc);
    $('t-vol-row').hidden = t.vol === 0;
    $('t-vol-label').textContent = 'Big order, ' + t.magnets + ' magnets (' + t.pct + '% off)';
    $('t-vol').textContent = '−' + money(t.vol);
    var vn = $('vol-note');
    if (t.next && t.magnets >= 5 && cart.some(function (l) { return l.kind !== 'package'; })) {   /* packages have their own price */ vn.textContent = 'Add ' + (t.next[0] - t.magnets) + ' more magnets for ' + t.next[1] + '% off your whole order.'; vn.hidden = false; }
    else vn.hidden = true;
    var sr = $('t-sale-row');
    if (sr) {
      sr.hidden = !t.promo;
      if (t.promo) {
        $('t-sale-label').textContent = t.sale.name + ', ' + (t.saleKind === 'free' ? (t.free === 1 ? '1 design free' : t.free + ' designs free') : t.sale.pct + '% off');
        $('t-sale').textContent = '−' + money(t.promo);
      }
    }
    var dn = $('sale-note');
    if (dn) {
      /* the next "buy N, get M free" step, when it would beat what they have now */
      var nd = cart.reduce(function (a, l) { return a + (l.kind === 'design' ? l.qty : 0); }, 0), tip = '';
      if (t.sale && nd > 0) {
        var steps = (SALE.free || []).map(function (f) { return [f[0] + f[1], f[1]]; }).sort(function (x, y) { return x[0] - y[0]; });
        var nx = steps.find(function (f) { return nd < f[0]; });
        if (nx) tip = t.sale.name + ': add ' + (nx[0] - nd) + (nx[0] - nd === 1 ? ' more design' : ' more designs') + ' and ' + nx[1] + (nx[1] === 1 ? ' of them is free.' : ' of them are free.');
      }
      dn.textContent = tip; dn.hidden = !tip;
    }
    $('t-ship').textContent = t.ship ? money(t.ship) : 'Free';
    $('t-total').textContent = money(t.total);
    var sn = $('ship-note');
    if (t.ship) { sn.textContent = 'Add ' + money(FREE_SHIP_AT - t.before) + ' more for free US shipping.'; sn.classList.remove('free'); }
    else if (t.sale && t.sale.freeShipping) { sn.textContent = t.sale.name + ': free shipping on every order today.'; sn.classList.add('free'); }
    else { sn.textContent = 'Your order ships free.'; sn.classList.add('free'); }
    etaNote();
  }

  /* when it arrives (assets/delivery.js): the strip, the quick view and the cart all show the same dates */
  function etaNote() {
    var en = $('eta-note'); if (!en) return;
    var pkg = cart.some(function (l) { return l.kind === 'package'; });
    var other = cart.some(function (l) { return l.kind !== 'package'; });
    en.textContent = '';
    var txt = [];
    if (other) txt.push(ETA ? 'Order today and it arrives about ' + ETA + ' in the US.' : 'Made by hand in 1–2 business days, then 2–5 days in the mail.');
    if (pkg) txt.push('Big orders ship 3–5 business days after you approve the proof.');
    en.appendChild(document.createTextNode(txt.join(' ') + ' '));
    var a = document.createElement('a'); a.href = ROOT + 'shipping.html'; a.textContent = 'Shipping details';
    en.appendChild(a);
  }

  var lastFocus = null;
  function openCart() { lastFocus = document.activeElement; $('scrim').hidden = false; $('drawer').hidden = false; $('close-cart').focus(); }
  function closeCart() { $('scrim').hidden = true; $('drawer').hidden = true; if (lastFocus && lastFocus.focus) lastFocus.focus(); }
  document.querySelectorAll('[data-open-cart]').forEach(function (b) { b.addEventListener('click', openCart); });
  $('close-cart').onclick = closeCart;
  $('scrim').onclick = closeCart;
  $('empty-shop').addEventListener('click', closeCart);
  $('drawer').addEventListener('keydown', function (e) { if (e.key === 'Escape') closeCart(); });

  function addDesign(el) {
    var id = el.getAttribute('data-add');
    var name = el.getAttribute('data-name');
    var line = cart.find(function (l) { return l.id === id; });
    if (line) line.qty += 1;
    else cart.push({ id: id, kind: 'design', name: name + ' magnet', detail: '2 × 2 in · ' + el.getAttribute('data-collection'), price: PRICE, qty: 1 });
    save(); render(); toast(name + ' added to cart');
    track('add_to_cart', { currency: 'USD', value: PRICE, items: [{ item_id: id, item_name: name, item_category: el.getAttribute('data-collection') || '', price: PRICE, quantity: 1 }] });
  }
  function track(n, p) { if (window.lhhTrack) window.lhhTrack(n, p); }
  document.addEventListener('click', function (e) {
    var b = e.target.closest('[data-add]');
    if (b) addDesign(b);
  });

  // mobile menu
  var mb = $('menu-btn'), mm = $('mobile-menu');
  if (mb && mm) {
    mb.addEventListener('click', function () {
      var open = mb.getAttribute('aria-expanded') === 'true';
      mb.setAttribute('aria-expanded', String(!open)); mm.hidden = open;
    });
  }

  // seasonal collections: in season they sit right after the place collections, out of season at the end
  (function () {
    var d = new Date(), md = (d.getMonth() + 1) * 100 + d.getDate();
    var inSeason = function (r) { var p = r.split('-'), a = +p[0], b = +p[1]; return a <= b ? (md >= a && md <= b) : (md >= a || md <= b); };
    var seen = [];
    document.querySelectorAll('[data-col-season]').forEach(function (el) {
      var box = el.parentNode; if (seen.indexOf(box) >= 0) return; seen.push(box);
      var items = Array.prototype.filter.call(box.children, function (c) { return c.hasAttribute('data-col-season'); });
      var anchor = Array.prototype.filter.call(box.children, function (c) { return c.hasAttribute('data-col-anchor'); })[0];
      var now = items.filter(function (c) { return inSeason(c.getAttribute('data-col-season')); });
      var later = items.filter(function (c) { return !inSeason(c.getAttribute('data-col-season')); });
      var ref = anchor ? anchor.nextSibling : box.firstChild;
      now.forEach(function (c) { box.insertBefore(c, ref); });
      later.forEach(function (c) { box.appendChild(c); });
    });
  })();

  // seasonal drifting leaves / snow / petals in the hero
  (function () {
    var hero = document.querySelector('.hero');
    var season = document.documentElement.getAttribute('data-season');
    var sets = { fall: ['fall-leaf1', 'fall-leaf2', 'fall-leaf3', 'fall-leaf4'], halloween: ['halloween-bat', 'fall-leaf1', 'fall-leaf3'],
                 christmas: ['snow1', 'snow2', 'snow3'], winter: ['snow1', 'snow2', 'snow3'], valentine: ['heart1', 'heart2'],
                 spring: ['petal1', 'petal2', 'petal3'], summer: [], thanksgiving: ['fall-leaf1', 'fall-leaf2', 'fall-leaf3', 'fall-leaf4'],
                 newyear: ['confetti1', 'confetti2', 'confetti3'], stpatricks: ['clover1', 'clover2'], july4: ['star1', 'star2', 'confetti1'] };
    var list = sets[season];
    if (!hero || !list || !list.length || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    var me = document.querySelector('script[src*="site.js"]');
    var base = me ? me.src.replace(/site\.js.*$/, 'decor/') : 'assets/decor/';
    var box = document.createElement('div'); box.className = 'drift'; box.setAttribute('aria-hidden', 'true');
    for (var i = 0; i < 9; i++) {
      var el = document.createElement('i');
      var s = 18 + Math.random() * 16;
      el.style.left = 'calc(' + (Math.random() * 100).toFixed(1) + '% - ' + Math.round(s + 30) + 'px)';
      el.style.width = el.style.height = s + 'px';
      el.style.backgroundImage = 'url(' + base + list[i % list.length] + '.svg)';
      el.style.animationDuration = (11 + Math.random() * 9) + 's';
      el.style.animationDelay = (-Math.random() * 18) + 's';
      box.appendChild(el);
    }
    hero.insertBefore(box, hero.firstChild);
  })();

  // day / night toggle
  var tb = $('theme-btn');
  if (tb) tb.addEventListener('click', function () {
    var next = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    /* a manual choice only lasts until the next sunrise (6:00) or sunset (19:00) on the visitor's clock */
    var now = new Date(), until = new Date(now);
    if (now.getHours() < 6) until.setHours(6, 0, 0, 0);
    else if (now.getHours() < 19) until.setHours(19, 0, 0, 0);
    else { until.setDate(until.getDate() + 1); until.setHours(6, 0, 0, 0); }
    try { localStorage.setItem('lhh-theme2', JSON.stringify({ t: next, until: until.getTime() })); } catch (e) {}
  });

  // quick view
  var qv = $('quick-view');
  if (qv && typeof qv.showModal === 'function') {
    var qvAdd = $('qv-add');
    document.addEventListener('click', function (e) {
      var art = e.target.closest('[data-view]');
      if (!art) return;
      var card = art.closest('.product');
      var btn = card.querySelector('[data-add]');
      $('qv-art').innerHTML = art.innerHTML;
      $('qv-title').textContent = btn.getAttribute('data-name');
      var col = $('qv-col');
      col.textContent = btn.getAttribute('data-collection') + ' collection';
      col.setAttribute('href', btn.getAttribute('data-href'));
      ['data-add', 'data-name', 'data-collection'].forEach(function (a) { qvAdd.setAttribute(a, btn.getAttribute(a)); });
      qv.showModal();
      if (window.lhhTrack) window.lhhTrack('view_item', { currency: 'USD', value: PRICE, items: [{ item_id: btn.getAttribute('data-add'), item_name: btn.getAttribute('data-name'), item_category: btn.getAttribute('data-collection') || '', price: PRICE }] });
    });
    $('qv-close').addEventListener('click', function () { qv.close(); });
    qv.addEventListener('click', function (e) { if (e.target === qv) qv.close(); });
    qvAdd.addEventListener('click', function () { setTimeout(function () { qv.close(); }, 150); });
  }

  // "See more": the rest of the designs (or collections) come back behind one button (tools/build.py more_button)
  document.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('[data-see-more]');
    if (!b) return;
    var box = b.closest('.wrap') || document;
    if (box.querySelector('#all-products')) return;   /* the shop's own list: handled below with the search */
    var first = null;
    Array.prototype.forEach.call(box.querySelectorAll('[data-more]'), function (el) { el.hidden = false; el.removeAttribute('data-more'); if (!first) first = el; });
    b.parentNode.remove();
    if (first) { var f = first.querySelector('a, button'); if (f) f.focus({ preventScroll: true }); }
  });

  // shop page: collection filter + search
  var grid = $('all-products');
  if (grid) {
    var items = Array.prototype.slice.call(grid.querySelectorAll('.product'));
    var tabs = Array.prototype.slice.call(document.querySelectorAll('[data-filter]'));
    var q = $('search'), countEl = $('result-count'), none = $('no-results');
    var current = 'all', expanded = false;
    var moreBtn = grid.parentNode.querySelector('[data-see-more]');
    if (moreBtn) moreBtn.addEventListener('click', function () {
      expanded = true; moreBtn.parentNode.hidden = true; apply();
      var first = grid.querySelector('[data-more]:not([hidden]) button'); if (first) first.focus({ preventScroll: true });
    });
    var params = new URLSearchParams(location.search);
    var fromUrl = params.get('c');
    if (params.get('q')) q.value = params.get('q');
    if (fromUrl && tabs.some(function (t) { return t.getAttribute('data-filter') === fromUrl; })) current = fromUrl;
    function apply() {
      var term = (q.value || '').trim().toLowerCase();
      var shown = 0;
      items.forEach(function (it) {
        var match = (current === 'all' || it.getAttribute('data-collection') === current) &&
                    (!term || it.getAttribute('data-search').indexOf(term) !== -1);
        /* the rest wait behind "See more" only on the full list: a collection or a search shows everything */
        var ok = match && (expanded || !!term || current !== 'all' || !it.hasAttribute('data-more'));
        it.hidden = !ok; if (match) shown++;
      });
      tabs.forEach(function (t) { t.setAttribute('aria-pressed', String(t.getAttribute('data-filter') === current)); });
      countEl.textContent = current === 'all' && !term && countEl.getAttribute('data-all') ? countEl.getAttribute('data-all') : shown + (shown === 1 ? ' design' : ' designs');
      none.hidden = shown !== 0;
      if (moreBtn && !expanded) moreBtn.parentNode.hidden = !!term || current !== 'all';
      var ask = $('no-results-idea');
      if (ask) ask.href = 'suggestions.html?kind=place' + (term ? '&idea=' + encodeURIComponent(q.value.trim()) : '');
    }
    tabs.forEach(function (t) {
      t.addEventListener('click', function () {
        current = t.getAttribute('data-filter');
        var u = new URL(location.href);
        if (current === 'all') u.searchParams.delete('c'); else u.searchParams.set('c', current);
        history.replaceState(null, '', u);
        apply();
      });
    });
    q.addEventListener('input', apply);
    apply();
  }

  // home page: show the seasonal spotlight for today's date
  var spot = $('spotlight');
  if (spot) {
    var now = new Date();
    var md = String(now.getMonth() + 1).padStart(2, '0') + '-' + String(now.getDate()).padStart(2, '0');
    var inRange = function (s, e) { return s <= e ? (md >= s && md <= e) : (md >= s || md <= e); };
    var tpl = Array.prototype.find.call(document.querySelectorAll('template[data-start]'), function (t) { return inRange(t.getAttribute('data-start'), t.getAttribute('data-end')); });
    if (tpl && spot.getAttribute('data-season') !== tpl.getAttribute('data-start') + '_' + tpl.getAttribute('data-end')) {
      spot.replaceWith(tpl.content.cloneNode(true));
    }
  }

  /* ---- store: big-order packages (big-orders.html), one buyable line per package size ---- */
  function pkgPicked(card) { return card.querySelector('.tier input:checked') || card.querySelector('.tier input'); }
  document.addEventListener('change', function (e) {
    var r = e.target.closest && e.target.closest('.tier input'); if (!r) return;
    var card = r.closest('[data-package]');
    var buy = card.querySelector('[data-buy-package]'); if (buy) buy.innerHTML = 'Buy now · ' + priceHtml(Number(r.getAttribute('data-price')));
    var q = card.querySelector('[data-pkg]'); if (q) q.setAttribute('data-qty', r.getAttribute('data-size'));
  });
  document.addEventListener('click', function (e) {
    /* bulk-order pages: "Use this style" picks it in the pack card and goes to the prices */
    var u = e.target.closest('[data-use-style]');
    if (u) {
      var sel = document.querySelector('[data-pkg-style]');
      if (sel) { sel.value = u.getAttribute('data-use-style'); }
      document.querySelectorAll('.occ-idea.picked').forEach(function (x) { x.classList.remove('picked'); });
      var li = u.closest('.occ-idea'); if (li) li.classList.add('picked');
      var packs = document.getElementById('packs'); if (packs) packs.scrollIntoView({ behavior: 'smooth', block: 'start' });
      return;
    }
    var b = e.target.closest('[data-buy-package]'); if (!b) return;
    var card = b.closest('[data-package]');
    var r = pkgPicked(card); if (!r) return;
    var size = Number(r.getAttribute('data-size'));
    var addr = Number(r.getAttribute('data-addresses')) || 0;
    var st = card.querySelector('[data-pkg-style]');
    var style = st && st.value ? st.value : '';
    var styleName = style ? st.options[st.selectedIndex].text : '';
    var line = { id: r.value, kind: 'package', name: r.getAttribute('data-title'), count: size, price: Number(r.getAttribute('data-price')),
                 detail: addr ? addr + ' addresses · we ask for your list after checkout' : size + ' magnets · ' + (styleName ? 'style: ' + styleName + ' · ' : '') + 'we plan the design with you by email after checkout' };
    if (style) line.style = style;
    addLine(line, true);
    openCart();
  });
  function addLine(line, quiet) {   /* quiet: the cart drawer opens right after, so no toast over it */
    /* a pack made in the studio or the QR maker is its own line: two different designs never merge */
    var same = line.kind !== 'custom' && !line.design && !line.qr && cart.find(function (l) { return l.id === line.id && l.kind === line.kind && !l.design && !l.qr && (l.style || '') === (line.style || ''); });
    if (same) same.qty += line.qty || 1;
    else { if (!line.qty) line.qty = 1; cart.push(line); }
    save(); render(); if (!quiet) toast(line.name + ' added to cart');
  }
  /* ---- /store ---- */

  /* the sale running now (same rules as totals()): {name, pct, freeShipping, end, last}, or null */
  function saleInfo(now) {
    var t = now == null ? Date.now() : now;
    if (!SALE || !(t >= Date.parse(SALE.start) && t < Date.parse(SALE.end))) return null;
    var day = (SALE.days || []).find(function (d) { return t >= Date.parse(d.start) && t < Date.parse(d.end); });
    var end = day ? Date.parse(day.end) : Date.parse(SALE.end);
    return { name: (day && day.name) || SALE.name, pct: (day && day.pct) || SALE.pct || 0, freeShipping: !!(day && day.freeShipping), day: !!day, end: end, last: Date.parse(SALE.end) - t < 864e5 };
  }
  /* a price as it is now: crossed out with the sale price next to it (designs, packs, buttons) */
  function priceHtml(p) {
    var s = saleInfo(), n = Number(p);
    if (!s || !s.pct || !(n > 0)) return money(n);
    return '<s class="was">' + money(n) + '</s> <span class="now">' + money(Math.round(n * (100 - s.pct)) / 100) + '</span>';
  }
  (function saleBar() {
    var s = saleInfo(); if (!s) return;
    var bar = document.createElement('div'); bar.className = 'sale-bar' + (s.day ? ' sale-day' : ''); bar.setAttribute('role', 'note');
    var steps = (SALE.free || []).slice().sort(function (a, b) { return a[0] - b[0]; })[0];
    var left = function () {
      var m = Math.max(0, Math.round((s.end - Date.now()) / 60000)), h = Math.floor(m / 60);
      return h >= 24 ? '' : ' · ends in ' + (h ? h + 'h ' : '') + (m % 60) + 'm';
    };
    var draw = function () {
      var what = s.day ? 'today only: ' + s.pct + '% off everything' + (s.freeShipping ? ' + free shipping' : '')
        : s.pct + '% off everything' + (steps ? ', or buy ' + steps[0] + ' designs, get ' + steps[1] + ' free' : '');
      bar.innerHTML = '<strong>' + (s.last ? 'Cyber Monday' : s.name) + '</strong> <span>' + what + (s.day || s.last ? left() : ' · through Cyber Monday') + '</span> <a href="' + ROOT + 'black-friday.html">Shop the sale</a>';
    };
    draw(); setInterval(draw, 60000);
    document.body.insertBefore(bar, document.body.firstChild);
    document.documentElement.classList.add('on-sale');
    /* the design price on shop and design pages, and the photo pack prices: crossed out with the sale price */
    if (!s.pct) return;
    document.querySelectorAll('.price, .pack label span').forEach(function (el) {
      var tn = Array.prototype.find.call(el.childNodes, function (c) { return c.nodeType === 3 && /^\s*\$\d+(\.\d+)?/.test(c.nodeValue); });
      if (!tn) return;
      var m = tn.nodeValue.match(/^(\s*)\$(\d+(?:\.\d+)?)(.*)$/);
      var span = document.createElement('span'); span.className = 'sale-price';
      span.innerHTML = m[1] + priceHtml(m[2]);
      el.replaceChild(span, tn);
      if (m[3]) span.parentNode.insertBefore(document.createTextNode(m[3]), span.nextSibling);
    });
  })();

  window.LHH = {
    sale: saleInfo, priceHtml: priceHtml,
    /* a bulk-order pack built on the page (the QR magnet maker): one cart line, then the cart */
    addPackage: function (line) { line.kind = 'package'; addLine(line, true); openCart(); },
    addCustom: function (item) {
      item.kind = 'custom'; item.qty = 1; cart.push(item);
      render(); toast('Photo magnets added to cart'); openCart();
      /* the photos are stored before the cart line is saved, so another page or tab always finds them */
      Promise.all((item.photos || []).map(function (ph) { return ph.blob ? PB.put(item.id + '/' + ph.n, ph.blob) : null; }))
        .then(function () { if (cart.indexOf(item) >= 0) save(); }, function () { if (cart.indexOf(item) >= 0) save(); });
    },
    /* resolves when the photos of the packs saved on another page are back (checkout.js waits for it) */
    photosReady: Promise.resolve(),
    money: money,
    toast: toast,
    report: report,
    /* store: used by assets/store.js, checkout.js and orders.js */
    cart: function () { return cart; },
    totals: totals,
    addLine: addLine,
    save: function () { save(); render(); },
    clear: function () { cart.length = 0; save(); render(); },
    openCart: openCart,
    closeCart: closeCart
  };
  render();

  /* sideways-scrolling rows (policy tabs, collection chips): on a phone, bring the current page's tab into view */
  document.querySelectorAll('[aria-current="page"]').forEach(function (a) {
    for (var row = a.parentElement; row && row !== document.body; row = row.parentElement) {
      if (row.scrollWidth > row.clientWidth + 2 && /(auto|scroll)/.test(getComputedStyle(row).overflowX)) {
        var rr = row.getBoundingClientRect(), ar = a.getBoundingClientRect();
        row.scrollLeft += (ar.left - rr.left) - (rr.width - ar.width) / 2;
        break;
      }
    }
  });

  /* photo packs saved on another page: their photos come back from this browser; a pack whose photos are gone
     (browser data cleared) can't be printed, so it leaves the cart */
  function loadPhotos(dropLost) {
    /* every photo comes back, even ones already uploaded: if the customer's sign-in changed (Instagram's browser
       can forget it), they go up again under the new one */
    var waiting = cart.filter(function (l) { return l.kind === 'custom' && l.photos.some(function (ph) { return !ph.blob; }); });
    if (!waiting.length) return Promise.resolve();
    return Promise.all(waiting.map(function (l) {
      return Promise.all(l.photos.map(function (ph) {
        if (ph.blob) return true;
        return PB.get(l.id + '/' + ph.n).then(function (b) { if (b && b.size) { ph.blob = b; return true; } return !!ph.path; });
      })).then(function (ok) { return ok.every(Boolean) ? null : l; });
    })).then(function (lost) {
      lost = lost.filter(Boolean);
      if (!lost.length || !dropLost) return;
      cart = cart.filter(function (l) { return lost.indexOf(l) < 0; });
      save(); render();
      report('photos_lost', { msg: 'photo pack photos missing from this browser', photos: lost.reduce(function (n, l) { return n + l.photos.length; }, 0) });
      toast('Your photo pack was removed. Please add your photos again.');
    }, function () { /* keep the cart as it is */ });
  }
  window.LHH.photosReady = loadPhotos(true);

  /* Instagram/Facebook shop: Meta sends the buyer here with ?products=<feed id>:<qty>,<feed id>:<qty>
     (the ids of google-products.xml). The designs go into the cart; a photo pack opens the photo builder. */
  (function fromMeta() {
    var raw = null;
    try { raw = new URLSearchParams(location.search).get('products'); } catch (e) { return; }
    if (!raw) return;
    try {
      var u = new URL(location.href);
      ['products', 'coupon', 'cart_origin'].forEach(function (k) { u.searchParams.delete(k); });
      history.replaceState(null, '', u);
    } catch (e) {}
    var want = raw.split(',').map(function (p) {
      var i = p.lastIndexOf(':'), id = (i < 0 ? p : p.slice(0, i)).trim();
      var n = i < 0 ? 1 : parseInt(p.slice(i + 1), 10);
      return [id, Math.max(1, Math.min(99, n || 1))];
    }).filter(function (w) { return w[0]; });
    var pack = null;
    want.forEach(function (w) { var m = /^photo-pack-(\d+)$/.exec(w[0]); if (m) pack = m[1]; });
    fetch('/assets/feed-ids.json', { cache: 'no-cache' }).then(function (r) { return r.json(); }).then(function (map) {
      var added = 0;
      /* the cart becomes exactly what was picked on Facebook/Instagram (Meta requires it: no leftovers, no doubled quantities) */
      if (want.some(function (w) { return map[w[0]]; })) { cart.length = 0; save(); }
      want.forEach(function (w) {
        var d = map[w[0]]; if (!d) return;
        if (d[4] === 'package') {   /* a bulk-order pack: [cart id, name, category, catalog title, "package", magnets, price] */
          addLine({ id: d[0], kind: 'package', name: d[3], count: d[5], price: d[6], qty: w[1], detail: d[5] + ' magnets · we plan the design with you by email after checkout' }, true);
          added += w[1] * d[5];
          return;
        }
        addLine({ id: d[0], kind: 'design', name: d[3] || d[1] + ' magnet', detail: '2 × 2 in · ' + d[2], price: PRICE, qty: w[1] }, true);   /* the catalog title: Meta checks the cart shows the same name */
        added += w[1];
      });
      return added;
    }).catch(function () { return 0; }).then(function (added) {
      if (pack) { location.replace('/photo-magnets.html?pack=' + pack); return; }
      if (added) { openCart(); toast(added === 1 ? 'Your magnet is in the cart' : 'Your ' + added + ' magnets are in the cart'); }
      else if (document.querySelector('[data-cart-page]')) openCart();
    });
  })();
  /* cart.html opened without products: show the cart right away */
  try { if (document.querySelector('[data-cart-page]') && !/[?&]products=/.test(location.search)) openCart(); } catch (e) {}
})();

/* the language buttons (the top one and the menu list): keep the choice and show the page again in that language.
   The top button only shows to someone not in English (back to English), or in English on a phone set to another
   language we have (back to that one). */
(function () {
  var ph = window.LHH_PHONE_LANG, names = window.LHH_LANGS || {};
  document.querySelectorAll('[data-lang-phone]').forEach(function (a) {
    if (!ph || ph === 'en' || !names[ph]) return;
    a.setAttribute('data-set-lang', ph);
    var n = a.querySelector('[data-lang-phone-name]'); if (n) n.textContent = names[ph];
  });
  document.querySelectorAll('.lang-list a').forEach(function (a) { if (a.getAttribute('data-set-lang') === (window.LHH_LANG || 'en')) a.classList.add('on'); });
})();
document.addEventListener("click", function (e) {
  var a = e.target.closest && e.target.closest("[data-set-lang]");
  if (!a) return;
  e.preventDefault();
  var l = a.getAttribute("data-set-lang");
  try { localStorage.setItem("lhh-lang", l); } catch (err) {}
  if (l !== (window.LHH_LANG || "en")) location.reload();
});

/* The header links must fit on one line in every language: measure after the page is translated and, if they
   overflow, tighten them (nav-tight) or switch to the Menu button (nav-squeeze). */
(function () {
  var h = document.documentElement;
  function over() {
    var r = document.querySelector('.header-row');
    if (!r) return false;
    var right = h.clientWidth - 12, out = false;   // the links may spill past the page column, but not off the screen
    r.querySelectorAll('a, button').forEach(function (e) {
      var b = e.offsetParent && e.getBoundingClientRect();
      if (b && (b.right > right + 1 || b.left < 11)) out = true;   /* right to left (Arabic) overflows on the left */
    });
    return out;
  }
  function fit() {
    h.classList.remove('nav-tight', 'nav-squeeze');
    if (h.getAttribute('data-lang') === 'en' || !over()) return;
    h.classList.add('nav-tight');
    if (over()) { h.classList.remove('nav-tight'); h.classList.add('nav-squeeze'); }
  }
  var t;
  window.addEventListener('resize', function () { clearTimeout(t); t = setTimeout(fit, 120); });
  function whenReady() {
    if (h.getAttribute('data-lang') === 'en' || h.classList.contains('i18n-ready')) { fit(); return; }
    setTimeout(whenReady, 100);
  }
  whenReady();
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(fit);
})();
