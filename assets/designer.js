/* Little Hive House: the magnet designs for businesses and events (business.html, weddings.html, graduation.html,
   parties.html) and the studio where a customer makes one their own: colors, words, their logo or photo, then buys
   the pack. The same code draws the gallery pictures (tools/biz_designs.py), the studio preview and the order in
   Hive Admin, so what the customer sees is what the owners get.
   window.LHHDesigner = { render(design, choices) -> html of a 600 x 600 magnet, fit(el), icons, palettes, open(slug) }
   Designs and palettes come from assets/designs.js (built from tools/biz_designs.py). */
(function () {
  'use strict';
  var DATA = window.LHHDesigns || { list: [], pal: {} };

  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function T(s) { return esc(s).replace(/\n/g, '<br>'); }

  /* ---------------------------------------------------------------- icons (64 x 64, drawn in the color c) */
  var S = 'fill="none" stroke="{c}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"';
  function st(d) { return '<path ' + S + ' d="' + d + '"/>'; }
  function circ(cx, cy, r) { return '<circle ' + S + ' cx="' + cx + '" cy="' + cy + '" r="' + r + '"/>'; }
  var ICONS = {
    tooth: st('M22 8C12 8 8 18 11 28c3 10 5 14 6 24 1 8 7 9 9 1 1-7 3-11 6-11s5 4 6 11c2 8 8 7 9-1 1-10 3-14 6-24 3-10-1-20-11-20-7 0-8 4-10 4s-3-4-10-4z') + st('M42 16c4 1 6 4 6 8'),
    pizza: '<path d="M32 4 58 54Q32 64 6 54Z" fill="#F2C14E" stroke="{c}" stroke-width="4" stroke-linejoin="round"/><path d="M10 50Q32 58 54 50" fill="none" stroke="#C97B2C" stroke-width="5"/><circle cx="32" cy="26" r="5" fill="#B23A2B"/><circle cx="24" cy="40" r="5" fill="#B23A2B"/><circle cx="40" cy="42" r="5" fill="#B23A2B"/>',
    sparkle: '<path d="M30 8c2 14 8 20 22 22-14 2-20 8-22 22-2-14-8-20-22-22 14-2 20-8 22-22z" fill="{c}"/><path d="M50 4c1 5 3 7 8 8-5 1-7 3-8 8-1-5-3-7-8-8 5-1 7-3 8-8z" fill="{c}"/>',
    spray: st('M20 28h20v26a4 4 0 0 1-4 4H24a4 4 0 0 1-4-4z') + st('M24 28v-8h12v8M28 20v-6h14l4 6') + st('M52 10l6-2M52 16h7M52 22l6 2'),
    house: st('M8 30 32 10l24 20M14 26v28h36V26M27 54V40h10v14'),
    key: circ(20, 32, 11) + st('M31 32h26M49 32v9M56 32v7'),
    flame: '<path d="M32 60c-13 0-20-9-18-20 2-10 12-14 12-28 8 6 14 14 14 22 4-4 4-8 4-10 6 6 8 14 6 22-2 9-9 14-18 14z" fill="{c}"/>',
    snow: st('M32 6v52M10 19l44 26M10 45l44-26M26 10l6 6 6-6M26 54l6-6 6 6'),
    drop: '<path d="M32 6C24 20 14 30 14 41a18 18 0 0 0 36 0C50 30 40 20 32 6z" fill="{c}"/>',
    wrench: st('M44 8a12 12 0 0 0-12 16L10 46a5 5 0 0 0 8 8l22-22a12 12 0 0 0 16-12l-8 8-8-2-2-8z'),
    car: st('M6 42v-9l7-13h38l7 13v9z') + circ(18, 44, 6) + circ(46, 44, 6) + st('M16 30h32'),
    scissors: circ(18, 48, 8) + circ(46, 48, 8) + st('M23 42 48 8M41 42 16 8'),
    comb: st('M8 22h48v10H8zM12 32v18M18 32v18M24 32v18M30 32v18M36 32v18M42 32v18M48 32v18M54 32v12'),
    dumbbell: '<path d="M6 26v12M14 18v28M50 18v28M58 26v12M14 32h36" fill="none" stroke="{c}" stroke-width="7" stroke-linecap="round"/>',
    lotus: st('M32 50c-6-8-6-20 0-30 6 10 6 22 0 30zM32 50c-10 0-20-8-22-20 10 0 18 6 22 20zM32 50c10 0 20-8 22-20-10 0-18 6-22 20zM12 54h40'),
    paw: '<g fill="{c}"><ellipse cx="32" cy="42" rx="13" ry="11"/><ellipse cx="15" cy="27" rx="6" ry="8"/><ellipse cx="26" cy="15" rx="6" ry="8"/><ellipse cx="38" cy="15" rx="6" ry="8"/><ellipse cx="49" cy="27" rx="6" ry="8"/></g>',
    bone: st('M18 22a6 6 0 1 0-6 8l26 22a6 6 0 1 0 8-6l6-6a6 6 0 1 0-8-8l-6 6L22 14a6 6 0 1 0-8 8'),
    shield: st('M32 6l20 8v16c0 14-10 24-20 28-10-4-20-14-20-28V14z') + st('M22 32l7 7 13-14'),
    scale: st('M32 8v46M20 56h24M12 18h40M12 18 5 34h14zM52 18l-7 16h14z'),
    leaf: '<path d="M32 58V30" stroke="{c}" stroke-width="4" stroke-linecap="round"/><path d="M32 40C16 40 8 28 10 10c16 0 24 12 22 30zM32 32c14 0 22-10 22-26-14 0-22 10-22 26z" fill="{c}"/>',
    tree: st('M32 60V42M32 6C20 6 14 16 16 26c-6 4-4 16 6 16h20c10 0 12-12 6-16 2-10-4-20-16-20z'),
    hammer: '<path d="M14 54 38 30" stroke="{c}" stroke-width="7" stroke-linecap="round"/><path d="M28 16l12-10 18 18-10 12z" fill="{c}"/>',
    roof: st('M4 34 32 10l28 24M12 28v26h40V28') + st('M20 38h24M20 46h24'),
    bolt: '<path d="M36 4 12 36h17l-4 24 25-34H33z" fill="{c}"/>',
    bug: '<ellipse ' + S + ' cx="32" cy="36" rx="12" ry="16"/>' + st('M32 20v32M26 14l-4-6M38 14l4-6M20 30H8M20 40H8M44 30h12M44 40h12M22 48l-8 8M42 48l8 8'),
    truck: st('M4 16h34v28H4zM38 26h12l10 10v8H38z') + circ(16, 48, 6) + circ(48, 48, 6),
    flower: '<g fill="{c}"><circle cx="32" cy="16" r="9"/><circle cx="47" cy="27" r="9"/><circle cx="41" cy="44" r="9"/><circle cx="23" cy="44" r="9"/><circle cx="17" cy="27" r="9"/></g><circle cx="32" cy="31" r="7" fill="#F2C14E"/>',
    camera: st('M6 20h12l5-7h18l5 7h12v32H6z') + circ(32, 35, 10),
    cross: '<path d="M32 4v56M16 20h32" stroke="{c}" stroke-width="7" stroke-linecap="round"/>',
    apple: st('M32 18c-10-8-24-2-22 14 2 16 12 26 22 22 10 4 20-6 22-22 2-16-12-22-22-14zM32 18c0-6 4-10 8-12'),
    steth: st('M14 8v16a11 11 0 0 0 22 0V8M25 35v7a11 11 0 0 0 22 0v-8') + circ(47, 28, 6),
    heart: '<path d="M32 56C14 42 6 32 8 20c2-10 16-14 24-2 8-12 22-8 24 2 2 12-6 22-24 36z" fill="{c}"/>',
    cup: st('M10 26h36v14c0 10-8 16-18 16S10 50 10 40zM46 30c10 0 10 14 0 14') + st('M22 8c-4 5 4 7 0 12M32 6c-4 5 4 7 0 12'),
    cake: st('M8 56h48V34H8zM8 44c6 4 10 4 16 0 6 4 10 4 16 0 6 4 10 4 16 0M32 34V24') + '<path d="M32 18c-4-4 0-10 0-10s4 6 0 10z" fill="{c}"/>',
    bread: st('M8 54V30c0-10 10-16 24-16s24 6 24 16v24zM22 26l-4 10M32 24v12M42 26l4 10'),
    taco: st('M6 48a26 26 0 0 1 52 0z') + '<path d="M12 36c4-6 8-2 12-6s8 2 12-2 8 2 12-2 6 4 6 8" fill="none" stroke="#5E9E4A" stroke-width="5" stroke-linecap="round"/>',
    bowl: st('M8 30h48a24 24 0 0 1-48 0zM20 56h24M48 6 30 26M56 10 36 28'),
    star: '<path d="M32 4l8 18 20 2-15 13 5 19-18-10-18 10 5-19L4 24l20-2z" fill="{c}"/>',
    rings: circ(24, 36, 15) + circ(40, 36, 15) + st('M36 12l4-6 4 6-4 4z'),
    cap: '<path d="M32 12 62 26 32 40 2 26z" fill="{c}"/><path d="M16 33v13c0 6 32 6 32 0V33L32 40z" fill="{c}"/><path d="M56 29v16" stroke="{c}" stroke-width="3"/><circle cx="56" cy="47" r="3.5" fill="{c}"/>',
    balloon: st('M32 6c-11 0-18 9-18 19 0 12 10 20 18 22 8-2 18-10 18-22 0-10-7-19-18-19zM29 47h6l-3 5zM32 52c-4 4 4 6 0 10'),
    cheers: st('M10 10l14 4-3 16c-1 5-7 6-10 3zM54 10l-14 4 3 16c1 5 7 6 10 3zM17 33l-4 20M47 33l4 20M8 56h12M44 56h12'),
    gift: st('M8 24h48v10H8zM12 34h40v22H12zM32 24v32M32 24c-6-12-18-10-14-2 2 3 8 2 14 2zM32 24c6-12 18-10 14-2-2 3-8 2-14 2z'),
    mic: '<rect ' + S + ' x="22" y="6" width="20" height="32" rx="10"/>' + st('M14 30c0 10 8 18 18 18s18-8 18-18M32 48v10M22 58h20'),
    phone: '<path d="M18 6h8l4 12-6 4c3 7 8 12 15 15l4-6 12 4v8c0 4-3 7-7 7C27 50 10 33 10 13c0-4 3-7 8-7z" fill="{c}"/>',
    calc: '<rect ' + S + ' x="12" y="6" width="40" height="52" rx="5"/>' + st('M20 14h24v10H20zM20 34h2M31 34h2M42 34h2M20 44h2M31 44h2M42 44h2M20 52h2M31 52h2M42 52h2'),
    sun: circ(32, 32, 11) + st('M32 4v8M32 52v8M4 32h8M52 32h8M12 12l6 6M46 46l6 6M12 52l6-6M46 18l6-6'),
    polish: st('M22 28h20v26a4 4 0 0 1-4 4H26a4 4 0 0 1-4-4zM26 28V8h12v20'),
    book: st('M6 12h20a6 6 0 0 1 6 6v38a5 5 0 0 0-5-5H6zM58 12H38a6 6 0 0 0-6 6v38a5 5 0 0 1 5-5h21z'),
    tag: st('M6 6h24l28 28-24 24L6 30z') + circ(18, 18, 4),
    clock: circ(32, 32, 24) + st('M32 18v15l10 6'),
    lock: '<rect ' + S + ' x="12" y="28" width="40" height="28" rx="5"/>' + st('M20 28v-8a12 12 0 0 1 24 0v8M32 38v8'),
    hook: st('M32 4v30a11 11 0 1 1-11 11') + st('M22 4h20'),
    chef: st('M18 40a10 10 0 0 1-2-20 12 12 0 0 1 22-6 10 10 0 0 1 12 18v8zM18 40v12h28V40'),
    building: st('M10 58V8h28v50M38 22h16v36M6 58h52M18 18h4M28 18h4M18 28h4M28 28h4M18 38h4M28 38h4M45 32h3M45 42h3'),
    pin: st('M32 58S12 38 12 24a20 20 0 0 1 40 0c0 14-20 34-20 34z') + circ(32, 24, 7),
    music: st('M22 46V12l30-6v34') + '<circle cx="16" cy="46" r="7" fill="{c}"/><circle cx="46" cy="40" r="7" fill="{c}"/>',
    church: st('M32 4v12M26 10h12M16 30l16-14 16 14M20 26v32h24V26M8 58h48M28 58V46h8v12'),
    pool: st('M4 46c7-6 14-6 21 0s14 6 21 0 10-4 14-2M20 40V12a6 6 0 0 1 12 0M36 40V12a6 6 0 0 1 12 0M20 22h28M20 32h28'),
    brush: st('M40 6l18 18-20 20-18-18zM20 26l-6 6c-6 6-4 14-10 22 8-6 16-4 22-10l6-6'),
    baby: circ(32, 34, 20) + st('M25 32h1M38 32h1M26 42c4 3 8 3 12 0M32 14c-4-6 4-10 6-4'),
    suitcase: '<rect ' + S + ' x="6" y="18" width="52" height="36" rx="5"/>' + st('M24 18v-6h16v6M6 32h52'),
    plate: circ(32, 34, 20) + circ(32, 34, 12) + st('M4 10v12a4 4 0 0 0 4 4v30M8 10v12M60 10c-6 0-6 10-6 16h6v30'),
    glasses: circ(18, 36, 10) + circ(46, 36, 10) + st('M28 36c2-3 6-3 8 0M8 34 4 22M56 34l4-12'),
    wave: st('M4 26c7-7 14-7 21 0s14 7 21 0 10-5 14-2M4 40c7-7 14-7 21 0s14 7 21 0 10-5 14-2')
  };

  /* the customer's logo replaces the drawing wherever the design has one */
  var cur = null;
  function ic(name, size, c) {
    if (cur && cur.logo) return '<img src="' + esc(cur.logo) + '" alt="" style="display:block;flex:none;width:' + size + 'px;height:' + size + 'px;object-fit:contain">';
    var body = ICONS[name] || ICONS.star;
    return '<svg width="' + size + '" height="' + size + '" viewBox="0 0 64 64" style="display:block;flex:none">' + body.split('{c}').join(c) + '</svg>';
  }
  function star(size, c) { return '<svg width="' + size + '" height="' + size + '" viewBox="0 0 64 64" style="display:block;flex:none">' + ICONS.star.split('{c}').join(c) + '</svg>'; }
  function qr(url, px, fg) { return window.LHHQR ? window.LHHQR.svg(url, px, fg || '#1B1B1B', '#FFFFFF') : '<div style="width:' + px + 'px;height:' + px + 'px;background:#eee"></div>'; }
  function photo(p) { return "url('" + String(p.photo || '').replace(/'/g, '%27') + "')"; }
  function def(v, d) { return v == null || v === '' ? d : v; }

  var A = "Anton", BE = "'Bebas Neue'", JO = "'Josefin Sans'", JT = "Jost", CA = "Caveat", PL = "'Playfair Display'", DS = "'DM Serif Display'",
    CI = "Cinzel", CO = "'Cormorant Garamond'", DA = "'Dancing Script'";
  var SQ = 'width:600px;height:600px;position:relative;overflow:hidden;';
  /* one line that shrinks to fit its box (see fit()) */
  function one(style, html) { return '<div data-fit style="white-space:nowrap;' + style + '">' + html + '</div>'; }

  /* ---------------------------------------------------------------- layouts (p: the design, colors and words) */
  var L = {};
  L.bar = function (p) {
    return '<div style="' + SQ + 'background:' + p.bg + ';color:' + p.ink + ';padding:38px 40px">' +
      '<div style="display:flex;align-items:center;gap:18px"><div style="width:96px;height:96px;border-radius:50%;background:' + (p.logo ? '#fff' : p.ac) + ';display:grid;place-items:center;flex:none">' + ic(p.icon, p.logo ? 76 : 62, def(p.icon_c, p.bg)) + '</div>' +
      '<div style="min-width:0;flex:1">' + one('font:400 50px/1.05 ' + A + ';text-transform:uppercase;letter-spacing:1px', T(p.name)) +
      one('font:700 18px ' + JO + ';letter-spacing:5px;color:' + p.ac + ';margin-top:8px', T(p.sub)) + '</div></div>' +
      one('font:400 ' + def(p.hs, 74) + 'px/1 ' + A + ';text-transform:uppercase;margin-top:34px', T(p.head)) +
      '<div style="font:500 26px ' + JT + ';margin-top:14px;opacity:.9">' + T(p.line) + '</div>' +
      '<div style="position:absolute;left:0;right:0;bottom:0;height:116px;background:' + p.ac + ';color:' + def(p.bar_ink, p.bg) + ';display:flex;align-items:center;justify-content:center;gap:18px;padding:0 30px">' +
      '<svg width="46" height="46" viewBox="0 0 64 64" style="flex:none">' + ICONS.phone.split('{c}').join(def(p.bar_ink, p.bg)) + '</svg>' +
      one('font:400 78px/1 ' + BE + ';letter-spacing:2px;padding-top:8px;min-width:0', T(p.phone)) + '</div></div>';
  };
  L.hazard = function (p) {
    var s = 'repeating-linear-gradient(-45deg,' + p.ac + ' 0 26px,' + p.ink + ' 26px 52px)';
    return '<div style="' + SQ + 'background:' + p.bg + ';color:' + p.ink + ';text-align:center"><div style="height:46px;background:' + s + '"></div>' +
      '<div style="padding:26px 34px 0;display:flex;flex-direction:column;align-items:center">' +
      '<div style="display:flex;align-items:center;justify-content:center;gap:14px;max-width:100%">' + ic(p.icon, 64, p.ink) + one('font:400 58px/1.05 ' + A + ';text-transform:uppercase;min-width:0', T(p.name)) + '</div>' +
      one('font:700 19px ' + JO + ';letter-spacing:6px;margin-top:10px;max-width:100%', T(p.sub)) +
      one('font:400 40px/1.05 ' + A + ';text-transform:uppercase;margin-top:28px;max-width:100%;color:' + def(p.head_c, p.ink), T(p.head)) +
      '<div style="margin-top:16px;background:' + p.ink + ';color:' + p.bg + ';padding:14px 26px 6px;border-radius:10px;max-width:100%">' + one('font:400 86px/1 ' + BE + ';letter-spacing:2px', T(p.phone)) + '</div>' +
      '<div style="font:600 22px ' + JT + ';margin-top:16px">' + T(p.line) + '</div></div>' +
      '<div style="position:absolute;left:0;right:0;bottom:0;height:46px;background:' + s + '"></div></div>';
  };
  L.classic = function (p) {
    return '<div style="' + SQ + 'background:' + p.bg + ';color:' + p.ink + ';text-align:center;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:40px 50px">' +
      '<div style="position:absolute;inset:18px;border:3px solid ' + p.ac + '"></div><div style="position:absolute;inset:28px;border:1px solid ' + p.ac + '"></div>' +
      ic(p.icon, p.logo ? 120 : 96, def(p.icon_c, p.ac)) +
      one('font:' + def(p.font, 'italic 700 66px/1.1 ' + PL) + ';margin-top:14px;max-width:100%', T(p.name)) +
      one('font:700 18px ' + JO + ';letter-spacing:6px;margin-top:14px;max-width:100%;color:' + p.ac, T(p.sub)) +
      '<div style="display:flex;align-items:center;gap:14px;margin-top:22px"><span style="width:60px;height:2px;background:' + p.ac + '"></span>' + star(18, p.ac) + '<span style="width:60px;height:2px;background:' + p.ac + '"></span></div>' +
      '<div style="font:500 26px ' + JT + ';margin-top:18px">' + T(p.line) + '</div>' +
      one('font:400 64px/1 ' + BE + ';letter-spacing:2px;margin-top:12px;max-width:100%', T(p.phone)) + '</div>';
  };
  L.split = function (p) {
    var items = (p.items || []).filter(function (x) { return String(x).trim(); }).map(function (x) {
      return '<div style="display:flex;align-items:center;gap:12px;font:500 25px ' + JT + ';margin-top:12px"><span style="width:30px;height:30px;border-radius:50%;background:' + p.ac + ';display:grid;place-items:center;flex:none">' +
        '<svg width="18" height="18" viewBox="0 0 20 20"><path d="M4 10l4 4 8-9" fill="none" stroke="' + p.bg + '" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg></span>' + one('min-width:0;flex:1', T(x)) + '</div>';
    }).join('');
    return '<div style="' + SQ + 'background:' + p.bg + ';color:' + p.ink + ';display:flex">' +
      '<div style="width:180px;flex:none;background:' + p.ac + ';display:flex;flex-direction:column;align-items:center;justify-content:space-between;padding:44px 0">' +
      (p.logo ? '<div style="background:#fff;border-radius:16px;padding:10px">' + ic(p.icon, 112, p.bg) + '</div>' : ic(p.icon, 104, p.bg)) +
      '<div style="writing-mode:vertical-rl;transform:rotate(180deg);font:700 20px ' + JO + ';letter-spacing:7px;color:' + p.bg + ';white-space:nowrap;max-height:250px;overflow:hidden">' + T(p.since) + '</div></div>' +
      '<div style="flex:1;min-width:0;padding:42px 34px 0"><div style="font:400 50px/1.02 ' + DS + '">' + T(p.name) + '</div>' +
      one('font:700 17px ' + JO + ';letter-spacing:5px;margin-top:10px;color:' + p.ac, T(p.sub)) + '<div style="margin-top:12px">' + items + '</div>' +
      one('font:700 44px ' + JT + ';margin-top:24px;letter-spacing:.5px', T(p.phone)) + one('font:500 21px ' + JT + ';opacity:.75;margin-top:2px', T(p.web)) + '</div></div>';
  };
  L.badge = function (p) {
    var r = 196, cx = 300, cy = 248;
    function arc(rr, sweep) { return 'M ' + (cx - rr) + ',' + cy + ' a ' + rr + ',' + rr + ' 0 1,' + sweep + ' ' + 2 * rr + ',0'; }
    var name = String(p.name || '').toUpperCase(), fs = Math.max(24, Math.min(42, Math.floor(640 / Math.max(1, name.length)) + 6));
    var sub = String(p.sub || ''), ss = Math.max(15, Math.min(22, Math.floor(560 / Math.max(1, sub.length)) + 4));
    var mid = p.logo ? '<foreignObject x="' + (cx - 70) + '" y="' + (cy - 96) + '" width="140" height="140"><div xmlns="http://www.w3.org/1999/xhtml" style="width:140px;height:140px;display:grid;place-items:center">' + ic(p.icon, 128, p.ac) + '</div></foreignObject>'
      : '<g transform="translate(' + (cx - 52) + ' ' + (cy - 76) + ')">' + ic(p.icon, 104, p.ac).replace(/^<svg /, '<svg x="0" y="0" ') + '</g>';
    return '<div style="' + SQ + 'background:' + p.bg + ';color:' + p.ink + ';text-align:center">' +
      '<svg width="600" height="470" viewBox="0 0 600 470" style="display:block"><defs><path id="bt" d="' + arc(r - 66, 1) + '"/><path id="bb" d="' + arc(r - 72, 0) + '"/></defs>' +
      '<circle cx="' + cx + '" cy="' + cy + '" r="' + r + '" fill="' + p.ac + '"/><circle cx="' + cx + '" cy="' + cy + '" r="' + (r - 12) + '" fill="none" stroke="' + p.bg + '" stroke-width="3"/>' +
      '<circle cx="' + cx + '" cy="' + cy + '" r="' + (r - 88) + '" fill="' + p.bg + '"/>' +
      '<text font-family="Anton" font-size="' + fs + '" letter-spacing="4" fill="' + p.bg + '" text-anchor="middle"><textPath href="#bt" startOffset="50%">' + esc(name) + '</textPath></text>' +
      '<text font-family="Josefin Sans" font-weight="700" font-size="' + ss + '" letter-spacing="6" fill="' + p.bg + '" text-anchor="middle" dominant-baseline="hanging"><textPath href="#bb" startOffset="50%">' + esc(sub) + '</textPath></text>' +
      mid + '<text x="' + cx + '" y="' + (cy + 68) + '" font-family="Josefin Sans" font-weight="700" font-size="22" letter-spacing="5" fill="' + p.ac + '" text-anchor="middle">' + esc(p.since) + '</text>' +
      '<text x="' + (cx - r + 46) + '" y="' + (cy + 8) + '" font-size="26" fill="' + p.bg + '" text-anchor="middle">★</text><text x="' + (cx + r - 46) + '" y="' + (cy + 8) + '" font-size="26" fill="' + p.bg + '" text-anchor="middle">★</text></svg>' +
      one('font:500 24px ' + JT + ';margin:-6px 30px 0', T(p.line)) + one('font:400 58px/1 ' + BE + ';letter-spacing:2px;margin:6px 30px 0', T(p.phone)) + '</div>';
  };
  L.appt = function (p) {
    var h = p.hand || ['', ''], pen = def(p.pen, '#1F3B73');
    return '<div style="' + SQ + 'background:' + p.bg + ';color:' + p.ink + ';padding:40px 44px">' +
      '<div style="display:flex;align-items:center;gap:16px">' + ic(p.icon, p.logo ? 96 : 76, p.ac) + '<div style="min-width:0;flex:1">' +
      one('font:' + def(p.font, '800 40px/1.1 ' + JO) + ';letter-spacing:1px', T(p.name)) + one('font:600 17px ' + JO + ';letter-spacing:7px;margin-top:6px;color:' + p.ac, T(p.sub)) + '</div></div>' +
      one('font:italic 700 46px ' + PL + ';margin-top:34px', T(p.head)) +
      '<div style="display:grid;grid-template-columns:96px 1fr;row-gap:24px;align-items:end;margin-top:22px;font:500 25px ' + JT + '">' +
      '<span>' + T(def(p.l1, 'Date')) + '</span>' + one('border-bottom:2px solid ' + p.ink + ';font:400 42px/1 ' + CA + ';color:' + pen + ';min-width:0', T(h[0]) || '&nbsp;') +
      '<span>' + T(def(p.l2, 'Time')) + '</span>' + one('border-bottom:2px solid ' + p.ink + ';font:400 42px/1 ' + CA + ';color:' + pen + ';min-width:0', T(h[1]) || '&nbsp;') + '</div>' +
      '<div style="position:absolute;left:0;right:0;bottom:0;height:78px;background:' + p.ac + ';color:' + p.bg + ';display:flex;align-items:center;justify-content:space-between;gap:16px;padding:0 44px">' +
      one('font:600 22px ' + JT + ';min-width:0;flex:1', T(p.line)) + one('font:400 44px/1 ' + BE + ';letter-spacing:1px;padding-top:6px;flex:none;max-width:60%', T(p.phone)) + '</div></div>';
  };
  L.qr = function (p) {
    var stars = p.stars ? '<div style="font:400 34px ' + JT + ';letter-spacing:6px;color:' + def(p.star_c, '#E0A526') + ';margin-top:10px">★★★★★</div>' : '';
    return '<div style="' + SQ + 'background:' + p.bg + ';color:' + p.ink + ';padding:40px 40px 0">' +
      '<div style="display:flex;align-items:center;gap:14px">' + ic(p.icon, p.logo ? 80 : 60, p.ac) + one('min-width:0;flex:1;font:' + def(p.font, '400 46px/1.1 ' + DS), T(p.name)) + '</div>' +
      '<div style="display:flex;gap:24px;margin-top:30px;align-items:center"><div style="flex:1;min-width:0"><div style="font:500 28px/1.15 ' + JT + '">' + T(p.line) + '</div>' +
      one('font:400 66px/1 ' + A + ';text-transform:uppercase;margin-top:12px;color:' + p.ac, T(p.head)) + stars + '</div>' +
      '<div style="background:#fff;padding:14px;border-radius:16px;box-shadow:0 0 0 4px ' + p.ac + ';flex:none">' + qr(p.url, 216, def(p.qr_c, '#1B1B1B')) + '</div></div>' +
      '<div style="position:absolute;left:0;right:0;bottom:0;height:70px;border-top:2px solid ' + p.ac + ';display:flex;align-items:center;justify-content:center;gap:20px;padding:0 30px">' +
      one('font:600 24px ' + JT + ';min-width:0', T(p.phone) + (p.phone && p.web ? ' <span style="opacity:.5">·</span> ' : '') + T(p.web)) + '</div></div>';
  };
  L.coupon = function (p) {
    return '<div style="' + SQ + 'background:' + p.bg + ';color:' + p.ink + ';padding:20px">' +
      '<div style="position:absolute;inset:20px;border:4px dashed ' + p.ac + ';border-radius:22px"></div>' +
      '<div style="position:absolute;top:2px;left:60px;background:' + p.bg + ';padding:0 8px"><svg width="38" height="38" viewBox="0 0 64 64">' + ICONS.scissors.split('{c}').join(p.ac) + '</svg></div>' +
      '<div style="text-align:center;padding:0 30px;height:100%;display:flex;flex-direction:column;align-items:center;justify-content:center">' +
      '<div style="background:' + p.ac + ';color:' + p.bg + ';padding:9px 18px 6px;border-radius:999px;max-width:100%">' + one('font:700 19px ' + JO + ';letter-spacing:5px', T(p.kicker)) + '</div>' +
      one('font:400 ' + def(p.os, 150) + 'px/1 ' + A + ';margin-top:14px;max-width:100%;color:' + p.ac, T(p.offer)) +
      one('font:600 30px ' + JT + ';margin-top:8px;max-width:100%', T(p.head)) +
      '<div style="display:flex;align-items:center;gap:14px;margin-top:26px;max-width:100%">' + ic(p.icon, p.logo ? 80 : 58, p.ink) + '<div style="text-align:left;min-width:0">' +
      one('font:400 36px/1.1 ' + DS, T(p.name)) + one('font:600 26px ' + JT + ';margin-top:4px', T(p.phone)) + '</div></div>' +
      '<div style="font:500 18px ' + JT + ';opacity:.75;margin-top:20px">' + T(p.line) + '</div></div></div>';
  };
  L.useful = function (p) {
    var rows = (p.rows || []).map(function (r) {
      return '<div style="display:flex;align-items:flex-end;gap:12px;border-bottom:2px solid ' + p.soft + ';padding:9px 0 7px;font:500 24px ' + JT + '">' +
        '<span style="flex:none;font-weight:700;' + (p.kw ? 'width:' + p.kw + 'px' : '') + '">' + T(r[0]) + '</span>' +
        one('flex:1;min-width:0;text-align:right;font:' + def(p.vf, '400 30px/1.1 ' + CA) + ';color:' + def(p.pen, p.ac), T(r[1]) || '&nbsp;') + '</div>';
    }).join('');
    return '<div style="' + SQ + 'background:' + p.bg + ';color:' + p.ink + '">' +
      '<div style="background:' + p.ac + ';color:' + p.bg + ';padding:24px 36px 18px;display:flex;align-items:center;gap:16px">' + ic(p.icon, 58, p.bg) +
      '<div style="min-width:0;flex:1">' + one('font:400 48px/1.05 ' + A + ';text-transform:uppercase;letter-spacing:1px', T(p.head)) + one('font:600 19px ' + JT + ';margin-top:4px;opacity:.9', T(p.line)) + '</div></div>' +
      '<div style="padding:8px 36px 0">' + rows + '</div>' +
      '<div style="position:absolute;left:0;right:0;bottom:0;height:84px;background:' + p.soft + ';display:flex;align-items:center;justify-content:space-between;gap:16px;padding:0 36px">' +
      one('font:400 32px/1.1 ' + DS + ';min-width:0;flex:1', T(p.name)) + one('font:700 30px ' + JT + ';flex:none;max-width:55%', T(p.phone)) + '</div></div>';
  };
  L.punch = function (p) {
    var n = 10, dots = '';
    for (var i = 0; i < n; i++) dots += '<div style="width:78px;height:78px;border-radius:50%;border:3px solid ' + p.ac + ';' + (i === n - 1 ? 'background:' + p.ac + ';' : '') + 'display:grid;place-items:center;font:700 16px ' + JO + ';color:' + p.bg + '">' + (i === n - 1 ? 'FREE' : '') + '</div>';
    return '<div style="' + SQ + 'background:' + p.bg + ';color:' + p.ink + ';padding:40px 40px 0;text-align:center">' +
      '<div style="display:flex;align-items:center;justify-content:center;gap:14px">' + ic(p.icon, p.logo ? 84 : 66, p.ac) + one('min-width:0;font:' + def(p.font, 'italic 700 52px/1.1 ' + PL), T(p.name)) + '</div>' +
      one('font:700 19px ' + JO + ';letter-spacing:6px;margin-top:10px;color:' + p.ac, T(p.sub)) +
      one('font:400 50px/1.05 ' + A + ';text-transform:uppercase;margin-top:24px', T(p.head)) +
      '<div style="display:grid;grid-template-columns:repeat(5,78px);gap:16px 18px;justify-content:center;margin-top:24px">' + dots + '</div>' +
      one('font:600 24px ' + JT + ';margin-top:24px', T(p.line)) + '</div>';
  };
  L.mono = function (p) {
    var inner = p.logo ? ic(p.icon, 150, p.ac) : one('font:500 ' + def(p.ms, 96) + 'px/1 ' + CI + ';color:' + p.ac + ';max-width:170px', T(p.mono));
    return '<div style="' + SQ + 'background:' + p.bg + ';color:' + p.ink + ';text-align:center;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:0 50px">' +
      '<div style="position:absolute;inset:24px;border:1.5px solid ' + p.ac + '"></div>' +
      '<div style="width:200px;height:200px;border-radius:50%;border:2px solid ' + p.ac + ';display:grid;place-items:center;flex:none">' + inner + '</div>' +
      one('font:600 30px ' + JO + ';letter-spacing:10px;margin-top:26px;max-width:100%', T(p.name)) + one('font:400 32px ' + CO + ';margin-top:8px;opacity:.9;max-width:100%', T(p.sub)) +
      '<div style="width:80px;height:1.5px;background:' + p.ac + ';margin:22px 0 18px"></div>' +
      one('font:500 28px ' + JT + ';letter-spacing:2px;max-width:100%', T(p.phone)) + one('font:500 21px ' + JT + ';letter-spacing:2px;opacity:.75;margin-top:4px;max-width:100%', T(p.web)) + '</div>';
  };
  L.word = function (p) {
    return '<div style="' + SQ + 'background:' + p.bg + ';color:' + p.ink + ';padding:44px 42px">' +
      '<div style="position:absolute;right:-90px;top:-90px;width:330px;height:330px;border-radius:50%;background:' + p.soft + '"></div>' +
      '<div style="position:absolute;left:-60px;bottom:110px;width:160px;height:160px;border-radius:50%;background:' + p.soft + ';opacity:.7"></div>' +
      '<div style="position:relative"><div style="position:absolute;right:0;top:-6px">' + ic(p.icon, 112, p.ac) + '</div>' +
      one('font:700 19px ' + JO + ';letter-spacing:6px;max-width:400px;color:' + p.ac, T(p.sub)) +
      one('font:400 ' + def(p.ws, 128) + 'px/.95 ' + A + ';text-transform:uppercase;margin-top:28px;max-width:' + (p.logo ? 400 : 420) + 'px;color:' + def(p.word_c, p.ink), T(p.head)) +
      '<div style="font:500 28px/1.25 ' + JT + ';margin-top:18px;max-width:470px">' + T(p.line) + '</div></div>' +
      '<div style="position:absolute;left:0;right:0;bottom:0;height:100px;background:' + p.ink + ';color:' + p.bg + ';display:flex;align-items:center;justify-content:space-between;gap:18px;padding:0 42px">' +
      one('min-width:0;flex:1;font:' + def(p.font, '400 38px/1.1 ' + DS), T(p.name)) + one('font:400 52px/1 ' + BE + ';letter-spacing:1px;padding-top:6px;flex:none;max-width:55%;color:' + def(p.ph_c, p.bg), T(p.phone)) + '</div></div>';
  };
  L.photo = function (p) {
    return '<div style="' + SQ + 'background:' + p.bg + ';color:' + p.ink + '"><div style="height:372px;background:' + photo(p) + ' ' + def(p.pos, 'center') + '/cover"></div>' +
      '<div style="position:absolute;top:338px;left:40px;max-width:520px;background:' + p.ac + ';color:' + p.bg + ';padding:12px 18px 9px">' + one('font:700 18px ' + JO + ';letter-spacing:5px', T(p.sub)) + '</div>' +
      (p.logo ? '<div style="position:absolute;top:24px;right:24px;background:#fff;border-radius:14px;padding:8px">' + ic(p.icon, 84, p.ac) + '</div>' : '') +
      '<div style="padding:42px 40px 0">' + one('font:' + def(p.font, '400 50px/1.1 ' + DS), T(p.name)) +
      '<div style="display:flex;justify-content:space-between;align-items:baseline;gap:16px;margin-top:14px">' + one('font:500 25px ' + JT + ';min-width:0;flex:1', T(p.line)) + one('font:700 32px ' + JT + ';flex:none;max-width:60%', T(p.phone)) + '</div></div></div>';
  };
  L.hours = function (p) {
    var rows = (p.rows || []).map(function (r) {
      return '<div style="display:flex;justify-content:space-between;gap:16px;font:500 27px ' + JT + ';padding:8px 0;border-bottom:1.5px dotted ' + p.ac + '"><span style="font-weight:700;white-space:nowrap">' + T(r[0]) + '</span>' + one('min-width:0;text-align:right', T(r[1])) + '</div>';
    }).join('');
    return '<div style="' + SQ + 'background:' + p.bg + ';color:' + p.ink + ';padding:38px 50px 0">' +
      '<div style="display:flex;align-items:center;justify-content:center;gap:16px">' + ic(p.icon, p.logo ? 90 : 74, p.ac) + one('min-width:0;font:' + def(p.font, 'italic 700 54px/1.1 ' + PL), T(p.name)) + '</div>' +
      one('text-align:center;font:700 19px ' + JO + ';letter-spacing:6px;margin-top:10px;color:' + p.ac, T(p.sub)) +
      one('font:400 40px/1.05 ' + A + ';text-transform:uppercase;text-align:center;margin-top:20px', T(p.head)) + '<div style="margin-top:8px">' + rows + '</div>' +
      '<div style="position:absolute;left:0;right:0;bottom:0;height:80px;background:' + p.ac + ';color:' + p.bg + ';display:flex;align-items:center;justify-content:center;gap:22px;padding:0 30px">' +
      one('font:400 48px/1 ' + BE + ';letter-spacing:1px;padding-top:6px;flex:none;max-width:60%', T(p.phone)) + one('font:600 22px ' + JT + ';min-width:0', T(p.line)) + '</div></div>';
  };
  L.thanks = function (p) {
    return '<div style="' + SQ + 'background:' + p.bg + ';color:' + p.ink + ';text-align:center;padding:56px 40px 0;display:flex;flex-direction:column;align-items:center">' +
      ic(p.icon, p.logo ? 110 : 92, p.ac) +
      one('font:' + def(p.font, '400 92px/1.1 ' + DA) + ';margin-top:12px;max-width:100%;color:' + def(p.head_c, p.ink), T(p.head)) +
      '<div style="font:500 27px/1.3 ' + JT + ';margin-top:14px;max-width:470px">' + T(p.line) + '</div>' +
      '<div style="position:absolute;left:0;right:0;bottom:0;height:120px;background:' + p.ac + ';color:' + def(p.bar_ink, p.bg) + ';display:flex;flex-direction:column;align-items:center;justify-content:center;padding:0 30px">' +
      one('font:400 40px/1.1 ' + DS + ';max-width:100%', T(p.name)) + one('font:600 24px ' + JT + ';margin-top:6px;letter-spacing:1px;max-width:100%', T(p.phone)) + '</div></div>';
  };
  /* events */
  L.names = function (p) {
    return '<div style="' + SQ + 'background:' + p.bg + ';color:' + p.ink + ';text-align:center">' +
      '<div style="position:absolute;left:84px;right:84px;top:44px;bottom:44px;border:2px solid ' + p.ac + ';border-radius:216px 216px 0 0"></div>' +
      '<div style="position:absolute;left:96px;right:96px;top:56px;bottom:56px;border:1px solid ' + p.ac + ';border-radius:204px 204px 0 0"></div>' +
      '<div style="position:relative;padding:150px 120px 0">' + one('font:600 17px ' + JO + ';letter-spacing:6px;color:' + p.ac, T(p.sub)) +
      '<div style="font:' + def(p.font, '400 84px/1.05 ' + DA) + ';margin-top:22px">' + one('', T(p.a)) + '<div style="font:400 46px ' + CO + ';color:' + p.ac + '">&amp;</div>' + one('', T(p.b)) + '</div>' +
      one('font:500 26px ' + CI + ';letter-spacing:6px;margin-top:22px', T(p.date)) + one('font:400 28px ' + CO + ';margin-top:6px;opacity:.85', T(p.place)) + '</div></div>';
  };
  L.botanical = function (p) {
    function leaf(r, x, y) {
      var g = '';
      for (var i = 1; i < 7; i++) { var s = i % 2 ? -1 : 1; g += '<ellipse cx="' + i * 26 + '" cy="' + s * 14 + '" rx="20" ry="9" transform="rotate(' + s * 30 + ' ' + i * 26 + ' ' + s * 14 + ')" fill="' + p.ac + '" opacity=".85"/>'; }
      return '<g transform="translate(' + x + ' ' + y + ') rotate(' + r + ')">' + g + '<path d="M0 0 L170 0" stroke="' + p.ac + '" stroke-width="3"/></g>';
    }
    return '<div style="' + SQ + 'background:' + p.bg + ';color:' + p.ink + ';text-align:center">' +
      '<svg width="600" height="600" style="position:absolute;inset:0">' + leaf(35, 10, 30) + leaf(215, 590, 570) + leaf(145, 590, 30) + leaf(-35, 10, 570) + '</svg>' +
      '<div style="position:relative;padding:150px 70px 0">' + one('font:600 17px ' + JO + ';letter-spacing:6px;color:' + p.ac, T(p.sub)) +
      one('font:' + def(p.font, '400 76px/1.1 ' + DS) + ';margin-top:22px', T(p.a) + ' <span style="font:400 64px ' + CO + ';color:' + p.ac + '">&amp;</span> ' + T(p.b)) +
      one('font:500 30px ' + CI + ';letter-spacing:6px;margin-top:26px', T(p.date)) + one('font:400 30px ' + CO + ';margin-top:8px;opacity:.85', T(p.place)) + '</div></div>';
  };
  L.bigdate = function (p) {
    var d = String(p.date || '').split(/[.\/·-]/).map(function (x) { return x.trim(); }).filter(Boolean);
    var bar = '<span style="width:4px;height:120px;background:' + p.ac + ';flex:none"></span>';
    return '<div style="' + SQ + 'background:' + p.bg + ';color:' + p.ink + ';text-align:center;padding:44px 40px 0">' +
      one('font:' + def(p.font, '400 64px/1.1 ' + DA) + ';color:' + p.ac, T(p.sub)) +
      '<div data-fit style="display:flex;justify-content:center;align-items:center;gap:16px;margin-top:20px;font:400 150px/1 ' + BE + ';white-space:nowrap">' + d.map(function (x) { return '<span>' + esc(x) + '</span>'; }).join(bar) + '</div>' +
      one('font:600 32px ' + JO + ';letter-spacing:9px;margin-top:20px', T(String(p.a || '').toUpperCase()) + ' &amp; ' + T(String(p.b || '').toUpperCase())) +
      one('font:400 30px ' + CO + ';margin-top:10px;opacity:.85', T(p.place)) + one('font:500 20px ' + JT + ';letter-spacing:3px;margin-top:22px;color:' + p.ac, T(p.line)) + '</div>';
  };
  L.wphoto = function (p) {
    return '<div style="' + SQ + 'background:' + photo(p) + ' ' + def(p.pos, 'center') + '/cover;color:' + p.ink + '">' +
      '<div style="position:absolute;left:0;right:0;bottom:0;padding:70px 30px 26px;background:linear-gradient(transparent,' + def(p.shade, 'rgba(0,0,0,.78)') + ' 45%);text-align:center;color:' + def(p.txt, '#fff') + '">' +
      one('font:' + def(p.font, '400 72px/1.1 ' + DA), T(p.head)) + one('font:600 24px ' + JO + ';letter-spacing:7px;margin-top:10px', T(p.line)) + '</div></div>';
  };
  L.polaroid = function (p) {
    return '<div style="' + SQ + 'background:' + p.bg + ';color:' + p.ink + '">' +
      '<div style="position:absolute;left:66px;top:34px;width:430px;background:#fff;padding:20px 20px 0;transform:rotate(-4deg);box-shadow:0 14px 30px rgba(0,0,0,.25)">' +
      '<div style="height:350px;background:' + photo(p) + ' ' + def(p.pos, 'center') + '/cover"></div>' + one('font:400 44px/1.1 ' + CA + ';color:#2B2118;text-align:center;padding:14px 0 16px', T(p.head)) + '</div>' +
      '<div style="position:absolute;right:34px;bottom:30px;text-align:right;max-width:330px">' + one('font:400 64px/1 ' + BE + ';letter-spacing:2px;color:' + p.ac, T(p.date)) + one('font:600 18px ' + JO + ';letter-spacing:5px', T(p.line)) + '</div></div>';
  };
  L.year = function (p) {
    return '<div style="' + SQ + 'background:' + p.bg + ';color:' + p.ink + ';text-align:center;padding:40px 40px 0">' +
      '<div style="display:flex;justify-content:center">' + ic(def(p.icon, 'cap'), 104, p.ac) + '</div>' + one('font:700 22px ' + JO + ';letter-spacing:9px;margin-top:8px', T(p.sub)) +
      one('font:400 210px/.95 ' + A + ';color:' + p.ac + ';margin-top:8px;letter-spacing:4px', T(p.year)) +
      one('font:' + def(p.font, '400 66px/1.1 ' + DA) + ';margin-top:10px', T(p.head)) + one('font:600 22px ' + JT + ';letter-spacing:3px;margin-top:10px;opacity:.85', T(p.line)) + '</div>';
  };
  L.pennant = function (p) {
    var s = String(p.school || '').toUpperCase(), fs = Math.min(def(p.ps, 66), Math.floor(760 / Math.max(1, s.length)) + 8);
    return '<div style="' + SQ + 'background:' + p.bg + ';color:' + p.ink + ';padding-top:62px">' +
      '<svg width="600" height="250" viewBox="0 0 600 250"><path d="M40 20 L570 125 L40 230 Z" fill="' + p.ac + '"/><rect x="24" y="8" width="18" height="242" rx="9" fill="' + p.ink + '"/>' +
      '<text x="230" y="' + (125 + fs * .36) + '" font-family="Anton" font-size="' + fs + '" letter-spacing="3" fill="' + p.bg + '" text-anchor="middle">' + esc(s) + '</text></svg>' +
      '<div style="text-align:center;margin-top:24px;padding:0 40px">' + one('font:' + def(p.font, '400 62px/1.1 ' + DA), T(p.head)) +
      one('font:700 24px ' + JO + ';letter-spacing:7px;margin-top:14px;color:' + p.ac, T(p.line)) + one('font:500 24px ' + JT + ';margin-top:8px', T(p.sub)) + '</div></div>';
  };
  L.party = function (p) {
    var seed = 0; String(p.slug || 'x').split('').forEach(function (ch) { seed = (seed * 31 + ch.charCodeAt(0)) % 2147483647; });
    function rnd(a, b) { seed = (seed * 48271) % 2147483647; return a + Math.floor((seed / 2147483647) * (b - a + 1)); }
    var cols = p.conf || [p.ac, p.ink, p.soft], conf = '';
    for (var i = 0; i < 46; i++) {
      var x = rnd(0, 590), y = rnd(0, 1) ? rnd(0, 120) : rnd(470, 590);
      conf += '<rect x="' + x + '" y="' + y + '" width="' + rnd(8, 16) + '" height="' + rnd(14, 26) + '" rx="3" fill="' + cols[rnd(0, cols.length - 1)] + '" transform="rotate(' + rnd(-60, 60) + ' ' + x + ' ' + y + ')"/>';
    }
    return '<div style="' + SQ + 'background:' + p.bg + ';color:' + p.ink + ';text-align:center"><svg width="600" height="600" style="position:absolute;inset:0">' + conf + '</svg>' +
      '<div style="position:relative;padding:' + (p.logo ? 116 : 142) + 'px 40px 0;display:flex;flex-direction:column;align-items:center">' + (p.logo ? ic(p.icon, 90, p.ac) : '') +
      one('font:700 21px ' + JO + ';letter-spacing:8px;max-width:100%;color:' + p.ac, T(p.sub)) +
      one('font:' + def(p.font, '400 104px/1 ' + A) + ';text-transform:' + def(p.tt, 'uppercase') + ';margin-top:14px;max-width:100%', T(p.head)) +
      '<div style="font:500 28px ' + JT + ';margin-top:18px">' + T(p.line) + '</div>' + one('font:600 22px ' + JO + ';letter-spacing:5px;margin-top:10px;max-width:100%;color:' + p.ac, T(p.date)) + '</div></div>';
  };
  L.eqr = function (p) {
    return '<div style="' + SQ + 'background:' + p.bg + ';color:' + p.ink + ';text-align:center;padding:36px 40px 0;display:flex;flex-direction:column;align-items:center">' +
      (p.logo ? ic(p.icon, 70, p.ac) : '') + one('font:' + def(p.font, '400 62px/1.1 ' + DA) + ';max-width:100%', T(p.head)) +
      one('font:700 20px ' + JO + ';letter-spacing:7px;margin-top:10px;max-width:100%;color:' + p.ac, T(p.sub)) +
      '<div style="background:#fff;padding:14px;border-radius:14px;margin-top:22px;box-shadow:0 0 0 3px ' + p.ac + '">' + qr(p.url, p.logo ? 190 : 220, def(p.qr_c, '#1B1B1B')) + '</div>' +
      one('font:400 50px/1.05 ' + A + ';text-transform:uppercase;margin-top:20px;max-width:100%;color:' + p.ac, T(p.line)) + '</div>';
  };

  /* ---------------------------------------------------------------- colors */
  function hex(c) { c = String(c || '').trim(); return /^#[0-9a-f]{6}$/i.test(c) ? c.toUpperCase() : null; }
  function mix(a, b, t) {
    a = hex(a); b = hex(b); if (!a || !b) return a || b || '#888888';
    var r = [1, 3, 5].map(function (i) { return Math.round(parseInt(a.substr(i, 2), 16) * (1 - t) + parseInt(b.substr(i, 2), 16) * t); });
    return '#' + r.map(function (x) { return ('0' + x.toString(16)).slice(-2); }).join('').toUpperCase();
  }
  /* the design's own colors, or the customer's: {bg, ink, ac} (soft is worked out) */
  function colorsOf(d, ch) {
    if (ch && ch.colors && hex(ch.colors.bg) && hex(ch.colors.ink) && hex(ch.colors.ac)) {
      var c = ch.colors;
      return { bg: hex(c.bg), ink: hex(c.ink), ac: hex(c.ac), soft: mix(c.bg, c.ac, .2), own: true };
    }
    return { bg: d.colors.bg, ink: d.colors.ink, ac: d.colors.ac, soft: d.colors.soft || mix(d.colors.bg, d.colors.ac, .2), own: false };
  }

  /* the words: the design's own unless the customer changed them */
  function words(d, ch) {
    var t = {}, k;
    for (k in d.text) t[k] = d.text[k];
    if (ch && ch.text) for (k in ch.text) if (k in d.text) t[k] = ch.text[k];
    return t;
  }

  /* design (from LHHDesigns) + choices {colors, text, icon, logo, photo, url} -> html of the 600 x 600 magnet */
  function render(d, ch) {
    ch = ch || {};
    var c = colorsOf(d, ch), t = words(d, ch), p = {}, k;
    for (k in d.opt) p[k] = d.opt[k];
    if (!c.own) for (k in d.tweak) p[k] = d.tweak[k];   /* the little color touches of the original */
    for (k in t) p[k] = t[k];
    p.bg = c.bg; p.ink = c.ink; p.ac = c.ac; p.soft = c.soft; p.slug = d.slug;
    p.icon = ch.icon && ICONS[ch.icon] ? ch.icon : d.opt.icon;
    p.logo = ch.logo || '';
    p.photo = ch.photo || (d.opt.photoUrl ? (window.LHHDesignBase || '') + d.opt.photoUrl : '');
    p.url = ch.url || d.opt.url || 'https://littlehivehouse.com/';
    if (d.opt.items) p.items = d.opt.items.map(function (x, i) { return 'items' + i in t ? t['items' + i] : x; });
    if (d.opt.rows) p.rows = d.opt.rows.map(function (r, i) { return [('rows' + i + 'a') in t ? t['rows' + i + 'a'] : r[0], ('rows' + i + 'b') in t ? t['rows' + i + 'b'] : r[1]]; });
    if (d.opt.hand) p.hand = [t.hand0 != null ? t.hand0 : d.opt.hand[0], t.hand1 != null ? t.hand1 : d.opt.hand[1]];
    cur = p;
    var html = (L[d.layout] || L.thanks)(p);
    cur = null;
    return html;
  }

  /* shrink every one-line text that runs past its box (call when the magnet is in the page at its real size) */
  function fit(root) {
    root.querySelectorAll('[data-fit]').forEach(function (el) {
      /* the size the design asked for, kept the first time (clearing the inline size would undo the font shorthand) */
      if (!el.getAttribute('data-fs')) el.setAttribute('data-fs', parseFloat(getComputedStyle(el).fontSize));
      var fs = parseFloat(el.getAttribute('data-fs')), n = 0;
      el.style.fontSize = fs + 'px';
      while (el.scrollWidth > el.clientWidth + 1 && fs > 8 && n++ < 40) { fs *= .93; el.style.fontSize = fs + 'px'; }
    });
  }

  /* draws a design into a box of any width: the magnet is laid out at 600 px and scaled */
  function paint(box, d, ch) {
    var w = box.getBoundingClientRect().width || box.clientWidth || 300;
    box.setAttribute('translate', 'no');   /* the customer's own words are never translated */
    box.innerHTML = '<div class="dz-mag" style="width:600px;height:600px;transform:scale(' + (w / 600) + ');transform-origin:0 0">' + render(d, ch) + '</div>';
    box.style.height = w + 'px';
    var m = box.firstChild;
    fit(m);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { fit(m); });
  }

  var byslug = {};
  DATA.list.forEach(function (d) { byslug[d.slug] = d; });

  window.LHHDesigner = { stock: DATA.stock || [], render: render, fit: fit, paint: paint, icons: ICONS, palettes: DATA.pal, designs: DATA.list, get: function (s) { return byslug[s]; }, esc: esc };
})();
