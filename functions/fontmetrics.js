"use strict";
/* Real font metrics for the caption text on photo magnets, without any npm package: a tiny TrueType reader
   (head, hhea, hmtx, cmap) over the static fonts in ./fonts. `captionSvg` is a port of tools/frames.py caption_svg,
   so the Cloud Function fits a caption to its frame exactly like the manual print tool and the shop's builder.

   Fonts (static instances of the variable fonts in tools/fonts, made with fontTools): the frame captions use
   serif (Playfair Display Bold Italic), dms (DM Serif Display), jos (Josefin Sans Bold), bebas (Bebas Neue),
   cinzel (Cinzel SemiBold), jost (Jost Medium) and mono (DM Mono Medium, also used inside the film frame). */

const fs = require("fs");
const path = require("path");

const FONTS_DIR = path.join(__dirname, "fonts");

/* key -> {file, attrs (the SVG attributes the builder/print tool emit), family, style, weight} */
const FONTS = {
  serif: { file: "PlayfairDisplay-BoldItalic.ttf", attrs: "font-family=\"'Playfair Display', Georgia, serif\" font-style=\"italic\" font-weight=\"700\"", family: "Playfair Display", style: "italic", weight: 700 },
  dms: { file: "DMSerifDisplay-Regular.ttf", attrs: "font-family=\"'DM Serif Display', Georgia, serif\"", family: "DM Serif Display", style: "normal", weight: 400 },
  cinzel: { file: "Cinzel-SemiBold.ttf", attrs: "font-family=\"Cinzel, 'Times New Roman', serif\" font-weight=\"600\"", family: "Cinzel", style: "normal", weight: 600 },
  jos: { file: "JosefinSans-Bold.ttf", attrs: "font-family=\"'Josefin Sans', sans-serif\" font-weight=\"700\"", family: "Josefin Sans", style: "normal", weight: 700 },
  bebas: { file: "BebasNeue-Regular.ttf", attrs: "font-family=\"'Bebas Neue', Impact, sans-serif\"", family: "Bebas Neue", style: "normal", weight: 400 },
  jost: { file: "Jost-Medium.ttf", attrs: "font-family=\"Jost, sans-serif\" font-weight=\"500\"", family: "Jost", style: "normal", weight: 500 },
  mono: { file: "DMMono-Medium.ttf", attrs: "font-family=\"'DM Mono', ui-monospace, monospace\" font-weight=\"500\"", family: "DM Mono", style: "normal", weight: 500 },
  // caption styles (tools/frames_v2.py): handwritten, script, classic
  caveat: { file: "Caveat-SemiBold.ttf", attrs: "font-family=\"Caveat, cursive\" font-weight=\"600\"", family: "Caveat", style: "normal", weight: 600 },
  dancing: { file: "DancingScript-SemiBold.ttf", attrs: "font-family=\"'Dancing Script', cursive\" font-weight=\"600\"", family: "Dancing Script", style: "normal", weight: 600 },
  cormorant: { file: "CormorantGaramond-SemiBoldItalic.ttf", attrs: "font-family=\"'Cormorant Garamond', Georgia, serif\" font-style=\"italic\" font-weight=\"600\"", family: "Cormorant Garamond", style: "italic", weight: 600 },
};

function fontFile(key) { return path.join(FONTS_DIR, (FONTS[key] || FONTS.jost).file); }

/* ---------- TrueType reader: just enough for advance widths ---------- */
function tables(buf) {
  const n = buf.readUInt16BE(4);
  const out = {};
  for (let i = 0; i < n; i++) {
    const o = 12 + i * 16;
    out[buf.toString("latin1", o, o + 4)] = { offset: buf.readUInt32BE(o + 8), length: buf.readUInt32BE(o + 12) };
  }
  return out;
}

function readCmap(buf, t) {
  const base = t.offset;
  const n = buf.readUInt16BE(base + 2);
  let best = null;
  for (let i = 0; i < n; i++) {
    const o = base + 4 + i * 8;
    const platform = buf.readUInt16BE(o), encoding = buf.readUInt16BE(o + 2), off = buf.readUInt32BE(o + 4);
    const format = buf.readUInt16BE(base + off);
    // prefer a full Unicode table (format 12), then the BMP one (format 4)
    const score = format === 12 && (platform === 3 || platform === 0) ? 3 : format === 4 && (platform === 3 && encoding === 1 || platform === 0) ? 2 : format === 4 ? 1 : 0;
    if (score && (!best || score > best.score)) best = { score, off: base + off, format };
  }
  if (!best) return () => 0;
  const map = new Map();
  if (best.format === 12) {
    const groups = buf.readUInt32BE(best.off + 12);
    for (let g = 0; g < groups; g++) {
      const o = best.off + 16 + g * 12;
      const start = buf.readUInt32BE(o), end = buf.readUInt32BE(o + 4), gid = buf.readUInt32BE(o + 8);
      for (let c = start; c <= end && c - start < 65536; c++) map.set(c, gid + (c - start));
    }
  } else {
    const segX2 = buf.readUInt16BE(best.off + 6);
    const segs = segX2 / 2;
    const ends = best.off + 14, starts = ends + segX2 + 2, deltas = starts + segX2, rangeOffs = deltas + segX2;
    for (let s = 0; s < segs; s++) {
      const end = buf.readUInt16BE(ends + s * 2), start = buf.readUInt16BE(starts + s * 2);
      const delta = buf.readInt16BE(deltas + s * 2), ro = buf.readUInt16BE(rangeOffs + s * 2);
      if (start === 0xFFFF) continue;
      for (let c = start; c <= end; c++) {
        let gid;
        if (ro === 0) gid = (c + delta) & 0xFFFF;
        else {
          const gi = rangeOffs + s * 2 + ro + (c - start) * 2;
          if (gi + 2 > buf.length) continue;
          gid = buf.readUInt16BE(gi);
          if (gid) gid = (gid + delta) & 0xFFFF;
        }
        if (gid) map.set(c, gid);
      }
    }
  }
  return (cp) => map.get(cp) || 0;
}

