/* Little Hive House admin: Etsy (functions/etsy.js). Connect the shop's Etsy store once, then publish the prepared
   listings (texts, tags, prices, variations, photos) with one tap. The tokens never come to the app.
   Etsy sends the owner back to admin/etsy-callback.html, which opens #etsy?code=…&state=… here.
   The screen picks its own language (T(en, pt)), translate="no". */
(function () {
  'use strict';
  var A = window.LHHAdmin, h = A.h, V = A.VIEWS, ACT = A.ACT;
  var esc = h.esc, icon = h.icon;
  function T(en, pt) { return h.LANG() === 'pt' ? pt : en; }
  var st = { data: null, loading: false, err: '', finishing: false, publishing: false, at: 0, total: 0, current: '' };

  function load() {
    if (st.loading) return;
    st.loading = true;
    h.call('adminEtsy', { action: 'status' }).then(function (d) { st.data = d; st.err = ''; })
      .catch(function (e) { st.err = h.friendlyError(e); })
      .then(function () { st.loading = false; if (A.parseHash().view === 'etsy') h.route(); });
  }

  var STATE = { active: ['On Etsy', 'No Etsy', 'ok'], draft: ['Draft, not finished', 'Rascunho, não terminou', 'warn'], '': ['Not published yet', 'Ainda não publicado', ''] };

  function connection(d) {
    var steps;
    if (!d.keystring) {
      steps = '<p>' + T('The Etsy key isn’t saved yet. In GitHub, add the secret ', 'A chave do Etsy ainda não foi guardada. No GitHub, crie o segredo ') + '<code>ETSY_KEYSTRING</code>' +
        T(' with the Keystring of your app on etsy.com/developers.', ' com o Keystring do app em etsy.com/developers.') + '</p>';
    } else if (!d.secret) {
      steps = '<p>' + T('Etsy is still approving your app (“Pending Personal Approval”). When they approve it, save the Shared secret in GitHub as ',
        'O Etsy ainda está aprovando o app (“Pending Personal Approval”). Quando aprovar, guarde o Shared secret no GitHub como ') + '<code>ETSY_SHARED_SECRET</code>' +
        T(' and tell Claude, who updates the store. Then the Connect button shows up here.', ' e avise o Claude, que atualiza a loja. Aí o botão de conectar aparece aqui.') + '</p>';
    } else if (!d.connected) {
      steps = '<p>' + T('You go to Etsy, tap Allow, and come back here.', 'Você vai para o Etsy, toca em Allow e volta para cá.') + '</p>' +
        '<p><button class="btn btn-honey" data-act="etsyConnect">' + icon('external') + T('Connect Etsy', 'Conectar Etsy') + '</button></p>';
    } else {
      var s = d.shop || {};
      steps = '<p class="ok">' + icon('check') + ' ' + T('Connected to ', 'Conectado à loja ') + '<b>' + esc(s.name || 'Etsy') + '</b>' +
        (s.url ? ' · <a href="' + esc(s.url) + '" target="_blank" rel="noopener">' + T('Open the shop', 'Abrir a loja') + ' ' + icon('external') + '</a>' : '') + '</p>' +
        (d.category ? '<p class="small muted">' + T('Category: ', 'Categoria: ') + esc(d.category) + '</p>' : '') +
        '<p><button class="linkish small" data-act="etsyDisconnect">' + T('Disconnect', 'Desconectar') + '</button></p>';
    }
    return '<section class="card"><div class="card-head"><h2>' + T('Connection', 'Conexão') + '</h2></div>' + steps + '</section>';
  }

  function listings(d) {
    var rows = d.listings || [];
    var left = rows.filter(function (l) { return l.state !== 'active'; }).length;
    var btn = !d.connected ? '' : st.publishing
      ? '<p class="small"><b>' + T('Publishing ', 'Publicando ') + st.at + T(' of ', ' de ') + st.total + '…</b> ' + esc(st.current) + '<br><span class="muted">' + T('Keep this screen open. Each one takes about half a minute.', 'Deixe esta tela aberta. Cada um leva mais ou menos meio minuto.') + '</span></p>'
      : left ? '<p><button class="btn btn-honey" data-act="etsyPublish">' + icon('shop') + T('Publish the ' + left + ' that are missing', 'Publicar os ' + left + ' que faltam') + '</button></p>' +
        '<p class="tiny muted">' + T('Etsy charges $0.20 for each listing.', 'O Etsy cobra $0,20 por produto publicado.') + '</p>' : '';
    var list = rows.map(function (l) {
      var s = STATE[l.state] || STATE[''];
      return '<li class="et-row"><div><b>' + esc(l.name) + '</b><span class="small muted"> · ' + esc(l.section) + ' · ' + l.images + T(' photos', ' fotos') + '</span>' +
        (l.error ? '<div class="small err">' + esc(l.error) + '</div>' : '') + '</div>' +
        (l.state === 'active' && l.url ? '<a class="pill ok" href="' + esc(l.url) + '" target="_blank" rel="noopener">' + esc(T(s[0], s[1])) + ' ' + icon('external') + '</a>'
          : '<span class="pill ' + s[2] + '">' + esc(T(s[0], s[1])) + '</span>') + '</li>';
    }).join('');
    return '<section class="card"><div class="card-head"><div><h2>' + T('Listings', 'Produtos') + '</h2><p class="sub">' +
      T('Ready with photos, texts, tags, prices and variations, the same as the “Etsy shop” page.', 'Prontos com fotos, textos, tags, preços e variações, os mesmos da página “Loja no Etsy”.') + '</p></div></div>' +
      btn + '<ul class="et-list">' + list + '</ul></section>';
  }

  function manual() {
    var items = [
      T('Shop texts (title, announcement, about, policies): copy them from the “Etsy shop” page.', 'Textos da loja (título, aviso, história, políticas): copie da página “Loja no Etsy”.'),
      T('Free US shipping on orders of $35 or more: Shop Manager › Settings › Shipping settings.', 'Frete grátis a partir de $35: Shop Manager › Settings › Shipping settings.'),
      T('20% off 3 or more items: Shop Manager › Marketing › Sales and discounts › Run a sale.', '20% de desconto em 3 ou mais: Shop Manager › Marketing › Sales and discounts › Run a sale.'),
      T('Offsite Ads, if you don’t want them: Shop Manager › Settings › Offsite Ads.', 'Offsite Ads, se não quiserem: Shop Manager › Settings › Offsite Ads.'),
    ];
    return '<section class="card"><div class="card-head"><h2>' + T('Done by hand on Etsy', 'Feito à mão no Etsy') + '</h2></div><p class="small muted">' +
      T('Etsy doesn’t let apps change these, so they’re a few taps in Etsy’s Shop Manager.', 'O Etsy não deixa um app mudar estas coisas, então são alguns toques no Shop Manager do Etsy.') + '</p><ul class="et-todo">' +
      items.map(function (t) { return '<li>' + esc(t) + '</li>'; }).join('') + '</ul></section>';
  }

  V.etsy = function (r) {
    var code = r.q.get('code'), state = r.q.get('state'), error = r.q.get('error');
    if ((code || error) && !st.finishing) {
      st.finishing = true;
      if (history.replaceState) history.replaceState(null, '', '#etsy');
      if (error) { h.toast(T('Etsy wasn’t connected: ', 'O Etsy não foi conectado: ') + error, true); st.finishing = false; }
      else {
        h.call('adminEtsy', { action: 'finish', code: code, state: state }).then(function (d) { st.data = d; h.toast(T('Etsy connected.', 'Etsy conectado.')); })
          .catch(function (e) { h.toast(h.friendlyError(e), true); })
          .then(function () { st.finishing = false; h.route(); });
      }
    }
    if (!st.data && !st.err) load();
    var d = st.data;
    var body = st.err ? '<p class="err">' + esc(st.err) + '</p>'
      : !d || st.finishing ? '<div class="loading"><span>' + (st.finishing ? T('Connecting to Etsy…', 'Conectando ao Etsy…') : T('Loading…', 'Carregando…')) + '</span></div>'
      : connection(d) + listings(d) + manual();
    var html = '<div translate="no" class="et-page"><div class="page-head"><div><p class="eyebrow">' + T('Sales channels', 'Canais de venda') + '</p><h1>Etsy</h1>' +
      '<p class="sub">' + T('The LittleHiveHouse shop on Etsy, run from here.', 'A loja LittleHiveHouse no Etsy, cuidada daqui.') + '</p></div></div>' + body + '</div>';
    return { title: 'Etsy', html: html };
  };

  ACT.etsyConnect = function (el) {
    el.disabled = true;
    h.call('adminEtsy', { action: 'start' }).then(function (res) { location.href = res.url; })
      .catch(function (e) { el.disabled = false; h.toast(h.friendlyError(e), true); });
  };
  ACT.etsyDisconnect = function () {
    h.call('adminEtsy', { action: 'disconnect' }).then(function (d) { st.data = d; h.route(); }).catch(function (e) { h.toast(h.friendlyError(e), true); });
  };
  ACT.etsyPublish = function () {
    var todo = (st.data.listings || []).filter(function (l) { return l.state !== 'active'; });
    st.publishing = true; st.total = todo.length; st.at = 0;
    var failed = 0;
    var next = function (i) {
      if (i >= todo.length) {
        st.publishing = false;
        h.toast(failed ? T(failed + ' didn’t publish. See the note next to them.', failed + (failed === 1 ? ' não publicou' : ' não publicaram') + '. Veja o aviso ao lado.') : T('All published on Etsy.', 'Tudo publicado no Etsy.'), !!failed);
        st.data = null; load(); return;
      }
      st.at = i + 1; st.current = todo[i].name; h.route();
      var row = (st.data.listings || []).find(function (l) { return l.id === todo[i].id; });
      h.call('adminEtsy', { action: 'publish', id: todo[i].id })
        .then(function (res) { if (row && res && res.listing) { Object.assign(row, res.listing); row.error = ''; } })
        .catch(function (e) { failed += 1; if (row) row.error = h.friendlyError(e); })
        .then(function () { next(i + 1); });
    };
    next(0);
  };
})();
