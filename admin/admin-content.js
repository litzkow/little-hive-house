/* Little Hive House admin: Conteúdo (functions/content.js adminContent). The posts the owners make together: videos and
   photos passed to each other in full quality (uploaded and saved as the original files, never resized), the planned
   posts from the 6-month calendar, captions to copy, scripts, and which networks already got each post.
   The screen picks its own language (T(en, pt)) and is marked translate="no". */
(function () {
  'use strict';
  var A = window.LHHAdmin, S = A.S, h = A.h, V = A.VIEWS, ACT = A.ACT;
  var esc = h.esc;
  function T(en, pt) { return h.LANG() === 'pt' ? pt : en; }
  var SDK = 'https://www.gstatic.com/firebasejs/10.14.1/firebase-storage-compat.js';
  var st = { data: null, err: null, loading: false, busy: false, tab: null, urls: {}, uploads: {} };

  function rerender() { if (A.parseHash().view === 'content') { var y = scrollY; h.route(); scrollTo(0, y); } }
  function load(action, args, done) {
    st.busy = true;
    return h.call('adminContent', Object.assign({ action: action || 'list' }, args || {})).then(function (d) { st.data = d; st.err = null; if (done) h.toast(done); return d; })
      .catch(function (e) { var m = h.friendlyError(e); if (!action || action === 'list') st.err = m; else h.toast(m, true); return null; })
      .then(function (d) { st.busy = false; st.loading = false; rerender(); return d; });
  }
  var storageReady = null;
  function storage() {
    if (!storageReady) storageReady = new Promise(function (resolve, reject) {
      if (window.firebase && firebase.storage) return resolve(firebase.storage());
      var s = document.createElement('script'); s.src = SDK;
      s.onload = function () { resolve(firebase.storage()); };
      s.onerror = function () { storageReady = null; reject(new Error(T('Couldn’t load the file tools. Check the internet.', 'Não deu para carregar. Confira a internet.'))); };
      document.head.appendChild(s);
    });
    return storageReady;
  }
  function urlOf(path) {
    if (st.urls[path]) return Promise.resolve(st.urls[path]);
    return storage().then(function (s) { return s.ref(path).getDownloadURL(); }).then(function (u) { st.urls[path] = u; return u; });
  }

  /* ---------- words ---------- */
  var KIND = { video: ['Video', 'Vídeo', '🎬'], photo: ['Photo / art', 'Foto / arte', '🖼️'], idea: ['Idea', 'Ideia', '💡'] };
  var STATUS = { idea: ['Idea', 'Ideia'], todo: ['To make', 'Falta fazer'], ready: ['Ready, not scheduled', 'Pronto, falta agendar'], scheduled: ['Scheduled in Meta', 'Agendado no Meta'], posted: ['Posted', 'Postado'] };
  var NETS = [['instagram', 'Instagram'], ['facebook', 'Facebook'], ['tiktok', 'TikTok']];
  var WEEK = { pt: ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'], en: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'] };
  var MON = { pt: ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez'], en: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'] };
  function when(it) {
    if (!it.date) return T('No date', 'Sem data');
    var p = it.date.split('-'), d = new Date(+p[0], +p[1] - 1, +p[2]), L = h.LANG() === 'pt' ? 'pt' : 'en';
    var s = WEEK[L][d.getDay()] + ' ' + (+p[2]) + '/' + MON[L][+p[1] - 1];
    if (it.time) s += ' · ' + (L === 'pt' ? it.time.replace(':00', 'h').replace(':', 'h') : it.time);
    return s;
  }
  function size(n) { n = Number(n) || 0; return n >= 1073741824 ? (n / 1073741824).toFixed(1) + ' GB' : n >= 1048576 ? (n / 1048576).toFixed(0) + ' MB' : Math.max(1, Math.round(n / 1024)) + ' KB'; }
  function item(id) { return ((st.data && st.data.items) || []).find(function (x) { return x.id === id; }); }

  /* ---------- a post ---------- */
  function fileTile(it, f) {
    var isVid = /^video\//.test(f.type), url = st.urls[f.path];
    if (!url) urlOf(f.path).then(rerender).catch(function () {});
    var media = !url ? '<span class="ct-media ct-wait"></span>'
      : isVid ? '<video class="ct-media" src="' + esc(url) + '#t=0.1" preload="metadata" playsinline controls></video>'
      : '<a href="' + esc(url) + '" target="_blank" rel="noopener"><img class="ct-media" src="' + esc(url) + '" alt="" loading="lazy"></a>';
    return '<figure class="ct-file">' + media + '<figcaption><span class="tiny">' + esc(f.name) + ' · ' + size(f.size) + (f.w && f.h ? ' · ' + f.w + '×' + f.h : '') + '</span>' +
      '<span class="row"><button class="btn btn-honey btn-sm" data-act="ctSave" data-id="' + esc(it.id) + '" data-path="' + esc(f.path) + '">' + T('Save to phone', 'Salvar no celular') + '</button>' +
      '<button class="icon-btn" data-act="ctDelFile" data-id="' + esc(it.id) + '" data-path="' + esc(f.path) + '" aria-label="' + T('Remove', 'Apagar') + '">' + h.icon('trash') + '</button></span></figcaption></figure>';
  }
  /* what Meta has of it: the video itself (plays here), or its picture */
  function metaMedia(it) {
    var link = it.igLink || it.fbLink || '';
    if (it.kind === 'video' && /^https:\/\//.test(it.mediaUrl || '')) {
      return '<div class="ct-files one"><video class="ct-media" src="' + esc(it.mediaUrl) + '" poster="' + esc(it.preview || '') + '" preload="none" playsinline controls></video></div>';
    }
    if (/^https:\/\//.test(it.preview || '')) {
      return '<div class="ct-files one"><a class="ct-thumb" href="' + esc(link || it.preview) + '" target="_blank" rel="noopener"><img class="ct-media" src="' + esc(it.preview) + '" alt="" loading="lazy" referrerpolicy="no-referrer">' +
        (it.kind === 'video' ? '<span class="ct-play">▶</span>' : '') + '</a></div>';
    }
    return '';
  }
  /* "hoje às 19h", "amanhã às 11h30", "em 3 dias" */
  function soon(it) {
    if (!it.date) return '';
    var n = Math.round((Date.parse(it.date + 'T12:00:00Z') - Date.parse(st.data.today + 'T12:00:00Z')) / 86400000);
    var at = it.time ? (h.LANG() === 'pt' ? ' às ' + it.time.replace(':00', 'h').replace(':', 'h') : ' at ' + it.time) : '';
    if (n === 0) return T('today', 'hoje') + at;
    if (n === 1) return T('tomorrow', 'amanhã') + at;
    if (n === -1) return T('yesterday', 'ontem') + at;
    return n > 0 ? T('in ' + n + ' days', 'em ' + n + ' dias') : T(-n + ' days ago', 'há ' + (-n) + ' dias');
  }
  function card(it, extra) {
    var k = KIND[it.kind] || KIND.idea, s = STATUS[it.status] || STATUS.idea, b = st.busy ? ' disabled' : '';
    var up = st.uploads[it.id], files = it.files || [];
    var nets = NETS.filter(function (n) { return it.nets && it.nets[n[0]]; }).map(function (n) {
      var done = it.posted && it.posted[n[0]];
      return '<span class="ct-net' + (done ? ' done' : '') + '">' + (done ? '✓ ' : '') + n[1] + '</span>';
    }).join('');
    var late = it.date && (it.status === 'todo' || it.status === 'ready') && it.date < st.data.today;
    var from = it.source === 'plan' ? T('📅 From the 6-month calendar', '📅 Do calendário de 6 meses') : it.source === 'instagram' || it.source === 'facebook' ? T('Came from Meta', 'Veio do Meta') : '';
    var note = it.status === 'scheduled' ? T('Goes out by itself ', 'Sai sozinho ') + soon(it) + T('. When it does, the app marks it posted.', '. Quando sair, o app marca como postado.')
      : it.status === 'todo' && !files.length ? T('Nobody has filmed or made this yet.', 'Ninguém gravou nem fez ainda.')
      : it.status === 'ready' ? T('The file is here. Schedule it in Meta and tap "Scheduled in Meta".', 'O arquivo está aqui. Agende no Meta e toque em "Agendei no Meta".') : '';
    var tiktokLeft = it.status === 'posted' && it.nets && it.nets.tiktok && !(it.posted && it.posted.tiktok);
    var acts = [];
    var upBtn = '<label class="btn btn-sm ct-pick ' + (it.status === 'todo' || it.status === 'idea' ? 'btn-honey' : 'btn-ghost') + (up ? ' disabled' : '') + '">' + T('+ Video or photo', '+ Vídeo ou foto') +
      '<input type="file" accept="image/*,video/*" multiple data-ct-upload="' + esc(it.id) + '" hidden' + (up ? ' disabled' : '') + '></label>';
    if (it.status === 'idea') acts.push('<button class="btn btn-honey btn-sm" data-act="ctPromote" data-id="' + esc(it.id) + '"' + b + '>' + T('Turn into a post', 'Virar post') + '</button>', upBtn);
    if (it.status === 'todo') acts.push(upBtn, '<button class="btn btn-ghost btn-sm" data-act="ctScheduled" data-id="' + esc(it.id) + '"' + b + '>' + T('Scheduled in Meta', 'Agendei no Meta') + '</button>');
    if (it.status === 'ready') acts.push('<button class="btn btn-honey btn-sm" data-act="ctScheduled" data-id="' + esc(it.id) + '"' + b + '>' + T('Scheduled in Meta', 'Agendei no Meta') + '</button>', upBtn,
      '<button class="btn btn-ghost btn-sm" data-act="ctPosted" data-id="' + esc(it.id) + '"' + b + '>' + T('Posted', 'Postei') + '</button>');
    if (it.status === 'scheduled') acts.push('<button class="btn btn-ghost btn-sm" data-act="ctPosted" data-id="' + esc(it.id) + '"' + b + '>' + T('Already out', 'Já saiu') + '</button>');
    if (tiktokLeft) acts.push('<button class="btn btn-ghost btn-sm" data-act="ctTiktok" data-id="' + esc(it.id) + '"' + b + '>' + T('Posted on TikTok', 'Postei no TikTok') + '</button>');
    acts.push('<button class="btn btn-ghost btn-sm" data-act="ctEdit" data-id="' + esc(it.id) + '"' + b + '>' + T('Edit', 'Editar') + '</button>');
    return '<article class="card ct-card ct-' + esc(it.status) + '" id="ct-' + esc(it.id) + '">' +
      '<div class="ct-top"><span class="ct-when' + (late ? ' late' : '') + '">' + k[2] + ' ' + esc(when(it)) + '</span><span class="sp-pill ct-st-' + esc(it.status) + '">' + esc(T(s[0], s[1])) + '</span></div>' +
      (extra || '') + '<h3>' + esc(it.title || T('(no title)', '(sem título)')) + '</h3>' +
      (from ? '<p class="tiny muted ct-from">' + from + '</p>' : '') +
      (nets ? '<div class="ct-nets">' + nets + '</div>' : '') +
      (files.length ? '<div class="ct-files' + (files.length === 1 ? ' one' : '') + '">' + files.map(function (f) { return fileTile(it, f); }).join('') + '</div>' : metaMedia(it)) +
      (it.igLink || it.fbLink || it.igStats ? '<p class="tiny ct-links">' + (it.igStats ? '♥ ' + it.igStats.likes + ' · 💬 ' + it.igStats.comments + ' · ' : '') +
        (it.igLink ? '<a href="' + esc(it.igLink) + '" target="_blank" rel="noopener">Instagram ›</a> ' : '') + (it.fbLink ? '<a href="' + esc(it.fbLink) + '" target="_blank" rel="noopener">Facebook ›</a>' : '') + '</p>' : '') +
      (note ? '<p class="small ct-note">' + esc(note) + '</p>' : '') +
      (up ? '<div class="ct-up"><div class="sp-bar"><i style="width:' + Math.max(3, up.pct) + '%"></i></div><p class="tiny">' + esc(up.text) + '</p></div>' : '') +
      (it.caption && it.source === 'plan' || it.caption && it.status !== 'posted' ? '<details class="ct-more"><summary>' + T('Caption', 'Legenda') + '</summary><p class="ct-cap">' + esc(it.caption) + '</p>' +
        '<button class="btn btn-ghost btn-sm" data-act="ctCopy" data-id="' + esc(it.id) + '">' + h.icon('copy') + T('Copy caption', 'Copiar legenda') + '</button></details>' : '') +
      (it.status !== 'posted' && (it.script || it.onScreen || it.tip) ? '<details class="ct-more"><summary>' + T('How to film', 'Como gravar') + '</summary>' +
        (it.script ? '<p>' + esc(it.script) + '</p>' : '') + (it.onScreen ? '<p><b>' + T('Text on screen: ', 'Texto na tela: ') + '</b>' + esc(it.onScreen) + '</p>' : '') +
        (it.tip ? '<p class="small muted">' + esc(it.tip) + '</p>' : '') + '</details>' : '') +
      (it.notes ? '<p class="small ct-notes">📝 ' + esc(it.notes) + '</p>' : '') +
      '<div class="row sp-acts">' + acts.join('') + '</div></article>';
  }

  V.content = function () {
    if (!st.data && !st.loading && !st.err) { st.loading = true; load('list'); }
    var d = st.data;
    var head = '<div class="page-head"><div><p class="eyebrow">Marketing</p><h1>' + T('Content', 'Conteúdo') + '</h1>' +
      '<p class="sub">' + T('What is out, what goes out by itself from Meta, what is left to make and your ideas. Videos and photos pass between you in full quality.',
        'O que já saiu, o que sai sozinho pelo Meta, o que falta fazer e as ideias de vocês. Vídeos e fotos passam entre vocês na qualidade original.') + '</p></div>' +
      '<div class="actions"><button class="btn btn-honey btn-sm" data-act="ctNew">' + T('+ New post or idea', '+ Novo post ou ideia') + '</button></div></div>';
    if (!d) return { title: T('Content', 'Conteúdo'), html: '<div translate="no">' + head + (st.err ? '<p class="err">' + esc(st.err) + '</p>' : '<div class="loading"><span>' + T('Loading…', 'Carregando…') + '</span></div>') + '</div>' };
    var all = d.items, t = d.today;
    var is = function (k) { return function (i) { return i.status === k; }; };
    var TABS = [
      ['scheduled', T('In Meta', 'No Meta'), is('scheduled')],
      ['todo', T('To make', 'Falta fazer'), function (i) { return i.status === 'todo' && (!i.date || i.date >= t); }],
      ['ready', T('Ready', 'Prontos'), function (i) { return i.status === 'ready' && (!i.date || i.date >= t); }],
      ['posted', T('Posted', 'Postados'), is('posted')],
      ['ideas', T('Ideas', 'Ideias'), is('idea')]
    ];
    var PAST = ['past', T('Day passed', 'Passaram do dia'), function (i) { return (i.status === 'todo' || i.status === 'ready') && i.date && i.date < t; }];
    var count = function (x) { return all.filter(x[2]).length; };
    if (!st.tab) st.tab = count(TABS[0]) ? 'scheduled' : 'todo';
    var cur = st.tab === 'past' ? PAST : TABS.find(function (x) { return x[0] === st.tab; }) || TABS[1];
    var list = all.filter(cur[2]);
    if (cur[0] === 'posted') list = list.slice().reverse();

    /* the two things that matter now: what goes out next, and what to film next */
    var nextOut = all.filter(function (i) { return i.status === 'scheduled' && i.date && i.date >= t; })[0];
    var nextMake = all.filter(function (i) { return i.status === 'todo' && i.date && i.date >= t; })[0];
    var heroOut = nextOut
      ? '<button class="ct-hero-box out" data-act="ctJump" data-id="' + esc(nextOut.id) + '" data-tab="scheduled"><b>' + T('Next out', 'Próximo a sair') + '</b><strong>' + esc(soon(nextOut)) + '</strong><span>' + esc(nextOut.title) + '</span></button>'
      : '<div class="ct-hero-box out empty"><b>' + T('Next out', 'Próximo a sair') + '</b><strong>' + T('Nothing marked', 'Nada marcado') + '</strong><span>' +
        T('Meta doesn’t show other apps what you schedule in Business Suite. After scheduling there, tap "Scheduled in Meta" on the post; when it goes out, the app sees it by itself.',
          'O Meta não mostra para outros apps o que vocês agendam no Business Suite. Agendou lá, toque em "Agendei no Meta" no post. Quando ele sair, o app vê sozinho.') + '</span></div>';
    var heroMake = nextMake
      ? '<button class="ct-hero-box make" data-act="ctJump" data-id="' + esc(nextMake.id) + '" data-tab="todo"><b>' + T('Next to make', 'Próximo a fazer') + '</b><strong>' + esc(soon(nextMake)) + '</strong><span>' + (KIND[nextMake.kind] || KIND.idea)[2] + ' ' + esc(nextMake.title) + '</span></button>'
      : '<div class="ct-hero-box make empty"><b>' + T('Next to make', 'Próximo a fazer') + '</b><strong>' + T('All done', 'Tudo feito') + '</strong><span></span></div>';
    var hero = '<div class="ct-hero">' + heroOut + heroMake + '</div>';

    var make7 = all.filter(function (i) { return i.status === 'todo' && i.date && i.date >= t && i.date <= addDays(t, 6); }).length;
    var posted30 = all.filter(function (i) { return i.status === 'posted' && i.date && i.date >= addDays(t, -30); }).length;
    var tiles = '<div class="tiles">' +
      h.tile(T('In Meta', 'No Meta'), String(count(TABS[0])), T('goes out by itself', 'sai sozinho'), true) +
      h.tile(T('To make, 7 days', 'Falta fazer, 7 dias'), String(make7), T('film or make', 'gravar ou fazer')) +
      h.tile(T('Posted, 30 days', 'Postados, 30 dias'), String(posted30), 'Instagram · Facebook · TikTok') +
      h.tile(T('Ideas', 'Ideias'), String(count(TABS[4])), T('for later', 'para depois')) + '</div>';

    /* the week: one chip per day, a mark per post */
    var MARK = { scheduled: '✅', posted: '✔︎', ready: '📦', todo: '⏳', idea: '💡' };
    var strip = '<div class="ct-week">' + [0, 1, 2, 3, 4, 5, 6].map(function (n) {
      var dd = addDays(t, n), its = all.filter(function (i) { return i.date === dd && i.status !== 'idea'; });
      var p = dd.split('-'), L = h.LANG() === 'pt' ? 'pt' : 'en', wd = WEEK[L][new Date(+p[0], +p[1] - 1, +p[2]).getDay()];
      return '<div class="ct-day' + (n === 0 ? ' today' : '') + '"><b>' + (n === 0 ? T('Today', 'Hoje') : wd) + '</b><span>' + (+p[2]) + '</span><i>' +
        (its.length ? its.map(function (i) { return '<em class="ct-dot ct-st-' + esc(i.status) + '" title="' + esc(i.title) + '">' + MARK[i.status] + '</em>'; }).join('') : '·') + '</i></div>';
    }).join('') + '</div><p class="tiny muted ct-legend">✅ ' + T('in Meta', 'no Meta') + ' · 📦 ' + T('ready, not scheduled', 'pronto, falta agendar') + ' · ⏳ ' + T('to make', 'falta fazer') + ' · ✔︎ ' + T('posted', 'postado') + '</p>';

    var sy = d.sync || {}, syncLine = sy.connected === false ? T('Connect Meta on the Ads page to bring in what is posted.', 'Conecte o Meta na página Anúncios para trazer o que já foi postado.')
      : sy.at ? T('Meta checked ', 'Meta conferido ') + esc(h.fmtDT(sy.at)) + (sy.counts ? ' · ' + T(sy.counts.instagram + ' on Instagram, ' + sy.counts.facebook + ' on Facebook', sy.counts.instagram + ' no Instagram, ' + sy.counts.facebook + ' no Facebook') : '') : '';
    var syncErr = sy.errors && Object.keys(sy.errors).length ? '<p class="tiny err">' + Object.keys(sy.errors).map(function (k) { return esc(k + ': ' + sy.errors[k]); }).join(' · ') + '</p>' : '';
    var syncBar = '<div class="ct-sync"><span class="tiny muted">' + syncLine + '</span><button class="btn btn-ghost btn-sm" data-act="ctSync"' + (st.busy ? ' disabled' : '') + '>' + h.icon('refresh') + T('Update from Meta', 'Atualizar do Meta') + '</button></div>' + syncErr;

    var tabs = '<div class="seg ct-tabs" role="tablist">' + TABS.map(function (x) {
      var n = count(x);
      if (x[0] === 'ready' && !n && cur[0] !== 'ready') return '';
      return '<button role="tab" data-act="ctTab" data-tab="' + x[0] + '"' + (x[0] === cur[0] ? ' class="on" aria-selected="true"' : '') + '>' + esc(x[1]) + (n ? ' <span class="count">' + n + '</span>' : '') + '</button>';
    }).join('') + '</div>';

    var top = '';
    if (cur[0] === 'ideas') top = '<form class="ct-quick" data-ct-quick><input class="input" name="idea" placeholder="' + T('An idea, in a few words…', 'Uma ideia, em poucas palavras…') + '" maxlength="120" autocomplete="off">' +
      '<button class="btn btn-honey btn-sm"' + (st.busy ? ' disabled' : '') + '>' + T('Save idea', 'Guardar') + '</button></form>';
    if (cur[0] === 'todo') { var pastN = count(PAST); if (pastN) top = '<button class="ct-past" data-act="ctTab" data-tab="past">' + T(pastN + ' from the calendar passed their day without being made ›', pastN + (pastN === 1 ? ' do calendário passou do dia sem ser feito ›' : ' do calendário passaram do dia sem ser feitos ›')) + '</button>'; }
    if (cur[0] === 'past') top = '<p class="small muted">' + T('These were planned for a day that passed. Make them later (Edit › new day), or delete.', 'Estavam planejados para um dia que já passou. Dá para fazer depois (Editar › novo dia) ou apagar.') +
      ' <button class="btn btn-ghost btn-sm" data-act="ctTab" data-tab="todo">‹ ' + T('Back', 'Voltar') + '</button></p>';
    if (cur[0] === 'scheduled' && !list.length) top = '<p class="small muted">' + T('Nothing marked yet. Scheduled something in Meta Business Suite? Find it in To make and tap "Scheduled in Meta".', 'Nada marcado ainda. Agendou algo no Meta Business Suite? Ache o post em Falta fazer e toque em "Agendei no Meta".') + '</p>';

    /* the most liked of the last 30 days gets a trophy */
    var champ = null;
    if (cur[0] === 'posted') list.forEach(function (i) { if (i.igStats && i.date >= addDays(t, -30) && (!champ || i.igStats.likes > champ.igStats.likes)) champ = i; });
    var cap = cur[0] === 'todo' || cur[0] === 'posted' ? (st.more ? 300 : 12) : 300;
    var shown = list.slice(0, cap);
    var body = shown.length ? '<div class="ct-list">' + shown.map(function (i) { return card(i, champ && i === champ && champ.igStats.likes > 0 ? '<span class="ct-badge">🏆 ' + T('Most liked this month', 'Mais curtido do mês') + '</span>' : ''); }).join('') + '</div>' +
      (list.length > shown.length ? '<p><button class="btn btn-ghost" data-act="ctMore">' + T('Show all ' + list.length, 'Mostrar todos os ' + list.length) + '</button></p>' : '')
      : cur[0] === 'scheduled' ? '' : '<p class="muted">' + T('Nothing here.', 'Nada aqui.') + '</p>';
    var tip = cur[0] === 'todo' || cur[0] === 'ready' || cur[0] === 'ideas' ? '<p class="tiny muted ct-tip">' + T('Full quality on iPhone: when picking a video or photo, tap Options at the top and choose Current, so the iPhone doesn’t shrink it.',
      'Qualidade máxima no iPhone: ao escolher o vídeo ou a foto, toque em Opções, lá em cima, e escolha Atual. Assim o iPhone não diminui o arquivo.') + '</p>' : '';
    return { title: T('Content', 'Conteúdo'), html: '<div translate="no" class="ct">' + head + hero + tiles + strip + syncBar + tabs + top + tip + body + '</div>' };
  };
  function addDays(day, n) { var p = day.split('-'), d = new Date(+p[0], +p[1] - 1, +p[2] + n); return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0'); }

  /* ---------- uploads: the original file, as it is ---------- */
  function mediaSize(file) {
    return new Promise(function (resolve) {
      var url = URL.createObjectURL(file), done = function (o) { URL.revokeObjectURL(url); resolve(o); };
      if (/^video\//.test(file.type)) {
        var v = document.createElement('video'); v.preload = 'metadata'; v.muted = true;
        v.onloadedmetadata = function () { done({ w: v.videoWidth, h: v.videoHeight, dur: Math.round(v.duration || 0) }); };
        v.onerror = function () { done({}); }; v.src = url;
      } else {
        var i = new Image(); i.onload = function () { done({ w: i.naturalWidth, h: i.naturalHeight }); }; i.onerror = function () { done({}); }; i.src = url;
      }
      setTimeout(function () { done({}); }, 8000);
    });
  }
  function safeName(n) { return String(n || 'file').replace(/[^A-Za-z0-9._ ()-]/g, '_').slice(-100); }
  function uploadAll(id, files) {
    var list = Array.prototype.slice.call(files).filter(function (f) { return /^(image|video)\//.test(f.type); });
    if (!list.length) { h.toast(T('Only photos and videos.', 'Só fotos e vídeos.'), true); return; }
    var i = 0;
    var next = function () {
      if (i >= list.length) { delete st.uploads[id]; return load('list', null, T('Sent. The other phone got a notification.', 'Enviado. O outro celular recebeu um aviso.')); }
      var f = list[i++], path = 'content/' + id + '/' + Date.now() + '-' + safeName(f.name);
      st.uploads[id] = { pct: 0, text: T('Uploading ', 'Enviando ') + (list.length > 1 ? i + '/' + list.length + ' · ' : '') + size(f.size) + '…' };
      rerender();
      return Promise.all([storage(), mediaSize(f)]).then(function (r) {
        var dims = r[1];
        return new Promise(function (resolve, reject) {
          // the file goes as it is: no resizing, no re-encoding
          var task = r[0].ref(path).put(f, { contentType: f.type, customMetadata: { name: safeName(f.name) } });
          task.on('state_changed', function (s) {
            var pct = s.totalBytes ? Math.round(s.bytesTransferred / s.totalBytes * 100) : 0;
            st.uploads[id] = { pct: pct, text: T('Uploading ', 'Enviando ') + (list.length > 1 ? i + '/' + list.length + ' · ' : '') + pct + '% de ' + size(f.size) };
            var bar = document.querySelector('#ct-' + id + ' .ct-up');
            if (bar) { bar.querySelector('i').style.width = Math.max(3, pct) + '%'; bar.querySelector('p').textContent = st.uploads[id].text; }
          }, reject, function () { resolve(dims); });
        });
      }).then(function (dims) {
        return h.call('adminContent', { action: 'addFile', id: id, path: path, name: f.name, type: f.type, size: f.size, w: dims.w, h: dims.h, dur: dims.dur });
      }).then(next).catch(function (e) {
        delete st.uploads[id];
        h.toast(T('The upload stopped: ', 'O envio parou: ') + h.friendlyError(e), true);
        rerender();
      });
    };
    next();
  }
  document.addEventListener('change', function (ev) {
    var el = ev.target;
    if (!el || !el.matches || !el.matches('[data-ct-upload]')) return;
    var id = el.getAttribute('data-ct-upload'), files = el.files;
    if (files && files.length) uploadAll(id, files);
    el.value = '';
  });

  /* ---------- saving to the phone: the same bytes that were uploaded ---------- */
  ACT.ctSave = function (el) {
    var it = item(el.getAttribute('data-id')), path = el.getAttribute('data-path');
    var f = it && (it.files || []).find(function (x) { return x.path === path; });
    if (!f) return;
    var label = el.textContent;
    el.disabled = true; el.textContent = T('Preparing…', 'Preparando…');
    var reset = function () { el.disabled = false; el.textContent = label; };
    urlOf(path).then(function (url) {
      // big videos open in Safari's own player (Share › Save Video), so the phone doesn't run out of memory
      if (f.size > 350 * 1048576 || !navigator.canShare) { window.open(url, '_blank', 'noopener'); reset(); return; }
      return fetch(url).then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.blob(); }).then(function (b) {
        var file = new File([b], f.name, { type: f.type || b.type });
        if (navigator.canShare({ files: [file] })) return navigator.share({ files: [file] }).catch(function () {});
        var a = document.createElement('a'); a.href = URL.createObjectURL(b); a.download = f.name; document.body.appendChild(a); a.click(); a.remove();
      }).then(reset);
    }).catch(function (e) { reset(); h.toast(h.friendlyError(e), true); });
  };
  ACT.ctDelFile = function (el) {
    var id = el.getAttribute('data-id'), path = el.getAttribute('data-path');
    h.dialog({ title: T('Delete this file?', 'Apagar este arquivo?'), html: '<p>' + T('It is deleted for both of you.', 'Ele some para os dois.') + '</p>', ok: T('Delete', 'Apagar'), cancel: T('Cancel', 'Cancelar'), danger: true })
      .then(function (ok) { if (ok) load('removeFile', { id: id, path: path }); });
  };
  ACT.ctCopy = function (el) { var it = item(el.getAttribute('data-id')); if (it) h.copyText(it.caption, T('Caption copied.', 'Legenda copiada.')); };
  ACT.ctTab = function (el) { st.tab = el.getAttribute('data-tab'); st.more = false; h.route(); };
  ACT.ctJump = function (el) {
    st.tab = el.getAttribute('data-tab'); h.route();
    var id = el.getAttribute('data-id');
    setTimeout(function () { var c = document.getElementById('ct-' + id); if (c) { c.scrollIntoView({ behavior: 'smooth', block: 'center' }); c.classList.add('ct-flash'); } }, 60);
  };
  ACT.ctTiktok = function (el) {
    var it = item(el.getAttribute('data-id')); if (!it) return;
    var nets = {}; NETS.forEach(function (n) { nets[n[0]] = !!(it.posted && it.posted[n[0]]); }); nets.tiktok = true;
    load('posted', { id: it.id, nets: nets }, T('Ticked TikTok.', 'TikTok marcado.'));
  };
  /* quick idea: a few words, saved as an idea */
  document.addEventListener('submit', function (ev) {
    var f = ev.target;
    if (!f || !f.matches || !f.matches('[data-ct-quick]')) return;
    ev.preventDefault();
    var v = (f.idea.value || '').trim(); if (!v) return;
    load('save', { item: { title: v, kind: 'idea', status: 'idea', nets: {} } }, T('Idea saved.', 'Ideia guardada.'));
  });
  ACT.ctMore = function () { st.more = true; h.route(); };
  ACT.ctSync = function () { load('sync', {}, T('Up to date with Meta.', 'Atualizado com o Meta.')); };

  /* ---------- the form ---------- */
  function ask(title, inner, okText, extra) {
    return new Promise(function (resolve) {
      var dlg = document.createElement('dialog'); dlg.className = 'modal'; dlg.setAttribute('translate', 'no');
      dlg.innerHTML = '<form method="dialog" class="in"><h2>' + esc(title) + '</h2>' + inner + '<div class="row end">' + (extra || '') +
        '<button class="btn btn-ghost" value="cancel">' + T('Cancel', 'Cancelar') + '</button><button class="btn btn-honey" value="ok">' + esc(okText || 'OK') + '</button></div></form>';
      document.body.appendChild(dlg);
      dlg.addEventListener('close', function () {
        var out = null;
        if (dlg.returnValue === 'ok') { out = {}; Array.prototype.forEach.call(dlg.querySelectorAll('[name]'), function (e) { out[e.name] = e.type === 'checkbox' ? e.checked : e.value; }); }
        if (dlg.returnValue === 'delete') out = { __delete: true };
        dlg.remove(); resolve(out);
      });
      if (dlg.showModal) dlg.showModal(); else dlg.setAttribute('open', '');
    });
  }
  function field(name, label, value, type) {
    return '<label class="field"><span>' + esc(label) + '</span><input class="input" name="' + name + '" value="' + esc(value == null ? '' : value) + '"' + (type ? ' type="' + type + '"' : '') + '></label>';
  }
  function area(name, label, value, rows) { return '<label class="field"><span>' + esc(label) + '</span><textarea class="input" name="' + name + '" rows="' + (rows || 3) + '">' + esc(value || '') + '</textarea></label>'; }
  function select(name, label, value, opts) {
    return '<label class="field"><span>' + esc(label) + '</span><select class="input" name="' + name + '">' + opts.map(function (o) { return '<option value="' + o[0] + '"' + (o[0] === value ? ' selected' : '') + '>' + esc(o[1]) + '</option>'; }).join('') + '</select></label>';
  }
  function form(it) {
    it = it || { kind: 'video', status: 'todo', nets: { instagram: true, facebook: true, tiktok: true } };
    return field('title', T('Title', 'Título'), it.title) +
      select('kind', T('Kind', 'Tipo'), it.kind, Object.keys(KIND).map(function (k) { return [k, T(KIND[k][0], KIND[k][1])]; })) +
      select('status', T('Status', 'Situação'), it.status, Object.keys(STATUS).map(function (k) { return [k, T(STATUS[k][0], STATUS[k][1])]; })) +
      '<div class="row">' + field('date', T('Day', 'Dia'), it.date, 'date') + field('time', T('Time', 'Hora'), it.time, 'time') + '</div>' +
      '<div class="ct-checks">' + NETS.map(function (n) { return '<label><input type="checkbox" name="net_' + n[0] + '"' + (it.nets && it.nets[n[0]] ? ' checked' : '') + '> ' + n[1] + '</label>'; }).join('') + '</div>' +
      area('caption', T('Caption (English, for the post)', 'Legenda (em inglês, para o post)'), it.caption, 4) +
      area('script', T('How to film', 'Como gravar'), it.script, 2) + field('onScreen', T('Text on screen', 'Texto na tela'), it.onScreen) +
      area('notes', T('Notes between you', 'Recado entre vocês'), it.notes, 2);
  }
  function toItem(v) {
    var o = { title: v.title, kind: v.kind, status: v.status, date: v.date, time: v.time, caption: v.caption, script: v.script, onScreen: v.onScreen, notes: v.notes, nets: {} };
    NETS.forEach(function (n) { o.nets[n[0]] = !!v['net_' + n[0]]; });
    return o;
  }
  ACT.ctNew = function () {
    ask(T('New post or idea', 'Novo post ou ideia'), form(null) + '<p class="tiny muted">' + T('Save it, then add the video or photo on the card.', 'Salve e depois toque em "+ Vídeo ou foto" no cartão.') + '</p>', T('Save', 'Salvar'))
      .then(function (v) {
        if (!v) return;
        load('save', { item: toItem(v) }).then(function (d) {
          if (!d || !d.id) return;
          var it = item(d.id);
          st.tab = !it ? st.tab : it.status === 'idea' ? 'ideas' : it.date && it.date < d.today && (it.status === 'todo' || it.status === 'ready') ? 'past' : it.status;
          h.route();
          setTimeout(function () { var c = document.getElementById('ct-' + d.id); if (c) c.scrollIntoView({ behavior: 'smooth', block: 'center' }); }, 60);
        });
      });
  };
  ACT.ctEdit = function (el) {
    var it = item(el.getAttribute('data-id')); if (!it) return;
    ask(T('Edit', 'Editar'), form(it), T('Save', 'Salvar'), '<button class="btn btn-ghost danger" value="delete" style="margin-right:auto">' + T('Delete post', 'Apagar post') + '</button>').then(function (v) {
      if (!v) return;
      if (v.__delete) {
        return h.dialog({ title: T('Delete this post and its files?', 'Apagar este post e os arquivos dele?'), html: '', ok: T('Delete', 'Apagar'), cancel: T('Cancel', 'Cancelar'), danger: true })
          .then(function (ok) { if (ok) load('remove', { id: it.id }, T('Deleted.', 'Apagado.')); });
      }
      load('save', { id: it.id, item: toItem(v) }, T('Saved.', 'Salvo.'));
    });
  };
  ACT.ctScheduled = function (el) {
    var it = item(el.getAttribute('data-id')); if (!it) return;
    ask(T('Scheduled in Meta', 'Agendei no Meta'), '<p class="small muted">' + T('The day and time you picked in Meta Business Suite. When it goes out, the app sees it and moves it to Posted.',
      'O dia e a hora que vocês escolheram no Meta Business Suite. Quando sair, o app vê e passa para Postados.') + '</p>' +
      '<div class="row">' + field('date', T('Day', 'Dia'), it.date || st.data.today, 'date') + field('time', T('Time', 'Hora'), it.time || '11:30', 'time') + '</div>' +
      '<div class="ct-checks">' + NETS.slice(0, 2).map(function (n) { return '<label><input type="checkbox" name="net_' + n[0] + '"' + (!it.nets || it.nets[n[0]] !== false ? ' checked' : '') + '> ' + n[1] + '</label>'; }).join('') + '</div>',
      T('Save', 'Salvar')).then(function (v) {
      if (!v) return;
      var nets = Object.assign({}, it.nets || {}, { instagram: !!v.net_instagram, facebook: !!v.net_facebook });
      load('save', { id: it.id, item: { status: 'scheduled', date: v.date, time: v.time, nets: nets } }, T('In Meta. It goes out by itself.', 'No Meta. Sai sozinho.'));
    });
  };
  ACT.ctPromote = function (el) {
    var it = item(el.getAttribute('data-id')); if (!it) return;
    var copy = Object.assign({}, it, { status: 'todo', kind: 'video', date: it.date || addDays(st.data.today, 2), time: it.time || '19:00', nets: { instagram: true, facebook: true, tiktok: true } });
    ask(T('Turn into a post', 'Virar post'), form(copy), T('Save', 'Salvar')).then(function (v) {
      if (v) load('save', { id: it.id, item: toItem(v) }, T('It’s in To make.', 'Está em Falta fazer.'));
    });
  };
  ACT.ctPosted = function (el) {
    var it = item(el.getAttribute('data-id')); if (!it) return;
    var nets = NETS.filter(function (n) { return it.nets && it.nets[n[0]]; });
    if (!nets.length) nets = NETS;
    ask(T('Where did it go out?', 'Onde já foi postado?'), '<div class="ct-checks">' + nets.map(function (n) {
      return '<label><input type="checkbox" name="' + n[0] + '"' + (it.posted && it.posted[n[0]] ? ' checked' : ' checked') + '> ' + n[1] + '</label>';
    }).join('') + '</div><p class="tiny muted">' + T('It moves to Posted. A network left unticked stays on the card to tick later.', 'Ele vai para Postados. A rede que ficar sem marcar aparece no cartão para marcar depois.') + '</p>', T('Save', 'Salvar')).then(function (v) {
      if (v) load('posted', { id: it.id, nets: v }, T('Saved.', 'Salvo.'));
    });
  };
})();
