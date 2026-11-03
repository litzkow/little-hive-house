/* Little Hive House admin: Visits. Who comes to the shop, from where, what they look at and how many buy, from Google
   Analytics (functions/analytics.js: adminAnalytics for the period, adminAnalyticsLive every 30 s while the page is open).
   The screen picks its own language (T(en, pt)) and is marked translate="no", like the Growth plan. */
(function () {
  'use strict';
  var A = window.LHHAdmin, S = A.S, h = A.h, V = A.VIEWS, ACT = A.ACT;
  var esc = h.esc, icon = h.icon;
  function T(en, pt) { return h.LANG() === 'pt' ? pt : en; }
  function loc() { return h.LANG() === 'pt' ? 'pt-BR' : 'en-US'; }
  function n0(v) { return Math.round(Number(v) || 0).toLocaleString(loc()); }
  function pc(v, digits) { return ((Number(v) || 0) * 100).toFixed(digits == null ? 0 : digits).replace('.', h.LANG() === 'pt' ? ',' : '.') + '%'; }
  function dur(sec) {
    sec = Math.round(Number(sec) || 0);
    if (sec < 60) return sec + ' s';
    var m = Math.floor(sec / 60), s = sec % 60;
    return m + ' min' + (s ? ' ' + s + ' s' : '');
  }
  var RANGES = [['7d', '7 days', '7 dias'], ['28d', '28 days', '28 dias'], ['90d', '90 days', '90 dias'], ['12m', '12 months', '12 meses']];

  var st = { range: '28d', group: 'day', data: {}, err: {}, loading: {}, live: null, liveErr: null, timer: null };

  function load(range, refresh) {
    if (st.loading[range]) return;
    st.loading[range] = true; st.err[range] = null;
    h.call('adminAnalytics', { range: range, refresh: !!refresh }).then(function (d) { st.data[range] = d; })
      .catch(function (e) { st.err[range] = h.friendlyError(e); })
      .then(function () { st.loading[range] = false; if (A.parseHash().view === 'visits') { var y = scrollY; h.route(); scrollTo(0, y); } });
  }
  function loadLive() {
    h.call('adminAnalyticsLive', {}).then(function (d) { st.live = d; st.liveErr = null; })
      .catch(function (e) { st.liveErr = h.friendlyError(e); })
      .then(drawLive);
  }
  function startLive() {
    stopLive();
    loadLive();
    st.timer = setInterval(function () {
      if (A.parseHash().view !== 'visits') { stopLive(); return; }
      if (!document.hidden) loadLive();
    }, 30000);
  }
  function stopLive() { if (st.timer) clearInterval(st.timer); st.timer = null; }

  /* ---------- names ---------- */
  var CHANNELS = { 'Direct': ['Typed the address or a saved link', 'Digitou o endereço ou link salvo'], 'Organic Search': ['Google and other search', 'Google e outras buscas'],
    'Organic Social': ['Instagram, Facebook and other social', 'Instagram, Facebook e outras redes'], 'Paid Social': ['Social ads', 'Anúncios nas redes'],
    'Paid Search': ['Search ads', 'Anúncios no Google'], 'Referral': ['Links on other sites', 'Links em outros sites'], 'Email': ['Emails', 'E-mails'],
    'Organic Shopping': ['Google Shopping (free)', 'Google Shopping (grátis)'], 'Paid Shopping': ['Shopping ads', 'Anúncios de Shopping'],
    'Unassigned': ['Unknown', 'Não identificado'], 'Organic Video': ['Videos (YouTube, TikTok)', 'Vídeos (YouTube, TikTok)'], 'Display': ['Display ads', 'Anúncios em sites'] };
  function channelName(n) { var c = CHANNELS[n]; return c ? T(c[0], c[1]) : n; }
  function sourceName(n) {
    var s = String(n || '').toLowerCase();
    if (s === '(direct)') return T('Direct', 'Direto');
    if (/instagram/.test(s)) return 'Instagram';
    if (/facebook|fb\.com/.test(s)) return 'Facebook';
    if (/tiktok/.test(s)) return 'TikTok';
    if (/pinterest/.test(s)) return 'Pinterest';
    if (/google/.test(s)) return 'Google';
    if (/bing/.test(s)) return 'Bing';
    return n;
  }
  function merge(list, nameFn) {
    var by = {}, out = [];
    list.forEach(function (x) { var k = nameFn(x.name); if (!by[k]) { by[k] = { name: k, value: 0 }; out.push(by[k]); } by[k].value += x.value; });
    return out.sort(function (a, b) { return b.value - a.value; });
  }
  var dn = null;
  function countryName(c) {
    try { if (c.id && window.Intl && Intl.DisplayNames) { dn = dn && dn.lang === loc() ? dn : { lang: loc(), f: new Intl.DisplayNames([loc()], { type: 'region' }) }; return dn.f.of(c.id); } } catch (e) {}
    return c.name;
  }
  function flag(id) {
    if (!/^[A-Z]{2}$/.test(id || '')) return '';
    return String.fromCodePoint(0x1F1E6 + id.charCodeAt(0) - 65, 0x1F1E6 + id.charCodeAt(1) - 65) + ' ';
  }
  var GENDER = { male: ['Men', 'Homens'], female: ['Women', 'Mulheres'] };
  var DEVICE = { mobile: ['Phone', 'Celular'], desktop: ['Computer', 'Computador'], tablet: ['Tablet', 'Tablet'], smart_tv: ['TV', 'TV'] };
  var NVR = { 'new': ['First visit', 'Primeira visita'], returning: ['Came back', 'Voltaram'] };
  function from(map, n) { var x = map[String(n).toLowerCase()]; return x ? T(x[0], x[1]) : n; }
  var PAGE_PT = { 'Home': 'Início', 'Shop': 'Loja', 'Photo magnets': 'Ímãs de foto', 'Big orders': 'Pedidos grandes', 'Checkout': 'Pagamento', 'Thank you': 'Obrigado (compra feita)',
    'Favorites': 'Favoritos', 'Account': 'Conta', 'My orders': 'Meus pedidos', 'Track order': 'Rastrear pedido', 'Contact': 'Contato', 'Shipping': 'Frete',
    'Returns': 'Devoluções', 'Privacy': 'Privacidade', 'Terms': 'Termos', 'Suggestions': 'Sugestões' };
  function pageName(p) {
    var m = /^\/collections\/([a-z0-9-]+)$/.exec(p.path || '');
    if (m) return T('Collection: ', 'Coleção: ') + h.colName(m[1]);
    if (p.name) return h.LANG() === 'pt' ? (PAGE_PT[p.name] || p.name) : p.name;
    return p.path;
  }

  /* ---------- pieces ---------- */
  function card(title, sub, body, cls) {
    return '<section class="card' + (cls ? ' ' + cls : '') + '"><div class="card-head"><div><h2>' + esc(title) + '</h2>' + (sub ? '<p class="sub">' + sub + '</p>' : '') + '</div></div>' + body + '</section>';
  }
  function bars(list, opts) {
    opts = opts || {};
    if (!list || !list.length) return '<div class="empty small">' + esc(opts.empty || T('Nothing yet in this period.', 'Nada ainda neste período.')) + '</div>';
    var total = list.reduce(function (t, x) { return t + x.value; }, 0) || 1;
    return h.hbars(list.slice(0, opts.n || 8).map(function (x) {
      return { label: (opts.label ? opts.label(x) : x.name), sub: opts.sub ? opts.sub(x) : '', value: x.value,
        valueText: n0(x.value) + (opts.share === false ? '' : ' · ' + pc(x.value / total)) };
    }));
  }
  function delta(cur, prev, goodUp, fmt) {
    if (!prev) return cur ? T('New in this period', 'Novo neste período') : T('Nothing in the period before', 'Nada no período anterior');
    var d = (cur - prev) / prev;
    if (Math.abs(d) < 0.005) return T('Same as before', 'Igual ao período anterior');
    var up = d > 0, good = goodUp ? up : !up;
    return '<span class="' + (good ? 'pos' : 'neg') + '">' + (up ? '▲ ' : '▼ ') + pc(Math.abs(d)) + '</span> ' + T('vs the ' + (fmt || 'period') + ' before', 'vs o período anterior');
  }
  function grouped(series, group) {
    if (group === 'day') return series.map(function (x) {
      var d = new Date(x.date + 'T12:00:00');
      return { key: x.date, label: d.toLocaleDateString(loc(), { weekday: 'short', day: 'numeric', month: 'short' }), tick: String(d.getDate()), visits: x.visits, users: x.users, views: x.views };
    });
    var by = {}, out = [];
    series.forEach(function (x) {
      var d = new Date(x.date + 'T12:00:00'), key, label, tick;
      if (group === 'week') {
        var mon = new Date(d); mon.setDate(d.getDate() - ((d.getDay() + 6) % 7));
        key = mon.toISOString().slice(0, 10);
        label = T('Week of ', 'Semana de ') + mon.toLocaleDateString(loc(), { day: 'numeric', month: 'short' });
        tick = mon.getDate() + '/' + (mon.getMonth() + 1);
      } else {
        key = x.date.slice(0, 7);
        label = d.toLocaleDateString(loc(), { month: 'long', year: 'numeric' });
        tick = d.toLocaleDateString(loc(), { month: 'short' }).replace('.', '');
      }
      if (!by[key]) { by[key] = { key: key, label: label, tick: tick, visits: 0, users: 0, views: 0 }; out.push(by[key]); }
      by[key].visits += x.visits; by[key].users += x.users; by[key].views += x.views;
    });
    return out;
  }
  function funnel(f) {
    var top = (f[0] && f[0].users) || 0;
    var labels = { page_view: T('Visited the shop', 'Visitaram a loja'), view_item: T('Opened a magnet', 'Abriram um ímã'), add_to_cart: T('Added to cart', 'Puseram no carrinho'),
      begin_checkout: T('Went to checkout', 'Foram para o pagamento'), purchase: T('Bought', 'Compraram') };
    return '<ol class="vfunnel">' + f.map(function (s, i) {
      var share = top ? s.users / top : 0, prev = i ? f[i - 1].users : 0;
      var drop = i && prev ? T(pc(s.users / prev) + ' of the step before', pc(s.users / prev) + ' do passo anterior') : '';
      return '<li><div class="vf-top"><span>' + esc(labels[s.key] || s.label) + '</span><b>' + n0(s.users) + '</b></div>' +
        '<div class="vf-track"><i style="width:' + Math.max(s.users ? 2 : 0, share * 100).toFixed(1) + '%"></i></div>' +
        '<small>' + (i ? pc(share, share < 0.1 ? 1 : 0) + T(' of visitors', ' dos visitantes') + (drop ? ' · ' + drop : '') : T('People', 'Pessoas')) + '</small></li>';
    }).join('') + '</ol>';
  }
  function heatmap(heat) {
    var max = 0; heat.forEach(function (r) { r.forEach(function (v) { if (v > max) max = v; }); });
    if (!max) return '<div class="empty small">' + esc(T('Not enough visits yet.', 'Ainda não tem visitas suficientes.')) + '</div>';
    var days = h.LANG() === 'pt' ? ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'] : ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    var best = { v: 0 }; heat.forEach(function (r, d) { r.forEach(function (v, hr) { if (v > best.v) best = { v: v, d: d, hr: hr }; }); });
    var dayLong = h.LANG() === 'pt' ? ['domingo', 'segunda', 'terça', 'quarta', 'quinta', 'sexta', 'sábado'] : ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    var hourTxt = function (hr) { return h.LANG() === 'pt' ? hr + 'h' : (hr % 12 || 12) + (hr < 12 ? ' am' : ' pm'); };
    var rows = heat.map(function (r, d) {
      return '<div class="hm-row"><span class="hm-d">' + days[d] + '</span>' + r.map(function (v, hr) {
        var a = v ? 0.15 + 0.85 * v / max : 0;
        return '<i title="' + esc(days[d] + ' ' + hourTxt(hr) + ': ' + n0(v)) + '" style="' + (a ? 'background:color-mix(in srgb, var(--honey) ' + Math.round(a * 100) + '%, var(--sunk))' : '') + '"></i>';
      }).join('') + '</div>';
    }).join('');
    var axis = '<div class="hm-row hm-axis"><span class="hm-d"></span>' + [0, 6, 12, 18].map(function (hr) { return '<em style="grid-column:' + (hr + 2) + '">' + hourTxt(hr) + '</em>'; }).join('') + '</div>';
    return '<p class="small" style="margin:0 0 10px">' + esc(T('Busiest: ' + dayLong[best.d] + ' around ' + hourTxt(best.hr) + '. A good time to post on Instagram is a little before.',
      'Mais movimento: ' + dayLong[best.d] + ' por volta das ' + hourTxt(best.hr) + '. Um bom horário para postar no Instagram é um pouco antes.')) + '</p>' +
      '<div class="heatmap" role="img" aria-label="' + esc(T('Visits by day and hour', 'Visitas por dia e hora')) + '">' + rows + axis + '</div>' +
      '<p class="tiny faint" style="margin-top:6px">' + esc(T('Eastern time.', 'Horário de Nova York (Leste).')) + '</p>';
  }

  /* ---------- live ---------- */
  function liveHTML() {
    var l = st.live;
    if (!l) return '<div class="live-box">' + (st.liveErr ? '<p class="err small">' + esc(st.liveErr) + '</p>' : '<p class="small muted">' + esc(T('Looking…', 'Olhando…')) + '</p>') + '</div>';
    var max = Math.max.apply(null, l.perMinute.concat([1]));
    return '<div class="live-box">' +
      '<div class="live-now"><span class="dot' + (l.now ? ' on' : '') + '"></span><b>' + n0(l.now) + '</b><span>' + esc(l.now === 1 ? T('person on the shop now', 'pessoa na loja agora') : T('people on the shop now', 'pessoas na loja agora')) + '</span></div>' +
      '<div class="live-mins" role="img" aria-label="' + esc(T('Visitors per minute, last 30 minutes', 'Visitantes por minuto, últimos 30 minutos')) + '">' + l.perMinute.map(function (v, i) {
        return '<i style="height:' + (v ? Math.max(8, v / max * 100) : 3) + '%" title="' + esc((29 - i ? T((29 - i) + ' min ago', 'há ' + (29 - i) + ' min') : T('now', 'agora')) + ': ' + v) + '"></i>';
      }).join('') + '</div><p class="tiny faint" style="margin:4px 0 0">' + esc(T('Last 30 minutes · updates every 30 seconds', 'Últimos 30 minutos · atualiza a cada 30 segundos')) + '</p>' +
      (l.places.length || l.pages.length ? '<div class="two live-lists">' +
        '<div><h3>' + esc(T('From', 'De onde')) + '</h3><ul>' + l.places.map(function (p) { return '<li><span>' + esc(flag(p.id) + (p.city ? p.city + ', ' : '') + countryName({ id: p.id, name: p.country })) + '</span><b>' + n0(p.value) + '</b></li>'; }).join('') + '</ul></div>' +
        '<div><h3>' + esc(T('Looking at', 'Vendo')) + '</h3><ul>' + l.pages.map(function (p) { return '<li><span>' + esc(String(p.name).replace(/\s*[·|–-]\s*Little Hive House\s*$/i, '') || 'Little Hive House') + '</span><b>' + n0(p.value) + '</b></li>'; }).join('') + '</ul></div></div>' : '') +
      '</div>';
  }
  function drawLive() { var el = document.getElementById('v-live'); if (el) el.innerHTML = liveHTML(); }

  /* ---------- the page ---------- */
  V.visits = function (r) {
    if (r.q.get('range') && RANGES.some(function (x) { return x[0] === r.q.get('range'); })) st.range = r.q.get('range');
    var d = st.data[st.range];
    if (!d && !st.err[st.range]) load(st.range);
    var rangeSeg = '<div class="seg" role="group" aria-label="' + esc(T('Period', 'Período')) + '">' + RANGES.map(function (x) {
      return '<button type="button" data-act="vrange" data-range="' + x[0] + '" aria-pressed="' + (st.range === x[0]) + '">' + esc(T(x[1], x[2])) + '</button>';
    }).join('') + '</div>';
    var headHtml = '<div class="page-head"><div><p class="eyebrow">' + esc(T('Google Analytics', 'Google Analytics')) + '</p><h1>' + esc(T('Visits', 'Visitas')) + '</h1>' +
      '<p class="sub">' + esc(T('Who comes to the shop, from where, and what they look at', 'Quem vem à loja, de onde, e o que olham')) + '</p></div>' +
      '<div class="actions">' + rangeSeg + '<button class="btn btn-ghost btn-sm" data-act="vrefresh"' + (st.loading[st.range] ? ' disabled' : '') + '>' + icon('refresh') + esc(T('Update', 'Atualizar')) + '</button></div></div>';
    var live = '<section class="card live-card" id="v-live-card"><div class="card-head"><div><h2>' + esc(T('Right now', 'Agora')) + '</h2></div></div><div id="v-live">' + liveHTML() + '</div></section>';

    var body;
    if (!d) {
      body = st.err[st.range] ? '<div class="callout">' + icon('info') + '<p class="small"><b>' + esc(T('Couldn’t read Google Analytics', 'Não deu para ler o Google Analytics')) + '</b><br>' + esc(st.err[st.range]) + '</p></div>'
        : '<div class="loading"><svg class="spin" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3a9 9 0 1 0 9 9" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/></svg><span>' + esc(T('Asking Google Analytics…', 'Perguntando ao Google Analytics…')) + '</span></div>';
    } else body = report(d);
    return {
      title: T('Visits', 'Visitas'), keepScroll: false,
      html: '<div class="visits" translate="no">' + headHtml + live + body + '</div>',
      after: function () { if (!st.timer) startLive(); else drawLive(); }
    };
  };

  function report(d) {
    var t = d.totals, p = d.previous, days = d.days;
    var periodTxt = T('Last ' + RANGES.filter(function (x) { return x[0] === d.range; })[0][1], 'Últimos ' + RANGES.filter(function (x) { return x[0] === d.range; })[0][2]);
    var conv = t.activeUsers ? t.ecommercePurchases / t.activeUsers : 0, convPrev = p.activeUsers ? p.ecommercePurchases / p.activeUsers : 0;
    var perVisitor = t.activeUsers ? t.purchaseRevenue / t.activeUsers : 0;
    var empty = !t.activeUsers && !t.sessions;
    var note = empty ? '<div class="callout calm">' + icon('info') + '<p class="small">' + esc(T('The Google Analytics tag went on the shop on November 3, 2026. Visits show up here a few hours after they happen; the “Right now” box above is instant.',
      'A medição do Google Analytics entrou na loja em 3 de novembro de 2026. As visitas aparecem aqui algumas horas depois; o quadro “Agora” acima é na hora.')) + '</p></div>' : '';

    var tiles = '<div class="tiles lead">' +
      h.tile(T('Visitors', 'Visitantes'), n0(t.activeUsers), delta(t.activeUsers, p.activeUsers, true), true) +
      h.tile(T('Visits', 'Visitas'), n0(t.sessions), delta(t.sessions, p.sessions, true)) +
      h.tile(T('Pages seen', 'Páginas vistas'), n0(t.screenPageViews), t.sessions ? T((t.screenPageViews / t.sessions).toFixed(1) + ' per visit', (t.screenPageViews / t.sessions).toFixed(1).replace('.', ',') + ' por visita') : '') +
      h.tile(T('Time per visit', 'Tempo por visita'), dur(t.averageSessionDuration), delta(t.averageSessionDuration, p.averageSessionDuration, true)) +
      h.tile(T('Really looked', 'Olharam de verdade'), pc(t.engagementRate), T('Stayed 10 s+, saw 2+ pages or bought', 'Ficaram 10 s+, viram 2+ páginas ou compraram')) +
      h.tile(T('New visitors', 'Visitantes novos'), n0(t.newUsers), t.activeUsers ? pc(t.newUsers / t.activeUsers) + T(' of visitors', ' dos visitantes') : '') +
      h.tile(T('Bought', 'Compraram'), pc(conv, 1), T(n0(t.ecommercePurchases) + ' orders · ', n0(t.ecommercePurchases) + ' pedidos · ') + delta(conv, convPrev, true)) +
      h.tile(T('Sales per visitor', 'Venda por visitante'), h.money(perVisitor), h.money(t.purchaseRevenue) + T(' in sales', ' em vendas')) +
      '</div>';

    var g = grouped(d.series || [], st.group);
    var groupSeg = '<div class="seg" role="group" aria-label="' + esc(T('Group by', 'Agrupar por')) + '">' + [['day', 'Day', 'Dia'], ['week', 'Week', 'Semana'], ['month', 'Month', 'Mês']].map(function (x) {
      return '<button type="button" data-act="vgroup" data-group="' + x[0] + '" aria-pressed="' + (st.group === x[0]) + '">' + esc(T(x[1], x[2])) + '</button>';
    }).join('') + '</div>';
    var over = '<section class="card gap-top"><div class="card-head"><div><h2>' + esc(T('Visits over time', 'Visitas no tempo')) + '</h2><p class="sub">' + esc(periodTxt) + '</p></div>' + groupSeg + '</div>' +
      (g.length ? h.chart('v-time', { data: g.map(function (x) {
        return { label: x.label, tick: x.tick, value: x.visits, tip: x.label + ' · ' + n0(x.users) + T(' visitors · ', ' visitantes · ') + n0(x.views) + T(' pages', ' páginas') };
      }), height: 220, format: n0, tipFormat: function (v) { return n0(v) + T(' visits', ' visitas'); }, aria: T('Visits over time', 'Visitas no tempo'), labelLast: g.length <= 14 }) : '<div class="empty small">' + esc(T('No visits yet.', 'Nenhuma visita ainda.')) + '</div>') + '</section>';

    var where = '<div class="three gap-top">' +
      card(T('Countries', 'Países'), esc(T('Visitors', 'Visitantes')), bars(d.countries, { label: function (c) { return flag(c.id) + countryName(c); } })) +
      card(T('US states', 'Estados dos EUA'), esc(T('Visitors from the US', 'Visitantes dos EUA')), bars(d.states)) +
      card(T('Cities', 'Cidades'), esc(T('Visitors', 'Visitantes')), bars(d.cities, { label: function (c) { return c.name + (c.region ? ', ' + c.region : ''); }, sub: function (c) { return c.country !== 'US' ? c.country : ''; } })) +
      '</div>';

    var noDemo = !(d.age || []).length && !(d.gender || []).length;
    var who = '<div class="three gap-top">' +
      card(T('Age', 'Idade'), esc(T('Visitors Google could estimate', 'Visitantes que o Google conseguiu estimar')), bars(d.age, { empty: T('Shows up once Google has enough visitors.', 'Aparece quando o Google tiver visitantes suficientes.') })) +
      card(T('Gender', 'Gênero'), esc(T('Visitors Google could estimate', 'Visitantes que o Google conseguiu estimar')), bars(d.gender, { label: function (x) { return from(GENDER, x.name); }, empty: T('Shows up once Google has enough visitors.', 'Aparece quando o Google tiver visitantes suficientes.') })) +
      card(T('New or coming back', 'Novos ou voltando'), '', bars(d.newVsReturning, { label: function (x) { return from(NVR, x.name); } })) +
      '</div>' + (noDemo ? '<p class="tiny faint" style="margin-top:6px">' + esc(T('Age and gender come from Google signals and only appear when there are enough visitors, so nobody can be singled out.',
        'Idade e gênero vêm dos sinais do Google e só aparecem quando há visitantes suficientes, para ninguém ser identificado.')) + '</p>' : '');

    var how = '<div class="three gap-top">' +
      card(T('How they found the shop', 'Como acharam a loja'), esc(T('Visits', 'Visitas')), bars(merge(d.channels || [], channelName))) +
      card(T('Sites and apps', 'Sites e apps'), esc(T('Where the visit came from', 'De onde a visita veio')), bars(merge(d.sources || [], sourceName))) +
      card(T('Devices', 'Aparelhos'), esc(T('Visitors', 'Visitantes')), bars(d.devices, { label: function (x) { return from(DEVICE, x.name); } }) +
        '<h3 class="mini-h">' + esc(T('System', 'Sistema')) + '</h3>' + bars(d.os, { n: 5 })) +
      '</div>';

    var cols = d.collections || [];
    var look = '<div class="two gap-top">' +
      card(T('Most visited collections', 'Coleções mais visitadas'), esc(T('Page views · average time', 'Visualizações · tempo médio')),
        cols.length ? h.hbars(cols.slice(0, 12).map(function (c) {
          return { label: h.colName(c.slug), sub: n0(c.users) + T(' visitors · ', ' visitantes · ') + dur(c.avgSeconds), value: c.views, valueText: n0(c.views) };
        })) : '<div class="empty small">' + esc(T('No collection visits yet.', 'Nenhuma visita a coleções ainda.')) + '</div>') +
      card(T('Magnets people look at', 'Ímãs que mais olham'), esc(T('Opened · added to cart · bought', 'Abertos · no carrinho · comprados')),
        (d.items || []).length ? h.hbars(d.items.slice(0, 12).map(function (x) {
          return { label: x.name, sub: (x.category ? h.colName(x.category) + ' · ' : '') + n0(x.added) + T(' in cart · ', ' no carrinho · ') + n0(x.bought) + T(' bought', ' comprados'), value: x.viewed, valueText: n0(x.viewed) };
        })) : '<div class="empty small">' + esc(T('Shows up when people open magnets on the shop.', 'Aparece quando abrirem ímãs na loja.')) + '</div>') +
      '</div>';

    var pages = card(T('Pages', 'Páginas'), esc(T('Most seen · visitors · time on the page', 'Mais vistas · visitantes · tempo na página')),
      (d.pages || []).length ? h.hbars(d.pages.slice(0, 15).map(function (x) {
        return { label: pageName(x), sub: n0(x.users) + T(' visitors · ', ' visitantes · ') + dur(x.avgSeconds), value: x.views, valueText: n0(x.views) };
      })) : '<div class="empty small">' + esc(T('No pages yet.', 'Nenhuma página ainda.')) + '</div>');
    var landing = card(T('Where they arrive', 'Por onde entram'), esc(T('First page of the visit', 'Primeira página da visita')), bars(d.landing, { label: pageName }));

    var ev = d.events || {}, evc = function (k) { return (ev[k] && ev[k].count) || 0; };
    var extra = '<div class="tiles gap-top">' +
      h.tile(T('Added to cart', 'Puseram no carrinho'), n0(evc('add_to_cart')), T('times', 'vezes')) +
      h.tile(T('Hearts (favorites)', 'Corações (favoritos)'), n0(evc('add_to_wishlist')), T('magnets saved', 'ímãs salvos')) +
      h.tile(T('Photos in the builder', 'Fotos no criador'), n0(evc('photo_added')), T('times someone added photos', 'vezes que puseram fotos')) +
      h.tile(T('Went to checkout', 'Foram para o pagamento'), n0(evc('begin_checkout')), t.ecommercePurchases && evc('begin_checkout') ? pc(t.ecommercePurchases / evc('begin_checkout')) + T(' of them paid', ' deles pagaram') : '') +
      '</div>';

    var funnelCard = card(T('From visit to sale', 'Da visita à venda'), esc(T('People at each step', 'Pessoas em cada passo')), funnel(d.funnel || []));
    var heatCard = card(T('Best days and hours', 'Melhores dias e horários'), esc(T('Visits', 'Visitas')), heatmap(d.heat || []));

    var updated = new Date(d.at);
    return note + tiles + over + '<div class="two gap-top">' + funnelCard + heatCard + '</div>' + extra + where + who + how + look +
      '<div class="two gap-top">' + pages + landing + '</div>' +
      '<p class="tiny faint gap-top">' + esc(T('From Google Analytics · updated ', 'Do Google Analytics · atualizado ') + updated.toLocaleString(loc(), { day: 'numeric', month: 'short', hour: 'numeric', minute: '2-digit' }) +
        T('. Visitors are people (each phone or computer counts once); a visit is one time on the site. Some people block measuring, so the real numbers are a little higher.',
          '. Visitantes são pessoas (cada celular ou computador conta uma vez); uma visita é cada vez que entram no site. Algumas pessoas bloqueiam a medição, então os números reais são um pouco maiores.')) + '</p>';
  }

  ACT.vrange = function (el) { st.range = el.getAttribute('data-range'); history.replaceState(null, '', '#visits'); var y = scrollY; h.route(); scrollTo(0, y); };
  ACT.vgroup = function (el) { st.group = el.getAttribute('data-group'); var y = scrollY; h.route(); scrollTo(0, y); };
  ACT.vrefresh = function () { load(st.range, true); loadLive(); var y = scrollY; h.route(); scrollTo(0, y); };
})();
