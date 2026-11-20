/* Little Hive House: a small QR code maker (byte mode, error correction level M, versions 1 to 10: links up to 213
   characters). Used on the business page to show a customer's own link as a QR magnet before they buy, and in the
   admin. window.LHHQR(text) -> {size, dark(x, y)} | null when the text is too long; LHHQR.svg(text, px, fg, bg) -> svg string.
   Checked against a real QR reader (OpenCV) in tools/test_qr.py. */
(function () {
  // [ec codewords per block, [[blocks, data codewords per block], ...]] for level M
  var BLOCKS = [null, [10, [[1, 16]]], [16, [[1, 28]]], [26, [[1, 44]]], [18, [[2, 32]]], [24, [[2, 43]]], [16, [[4, 27]]],
    [18, [[4, 31]]], [22, [[2, 38], [2, 39]]], [22, [[3, 36], [2, 37]]], [26, [[4, 43], [1, 44]]]];
  var ALIGN = [null, [], [6, 18], [6, 22], [6, 26], [6, 30], [6, 34], [6, 22, 38], [6, 24, 42], [6, 26, 46], [6, 28, 50]];
  var EXP = [], LOG = [];
  (function () { var x = 1; for (var i = 0; i < 255; i++) { EXP[i] = x; LOG[x] = i; x <<= 1; if (x & 256) x ^= 0x11d; } for (i = 255; i < 512; i++) EXP[i] = EXP[i - 255]; })();
  function mul(a, b) { return a && b ? EXP[LOG[a] + LOG[b]] : 0; }
  function generator(n) {
    var g = [1];
    for (var i = 0; i < n; i++) {
      var next = new Array(g.length + 1).fill(0);
      for (var j = 0; j < g.length; j++) { next[j] ^= g[j]; next[j + 1] ^= mul(g[j], EXP[i]); }
      g = next;
    }
    return g;
  }
  function ecc(data, n) {
    var g = generator(n), r = data.concat(new Array(n).fill(0));
    for (var i = 0; i < data.length; i++) {
      var c = r[i]; if (!c) continue;
      for (var j = 0; j < g.length; j++) r[i + j] ^= mul(g[j], c);
    }
    return r.slice(data.length);
  }
  function utf8(s) {
    var out = [];
    for (var i = 0; i < s.length; i++) {
      var c = s.charCodeAt(i);
      if (c >= 0xd800 && c < 0xdc00 && i + 1 < s.length) { c = 0x10000 + ((c - 0xd800) << 10) + (s.charCodeAt(++i) - 0xdc00); }
      if (c < 0x80) out.push(c);
      else if (c < 0x800) out.push(0xc0 | c >> 6, 0x80 | c & 63);
      else if (c < 0x10000) out.push(0xe0 | c >> 12, 0x80 | c >> 6 & 63, 0x80 | c & 63);
      else out.push(0xf0 | c >> 18, 0x80 | c >> 12 & 63, 0x80 | c >> 6 & 63, 0x80 | c & 63);
    }
    return out;
  }
  function dataCount(v) { var b = BLOCKS[v][1], n = 0; b.forEach(function (x) { n += x[0] * x[1]; }); return n; }

  function encode(text) {
    var bytes = utf8(String(text || ''));
    var v = 1;
    for (; v <= 10; v++) { if (4 + (v < 10 ? 8 : 16) + bytes.length * 8 <= dataCount(v) * 8) break; }
    if (v > 10) return null;
    // the bit stream: mode, length, bytes, terminator, padding
    var bits = [];
    function put(val, len) { for (var i = len - 1; i >= 0; i--) bits.push(val >> i & 1); }
    put(4, 4); put(bytes.length, v < 10 ? 8 : 16); bytes.forEach(function (b) { put(b, 8); });
    var cap = dataCount(v) * 8;
    put(0, Math.min(4, cap - bits.length));
    while (bits.length % 8) bits.push(0);
    var words = [];
    for (var i = 0; i < bits.length; i += 8) { var w = 0; for (var j = 0; j < 8; j++) w = w << 1 | bits[i + j]; words.push(w); }
    for (var p = 0; words.length < dataCount(v); p++) words.push(p % 2 ? 0x11 : 0xec);
    // blocks with their error correction, interleaved
    var ecn = BLOCKS[v][0], blocks = [], k = 0;
    BLOCKS[v][1].forEach(function (g) { for (var b = 0; b < g[0]; b++) { var d = words.slice(k, k + g[1]); k += g[1]; blocks.push({ d: d, e: ecc(d, ecn) }); } });
    var all = [], maxD = Math.max.apply(null, blocks.map(function (b) { return b.d.length; }));
    for (i = 0; i < maxD; i++) blocks.forEach(function (b) { if (i < b.d.length) all.push(b.d[i]); });
    for (i = 0; i < ecn; i++) blocks.forEach(function (b) { all.push(b.e[i]); });

    var size = v * 4 + 17, m = [], fn = [];
    for (i = 0; i < size; i++) { m.push(new Array(size).fill(0)); fn.push(new Array(size).fill(false)); }
    function set(x, y, d) { m[y][x] = d ? 1 : 0; fn[y][x] = true; }
    function finder(cx, cy) {
      for (var dy = -4; dy <= 4; dy++) for (var dx = -4; dx <= 4; dx++) {
        var x = cx + dx, y = cy + dy; if (x < 0 || y < 0 || x >= size || y >= size) continue;
        var d = Math.max(Math.abs(dx), Math.abs(dy));
        set(x, y, d !== 2 && d !== 4);
      }
    }
    finder(3, 3); finder(size - 4, 3); finder(3, size - 4);
    for (i = 0; i < size; i++) { if (!fn[6][i]) set(i, 6, i % 2 === 0); if (!fn[i][6]) set(6, i, i % 2 === 0); }
    var al = ALIGN[v];
    al.forEach(function (ay) { al.forEach(function (ax) {
      if ((ax === 6 && ay === 6) || (ax === 6 && ay === size - 7) || (ax === size - 7 && ay === 6)) return;
      for (var dy = -2; dy <= 2; dy++) for (var dx = -2; dx <= 2; dx++) set(ax + dx, ay + dy, Math.max(Math.abs(dx), Math.abs(dy)) !== 1);
    }); });
    // reserve the format areas (and version areas from 7), and the dark module
    for (i = 0; i < 9; i++) { if (!fn[8][i]) set(i, 8, 0); if (!fn[i][8]) set(8, i, 0); }
    for (i = 0; i < 8; i++) { set(size - 1 - i, 8, 0); set(8, size - 1 - i, 0); }
    set(8, size - 8, 1);
    if (v >= 7) {
      var rem = v; for (i = 0; i < 12; i++) rem = rem << 1 ^ (rem >> 11) * 0x1f25;
      var vb = v << 12 | rem;
      for (i = 0; i < 18; i++) { var bit = vb >> i & 1, a = size - 11 + i % 3, b2 = Math.floor(i / 3); set(a, b2, bit); set(b2, a, bit); }
    }
    // the data, in the zigzag
    var idx = 0;
    for (var right = size - 1; right >= 1; right -= 2) {
      if (right === 6) right = 5;
      for (var vert = 0; vert < size; vert++) for (j = 0; j < 2; j++) {
        var x = right - j, up = ((right + 1) & 2) === 0, y = up ? size - 1 - vert : vert;
        if (!fn[y][x] && idx < all.length * 8) { m[y][x] = all[idx >> 3] >> (7 - (idx & 7)) & 1; idx++; }
      }
    }
    function maskBit(mk, x, y) {
      switch (mk) {
        case 0: return (x + y) % 2 === 0; case 1: return y % 2 === 0; case 2: return x % 3 === 0; case 3: return (x + y) % 3 === 0;
        case 4: return (Math.floor(x / 3) + Math.floor(y / 2)) % 2 === 0; case 5: return x * y % 2 + x * y % 3 === 0;
        case 6: return (x * y % 2 + x * y % 3) % 2 === 0; default: return ((x + y) % 2 + x * y % 3) % 2 === 0;
      }
    }
    function format(mk, g) {
      var data = 0 << 3 | mk, rem = data;           // level M = 00
      for (var i = 0; i < 10; i++) rem = rem << 1 ^ (rem >> 9) * 0x537;
      var bits = (data << 10 | rem) ^ 0x5412;
      for (i = 0; i <= 5; i++) g[i][8] = bits >> i & 1;
      g[7][8] = bits >> 6 & 1; g[8][8] = bits >> 7 & 1; g[8][7] = bits >> 8 & 1;
      for (i = 9; i < 15; i++) g[8][14 - i] = bits >> i & 1;
      for (i = 0; i < 8; i++) g[8][size - 1 - i] = bits >> i & 1;
      for (i = 8; i < 15; i++) g[size - 15 + i][8] = bits >> i & 1;
      g[size - 8][8] = 1;
    }
    function penalty(g) {
      var s = 0, x, y, run, c;
      for (var pass = 0; pass < 2; pass++) for (y = 0; y < size; y++) {
        run = 1;
        for (x = 1; x <= size; x++) {
          var a = x < size ? (pass ? g[x][y] : g[y][x]) : -1, b = pass ? g[x - 1][y] : g[y][x - 1];
          if (a === b) run++; else { if (run >= 5) s += run - 2; run = 1; }
        }
      }
      for (y = 0; y < size - 1; y++) for (x = 0; x < size - 1; x++) { c = g[y][x]; if (c === g[y][x + 1] && c === g[y + 1][x] && c === g[y + 1][x + 1]) s += 3; }
      var pat = [1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0], pat2 = [0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1];
      for (y = 0; y < size; y++) for (x = 0; x <= size - 11; x++) {
        var h1 = true, h2 = true, v1 = true, v2 = true;
        for (var t = 0; t < 11; t++) {
          if (g[y][x + t] !== pat[t]) h1 = false; if (g[y][x + t] !== pat2[t]) h2 = false;
          if (g[x + t][y] !== pat[t]) v1 = false; if (g[x + t][y] !== pat2[t]) v2 = false;
        }
        s += 40 * (h1 + h2 + v1 + v2);
      }
      var dark = 0; for (y = 0; y < size; y++) for (x = 0; x < size; x++) dark += g[y][x];
      s += Math.floor(Math.abs(dark * 20 - size * size * 10) / (size * size)) * 10;
      return s;
    }
    var best = null, bestScore = Infinity;
    for (var mk = 0; mk < 8; mk++) {
      var g = m.map(function (row, y) { return row.map(function (c, x) { return fn[y][x] ? c : c ^ (maskBit(mk, x, y) ? 1 : 0); }); });
      format(mk, g);
      var sc = penalty(g);
      if (sc < bestScore) { bestScore = sc; best = g; }
    }
    return { size: size, version: v, dark: function (x, y) { return best[y][x] === 1; }, grid: best };
  }

  function svg(text, px, fg, bg) {
    var q = encode(text); if (!q) return '';
    var n = q.size + 8, p = '';
    for (var y = 0; y < q.size; y++) for (var x = 0; x < q.size; x++) if (q.dark(x, y)) p += 'M' + (x + 4) + ' ' + (y + 4) + 'h1v1h-1z';
    return '<svg xmlns="http://www.w3.org/2000/svg" width="' + (px || 200) + '" height="' + (px || 200) + '" viewBox="0 0 ' + n + ' ' + n + '" shape-rendering="crispEdges">' +
      '<rect width="' + n + '" height="' + n + '" fill="' + (bg || '#fff') + '"/><path d="' + p + '" fill="' + (fg || '#000') + '"/></svg>';
  }
  var api = function (t) { return encode(t); };
  api.svg = svg;
  if (typeof window !== 'undefined') window.LHHQR = api;
  if (typeof module !== 'undefined') module.exports = api;
})();
