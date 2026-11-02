/* The opening screen of Hive Admin: a little honeycomb filling with honey while two bees fly around it, and a few
   sweet lines that change while the app loads, in the language each person chose (i18n.js keeps it in localStorage).
   index.html shows it straight away; admin.js shows it again while the orders load. Calm when the phone asks for less
   motion. */
(function () {
  'use strict';
  var LINES = {
    pt: ['Abrindo a colmeia…', 'Acordando as abelhas…', 'Contando o mel…', 'Separando os ímãs…', 'Quase pronto…'],
    en: ['Opening the hive…', 'Waking up the bees…', 'Counting the honey…', 'Sorting the magnets…', 'Almost there…']
  };
  function lang() { try { var l = localStorage.getItem('lhh-admin-lang'); if (l === 'en' || l === 'pt') return l; } catch (e) { /* ignore */ } return 'pt'; }
  // seven cells: the middle one and six around it (flat-topped hexagons, radius 17)
  function hex(cx, cy, r) {
    var p = [];
    for (var i = 0; i < 6; i++) { var a = Math.PI / 3 * i; p.push((cx + r * Math.cos(a)).toFixed(1) + ',' + (cy + r * Math.sin(a)).toFixed(1)); }
    return p.join(' ');
  }
  var CELLS = [[80, 70], [80, 40], [106, 55], [106, 85], [80, 100], [54, 85], [54, 55]];
  function bee(cls) {
    return '<g class="bee ' + cls + '"><g class="bee-bob">' +
      '<ellipse class="wing w1" cx="-3" cy="-9" rx="6" ry="8"/><ellipse class="wing w2" cx="5" cy="-8" rx="5" ry="7"/>' +
      '<ellipse cx="0" cy="0" rx="11" ry="8" fill="#F5B83A"/>' +
      '<path d="M-3 -7.6v15.2M3.5 -7v14" stroke="#2B2118" stroke-width="3" stroke-linecap="round"/>' +
      '<circle cx="11" cy="-1" r="5" fill="#2B2118"/><circle cx="12.6" cy="-2.4" r="1.3" fill="#FFF"/>' +
      '<path d="M13 -5.5c1.5-3 3.5-4.5 5-4.5M10.5 -5.8c.5-3.2 2-5.2 3.4-5.8" stroke="#2B2118" stroke-width="1.2" fill="none" stroke-linecap="round"/>' +
      '<path d="M-11 0l-4 0" stroke="#2B2118" stroke-width="2" stroke-linecap="round"/></g></g>';
  }
  function html() {
    var l = lang();
    var cells = CELLS.map(function (c, i) {
      return '<polygon class="cell" style="animation-delay:' + (i * 0.22).toFixed(2) + 's" points="' + hex(c[0], c[1], 16.5) + '"/>';
    }).join('');
    return '<div class="boot" role="status" aria-live="polite"><svg class="boot-art" viewBox="0 0 160 140" aria-hidden="true">' +
      '<g class="comb">' + cells + '<path class="drip" d="M80 116c-2.4 4-3.6 6.6-3.6 8.4a3.6 3.6 0 0 0 7.2 0c0-1.8-1.2-4.4-3.6-8.4z"/></g>' +
      bee('b1') + bee('b2') + '</svg><p class="boot-txt" data-boot-lines>' + LINES[l][0] + '</p></div>';
  }
  var timer = null;
  function start() {
    if (timer) return;
    var i = 0, l = lang();
    timer = setInterval(function () {
      var el = document.querySelector('[data-boot-lines]');
      if (!el) { clearInterval(timer); timer = null; return; }
      i = (i + 1) % LINES[l].length;
      el.classList.add('out');
      setTimeout(function () { el.textContent = LINES[l][i]; el.classList.remove('out'); }, 220);
    }, 1500);
  }
  window.LHHBoot = { html: html, start: start, lines: LINES };
  var app = document.getElementById('app');
  if (app && app.querySelector('.boot-placeholder')) { app.innerHTML = html(); start(); }
})();
