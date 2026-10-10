/* Run: node --test admin/tests/ */
'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const Z = require('../zip.js');

test('crc32 of "hello"', () => {
  assert.equal(Z.crc32(Buffer.from('hello')), 0x3610a686);
});

test('zip layout: local headers, central directory and end record', () => {
  const out = Z.zip([{ name: 'a.txt', data: 'hello' }, { name: 'dir/b.json', data: '{"x":1}' }]);
  const v = new DataView(out.buffer);
  assert.equal(v.getUint32(0, true), 0x04034b50);
  const end = out.length - 22;
  assert.equal(v.getUint32(end, true), 0x06054b50);
  assert.equal(v.getUint16(end + 10, true), 2);
  const cd = v.getUint32(end + 16, true);
  assert.equal(v.getUint32(cd, true), 0x02014b50);
  assert.equal(Buffer.from(out.slice(30, 35)).toString(), 'a.txt');
  assert.equal(Buffer.from(out.slice(35, 40)).toString(), 'hello');
});
