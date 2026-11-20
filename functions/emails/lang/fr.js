// Little Hive House emails (and the Stripe checkout page) in French, "vous"; prices stay in the US format ($5.49).
// look(key): the exact dictionary (functions/emails/fr.json), the collection names, then the patterns below.
"use strict";

let DICT = null;
function dict() {
  if (!DICT) { try { DICT = require("../fr.json"); } catch (e) { DICT = {}; } }
  return DICT;
}
const MON = { Jan: "janv.", Feb: "févr.", Mar: "mars", Apr: "avr.", May: "mai", Jun: "juin", Jul: "juil.", Aug: "août", Sep: "sept.", Oct: "oct.", Nov: "nov.", Dec: "déc.",
  January: "janvier", February: "février", March: "mars", April: "avril", June: "juin", July: "juillet", August: "août",
  September: "septembre", October: "octobre", November: "novembre", December: "décembre" };
const M = "(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)";
/** "Nov 17–20" → "17–20 nov."; "Nov 28–Dec 2" → "28 nov.–2 déc."; "November 3, 2026" → "3 novembre 2026" */
function date(s) {
  return String(s)
    .replace(new RegExp(M + " (\\d{1,2}), (\\d{4})", "g"), (_, m, d, y) => `${d} ${MON[m]} ${y}`)
    .replace(new RegExp(M + " (\\d{1,2})[–-](\\d{1,2})\\b", "g"), (_, m, a, b) => `${a}–${b} ${MON[m]}`)
    .replace(new RegExp(M + " (\\d{1,2})[–-]" + M + " (\\d{1,2})", "g"), (_, m1, a, m2, b) => `${a} ${MON[m1]}–${b} ${MON[m2]}`)
    .replace(new RegExp(M + " (\\d{1,2})\\b", "g"), (_, m, d) => `${d} ${MON[m]}`);
}
/** "15% off" → "-15 %"; "$5.00 off" → "$5.00 de réduction" */
function off(s) {
  s = String(s);
  let m = /^(\d+)% off$/.exec(s); if (m) return `-${m[1]} %`;
  m = /^(\$[\d.,]+) off$/.exec(s); if (m) return `${m[1]} de réduction`;
  return s === "a little something off" ? "une petite réduction" : s;
}
/** "1 hour" → "1 heure"; "30 minutes" → "30 minutes" */
function dur(s) { return String(s).replace(/\b1 hour\b/, "1 heure").replace(/(\d+) hours/, "$1 heures"); }
const ord = (n) => (n === "your order" ? "votre commande" : "la commande " + n);
const COL = {
  "USA Places": "Lieux des États-Unis", "World Places": "Lieux du monde", "Ink Cities": "Villes à l'encre", "City Sketches": "Croquis de villes",
  "Fall": "Automne", "Horror Classics": "Classiques de l'horreur", "Furry Friends": "Amis à poils", "Kitchen Words": "Mots de cuisine",
  "México": "Mexique", "Ireland": "Irlande", "Italia": "Italie", "Puerto Rico": "Porto Rico", "Pilipinas": "Philippines", "India": "Inde",
  "Korea": "Corée", "Japan": "Japon", "Brasil": "Brésil", "Greece": "Grèce", "Great Masters": "Grands maîtres", "Mythology": "Mythologie",
  "Home Notes": "Petits mots de la maison", "Night Sky": "Ciel nocturne", "Birth Flowers": "Fleurs de naissance",
  "Storybook Classics": "Classiques de la littérature", "Fairy Tales & Myths": "Contes et mythes", "Wise Words": "Paroles de sagesse",
  "Holidays & Dates": "Fêtes et dates", "Bumper Stickers": "Autocollants de pare-chocs", "Christmas": "Noël", "Summer": "Été", "Heritage": "Racines",
};
const DATE_ONLY = new RegExp("^(about )?" + M + " \\d{1,2}([–-](" + M + " )?\\d{1,2})?(, \\d{4})?$");
const P = [
  [/^Here's everything that's coming your way, ordered (.+)\.$/, (_, d) => `Voici tout ce qui arrive chez vous, commandé le ${date(d)}.`],
  [/^Here's everything that's coming your way\.$/, "Voici tout ce qui arrive chez vous."],
  [/^(\d+) magnets? coming your way\. We'll start making them by hand right away\.$/, (_, n) => `${n} ${n === "1" ? "aimant arrive" : "aimants arrivent"} chez vous. Nous commençons à les fabriquer à la main tout de suite.`],
  [/^Thank you! Order (.+) is confirmed$/, "Merci ! La commande $1 est confirmée"],
  [/^Estimated arrival: about 1 to 2 weeks after you approve the proof$/, "Arrivée estimée : environ 1 à 2 semaines après validation de l'épreuve"],
  [/^Estimated arrival: (.+)$/, (_, d) => `Arrivée estimée : ${d.startsWith("about ") ? "vers le " + date(d.slice(6)) : date(d)}`],
  [/^Your magnets are on the way!( \((.+)\))?$/, (_, x, n) => `Vos aimants sont en route !${n ? ` (${n})` : ""}`],
  [/^(.+?)( tracking (.+))?\. Follow your package all the way to your door\.$/, (_, c, x, t) => `${c}${t ? `, suivi ${t}` : ""}. Suivez votre colis jusqu'à votre porte.`],
  [/^Charged to your card today, when your order shipped( \(order (.+)\))?\. Keep this email as your receipt\.$/, (_, x, n) => `Débité aujourd'hui sur votre carte, à l'expédition de votre commande${n ? ` (commande ${n})` : ""}. Gardez cet e-mail comme reçu.`],
  [/^Carrier: (.+)$/, "Transporteur : $1"],
  [/^Tracking number: see the tracking page$/, "Numéro de suivi : voir la page de suivi"],
  [/^Tracking number: (.+)$/, "Numéro de suivi : $1"],
  [/^Order (.+) · Out for delivery$/, "Commande $1 · En cours de livraison"],
  [/^Order (.+) · Delivered$/, "Commande $1 · Livrée"],
  [/^(.+), your magnets arrive today!$/, "$1, vos aimants arrivent aujourd'hui !"],
  [/^(.+) has your package out for delivery\. Keep an eye on the porch and the mailbox\.$/, "$1 est en train de livrer votre colis. Surveillez la porte et la boîte aux lettres."],
  [/^(.+) has your package out for delivery( \(order (.+)\))?\. Keep an eye on the porch!$/, (_, c, x, n) => `${c} est en train de livrer votre colis${n ? ` (commande ${n})` : ""}. Surveillez la porte !`],
  [/^Latest scan: (.+)$/, "Dernier scan : $1"],
  [/^(.+), how do they look on your fridge\?$/, "$1, ils rendent comment sur votre frigo ?"],
  [/^for your next order: (.+?) until (.+)\.$/, (_, o, d) => `sur votre prochaine commande : ${off(o)} jusqu'au ${date(d)}.`],
  [/^for your next order: (.+)\.$/, (_, o) => `sur votre prochaine commande : ${off(o)}.`],
  [/^Show us your fridge! Share a photo on Instagram and tag (.+)$/, "Montrez-nous votre frigo ! Partagez une photo sur Instagram et identifiez $1"],
  [/^Return · (.+)$/, "Retour · $1"],
  [/^Hi (.+?)[.!]$/, "Bonjour $1 !"],
  [/^Your return label for (.+)$/, (_, n) => `Votre étiquette de retour pour ${ord(n)}`],
  [/^We got your return request \((.+)\)$/, (_, n) => `Nous avons reçu votre demande de retour (${n === "your order" ? "votre commande" : "commande " + n})`],
  [/^We're reprinting your magnets \((.+)\)$/, (_, n) => `Nous réimprimons vos aimants (${n === "your order" ? "votre commande" : "commande " + n})`],
  [/^About your return for (.+)$/, (_, n) => `À propos de votre retour pour ${ord(n)}`],
  [/^No printer\? Show this QR code at the Post Office: (.+)$/, "Pas d'imprimante ? Montrez ce QR code à la poste : $1"],
  [/^In this return:\n([\s\S]+)$/, "Dans ce retour :\n$1"],
  [/^A note from us: ([\s\S]+)$/, "Un mot de notre part : $1"],
  [/^A partial refund of (\$[\d.,]+) for (.+)$/, (_, a, n) => `Un remboursement partiel de ${a} pour ${ord(n)}`],
  [/^Your refund for (.+) is on its way$/, (_, n) => `Votre remboursement pour ${ord(n)} est en route`],
  [/^(\$[\d.,]+) is heading back to you\. Banks usually show it within 5 to 10 business days\.$/, "$1 vous revient. Les banques l'affichent généralement sous 5 à 10 jours ouvrés."],
  [/^(Full|Partial) refund: (\$[\d.,]+)(.*)$/, (_, k, a, rest) => `${k === "Full" ? "Remboursement intégral" : "Remboursement partiel"} : ${a}${rest.replace(/ for order /g, " pour la commande ")}`],
  [/^Back to your original payment method( for order (.+))?$/, (_, x, n) => `Sur votre moyen de paiement d'origine${n ? ` pour la commande ${n}` : ""}`],
  [/^Refunded on this order so far: (\$[\d.,]+) of (\$[\d.,]+)\.$/, "Remboursé sur cette commande jusqu'ici : $1 sur $2."],
  [/^Welcome to the hive, (.+)!$/, "Bienvenue dans la ruche, $1 !"],
  [/^(\d+% off|\$[\d.,]+ off|a little something off) your first order( until (.+))?\.?$/, (_, o, x, d) => `${off(o)} sur votre première commande${d ? ` jusqu'au ${date(d)}` : ""}.`],
  [/^Your account is ready, and (.+) your first order is waiting\.$/, (_, o) => `Votre compte est prêt, et ${off(o)} sur votre première commande vous attend.`],
  [/^Thanks for joining! Here's (.+) your first order\.$/, (_, o) => `Merci de votre inscription ! Voici ${off(o)} sur votre première commande.`],
  [/^One quick tap, (.+)!$/, "Un petit geste, $1 !"],
  [/^For your security this link expires in (.+) and works only once\. If it has expired, you can$/, (_, e) => `Pour votre sécurité, ce lien expire dans ${dur(e)} et ne fonctionne qu'une fois. S'il a expiré, vous pouvez`],
  [/^Tap the button to choose a new password\. The link works for (.+)\.$/, (_, e) => `Touchez le bouton pour choisir un nouveau mot de passe. Le lien est valable ${dur(e)}.`],
  [/^(.+), your magnets are still waiting$/, "$1, vos aimants vous attendent toujours"],
  [/^We saved your (\d+) magnets?\. Pick up right where you left off\.$/, (_, n) => `Nous avons gardé ${n === "1" ? "votre aimant" : `vos ${n} aimants`}. Reprenez là où vous en étiez.`],
  [/^Thanks for writing, (.+)!$/, "Merci de nous avoir écrit, $1 !"],
  [/^You wrote · (.+)$/, (_, t) => `Vous avez écrit · ${look(t) || t}`],
  [/^Thanks! We'll reply within 1 business day with ideas, a price for (\d+) magnets and next steps\.$/, "Merci ! Nous répondrons sous 1 jour ouvré avec des idées, un prix pour $1 aimants et la suite."],
  [/^Thanks! We'll reply within 1 business day with ideas, a price and next steps\.$/, "Merci ! Nous répondrons sous 1 jour ouvré avec des idées, un prix et la suite."],
  [/^Here's your link, (.+)$/, "Voici votre lien, $1"],
  [/^Your payment link for (.+)$/, "Votre lien de paiement pour $1"],
  [/^(\$[\d.,]+) for (.+)\. Pay securely by card, Apple Pay or Google Pay\.$/, "$1 pour $2. Payez en toute sécurité par carte, Apple Pay ou Google Pay."],
  [/^Payments are processed by Stripe\. We never see or store your card number\.( This link works until (.+)\.)?$/, (_, x, d) => `Les paiements sont traités par Stripe. Nous ne voyons ni ne conservons jamais votre numéro de carte.${d ? ` Ce lien est valable jusqu'au ${date(d)}.` : ""}`],
  // the Stripe checkout page (functions/checkout.js)
  [/^(\d+) custom photo magnets, 2 × 2 in$/, "$1 aimants photo personnalisés, 5 × 5 cm"],
  [/^(\d+) custom magnets\. We email you about your design after checkout\.$/, "$1 aimants sur mesure. Nous vous écrivons au sujet du design après le paiement."],
  [/^(.+) discount included$/, "remise $1 incluse"],
  [/^(\d+) photo magnets$/, "$1 aimants photo"],
  [/^(\d+) photos?$/, (_, n) => `${n} ${n === "1" ? "photo" : "photos"}`],
  [/^(\d+) frames$/, "$1 cadres"],
  [/^(\d+) packs$/, "$1 lots"],
  [/^(.+) frame$/, (_, f) => `Cadre ${(look(f) || f).toLowerCase()}`],
  [/^(.+) magnet$/, "Aimant $1"],
  [DATE_ONLY, (s) => (s.startsWith("about ") ? "vers le " + date(s.slice(6)) : date(s))],
  [/^Good news, (.+)!$/, "Bonne nouvelle, $1 !"],
  [/^Thank you, (.+)!$/, "Merci, $1 !"],
  [/^Thanks, (.+)!$/, "Merci, $1 !"],
  [/^Hi (.+),$/, "Bonjour $1,"],
  [/^Order (LHH-\d+)$/, "Commande $1"],
  [/^Qty (\d+)$/, "Qté $1"],
  [/^(\d+) magnets( × (\d+))?$/, (_, n, x, q) => `${n} aimants${q ? ` × ${q}` : ""}`],
  [/^Volume discount \((\d+)% off\)$/, "Remise quantité (-$1 %)"],
  [/^Promo code (.+)$/, "Code promo $1"],
  [/^(.+), (\d+)% off$/, "$1, -$2 %"],
  [/^(.+), (\d+) designs? free$/, (_, n, k) => `${n}, ${k} ${k === "1" ? "modèle offert" : "modèles offerts"}`],
  [/^Captions: (.+)$/, "Légendes : $1"],
  [/^Note: (.+)$/, "Note : $1"],
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
