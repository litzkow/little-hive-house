// Shared look of every Little Hive House email: the page shell plus small building blocks.
// Every block returns {html, text} so the HTML and the plain-text version always say the same thing.
// Table layout + inline CSS for Outlook/Gmail; the <style> only adds mobile tweaks and Apple Mail dark mode.
"use strict";

const { esc, str, safeUrl, SUPPORT } = require("./format");

const C = {
  honey: "#F2A81D", honeySoft: "#F9D88A", wash: "#FDF0D2", ink: "#2B2118", muted: "#6A5845", line: "#E8D6B3",
  cream: "#FFF6E5", surface: "#FFFCF4", fridge: "#F3E7CF", link: "#8A5200", green: "#2E7D4F", red: "#A33A22",
};
const FD = "'Josefin Sans','Futura','Century Gothic','Trebuchet MS',Arial,sans-serif";
const FB = "'Jost','Avenir Next','Segoe UI',-apple-system,BlinkMacSystemFont,Roboto,Helvetica,Arial,sans-serif";
const FS = "Georgia,'Times New Roman',Times,serif";

const T = 'role="presentation" cellpadding="0" cellspacing="0" border="0"';

/** Rich inline text: parts are strings or {b}, {i}, {a, href}, {code}. Everything is escaped. */
function rich(parts) {
  const list = Array.isArray(parts) ? parts : [parts];
  let html = "";
  let text = "";
  for (const p of list) {
    if (p === null || p === undefined || p === false) continue;
    if (typeof p === "string" || typeof p === "number") {
      html += esc(p);
      text += str(p);
    } else if (p.a !== undefined) {
      const href = safeUrl(p.href);
      html += href ? `<a class="lh-a" href="${esc(href)}" style="color:${C.link};text-decoration:underline">${esc(p.a)}</a>` : esc(p.a);
      text += href && !href.startsWith("mailto:") && str(p.a) !== href ? `${str(p.a)} (${href})` : str(p.a);
    } else if (p.b !== undefined) {
      html += `<strong style="font-weight:600">${esc(p.b)}</strong>`;
      text += str(p.b);
    } else if (p.i !== undefined) {
      html += `<em>${esc(p.i)}</em>`;
      text += str(p.i);
    } else if (p.code !== undefined) {
      html += `<span style="font-family:Menlo,Consolas,monospace;font-weight:600;letter-spacing:.06em">${esc(p.code)}</span>`;
      text += str(p.code);
    }
  }
  return { html, text };
}

/** Wraps block html in a spacing row. */
function row(inner, pad = "0 0 24px") {
  return `<table ${T} width="100%"><tr><td style="padding:${pad}">${inner}</td></tr></table>`;
}

function hero({ eyebrow, title, lead }) {
  const lr = lead ? rich(lead) : null;
  const pill = eyebrow
    ? `<table ${T}><tr><td style="background:${C.honeySoft};border-radius:999px;padding:6px 14px 5px;font-family:${FD};font-weight:700;font-size:12px;line-height:16px;letter-spacing:2.4px;text-transform:uppercase;color:${C.ink}">${esc(eyebrow)}</td></tr></table>`
    : "";
  const html = row(
    `${pill}<h1 class="lh-t h1" style="margin:${eyebrow ? "16px" : "0"} 0 0;font-family:${FD};font-weight:700;font-size:32px;line-height:38px;letter-spacing:-.2px;color:${C.ink}">${esc(title)}</h1>` +
    (lr ? `<p class="lh-m" style="margin:12px 0 0;font-family:${FB};font-size:17px;line-height:27px;color:${C.muted}">${lr.html}</p>` : ""),
    "0 0 28px");
  const text = [eyebrow ? str(eyebrow).toUpperCase() : "", str(title), lr ? lr.text : ""].filter(Boolean).join("\n\n");
  return { html, text };
}

function p(parts, opts = {}) {
  const r = rich(parts);
  const size = opts.small ? "14px" : "16px";
  const lh = opts.small ? "22px" : "26px";
  const color = opts.muted ? C.muted : C.ink;
  return {
    html: row(`<p class="${opts.muted ? "lh-m" : "lh-t"}" style="margin:0;font-family:${FB};font-size:${size};line-height:${lh};color:${color}${opts.center ? ";text-align:center" : ""}">${r.html}</p>`, opts.pad || "0 0 18px"),
    text: r.text,
  };
}

