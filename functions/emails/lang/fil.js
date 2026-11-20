// Little Hive House emails (and the Stripe checkout page) in Tagalog, the everyday Filipino-American way
// (common English shop words kept: order, cart, shipping, magnet, refund).
// look(key): the exact dictionary (functions/emails/fil.json), the collection names, then the patterns below.
"use strict";

let DICT = null;
function dict() {
  if (!DICT) { try { DICT = require("../fil.json"); } catch (e) { DICT = {}; } }
  return DICT;
}
const MON = { Jan: "Ene", Feb: "Peb", Mar: "Mar", Apr: "Abr", May: "May", Jun: "Hun", Jul: "Hul", Aug: "Ago", Sep: "Set", Oct: "Okt", Nov: "Nob", Dec: "Dis",
  January: "Enero", February: "Pebrero", March: "Marso", April: "Abril", June: "Hunyo", July: "Hulyo", August: "Agosto",
  September: "Setyembre", October: "Oktubre", November: "Nobyembre", December: "Disyembre" };
const M = "(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)";
/** Tagalog writes dates like English, with its own month names: "Nov 17–20" → "Nob 17–20" */
function date(s) { return String(s).replace(new RegExp("\\b" + M + "\\b(?= \\d)", "g"), (m) => MON[m]); }
/** "15% off" stays; "a little something off" → "kaunting discount" */
function off(s) { return String(s).replace(/^a little something off$/, "kaunting discount"); }
/** "1 hour" → "1 oras"; "30 minutes" → "30 minuto" */
function dur(s) { return String(s).replace(/\b1 hour\b/, "1 oras").replace(/(\d+) hours/, "$1 oras").replace(/(\d+) minutes/, "$1 minuto"); }
const ord = (n) => (n === "your order" ? "ng order mo" : "ng order " + n);
const COL = {
  "USA Places": "Mga Lugar sa USA", "World Places": "Mga Lugar sa Mundo", "Ink Cities": "Mga Lungsod sa Tinta", "City Sketches": "Sketch ng mga Lungsod",
  "Fall": "Taglagas", "Horror Classics": "Klasikong Katatakutan", "Furry Friends": "Mga Mabalahibong Kaibigan", "Kitchen Words": "Mga Salita sa Kusina",
  "Italia": "Italya", "Great Masters": "Mga Dakilang Pintor", "Mythology": "Mitolohiya", "Home Notes": "Mga Paalala sa Bahay",
  "Night Sky": "Langit sa Gabi", "Birth Flowers": "Bulaklak ng Kapanganakan", "Storybook Classics": "Klasikong Kuwento",
  "Fairy Tales & Myths": "Mga Engkanto at Mito", "Wise Words": "Matatalinong Salita", "Holidays & Dates": "Mga Okasyon at Petsa",
  "Christmas": "Pasko", "Summer": "Tag-init", "Heritage": "Pinagmulan",
};
const DATE_ONLY = new RegExp("^(about )?" + M + " \\d{1,2}([–-](" + M + " )?\\d{1,2})?(, \\d{4})?$");
const P = [
  [/^Here's everything that's coming your way, ordered (.+)\.$/, (_, d) => `Narito ang lahat ng papunta sa iyo, inorder noong ${date(d)}.`],
  [/^Here's everything that's coming your way\.$/, "Narito ang lahat ng papunta sa iyo."],
  [/^(\d+) magnets? coming your way\. We'll start making them by hand right away\.$/, "$1 magnet ang papunta sa iyo. Sisimulan na namin itong gawin nang kamay."],
  [/^Thank you! Order (.+) is confirmed$/, "Salamat! Kumpirmado na ang order $1"],
  [/^Estimated arrival: about 1 to 2 weeks after you approve the proof$/, "Tinatayang pagdating: mga 1 hanggang 2 linggo pagkatapos mong aprubahan ang proof"],
  [/^Estimated arrival: (.+)$/, (_, d) => `Tinatayang pagdating: ${d.startsWith("about ") ? "bandang " + date(d.slice(6)) : date(d)}`],
  [/^Your magnets are on the way!( \((.+)\))?$/, (_, x, n) => `Papunta na ang mga magnet mo!${n ? ` (${n})` : ""}`],
  [/^(.+?)( tracking (.+))?\. Follow your package all the way to your door\.$/, (_, c, x, t) => `${c}${t ? `, tracking ${t}` : ""}. Subaybayan ang package mo hanggang sa pinto mo.`],
  [/^Charged to your card today, when your order shipped( \(order (.+)\))?\. Keep this email as your receipt\.$/, (_, x, n) => `Siningil sa card mo ngayon, nang maipadala ang order mo${n ? ` (order ${n})` : ""}. Itago ang email na ito bilang resibo.`],
  [/^Carrier: (.+)$/, "Carrier: $1"],
  [/^Tracking number: see the tracking page$/, "Tracking number: tingnan ang tracking page"],
  [/^Tracking number: (.+)$/, "Tracking number: $1"],
  [/^Order (.+) · Out for delivery$/, "Order $1 · Ihahatid na"],
  [/^Order (.+) · Delivered$/, "Order $1 · Naihatid"],
  [/^(.+), your magnets arrive today!$/, "$1, darating ngayon ang mga magnet mo!"],
  [/^(.+) has your package out for delivery\. Keep an eye on the porch and the mailbox\.$/, "Ihahatid na ng $1 ang package mo. Bantayan ang pinto at ang mailbox."],
  [/^(.+) has your package out for delivery( \(order (.+)\))?\. Keep an eye on the porch!$/, (_, c, x, n) => `Ihahatid na ng ${c} ang package mo${n ? ` (order ${n})` : ""}. Bantayan ang pinto!`],
  [/^Latest scan: (.+)$/, "Pinakabagong scan: $1"],
  [/^(.+), how do they look on your fridge\?$/, "$1, kumusta sila sa ref mo?"],
  [/^for your next order: (.+?) until (.+)\.$/, (_, o, d) => `para sa susunod mong order: ${off(o)} hanggang ${date(d)}.`],
  [/^for your next order: (.+)\.$/, (_, o) => `para sa susunod mong order: ${off(o)}.`],
  [/^Show us your fridge! Share a photo on Instagram and tag (.+)$/, "Ipakita sa amin ang ref mo! Magbahagi ng litrato sa Instagram at i-tag ang $1"],
  [/^Return · (.+)$/, "Return · $1"],
  [/^Hi (.+?)[.!]$/, "Hi $1!"],
  [/^Your return label for (.+)$/, (_, n) => `Ang return label ${ord(n)}`],
  [/^We got your return request \((.+)\)$/, (_, n) => `Natanggap namin ang return request mo (${n === "your order" ? "order mo" : n})`],
  [/^We're reprinting your magnets \((.+)\)$/, (_, n) => `Ipi-print namin ulit ang mga magnet mo (${n === "your order" ? "order mo" : n})`],
  [/^About your return for (.+)$/, (_, n) => `Tungkol sa return ${ord(n)}`],
  [/^No printer\? Show this QR code at the Post Office: (.+)$/, "Walang printer? Ipakita ang QR code na ito sa Post Office: $1"],
  [/^In this return:\n([\s\S]+)$/, "Sa return na ito:\n$1"],
  [/^A note from us: ([\s\S]+)$/, "Isang mensahe mula sa amin: $1"],
  [/^A partial refund of (\$[\d.,]+) for (.+)$/, (_, a, n) => `Bahagyang refund na ${a} para sa ${n === "your order" ? "order mo" : "order " + n}`],
  [/^Your refund for (.+) is on its way$/, (_, n) => `Papunta na ang refund mo para sa ${n === "your order" ? "order mo" : "order " + n}`],
  [/^(\$[\d.,]+) is heading back to you\. Banks usually show it within 5 to 10 business days\.$/, "Pabalik na sa iyo ang $1. Karaniwang ipinapakita ito ng bangko sa loob ng 5 hanggang 10 business day."],
  [/^(Full|Partial) refund: (\$[\d.,]+)(.*)$/, (_, k, a, rest) => `${k === "Full" ? "Buong refund" : "Bahagyang refund"}: ${a}${rest.replace(/ for order /g, " para sa order ")}`],
  [/^Back to your original payment method( for order (.+))?$/, (_, x, n) => `Ibinalik sa orihinal mong paraan ng pagbayad${n ? ` para sa order ${n}` : ""}`],
  [/^Refunded on this order so far: (\$[\d.,]+) of (\$[\d.,]+)\.$/, "Na-refund sa order na ito sa ngayon: $1 sa $2."],
  [/^Welcome to the hive, (.+)!$/, "Maligayang pagdating sa bahay-pukyutan, $1!"],
  [/^(\d+% off|\$[\d.,]+ off|a little something off) your first order( until (.+))?\.?$/, (_, o, x, d) => `${off(o)} sa unang order mo${d ? ` hanggang ${date(d)}` : ""}.`],
  [/^Your account is ready, and (.+) your first order is waiting\.$/, (_, o) => `Handa na ang account mo, at naghihintay ang ${off(o)} sa unang order mo.`],
  [/^Thanks for joining! Here's (.+) your first order\.$/, (_, o) => `Salamat sa pagsali! Narito ang ${off(o)} sa unang order mo.`],
  [/^One quick tap, (.+)!$/, "Isang mabilis na tap, $1!"],
  [/^For your security this link expires in (.+) and works only once\. If it has expired, you can$/, (_, e) => `Para sa seguridad mo, mag-e-expire ang link na ito sa loob ng ${dur(e)} at isang beses lang gagana. Kung expired na, puwede kang`],
  [/^Tap the button to choose a new password\. The link works for (.+)\.$/, (_, e) => `I-tap ang button para pumili ng bagong password. Gagana ang link sa loob ng ${dur(e)}.`],
  [/^(.+), your magnets are still waiting$/, "$1, naghihintay pa rin ang mga magnet mo"],
  [/^We saved your (\d+) magnets?\. Pick up right where you left off\.$/, "Na-save namin ang $1 magnet mo. Ituloy kung saan ka huminto."],
  [/^Thanks for writing, (.+)!$/, "Salamat sa pagsulat, $1!"],
  [/^You wrote · (.+)$/, (_, t) => `Isinulat mo · ${look(t) || t}`],
  [/^Thanks! We'll reply within 1 business day with ideas, a price for (\d+) magnets and next steps\.$/, "Salamat! Sasagot kami sa loob ng 1 business day na may mga ideya, presyo para sa $1 magnet at susunod na hakbang."],
  [/^Thanks! We'll reply within 1 business day with ideas, a price and next steps\.$/, "Salamat! Sasagot kami sa loob ng 1 business day na may mga ideya, presyo at susunod na hakbang."],
  [/^Here's your link, (.+)$/, "Narito ang link mo, $1"],
  [/^Your payment link for (.+)$/, "Ang payment link mo para sa $1"],
  [/^(\$[\d.,]+) for (.+)\. Pay securely by card, Apple Pay or Google Pay\.$/, "$1 para sa $2. Magbayad nang ligtas gamit ang card, Apple Pay o Google Pay."],
  [/^Payments are processed by Stripe\. We never see or store your card number\.( This link works until (.+)\.)?$/, (_, x, d) => `Stripe ang nagpoproseso ng bayad. Hindi namin kailanman nakikita o itinatago ang card number mo.${d ? ` Gagana ang link na ito hanggang ${date(d)}.` : ""}`],
  // the Stripe checkout page (functions/checkout.js)
  [/^(\d+) custom photo magnets, 2 × 2 in$/, "$1 custom na photo magnet, 2 × 2 pulgada (5 cm)"],
  [/^(\d+) custom magnets\. We email you about your design after checkout\.$/, "$1 custom na magnet. Mag-e-email kami tungkol sa disenyo mo pagkatapos ng checkout."],
  [/^(.+) discount included$/, "kasama na ang $1 discount"],
  [/^(\d+) photo magnets$/, "$1 photo magnet"],
  [/^(\d+) photos?$/, "$1 litrato"],
  [/^(\d+) frames$/, "$1 frame"],
  [/^(\d+) packs$/, "$1 pack"],
  [/^(.+) frame$/, (_, f) => `Frame na ${look(f) || f}`],
  [/^(.+) magnet$/, "$1 magnet"],
  [DATE_ONLY, (s) => (s.startsWith("about ") ? "bandang " + date(s.slice(6)) : date(s))],
  [/^Good news, (.+)!$/, "Magandang balita, $1!"],
  [/^Thank you, (.+)!$/, "Salamat, $1!"],
  [/^Thanks, (.+)!$/, "Salamat, $1!"],
  [/^Hi (.+),$/, "Hi $1,"],
  [/^Order (LHH-\d+)$/, "Order $1"],
  [/^Qty (\d+)$/, "Dami $1"],
  [/^(\d+) magnets( × (\d+))?$/, (_, n, x, q) => `${n} magnet${q ? ` × ${q}` : ""}`],
  [/^Volume discount \((\d+)% off\)$/, "Discount sa dami ($1% off)"],
  [/^Promo code (.+)$/, "Promo code $1"],
  [/^(.+), (\d+)% off$/, "$1, $2% off"],
  [/^(.+), (\d+) designs? free$/, "$1, $2 libreng disenyo"],
  [/^Captions: (.+)$/, "Mga caption: $1"],
  [/^Note: (.+)$/, "Note: $1"],
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
