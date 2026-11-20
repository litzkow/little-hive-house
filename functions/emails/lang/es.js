// Little Hive House emails (and the Stripe checkout page) in neutral Latin American Spanish, "tú".
// look(key): the exact dictionary (functions/emails/es.json), the collection names, then the patterns below.
"use strict";

let DICT = null;
function dict() {
  if (!DICT) { try { DICT = require("../es.json"); } catch (e) { DICT = {}; } }
  return DICT;
}
const MON = { Jan: "ene", Feb: "feb", Mar: "mar", Apr: "abr", May: "may", Jun: "jun", Jul: "jul", Aug: "ago", Sep: "sep", Oct: "oct", Nov: "nov", Dec: "dic",
  January: "enero", February: "febrero", March: "marzo", April: "abril", June: "junio", July: "julio", August: "agosto",
  September: "septiembre", October: "octubre", November: "noviembre", December: "diciembre" };
const M = "(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)";
/** "Nov 17–20" → "17–20 de nov"; "Nov 28–Dec 2" → "28 de nov–2 de dic"; "November 3, 2026" → "3 de noviembre de 2026" */
function date(s) {
  return String(s)
    .replace(new RegExp(M + " (\\d{1,2}), (\\d{4})", "g"), (_, m, d, y) => `${d} de ${MON[m]} de ${y}`)
    .replace(new RegExp(M + " (\\d{1,2})[–-](\\d{1,2})\\b", "g"), (_, m, a, b) => `${a}–${b} de ${MON[m]}`)
    .replace(new RegExp(M + " (\\d{1,2})[–-]" + M + " (\\d{1,2})", "g"), (_, m1, a, m2, b) => `${a} de ${MON[m1]}–${b} de ${MON[m2]}`)
    .replace(new RegExp(M + " (\\d{1,2})\\b", "g"), (_, m, d) => `${d} de ${MON[m]}`);
}
/** "15% off" → "15% de descuento"; "$5.00 off" → "$5.00 de descuento" */
function off(s) { return String(s).replace(/ off$/, " de descuento").replace(/^a little something off$/, "un descuentito"); }
/** "1 hour" → "1 hora"; "30 minutes" → "30 minutos" */
function dur(s) { return String(s).replace(/\b1 hour\b/, "1 hora").replace(/(\d+) hours/, "$1 horas").replace(/(\d+) minutes/, "$1 minutos"); }
const ord = (n) => (n === "your order" ? "tu pedido" : n);
const ped = (n) => (n === "your order" ? "de tu pedido" : "del pedido " + n);
const pl = (k, one, many) => `${k} ${k === "1" ? one : many}`;
const COL = {
  "USA Places": "Lugares de EE. UU.", "World Places": "Lugares del Mundo", "Ink Cities": "Ciudades en Tinta", "City Sketches": "Ciudades en Trazo",
  "Fall": "Otoño", "Horror Classics": "Clásicos del Terror", "Furry Friends": "Amigos Peludos", "Kitchen Words": "Frases de Cocina",
  "Ireland": "Irlanda", "Pilipinas": "Filipinas", "Korea": "Corea", "Japan": "Japón", "Greece": "Grecia", "France": "Francia",
  "Great Masters": "Grandes Maestros", "Mythology": "Mitología", "Home Notes": "Notitas de Casa", "Night Sky": "Cielo Nocturno",
  "Birth Flowers": "Flores del Mes", "Storybook Classics": "Clásicos de la Literatura", "Fairy Tales & Myths": "Cuentos de Hadas y Mitos",
  "Wise Words": "Palabras Sabias", "Holidays & Dates": "Fechas Especiales", "Bumper Stickers": "Calcomanías de Defensa",
  "Christmas": "Navidad", "Summer": "Verano", "Heritage": "Raíces",
};
const DATE_ONLY = new RegExp("^(about )?" + M + " \\d{1,2}([–-](" + M + " )?\\d{1,2})?(, \\d{4})?$");
const P = [
  [/^Here's everything that's coming your way, ordered (.+)\.$/, (_, d) => `Aquí está todo lo que va en camino, pedido el ${date(d)}.`],
  [/^Here's everything that's coming your way\.$/, "Aquí está todo lo que va en camino."],
  [/^(\d+) magnets? coming your way\. We'll start making them by hand right away\.$/, (_, n) => `${pl(n, "imán", "imanes")} en camino. Empezamos a hacerlos a mano ahora mismo.`],
  [/^Thank you! Order (.+) is confirmed$/, "¡Gracias! El pedido $1 está confirmado"],
  [/^Estimated arrival: about 1 to 2 weeks after you approve the proof$/, "Llegada estimada: más o menos de 1 a 2 semanas después de que apruebes la prueba"],
  [/^Estimated arrival: (.+)$/, (_, d) => `Llegada estimada: ${d.startsWith("about ") ? "alrededor del " + date(d.slice(6)) : date(d)}`],
  [/^Your magnets are on the way!( \((.+)\))?$/, (_, x, n) => `¡Tus imanes van en camino!${n ? ` (${n})` : ""}`],
  [/^(.+?)( tracking (.+))?\. Follow your package all the way to your door\.$/, (_, c, x, t) => `${c}${t ? `, rastreo ${t}` : ""}. Sigue tu paquete hasta tu puerta.`],
  [/^Charged to your card today, when your order shipped( \(order (.+)\))?\. Keep this email as your receipt\.$/, (_, x, n) => `Cobrado hoy a tu tarjeta, cuando salió tu pedido${n ? ` (pedido ${n})` : ""}. Guarda este correo como recibo.`],
  [/^Carrier: (.+)$/, "Transportista: $1"],
  [/^Tracking number: see the tracking page$/, "Número de rastreo: mira la página de rastreo"],
  [/^Tracking number: (.+)$/, "Número de rastreo: $1"],
  [/^Order (.+) · Out for delivery$/, "Pedido $1 · Salió a entrega"],
  [/^Order (.+) · Delivered$/, "Pedido $1 · Entregado"],
  [/^(.+), your magnets arrive today!$/, "¡$1, tus imanes llegan hoy!"],
  [/^(.+) has your package out for delivery\. Keep an eye on the porch and the mailbox\.$/, "$1 ya salió a entregar tu paquete. Pendiente de la puerta y del buzón."],
  [/^(.+) has your package out for delivery( \(order (.+)\))?\. Keep an eye on the porch!$/, (_, c, x, n) => `${c} ya salió a entregar tu paquete${n ? ` (pedido ${n})` : ""}. ¡Pendiente de la puerta!`],
  [/^Latest scan: (.+)$/, "Última actualización: $1"],
  [/^(.+), how do they look on your fridge\?$/, "$1, ¿cómo se ven en tu refri?"],
  [/^for your next order: (.+?) until (.+)\.$/, (_, o, d) => `en tu próximo pedido: ${off(o)} hasta el ${date(d)}.`],
  [/^for your next order: (.+)\.$/, (_, o) => `en tu próximo pedido: ${off(o)}.`],
  [/^Show us your fridge! Share a photo on Instagram and tag (.+)$/, "¡Muéstranos tu refri! Comparte una foto en Instagram y etiqueta a $1"],
  [/^Return · (.+)$/, "Devolución · $1"],
  [/^Hi (.+?)[.!]$/, "¡Hola, $1!"],
  [/^Your return label for (.+)$/, (_, n) => `Tu etiqueta de devolución de ${ord(n)}`],
  [/^We got your return request \((.+)\)$/, (_, n) => `Recibimos tu solicitud de devolución (${ord(n)})`],
  [/^We're reprinting your magnets \((.+)\)$/, (_, n) => `Estamos reimprimiendo tus imanes (${ord(n)})`],
  [/^About your return for (.+)$/, (_, n) => `Sobre tu devolución de ${ord(n)}`],
  [/^No printer\? Show this QR code at the Post Office: (.+)$/, "¿No tienes impresora? Muestra este código QR en la oficina de correos: $1"],
  [/^In this return:\n([\s\S]+)$/, "En esta devolución:\n$1"],
  [/^A note from us: ([\s\S]+)$/, "Una nota de nuestra parte: $1"],
  [/^A partial refund of (\$[\d.,]+) for (.+)$/, (_, a, n) => `Un reembolso parcial de ${a} ${ped(n)}`],
  [/^Your refund for (.+) is on its way$/, (_, n) => `El reembolso ${ped(n)} va en camino`],
  [/^(\$[\d.,]+) is heading back to you\. Banks usually show it within 5 to 10 business days\.$/, "$1 va de regreso a ti. Los bancos normalmente lo muestran en 5 a 10 días hábiles."],
  [/^(Full|Partial) refund: (\$[\d.,]+)(.*)$/, (_, k, a, rest) => `${k === "Full" ? "Reembolso total" : "Reembolso parcial"}: ${a}${rest.replace(/order/g, "pedido")}`],
  [/^Back to your original payment method( for order (.+))?$/, (_, x, n) => `De vuelta a tu método de pago original${n ? ` del pedido ${n}` : ""}`],
  [/^Refunded on this order so far: (\$[\d.,]+) of (\$[\d.,]+)\.$/, "Reembolsado en este pedido hasta ahora: $1 de $2."],
  [/^Welcome to the hive, (.+)!$/, "¡Bienvenido a la colmena, $1!"],
  [/^(\d+% off|\$[\d.,]+ off|a little something off) your first order(,? until (.+?))?\.?$/, (_, o, x, d) => `${off(o)} en tu primer pedido${d ? ` hasta el ${date(d)}` : ""}.`],
  [/^Your account is ready, and (.+) your first order is waiting\.$/, (_, o) => `Tu cuenta está lista, y te espera ${off(o)} en tu primer pedido.`],
  [/^Thanks for joining! Here's (.+) your first order\.$/, (_, o) => `¡Gracias por unirte! Aquí tienes ${off(o)} en tu primer pedido.`],
  [/^One quick tap, (.+)!$/, "¡Solo un toque, $1!"],
  [/^For your security this link expires in (.+) and works only once\. If it has expired, you can$/, (_, e) => `Por seguridad, este enlace vence en ${dur(e)} y solo funciona una vez. Si ya venció, puedes`],
  [/^Tap the button to choose a new password\. The link works for (.+)\.$/, (_, e) => `Toca el botón para elegir una contraseña nueva. El enlace funciona por ${dur(e)}.`],
  [/^(.+), your magnets are still waiting$/, "$1, tus imanes todavía te esperan"],
  [/^We saved your (\d+) magnets?\. Pick up right where you left off\.$/, (_, n) => `Guardamos ${n === "1" ? "tu imán" : `tus ${n} imanes`}. Sigue justo donde te quedaste.`],
  [/^Thanks for writing, (.+)!$/, "¡Gracias por escribir, $1!"],
  [/^You wrote · (.+)$/, (_, t) => `Escribiste · ${look(t) || t}`],
  [/^Thanks! We'll reply within 1 business day with ideas, a price for (\d+) magnets and next steps\.$/, "¡Gracias! Te respondemos en 1 día hábil con ideas, el precio de $1 imanes y los siguientes pasos."],
  [/^Thanks! We'll reply within 1 business day with ideas, a price and next steps\.$/, "¡Gracias! Te respondemos en 1 día hábil con ideas, un precio y los siguientes pasos."],
  [/^Here's your link, (.+)$/, "Aquí está tu enlace, $1"],
  [/^Your payment link for (.+)$/, "Tu enlace de pago: $1"],
  [/^(\$[\d.,]+) for (.+)\. Pay securely by card, Apple Pay or Google Pay\.$/, "$1 por $2. Paga de forma segura con tarjeta, Apple Pay o Google Pay."],
  [/^Payments are processed by Stripe\. We never see or store your card number\.( This link works until (.+)\.)?$/, (_, x, d) => `Los pagos los procesa Stripe. Nunca vemos ni guardamos el número de tu tarjeta.${d ? ` Este enlace funciona hasta el ${date(d)}.` : ""}`],
  // the Stripe checkout page (functions/checkout.js)
  [/^(\d+) custom photo magnets, 2 × 2 in$/, "$1 imanes con foto personalizados, 2 × 2 pulg. (5 cm)"],
  [/^(\d+) custom magnets\. We email you about your design after checkout\.$/, "$1 imanes personalizados. Después del pago te escribimos sobre tu diseño."],
  [/^(.+) discount included$/, "descuento de $1 incluido"],
  [/^(\d+) photo magnets$/, "$1 imanes con foto"],
  [/^(\d+) photos?$/, (_, n) => pl(n, "foto", "fotos")],
  [/^(\d+) frames$/, "$1 marcos"],
  [/^(\d+) packs$/, "$1 paquetes"],
  [/^(.+) frame$/, (_, f) => `Marco ${(look(f) || f).toLowerCase()}`],
  [/^(.+) magnet$/, "Imán $1"],
  [DATE_ONLY, (s) => (s.startsWith("about ") ? "alrededor del " + date(s.slice(6)) : date(s))],
  [/^Good news, (.+)!$/, "¡Buenas noticias, $1!"],
  [/^Thank you, (.+)!$/, "¡Gracias, $1!"],
  [/^Thanks, (.+)!$/, "¡Gracias, $1!"],
  [/^Hi (.+),$/, "Hola, $1:"],
  [/^Order (LHH-\d+)$/, "Pedido $1"],
  [/^Qty (\d+)$/, "Cant. $1"],
  [/^(\d+) magnets( × (\d+))?$/, (_, n, x, q) => `${n} imanes${q ? ` × ${q}` : ""}`],
  [/^Volume discount \((\d+)% off\)$/, "Descuento por cantidad ($1% de descuento)"],
  [/^Promo code (.+)$/, "Código $1"],
  [/^(.+), (\d+)% off$/, "$1, $2% de descuento"],
  [/^(.+), (\d+) designs? free$/, (_, n, k) => `${n}, ${pl(k, "diseño gratis", "diseños gratis")}`],
  [/^Captions: (.+)$/, "Textos: $1"],
  [/^Note: (.+)$/, "Nota: $1"],
];
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
module.exports = { look, date };