/** Small uppercase section label with a hairline under it. */
function h2(label) {
  return {
    html: row(`<p class="lh-m lh-line" style="margin:0;padding:0 0 10px;border-bottom:1px solid ${C.line};font-family:${FD};font-weight:700;font-size:13px;line-height:16px;letter-spacing:2.6px;text-transform:uppercase;color:${C.muted}">${esc(label)}</p>`, "8px 0 16px"),
    text: `${str(label).toUpperCase()}\n${"-".repeat(Math.min(40, str(label).length))}`,
  };
}

/** A tappable button (min 48 px tall). variant: honey | ink | ghost. */
function buttonCell(href, label, variant = "honey", full = false) {
  const url = safeUrl(href, "#");
  const bg = variant === "honey" ? C.honey : variant === "ink" ? C.ink : "transparent";
  const fg = variant === "ink" ? C.cream : C.ink;
  const border = variant === "ghost" ? C.ink : bg;
  const cls = variant === "ink" ? ' class="lh-ink"' : variant === "ghost" ? ' class="lh-ghost"' : "";
  const acls = variant === "ink" ? "lh-ink-a" : variant === "ghost" ? "lh-t" : "";
  return `<table ${T} class="btn-t"${full ? ' width="100%"' : ""} style="border-collapse:separate"><tr><td align="center"${cls}${variant === "ghost" ? "" : ` bgcolor="${bg}"`} style="border-radius:999px;background:${bg};border:2px solid ${border};mso-padding-alt:14px 30px">` +
    `<a${acls ? ` class="${acls}"` : ""} href="${esc(url)}" target="_blank" style="display:${full ? "block" : "inline-block"};padding:14px 30px;mso-padding-alt:0;font-family:${FB};font-weight:600;font-size:17px;line-height:20px;color:${fg};text-decoration:none;border-radius:999px;text-align:center">${esc(label)}</a></td></tr></table>`;
}

/** One or two buttons in a row (they stack on phones). items: [{href, label, variant}] */
function buttons(items, opts = {}) {
  const list = items.filter((b) => b && safeUrl(b.href));
  if (!list.length) return { html: "", text: "" };
  const align = opts.center ? "center" : "left";
  let cells;
  if (list.length === 1 || opts.stack) {
    cells = list.map((b, i) => `<tr><td align="${align}" style="padding:${i ? "12px" : "0"} 0 0">${buttonCell(b.href, b.label, b.variant, opts.full)}</td></tr>`).join("");
    cells = `<table ${T} width="100%">${cells}</table>`;
  } else {
    cells = `<table ${T} class="btn-row"${opts.center ? ' align="center"' : ""}><tr>` + list.map((b, i) =>
      `<td class="stack${i ? " stack-top" : ""}" valign="top" style="padding:0 ${i < list.length - 1 ? "12px" : "0"} 0 0">${buttonCell(b.href, b.label, b.variant)}</td>`).join("") + "</tr></table>";
  }
  return {
    html: row(cells, opts.pad || "6px 0 28px"),
    text: list.map((b) => `${b.label}: ${safeUrl(b.href)}`).join("\n"),
  };
}

/** A soft honey box for notes, gift messages and codes. tone: honey | cream | alert */
function box(innerHtml, innerText, tone = "honey", opts = {}) {
  const bg = tone === "alert" ? "#FBE3D6" : tone === "cream" ? C.cream : C.wash;
  const border = tone === "alert" ? "#E9B49A" : C.line;
  return {
    html: row(`<table ${T} width="100%"><tr><td class="lh-box" style="background:${bg};border:1px solid ${border};border-radius:16px;padding:${opts.pad || "18px 22px"}${opts.center ? ";text-align:center" : ""}">${innerHtml}</td></tr></table>`, opts.outer || "0 0 24px"),
    text: innerText,
  };
}

