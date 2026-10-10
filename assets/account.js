/* Little Hive House: account.html. Sign in / create account / forgot password, and the signed-in home
   (recent orders, favorites, email preference, sign out). Needs site.js, store.js and orders.js first. */
(function () {
  var S = window.LHHStore, L = window.LHH;
  var $ = function (id) { return document.getElementById(id); };
  var q = new URLSearchParams(location.search);
  var EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  function show(id) { ['st-loading', 'st-soon', 'st-auth', 'st-home', 'st-error'].forEach(function (k) { $(k).hidden = k !== id; }); }
  function say(el, text, kind) { el.textContent = text || ''; el.className = 'msg' + (kind ? ' ' + kind : ''); el.hidden = !text; }
  function busy(btn, on, label) { btn.disabled = on; if (on) { btn.dataset.label = btn.textContent; btn.textContent = label; btn.setAttribute('aria-busy', 'true'); } else { btn.textContent = btn.dataset.label || btn.textContent; btn.removeAttribute('aria-busy'); } }
  /* only same-site page names, e.g. orders.html or order.html?id=abc */
  function nextUrl() { var n = q.get('next') || ''; return /^[a-z0-9-]+\.html(\?[\w=&%.-]*)?$/i.test(n) ? S.base + n : null; }

  if (!S.configured) { $('page-lede').textContent = 'Customer accounts are almost ready. Here’s what you can do in the meantime.'; show('st-soon'); return; }

  /* ---------- tabs (sign in / create account) + forgot password ---------- */
  var tabs = [$('tab-in'), $('tab-up')], panes = { 'tab-in': $('pane-in'), 'tab-up': $('pane-up') };
  function pick(tab, focus) {
    $('pane-reset').hidden = true; $('auth-tabs').hidden = false;
    tabs.forEach(function (t) {
      var on = t === tab;
      t.setAttribute('aria-selected', String(on)); t.tabIndex = on ? 0 : -1;
      panes[t.id].hidden = !on;
    });
    if (focus) { var f = panes[tab.id].querySelector('input:not([type=checkbox])'); if (f) f.focus(); }
  }
  tabs.forEach(function (t, i) {
    t.addEventListener('click', function () { pick(t, true); });
    t.addEventListener('keydown', function (e) {
      if (e.key !== 'ArrowRight' && e.key !== 'ArrowLeft' && e.key !== 'Home' && e.key !== 'End') return;
      e.preventDefault();
      var n = e.key === 'Home' ? 0 : e.key === 'End' ? tabs.length - 1 : (i + (e.key === 'ArrowRight' ? 1 : -1) + tabs.length) % tabs.length;
      pick(tabs[n]); tabs[n].focus();
    });
  });
  document.querySelectorAll('[data-go]').forEach(function (a) {
    a.addEventListener('click', function (e) {
      e.preventDefault();
      var to = a.getAttribute('data-go');
      if (to === 'reset') {
        var em = ($('in-email').value || $('up-email').value || '').trim();
        if (em) $('reset-email').value = em;
        $('auth-tabs').hidden = true; $('pane-in').hidden = true; $('pane-up').hidden = true; $('pane-reset').hidden = false;
        say($('reset-msg'), ''); $('reset-email').focus();
      } else pick($(to), true);
    });
  });
  document.querySelectorAll('[data-reveal]').forEach(function (b) {
    b.addEventListener('click', function () {
      var inp = $(b.getAttribute('data-reveal')), shown = inp.type === 'text';
      inp.type = shown ? 'password' : 'text';
      b.textContent = shown ? 'Show' : 'Hide';
      b.setAttribute('aria-pressed', String(!shown));
    });
  });

  var prefill = q.get('email');
  if (prefill && EMAIL_RE.test(prefill)) { $('in-email').value = prefill; $('up-email').value = prefill; }
  pick(q.get('tab') === 'create' || location.hash === '#create' ? $('tab-up') : $('tab-in'));

  function done() { var n = nextUrl(); if (n) location.href = n; }

  $('pane-in').addEventListener('submit', function (e) {
    e.preventDefault();
    var msg = $('in-msg'), email = $('in-email').value.trim(), pw = $('in-pw').value, b = $('in-go');
    if (!EMAIL_RE.test(email)) { say(msg, 'Please enter your email address.', 'err'); $('in-email').focus(); return; }
    if (!pw) { say(msg, 'Please enter your password.', 'err'); $('in-pw').focus(); return; }
    say(msg, ''); busy(b, true, 'Signing in…');
    S.signIn(email, pw).then(function () { busy(b, false); $('in-pw').value = ''; done(); })
      .catch(function (er) { busy(b, false); say(msg, S.message(er), 'err'); });
  });

  $('pane-up').addEventListener('submit', function (e) {
    e.preventDefault();
    var msg = $('up-msg'), name = $('up-name').value.trim(), email = $('up-email').value.trim(), pw = $('up-pw').value, b = $('up-go');
    if (!name) { say(msg, 'Please tell us your name.', 'err'); $('up-name').focus(); return; }
    if (!EMAIL_RE.test(email)) { say(msg, 'That email address doesn’t look right.', 'err'); $('up-email').focus(); return; }
    if (pw.length < 8) { say(msg, 'Please use at least 8 characters for your password.', 'err'); $('up-pw').focus(); return; }
    say(msg, ''); busy(b, true, 'Creating your account…');
    S.signUp({ name: name, email: email, password: pw, marketing: $('up-mkt').checked })
      .then(function () { busy(b, false); $('up-pw').value = ''; if (window.LHH) L.toast('Welcome to Little Hive House, ' + name.split(/\s+/)[0] + '!'); done(); })
      .catch(function (er) {
        busy(b, false); say(msg, S.message(er), 'err');
        if (/already-in-use/.test(er.code || '')) { $('in-email').value = email; }
      });
  });

  $('pane-reset').addEventListener('submit', function (e) {
    e.preventDefault();
    var msg = $('reset-msg'), email = $('reset-email').value.trim(), b = $('reset-go');
    if (!EMAIL_RE.test(email)) { say(msg, 'Please enter the email you use for your account.', 'err'); $('reset-email').focus(); return; }
    busy(b, true, 'Sending…');
    S.sendReset(email).then(function () {
      busy(b, false);
      say(msg, 'Check your inbox. If there’s an account for ' + email + ', we just sent a link to choose a new password. It can take a minute, and sometimes lands in spam.', 'ok');
    }).catch(function (er) {
      busy(b, false);
      var c = String(er.code || '').replace(/^functions\//, '');
      /* never reveal whether an account exists */
      if (c === 'not-found') say(msg, 'Check your inbox. If there’s an account for ' + email + ', we just sent a link to choose a new password.', 'ok');
      else say(msg, S.message(er), 'err');
    });
  });

  /* ---------- signed-in home ---------- */
  var homeFor = null, loadSeq = 0;
  function loadOrders() {
    var list = $('recent'), empty = $('recent-empty'), more = $('recent-more'), seq = ++loadSeq;
    list.replaceChildren(); empty.hidden = true; more.hidden = true; $('recent-loading').hidden = false;
    return S.myOrders().then(function (orders) {
      if (seq !== loadSeq) return;     /* a newer load (e.g. right after the email was confirmed) wins */
      $('recent-loading').hidden = true;
      if (!orders.length) { empty.hidden = false; return; }
      orders.slice(0, 3).forEach(function (o) { list.append(window.LHHOrders.card(o)); });
      more.hidden = orders.length <= 3;
      more.textContent = 'See all ' + orders.length + ' orders';
    }).catch(function (er) { if (seq !== loadSeq) return; $('recent-loading').hidden = true; empty.hidden = false; empty.querySelector('p').textContent = S.message(er); });
  }

  /* ---------- "please confirm your email" ---------- */
  function linkKey(u) { return 'lhh-linked-' + u.uid; }
  function linkedAlready(u) { try { return localStorage.getItem(linkKey(u)) === '1'; } catch (e) { return false; } }
  /* once the email is confirmed: welcome() links guest orders placed with it (once per account and device) */
  function onVerified(u, fromLink) {
    $('verify-banner').hidden = true;
    if (fromLink && window.LHH) L.toast('Thank you! Your email is confirmed.');
    if (linkedAlready(u)) return;
    S.call('welcome', {}).then(function (r) {
      try { localStorage.setItem(linkKey(u), '1'); } catch (e) {}
      if (r && r.linked) {
        if (window.LHH) L.toast(r.linked === 1 ? 'We found 1 earlier order with your email and added it to your account.' : 'We found ' + r.linked + ' earlier orders with your email and added them to your account.');
        loadOrders();
      }
    }).catch(function () {});
  }
  function verifyState(u) {
    var b = $('verify-banner'), fromLink = q.get('verified') === '1';
    if (S.verified(u)) { onVerified(u, false); return; }
    $('verify-email').textContent = u.email || 'your email';
    b.hidden = false;
    /* maybe they just tapped the link (in this tab or another): ask Firebase again */
    S.refreshUser().then(function (fresh) {
      if (fresh && S.verified(fresh)) { onVerified(fresh, fromLink); loadOrders(); }   /* guest orders with this email now count */
    }).catch(function () {});
  }
  $('verify-resend').addEventListener('click', function () {
    var b = $('verify-resend'), msg = $('verify-msg');
    busy(b, true, 'Sending…');
    S.resendVerify().then(function (r) {
      busy(b, false);
      if (r && r.already) { onVerified(S.user(), true); return; }
      say(msg, 'Sent! Check your inbox for an email from Little Hive House. It can take a minute, and sometimes lands in spam.', 'ok');
    }).catch(function (er) { busy(b, false); say(msg, S.message(er), 'err'); });
  });
  $('verify-check').addEventListener('click', function () {
    var b = $('verify-check'), msg = $('verify-msg');
    busy(b, true, 'Checking…');
    S.refreshUser().then(function (fresh) {
      busy(b, false);
      if (fresh && S.verified(fresh)) { say(msg, ''); onVerified(fresh, true); loadOrders(); }
      else say(msg, 'Not confirmed yet. Tap the button in the email we sent you, then come back and try again.', 'err');
    }).catch(function (er) { busy(b, false); say(msg, S.message(er), 'err'); });
  });

  function home(u) {
    var name = u.displayName || '';
    $('page-title').textContent = name ? 'Hi, ' + name.split(/\s+/)[0] + '!' : 'Your account';
    $('page-lede').textContent = 'Signed in as ' + u.email + '.';
    $('me-name').textContent = name || '—';
    $('me-email').textContent = u.email || '';
    show('st-home');
    if (homeFor === u.uid) return;
    homeFor = u.uid;
    say($('verify-msg'), '');
    verifyState(u);
    loadOrders();
    var mk = $('me-mkt');
    S.getProfile().then(function (p) { mk.checked = !!p.marketing; mk.disabled = false; }).catch(function () { mk.disabled = false; });
  }
  $('me-mkt').addEventListener('change', function () {
    var mk = $('me-mkt'), msg = $('me-msg');
    mk.disabled = true;
    S.saveProfile({ marketing: mk.checked }).then(function () {
      mk.disabled = false; say(msg, mk.checked ? 'You’re on the list for new designs and offers. You can turn this off anytime.' : 'Done. We won’t send you marketing emails. Order emails still arrive.', 'ok');
    }).catch(function (er) { mk.disabled = false; mk.checked = !mk.checked; say(msg, S.message(er), 'err'); });
  });
  $('me-reset').addEventListener('click', function () {
    var u = S.user(), msg = $('me-msg'), b = $('me-reset');
    busy(b, true, 'Sending…');
    S.sendReset(u.email).then(function () { busy(b, false); say(msg, 'We emailed ' + u.email + ' a link to choose a new password.', 'ok'); })
      .catch(function (er) { busy(b, false); say(msg, S.message(er), 'err'); });
  });
  $('me-out').addEventListener('click', function () {
    S.signOut().then(function () { if (window.LHH) L.toast('You’re signed out. See you soon!'); });
  });

  S.onUser(function (u) {
    if (S.isMember(u)) {
      if (nextUrl() && !homeFor) { location.replace(nextUrl()); return; }
      home(u);
    } else {
      if (homeFor) { homeFor = null; pick($('tab-in')); }   /* just signed out: back to "Sign in", not the last tab */
      $('page-title').textContent = 'Your account';
      $('page-lede').textContent = 'Sign in to see your orders and tracking, and keep your favorite designs on every device.';
      show('st-auth');
    }
  });
  S.ready().catch(function (e) { $('st-error-msg').textContent = S.message(e); show('st-error'); });
})();
