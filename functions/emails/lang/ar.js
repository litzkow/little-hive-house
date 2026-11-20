// Little Hive House emails (and the Stripe checkout page item names) in Arabic (Modern Standard Arabic).
// look(key): the exact dictionary (functions/emails/ar.json), the collection names, then the patterns below.
// The layout sets dir="rtl" for Arabic.
"use strict";

let DICT = null;
function dict() {
  if (!DICT) { try { DICT = require("../ar.json"); } catch (e) { DICT = {}; } }
  return DICT;
}
const MONS = ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو", "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"];
const MON = { Jan: 0, Feb: 1, Mar: 2, Apr: 3, May: 4, Jun: 5, Jul: 6, Aug: 7, Sep: 8, Oct: 9, Nov: 10, Dec: 11,
  January: 0, February: 1, March: 2, April: 3, June: 5, July: 6, August: 7, September: 8, October: 9, November: 10, December: 11 };
const M = "(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)";
/** "Nov 17–20" → "17–20 نوفمبر"; "Nov 28–Dec 2" → "28 نوفمبر – 2 ديسمبر"; "November 3, 2026" → "3 نوفمبر 2026" */
function date(s) {
  return String(s)
    .replace(new RegExp(M + " (\\d{1,2}), (\\d{4})", "g"), (_, m, d, y) => `${d} ${MONS[MON[m]]} ${y}`)
    .replace(new RegExp(M + " (\\d{1,2})[–-](\\d{1,2})\\b", "g"), (_, m, a, b) => `${a}–${b} ${MONS[MON[m]]}`)
    .replace(new RegExp(M + " (\\d{1,2})[–-]" + M + " (\\d{1,2})", "g"), (_, m1, a, m2, b) => `${a} ${MONS[MON[m1]]} – ${b} ${MONS[MON[m2]]}`)
    .replace(new RegExp(M + " (\\d{1,2})\\b", "g"), (_, m, d) => `${d} ${MONS[MON[m]]}`);
}
/** Arabic counted noun: w = [one, two, plural 3–10, singular 11–99, singular 100+] */
function cnt(n, w) {
  const k = Math.abs(parseInt(String(n).replace(/[^\d]/g, ""), 10) || 0), r = k % 100;
  if (k === 1) return w[0];
  if (k === 2) return w[1];
  if (r >= 3 && r <= 10) return `${n} ${w[2]}`;
  if (r >= 11 && r <= 99) return `${n} ${w[3]}`;
  return `${n} ${w[4]}`;
}
const mag = (n) => cnt(n, ["مغناطيس واحد", "مغناطيسان", "مغناطيسات", "مغناطيسًا", "مغناطيس"]);
/** "15% off" → "خصم 15%"; "$5.00 off" → "خصم $5.00" */
function off(s) {
  s = String(s);
  let m = /^(\d+)% off$/.exec(s); if (m) return `خصم ${m[1]}%`;
  m = /^(\$[\d.,]+) off$/.exec(s); if (m) return `خصم ${m[1]}`;
  return s === "a little something off" ? "خصم صغير" : s;
}
/** "1 hour" → "ساعة واحدة"; "30 minutes" → "30 دقيقة" */
function dur(s) {
  return String(s).replace(/\b1 hour\b/, "ساعة واحدة").replace(/(\d+) hours/, (_, n) => cnt(n, ["ساعة واحدة", "ساعتين", "ساعات", "ساعة", "ساعة"]))
    .replace(/(\d+) minutes/, (_, n) => cnt(n, ["دقيقة واحدة", "دقيقتين", "دقائق", "دقيقة", "دقيقة"]));
}
const ord = (n) => (n === "your order" ? "طلبك" : `الطلب ${n}`);
/** "for the order": لـ joins the article (للطلب) */
const forOrd = (n) => (n === "your order" ? "لطلبك" : `للطلب ${n}`);
/** names in Latin script stay in one piece inside Arabic text (Unicode first-strong isolate) */
const iso = (s) => (/[A-Za-z]/.test(s) ? `\u2068${s}\u2069` : s);
const ev = (n) => (n === "Black Friday" ? "الجمعة السوداء" : n === "Cyber Monday" ? "الاثنين الإلكتروني" : n);
const COL = {
  "USA Places": "أماكن أمريكية", "World Places": "أماكن من العالم", "Ink Cities": "مدن بالحبر", "City Sketches": "رسومات المدن",
  "Fall": "الخريف", "Halloween": "الهالوين", "Horror Classics": "كلاسيكيات الرعب", "Furry Friends": "أصدقاء بفرو", "Kitchen Words": "كلمات المطبخ",
  "Americana": "أمريكانا", "México": "المكسيك", "Ireland": "أيرلندا", "Italia": "إيطاليا", "Puerto Rico": "بورتوريكو", "Pilipinas": "الفلبين",
  "India": "الهند", "Korea": "كوريا", "Japan": "اليابان", "Brasil": "البرازيل", "Greece": "اليونان", "France": "فرنسا",
  "Great Masters": "كبار الفنانين", "Mythology": "الأساطير", "Home Notes": "ملاحظات البيت", "Night Sky": "سماء الليل",
  "Birth Flowers": "زهور الميلاد", "Storybook Classics": "كلاسيكيات الأدب", "Fairy Tales & Myths": "حكايات وأساطير",
  "Wise Words": "كلمات حكيمة", "Holidays & Dates": "مناسبات وأعياد", "Bumper Stickers": "ملصقات السيارات",
  "Christmas": "عيد الميلاد", "Summer": "الصيف", "Heritage": "الجذور",
};
const DATE_ONLY = new RegExp("^(about )?" + M + " \\d{1,2}([–-](" + M + " )?\\d{1,2})?(, \\d{4})?$");
const P = [
  [/^Here's everything that's coming your way, ordered (.+)\.$/, (_, d) => `هذا كل ما في طريقه إليك، طلبته في ${date(d)}.`],
  [/^Here's everything that's coming your way\.$/, "هذا كل ما في طريقه إليك."],
  [/^(\d+) magnets? coming your way\. We'll start making them by hand right away\.$/, (_, n) => `في طريقه إليك: ${mag(n)}. سنبدأ صنعها يدويًا فورًا.`],
  [/^Thank you! Order (.+) is confirmed$/, "شكرًا! تم تأكيد الطلب $1"],
  [/^Estimated arrival: about 1 to 2 weeks after you approve the proof$/, "الوصول المتوقع: بعد أسبوع إلى أسبوعين تقريبًا من موافقتك على النموذج"],
  [/^Estimated arrival: (.+)$/, (_, d) => `الوصول المتوقع: ${d.startsWith("about ") ? "نحو " + date(d.slice(6)) : date(d)}`],
  [/^Your magnets are on the way!( \((.+)\))?$/, (_, x, n) => `مغناطيساتك في الطريق!${n ? ` (${n})` : ""}`],
  [/^(.+?)( tracking (.+))?\. Follow your package all the way to your door\.$/, (_, c, x, t) => `${c}${t ? `، رقم التتبّع ${t}` : ""}. تابع طردك حتى باب بيتك.`],
  [/^Charged to your card today, when your order shipped( \(order (.+)\))?\. Keep this email as your receipt\.$/, (_, x, n) => `خُصم المبلغ من بطاقتك اليوم عند شحن طلبك${n ? ` (الطلب ${n})` : ""}. احتفظ بهذه الرسالة كإيصال.`],
  [/^Carrier: (.+)$/, "شركة الشحن: $1"],
  [/^Tracking number: see the tracking page$/, "رقم التتبّع: انظر صفحة التتبّع"],
  [/^Tracking number: (.+)$/, "رقم التتبّع: $1"],
  [/^Order (.+) · Out for delivery$/, "الطلب $1 · خرج للتوصيل"],
  [/^Order (.+) · Delivered$/, "الطلب $1 · تم التوصيل"],
  [/^(.+), your magnets arrive today!$/, "$1، مغناطيساتك تصل اليوم!"],
  [/^(.+) has your package out for delivery\. Keep an eye on the porch and the mailbox\.$/, "طردك خرج للتوصيل مع $1. راقب باب البيت وصندوق البريد."],
  [/^(.+) has your package out for delivery( \(order (.+)\))?\. Keep an eye on the porch!$/, (_, c, x, n) => `طردك خرج للتوصيل مع ${c}${n ? ` (الطلب ${n})` : ""}. راقب باب البيت!`],
  [/^Latest scan: (.+)$/, "آخر تحديث: $1"],
  [/^(.+), how do they look on your fridge\?$/, "$1، كيف تبدو على ثلاجتك؟"],
  [/^for your next order: (.+?) until (.+)\.$/, (_, o, d) => `لطلبك القادم: ${off(o)} حتى ${date(d)}.`],
  [/^for your next order: (.+)\.$/, (_, o) => `لطلبك القادم: ${off(o)}.`],
  [/^Show us your fridge! Share a photo on Instagram and tag (.+?)\.?$/, "أرنا ثلاجتك! شارك صورة على Instagram وأشِر إلى $1."],
  [/^Return · (.+)$/, "إرجاع · $1"],
  [/^Hi (.+?)[.!]$/, (_, x) => `مرحبًا ${iso(x)}!`],
  [/^Your return label for (.+)$/, (_, n) => `ملصق الإرجاع ${forOrd(n)}`],
  [/^We got your return request \((.+)\)$/, (_, n) => `وصلنا طلب الإرجاع (${ord(n)})`],
  [/^We're reprinting your magnets \((.+)\)$/, (_, n) => `نعيد طباعة مغناطيساتك (${ord(n)})`],
  [/^About your return for (.+)$/, (_, n) => `بخصوص إرجاع ${ord(n)}`],
  [/^No printer\? Show this QR code at the Post Office: (.+)$/, "لا توجد طابعة؟ اعرض رمز QR هذا في مكتب البريد: $1"],
  [/^In this return:\n([\s\S]+)$/, "في هذا الإرجاع:\n$1"],
  [/^A note from us: ([\s\S]+)$/, "ملاحظة منا: $1"],
  [/^A partial refund of (\$[\d.,]+) for (.+)$/, (_, a, n) => `استرداد جزئي بقيمة ${a} ${forOrd(n)}`],
  [/^Your refund for (.+) is on its way$/, (_, n) => `استرداد ${ord(n)} في الطريق`],
  [/^(\$[\d.,]+) is heading back to you\. Banks usually show it within 5 to 10 business days\.$/, "$1 في طريقها إليك. تُظهرها البنوك عادةً خلال 5 إلى 10 أيام عمل."],
  [/^(Full|Partial) refund: (\$[\d.,]+)(.*)$/, (_, k, a, rest) => `${k === "Full" ? "استرداد كامل" : "استرداد جزئي"}: ${a}${rest.replace(/ for order /g, "، الطلب ").replace(/order/g, "الطلب")}`],
  [/^Back to your original payment method( for order (.+))?$/, (_, x, n) => `إلى وسيلة الدفع الأصلية${n ? `، الطلب ${n}` : ""}`],
  [/^Refunded on this order so far: (\$[\d.,]+) of (\$[\d.,]+)\.$/, "المسترد من هذا الطلب حتى الآن: $1 من $2."],
  [/^Welcome to the hive, (.+)!$/, "أهلًا بك في الخلية، $1!"],
  [/^(\d+% off|\$[\d.,]+ off|a little something off) your first order(,? until (.+?))?\.?$/, (_, o, x, d) => `${off(o)} على طلبك الأول${d ? ` حتى ${date(d)}` : ""}.`],
  [/^Your account is ready, and (.+) your first order is waiting\.$/, (_, o) => `حسابك جاهز، و${off(o)} على طلبك الأول بانتظارك.`],
  [/^Thanks for joining! Here's (.+) your first order\.$/, (_, o) => `شكرًا لانضمامك! إليك ${off(o)} على طلبك الأول.`],
  [/^One quick tap, (.+)!$/, "$1، ضغطة واحدة فقط!"],
  [/^For your security this link expires in (.+) and works only once\. If it has expired, you can$/, (_, e) => `لأمانك، تنتهي صلاحية هذا الرابط بعد ${dur(e)} ويعمل مرة واحدة فقط. إن انتهت صلاحيته، يمكنك`],
  [/^Tap the button to choose a new password\. The link works for (.+)\.$/, (_, e) => `اضغط الزر لاختيار كلمة مرور جديدة. الرابط صالح لمدة ${dur(e)}.`],
  [/^(.+), your magnets are still waiting$/, "$1، مغناطيساتك ما زالت بانتظارك"],
  [/^We saved your (\d+) magnets?\. Pick up right where you left off\.$/, (_, n) => `حفظنا لك ${mag(n)}. أكمل من حيث توقفت.`],
  [/^Thanks for writing, (.+)!$/, "شكرًا لرسالتك، $1!"],
  [/^You wrote · (.+)$/, (_, t) => `كتبت · ${look(t) || t}`],
  [/^Thanks! We'll reply within 1 business day with ideas, a price for (\d+) magnets and next steps\.$/, (_, n) => `شكرًا! سنرد خلال يوم عمل واحد بأفكار وسعر لـ ${mag(n)} والخطوات التالية.`],
  [/^Thanks! We'll reply within 1 business day with ideas, a price and next steps\.$/, "شكرًا! سنرد خلال يوم عمل واحد بأفكار وسعر والخطوات التالية."],
  [/^Here's your link, (.+)$/, "$1، إليك رابطك"],
  [/^Your payment link for (.+)$/, "رابط الدفع: $1"],
  [/^(\$[\d.,]+) for (.+)\. Pay securely by card, Apple Pay or Google Pay\.$/, "$2: $1. ادفع بأمان بالبطاقة أو Apple Pay أو Google Pay."],
  [/^Payments are processed by Stripe\. We never see or store your card number\.( This link works until (.+)\.)?$/, (_, x, d) => `تعالج Stripe المدفوعات. لا نرى رقم بطاقتك ولا نخزّنه أبدًا.${d ? ` هذا الرابط صالح حتى ${date(d)}.` : ""}`],
  // the Stripe checkout page (functions/checkout.js)
  [/^(\d+) custom photo magnets, 2 × 2 in$/, (_, n) => `${cnt(n, ["مغناطيس صور مخصّص واحد", "مغناطيسا صور مخصّصان", "مغناطيسات صور مخصّصة", "مغناطيس صور مخصّصًا", "مغناطيس صور مخصّص"])}، 2 × 2 إنش (5 سم)`],
  [/^(\d+) custom magnets\. We email you about your design after checkout\.$/, (_, n) => `${cnt(n, ["مغناطيس مخصّص واحد", "مغناطيسان مخصّصان", "مغناطيسات مخصّصة", "مغناطيسًا مخصّصًا", "مغناطيس مخصّص"])}. نراسلك بخصوص التصميم بعد الدفع.`],
  [/^(.+) discount included$/, (_, n) => `يشمل خصم ${ev(n)}`],
  [/^(\d+) photo magnets$/, (_, n) => cnt(n, ["مغناطيس صور واحد", "مغناطيسا صور", "مغناطيسات صور", "مغناطيس صور", "مغناطيس صور"])],
  [/^(\d+) photos?$/, (_, n) => cnt(n, ["صورة واحدة", "صورتان", "صور", "صورة", "صورة"])],
  [/^(\d+) frames$/, (_, n) => cnt(n, ["إطار واحد", "إطاران", "إطارات", "إطارًا", "إطار"])],
  [/^(\d+) packs$/, (_, n) => cnt(n, ["باقة واحدة", "باقتان", "باقات", "باقة", "باقة"])],
  [/^(.+) frame$/, (_, f) => `إطار ${look(f) || f}`],
  [/^(.+) magnet$/, (_, x) => `مغناطيس ${iso(x)}`],
  [DATE_ONLY, (s) => (s.startsWith("about ") ? "نحو " + date(s.slice(6)) : date(s))],
  [/^Good news, (.+)!$/, "$1، أخبار سارة!"],
  [/^Thank you, (.+)!$/, (_, x) => `شكرًا، ${iso(x)}!`],
  [/^Thanks, (.+)!$/, (_, x) => `شكرًا، ${iso(x)}!`],
  [/^Hi (.+),$/, (_, x) => `مرحبًا ${iso(x)}،`],
  [/^Order (LHH-\d+)$/, "الطلب $1"],
  [/^Qty (\d+)$/, "الكمية $1"],
  [/^(\d+) magnets( × (\d+))?$/, (_, n, x, q) => `${mag(n)}${q ? ` × ${q}` : ""}`],
  [/^Volume discount \((\d+)% off\)$/, (_, p) => `خصم الكمية (${p}%)`],
  [/^Promo code (.+)$/, "رمز الخصم $1"],
  [/^(.+), (\d+)% off$/, (_, n, p) => `${ev(n)}، خصم ${p}%`],
  [/^(.+), (\d+) designs? free$/, (_, n, k) => `${ev(n)}، ${cnt(k, ["تصميم واحد", "تصميمان", "تصاميم", "تصميمًا", "تصميم"])} مجانًا`],
  [/^Captions: (.+)$/, (_, x) => `التعليقات: ${iso(x)}`],
  [/^Note: (.+)$/, (_, x) => `ملاحظة: ${iso(x)}`],
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