function label(textValue) {
  return `<p class="lh-m" style="margin:0 0 6px;font-family:${FD};font-weight:700;font-size:12px;line-height:16px;letter-spacing:2.2px;text-transform:uppercase;color:${C.muted}">${esc(textValue)}</p>`;
}
function bodyText(html, opts = {}) {
  return `<p class="${opts.muted ? "lh-m" : "lh-t"}" style="margin:${opts.margin || "0"};font-family:${opts.serif ? FS : FB};font-size:${opts.size || 16}px;line-height:${opts.lh || 25}px;color:${opts.muted ? C.muted : C.ink}${opts.italic ? ";font-style:italic" : ""}${opts.weight ? ";font-weight:" + opts.weight : ""}">${html}</p>`;
}

/** Big promo / discount code with an optional caption. */
function code(codeText, caption) {
  const cap = caption ? rich(caption) : null;
  return box(
    `${label("Your code")}<p class="lh-t" style="margin:2px 0 0;font-family:Menlo,Consolas,'Courier New',monospace;font-weight:700;font-size:26px;line-height:34px;letter-spacing:4px;color:${C.ink}">${esc(codeText)}</p>` +
    (cap ? bodyText(cap.html, { muted: true, size: 14, lh: 21, margin: "6px 0 0" }) : ""),
    `Your code: ${str(codeText)}${cap ? "\n" + cap.text : ""}`, "honey", { center: true, pad: "20px 22px" });
}

/** Two columns that stack on phones. cols: [{label, html, text}] */
function columns(cols) {
  const list = cols.filter(Boolean);
  if (!list.length) return { html: "", text: "" };
  const w = list.length > 1 ? "50%" : "100%";
  const html = row(`<table ${T} width="100%"><tr>` + list.map((c, i) =>
    `<td class="stack${i ? " stack-top" : ""}" width="${w}" valign="top" style="padding:0 ${i < list.length - 1 ? "16px" : "0"} 0 0">${label(c.label)}${c.html}</td>`).join("") + "</tr></table>", "0 0 26px");
  return { html, text: list.map((c) => `${str(c.label).toUpperCase()}\n${c.text}`).join("\n\n") };
}

/** Key/value rows (admin summaries). rows: [[label, valueParts]] */
function facts(rows) {
  const list = rows.filter((r) => r && r[1] !== undefined && r[1] !== null && r[1] !== "");
  const html = row(`<table ${T} width="100%">` + list.map(([k, v], i) => {
    const r = rich(v);
    return `<tr><td class="lh-m lh-line" valign="top" width="34%" style="padding:9px 12px 9px 0;border-top:${i ? `1px solid ${C.line}` : "0"};font-family:${FB};font-size:14px;line-height:20px;color:${C.muted}">${esc(k)}</td>` +
      `<td class="lh-t lh-line" valign="top" style="padding:9px 0;border-top:${i ? `1px solid ${C.line}` : "0"};font-family:${FB};font-size:15px;line-height:21px;color:${C.ink}">${r.html}</td></tr>`;
  }).join("") + "</table>", "0 0 22px");
  return { html, text: list.map(([k, v]) => `${k}: ${rich(v).text}`).join("\n") };
}

/** Numbered "what happens next" steps with honey number chips. steps: [{title, body}] */
function steps(list) {
  const html = row(`<table ${T} width="100%">` + list.map((s, i) =>
    `<tr><td valign="top" width="44" style="padding:0 14px ${i < list.length - 1 ? "16px" : "0"} 0">` +
    `<table ${T}><tr><td align="center" valign="middle" width="32" height="32" bgcolor="${C.honey}" style="width:32px;height:32px;border-radius:10px;background:${C.honey};font-family:${FD};font-weight:700;font-size:15px;line-height:32px;color:${C.ink};text-align:center">${i + 1}</td></tr></table></td>` +
    `<td valign="top" style="padding:3px 0 ${i < list.length - 1 ? "16px" : "0"}">${bodyText(`<strong style="font-weight:600">${esc(s.title)}</strong>`, { size: 16, lh: 22 })}${bodyText(rich(s.body).html, { muted: true, size: 15, lh: 22, margin: "3px 0 0" })}</td></tr>`).join("") + "</table>", "0 0 28px");
  return { html, text: list.map((s, i) => `${i + 1}. ${s.title}: ${rich(s.body).text}`).join("\n") };
}