const cache = new Map();
/** {unitsPerEm, advance(codePoint) -> font units} for one of the FONTS keys. */
function metrics(key) {
  if (cache.has(key)) return cache.get(key);
  const buf = fs.readFileSync(fontFile(key));
  const t = tables(buf);
  if (!t.head || !t.hhea || !t.hmtx || !t.cmap) throw new Error(`${FONTS[key].file}: not a TrueType font`);
  const unitsPerEm = buf.readUInt16BE(t.head.offset + 18);
  const numH = buf.readUInt16BE(t.hhea.offset + 34);
  const glyph = readCmap(buf, t.cmap);
  const hmtx = t.hmtx.offset;
  const advanceOf = (gid) => buf.readUInt16BE(hmtx + Math.min(gid, numH - 1) * 4);
  const m = {
    unitsPerEm,
    advance(cp) { const g = glyph(cp); return g ? advanceOf(g) : unitsPerEm * 0.5; },   // missing glyph: half an em, like the print tool
  };
  cache.set(key, m);
  return m;
}

/** Width in SVG units of `s` at `size`, with letter-spacing `ls` (tools/designs/common.py measure). */
function measure(s, key, size, ls = 0) {
  const m = metrics(key);
  let w = 0;
  for (const ch of String(s)) w += m.advance(ch.codePointAt(0));
  const n = Array.from(String(s)).length;
  return w * size / m.unitsPerEm + ls * Math.max(0, n - 1);
}

/** Largest size <= `size` whose width fits in maxW (never below 10; the frame's own `min` is applied by captionSvg). */
function fitSize(s, key, size, maxW, ls = 0) {
  while (size > 10 && measure(s, key, size, ls) > maxW) size -= 1;
  return size;
}

const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
const num = (v) => (Number.isInteger(v) ? String(v) : String(Number(v.toFixed(4))));

/** The frame's caption in the lettering the customer picked (caption.styles, tools/frames_v2.py), or its default. */
function captionOf(frame, style) {
  const c = frame && frame.caption;
  if (!c) return null;
  const st = style && c.styles && c.styles[style];
  return st ? { ...c, ...st } : c;
}

/** The text a caption frame shows for the customer's input: trimmed, cut to the frame's max, upper-cased if the frame says so. */
function captionText(frame, text, style) {
  const c = captionOf(frame, style);
  if (!c) return "";
  const s = String(text || "").trim().slice(0, c.max || 40);
  return c.upper ? s.toUpperCase() : s;
}

/**
 * Port of tools/frames.py caption_svg: the <text> element(s) for a caption, fitted to the frame's width with the
 * real font metrics. `text` is the raw customer caption (this applies trim/max/upper itself). "" when none.
 */
function captionSvg(frame, text, style) {
  const c = captionOf(frame, style);
  const s = captionText(frame, text, style);
  if (!c || !s) return "";
  const key = FONTS[c.font] ? c.font : "jost";
  const ls = Number(c.ls) || 0;
  const size = Math.max(c.min || 10, fitSize(s, key, c.size, c.w, ls));
  const x = c.x + (ls ? ls / 2 : 0);
  const tr = c.rot ? ` transform="rotate(${c.rot} ${c.x} ${c.y})"` : "";
  const lsAttr = ls ? ` letter-spacing="${ls}"` : "";
  let out = `<text x="${num(x)}" y="${c.y}" text-anchor="middle" ${FONTS[key].attrs} font-size="${size}"${lsAttr} fill="${c.color}"${tr}>${esc(s)}</text>`;
  const k = c.kicker;
  if (k && k.text) {
    const kkey = FONTS[k.font] ? k.font : "jos";
    const kls = Number(k.ls) || 0;
    const klsAttr = kls ? ` letter-spacing="${kls}"` : "";
    out = `<text x="${num(c.x + kls / 2)}" y="${k.y}" text-anchor="middle" ${FONTS[kkey].attrs} font-size="${k.size}"${klsAttr} fill="${k.color}">${esc(k.text)}</text>` + out;
  }
  return out;
}

module.exports = { FONTS, FONTS_DIR, fontFile, metrics, measure, fitSize, captionOf, captionText, captionSvg, esc };
