/* Little Hive House admin: Ads (functions/ads.js adminAds). The month's cap the owners approve, what each channel spends
   and sells, the Instagram posts the robot boosts (and the owners' say over each one), Etsy advice, spend logged by hand
   and what the robot did and why. The screen picks its own language (T(en, pt)) and is marked translate="no". */
(function () {
  'use strict';
  var A = window.LHHAdmin, h = A.h, V = A.VIEWS, ACT = A.ACT;
  var esc = h.esc, money = h.money;
  function T(en, pt) { return h.LANG() === 'pt' ? pt : en; }
  var st = { data: null, err: null, loading: false, busy: false };

  function load(action, args, done) {
    st.busy = true;
    if (A.parseHash().view === 'ads') { var y0 = scrollY; h.route(); scrollTo(0, y0); }
    return h.call('adminAds', Object.assign({ action: action || 'view' }, args || {})).then(function (d) { st.data = d; st.err = null; if (done) h.toast(done); })
      .catch(function (e) { var m = h.friendlyError(e); if (!action || action === 'view') st.err = m; else h.toast(m, true); })
      .then(function () { st.busy = false; st.loading = false; if (A.parseHash().view === 'ads') { var y = scrollY; h.route(); scrollTo(0, y); } });
  }
  function n2(v) { return (Math.round((Number(v) || 0) * 100) / 100).toLocaleString(h.LANG() === 'pt' ? 'pt-BR' : 'en-US', { minimumFractionDigits: 0, maximumFractionDigits: 2 }); }
  function dollars(v) { return money(v); }
  function day(k) { return h.fmtDate(k + 'T12:00:00'); }

  var NAMES = {
    meta: ['Instagram & Facebook', 'Instagram e Facebook'], etsy: ['Etsy Ads', 'Etsy Ads'], google: ['Google', 'Google'], tiktok: ['TikTok', 'TikTok'], amazon: ['Amazon', 'Amazon'], all: ['All', 'Todos']
  };
  function cname(k) { var n = NAMES[k] || [k, k]; return T(n[0], n[1]); }

  /* ---------- is it worth it? ----------
     A sale isn't all profit: magnets, packaging, label and fees come out of it. The share left is the shop's real margin
     over the last 90 days (Reports' numbers, without the ads), or 45% until there are a few orders. Etsy keeps about 9.5%
     more (transaction 6.5% + payment 3% + $0.25). Profit from the ads = sales from the ads x margin - what the ads cost. */
  var TEST = 10;   // under $10 spent it's too early to judge
  function margin() {
    var R = A.R, S = A.S, out = { pct: 0.45, est: true, orders: 0 };
    try {
      if (!S.orders || !R || !R.summarize) return out;
      var to = Date.now(), m = R.summarize(S.orders, Object.assign({}, S.settings, { adSpendByDay: {} }), { from: to - 90 * 86400000, to: to }, { months: 3 });
      if (m.orders >= 3 && m.netSales > 0) { out.pct = Math.min(0.8, Math.max(0.05, m.profit / m.netSales)); out.est = false; out.orders = m.orders; }
    } catch (e) { /* keep the estimate */ }
    return out;
  }
  function verdict(spend, sales, pct) {
    var profit = Math.round((sales * pct - spend) * 100) / 100;
    if (spend < 0.01 && sales < 0.01) return { kind: 'idle', profit: 0 };
    if (profit >= 0 && sales > 0) return { kind: 'good', profit: profit };
    if (spend < TEST) return { kind: 'early', profit: profit };
    return { kind: 'bad', profit: profit };
  }
  var VERDICT = {
    idle: ['Nothing spent yet', 'Nada gasto ainda'], early: ['Too early to tell', 'Ainda é cedo para saber'],
    good: ['Worth it', 'Está valendo a pena'], bad: ['Not worth it', 'Não está valendo a pena']
  };
  function signed(v) { return (v < 0 ? '−' : '+') + money(Math.abs(v)); }
  function worth(d) {
    var t = d.totals, mg = margin(), etsyPct = Math.max(0.02, mg.pct - 0.095);
    var rows = [
      { k: 'meta', spend: t.spend.meta, sales: t.sales.meta, pct: mg.pct },
      { k: 'etsy', spend: t.spend.etsy, sales: t.sales.etsy, pct: etsyPct }
    ];
    var other = (t.spend.google || 0) + (t.spend.tiktok || 0) + (t.spend.amazon || 0);
    if (other > 0) rows.push({ k: 'other', spend: other, sales: 0, pct: mg.pct });
    rows.forEach(function (r) { r.v = verdict(r.spend, r.sales, r.pct); });
    var spend = t.total, profit = Math.round(rows.reduce(function (a, r) { return a + r.v.profit; }, 0) * 100) / 100;
    var sales = Math.round((t.sales.meta + t.sales.etsy) * 100) / 100;
    var all = verdict(spend, sales, sales > 0 ? (profit + spend) / sales : mg.pct);
    var line = function (r) {
      var name = r.k === 'other' ? T('Google, TikTok, Amazon', 'Google, TikTok, Amazon') : cname(r.k);
      var txt = r.v.kind === 'idle' ? T('nothing spent yet', 'nada gasto ainda')
        : T('spent ' + money(r.spend) + ', sold ' + money(r.sales) + ' → ', 'gastou ' + money(r.spend) + ', vendeu ' + money(r.sales) + ' → ') + '<b class="' + (r.v.profit < 0 ? 'neg' : 'pos') + '">' + signed(r.v.profit) + '</b>';
      return '<li><span><b>' + esc(name) + '</b> <span class="ads-v ' + r.v.kind + '">' + esc(T(VERDICT[r.v.kind][0], VERDICT[r.v.kind][1])) + '</span></span><span class="small">' + txt + '</span></li>';
    };
    var head = all.kind === 'good' ? T('Yes. This month the ads left ' + money(profit) + ' of profit after paying for themselves.', 'Sim. Este mês os anúncios deixaram ' + money(profit) + ' de lucro, já pagando o que custaram.')
      : all.kind === 'bad' ? T('No. This month the ads cost ' + money(-profit) + ' more than the profit they brought. The robot stops what doesn’t sell; you can also turn a channel off below.', 'Não. Este mês os anúncios custaram ' + money(-profit) + ' a mais do que o lucro que trouxeram. O robô para o que não vende; vocês também podem desligar um canal aqui embaixo.')
      : all.kind === 'early' ? T('Spent ' + money(spend) + ' so far. It takes about ' + money(TEST) + ' to know; until then the robot limits each post to ' + money(d.config.rules.stopAfter) + ' without a sale.', 'Gastou ' + money(spend) + ' até agora. Precisa de uns ' + money(TEST) + ' para saber; até lá o robô limita cada post a ' + money(d.config.rules.stopAfter) + ' sem venda.')
      : T('When the ads start, this shows here whether they are paying off.', 'Quando os anúncios começarem, aqui vai aparecer se estão dando lucro ou prejuízo.');
    return '<section class="card ads-worth ' + all.kind + '"><p class="eyebrow">' + T('Is it worth it? (this month)', 'Está valendo a pena? (este mês)') + '</p>' +
      '<h2>' + esc(T(VERDICT[all.kind][0], VERDICT[all.kind][1])) + (all.kind === 'idle' ? '' : ' <span class="' + (profit < 0 ? 'neg' : 'pos') + '">' + signed(profit) + '</span>') + '</h2>' +
      '<p class="small">' + head + '</p><ul class="ads-worth-list">' + rows.map(line).join('') + '</ul>' +
      '<p class="tiny muted">' + (mg.est ? T('Each sale counts as about 45% profit until the shop has a few more orders; then it uses your real margin.', 'Cada venda conta como uns 45% de lucro até a loja ter mais alguns pedidos; depois usa a margem de verdade de vocês.')
        : T('Each sale counts as ' + Math.round(mg.pct * 100) + '% profit: your real margin over the last 90 days (' + mg.orders + ' orders), after magnets, packaging, label and fees. Etsy keeps about 9.5% more.',
          'Cada venda conta como ' + Math.round(mg.pct * 100) + '% de lucro: a margem de verdade de vocês nos últimos 90 dias (' + mg.orders + ' pedidos), depois de ímãs, embalagem, etiqueta e taxas. O Etsy fica com uns 9,5% a mais.')) + '</p></section>';
  }

  /* ---------- where each sale came from ---------- */
  function hostName(src) {
    var x = String(src || '').toLowerCase();
    if (/instagram/.test(x)) return 'Instagram'; if (/facebook|^fb$/.test(x)) return 'Facebook'; if (/google/.test(x)) return 'Google';
    if (/tiktok/.test(x)) return 'TikTok'; if (/pinterest/.test(x)) return 'Pinterest'; if (/etsy/.test(x)) return 'Etsy';
    return String(src || '').replace(/^l\.|^m\.|^lm\./, '');
  }
  /** One line about what brought a sale (also used in the order page). */
  function originText(o, post) {
    o = o || {};
    var name = hostName(o.source);
    if (o.kind === 'ad') return T('Ad on ' + (name || 'an ad'), 'Anúncio no ' + (name || 'anúncio')) + (post ? ': “' + (post.caption ? post.caption.slice(0, 40) : '#' + post.id.slice(-5)) + '”' : (o.campaign ? ' (' + o.campaign + ')' : ''));
    if (o.kind === 'social') return T(name + ' (normal post or profile, no ad)', name + ' (post normal ou perfil, sem anúncio)');
    if (o.kind === 'search') return T(name + ' search (free)', 'Busca no ' + name + ' (grátis)');
    if (o.kind === 'email') return T('Email to subscribers', 'E-mail para inscritos');
    if (o.kind === 'site') return T('Link on ' + name, 'Link no ' + name);
    return T('Typed the address or unknown', 'Digitou o endereço ou não identificado');
  }
  window.LHHAdsOrigin = function (ref) {
    var r = ref || {}, src = String(r.source || '').toLowerCase(), med = String(r.medium || '').toLowerCase(), kind;
    if (!src && !med) kind = 'direct';
    else if (/^(paid|cpc|ppc|paidsocial|paid_social|ads?)$/.test(med)) kind = 'ad';
    else if (/mail/.test(med) || /mail|newsletter/.test(src)) kind = 'email';
    else if (/google|bing|duckduckgo|yahoo|search/.test(src)) kind = 'search';
    else if (/instagram|facebook|^fb$|tiktok|pinterest/.test(src) || med === 'social') kind = 'social';
    else kind = 'site';
    return originText({ kind: kind, source: r.source, campaign: r.campaign }, /^\d{5,}$/.test(String(r.content || '')) && kind === 'ad' ? { id: String(r.content), caption: '' } : null);
  };
  function salesCard(d) {
    var list = d.sales || [];
    if (!list.length) return '<section class="card gap-top"><div class="card-head"><div><h2>' + T('Where each sale came from (this month)', 'De onde veio cada venda (este mês)') + '</h2>' +
      '<p class="sub">' + T('No site sales this month yet.', 'Nenhuma venda no site este mês ainda.') + '</p></div></div></section>';
    var count = {}; list.forEach(function (x) { count[x.origin.kind] = (count[x.origin.kind] || 0) + 1; });
    return '<section class="card gap-top"><div class="card-head"><div><h2>' + T('Where each sale came from (this month)', 'De onde veio cada venda (este mês)') + '</h2>' +
      '<p class="sub">' + T(list.length + ' site sales · ' + (count.ad || 0) + ' from ads', list.length + ' vendas no site · ' + (count.ad || 0) + ' de anúncios') + '</p></div></div>' +
      '<ul class="sp-buys ads-sales">' + list.map(function (x) {
        return '<li><span><a href="#order/' + encodeURIComponent(x.id) + '"><b>' + esc(x.number || T('Order', 'Pedido')) + '</b></a><small>' + esc(day(x.day)) + ' · ' +
          '<span class="ads-o ' + esc(x.origin.kind) + '">' + esc(originText(x.origin, x.post)) + '</span></small></span><span class="sp-cost">' + money(x.total) + '</span></li>';
      }).join('') + '</ul><p class="tiny muted">' + T('Etsy sales come from Etsy itself; Etsy doesn’t tell apps which ones came from Etsy Ads (its own dashboard shows it).',
        'As vendas do Etsy acontecem no próprio Etsy, e ele não conta para os apps quais vieram do Etsy Ads (o painel do Etsy mostra).') + '</p></section>';
  }

  /* ---------- pieces ---------- */
  function capCard(d) {
    var c = d.config, t = d.totals, pct = c.monthCap > 0 ? Math.min(100, Math.round(t.total / c.monthCap * 100)) : 100;
    var left = Math.max(0, c.monthCap - t.total), daysLeft = d.daysInMonth - d.dayOfMonth + 1;
    var over = d.planned * daysLeft + t.total > c.monthCap + 0.01;
    return '<section class="card ads-cap"><div class="card-head"><div><h2>' + T('Monthly cap', 'Teto do mês') + ': ' + dollars(c.monthCap) + '</h2>' +
      '<p class="sub">' + (c.capAt ? T('Approved by ' + esc(c.capBy || '') + ' on ' + esc(h.fmtDate(c.capAt)), 'Aprovado por ' + esc(c.capBy || '') + ' em ' + esc(h.fmtDate(c.capAt))) :
        T('The most the shop can spend on ads in a month. The robot never goes past it.', 'O máximo que a loja pode gastar com anúncios no mês. O robô nunca passa disso.')) + '</p></div>' +
      '<button class="btn btn-ghost btn-sm" data-act="adsCap">' + T('Change cap', 'Mudar teto') + '</button></div>' +
      '<div class="sp-bar ads-bar' + (pct >= 100 ? ' full' : pct >= 80 ? ' near' : '') + '"><i style="width:' + Math.max(2, pct) + '%"></i></div>' +
      '<p class="small">' + T('Spent <b>' + dollars(t.total) + '</b> so far this month · ' + dollars(left) + ' left for ' + daysLeft + ' days',
        'Gasto até agora no mês: <b>' + dollars(t.total) + '</b> · sobram ' + dollars(left) + ' para ' + daysLeft + ' dias') + '</p>' +
      '<p class="small muted">' + T('Plan: ' + dollars(d.planned) + ' a day on the channels that are on (about ' + dollars(d.planned * d.daysInMonth) + ' a month).',
        'Plano: ' + dollars(d.planned) + ' por dia nos canais ligados (uns ' + dollars(d.planned * d.daysInMonth) + ' por mês).') +
      (over ? ' <b>' + T('That passes the cap: the robot spends less each day so it fits.', 'Isso passa do teto: o robô gasta menos por dia para caber.') + '</b>' : '') + '</p>' +
      '<label class="ads-auto"><input type="checkbox" data-act="adsAuto"' + (c.auto ? ' checked' : '') + (st.busy ? ' disabled' : '') + '> ' +
        T('The robot chooses and swaps by itself (every morning, inside the cap); you can change it whenever you want', 'O robô escolhe e troca sozinho (toda manhã, dentro do teto); vocês podem mudar quando quiserem') + '</label></section>';
  }

  function proposals(d) {
    if (!d.proposals.length) return '';
    return d.proposals.map(function (p) {
      return '<section class="card ads-prop"><p><b>' + T('The robot asks', 'O robô pede') + ':</b> ' + esc(T(p.en || p.pt, p.pt)) + '</p><div class="row">' +
        '<button class="btn btn-honey btn-sm" data-act="adsApprove" data-id="' + esc(p.id) + '"' + (st.busy ? ' disabled' : '') + '>' + T('Approve', 'Aprovar') + '</button>' +
        '<button class="btn btn-ghost btn-sm" data-act="adsDecline" data-id="' + esc(p.id) + '"' + (st.busy ? ' disabled' : '') + '>' + T('No, keep it', 'Não, deixa assim') + '</button></div></section>';
    }).join('');
  }

  function tiles(d) {
    var t = d.totals, sales = Math.round((t.sales.ads + t.sales.etsy) * 100) / 100, orders = t.sales.adOrders + t.sales.etsyOrders;
    var ret = t.total > 0 ? sales / t.total : null;
    return '<div class="tiles">' +
      h.tile(T('Spent this month', 'Gasto no mês'), dollars(t.total), T('of ' + dollars(d.config.monthCap), 'de ' + dollars(d.config.monthCap)), true) +
      h.tile(T('Sales from ads', 'Vendas dos anúncios'), dollars(sales), orders ? T(orders + (orders === 1 ? ' order' : ' orders'), orders + (orders === 1 ? ' pedido' : ' pedidos')) : T('None yet', 'Nenhuma ainda')) +
      h.tile(T('Return', 'Retorno'), ret == null ? '—' : dollars(ret), ret == null ? T('per $1 spent', 'para cada $1 gasto') : T('back for each $1 spent', 'de volta para cada $1 gasto')) +
      h.tile(T('Site sales this month', 'Vendas do site no mês'), dollars(t.sales.site), T('all sales, with or without ads', 'todas, com ou sem anúncio')) +
      '</div>';
  }

  function chan(d, k) {
    var c = d.config.channels[k], t = d.totals, spend = t.spend[k] || 0;
    var head = '<div class="sp-top"><b>' + esc(cname(k)) + '</b><span class="sp-pill">' + (c.on ? T('On', 'Ligado') + ' · ' + dollars(c.daily) + T('/day', '/dia') : T('Off', 'Desligado')) + '</span></div>';
    var body = '', acts = '<button class="btn btn-ghost btn-sm" data-act="adsChan" data-k="' + k + '"' + (st.busy ? ' disabled' : '') + '>' + T('Change', 'Mudar') + '</button>';
    if (k === 'meta') {
      var m = d.meta;
      if (!m.connected) {
        body = '<p class="small">' + T('Not connected yet. Connect once and the robot boosts your best Instagram posts, pauses the ones that don’t sell and keeps inside the cap.',
          'Ainda não conectado. Conecte uma vez e o robô impulsiona os melhores posts do Instagram, pausa os que não vendem e fica dentro do teto.') + '</p>';
        acts = '<button class="btn btn-honey btn-sm" data-act="adsConnect"' + (st.busy ? ' disabled' : '') + '>' + T('Connect Meta', 'Conectar Meta') + '</button>' + acts;
      } else {
        body = '<p class="small">' + T('Ad account', 'Conta de anúncios') + ': <b>' + esc(m.accountName || m.adAccountId) + '</b>' + (m.igUsername ? ' · Instagram <b>@' + esc(m.igUsername) + '</b>' : '') + '</p>' +
          (m.igReady ? '' : '<p class="small err">' + T('The Instagram account or the Facebook Page isn’t linked to this token, so no post can be boosted. Give the system user the Page and the Instagram account and connect again.',
            'A conta do Instagram ou a página do Facebook não está ligada a este token, então nenhum post pode ser impulsionado. Dê ao usuário do sistema a página e o Instagram e conecte de novo.') + '</p>') +
          (m.accountStatus && m.accountStatus !== 1 ? '<p class="small err">' + T('Meta says the ad account isn’t active (status ' + esc(m.accountStatus) + '). Check the payment method in Meta.', 'O Meta diz que a conta de anúncios não está ativa (status ' + esc(m.accountStatus) + '). Confira a forma de pagamento no Meta.') + '</p>' : '') +
          '<p class="small">' + T('This month: spent ', 'Este mês: gastou ') + '<b>' + dollars(spend) + '</b> · ' + T('sales from the ads ', 'vendas pelos anúncios ') + '<b>' + dollars(t.sales.meta) + '</b></p>' +
          '<p class="tiny ' + (d.pixel ? 'muted' : 'err') + '">' + (d.pixel ? T('Meta Pixel on: Meta sees the visits, carts and sales the ads bring.', 'Pixel do Meta ligado: o Meta vê as visitas, carrinhos e vendas que os anúncios trazem.')
            : T('Meta Pixel not set up yet.', 'Pixel do Meta ainda não configurado.')) + '</p>';
        acts += '<button class="btn btn-ghost btn-sm" data-act="adsConnect"' + (st.busy ? ' disabled' : '') + '>' + T('Connect again', 'Conectar de novo') + '</button>';
      }
    } else if (k === 'etsy') {
      var a = d.etsy.advice || {};
      body = (d.etsy.connected ? '<p class="small">' + T('Read from Etsy by itself: spent ', 'Lido do Etsy sozinho: gastou ') + '<b>' + dollars(spend) + '</b> · ' + T('Etsy sales ', 'vendas no Etsy ') + '<b>' + dollars(t.sales.etsy) + '</b></p>'
        : '<p class="small err">' + T('Etsy isn’t connected, so the app can’t read the ad spend. Connect it on the Etsy page.', 'O Etsy não está conectado, então o app não consegue ler o gasto. Conecte na página do Etsy.') + '</p>') +
        (a.pt ? '<p class="small ads-advice ' + esc(a.kind || '') + '">' + esc(T(a.en || a.pt, a.pt)) + '</p>' : '') +
        '<p class="tiny muted">' + T('Etsy doesn’t let any app change Etsy Ads: the budget is set in the Etsy app (Shop Manager › Marketing › Etsy Ads).', 'O Etsy não deixa nenhum app mudar o Etsy Ads: o orçamento é colocado no app do Etsy (Gerenciador da loja › Marketing › Etsy Ads).') + '</p>';
      acts = '<a class="btn btn-ghost btn-sm" href="https://www.etsy.com/your/shops/me/advertising" target="_blank" rel="noopener">' + T('Open Etsy Ads', 'Abrir Etsy Ads') + ' ›</a>' + acts;
    } else {
      var why = {
        google: ['Free first: your products in Google Shopping through Merchant Center. Paid Google ads come later.', 'Primeiro o grátis: os produtos no Google Shopping pelo Merchant Center. O anúncio pago do Google vem depois.'],
        tiktok: ['TikTok ads start at $20 a day, too much for now. Keep posting videos for free.', 'O TikTok cobra no mínimo $20 por dia, muito para agora. Continuem postando vídeos de graça.'],
        amazon: ['Comes in when the Amazon seller account is approved.', 'Entra quando a conta de vendedor da Amazon for aprovada.']
      }[k];
      body = '<p class="small">' + esc(T(why[0], why[1])) + '</p>' + (spend ? '<p class="small">' + T('Logged by hand this month: ', 'Registrado à mão este mês: ') + '<b>' + dollars(spend) + '</b></p>' : '');
      acts = '<button class="btn btn-ghost btn-sm" data-act="adsManual" data-k="' + k + '"' + (st.busy ? ' disabled' : '') + '>' + T('Log spend', 'Registrar gasto') + '</button>' + acts;
    }
    return '<section class="card sp-card ads-chan' + (c.on ? '' : ' off') + '">' + head + body + '<div class="row sp-acts">' + acts + '</div></section>';
  }

  function boostLine(b) {
    var who = !b.by || b.by === 'robot' ? T('chosen by the robot', 'escolhido pelo robô') : T('chosen by you', 'escolhido por vocês');
    var why = { 'no-sales': T('Stopped: spent and nobody put it in the cart', 'Parado: gastou e ninguém pôs no carrinho'), tired: T('Paused: the same people saw it 4+ times', 'Pausado: as mesmas pessoas já viram 4+ vezes'),
      reel: T('Paused: gave its place to a Reel', 'Pausado: deu lugar a um Reel'), room: T('Paused: gave its place to the new Reel', 'Pausado: deu lugar ao Reel novo'),
      cap: T('Paused: cap reached', 'Pausado: teto do mês'), season: T('Paused until January (post office)', 'Pausado até janeiro (Correios)') };
    var stat = b.status === 'active' ? T('Boosting', 'Impulsionando') + ' · ' + who
      : b.why === 'owner' ? (b.status === 'stopped' ? T('Never boost', 'Nunca impulsionar') : T('Paused by you', 'Pausado por vocês'))
      : why[b.why] || T('Paused', 'Pausado');
    return '<span class="sp-pill ads-' + esc(b.status) + '">' + esc(stat) + '</span>';
  }
  function warnLine(b) {
    if (!b || b.status !== 'active' || !b.warn) return '';
    return '<p class="tiny ct-warn">' + esc(b.warn === 'tired' ? T('Getting tired: the same people saw it 4+ times. Worth swapping.', 'Cansando: as mesmas pessoas já viram 4+ vezes. Vale trocar.')
      : T('Spent ' + money(b.spend) + ' and nobody put it in the cart. Worth swapping.', 'Gastou ' + money(b.spend) + ' e ninguém pôs no carrinho. Vale trocar.')) + '</p>';
  }
  function postCard(p, b) {
    var x = b || {};
    var img = /^https:\/\//.test(p.thumb || x.thumb || '') ? '<img src="' + esc(p.thumb || x.thumb) + '" alt="" loading="lazy" referrerpolicy="no-referrer">' : '<span class="ads-noimg"></span>';
    var link = /^https:\/\//.test(p.permalink || x.permalink || '') ? '<a class="tiny" href="' + esc(p.permalink || x.permalink) + '" target="_blank" rel="noopener">' + T('See on Instagram', 'Ver no Instagram') + ' ›</a>' : '';
    var numbers = b ? '<p class="tiny">' + T('Spent ', 'Gastou ') + '<b>' + dollars(x.spend) + '</b> · ' + n2(x.clicks) + (x.clicks === 1 ? T(' click', ' clique') : T(' clicks', ' cliques')) + ' · ' +
      (x.carts > 0 ? n2(x.carts) + T(' in cart · ', ' no carrinho · ') : '') +
      (x.revenue > 0 ? T('sold ', 'vendeu ') + '<b>' + dollars(x.revenue) + '</b>' : T('no sale yet', 'nenhuma venda ainda')) + '</p>' + warnLine(b) :
      '<p class="tiny muted">' + n2(p.likes) + ' ♥ · ' + n2(p.comments) + (p.comments === 1 ? T(' comment', ' comentário') : T(' comments', ' comentários')) + (p.at ? ' · ' + esc(h.fmtDate(p.at)) : '') + '</p>' +
      (p.views || p.reach ? '<p class="tiny muted">' + n2(p.views) + T(' views · ', ' visualizações · ') + n2(p.shares) + T(' sends · ', ' envios · ') + n2(p.saves) + T(' saves', ' salvos') +
        (p.watch ? ' · ' + n2(p.watch) + T(' s watched on average', ' s assistidos em média') : '') + '</p>' : '');
    var dis = st.busy ? ' disabled' : '';
    var btns = '';
    if (b && b.status === 'active') btns = '<button class="btn btn-ghost btn-sm" data-act="adsPost" data-what="pause" data-id="' + esc(x.id) + '"' + dis + '>' + T('Pause', 'Pausar') + '</button>';
    else if (p.never || (b && b.why === 'owner' && b.status === 'stopped')) btns = '<button class="btn btn-ghost btn-sm" data-act="adsPost" data-what="allow" data-id="' + esc(p.id || x.id) + '"' + dis + '>' + T('Let the robot choose', 'Deixar o robô escolher') + '</button>';
    else if (p.eligible === false) btns = '<span class="tiny muted">' + T('Meta doesn’t allow boosting this one', 'O Meta não deixa impulsionar este') + '</span>';
    else btns = '<button class="btn btn-honey btn-sm" data-act="adsPost" data-what="boost" data-id="' + esc(p.id || x.id) + '"' + dis + '>' + T('Boost now', 'Impulsionar') + '</button>';
    if (!(b && b.status === 'stopped' && b.why === 'owner') && !p.never) btns += '<button class="btn btn-ghost btn-sm" data-act="adsPost" data-what="never" data-id="' + esc(p.id || x.id) + '"' + dis + '>' + T('Never', 'Nunca') + '</button>';
    return '<article class="card ads-post">' + img + '<div class="ads-post-in"><div class="sp-top">' + (b ? boostLine(x) : (p.never ? '<span class="sp-pill">' + T('Never boost', 'Nunca impulsionar') + '</span>' : '<span class="sp-pill">' + (p.type === 'reel' ? 'Reel · ' : '') + T('In line', 'Na fila') + '</span>')) + link + '</div>' +
      '<p class="small ads-cap-text">' + esc(p.caption || x.caption || T('(no caption)', '(sem legenda)')) + '</p>' + numbers + '<div class="row sp-acts">' + btns + '</div></div></article>';
  }
  function posts(d) {
    if (!d.meta.connected) return '';
    var byId = {}; d.boosts.forEach(function (b) { byId[b.id] = b; });
    var boosted = d.boosts.map(function (b) { var p = d.posts.find(function (x) { return x.id === b.id; }) || {}; return postCard(Object.assign({ id: b.id }, p), b); }).join('');
    var line = d.posts.filter(function (p) { return !byId[p.id]; }).slice(0, 12).map(function (p) { return postCard(p, null); }).join('');
    var dis = st.busy ? ' disabled' : '';
    var next = d.nextReel ? '<section class="card ads-next"><p class="small"><b>' + T('Waiting for the next Reel.', 'Esperando o próximo Reel.') + '</b> ' +
        T('As soon as it’s out on Instagram it is boosted first (checked every 5 minutes).', 'Assim que sair no Instagram ele é impulsionado primeiro (confere a cada 5 minutos).') + '</p>' +
        '<div class="row sp-acts"><button class="btn btn-ghost btn-sm" data-act="adsNextReel" data-on="0"' + dis + '>' + T('Cancel', 'Cancelar') + '</button></div></section>'
      : '<div class="row sp-acts"><button class="btn btn-ghost btn-sm" data-act="adsNextReel" data-on="1"' + dis + '>' + T('Boost the next Reel that goes out', 'Impulsionar o próximo Reel que sair') + '</button></div>';
    var active = d.boosts.filter(function (b) { return b.status === 'active'; }).length;
    var seasonNote = d.season === 'shipping' ? T('From Dec 15 the post office can’t deliver by Christmas: the ads rest until January.', 'Depois de 15/dez os Correios não entregam antes do Natal: os anúncios descansam até janeiro.')
      : d.season === 'lastcall' ? T('Dec 2–14: last days to buy for Christmas, so the day’s budget is doubled (inside the cap).', '2 a 14/dez: últimos dias para comprar para o Natal, então o orçamento do dia dobra (dentro do teto).')
      : d.season === 'peak' ? T('Black Friday week: ads cost the most now, so the budget stays the usual.', 'Semana da Black Friday: o anúncio está mais caro, então o orçamento fica o de sempre.') : '';
    var budget = '<p class="small">' + (active ? T('Today: ' + dollars(d.allowed) + ' for all ' + active + ' boosted posts together; Meta puts more into the one that works.',
        'Hoje: ' + dollars(d.allowed) + ' para os ' + active + ' posts impulsionados juntos; o Meta põe mais no que funciona.') : '') + (seasonNote ? ' ' + esc(seasonNote) : '') + '</p>';
    var aud = '<p class="tiny muted">' + T('Who sees them: only people who live in the US, 25 to 65', 'Quem vê: só quem mora nos EUA, de 25 a 65 anos') +
      (d.audience && d.audience.length ? ' · ' + esc(d.audience.join(', ')) : '') + '. ' +
      T('The groups follow what is boosted; Meta goes further only where it finds buyers.', 'Os grupos seguem o que está impulsionado; o Meta só vai além onde acha compradores.') + '</p>';
    return '<h2 class="sp-h2">' + T('Boosted posts', 'Posts impulsionados') + '</h2>' + next + budget + aud +
      (boosted ? '<div class="ads-posts">' + boosted + '</div>' : '<p class="small muted">' + T('None yet. The robot starts with the best posts at the next run.', 'Nenhum ainda. O robô começa pelos melhores posts na próxima rodada.') + '</p>') +
      '<h2 class="sp-h2">' + T('Recent posts (best first: Reels, then sends, saves and watch time)', 'Posts recentes (melhores primeiro: Reels, depois envios, salvos e tempo assistido)') + '</h2>' +
      (line ? '<div class="ads-posts">' + line + '</div>' : '<p class="small muted">' + T('The posts show up after the first run.', 'Os posts aparecem depois da primeira rodada.') + '</p>');
  }

  function chart(d) {
    if (!d.last30.length) return '';
    return '<section class="card gap-top"><div class="card-head"><div><h2>' + T('Ad spend, last 30 days', 'Gasto com anúncios, últimos 30 dias') + '</h2></div></div>' +
      h.chart('ads-spend', { data: d.last30.map(function (x) { return { label: day(x.day), tick: String(Number(x.day.slice(8))), value: x.spend, tip: day(x.day) + ' · ' + T('sales from ads ', 'vendas dos anúncios ') + money(x.sales) }; }), height: 180, aria: 'Ad spend by day' }) + '</section>';
  }

  function logCard(d) {
    var run = d.lastRun;
    var errs = run && run.errors ? Object.keys(run.errors).map(function (k) { return '<li class="err">' + esc(cname(k === 'site' ? 'all' : k)) + ': ' + esc(run.errors[k]) + '</li>'; }).join('') : '';
    return '<section class="card gap-top"><div class="card-head"><div><h2>' + T('What the robot did', 'O que o robô fez') + '</h2><p class="sub">' +
      (run ? T('Last check: ', 'Última verificação: ') + esc(h.fmtDT(run.at)) : T('It hasn’t run yet. It runs every morning, or tap Run now.', 'Ainda não rodou. Ele roda toda manhã, ou toque em Rodar agora.')) + '</p></div></div>' +
      (errs ? '<ul class="ads-errs">' + errs + '</ul>' : '') +
      (d.log.length ? '<ul class="sp-buys ads-log">' + d.log.map(function (l) {
        return '<li><span><b>' + esc(T(l.en || l.pt, l.pt)) + '</b><small>' + esc(h.fmtDT(l.at)) + ' · ' + esc(cname(l.channel)) + '</small></span></li>';
      }).join('') + '</ul>' : '<p class="small muted">' + T('Nothing yet.', 'Nada ainda.') + '</p>') + '</section>';
  }

  function manualCard(d) {
    if (!d.manual.length) return '';
    return '<section class="card gap-top"><div class="card-head"><div><h2>' + T('Spend logged by hand', 'Gastos registrados à mão') + '</h2></div></div><ul class="sp-buys">' + d.manual.map(function (m) {
      return '<li><span><b>' + esc(cname(m.channel)) + (m.note ? ' · ' + esc(m.note) : '') + '</b><small>' + esc(day(m.date)) + '</small></span><span class="sp-cost">' + money(m.amount) +
        '<button class="icon-btn" data-act="adsDelManual" data-id="' + esc(m.id) + '" aria-label="' + T('Remove', 'Apagar') + '">' + h.icon('trash') + '</button></span></li>';
    }).join('') + '</ul></section>';
  }

  function rulesCard(d) {
    var r = d.config.rules;
    return '<details class="card gap-top ads-rules"><summary><b>' + T('The robot’s rules', 'As regras do robô') + '</b></summary><ul class="small">' +
      '<li>' + T('At most ' + r.maxPosts + ' posts at a time, in one budget: Meta puts more into the one that works. Reels first.', 'No máximo ' + r.maxPosts + ' posts ao mesmo tempo, num orçamento só: o Meta põe mais no que funciona. Reels primeiro.') + '</li>' +
      '<li>' + T('The ads look for people who wait for the site to open (not just clicks).', 'Os anúncios procuram quem espera o site abrir (não só quem clica).') + '</li>' +
      '<li>' + T('A post the robot chose that spends ' + dollars(r.stopAfter) + ' and nobody puts in the cart is swapped; also when the same people saw it 4+ times. If you chose it, the robot only warns.', 'O post escolhido pelo robô que gastar ' + dollars(r.stopAfter) + ' sem ninguém pôr no carrinho é trocado; também quando as mesmas pessoas já viram 4+ vezes. Se foram vocês que escolheram, o robô só avisa.') + '</li>' +
      '<li>' + T('Only posts from the last ' + r.postDays + ' days and at least a day old (except the next Reel you asked for).', 'Só posts dos últimos ' + r.postDays + ' dias e com pelo menos um dia (menos o próximo Reel que vocês pediram).') + '</li>' +
      (r.holiday !== false ? '<li>' + T('Christmas: Black Friday week the usual; Dec 2–14 double; from Dec 15 the ads rest until January.', 'Natal: semana da Black Friday o de sempre; 2 a 14/dez o dobro; a partir de 15/dez os anúncios descansam até janeiro.') + '</li>' : '') +
      '<li>' + T('The cap is never passed. When the ads pay off and the cap gets close, the robot asks you to approve a higher one.', 'O teto nunca é passado. Quando os anúncios dão retorno e o teto está perto, o robô pede para vocês aprovarem um maior.') + '</li>' +
      '<li>' + T('A sale counts for an ad when the customer came to the site from the ad’s link (Google Analytics).', 'Uma venda conta para o anúncio quando o cliente chegou ao site pelo link do anúncio (Google Analytics).') + '</li>' +
      '</ul><button class="btn btn-ghost btn-sm" data-act="adsRules"' + (st.busy ? ' disabled' : '') + '>' + T('Change the rules', 'Mudar as regras') + '</button></details>';
  }

  V.ads = function () {
    if (!st.data && !st.loading && !st.err) { st.loading = true; load('view'); }
    var d = st.data;
    var head = '<div class="page-head"><div><p class="eyebrow">Marketing</p><h1>' + T('Ads', 'Anúncios') + '</h1>' +
      '<p class="sub">' + T('Every morning the robot checks what each ad spent and brought, swaps what doesn’t work (Reels first) and never passes the cap you approved. You see everything here and can change it whenever you want.',
        'Toda manhã o robô confere quanto cada anúncio gastou e trouxe, troca o que não funciona (Reels primeiro) e nunca passa do teto que vocês aprovaram. Vocês veem tudo aqui e podem mudar quando quiserem.') + '</p></div>' +
      '<div class="actions"><button class="btn btn-ghost btn-sm" data-act="adsRun"' + (st.busy ? ' disabled' : '') + '>' + (st.busy ? T('Working…', 'Trabalhando…') : T('Run now', 'Rodar agora')) + '</button></div></div>';
    if (!d) return { title: T('Ads', 'Anúncios'), html: '<div translate="no">' + head + (st.err ? '<p class="err">' + esc(st.err) + '</p>' : '<div class="loading"><span>' + T('Loading…', 'Carregando…') + '</span></div>') + '</div>' };
    var chans = '<h2 class="sp-h2">' + T('Channels', 'Canais') + '</h2><div class="sp-grid">' + ['meta', 'etsy', 'google', 'tiktok', 'amazon'].map(function (k) { return chan(d, k); }).join('') + '</div>';
    return { title: T('Ads', 'Anúncios'), html: '<div translate="no" class="ads">' + head + proposals(d) + worth(d) + tiles(d) + capCard(d) + chans + posts(d) + salesCard(d) + chart(d) + logCard(d) + manualCard(d) + rulesCard(d) + '</div>' };
  };

  /* ---------- dialogs ---------- */
  function ask(title, inner, okText) {
    return new Promise(function (resolve) {
      var dlg = document.createElement('dialog'); dlg.className = 'modal'; dlg.setAttribute('translate', 'no');
      dlg.innerHTML = '<form method="dialog" class="in"><h2>' + esc(title) + '</h2>' + inner + '<div class="row end"><button class="btn btn-ghost" value="cancel">' + T('Cancel', 'Cancelar') + '</button><button class="btn btn-honey" value="ok">' + esc(okText || 'OK') + '</button></div></form>';
      document.body.appendChild(dlg);
      dlg.addEventListener('close', function () {
        var out = null;
        if (dlg.returnValue === 'ok') { out = {}; Array.prototype.forEach.call(dlg.querySelectorAll('[name]'), function (el) { if (el.type === 'radio') { if (el.checked) out[el.name] = el.value; } else out[el.name] = el.type === 'checkbox' ? el.checked : el.value; }); }
        dlg.remove(); resolve(out);
      });
      if (dlg.showModal) dlg.showModal(); else dlg.setAttribute('open', '');
    });
  }
  function field(name, label, value, type, extra) {
    return '<label class="field"><span>' + esc(label) + '</span><input class="input" name="' + name + '" value="' + esc(value == null ? '' : value) + '"' + (type ? ' type="' + type + '"' : '') +
      (type === 'number' ? ' inputmode="decimal" step="any" min="0"' : '') + (extra || '') + '></label>';
  }

  ACT.adsRun = function () { load('run', {}, T('Done. The numbers are up to date.', 'Pronto. Os números estão em dia.')); };
  ACT.adsCap = function () {
    var c = st.data.config;
    ask(T('Monthly cap', 'Teto do mês'), '<p class="small">' + T('The most the shop may spend on ads in a month, all channels together. Saving it is your approval: the robot works alone inside it and asks before going over.',
      'O máximo que a loja pode gastar com anúncios no mês, todos os canais juntos. Salvar é a aprovação de vocês: o robô trabalha sozinho dentro dele e pergunta antes de passar.') + '</p>' +
      field('cap', T('Cap ($ a month)', 'Teto ($ por mês)'), c.monthCap, 'number'), T('Approve', 'Aprovar')).then(function (v) {
      if (v && v.cap !== '') load('save', { config: { monthCap: Number(v.cap) } }, T('Cap saved.', 'Teto salvo.'));
    });
  };
  ACT.adsAuto = function (el) { load('save', { config: { auto: !!el.checked } }); };
  ACT.adsApprove = function (el) { load('approve', { id: el.getAttribute('data-id') }, T('Approved.', 'Aprovado.')); };
  ACT.adsDecline = function (el) { load('decline', { id: el.getAttribute('data-id') }); };
  ACT.adsChan = function (el) {
    var k = el.getAttribute('data-k'), c = st.data.config.channels[k], min = (st.data.minDaily || {})[k] || 1;
    ask(cname(k), '<label class="field ads-check"><input type="checkbox" name="on"' + (c.on ? ' checked' : '') + '> <span>' + T('On', 'Ligado') + '</span></label>' +
      field('daily', T('Budget a day ($, at least ' + money(min) + ')', 'Orçamento por dia ($, no mínimo ' + money(min) + ')'), c.daily, 'number') +
      (k === 'etsy' ? '<p class="tiny muted">' + T('Put the same amount in the Etsy app: the app can’t change it there.', 'Coloque o mesmo valor no app do Etsy: o app não consegue mudar lá.') + '</p>' : '') +
      (k === 'meta' ? '<p class="tiny muted">' + T('One budget for all the boosted posts: Meta puts more into the one that works.', 'Um orçamento só para todos os posts impulsionados: o Meta põe mais no que funciona.') + '</p>' : ''), T('Save', 'Salvar')).then(function (v) {
      if (!v) return;
      var ch = {}; ch[k] = { on: !!v.on, daily: Number(v.daily) || 0 };
      load('save', { config: { channels: ch } }, T('Saved.', 'Salvo.'));
    });
  };
  ACT.adsRules = function () {
    var r = st.data.config.rules;
    ask(T('The robot’s rules', 'As regras do robô'), field('maxPosts', T('Posts at the same time', 'Posts ao mesmo tempo'), r.maxPosts, 'number') +
      field('stopAfter', T('Swap a post after spending ($) with nobody putting it in the cart', 'Trocar o post depois de gastar ($) sem ninguém pôr no carrinho'), r.stopAfter, 'number') +
      field('postDays', T('Only posts from the last (days)', 'Só posts dos últimos (dias)'), r.postDays, 'number') +
      '<label class="field ads-check"><input type="checkbox" name="holiday"' + (r.holiday !== false ? ' checked' : '') + '> <span>' + T('Christmas calendar (double Dec 2–14, rest from Dec 15)', 'Calendário do Natal (dobro de 2 a 14/dez, descanso a partir de 15/dez)') + '</span></label>', T('Save', 'Salvar')).then(function (v) {
      if (!v) return;
      var rules = {}; Object.keys(v).forEach(function (k) { if (k === 'holiday') rules[k] = !!v[k]; else if (v[k] !== '') rules[k] = Number(v[k]); });
      load('save', { config: { rules: rules } }, T('Saved.', 'Salvo.'));
    });
  };
  ACT.adsManual = function (el) {
    var k = el.getAttribute('data-k');
    ask(T('Log spend: ', 'Registrar gasto: ') + cname(k), field('amount', T('How much ($)', 'Quanto ($)'), '', 'number') + field('date', T('Day', 'Dia'), h.today(), 'date') +
      field('note', T('Note (optional)', 'Observação (opcional)'), ''), T('Save', 'Salvar')).then(function (v) {
      if (v && v.amount) load('manual', { channel: k, amount: Number(v.amount), date: v.date, note: v.note }, T('Saved. It counts in the cap and in Reports.', 'Salvo. Conta no teto e nos Relatórios.'));
    });
  };
  ACT.adsDelManual = function (el) {
    var id = el.getAttribute('data-id');
    h.dialog({ title: T('Remove this spend?', 'Apagar este gasto?'), html: '', ok: T('Remove', 'Apagar'), cancel: T('Cancel', 'Cancelar'), danger: true }).then(function (ok) { if (ok) load('removeManual', { id: id }); });
  };
  ACT.adsPost = function (el) {
    var what = el.getAttribute('data-what'), id = el.getAttribute('data-id'), d = st.data;
    var msg = { boost: T('Boosting.', 'Impulsionando.'), pause: T('Paused.', 'Pausado.'), never: T('This post won’t be boosted.', 'Este post não vai ser impulsionado.'), allow: T('The robot can choose it again.', 'O robô pode escolher de novo.') }[what];
    var active = (d.boosts || []).filter(function (b) { return b.status === 'active' && b.id !== id; });
    if (what !== 'boost' || active.length < d.config.rules.maxPosts) return load('post', { id: id, what: what }, msg);
    // no room: which one comes out?
    ask(T('Swap which one?', 'Trocar qual?'), '<p class="small">' + T('There are already ' + active.length + ' posts boosted. Pick the one that stops:', 'Já tem ' + active.length + ' posts impulsionados. Escolha o que para:') + '</p>' +
      active.map(function (b, i) {
        return '<label class="field ads-check"><input type="radio" name="out" value="' + esc(b.id) + '"' + (i === 0 ? ' checked' : '') + '> <span>' + esc(b.caption || ('#' + String(b.id).slice(-5))) +
          ' · ' + T('spent ', 'gastou ') + money(b.spend) + (b.revenue > 0 ? ' · ' + T('sold ', 'vendeu ') + money(b.revenue) : '') + '</span></label>';
      }).join(''), T('Swap', 'Trocar')).then(function (v) {
      if (!v) return;
      load('post', { id: id, what: 'boost', instead: v.out }, T('Swapped.', 'Trocado.'));
    });
  };
  ACT.adsNextReel = function (el) {
    var on = el.getAttribute('data-on') === '1';
    load('nextReel', { on: on }, on ? T('Done: the next Reel is boosted as soon as it’s out.', 'Pronto: o próximo Reel é impulsionado assim que sair.') : T('Cancelled.', 'Cancelado.'));
  };
  ACT.adsConnect = function () {
    var steps = T(
      '<ol class="small ads-steps"><li>Easier on a computer. Open <b>business.facebook.com/settings</b> (Little Hive House business).</li>' +
      '<li><b>Accounts › Ad accounts</b>: if there isn’t one, create “Little Hive House”, in US dollars and New York time, and add a card under <b>Payment methods</b>.</li>' +
      '<li>Open <b>developers.facebook.com/apps</b> › <b>Create app</b> › type <b>Business</b> › name “Hive Admin” › pick the Little Hive House business. In the app, add the <b>Marketing API</b> product.</li>' +
      '<li>Back in business settings: <b>Users › System users › Add</b> › name “Hive Admin”, role <b>Admin</b>.</li>' +
      '<li>On that system user, <b>Assign assets</b>: the ad account (full control), the Facebook Page (full control), the Instagram account (full control) and the Hive Admin app.</li>' +
      '<li><b>Generate new token</b> › app “Hive Admin” › expiry <b>Never</b> › tick: ads_management, ads_read, business_management, pages_show_list, pages_read_engagement, instagram_basic › <b>Generate</b>.</li>' +
      '<li>Copy the token and paste it here. It is kept on the shop’s server and never shown again; don’t send it in chats or emails.</li></ol>',
      '<ol class="small ads-steps"><li>É mais fácil no computador. Abra <b>business.facebook.com/settings</b> (empresa Little Hive House).</li>' +
      '<li><b>Contas › Contas de anúncios</b>: se não tiver, crie “Little Hive House”, em dólar americano e horário de Nova York, e coloque um cartão em <b>Formas de pagamento</b>.</li>' +
      '<li>Abra <b>developers.facebook.com/apps</b> › <b>Criar app</b> › tipo <b>Empresa</b> (Business) › nome “Hive Admin” › escolha a empresa Little Hive House. No app, adicione o produto <b>API de Marketing</b>.</li>' +
      '<li>Volte nas configurações da empresa: <b>Usuários › Usuários do sistema › Adicionar</b> › nome “Hive Admin”, função <b>Administrador</b>.</li>' +
      '<li>Nesse usuário do sistema, <b>Atribuir ativos</b>: a conta de anúncios (controle total), a página do Facebook (controle total), a conta do Instagram (controle total) e o app Hive Admin.</li>' +
      '<li><b>Gerar novo token</b> › app “Hive Admin” › validade <b>Nunca</b> › marque: ads_management, ads_read, business_management, pages_show_list, pages_read_engagement, instagram_basic › <b>Gerar</b>.</li>' +
      '<li>Copie o token e cole aqui. Ele fica guardado no servidor da loja e não aparece de novo; não mande em chat nem e-mail.</li></ol>');
    ask(T('Connect Instagram & Facebook', 'Conectar Instagram e Facebook'), steps +
      '<label class="field"><span>' + T('Token', 'Token') + '</span><textarea class="input" name="token" rows="3" autocomplete="off" autocapitalize="off" spellcheck="false"></textarea></label>' +
      '<details class="small"><summary>' + T('Optional', 'Opcional') + '</summary>' +
      field('adAccountId', T('Ad account ID (only if you have more than one)', 'ID da conta de anúncios (só se tiver mais de uma)'), '') +
      field('appSecret', T('App secret (only if Meta asks for “appsecret_proof”)', 'Chave secreta do app (só se o Meta pedir “appsecret_proof”)'), '', 'password', ' autocomplete="off"') + '</details>',
      T('Connect', 'Conectar')).then(function (v) {
      if (v && v.token) load('connectMeta', { token: v.token, adAccountId: v.adAccountId, appSecret: v.appSecret }, T('Connected.', 'Conectado.'));
    });
  };
})();