/** Order progress: Ordered · Making · Shipped · Delivered, `at` = index of the current step. */
function progress(at) {
  const names = ["Ordered", "Making", "Shipped", "Delivered"];
  const bars = names.map((n, i) =>
    `<td width="25%" style="padding:0 ${i < 3 ? "4px" : "0"} 0 ${i ? "4px" : "0"}"><table ${T} width="100%"><tr><td height="8" bgcolor="${i <= at ? C.honey : C.fridge}" class="${i <= at ? "" : "lh-track"}" style="height:8px;line-height:8px;font-size:0;border-radius:99px;background:${i <= at ? C.honey : C.fridge}">&nbsp;</td></tr></table></td>`).join("");
  const labels = names.map((n, i) =>
    `<td width="25%" class="${i <= at ? "lh-t" : "lh-m"}" style="padding:8px 4px 0 ${i ? "4px" : "0"};font-family:${FB};font-size:13px;line-height:16px;font-weight:${i === at ? 600 : 400};color:${i <= at ? C.ink : C.muted}">${n}</td>`).join("");
  return {
    html: row(`<table ${T} width="100%"><tr>${bars}</tr><tr>${labels}</tr></table>`, "0 0 30px"),
    text: names.map((n, i) => (i < at ? `[x] ${n}` : i === at ? `[>] ${n}` : `[ ] ${n}`)).join("  "),
  };
}

/** Five star links (rating 1..5). */
function stars(hrefFor) {
  const cells = [1, 2, 3, 4, 5].map((n) =>
    `<td align="center" style="padding:0 4px"><a href="${esc(hrefFor(n))}" target="_blank" title="${n} star${n > 1 ? "s" : ""}" aria-label="${n} star${n > 1 ? "s" : ""}" style="display:inline-block;width:48px;height:48px;line-height:48px;border-radius:14px;background:${C.honey};color:${C.ink};font-size:26px;text-decoration:none;text-align:center;font-family:Arial,sans-serif">&#9733;</a></td>`).join("");
  return {
    html: row(`<table ${T} align="center"><tr>${cells}</tr></table>`, "4px 0 10px"),
    text: [5, 4, 3, 2, 1].map((n) => `${"*".repeat(n)}${" ".repeat(6 - n)}${hrefFor(n)}`).join("\n"),
  };
}

/** A row of design thumbnails with titles. items: [{src, alt, title, href}] (max 3) */
function gallery(items) {
  const list = items.filter((g) => g && safeUrl(g.src)).slice(0, 3);
  if (!list.length) return { html: "", text: "" };
  const cells = list.map((g, i) =>
    `<td width="33%" valign="top" align="center" style="padding:0 ${i < list.length - 1 ? "8px" : "0"} 0 ${i ? "8px" : "0"}">` +
    `<a href="${esc(safeUrl(g.href, "#"))}" target="_blank" style="text-decoration:none"><img class="lh-thumb" src="${esc(g.src)}" width="160" alt="${esc(g.alt || g.title)}" style="display:block;width:100%;max-width:160px;height:auto;border:1px solid ${C.line};border-radius:14px"></a>` +
    `<p class="lh-t" style="margin:8px 0 0;font-family:${FB};font-size:14px;line-height:19px;font-weight:600;color:${C.ink}">${esc(g.title)}</p>` +
    (g.sub ? `<p class="lh-m" style="margin:2px 0 0;font-family:${FB};font-size:12px;line-height:17px;color:${C.muted}">${esc(g.sub)}</p>` : "") + "</td>").join("");
  return {
    html: row(`<table ${T} width="100%"><tr>${cells}</tr></table>`, "0 0 26px"),
    text: list.map((g) => `- ${g.title}${g.sub ? ` (${g.sub})` : ""}: ${safeUrl(g.href)}`).join("\n"),
  };
}

function divider() {
  return { html: row(`<table ${T} width="100%"><tr><td class="lh-line" style="border-top:1px solid ${C.line};font-size:0;line-height:0;height:1px">&nbsp;</td></tr></table>`, "6px 0 26px"), text: "" };
}

/** Raw html+text block (for the order parts). */
function raw(html, text, pad = "0 0 24px") {
  return { html: row(html, pad), text: text || "" };
}

