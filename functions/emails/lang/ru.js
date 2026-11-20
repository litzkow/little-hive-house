// Little Hive House emails (and the Stripe checkout page) in Russian (formal «вы»).
// look(key): the exact dictionary (functions/emails/ru.json), the collection names, then the patterns below.
"use strict";

let DICT = null;
function dict() {
  if (!DICT) { try { DICT = require("../ru.json"); } catch (e) { DICT = {}; } }
  return DICT;
}
const MON = { Jan: 0, Feb: 1, Mar: 2, Apr: 3, May: 4, Jun: 5, Jul: 6, Aug: 7, Sep: 8, Oct: 9, Nov: 10, Dec: 11,
  January: 0, February: 1, March: 2, April: 3, June: 5, July: 6, August: 7, September: 8, October: 9, November: 10, December: 11 };
const GEN = ["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября", "октября", "ноября", "декабря"];
const M = "(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)";
/** "Nov 17–20" → "17–20 ноября"; "Nov 28–Dec 2" → "28 ноября – 2 декабря"; "November 3, 2026" → "3 ноября 2026 г." */
function date(s) {
  return String(s)
    .replace(new RegExp(M + " (\\d{1,2}), (\\d{4})", "g"), (_, m, d, y) => `${d} ${GEN[MON[m]]} ${y} г.`)
    .replace(new RegExp(M + " (\\d{1,2})[–-](\\d{1,2})\\b", "g"), (_, m, a, b) => `${a}–${b} ${GEN[MON[m]]}`)
    .replace(new RegExp(M + " (\\d{1,2})[–-]" + M + " (\\d{1,2})", "g"), (_, m1, a, m2, b) => `${a} ${GEN[MON[m1]]} – ${b} ${GEN[MON[m2]]}`)
    .replace(new RegExp(M + " (\\d{1,2})\\b", "g"), (_, m, d) => `${d} ${GEN[MON[m]]}`);
}
/** Russian plural */
function pl(n, one, few, many) {
  n = Math.abs(parseInt(String(n).replace(/[^\d]/g, ""), 10) || 0);
  const a = n % 10, b = n % 100;
  return a === 1 && b !== 11 ? one : a >= 2 && a <= 4 && (b < 12 || b > 14) ? few : many;
}
const mag = (n) => `${n} ${pl(n, "магнит", "магнита", "магнитов")}`;
/** "15% off" → "скидка 15%"; "$5.00 off" → "скидка $5.00" */
function off(s) {
  s = String(s);
  let m = /^(\d+)% off$/.exec(s); if (m) return `скидка ${m[1]}%`;
  m = /^(\$[\d.,]+) off$/.exec(s); if (m) return `скидка ${m[1]}`;
  return s === "a little something off" ? "небольшая скидка" : s;
}
/** "1 hour" → "1 час"; "30 minutes" → "30 минут" */
function dur(s) {
  return String(s).replace(/\b1 hour\b/, "1 час").replace(/(\d+) hours/, (_, n) => `${n} ${pl(n, "час", "часа", "часов")}`)
    .replace(/(\d+) minutes/, (_, n) => `${n} ${pl(n, "минуту", "минуты", "минут")}`);
}
const ord = (n) => (n === "your order" ? "вашего заказа" : `заказа ${n}`);
const ev = (n) => (n === "Black Friday" ? "Чёрная пятница" : n === "Cyber Monday" ? "Киберпонедельник" : n);
const COL = {
  "USA Places": "Места США", "World Places": "Места мира", "Ink Cities": "Города тушью", "City Sketches": "Городские скетчи",
  "Fall": "Осень", "Halloween": "Хэллоуин", "Horror Classics": "Классика ужасов", "Furry Friends": "Пушистые друзья", "Kitchen Words": "Кухонные слова",
  "Americana": "Американа", "México": "Мексика", "Ireland": "Ирландия", "Italia": "Италия", "Puerto Rico": "Пуэрто-Рико", "Pilipinas": "Филиппины",
  "India": "Индия", "Korea": "Корея", "Japan": "Япония", "Brasil": "Бразилия", "Greece": "Греция", "France": "Франция",
  "Great Masters": "Великие мастера", "Mythology": "Мифология", "Home Notes": "Записки для дома", "Night Sky": "Ночное небо",
  "Birth Flowers": "Цветы месяца рождения", "Storybook Classics": "Классика литературы", "Fairy Tales & Myths": "Сказки и мифы",
  "Wise Words": "Мудрые слова", "Holidays & Dates": "Праздники и даты", "Bumper Stickers": "Наклейки на бампер",
  "Christmas": "Рождество", "Summer": "Лето", "Heritage": "Корни",
};
const DATE_ONLY = new RegExp("^(about )?" + M + " \\d{1,2}([–-](" + M + " )?\\d{1,2})?(, \\d{4})?$");
const P = [
  [/^Here's everything that's coming your way, ordered (.+)\.$/, (_, d) => `Вот всё, что к вам едет, заказ от ${date(d)}.`],
  [/^Here's everything that's coming your way\.$/, "Вот всё, что к вам едет."],
  [/^(\d+) magnets? coming your way\. We'll start making them by hand right away\.$/, (_, n) => `Скоро у вас: ${mag(n)}. Мы сразу начнём делать их вручную.`],
  [/^Thank you! Order (.+) is confirmed$/, "Спасибо! Заказ $1 подтверждён"],
  [/^Estimated arrival: about 1 to 2 weeks after you approve the proof$/, "Ожидаемая доставка: примерно через 1–2 недели после утверждения макета"],
  [/^Estimated arrival: (.+)$/, (_, d) => `Ожидаемая доставка: ${d.startsWith("about ") ? "примерно " + date(d.slice(6)) : date(d)}`],
  [/^Your magnets are on the way!( \((.+)\))?$/, (_, x, n) => `Ваши магниты в пути!${n ? ` (${n})` : ""}`],
  [/^(.+?)( tracking (.+))?\. Follow your package all the way to your door\.$/, (_, c, x, t) => `${c}${t ? `, трек-номер ${t}` : ""}. Следите за посылкой до самой двери.`],
  [/^Charged to your card today, when your order shipped( \(order (.+)\))?\. Keep this email as your receipt\.$/, (_, x, n) => `Списано с вашей карты сегодня, при отправке заказа${n ? ` (заказ ${n})` : ""}. Сохраните это письмо как чек.`],
  [/^Carrier: (.+)$/, "Перевозчик: $1"],
  [/^Tracking number: see the tracking page$/, "Трек-номер: смотрите страницу отслеживания"],
  [/^Tracking number: (.+)$/, "Трек-номер: $1"],
  [/^Order (.+) · Out for delivery$/, "Заказ $1 · Доставка сегодня"],
  [/^Order (.+) · Delivered$/, "Заказ $1 · Доставлен"],
  [/^(.+), your magnets arrive today!$/, "$1, ваши магниты приедут сегодня!"],
  [/^(.+) has your package out for delivery\. Keep an eye on the porch and the mailbox\.$/, "$1 уже везёт вашу посылку. Поглядывайте на крыльцо и почтовый ящик."],
  [/^(.+) has your package out for delivery( \(order (.+)\))?\. Keep an eye on the porch!$/, (_, c, x, n) => `${c} уже везёт вашу посылку${n ? ` (заказ ${n})` : ""}. Поглядывайте на крыльцо!`],
  [/^Latest scan: (.+)$/, "Последняя отметка: $1"],
  [/^(.+), how do they look on your fridge\?$/, "$1, как они смотрятся на холодильнике?"],
  [/^for your next order: (.+?) until (.+)\.$/, (_, o, d) => `на следующий заказ: ${off(o)} до ${date(d)}.`.replace(/\.+$/, ".")],
  [/^for your next order: (.+)\.$/, (_, o) => `на следующий заказ: ${off(o)}.`],
  [/^Show us your fridge! Share a photo on Instagram and tag (.+?)\.?$/, "Покажите нам свой холодильник! Выложите фото в Instagram и отметьте $1."],
  [/^Return · (.+)$/, "Возврат · $1"],
  [/^Hi (.+?)[.!]$/, "Здравствуйте, $1!"],
  [/^Your return label for (.+)$/, (_, n) => `Этикетка для возврата ${ord(n)}`],
  [/^We got your return request \((.+)\)$/, (_, n) => `Мы получили ваш запрос на возврат (${ord(n).replace(/^заказа/, "заказ")})`],
  [/^We're reprinting your magnets \((.+)\)$/, (_, n) => `Мы перепечатываем ваши магниты (${ord(n).replace(/^заказа/, "заказ")})`],
  [/^About your return for (.+)$/, (_, n) => `О возврате ${ord(n)}`],
  [/^No printer\? Show this QR code at the Post Office: (.+)$/, "Нет принтера? Покажите этот QR-код на почте: $1"],
  [/^In this return:\n([\s\S]+)$/, "В этом возврате:\n$1"],
  [/^A note from us: ([\s\S]+)$/, "Записка от нас: $1"],
  [/^A partial refund of (\$[\d.,]+) for (.+)$/, (_, a, n) => `Частичный возврат ${a} для ${ord(n)}`],
  [/^Your refund for (.+) is on its way$/, (_, n) => `Возврат денег для ${ord(n)} уже в пути`],
  [/^(\$[\d.,]+) is heading back to you\. Banks usually show it within 5 to 10 business days\.$/, "$1 возвращаются к вам. Банки обычно показывают возврат в течение 5–10 рабочих дней."],
  [/^(Full|Partial) refund: (\$[\d.,]+)(.*)$/, (_, k, a, rest) => `${k === "Full" ? "Полный возврат" : "Частичный возврат"}: ${a}${rest.replace(/ for order /g, ", заказ ").replace(/order/g, "заказ")}`],
  [/^Back to your original payment method( for order (.+))?$/, (_, x, n) => `На исходный способ оплаты${n ? `, заказ ${n}` : ""}`],
  [/^Refunded on this order so far: (\$[\d.,]+) of (\$[\d.,]+)\.$/, "По этому заказу уже возвращено: $1 из $2."],
  [/^Welcome to the hive, (.+)!$/, "Добро пожаловать в улей, $1!"],
  [/^(\d+% off|\$[\d.,]+ off|a little something off) your first order(,? until (.+?))?\.?$/, (_, o, x, d) => `${off(o).replace(/^с/, "С")} на первый заказ${d ? ` до ${date(d)}` : ""}.`.replace(/\.+$/, ".")],
  [/^Your account is ready, and (.+) your first order is waiting\.$/, (_, o) => `Ваш аккаунт готов, а на первый заказ вас ждёт ${off(o)}.`],
  [/^Thanks for joining! Here's (.+) your first order\.$/, (_, o) => `Спасибо, что присоединились! Вот ваша ${off(o)} на первый заказ.`],
  [/^One quick tap, (.+)!$/, "$1, всего одно касание!"],
  [/^For your security this link expires in (.+) and works only once\. If it has expired, you can$/, (_, e) => `Для вашей безопасности ссылка действует ${dur(e)} и срабатывает только один раз. Если срок истёк, можно`],
  [/^Tap the button to choose a new password\. The link works for (.+)\.$/, (_, e) => `Нажмите кнопку, чтобы задать новый пароль. Ссылка действует ${dur(e)}.`],
  [/^(.+), your magnets are still waiting$/, "$1, ваши магниты всё ещё ждут"],
  [/^We saved your (\d+) magnets?\. Pick up right where you left off\.$/, (_, n) => `Мы сохранили ${mag(n)}. Продолжите с того места, где остановились.`],
  [/^Thanks for writing, (.+)!$/, "Спасибо за письмо, $1!"],
  [/^You wrote · (.+)$/, (_, t) => `Вы написали · ${look(t) || t}`],
  [/^Thanks! We'll reply within 1 business day with ideas, a price for (\d+) magnets and next steps\.$/, (_, n) => `Спасибо! В течение 1 рабочего дня пришлём идеи, цену за ${mag(n)} и следующие шаги.`],
  [/^Thanks! We'll reply within 1 business day with ideas, a price and next steps\.$/, "Спасибо! В течение 1 рабочего дня пришлём идеи, цену и следующие шаги."],
  [/^Here's your link, (.+)$/, "$1, вот ваша ссылка"],
  [/^Your payment link for (.+)$/, "Ссылка на оплату: $1"],
  [/^(\$[\d.,]+) for (.+)\. Pay securely by card, Apple Pay or Google Pay\.$/, "$2: $1. Безопасная оплата картой, Apple Pay или Google Pay."],
  [/^Payments are processed by Stripe\. We never see or store your card number\.( This link works until (.+)\.)?$/, (_, x, d) => `Платежи обрабатывает Stripe. Мы никогда не видим и не храним номер вашей карты.${d ? ` Ссылка действует до ${date(d)}.` : ""}`],
  // the Stripe checkout page (functions/checkout.js)
  [/^(\d+) custom photo magnets, 2 × 2 in$/, (_, n) => `${n} ${pl(n, "фотомагнит", "фотомагнита", "фотомагнитов")} на заказ, 2 × 2 дюйма (5 см)`],
  [/^(\d+) custom magnets\. We email you about your design after checkout\.$/, (_, n) => `${mag(n)} на заказ. После оплаты напишем вам о дизайне.`],
  [/^(.+) discount included$/, (_, n) => `Скидка «${ev(n)}» учтена`],
  [/^(\d+) photo magnets$/, (_, n) => `${n} ${pl(n, "фотомагнит", "фотомагнита", "фотомагнитов")}`],
  [/^(\d+) photos?$/, "$1 фото"],
  [/^(\d+) frames$/, (_, n) => `${n} ${pl(n, "рамка", "рамки", "рамок")}`],
  [/^(\d+) packs$/, (_, n) => `${n} ${pl(n, "набор", "набора", "наборов")}`],
  [/^(.+) frame$/, (_, f) => `Рамка «${look(f) || f}»`],
  [/^(.+) magnet$/, "Магнит «$1»"],
  [DATE_ONLY, (s) => (s.startsWith("about ") ? "примерно " + date(s.slice(6)) : date(s))],
  [/^Good news, (.+)!$/, "$1, хорошие новости!"],
  [/^Thank you, (.+)!$/, "Спасибо, $1!"],
  [/^Thanks, (.+)!$/, "Спасибо, $1!"],
  [/^Hi (.+),$/, "Здравствуйте, $1!"],
  [/^Order (LHH-\d+)$/, "Заказ $1"],
  [/^Qty (\d+)$/, "Кол-во $1"],
  [/^(\d+) magnets( × (\d+))?$/, (_, n, x, q) => `${mag(n)}${q ? ` × ${q}` : ""}`],
  [/^Volume discount \((\d+)% off\)$/, (_, p) => `Скидка за объём (−${p}%)`],
  [/^Promo code (.+)$/, "Промокод $1"],
  [/^(.+), (\d+)% off$/, (_, n, p) => `${ev(n)}, скидка ${p}%`],
  [/^(.+), (\d+) designs? free$/, (_, n, k) => `${ev(n)}, ${k} ${pl(k, "дизайн", "дизайна", "дизайнов")} в подарок`],
  [/^Captions: (.+)$/, "Подписи: $1"],
  [/^Note: (.+)$/, "Записка: $1"],
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
