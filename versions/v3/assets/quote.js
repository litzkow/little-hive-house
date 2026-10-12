/* Little Hive House: big-order quote form. Opens the customer's email app with the request filled in. */
(function () {
  var form = document.getElementById('quote');
  if (!form) return;
  document.querySelectorAll('[data-pkg]').forEach(function (b) {
    b.addEventListener('click', function () {
      form.elements.occasion.value = b.getAttribute('data-pkg');
      var q = b.getAttribute('data-qty');
      if (q) form.elements.quantity.value = q;
      form.scrollIntoView({ behavior: 'smooth', block: 'start' });
      setTimeout(function () { form.elements.name.focus({ preventScroll: true }); }, 400);
    });
  });
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    if (!form.reportValidity()) return;
    var f = form.elements;
    var lines = [
      'Name: ' + f.name.value,
      'Email: ' + f.email.value,
      'Occasion: ' + f.occasion.value,
      'How many magnets: ' + f.quantity.value,
      'Date needed: ' + (f.date.value || 'Flexible'),
      '',
      f.message.value
    ];
    var subject = 'Big order request: ' + f.occasion.value + ' (' + f.quantity.value + ' magnets)';
    location.href = 'mailto:support@littlehivehouse.com?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(lines.join('\n'));
    var done = document.getElementById('quote-done');
    done.hidden = false;
  });
})();
