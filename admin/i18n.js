/* Hive Admin in Portuguese (the owners' language) or English, chosen by each person and kept on their account
   (Firestore adminPrefs/{uid}.lang, mirrored in localStorage so the app opens in it straight away). Portuguese is the
   default. The views are written in English; when the language is Portuguese every text the app puts on screen is
   swapped for its translation from i18n-pt.js (window.LHH_PT: exact texts, and texts with * where a number, a name or
   a date goes). Customer content (their messages, the email previews, the packing slip) is marked translate="no" and
   stays as written. */
(function () {
  'use strict';
  var KEY = 'lhh-admin-lang';
  var lang = 'pt';
  try { var v = localStorage.getItem(KEY); if (v === 'en' || v === 'pt') lang = v; } catch (e) { /* private mode */ }
  var PT = window.LHH_PT || {};
  var exact = Object.create(null), pats = [], cache = Object.create(null);
  function escRe(s) { return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); }
  function norm(s) { return String(s).replace(/\s+/g, ' ').trim(); }
  Object.keys(PT).forEach(function (en) {
    var k = norm(en);
    if (k.indexOf('*') < 0) { exact[k] = PT[en]; return; }
    var lit = k.replace(/\*/g, ''), letters = lit.replace(/[^A-Za-z]/g, '').length;
    // too general to be safe ("* of *", "* for"): they would bite into ordinary sentences
    var head = /^\*/.test(k), tail = /\*$/.test(k);
    if (letters < 2 || (head && tail && letters < 9) || (head && letters < 4)) return;
    pats.push({ re: new RegExp('^' + k.split('*').map(escRe).join('([\\s\\S]*?)') + '$'), pt: PT[en], lit: lit.length });
  });
  pats.sort(function (a, b) { return b.lit - a.lit; });

  /** The Portuguese for one text without its outer spaces, or null. A part that fills a * (a status, a saved note, a
     reason) is translated too, the same way; a text that starts with "· " (the dot between two facts) is looked up
     without it. */
  function trCore(core, depth) {
    if (!core || !/[A-Za-z]/.test(core)) return null;
    if (core in cache) return cache[core];
    var out = exact[core];
    if (out === undefined) {
      out = null;
      for (var i = 0; i < pats.length; i++) {
        var m = core.match(pats[i].re);
        if (!m) continue;
        var parts = pats[i].pt.split('*'), r = parts[0];
        for (var j = 1; j < parts.length; j++) {
          var cap = m[j] !== undefined ? m[j] : '', c = norm(cap);
          var t = c && depth < 3 ? trCore(c, depth + 1) : null;
          if (t !== null) cap = cap.replace(c, t);
          r += cap + parts[j];
        }
        out = r; break;
      }
      if (out === null) {
        var dot = /^·\s+([\s\S]+)$/.exec(core);
        if (dot) { var rest = trCore(dot[1], depth + 1); if (rest !== null) out = '· ' + rest; }
      }
    }
    cache[core] = out;
    return out;
  }
  /** The Portuguese for one text (whitespace around it kept), or null when there is none. */
  function tr(s) {
    var out = trCore(norm(s), 0);
    return out === null ? null : s.replace(/^(\s*)[\s\S]*?(\s*)$/, '$1' + out.replace(/\$/g, '$$$$') + '$2');
  }
  function skip(el) {
    for (var e = el; e && e.nodeType === 1; e = e.parentNode) {
      var t = e.tagName;
      if (t === 'SCRIPT' || t === 'STYLE' || t === 'TEXTAREA' || t === 'svg' || t === 'SVG' || t === 'CODE') return true;
      if (e.getAttribute('translate') === 'no' || e.isContentEditable) return true;
    }
    return false;
  }
  var ATTRS = ['placeholder', 'title', 'aria-label'];
  function doNode(n) {
    if (n.nodeType === 3) {
      if (n.parentNode && !skip(n.parentNode)) { var r = tr(n.nodeValue); if (r !== null && r !== n.nodeValue) n.nodeValue = r; }
      return;
    }
    if (n.nodeType !== 1 || skip(n)) return;
    ATTRS.forEach(function (a) { var v = n.getAttribute(a); if (v) { var r = tr(v); if (r !== null && r !== v) n.setAttribute(a, r); } });
    if (n.tagName === 'INPUT' && (n.type === 'button' || n.type === 'submit') && n.value) { var r2 = tr(n.value); if (r2 !== null) n.value = r2; }
    for (var c = n.firstChild; c; c = c.nextSibling) doNode(c);
  }
  var titleRaw = null;
  function doTitle() { var t = document.title; var r = tr(t); if (r !== null && r !== t) document.title = r; }
  function start() {
    doNode(document.body);
    doTitle();
    new MutationObserver(function (list) {
      list.forEach(function (m) {
        if (m.type === 'characterData') doNode(m.target);
        else if (m.type === 'attributes') doNode(m.target);
        else m.addedNodes.forEach(doNode);
      });
      doTitle();
    }).observe(document.documentElement, { childList: true, subtree: true, characterData: true, attributes: true, attributeFilter: ATTRS });
  }

  /* plural words for h.plural() */
  var WORDS = { magnet: ['ímã', 'ímãs'], sheet: ['folha', 'folhas'], 'empty space': ['espaço vazio', 'espaços vazios'], 'logo magnet': ['ímã com o logo', 'ímãs com o logo'], order: ['pedido', 'pedidos'], customer: ['cliente', 'clientes'], day: ['dia', 'dias'],
    email: ['e-mail', 'e-mails'], link: ['link', 'links'], parcel: ['pacote', 'pacotes'], photo: ['foto', 'fotos'], refund: ['reembolso', 'reembolsos'],
    review: ['avaliação', 'avaliações'], subscriber: ['inscrito', 'inscritos'], thing: ['coisa', 'coisas'], 'abandoned checkout': ['pagamento abandonado', 'pagamentos abandonados'],
    'card hold': ['reserva no cartão', 'reservas no cartão'], 'shipped order': ['pedido enviado', 'pedidos enviados'], design: ['design', 'designs'], item: ['item', 'itens'],
    message: ['mensagem', 'mensagens'], idea: ['ideia', 'ideias'], code: ['cupom', 'cupons'], hour: ['hora', 'horas'], week: ['semana', 'semanas'], month: ['mês', 'meses'] };
  function word(n, one, many) {
    if (lang !== 'pt' || !WORDS[one]) return n === 1 ? one : (many || one + 's');
    return n === 1 ? WORDS[one][0] : WORDS[one][1];
  }

  /** Each person's choice is kept on their account: the app follows it on any device they sign in on. */
  function setLang(l, save) {
    l = l === 'en' ? 'en' : 'pt';
    try { localStorage.setItem(KEY, l); } catch (e) { /* ignore */ }
    var done = save ? save(l) : Promise.resolve();
    return Promise.resolve(done).catch(function () {}).then(function () { if (l !== lang) location.reload(); });
  }
  /** After sign-in: the language saved on the account wins over this device's (reloads once when they differ). */
  function syncFromAccount(saved) {
    if ((saved === 'en' || saved === 'pt') && saved !== lang) { try { localStorage.setItem(KEY, saved); } catch (e) { /* ignore */ } location.reload(); }
  }

  window.LHHI18N = { lang: lang, tr: tr, word: word, locale: function () { return lang === 'pt' ? 'pt-BR' : 'en-US'; }, setLang: setLang, syncFromAccount: syncFromAccount };
  document.documentElement.setAttribute('lang', lang === 'pt' ? 'pt-BR' : 'en');
  if (lang === 'pt') { if (document.body) start(); else document.addEventListener('DOMContentLoaded', start); }
})();
