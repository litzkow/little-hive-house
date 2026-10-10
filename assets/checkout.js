/* Little Hive House: checkout from the cart drawer. Needs site.js and store.js first.
   While the store isn't connected the button keeps saying "Checkout opens soon".
   With photo packs in the cart: sign in anonymously (unless signed in), upload every photo to
   Storage under uploads/{uid}/{packId}/{n}.{ext} with a progress bar, then createCheckout → Stripe. */
(function () {
  var $ = function (id) { return document.getElementById(id); };
  var S = window.LHHStore, L = window.LHH;
  var btn = $('checkout');
  if (!btn || !L) return;

  /* back from Stripe without paying */
  var qs = new URLSearchParams(location.search);
  if (qs.get('checkout') === 'canceled') {
    var u = new URL(location.href); u.searchParams.delete('checkout'); history.replaceState(null, '', u);
    setTimeout(function () { L.toast('Checkout canceled. Your cart is saved.'); if (L.cart().length) L.openCart(); }, 300);
  }
  if (!S || !S.configured) return;

  var LABEL = 'Checkout';
  btn.disabled = false; btn.textContent = LABEL;
  $('co').hidden = false; $('co-secure').hidden = false;
  var errEl = $('co-error'), prog = $('co-progress'), bar = $('co-bar'), fill = $('co-bar-fill'), plabel = $('co-progress-label');
  var busy = false;

  function setError(msg) { errEl.textContent = msg || ''; errEl.hidden = !msg; }
  function guard(e) { e.preventDefault(); e.returnValue = ''; }
  function progress(done, total, finished, count) {
    var pct = total ? Math.min(100, Math.round(done / total * 100)) : 0;
    prog.hidden = false;
    fill.style.width = pct + '%';
    bar.setAttribute('aria-valuenow', pct);
    plabel.textContent = finished >= count ? 'All ' + count + ' photos uploaded' : 'Uploading your ' + (count === 1 ? 'photo' : count + ' photos') + ' · ' + pct + '%';
    btn.textContent = finished >= count ? 'Opening secure checkout…' : 'Please keep this page open…';
  }

  /* ---------- photos ---------- */
  var EXT = { 'image/jpeg': 'jpg', 'image/jpg': 'jpg', 'image/png': 'png', 'image/heic': 'heic', 'image/heif': 'heic', 'image/webp': 'webp' };
  function toJpeg(blob) {
    if (!window.createImageBitmap) return Promise.reject(new Error('no-decode'));
    return createImageBitmap(blob).then(function (bmp) {
      var c = document.createElement('canvas'); c.width = bmp.width; c.height = bmp.height;
      c.getContext('2d').drawImage(bmp, 0, 0);
      return new Promise(function (res, rej) { c.toBlob(function (b) { if (b) res(b); else rej(new Error('no-encode')); }, 'image/jpeg', 0.92); });
    });
  }
  /* → {blob, ext, type}: JPG, PNG, HEIC and WebP go up as they are; anything else (GIF, BMP, AVIF...) becomes a JPG */
  function prepare(ph) {
    var got = ph.blob ? Promise.resolve(ph.blob)
      : ph.url && /^blob:/.test(ph.url) ? fetch(ph.url).then(function (r) { if (!r.ok) throw new Error('gone'); return r.blob(); })
      : Promise.reject(new Error('gone'));
    return got.catch(function () { var e = new Error('photos missing'); e.code = 'photos/missing'; throw e; }).then(function (b) {
      var type = (b.type || '').toLowerCase();
      if (!type && /\.(heic|heif)$/i.test(ph.file || '')) type = 'image/heic';
      if (EXT[type]) return { blob: b, ext: EXT[type], type: type === 'image/jpg' ? 'image/jpeg' : type };
      return toJpeg(b).then(function (j) { return { blob: j, ext: 'jpg', type: 'image/jpeg' }; });
    });
  }
  function packId(line) { return String(line.id || 'pack').toLowerCase().replace(/[^a-z0-9-]/g, '').slice(0, 48) || 'pack'; }

  function uploadAll(packs, user) {
    var jobs = [];
    packs.forEach(function (line) {
      var fresh = line.uploaded && line.uploaded.uid === user.uid && line.photos.every(function (p) { return p.path; });
      if (fresh) return;
      line.uploaded = null;
      line.photos.forEach(function (ph, i) { jobs.push({ line: line, ph: ph, n: i + 1 }); });
    });
    if (!jobs.length) return Promise.resolve();
    progress(0, 1, 0, jobs.length);
    btn.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
    return Promise.all(jobs.map(function (j) { return prepare(j.ph).then(function (p) { j.file = p; }); })).then(function () {
      window.addEventListener('beforeunload', guard);
      var total = jobs.reduce(function (a, j) { return a + j.file.blob.size; }, 0);
      var sent = jobs.map(function () { return 0; });
      var finished = 0, next = 0;
      function tick() { progress(sent.reduce(function (a, b) { return a + b; }, 0), total, finished, jobs.length); }
      function worker() {
        if (next >= jobs.length) return Promise.resolve();
        var k = next++, j = jobs[k];
        var path = 'uploads/' + user.uid + '/' + packId(j.line) + '/' + j.n + '.' + j.file.ext;
        return S.upload(path, j.file.blob, { contentType: j.file.type, customMetadata: { frame: j.ph.frame || 'none' } }, function (b) { sent[k] = b; tick(); })
          .then(function () { j.ph.path = path; sent[k] = j.file.blob.size; finished++; tick(); return worker(); });
      }
      return Promise.all([worker(), worker(), worker()]);
    }).then(function () {
      packs.forEach(function (line) { line.uploaded = { uid: user.uid, at: Date.now() }; });
      L.save();   /* uploaded packs now survive a canceled checkout */
    }).then(function () { window.removeEventListener('beforeunload', guard); },
      function (e) { window.removeEventListener('beforeunload', guard); throw e; });
  }

  /* ---------- the createCheckout payload (contract: see STORE_SPEC "createCheckout") ---------- */
  function payloadCart() {
    return L.cart().map(function (l) {
      if (l.kind === 'design') return { kind: 'design', id: l.id, qty: l.qty };
      if (l.kind === 'package') return { kind: 'package', id: l.id, qty: l.qty };
      if (l.kind === 'custom') {
        return { kind: 'photos', packSize: l.count, qty: l.qty, notes: l.notes || '',
                 photos: l.photos.map(function (p) { return { path: p.path, frame: p.frame || 'none', caption: p.caption || '' }; }) };
      }
      return null;
    }).filter(Boolean);
  }

  function start() {
    if (busy) return;
    var cart = L.cart();
    if (!cart.length) return;
    busy = true; setError(''); btn.disabled = true; btn.setAttribute('aria-busy', 'true'); btn.textContent = 'One moment…';
    var packs = cart.filter(function (l) { return l.kind === 'custom' && Array.isArray(l.photos) && l.photos.length; });
    var who = null;
    S.ready()
      .then(function () { return packs.length ? S.ensureUser() : S.user(); })
      .then(function (u) { who = u; return packs.length ? uploadAll(packs, u) : null; })
      .then(function () {
        btn.textContent = 'Opening secure checkout…';
        var data = { cart: payloadCart(), giftMessage: $('co-gift').value.trim(), notes: $('co-notes').value.trim(), marketing: $('co-mkt').checked };
        if (S.isMember(who) && who.email) data.email = who.email;
        return S.call('createCheckout', data);
      })
      .then(function (r) {
        if (!r || !r.url) { var e = new Error('no url'); e.code = 'internal'; throw e; }
        location.assign(r.url);
        /* keep the button busy until the browser leaves; re-enable if the visitor comes straight back */
        setTimeout(reset, 8000);
      })
      .catch(function (e) {
        if (window.console) console.warn('checkout failed', e && e.code, e && e.message);
        reset();
        prog.hidden = true;
        setError(S.message(e, 'checkout'));
        errEl.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
      });
  }
  function reset() { busy = false; btn.disabled = false; btn.removeAttribute('aria-busy'); btn.textContent = LABEL; }
  btn.addEventListener('click', start);
  window.addEventListener('pageshow', function (e) { if (e.persisted) { reset(); prog.hidden = true; } });

  /* signed-in customers who already said yes to emails don't need the box */
  var asked = false;
  document.addEventListener('click', function (e) {
    if (asked || !(e.target.closest && e.target.closest('[data-open-cart]'))) return;
    asked = true;
    S.ready().then(function (r) {
      if (!S.isMember(r.user)) return;
      return S.getProfile().then(function (p) { if (p.marketing) $('co-mkt').closest('label').hidden = true; });
    }).catch(function () {});
  });
})();
