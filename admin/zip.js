/* A tiny ZIP writer (files stored as-is, no compression: photos are already compressed).
   zip([{name: "LHH-1042/01.jpg", data: Uint8Array, date: Date}]) -> Uint8Array. Pure, tested in admin/tests/. */
(function (root, factory) {
  var api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.LHHZip = api;
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';
  var TABLE = null;
  function crc32(u8) {
    if (!TABLE) {
      TABLE = new Uint32Array(256);
      for (var n = 0; n < 256; n++) {
        var c = n;
        for (var k = 0; k < 8; k++) c = c & 1 ? 0xEDB88320 ^ (c >>> 1) : c >>> 1;
        TABLE[n] = c >>> 0;
      }
    }
    var crc = 0xFFFFFFFF;
    for (var i = 0; i < u8.length; i++) crc = TABLE[(crc ^ u8[i]) & 0xFF] ^ (crc >>> 8);
    return (crc ^ 0xFFFFFFFF) >>> 0;
  }
  function utf8(s) {
    if (typeof TextEncoder !== 'undefined') return new TextEncoder().encode(s);
    return Uint8Array.from(Buffer.from(s, 'utf8'));
  }
  function dosTime(d) {
    return { time: (d.getHours() << 11) | (d.getMinutes() << 5) | (d.getSeconds() >> 1),
             date: ((Math.max(1980, d.getFullYear()) - 1980) << 9) | ((d.getMonth() + 1) << 5) | d.getDate() };
  }
  function zip(files) {
    var parts = [], central = [], offset = 0;
    files.forEach(function (f) {
      var name = utf8(f.name), data = typeof f.data === 'string' ? utf8(f.data) : new Uint8Array(f.data);
      var crc = crc32(data), t = dosTime(f.date || new Date());
      var h = new DataView(new ArrayBuffer(30));
      h.setUint32(0, 0x04034b50, true); h.setUint16(4, 20, true); h.setUint16(6, 0x0800, true); h.setUint16(8, 0, true);
      h.setUint16(10, t.time, true); h.setUint16(12, t.date, true); h.setUint32(14, crc, true);
      h.setUint32(18, data.length, true); h.setUint32(22, data.length, true); h.setUint16(26, name.length, true); h.setUint16(28, 0, true);
      var c = new DataView(new ArrayBuffer(46));
      c.setUint32(0, 0x02014b50, true); c.setUint16(4, 20, true); c.setUint16(6, 20, true); c.setUint16(8, 0x0800, true); c.setUint16(10, 0, true);
      c.setUint16(12, t.time, true); c.setUint16(14, t.date, true); c.setUint32(16, crc, true);
      c.setUint32(20, data.length, true); c.setUint32(24, data.length, true); c.setUint16(28, name.length, true);
      c.setUint32(42, offset, true);
      parts.push(new Uint8Array(h.buffer), name, data);
      central.push(new Uint8Array(c.buffer), name);
      offset += 30 + name.length + data.length;
    });
    var cdSize = central.reduce(function (a, p) { return a + p.length; }, 0);
    var e = new DataView(new ArrayBuffer(22));
    e.setUint32(0, 0x06054b50, true); e.setUint16(8, files.length, true); e.setUint16(10, files.length, true);
    e.setUint32(12, cdSize, true); e.setUint32(16, offset, true);
    var all = parts.concat(central, [new Uint8Array(e.buffer)]);
    var out = new Uint8Array(offset + cdSize + 22), pos = 0;
    all.forEach(function (p) { out.set(p, pos); pos += p.length; });
    return out;
  }
  return { zip: zip, crc32: crc32 };
});
