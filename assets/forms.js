/* Little Hive House: contact.html (form → callable contact, or the email app while the store isn't connected),
   suggestions.html (ideas box → callable suggest)
   and unsubscribe.html (callable unsubscribe({e, t}) from the link in our emails). Needs site.js and store.js first. */
(function () {
  var S = window.LHHStore;
  var $ = function (id) { return document.getElementById(id); };
  var q = new URLSearchParams(location.search);
  var EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  function say(el, text, kind) { el.textContent = text || ''; el.className = 'msg' + (kind ? ' ' + kind : ''); el.hidden = !text; }

  /* ---------- contact ---------- */
  var form = $('contact-form');
  if (form) {
    var f = form.elements, msg = $('contact-msg');
    if (q.get('order')) f.order.value = q.get('order').slice(0, 20);
    var topic = q.get('topic'); if (topic && f.topic.querySelector('option[value="' + topic.replace(/[^a-z-]/g, '') + '"]')) f.topic.value = topic;
    if (!S.configured) $('contact-hint').textContent = 'This opens your email app with your message filled in.';
    S.onUser(function (u) {
      if (!S.isMember(u)) return;
      if (!f.name.value) f.name.value = u.displayName || '';
      if (!f.email.value) f.email.value = u.email || '';
    });
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var name = f.name.value.trim(), email = f.email.value.trim(), text = f.message.value.trim(), order = f.order.value.trim();
      var topicLabel = f.topic.options[f.topic.selectedIndex].text;
      if (!name) { say(msg, 'Please tell us your name.', 'err'); f.name.focus(); return; }
      if (!EMAIL_RE.test(email)) { say(msg, 'Please enter your email so we can reply.', 'err'); f.email.focus(); return; }
      if (text.length < 5) { say(msg, 'Please write a short message.', 'err'); f.message.focus(); return; }
      var body = (order ? 'Order: ' + order + '\n\n' : '') + text;
      if (!S.configured) {
        location.href = 'mailto:' + S.support + '?subject=' + encodeURIComponent(topicLabel + (order ? ' (' + order + ')' : '')) +
          '&body=' + encodeURIComponent(body + '\n\n' + name + '\n' + email);
        say(msg, 'Your email app should open now. If it doesn’t, write to us at ' + S.support + '.', 'ok');
        return;
      }
      var b = form.querySelector('button[type="submit"]');
      b.disabled = true; b.textContent = 'Sending…'; say(msg, '');
      S.call('contact', { name: name, email: email, topic: topicLabel, message: body, website: f.website.value }).then(function () {
        $('contact-done-name').textContent = name.split(/\s+/)[0];
        $('contact-done-email').textContent = email;
        form.hidden = true; $('contact-done').hidden = false; $('contact-done').focus();
      }).catch(function (er) {
        b.disabled = false; b.textContent = 'Send message';
        say(msg, S.message(er), 'err');
      });
    });
  }

  /* ---------- ideas box (suggestions.html) ---------- */
  var idea = $('idea-form');
  if (idea) {
    var g = idea.elements, imsg = $('idea-msg');
    var k = (q.get('kind') || '').replace(/[^a-z]/g, ''); if (k && g.kind.querySelector('option[value="' + k + '"]')) g.kind.value = k;
    if (q.get('idea')) g.idea.value = q.get('idea').slice(0, 300);
    if (!S.configured) $('idea-hint').textContent = 'This opens your email app with your idea filled in.';
    S.onUser(function (u) {
      if (!S.isMember(u)) return;
      if (!g.name.value) g.name.value = u.displayName || '';
      if (!g.email.value) g.email.value = u.email || '';
    });
    $('idea-again').addEventListener('click', function () {
      g.idea.value = ''; $('idea-done').hidden = true; idea.hidden = false; g.idea.focus();
    });
    idea.addEventListener('submit', function (e) {
      e.preventDefault();
      var name = g.name.value.trim(), email = g.email.value.trim(), text = g.idea.value.trim();
      var kindLabel = g.kind.options[g.kind.selectedIndex].text;
      if (text.length < 3) { say(imsg, 'Please tell us your idea.', 'err'); g.idea.focus(); return; }
      if (email && !EMAIL_RE.test(email)) { say(imsg, 'That email doesn’t look right. You can also leave it empty.', 'err'); g.email.focus(); return; }
      if (!S.configured) {
        location.href = 'mailto:' + S.support + '?subject=' + encodeURIComponent('An idea: ' + kindLabel) +
          '&body=' + encodeURIComponent(text + (name || email ? '\n\n' + [name, email].filter(Boolean).join('\n') : ''));
        say(imsg, 'Your email app should open now. If it doesn’t, write to us at ' + S.support + '.', 'ok');
        return;
      }
      var b = idea.querySelector('button[type="submit"]');
      b.disabled = true; b.textContent = 'Sending…'; say(imsg, '');
      S.call('suggest', { kind: g.kind.value, idea: text, name: name, email: email, page: document.referrer.slice(0, 200), website: g.website.value }).then(function () {
        b.disabled = false; b.textContent = 'Send my idea';
        $('idea-done-name').textContent = name ? ', ' + name.split(/\s+/)[0] : '';
        $('idea-done-email').textContent = email ? ' and will write to ' + email + ' if we make it' : '';
        idea.hidden = true; $('idea-done').hidden = false; $('idea-done').focus();
      }).catch(function (er) {
        b.disabled = false; b.textContent = 'Send my idea';
        say(imsg, S.message(er), 'err');
      });
    });
  }

  /* ---------- unsubscribe ---------- */
  var un = $('unsub');
  if (un) {
    var e = q.get('e') || '', t = q.get('t') || '';
    var state = function (id) { ['un-ask', 'un-done', 'un-bad', 'un-soon'].forEach(function (k) { $(k).hidden = k !== id; }); };
    if (!e || !t) return state('un-bad');
    if (!S.configured) return state('un-soon');
    $('un-email').textContent = e;
    state('un-ask');
    $('un-go').addEventListener('click', function () {
      var b = $('un-go'), m = $('un-msg');
      b.disabled = true; b.textContent = 'One moment…'; say(m, '');
      S.call('unsubscribe', { e: e, t: t }).then(function () {
        $('un-done-email').textContent = e; state('un-done'); $('un-done').focus();
      }).catch(function (er) {
        b.disabled = false; b.textContent = 'Unsubscribe';
        var c = String(er.code || '').replace(/^functions\//, '');
        say(m, c === 'invalid-argument' || c === 'permission-denied' ? 'This link has expired or is incomplete. Email ' + S.support + ' and we’ll remove you by hand.' : S.message(er), 'err');
      });
    });
  }
})();