const STYLE = `
:root{color-scheme:light dark;supported-color-schemes:light dark}
body{margin:0!important;padding:0!important;width:100%!important;-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%}
table,td{mso-table-lspace:0pt;mso-table-rspace:0pt}
img{border:0;outline:none;text-decoration:none;-ms-interpolation-mode:bicubic}
a[x-apple-data-detectors]{color:inherit!important;text-decoration:none!important;font-size:inherit!important;font-family:inherit!important;font-weight:inherit!important;line-height:inherit!important}
.lh-btn-wrap a:hover{opacity:.92}
@media only screen and (max-width:620px){
  .px{padding-left:22px!important;padding-right:22px!important}
  .pt{padding-top:28px!important}
  .stack{display:block!important;width:100%!important;max-width:100%!important;padding-right:0!important}
  .stack-top{padding-top:14px!important}
  .h1{font-size:28px!important;line-height:34px!important}
  .btn-t,.btn-row{width:100%!important}
  .btn-t a{display:block!important}
  .hide-m{display:none!important}
  .logo{width:96px!important;height:96px!important}
  .thumb-td{width:56px!important;padding-right:12px!important}
  .thumb{width:56px!important;height:56px!important}
}
@media (prefers-color-scheme:dark){
  .lh-bg{background:#1C1610!important}
  .lh-card{background:#261E17!important;border-color:#3E3228!important;border-top-color:#F5B83A!important}
  .lh-t{color:#F7EBD3!important}
  .lh-m{color:#CDB898!important}
  .lh-a{color:#F9D88A!important}
  .lh-box{background:#33281C!important;border-color:#4A3A28!important}
  .lh-line{border-color:#3E3228!important}
  .lh-track{background:#3E3228!important}
  .lh-green{color:#8FD3A6!important}
  .lh-ink{background:#F7EBD3!important;border-color:#F7EBD3!important}
  .lh-ink-a{color:#1C1610!important}
  .lh-ghost{border-color:#F7EBD3!important}
  .lh-thumb{border-color:#4A3A28!important}
}
[data-ogsb] .lh-bg{background:#1C1610!important}
[data-ogsb] .lh-card{background:#261E17!important}
[data-ogsb] .lh-box{background:#33281C!important}
[data-ogsc] .lh-t{color:#F7EBD3!important}
[data-ogsc] .lh-m{color:#CDB898!important}
[data-ogsc] .lh-a{color:#F9D88A!important}
`;

/**
 * The page shell.
 * opts: {title, preheader, blocks, links, audience: "customer"|"admin", marketing, unsubscribeUrl, reason, postalAddress}
 */
