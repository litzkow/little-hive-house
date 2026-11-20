/* Little Hive House: the QR magnet maker on the bulk-order pages (business.html, weddings.html). The customer types
   their link, name and message, picks colors and sees the magnet with a real, working QR code (assets/qr.js), then buys
   the pack: one cart line (kind "package", style "qr") carrying what they typed, for the proof. */
(function () {
  var box = document.querySelector('[data-qr-maker]');
  if (!box || !window.LHHQR) return;
  var $ = function (s) { return box.querySelector(s); };
  var url = $('#qr-url'), name = $('#qr-name'), line = $('#qr-line'), pack = $('#qr-pack'), buy = $('[data-qr-buy]'), msg = $('[data-qr-msg]');
  var prev = $('[data-qr-preview]'), code = prev.querySelector('.qrm-code');
  var pal = 'fern';
  function clean(u) {
    u = String(u || '').trim();
    if (!u) return '';
    if (!/^https?:\/\//i.test(u)) u = 'https://' + u;
    return u.slice(0, 200);
  }
  function looksLikeLink(u) { return /^https?:\/\/[^\s/$.?#]+\.[^\s]{2,}$/i.test(u); }
  function draw() {
    var u = clean(url.value) || code.getAttribute('data-default');
    var o = line.options[line.selectedIndex];
    prev.setAttribute('data-pal', pal);
    prev.querySelector('.qrm-name').textContent = name.value.trim() || name.getAttribute('placeholder');
    prev.querySelector('.qrm-top').textContent = o.getAttribute('data-top');
    prev.querySelector('.qrm-cta').textContent = o.getAttribute('data-cta');
    prev.querySelector('.qrm-stars').hidden = !o.hasAttribute('data-stars');
    var c = getComputedStyle(prev).getPropertyValue('--qr-ink').trim() || '#2B2118';
    code.innerHTML = window.LHHQR.svg(u, 240, c, '#fff');
    var p = pack.options[pack.selectedIndex];
    var pr = Number(p.getAttribute('data-price'));
    buy.innerHTML = 'Buy now · ' + (window.LHH && LHH.priceHtml ? LHH.priceHtml(pr) : '$' + pr);
  }
  box.addEventListener('input', draw);
  box.addEventListener('change', draw);
  box.addEventListener('click', function (e) {
    var b = e.target.closest('.qr-pal');
    if (b) {
      pal = b.getAttribute('data-pal');
      box.querySelectorAll('.qr-pal').forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
      draw();
      return;
    }
    if (!e.target.closest('[data-qr-buy]')) return;
    var u = clean(url.value);
    if (!looksLikeLink(u)) { msg.textContent = 'Type your link first (your website, Google reviews page, menu or Instagram).'; msg.classList.add('err'); url.focus(); return; }
    msg.classList.remove('err');
    var o = line.options[line.selectedIndex], p = pack.options[pack.selectedIndex];
    var n = Number(p.getAttribute('data-size')), nm = name.value.trim();
    window.LHH.addPackage({
      id: p.value, name: p.getAttribute('data-title'), count: n, price: Number(p.getAttribute('data-price')), qty: 1, style: 'qr',
      qr: { url: u, name: nm, top: o.getAttribute('data-top'), cta: o.getAttribute('data-cta'), stars: o.hasAttribute('data-stars'), pal: pal },
      detail: n + ' QR magnets · ' + (nm ? nm + ' · ' : '') + u.replace(/^https?:\/\//, '') + ' · proof before we print'
    });
  });
  draw();
})();
