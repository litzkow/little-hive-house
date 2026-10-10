/* Little Hive House: contact.html (form → callable contact, or the email app while the store isn't connected)
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
