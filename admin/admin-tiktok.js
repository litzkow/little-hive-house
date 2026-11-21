/* Little Hive House admin: TikTok Shop (functions/tiktok.js). Paste the Hive Admin app's secret once, connect the
   shop once; then the products and orders (coming next). The secret and the tokens never come back to the app.
   TikTok sends the owner back to admin/tiktok-callback.html, which opens #tiktok?code=…&state=… here.
   The screen picks its own language (T(en, pt)), translate="no". */
(function () {
  'use strict';
  var A = window.LHHAdmin, h = A.h, V = A.VIEWS, ACT = A.ACT;
  var esc = h.esc, icon = h.icon;
  function T(en, pt) { return h.LANG() === 'pt' ? pt : en; }
  function errText(e) {
    var msg = String((e && e.message) || '').replace(/^Firebase:\s*/, '');
    var m = /^TikTok:\s*([\s\S]*)$/.exec(msg);
    if (m) return T('TikTok refused: ', 'O TikTok recusou: ') + m[1];
    if (/doesn't look like the app secret/.test(msg)) return T(msg, 'Isso não parece a chave secreta do app. No Partner Center, abra o app Hive Admin › App secret › Manage app secret, copie e cole de novo.');
    if (/secret isn't saved/.test(msg)) return T(msg, 'A chave secreta do app ainda não foi colada.');
    if (/doesn't match|took too long/.test(msg)) return T(msg, 'A autorização do TikTok não bateu ou demorou demais. Toque em “Conectar TikTok” de novo.');
    var f = h.friendlyError(e);
    var I = window.LHHI18N;
    var pt = h.LANG() === 'pt' && I && I.tr ? I.tr(f) : null;
    return pt || f;
  }
  var st = { data: null, loading: false, err: '', finishing: false, saving: false, products: null, loadingProducts: false, publishing: false, at: 0, total: 0, current: '' };

  function load() {
    if (st.loading) return;
    st.loading = true;
    h.call('adminTikTok', { action: 'status' }).then(function (d) { st.data = d; st.err = ''; })
      .catch(function (e) { st.err = errText(e); })
      .then(function () { st.loading = false; if (A.parseHash().view === 'tiktok') h.route(); });
  }

  function secretStep(d) {
    if (d.secret) {
      return '<li class="tt-done">' + icon('check') + ' ' + T('App secret saved', 'Chave secreta guardada') + (d.secretEnd ? ' <span class="muted small">(…' + esc(d.secretEnd) + ')</span>' : '') +
        ' · <button class="linkish small" data-act="ttNewSecret">' + T('Paste a new one', 'Colar outra') + '</button></li>';
    }
    return '<li><b>' + T('Paste the app secret', 'Cole a chave secreta do app') + '</b>' +
      '<ol class="small tt-how"><li>' + T('In the TikTok Shop Partner Center (partner.us.tiktokshop.com, Gmail account), open <b>App & service › Hive Admin</b>.',
        'No TikTok Shop Partner Center (partner.us.tiktokshop.com, conta do Gmail), abra <b>App & service › Hive Admin</b>.') + '</li>' +
      '<li>' + T('Under <b>App secret</b>, tap <b>Manage app secret</b> and copy it.', 'Em <b>App secret</b>, toque em <b>Manage app secret</b> e copie.') + '</li>' +
      '<li>' + T('Paste it here. It stays on the shop’s server and never shows again; don’t send it in chats or emails.',
        'Cole aqui. Ela fica guardada no servidor da loja e não aparece de novo; não mande em chat nem e-mail.') + '</li></ol>' +
      '<form data-form="ttSecret" class="tt-secret"><input class="input" name="secret" type="password" autocomplete="off" autocapitalize="off" spellcheck="false" placeholder="' + T('App secret', 'App secret') + '">' +
      '<button class="btn btn-honey" ' + (st.saving ? 'disabled' : '') + '>' + (st.saving ? T('Saving…', 'Guardando…') : T('Save', 'Guardar')) + '</button></form></li>';
  }

  function connectStep(d) {
    if (d.connected) {
      var s = d.shop || {};
      return '<li class="tt-done">' + icon('check') + ' ' + T('Connected to ', 'Conectado à loja ') + '<b>' + esc(s.name || 'TikTok Shop') + '</b>' +
        (s.region ? ' <span class="muted small">(' + esc(s.region) + ')</span>' : '') +
        ' · <button class="linkish small" data-act="ttDisconnect">' + T('Disconnect', 'Desconectar') + '</button></li>';
    }
    return '<li><b>' + T('Connect the shop', 'Conecte a loja') + '</b><p class="small">' +
      T('You go to TikTok, sign in with the <b>Little Hive House shop</b> account, tap Authorize and come back here.',
        'Você vai para o TikTok, entra com a conta da <b>loja Little Hive House</b>, toca em Authorize e volta para cá.') + '</p>' +
      '<p><button class="btn btn-honey" data-act="ttConnect" ' + (d.secret ? '' : 'disabled') + '>' + icon('external') + T('Connect TikTok', 'Conectar TikTok') + '</button></p></li>';
  }

  function connection(d) {
    return '<section class="card"><div class="card-head"><h2>' + T('Connection', 'Conexão') + '</h2></div><ol class="tt-steps">' +
      secretStep(d) + connectStep(d) + '</ol>' + links(d) + '</section>';
  }

  function links(d) {
    if (!d.connected) return '';
    return '<p class="tt-links">' +
      '<a class="btn btn-ghost btn-sm" href="https://seller-us.tiktok.com/homepage" target="_blank" rel="noopener">' + T('Open Seller Center', 'Abrir o Seller Center') + ' ' + icon('external') + '</a>' +
      '<a class="btn btn-ghost btn-sm" href="https://www.tiktok.com/@littlehivehouse" target="_blank" rel="noopener">' + T('See the shop on TikTok', 'Ver a loja no TikTok') + ' ' + icon('external') + '</a></p>' +
      '<p class="tiny muted">' + T('Seller Center opens with the shop’s TikTok account (the same as the TikTok Shop Seller Center app).', 'O Seller Center abre com a conta da loja no TikTok (a mesma do app TikTok Shop Seller Center).') + '</p>';
  }

  var PSTATE = { active: ['On TikTok', 'No TikTok', 'ok'], pending: ['TikTok is reviewing it', 'O TikTok está revisando', 'warn'], draft: ['Draft, not for sale', 'Rascunho, não está à venda', 'warn'],
    failed: ['TikTok didn’t approve it', 'O TikTok não aprovou', 'err'], '': ['Not published yet', 'Ainda não publicado', ''] };

  function products(d) {
    if (!d.connected) return '';
    var rows = st.products;
    if (!rows) {
      if (!st.loadingProducts) {
        st.loadingProducts = true;
        h.call('adminTikTok', { action: 'products', check: true }).then(function (res) { st.products = res.products || []; })
          .catch(function (e) { st.products = []; h.toast(errText(e), true); })
          .then(function () { st.loadingProducts = false; if (A.parseHash().view === 'tiktok') h.route(); });
      }
      return '<section class="card"><div class="card-head"><h2>' + T('Products', 'Produtos') + '</h2></div><div class="loading"><span>' + T('Loading…', 'Carregando…') + '</span></div></section>';
    }
    var left = rows.filter(function (p) { return p.state !== 'active' && p.state !== 'pending'; }).length;
    var btn = st.publishing
      ? '<p class="small"><b>' + T('Publishing ', 'Publicando ') + st.at + T(' of ', ' de ') + st.total + '…</b> ' + esc(st.current) + '<br><span class="muted">' + T('Keep this screen open. Each one takes about a minute.', 'Deixe esta tela aberta. Cada um leva mais ou menos um minuto.') + '</span></p>'
      : left ? '<p><button class="btn btn-honey" data-act="ttPublish">' + icon('shop') + T('Publish the ' + left + ' that are missing', 'Publicar os ' + left + ' que faltam') + '</button></p>' : '';
    var list = rows.map(function (p) {
      var s = PSTATE[p.state] || PSTATE[''];
      return '<li class="et-row"><div><b>' + esc(p.name) + '</b><span class="small muted"> · ' + p.designs + T(' designs', ' designs') + '</span>' +
        (p.error ? '<div class="small err">' + esc(errText({ message: p.error })) + '</div>' : '') + '</div>' +
        (p.state === 'active' && p.productId ? '<a class="pill ok" href="https://www.tiktok.com/view/product/' + esc(p.productId) + '" target="_blank" rel="noopener">' + esc(T(s[0], s[1])) + ' ' + icon('external') + '</a>'
          : '<span class="pill ' + s[2] + '">' + esc(T(s[0], s[1])) + '</span>') + '</li>';
    }).join('');
    return '<section class="card"><div class="card-head"><div><h2>' + T('Products', 'Produtos') + '</h2><p class="sub">' +
      T('The site’s design collections, in the site’s order, with photos in the site’s look and the site’s price ($5 a magnet).',
        'As coleções de design do site, na ordem do site, com fotos no visual do site e o preço do site ($5 o ímã).') + '</p></div></div>' +
      btn + '<ul class="et-list">' + list + '</ul></section>';
  }

  V.tiktok = function (r) {
    var code = r.q.get('code'), state = r.q.get('state'), error = r.q.get('error');
    if ((code || error) && !st.finishing) {
      st.finishing = true;
      if (history.replaceState) history.replaceState(null, '', '#tiktok');
      if (error || !code) { h.toast(T('TikTok wasn’t connected: ', 'O TikTok não foi conectado: ') + (error || 'no code'), true); st.finishing = false; }
      else {
        h.call('adminTikTok', { action: 'finish', code: code, state: state }).then(function (d) { st.data = d; h.toast(T('TikTok Shop connected.', 'TikTok Shop conectado.')); })
          .catch(function (e) { h.toast(errText(e), true); })
          .then(function () { st.finishing = false; h.route(); });
      }
    }
    if (!st.data && !st.err) load();
    var d = st.data;
    var body = st.err ? '<p class="err">' + esc(st.err) + '</p>'
      : !d || st.finishing ? '<div class="loading"><span>' + (st.finishing ? T('Connecting to TikTok…', 'Conectando ao TikTok…') : T('Loading…', 'Carregando…')) + '</span></div>'
      : connection(d) + products(d);
    var html = '<div translate="no" class="tt-page"><div class="page-head"><div><p class="eyebrow">' + T('Sales channels', 'Canais de venda') + '</p><h1>TikTok Shop</h1>' +
      '<p class="sub">' + T('The Little Hive House shop on TikTok, run from here.', 'A loja Little Hive House no TikTok, cuidada daqui.') + '</p></div></div>' + body + '</div>';
    return { title: 'TikTok Shop', html: html };
  };

  function saveSecret(form) {
    var v = (form.querySelector('[name=secret]') || {}).value || '';
    if (!v.trim()) { h.toast(T('Paste the app secret first.', 'Cole a chave secreta primeiro.'), true); return; }
    st.saving = true; h.route();
    h.call('adminTikTok', { action: 'saveSecret', secret: v }).then(function (d) { st.data = d; h.toast(T('Saved.', 'Guardada.')); })
      .catch(function (e) { h.toast(errText(e), true); })
      .then(function () { st.saving = false; h.route(); });
  }
  document.addEventListener('submit', function (ev) {
    var f = ev.target;
    if (!f || f.getAttribute('data-form') !== 'ttSecret') return;
    ev.preventDefault();
    saveSecret(f);
  }, true);

  ACT.ttNewSecret = function () { if (st.data) { st.data.secret = false; st.data.secretEnd = ''; h.route(); } };
  ACT.ttConnect = function (el) {
    el.disabled = true;
    h.call('adminTikTok', { action: 'start' }).then(function (res) { location.href = res.url; })
      .catch(function (e) { el.disabled = false; h.toast(errText(e), true); });
  };
  ACT.ttPublish = function () {
    var todo = (st.products || []).filter(function (p) { return p.state !== 'active' && p.state !== 'pending'; });
    st.publishing = true; st.total = todo.length; st.at = 0;
    var failed = 0;
    var next = function (i) {
      if (i >= todo.length) {
        st.publishing = false;
        h.toast(failed ? T(failed + ' didn’t publish. See the note next to them.', failed + (failed === 1 ? ' não publicou' : ' não publicaram') + '. Veja o aviso ao lado.') : T('All sent to TikTok. TikTok reviews each one before it goes on sale.', 'Tudo enviado ao TikTok. O TikTok revisa cada um antes de pôr à venda.'), !!failed);
        st.products = null; h.route(); return;
      }
      st.at = i + 1; st.current = todo[i].name; h.route();
      var row = todo[i];
      h.call('adminTikTok', { action: 'publish', id: row.id })
        .then(function (res) { if (res && res.product) { Object.assign(row, res.product); row.error = ''; } })
        .catch(function (e) { failed += 1; row.error = errText(e); })
        .then(function () { next(i + 1); });
    };
    next(0);
  };
  ACT.ttDisconnect = function () {
    if (!confirm(T('Disconnect TikTok Shop? Products and orders stop syncing until you connect again.', 'Desconectar o TikTok Shop? Produtos e pedidos param de sincronizar até conectar de novo.'))) return;
    h.call('adminTikTok', { action: 'disconnect' }).then(function (d) { st.data = d; h.route(); }).catch(function (e) { h.toast(errText(e), true); });
  };
})();
