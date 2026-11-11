// Little Hive House emails in Brazilian Portuguese: the customer's language comes with the order (order.lang, set at
// checkout from the site's EN/PT choice) or with the request (data.lang). render() sets it for the duration of one
// email; every piece of customer text goes through tx(), which looks it up in pt.json, then in the patterns below
// (text with numbers, dates or names). Anything missing stays in English.
"use strict";

let LANG = "en";
let DICT = null;
const missed = new Set();   // what tx() couldn't translate (for the checking tools)

const MON = { Jan: "jan", Feb: "fev", Mar: "mar", Apr: "abr", May: "mai", Jun: "jun", Jul: "jul", Aug: "ago", Sep: "set", Oct: "out", Nov: "nov", Dec: "dez",
  January: "janeiro", February: "fevereiro", March: "março", April: "abril", June: "junho", July: "julho", August: "agosto",
  September: "setembro", October: "outubro", November: "novembro", December: "dezembro" };
const M = "(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)";
/** "Nov 17–20" → "17–20 de nov"; "Nov 28–Dec 2" → "28 de nov–2 de dez"; "November 3, 2026" → "3 de novembro de 2026" */
function date(s) {
  return String(s)
    .replace(new RegExp(M + " (\\d{1,2}), (\\d{4})", "g"), (_, m, d, y) => `${d} de ${MON[m]} de ${y}`)
    .replace(new RegExp(M + " (\\d{1,2})[–-](\\d{1,2})\\b", "g"), (_, m, a, b) => `${a}–${b} de ${MON[m]}`)
    .replace(new RegExp(M + " (\\d{1,2})[–-]" + M + " (\\d{1,2})", "g"), (_, m1, a, m2, b) => `${a} de ${MON[m1]}–${b} de ${MON[m2]}`)
    .replace(new RegExp(M + " (\\d{1,2})\\b", "g"), (_, m, d) => `${d} de ${MON[m]}`);
}
/** "15% off" → "15% de desconto"; "$5.00 off" → "$5.00 de desconto" */
function off(s) { return String(s).replace(/ off$/, " de desconto").replace(/^a little something off$/, "um descontinho"); }
/** "1 hour" → "1 hora"; "30 minutes" → "30 minutos" */
function dur(s) { return String(s).replace(/\b1 hour\b/, "1 hora").replace(/(\d+) hours/, "$1 horas").replace(/(\d+) minutes/, "$1 minutos"); }
const COL = {
  "USA Places": "Lugares dos EUA", "World Places": "Lugares pelo Mundo", "Ink Cities": "Cidades a Nanquim", "City Sketches": "Cidades em Traço",
  "Fall": "Outono", "Horror Classics": "Clássicos do Terror", "Furry Friends": "Amigos Peludos", "Kitchen Words": "Frases de Cozinha",
  "Ireland": "Irlanda", "Italia": "Itália", "Puerto Rico": "Porto Rico", "Pilipinas": "Filipinas", "India": "Índia", "Korea": "Coreia",
  "Japan": "Japão", "Greece": "Grécia", "France": "França", "Great Masters": "Grandes Mestres", "Mythology": "Mitologia",
  "Home Notes": "Recadinhos de Casa", "Night Sky": "Céu Noturno", "Birth Flowers": "Flores do Mês", "Storybook Classics": "Clássicos da Literatura",
  "Fairy Tales & Myths": "Contos de Fadas e Mitos", "Wise Words": "Palavras Sábias", "Holidays & Dates": "Datas Comemorativas",
  "Bumper Stickers": "Adesivos de Para-choque", "Christmas": "Natal", "Summer": "Verão", "Heritage": "Raízes",
};
const DATE_ONLY = new RegExp("^(about )?" + M + " \\d{1,2}([–-](" + M + " )?\\d{1,2})?(, \\d{4})?$");
const P = [
  [/^Here's everything that's coming your way, ordered (.+)\.$/, "Aqui está tudo o que vai chegar para você, pedido em $1."],
  [/^Here's everything that's coming your way\.$/, "Aqui está tudo o que vai chegar para você."],
  [/^(\d+) magnets? coming your way\. We'll start making them by hand right away\.$/, (_, n) => `${n} ${n === "1" ? "ímã" : "ímãs"} a caminho. Vamos começar a fazer à mão agora mesmo.`],
  [/^Thank you! Order (.+) is confirmed$/, "Obrigado! O pedido $1 está confirmado"],
  [/^Estimated arrival: about 1 to 2 weeks after you approve the proof$/, "Previsão de chegada: cerca de 1 a 2 semanas depois que você aprova a prova"],
  [/^Estimated arrival: (.+)$/, (_, d) => `Previsão de chegada: ${date(d)}`],
  [/^Your magnets are on the way!( \((.+)\))?$/, (_, x, n) => `Seus ímãs estão a caminho!${n ? ` (${n})` : ""}`],
  [/^(.+?)( tracking (.+))?\. Follow your package all the way to your door\.$/, (_, c, x, t) => `${c}${t ? `, rastreio ${t}` : ""}. Acompanhe o pacote até a sua porta.`],
  [/^Charged to your card today, when your order shipped( \(order (.+)\))?\. Keep this email as your receipt\.$/, (_, x, n) => `Cobrado no seu cartão hoje, quando o pedido foi enviado${n ? ` (pedido ${n})` : ""}. Guarde este e-mail como recibo.`],
  [/^Carrier: (.+)$/, "Transportadora: $1"],
  [/^Tracking number: see the tracking page$/, "Número de rastreio: veja a página de rastreio"],
  [/^Tracking number: (.+)$/, "Número de rastreio: $1"],
  [/^Order (.+) · Out for delivery$/, "Pedido $1 · Saiu para entrega"],
  [/^Order (.+) · Delivered$/, "Pedido $1 · Entregue"],
  [/^(.+), your magnets arrive today!$/, "$1, seus ímãs chegam hoje!"],
  [/^(.+) has your package out for delivery\. Keep an eye on the porch and the mailbox\.$/, "O $1 saiu para entregar o seu pacote. Fique de olho na porta e na caixa de correio."],
  [/^(.+) has your package out for delivery( \(order (.+)\))?\. Keep an eye on the porch!$/, (_, c, x, n) => `O ${c} saiu para entregar o seu pacote${n ? ` (pedido ${n})` : ""}. Fique de olho na porta!`],
  [/^Latest scan: (.+)$/, "Última atualização: $1"],
  [/^(.+), how do they look on your fridge\?$/, "$1, como eles ficaram na sua geladeira?"],
  [/^for your next order: (.+?) until (.+)\.$/, (_, o, d) => `no seu próximo pedido: ${off(o)} até ${date(d)}.`],
  [/^for your next order: (.+)\.$/, (_, o) => `no seu próximo pedido: ${off(o)}.`],
  [/^Show us your fridge! Share a photo on Instagram and tag (.+)$/, "Mostre a sua geladeira! Compartilhe uma foto no Instagram e marque $1"],
  [/^Return · (.+)$/, "Devolução · $1"],
  [/^Hi (.+?)[.!]$/, "Oi, $1!"],
  [/^Your return label for (.+)$/, (_, n) => `A sua etiqueta de devolução de ${n === "your order" ? "seu pedido" : n}`],
  [/^We got your return request \((.+)\)$/, (_, n) => `Recebemos o seu pedido de devolução (${n === "your order" ? "seu pedido" : n})`],
  [/^We're reprinting your magnets \((.+)\)$/, (_, n) => `Estamos reimprimindo seus ímãs (${n === "your order" ? "seu pedido" : n})`],
  [/^About your return for (.+)$/, (_, n) => `Sobre a sua devolução de ${n === "your order" ? "seu pedido" : n}`],
  [/^No printer\? Show this QR code at the Post Office: (.+)$/, "Sem impressora? Mostre este QR code na agência do correio: $1"],
  [/^In this return:\n([\s\S]+)$/, "Nesta devolução:\n$1"],
  [/^A note from us: ([\s\S]+)$/, "Um recado nosso: $1"],
  [/^A partial refund of (\$[\d.,]+) for (.+)$/, (_, a, n) => `Um reembolso parcial de ${a} do ${n === "your order" ? "seu pedido" : "pedido " + n}`],
  [/^Your refund for (.+) is on its way$/, (_, n) => `O reembolso do ${n === "your order" ? "seu pedido" : "pedido " + n} está a caminho`],
  [/^(\$[\d.,]+) is heading back to you\. Banks usually show it within 5 to 10 business days\.$/, "$1 está voltando para você. Os bancos costumam mostrar em 5 a 10 dias úteis."],
  [/^(Full|Partial) refund: (\$[\d.,]+)(.*)$/, (_, k, a, rest) => `${k === "Full" ? "Reembolso total" : "Reembolso parcial"}: ${a}${rest.replace(/order/g, "pedido")}`],
  [/^Back to your original payment method( for order (.+))?$/, (_, x, n) => `De volta para a forma de pagamento original${n ? ` do pedido ${n}` : ""}`],
  [/^Refunded on this order so far: (\$[\d.,]+) of (\$[\d.,]+)\.$/, "Reembolsado neste pedido até agora: $1 de $2."],
  [/^Welcome to the hive, (.+)!$/, "Bem-vindo à colmeia, $1!"],
  [/^(\d+% off|\$[\d.,]+ off|a little something off) your first order( until (.+))?\.?$/, (_, o, x, d) => `${off(o)} no seu primeiro pedido${d ? ` até ${date(d)}` : ""}.`],
  [/^Your account is ready, and (.+) your first order is waiting\.$/, (_, o) => `Sua conta está pronta, e ${off(o)} no seu primeiro pedido está esperando.`],
  [/^Thanks for joining! Here's (.+) your first order\.$/, (_, o) => `Obrigado por entrar! Aqui vai ${off(o)} no seu primeiro pedido.`],
  [/^One quick tap, (.+)!$/, "Só um toque, $1!"],
  [/^For your security this link expires in (.+) and works only once\. If it has expired, you can$/, (_, e) => `Por segurança, este link vence em ${dur(e)} e só funciona uma vez. Se ele já venceu, você pode`],
  [/^Tap the button to choose a new password\. The link works for (.+)\.$/, (_, e) => `Toque no botão para escolher uma senha nova. O link funciona por ${dur(e)}.`],
  [/^(.+), your magnets are still waiting$/, "$1, seus ímãs ainda estão esperando"],
  [/^We saved your (\d+) magnets?\. Pick up right where you left off\.$/, (_, n) => `Guardamos ${n === "1" ? "o seu ímã" : `os seus ${n} ímãs`}. Continue de onde parou.`],
  [/^Thanks for writing, (.+)!$/, "Obrigado por escrever, $1!"],
  [/^You wrote · (.+)$/, (_, t) => `Você escreveu · ${look(t) || t}`],
  [/^Thanks! We'll reply within 1 business day with ideas, a price for (\d+) magnets and next steps\.$/, "Obrigado! Respondemos em até 1 dia útil com ideias, o preço de $1 ímãs e os próximos passos."],
  [/^Thanks! We'll reply within 1 business day with ideas, a price and next steps\.$/, "Obrigado! Respondemos em até 1 dia útil com ideias, preço e os próximos passos."],
  [/^Here's your link, (.+)$/, "Aqui está o seu link, $1"],
  [/^Your payment link for (.+)$/, "O seu link de pagamento: $1"],
  [/^(\$[\d.,]+) for (.+)\. Pay securely by card, Apple Pay or Google Pay\.$/, "$1 por $2. Pague com segurança no cartão, Apple Pay ou Google Pay."],
  [/^Payments are processed by Stripe\. We never see or store your card number\.( This link works until (.+)\.)?$/, (_, x, d) => `Os pagamentos são processados pelo Stripe. Nunca vemos nem guardamos o número do seu cartão.${d ? ` Este link funciona até ${date(d)}.` : ""}`],
  [/^(\d+) photos?$/, (_, n) => `${n} ${n === "1" ? "foto" : "fotos"}`],
  [/^(\d+) frames$/, "$1 molduras"],
  [/^(\d+) packs$/, "$1 pacotes"],
  [/^(.+) frame$/, (_, f) => `Moldura ${(look(f) || f).toLowerCase()}`],
  [/^(.+) magnet$/, "Ímã $1"],
  [DATE_ONLY, (s) => (s.startsWith("about ") ? "por volta de " + date(s.slice(6)) : date(s))],
  [/^Good news, (.+)!$/, (_, n) => `Boa notícia, ${n}!`],
  [/^Thank you, (.+)!$/, (_, n) => `Obrigado, ${n}!`],
  [/^Thanks, (.+)!$/, (_, n) => `Obrigado, ${n}!`],
  [/^Hi (.+),$/, (_, n) => `Oi, ${n},`],
  [/^Order (LHH-\d+)$/, "Pedido $1"],
  [/^Qty (\d+)$/, "Qtd. $1"],
  [/^(\d+) photo magnets$/, "$1 ímãs com foto"],
  [/^(\d+) magnets( × (\d+))?$/, (_, n, x, q) => `${n} ímãs${q ? ` × ${q}` : ""}`],
  [/^Volume discount \((\d+)% off\)$/, "Desconto por quantidade ($1% off)"],
  [/^Promo code (.+)$/, "Cupom $1"],
  [/^Captions: (.+)$/, "Legendas: $1"],
  [/^Note: (.+)$/, "Recado: $1"],
];

function dict() {
  if (!DICT) { try { DICT = require("./pt.json"); } catch (e) { DICT = {}; } }
  return DICT;
}
function set(lang) { LANG = lang === "pt" ? "pt" : "en"; }
function get() { return LANG; }
/** The language to use for one email: the request's, else the order's, else English. */
function pick(data) {
  const d = data || {};
  const l = d.lang || (d.order && d.order.lang) || (d.contact && d.contact.lang) || (d.quote && d.quote.lang);
  return l === "pt" ? "pt" : "en";
}
function look(k) {
  const D = dict();
  if (Object.prototype.hasOwnProperty.call(D, k)) return D[k];
  if (Object.prototype.hasOwnProperty.call(COL, k)) return COL[k];
  for (const [re, r] of P) {
    const m = re.exec(k);
    if (m) return typeof r === "function" ? r(...m) : k.replace(re, r);
  }
  return null;
}
/** Customer text in the email's language. Keeps the leading/trailing spaces the pieces are glued with. */
function tx(s) {
  if (LANG !== "pt" || s === null || s === undefined || typeof s === "object") return s;
  const v = String(s);
  if (!/[A-Za-z]{2}/.test(v)) return s;
  const lead = /^\s*/.exec(v)[0], trail = /\s*$/.exec(v)[0], k = v.replace(/\s+/g, " ").trim();
  const r = look(k);
  if (r === null) { missed.add(k); return s; }
  return lead + r.trim() + trail;
}
module.exports = { set, get, pick, tx, date, missed };
