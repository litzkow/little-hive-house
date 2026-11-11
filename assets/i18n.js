/* Little Hive House: the site in Brazilian Portuguese.
   The pages are written in English. When the visitor's language is Portuguese (their phone's language, or the EN/PT
   switch at the top, kept in localStorage "lhh-lang"), the head of every page loads this file and assets/i18n-pt.js,
   and the text is swapped as the page is built, before it shows (and again whenever a script adds or changes text:
   the cart, the photo builder, the order pages).

   How a piece of text is found in the dictionary (assets/i18n-pt.js):
   - a sentence with links or bold inside (a <p>, <li>, heading… whose own text runs around inline tags) is looked up
     whole, as its HTML with the inline tags' attributes left out:  "Free US shipping on orders over <a>$35</a>";
     the translation is written the same way and gets the original tags' attributes back, in order of appearance;
   - any other text is looked up as it reads, with the spaces tidied ("Add to cart");
   - text with numbers or names in it goes through the patterns (LHH_I18N.load(dict, patterns));
   - aria-label, placeholder, title and alt are looked up like text.
   Anything not found stays in English. Elements with translate="no" (design names, prices…) are left alone. */
(function () {
  "use strict";
  var D = Object.create(null), P = [], ready = false, html = document.documentElement;
  var SKIP = { SCRIPT: 1, STYLE: 1, TEXTAREA: 1, CODE: 1, PRE: 1, svg: 1, SVG: 1, NOSCRIPT: 1, TEMPLATE: 1, OPTION: 0 };
  var INLINE = { A: 1, STRONG: 1, EM: 1, B: 1, I: 1, SPAN: 1, BR: 1, SMALL: 1, SUP: 1, SUB: 1, U: 1, MARK: 1, TIME: 1, ABBR: 1, S: 1 };
  var BLOCK = { P: 1, LI: 1, H1: 1, H2: 1, H3: 1, H4: 1, H5: 1, H6: 1, DT: 1, DD: 1, LABEL: 1, FIGCAPTION: 1, TD: 1, TH: 1,
    BUTTON: 1, SUMMARY: 1, LEGEND: 1, BLOCKQUOTE: 1, CAPTION: 1, DIV: 1, SPAN: 1, A: 1, SMALL: 1, STRONG: 1, EM: 1 };
  var ATTRS = ["aria-label", "placeholder", "title", "alt", "data-label", "data-title"];

  function norm(s) { return s.replace(/\s+/g, " ").trim(); }
  var C = Object.create(null);   // what the patterns gave for a text before (the shop repeats thousands of names)
  function look(s) {
    var k = norm(s);
    if (!k || !/[A-Za-z]/.test(k)) return null;
    if (k in D) return D[k];
    if (k in C) return C[k];
    return (C[k] = pat(k));
  }
  function pat(k) {
    for (var i = 0; i < P.length; i++) {
      var m = P[i][0].exec(k);
      if (m) {
        var r = P[i][1], out = typeof r === "function" ? r.apply(null, m) : k.replace(P[i][0], r);
        if (out != null) return out;                       // a pattern can pass (null) when the name isn't one it knows
      }
    }
    return null;
  }
  function t(s) { var r = look(String(s)); return r == null ? s : r; }

  // the whole-sentence key of an element: its inner HTML with every tag's attributes dropped
  function shape(el) {
    var out = "";
    for (var n = el.firstChild; n; n = n.nextSibling) {
      if (n.nodeType === 3) out += n.nodeValue;
      else if (n.nodeType === 1) {
        var tag = n.tagName.toLowerCase();
        if (!INLINE[n.tagName]) return null;               // a block inside: not a sentence
        out += tag === "br" ? "<br>" : "<" + tag + ">" + (shape(n) || "") + "</" + tag + ">";
      }
    }
    return out;
  }
  function mixed(el) {
    var text = false, tags = false;
    for (var n = el.firstChild; n; n = n.nextSibling) {
      if (n.nodeType === 3 && /\S/.test(n.nodeValue)) text = true;
      else if (n.nodeType === 1) { if (!INLINE[n.tagName]) return false; tags = true; }
    }
    return text && tags;
  }
  function inlineList(el, acc) {
    for (var n = el.firstElementChild; n; n = n.nextElementSibling) { acc.push(n); inlineList(n, acc); }
    return acc;
  }
  // the tag tree without the text: "a(span())strong()"
  function sig(el) {
    var s = "";
    for (var n = el.firstElementChild; n; n = n.nextElementSibling) s += n.tagName + "(" + sig(n) + ")";
    return s;
  }
  // same tags in the same places: only the words change, so the page's own elements (and their click handlers) stay
  function merge(o, t) {
    var oe = [], te = [], gaps = [""], n;
    for (n = t.firstChild; n; n = n.nextSibling) {
      if (n.nodeType === 1) { te.push(n); gaps.push(""); } else if (n.nodeType === 3) gaps[gaps.length - 1] += n.nodeValue;
    }
    for (n = o.firstChild; n;) { var nx = n.nextSibling; if (n.nodeType === 3) o.removeChild(n); else if (n.nodeType === 1) oe.push(n); n = nx; }
    for (var i = 0; i <= oe.length; i++) {
      if (gaps[i]) o.insertBefore(document.createTextNode(gaps[i]), oe[i] || null);
      if (i < oe.length) merge(oe[i], te[i]);
    }
  }
  function swapWhole(el) {
    var key = norm(shape(el) || ""), tr = key ? look(key) : null;
    if (tr == null) return false;
    if (norm(tr) === key) return true;                     // already in Portuguese (a pattern gave the same text back)
    var tpl = document.createElement("div");
    tpl.innerHTML = tr;
    if (sig(tpl) === sig(el)) { merge(el, tpl); return true; }
    var old = inlineList(el, []), byTag = {};
    old.forEach(function (o) { (byTag[o.tagName] = byTag[o.tagName] || []).push(o); });
    el.innerHTML = tr;
    var seen = {};
    inlineList(el, []).forEach(function (n) {
      var i = seen[n.tagName] = (seen[n.tagName] || 0) + 1, o = (byTag[n.tagName] || [])[i - 1];
      if (o) for (var a = 0; a < o.attributes.length; a++) n.setAttribute(o.attributes[a].name, o.attributes[a].value);
    });
    return true;
  }
  function doText(n) {
    var v = n.nodeValue, r = look(v);
    if (r == null) return;
    var lead = /^\s*/.exec(v)[0], trail = /\s*$/.exec(v)[0];
    var nv = lead + r + trail;
    if (nv !== v) n.nodeValue = nv;
  }
  function doAttrs(el) {
    for (var i = 0; i < ATTRS.length; i++) {
      var v = el.getAttribute(ATTRS[i]);
      if (v) { var r = look(v); if (r != null && r !== v) el.setAttribute(ATTRS[i], r); }
    }
    if (el.tagName === "INPUT" && /^(submit|button)$/i.test(el.type) && el.value) { var r2 = look(el.value); if (r2 != null) el.value = r2; }
  }
  function walk(node) {
    if (node.nodeType === 3) { if (!node.parentNode || !skipped(node.parentNode)) doText(node); return; }
    if (node.nodeType !== 1 || SKIP[node.tagName] || node.getAttribute("translate") === "no") return;
    doAttrs(node);
    if (BLOCK[node.tagName] && mixed(node) && swapWhole(node)) return;
    for (var c = node.firstChild; c; c = c.nextSibling) walk(c);
  }
  function skipped(el) {
    for (; el && el.nodeType === 1; el = el.parentNode) {
      if (SKIP[el.tagName] || el.getAttribute("translate") === "no") return true;
    }
    return false;
  }
  // a text change inside a sentence: redo the whole sentence when the sentence is in the dictionary
  function sentenceOf(n) {
    var el = n.nodeType === 1 ? n : n.parentNode;
    for (var k = 0; el && el.nodeType === 1 && k < 3; el = el.parentNode, k++) if (BLOCK[el.tagName] && mixed(el)) return el;
    return null;
  }
  var busy = false;
  var mo = new MutationObserver(function (list) {
    if (busy || !ready) return;
    busy = true;
    try {
      for (var i = 0; i < list.length; i++) {
        var m = list[i];
        if (m.type === "characterData") {
          if (skipped(m.target.parentNode)) continue;
          var s = sentenceOf(m.target);
          if (s && swapWhole(s)) continue;
          doText(m.target);
        } else if (m.type === "attributes") {
          if (!skipped(m.target)) doAttrs(m.target);
        } else {
          for (var j = 0; j < m.addedNodes.length; j++) {
            var a = m.addedNodes[j];
            if (a.parentNode && skipped(a.parentNode)) continue;
            var s2 = a.nodeType === 3 && sentenceOf(a);
            if (s2 && swapWhole(s2)) continue;
            walk(a);
          }
          if (m.target.nodeType === 1 && BLOCK[m.target.tagName] && mixed(m.target) && !skipped(m.target)) swapWhole(m.target);
        }
      }
    } finally { busy = false; }
  });
  function title() { var r = look(document.title); if (r != null) document.title = r; }

  window.LHH_I18N = {
    lang: "pt",
    t: t,
    load: function (dict, patterns) {
      for (var k in dict) D[norm(k)] = dict[k];
      P = P.concat(patterns || []); C = Object.create(null);
      if (ready || window.LHH_I18N_DRY) return;          // DRY: checking tools only look things up
      ready = true;
      title();
      if (document.body) walk(document.body);
      mo.observe(html, { childList: true, subtree: true, characterData: true, attributes: true, attributeFilter: ATTRS.concat(["value"]) });
      var done = function () { title(); walk(document.body); html.classList.add("i18n-ready"); };
      if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", done); else done();
    },
    apply: function (root) { walk(root || document.body); },
    /** For checking: every piece of English text on the page that the dictionary doesn't have yet. */
    missing: function () {
      var out = [];
      function add(kind, s) { var k = norm(s); if (k && /[A-Za-z]{2}/.test(k) && look(k) == null) out.push([kind, k]); }
      (function w(node) {
        if (node.nodeType === 3) { add("T", node.nodeValue); return; }
        if (node.nodeType !== 1 || SKIP[node.tagName] || node.getAttribute("translate") === "no") return;
        ATTRS.forEach(function (a) { var v = node.getAttribute(a); if (v) add("A", v); });
        if (BLOCK[node.tagName] && mixed(node)) { var k = norm(shape(node) || ""); if (k && look(k) == null) out.push(["H", k]); else if (k) return; }
        for (var c = node.firstChild; c; c = c.nextSibling) w(c);
      })(document.body);
      add("T", document.title);
      return out;
    },
  };
})();
