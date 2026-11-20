/* Little Hive House: the design gallery and the studio on the bulk-order pages. The customer filters the designs by
   kind of business or event, opens one and makes it theirs (colors, words, their logo or photo, the QR link), sees it
   change at once, and buys the pack: one cart line (kind "package", style = the design) carrying their choices for the
   proof. The logo and the photo are uploaded to the store when they buy (uploads/<uid>/<design id>/1.png and 2.jpg).
   Drawing: assets/designer.js. */
(function () {
  'use strict';
  var D = window.LHHDesigner, S = window.LHHStore;
  var gal = document.querySelector('[data-gallery]'), dlg = document.querySelector('[data-studio]');
  if (!D || !gal || !dlg) return;
  var $ = function (s, r) { return (r || dlg).querySelector(s); };

  /* ---------------------------------------------------------------- the gallery: filter chips and "show more" */
  var STEP = 12, shown = STEP, group = 'all', words = '';
  /* plain letters to compare (accents and case don't matter): what the card shows, in English or Portuguese */
  function plain(t) { return String(t || '').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, ''); }
  function filter() {
    var n = 0, total = 0, q = plain(words).trim().split(/\s+/).filter(Boolean);
    gal.querySelectorAll('.dz-card').forEach(function (li) {
      var g = li.getAttribute('data-group'), chip = gal.querySelector('.dz-chip[data-dz-group="' + g.replace(/"/g, '') + '"]');
      var text = plain(li.textContent + ' ' + g + ' ' + (chip ? chip.textContent : '') + ' ' + (li.getAttribute('data-words') || ''));
      var ok = (group === 'all' || g === group) && q.every(function (w) { return text.indexOf(w) >= 0; });
      if (ok) total++;
      li.hidden = !ok || ++n > shown;
    });
    var more = gal.querySelector('[data-dz-more]');
    if (more) more.hidden = total <= shown;
    var none = gal.querySelector('[data-dz-none]');
    if (none) none.hidden = total > 0;
  }
  /* each kind of business with its little drawing */
  gal.querySelectorAll('.dz-chip[data-icon]').forEach(function (c) {
    var k = c.getAttribute('data-icon'), box = c.querySelector('.dz-ci');
    if (box && D.icons[k]) box.innerHTML = '<svg viewBox="0 0 64 64" width="26" height="26">' + D.icons[k].split('{c}').join('currentColor') + '</svg>';
  });
  var search = gal.querySelector('[data-dz-search]');
  if (search) search.addEventListener('input', function () {
    words = search.value; shown = STEP;
    if (words.trim() && group !== 'all') { group = 'all'; gal.querySelectorAll('[data-dz-group]').forEach(function (c) { c.setAttribute('aria-pressed', c.getAttribute('data-dz-group') === 'all' ? 'true' : 'false'); }); }
    filter();
  });
  gal.addEventListener('click', function (e) {
    var chip = e.target.closest('[data-dz-group]');
    if (chip) {
      group = chip.getAttribute('data-dz-group'); shown = STEP;
      if (search && search.value) { search.value = ''; words = ''; }
      gal.querySelectorAll('[data-dz-group]').forEach(function (c) { c.setAttribute('aria-pressed', c === chip ? 'true' : 'false'); });
      filter();
      var grid = gal.querySelector('.dz-grid');
      if (group !== 'all' && grid && grid.getBoundingClientRect().top > window.innerHeight * .6) grid.scrollIntoView({ behavior: 'smooth', block: 'start' });
      return;
    }
    if (e.target.closest('[data-dz-more]')) { shown += STEP * 2; filter(); return; }
    var card = e.target.closest('[data-design]');
    if (card) open(card.getAttribute('data-design'));
  });
  filter();

  /* the drawings to pick from (the same ones the designs use) */
  var box = dlg.querySelector('[data-dz-icons]');
  if (box) box.innerHTML = Object.keys(D.icons).map(function (k) {
    return '<button type="button" class="dz-ic" data-icon="' + k + '" aria-label="' + k + '"><svg viewBox="0 0 64 64" width="30" height="30">' + D.icons[k].split('{c}').join('currentColor') + '</svg></button>';
  }).join('');

  /* our own photos to pick from (free stock photos, assets/stock), drawn the first time a photo design opens */
  var stockBox = dlg.querySelector('[data-dz-stock]');
  function fillStock() {
    if (!stockBox || stockBox.childElementCount || !D.stock.length) return;
    var base = (document.querySelector('script[src*="studio.js"]').src || '').replace(/assets\/studio\.js.*$/, '');
    stockBox.innerHTML = D.stock.map(function (n) {
      return '<button type="button" class="dz-st" data-stock="' + n + '" aria-label="' + n.replace(/-\d+$/, '') + '"><img src="' + base + 'assets/stock/t/' + n + '.webp" alt="" width="110" height="110" loading="lazy" decoding="async"></button>';
    }).join('');
  }

  /* the photos that fit this design come first: its own kind (a pizza design shows pizzas), then its page's */
  var PRI = {
    business: ['pizza', 'bakery', 'coffee', 'food', 'chef', 'barber', 'salon', 'gym', 'yoga', 'dentist', 'house', 'kitchen', 'home-interior', 'cleaning', 'garden', 'car', 'mechanic', 'vet', 'flowers', 'team', 'handshake', 'church', 'school', 'football'],
    weddings: ['wedding', 'bride', 'couple', 'engagement', 'flowers', 'sunset'],
    graduation: ['grad-girl', 'grad', 'school', 'party', 'family'],
    parties: ['birthday', 'party', 'baby', 'toddler', 'kids', 'family', 'grandparents', 'dog', 'puppy', 'dog-small', 'cat', 'beach', 'travel', 'christmas-family']
  };
  function sortStock() {
    if (!stockBox) return;
    var own = d.slug.split('-')[0], list = PRI[d.page] || [];
    var rank = function (n) { var k = n.replace(/-\d+$/, ''); if (k === own || k.indexOf(own) === 0) return 0; var i = list.indexOf(k); return i < 0 ? 100 : i + 1; };
    Array.prototype.slice.call(stockBox.children).sort(function (a, b) { return rank(a.getAttribute('data-stock')) - rank(b.getAttribute('data-stock')); })
      .forEach(function (el) { stockBox.appendChild(el); });
    stockBox.scrollTop = 0;
  }

  /* ---------------------------------------------------------------- the studio */
  var LABEL = {
    name: 'Name', sub: 'Small line', head: 'Headline', line: 'Message', phone: 'Phone', web: 'Website or @',
    since: 'Side note', kicker: 'Label', offer: 'Offer', mono: 'Initials', a: 'First name', b: 'Second name', date: 'Date',
    place: 'Place', year: 'Year', school: 'School or team', hand0: 'Written on line 1', hand1: 'Written on line 2'
  };
  var MULTI = { head: 1, line: 1 };
  var d = null, ch = null, logoBlob = null, photoBlob = null, did = '';

  function rid() { return 'd' + Date.now().toString(36) + Math.random().toString(36).slice(2, 8); }
  function draw() { if (d) D.paint($('[data-dz-prev]'), d, ch); }
  /* the preview follows its box (the dialog opening, a phone turning) */
  if (window.ResizeObserver) {
    var lastW = 0;
    new ResizeObserver(function (en) { var w = Math.round(en[0].contentRect.width); if (w && w !== lastW) { lastW = w; draw(); } }).observe($('[data-dz-prev]'));
  }

  function field(k, v) {
    var lab = LABEL[k] || '', id = 'dz-' + k;
    if (/^items\d$/.test(k)) lab = 'Service ' + (+k.slice(5) + 1);
    var m = /^rows(\d)([ab])$/.exec(k);
    if (m) lab = (m[2] === 'a' ? 'Line ' + (+m[1] + 1) : 'Line ' + (+m[1] + 1) + ', right side');
    var multi = MULTI[k] || String(v).indexOf('\n') >= 0;
    var input = multi ? '<textarea id="' + id + '" rows="2" maxlength="120" data-dz-t="' + k + '">' + D.esc(v) + '</textarea>'
      : '<input id="' + id + '" maxlength="80" data-dz-t="' + k + '" value="' + D.esc(v) + '">';
    return '<div class="field dz-f' + (m ? ' dz-half' : '') + '"><label for="' + id + '">' + lab + '</label>' + input + '</div>';
  }

  function colorsNow() {
    if (ch.colors) return ch.colors;
    return { bg: d.colors.bg, ink: d.colors.ink, ac: d.colors.ac };
  }
  function setPickers() {
    var c = colorsNow();
    dlg.querySelectorAll('[data-dz-c]').forEach(function (inp) { var v = c[inp.getAttribute('data-dz-c')]; if (/^#[0-9a-f]{6}$/i.test(v)) inp.value = v; });
    dlg.querySelectorAll('.dz-pal').forEach(function (b) {
      var p = D.palettes[b.getAttribute('data-pal')];
      b.setAttribute('aria-pressed', ch.colors && p && p.bg === ch.colors.bg && p.ink === ch.colors.ink && p.ac === ch.colors.ac ? 'true' : 'false');
    });
    $('[data-dz-orig]').setAttribute('aria-pressed', ch.colors ? 'false' : 'true');
  }

  function open(slug) {
    d = D.get(slug); if (!d) return;
    ch = { text: {} }; logoBlob = photoBlob = null; did = rid();
    $('[data-dz-title]').textContent = d.title;
    $('[data-dz-fields]').innerHTML = Object.keys(d.text).map(function (k) { return field(k, d.text[k]); }).join('') +
      (/^(qr|eqr)$/.test(d.layout) ? '<div class="field dz-f"><label for="dz-url">Link for the QR code</label><input id="dz-url" type="url" inputmode="url" maxlength="200" placeholder="https://your-site.com" data-dz-url></div>' : '');
    $('[data-dz-photo-box]').hidden = !/^(photo|wphoto|polaroid)$/.test(d.layout);
    if (!$('[data-dz-photo-box]').hidden) { fillStock(); sortStock(); }
    dlg.querySelectorAll('.dz-st').forEach(function (b) { b.setAttribute('aria-pressed', 'false'); });
    $('[data-dz-logo-name]').textContent = '';
    $('[data-dz-photo-name]').textContent = '';
    $('[data-dz-nologo]').hidden = true;
    $('[data-dz-msg]').classList.remove('err');
    $('[data-dz-msg]').textContent = $('[data-dz-msg]').getAttribute('data-default');
    var ic = d.opt.icon;
    dlg.querySelectorAll('.dz-ic').forEach(function (b) { b.setAttribute('aria-pressed', b.getAttribute('data-icon') === ic ? 'true' : 'false'); });
    $('[data-dz-icons-box]').hidden = !ic;
    setPickers();
    price();
    if (dlg.showModal) { if (!dlg.open) dlg.showModal(); } else dlg.setAttribute('open', '');
    document.documentElement.classList.add('dz-lock');
    requestAnimationFrame(draw);
    if (window.lhhTrack) window.lhhTrack('select_item', { item_list_name: 'designs', items: [{ item_id: d.slug, item_name: d.title }] });
  }
  function close() { if (dlg.close) dlg.close(); else dlg.removeAttribute('open'); document.documentElement.classList.remove('dz-lock'); }
  dlg.addEventListener('close', function () { document.documentElement.classList.remove('dz-lock'); });

  function price() {
    var o = $('[data-dz-pack]').selectedOptions[0];
    $('[data-dz-buy]').textContent = 'Buy now · $' + Number(o.getAttribute('data-price'));
  }

  /* the logo: PNG with its transparency, at most 1200 px (an SVG is drawn into a PNG too) */
  function toImage(file, kind) {
    return new Promise(function (res, rej) {
      var u = URL.createObjectURL(file), im = new Image();
      im.onload = function () {
        var max = kind === 'logo' ? 1200 : 2000, w = im.naturalWidth || 1200, h = im.naturalHeight || 1200, k = Math.min(1, max / Math.max(w, h));
        if (!im.naturalWidth) { w = h = 1200; k = 1; }
        var c = document.createElement('canvas'); c.width = Math.round(w * k); c.height = Math.round(h * k);
        var x = c.getContext('2d');
        if (kind !== 'logo') { x.fillStyle = '#fff'; x.fillRect(0, 0, c.width, c.height); }
        x.drawImage(im, 0, 0, c.width, c.height);
        URL.revokeObjectURL(u);
        c.toBlob(function (b) { b ? res(b) : rej(new Error('blob')); }, kind === 'logo' ? 'image/png' : 'image/jpeg', .9);
      };
      im.onerror = function () { URL.revokeObjectURL(u); rej(new Error('read')); };
      im.src = u;
    });
  }

  dlg.addEventListener('input', function (e) {
    var t = e.target;
    if (t.hasAttribute('data-dz-t')) { ch.text[t.getAttribute('data-dz-t')] = t.value; draw(); return; }
    if (t.hasAttribute('data-dz-url')) { var u = t.value.trim(); ch.url = u ? (/^https?:\/\//i.test(u) ? u : 'https://' + u) : ''; draw(); return; }
    if (t.hasAttribute('data-dz-c')) { var c = colorsNow(); ch.colors = { bg: c.bg, ink: c.ink, ac: c.ac }; ch.colors[t.getAttribute('data-dz-c')] = t.value.toUpperCase(); setPickers(); draw(); }
  });
  dlg.addEventListener('change', function (e) {
    var t = e.target;
    if (t.hasAttribute('data-dz-pack')) { price(); return; }
    if (t.hasAttribute('data-dz-logo') || t.hasAttribute('data-dz-photo')) {
      var f = t.files && t.files[0], kind = t.hasAttribute('data-dz-logo') ? 'logo' : 'photo';
      if (!f) return;
      var msg = $('[data-dz-msg]');
      toImage(f, kind).then(function (b) {
        if (kind === 'logo') { logoBlob = b; if (ch.logo) URL.revokeObjectURL(ch.logo); ch.logo = URL.createObjectURL(b); $('[data-dz-nologo]').hidden = false; $('[data-dz-logo-name]').textContent = f.name; }
        else { photoBlob = b; if (ch.photo && /^blob:/.test(ch.photo)) URL.revokeObjectURL(ch.photo); ch.stock = ''; ch.photo = URL.createObjectURL(b); $('[data-dz-photo-name]').textContent = f.name; dlg.querySelectorAll('.dz-st').forEach(function (x) { x.setAttribute('aria-pressed', 'false'); }); }
        msg.classList.remove('err'); draw();
      }, function () {
        msg.textContent = 'We couldn’t open that file here. Try a PNG or JPG, or send it to us by email after checkout.'; msg.classList.add('err');
      });
      t.value = '';
    }
  });
  dlg.addEventListener('click', function (e) {
    var t = e.target;
    if (t.closest('[data-dz-close]')) { close(); return; }
    if (t === dlg) { close(); return; }   /* a click on the backdrop */
    var p = t.closest('.dz-pal');
    if (p) { var c = D.palettes[p.getAttribute('data-pal')]; ch.colors = { bg: c.bg, ink: c.ink, ac: c.ac }; setPickers(); draw(); return; }
    if (t.closest('[data-dz-orig]')) { ch.colors = null; setPickers(); draw(); return; }
    var sp = t.closest('.dz-st');
    if (sp) {
      if (ch.photo && /^blob:/.test(ch.photo)) URL.revokeObjectURL(ch.photo);
      photoBlob = null; ch.stock = sp.getAttribute('data-stock'); ch.photo = 'assets/stock/' + ch.stock + '.webp';
      dlg.querySelectorAll('.dz-st').forEach(function (b) { b.setAttribute('aria-pressed', b === sp ? 'true' : 'false'); });
      $('[data-dz-photo-name]').textContent = ''; draw(); return;
    }
    var i = t.closest('.dz-ic');
    if (i) { ch.icon = i.getAttribute('data-icon'); dlg.querySelectorAll('.dz-ic').forEach(function (b) { b.setAttribute('aria-pressed', b === i ? 'true' : 'false'); }); draw(); return; }
    if (t.closest('[data-dz-nologo]')) { if (ch.logo) URL.revokeObjectURL(ch.logo); ch.logo = ''; logoBlob = null; $('[data-dz-nologo]').hidden = true; $('[data-dz-logo-name]').textContent = ''; draw(); return; }
    if (t.closest('[data-dz-buy]')) buy();
  });

  function changed() {
    var out = {};
    Object.keys(ch.text).forEach(function (k) { if (ch.text[k] !== d.text[k]) out[k] = String(ch.text[k]).slice(0, 120); });
    return out;
  }

  function upload(blob, n, ext) {
    return S.ready().then(function () { return S.ensureUser(); }).then(function (u) {
      var path = 'uploads/' + u.uid + '/' + did + '/' + n + '.' + ext;
      return S.upload(path, blob, { contentType: ext === 'png' ? 'image/png' : 'image/jpeg', customMetadata: { design: d.slug } }, function () {}).then(function () { return path; });
    });
  }

  var busy = false;
  function buy() {
    if (busy) return;
    var msg = $('[data-dz-msg]'), btn = $('[data-dz-buy]');
    if (/^(qr|eqr)$/.test(d.layout) && ch.url && !/^https?:\/\/[^\s/$.?#]+\.[^\s]{2,}$/i.test(ch.url)) {
      msg.textContent = 'The QR link doesn’t look like a web address.'; msg.classList.add('err'); $('[data-dz-url]').focus(); return;
    }
    busy = true; btn.disabled = true; btn.textContent = 'One moment…';
    var o = $('[data-dz-pack]').selectedOptions[0], n = Number(o.getAttribute('data-size'));
    var design = { slug: d.slug, text: changed() };
    if (ch.colors) design.colors = ch.colors;
    if (ch.icon && ch.icon !== d.opt.icon) design.icon = ch.icon;
    if (ch.url) design.url = ch.url;
    if (ch.stock && !photoBlob) design.stock = ch.stock;
    var jobs = [];
    if (logoBlob) jobs.push(upload(logoBlob, 1, 'png').then(function (p) { design.logo = p; }));
    if (photoBlob) jobs.push(upload(photoBlob, 2, 'jpg').then(function (p) { design.photo = p; }));
    if (jobs.length) { msg.classList.remove('err'); msg.textContent = 'Sending your ' + (logoBlob ? 'logo' : 'photo') + '…'; }
    Promise.all(jobs).then(function () {
      var nm = (design.text.name || d.text.name || d.text.head || d.text.a || '').replace(/\n/g, ' ');
      window.LHH.addPackage({
        id: o.value, name: o.getAttribute('data-title'), count: n, price: Number(o.getAttribute('data-price')), qty: 1, style: d.slug, design: design,
        detail: n + ' magnets · ' + d.title + (nm ? ' · ' + nm : '') + (design.logo ? ' · with your logo' : '') + ' · proof before we print'
      });
      if (window.lhhTrack) window.lhhTrack('add_to_cart', { currency: 'USD', value: Number(o.getAttribute('data-price')), items: [{ item_id: o.value, item_name: d.title, price: Number(o.getAttribute('data-price')), quantity: 1 }] });
      close();
    }, function () {
      msg.textContent = 'We couldn’t send your file. Check the connection and try again, or buy without it and email it to us after checkout.'; msg.classList.add('err');
    }).then(function () { busy = false; btn.disabled = false; price(); });
  }

  /* "Use this style" anywhere on the page, or a link to #design-<slug>, opens the studio */
  var m = /^#design-([a-z0-9-]+)$/.exec(location.hash);
  if (m && D.get(m[1])) setTimeout(function () { open(m[1]); }, 300);
  window.LHHStudio = { open: open };
})();