function page(opts) {
  const L = opts.links;
  const blocks = opts.blocks.filter((b) => b && (b.html || b.text));
  const admin = opts.audience === "admin";
  const pre = str(opts.preheader);
  // The spacer keeps mail apps from pulling body text into the inbox preview.
  const spacer = "&#847;&zwnj;&nbsp;".repeat(60);
  const logoSize = admin ? 72 : 112;
  const unsub = safeUrl(opts.unsubscribeUrl) || (opts.marketing ? `mailto:${SUPPORT}?subject=Unsubscribe` : "");
  const postal = str(opts.postalAddress || process.env.MAIL_POSTAL_ADDRESS);
  const small = (html, m = "10px 0 0") => `<p class="lh-m" style="margin:${m};font-family:${FB};font-size:13px;line-height:20px;color:${C.muted}">${html}</p>`;
  const a = (href, t) => `<a class="lh-a" href="${esc(href)}" style="color:${C.link};text-decoration:underline">${esc(t)}</a>`;

  const footerHtml = admin
    ? small(`Little Hive House store alert · ${a(L.adminHome, "Open the admin")}`, "0")
    : `<img src="${esc(L.hexes)}" width="54" height="18" alt="" style="display:block;margin:0 auto;width:54px;height:18px">` +
      `<p class="lh-t" style="margin:14px 0 0;font-family:${FD};font-weight:700;font-size:13px;line-height:18px;letter-spacing:2.6px;text-transform:uppercase;color:${C.ink}">Little Hive House</p>` +
      small("Handmade fridge magnets and little gifts, made by hand in small batches.", "6px 0 0") +
      small(`Questions? Just reply, or write to ${a(`mailto:${SUPPORT}`, SUPPORT)}`) +
      small(a(L.site, L.host)) +
      (opts.reason ? small(esc(opts.reason)) : "") +
      (unsub ? small(`${a(unsub, "Unsubscribe")} from these emails at any time.`) : "") +
      (postal ? small(esc(postal)) : "");

  const html = `<!doctype html>
<html lang="en" xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<meta name="x-apple-disable-message-reformatting">
<meta name="format-detection" content="telephone=no,date=no,address=no,email=no,url=no">
<meta name="color-scheme" content="light dark">
<meta name="supported-color-schemes" content="light dark">
<title>${esc(opts.title)}</title>
<!--[if mso]><noscript><xml><o:OfficeDocumentSettings><o:PixelsPerInch>96</o:PixelsPerInch></o:OfficeDocumentSettings></xml></noscript>
<style>table,td,p,h1,a,span,strong{font-family:Arial,Helvetica,sans-serif!important}</style><![endif]-->
<!--[if !mso]><!--><link href="https://fonts.googleapis.com/css2?family=Josefin+Sans:wght@600;700&amp;family=Jost:wght@400;500;600&amp;display=swap" rel="stylesheet"><!--<![endif]-->
<style>${STYLE}</style>
</head>
<body class="lh-bg" style="margin:0;padding:0;background:${C.cream};word-spacing:normal">
<div role="article" aria-roledescription="email" aria-label="${esc(opts.title)}" lang="en" style="font-size:16px">
<div style="display:none;font-size:1px;line-height:1px;max-height:0;max-width:0;opacity:0;overflow:hidden;mso-hide:all">${esc(pre)}${spacer}</div>
<table ${T} width="100%" class="lh-bg" bgcolor="${C.cream}" style="background:${C.cream}">
<tr><td align="center" style="padding:${admin ? "20px" : "28px"} 10px 40px">
<!--[if mso]><table ${T} width="600" align="center"><tr><td><![endif]-->
<table ${T} width="100%" style="max-width:600px;margin:0 auto">
<tr><td align="center" style="padding:0 0 ${admin ? "14px" : "20px"}"><a href="${esc(L.site)}" target="_blank" style="text-decoration:none"><img class="${admin ? "" : "logo"}" src="${esc(L.logo)}" width="${logoSize}" height="${logoSize}" alt="Little Hive House" style="display:block;width:${logoSize}px;height:${logoSize}px;border:0;font-family:${FD};font-size:14px;color:${C.ink}"></a></td></tr>
<tr><td class="lh-card" bgcolor="${C.surface}" style="background:${C.surface};border:1px solid ${C.line};border-top:6px solid ${C.honey};border-radius:22px">
<table ${T} width="100%"><tr><td class="px pt" style="padding:${admin ? "28px 32px 12px" : "38px 44px 16px"}">
${blocks.map((b) => b.html).join("\n")}
</td></tr></table>
</td></tr>
<tr><td align="center" class="px" style="padding:28px 32px 0;text-align:center">${footerHtml}</td></tr>
</table>
<!--[if mso]></td></tr></table><![endif]-->
</td></tr>
</table>
</div>
</body>
</html>`;

  const textBody = blocks.map((b) => b.text).filter(Boolean).join("\n\n");
  const footerText = admin
    ? `--\nLittle Hive House store alert\n${L.adminHome}`
    : ["--", "Little Hive House · handmade fridge magnets and little gifts", `Questions? Just reply, or write to ${SUPPORT}`, L.site,
      opts.reason || "", unsub ? `Unsubscribe: ${unsub.replace(/^mailto:/, "")}` : "", postal].filter(Boolean).join("\n");
  const text = `${admin ? "LITTLE HIVE HOUSE · STORE ALERT" : "LITTLE HIVE HOUSE"}\n\n${textBody}\n\n${footerText}\n`;
  return { html, text: text.replace(/\n{3,}/g, "\n\n") };
}

module.exports = { C, FD, FB, FS, T, rich, row, hero, p, h2, buttons, buttonCell, box, label, bodyText, code, columns, facts, steps, progress, stars, gallery, divider, raw, page };
