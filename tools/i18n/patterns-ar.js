/* Patterns: English text with a number, a date or a name in it. Each is [regex, Arabic] where the Arabic is a
   replacement string ($1…) or a function of the match. Checked in order, after the exact dictionary.
   Modern Standard Arabic, Western digits, prices in US format ($5.49, 1,200). Counted words follow Arabic number agreement (cnt). */
var COL = {
  "USA Places": "أماكن أمريكية", "World Places": "أماكن من العالم", "Ink Cities": "مدن بالحبر",
  "City Sketches": "رسومات المدن", "Fall": "الخريف", "Halloween": "الهالوين", "Horror Classics": "كلاسيكيات الرعب",
  "Furry Friends": "أصدقاء بفرو", "Kitchen Words": "كلمات المطبخ", "Americana": "أمريكانا", "México": "المكسيك",
  "Ireland": "أيرلندا", "Italia": "إيطاليا", "Puerto Rico": "بورتوريكو", "Pilipinas": "الفلبين", "India": "الهند",
  "Korea": "كوريا", "Japan": "اليابان", "Brasil": "البرازيل", "Greece": "اليونان", "France": "فرنسا",
  "Great Masters": "كبار الفنانين", "Mythology": "الأساطير", "Home Notes": "ملاحظات البيت", "Bee Kind": "Bee Kind",
  "Night Sky": "سماء الليل", "Birth Flowers": "زهور الميلاد", "Storybook Classics": "كلاسيكيات الأدب",
  "Fairy Tales & Myths": "حكايات وأساطير", "Wise Words": "كلمات حكيمة", "Holidays & Dates": "مناسبات وأعياد",
  "Bumper Stickers": "ملصقات السيارات", "Christmas": "عيد الميلاد", "Summer": "الصيف", "Heritage": "الجذور",
  "Photo magnets": "مغناطيسات الصور", "Custom photo magnets": "مغناطيسات صور مخصّصة"
};
var FRAME = { "Arch": "قوس", "Art deco": "آرت ديكو", "Autumn": "الخريف", "Birthday": "عيد ميلاد", "Botanical": "نباتي",
  "Circle": "دائرة", "Classic": "كلاسيكي", "Crisp white mat": "إطار أبيض ناصع", "Date stamp": "ختم التاريخ",
  "Eucalyptus wreath": "إكليل أوكالبتوس", "Film frame": "إطار فيلم", "Full photo": "الصورة كاملة",
  "Gallery mat": "إطار معرض", "Gallery with caption": "معرض مع تعليق", "Gold line": "خط ذهبي",
  "Graduation": "تخرج", "Handwritten": "بخط اليد", "Holiday": "عيد", "Honeycomb": "خلية نحل",
  "Instant print": "صورة فورية", "Love": "حب", "Modern": "عصري", "Name band": "شريط الاسم",
  "Postage stamp": "طابع بريد", "Postcard": "بطاقة بريدية", "Rounded modern": "عصري مستدير",
  "Scalloped lace": "دانتيل مموّج", "Script": "خط مزخرف", "Sweet dreams": "أحلامًا سعيدة", "Team": "فريق",
  "Thin white border": "حافة بيضاء رفيعة", "Tropical leaves": "أوراق استوائية", "Vintage ornate gold": "ذهبي عتيق مزخرف",
  "Watercolour peonies": "فاوانيا بالألوان المائية", "Wedding": "عرس", "Winter": "الشتاء", "No border": "بلا إطار" };
function fr(s) { return FRAME[s] || s; }
function col(s) { return COL[s] || s; }
/** only for the shop's own collection names: anything else is left to the dictionary */
function known(s) { return Object.prototype.hasOwnProperty.call(COL, s) || /^(Americana|México|Brasil|Halloween|Bee Kind)$/.test(s); }
/** Arabic counted noun: w = [one, two, plural 3–10, singular 11–99, singular 100+] */
function cnt(n, w) {
  var k = Math.abs(parseInt(String(n).replace(/[^\d]/g, ""), 10) || 0), r = k % 100;
  if (k === 1) return w[0];
  if (k === 2) return w[1];
  if (r >= 3 && r <= 10) return n + " " + w[2];
  if (r >= 11 && r <= 99) return n + " " + w[3];
  return n + " " + w[4];
}
var MAG = ["مغناطيس واحد", "مغناطيسان", "مغناطيسات", "مغناطيسًا", "مغناطيس"];
var DES = ["تصميم واحد", "تصميمان", "تصاميم", "تصميمًا", "تصميم"];
var PHO = ["صورة واحدة", "صورتان", "صور", "صورة", "صورة"];
var CTRY = ["دولة واحدة", "دولتان", "دول", "دولة", "دولة"];
var ADDR = ["عنوان واحد", "عنوانان", "عناوين", "عنوانًا", "عنوان"];
var FRM = ["إطار واحد", "إطاران", "إطارات", "إطارًا", "إطار"];
function mag(n) { return cnt(n, MAG); }
function des(n) { return cnt(n, DES); }
function pho(n) { return cnt(n, PHO); }
var MONS = ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو", "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"];
var MON = { Jan: 0, Feb: 1, Mar: 2, Apr: 3, May: 4, Jun: 5, Jul: 6, Aug: 7, Sep: 8, Oct: 9, Nov: 10, Dec: 11,
  January: 0, February: 1, March: 2, April: 3, June: 5, July: 6, August: 7, September: 8, October: 9, November: 10, December: 11 };
var DAY = { Mon: "الاثنين", Tue: "الثلاثاء", Wed: "الأربعاء", Thu: "الخميس", Fri: "الجمعة", Sat: "السبت", Sun: "الأحد",
  Monday: "الاثنين", Tuesday: "الثلاثاء", Wednesday: "الأربعاء", Thursday: "الخميس", Friday: "الجمعة", Saturday: "السبت", Sunday: "الأحد" };
var M = "(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)";
/* "Nov 17–20" → "17–20 نوفمبر"; "Nov 28–Dec 2" → "28 نوفمبر – 2 ديسمبر"; "November 3, 2026" → "3 نوفمبر 2026";
   "Tue, Nov 17" → "الثلاثاء، 17 نوفمبر" */
function date(s) {
  return s
    .replace(/\b(Mon|Tue|Wed|Thu|Fri|Sat|Sun|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b,?/g, function (d, x) { return DAY[x] + (/,/.test(d) ? "،" : ""); })
    .replace(new RegExp(M + " (\\d{1,2}), (\\d{4})", "g"), function (_, m, d, y) { return d + " " + MONS[MON[m]] + " " + y; })
    .replace(new RegExp(M + " (\\d{1,2})[–-](\\d{1,2})\\b", "g"), function (_, m, a, b) { return a + "–" + b + " " + MONS[MON[m]]; })
    .replace(new RegExp(M + " (\\d{1,2})[–-]" + M + " (\\d{1,2})", "g"), function (_, m1, a, m2, b) { return a + " " + MONS[MON[m1]] + " – " + b + " " + MONS[MON[m2]]; })
    .replace(new RegExp(M + " (\\d{1,2})\\b", "g"), function (_, m, d) { return d + " " + MONS[MON[m]]; })
    .replace(new RegExp(M + " (\\d{4})", "g"), function (_, m, y) { return MONS[MON[m]] + " " + y; });
}
/** names in Latin script stay in one piece inside Arabic text (Unicode first-strong isolate) */
function iso(s) { return /[A-Za-z]/.test(s) ? "\u2068" + s + "\u2069" : s; }
function tr(s) { return COL[s] || (window.LHH_I18N ? window.LHH_I18N.t(s) : s); }
function ev(n) { return n === "Black Friday" ? "الجمعة السوداء" : n === "Cyber Monday" ? "الاثنين الإلكتروني" : n; }
var FOR = { "your business": "لعملك", "your wedding": "لعرسك", "your graduation": "لتخرجك", "your party or event": "لحفلتك أو مناسبتك", "your home": "لبيتك",
  business: "لعملك", wedding: "لعرسك", graduation: "لتخرجك", party: "لحفلتك" };
var PATTERNS = [
  [/^([\d,]+) ready-made designs for (your business|your wedding|your graduation|your party or event|your home)\. Tap one to change the colors and the words, add your (logo|photo) and see it right away\.$/, function (_, n, w, x) { return "تصاميم جاهزة " + FOR[w] + ": " + n + ". اضغط على أي منها لتغيّر الألوان والكلمات، وتضيف " + (x === "logo" ? "شعارك" : "صورتك") + " وتشاهد النتيجة فورًا."; }],
  [/^(\d+) kinds · ([\d,]+) designs$/, function (_, k, d) { return cnt(k, ["نوع واحد", "نوعان", "أنواع", "نوعًا", "نوع"]) + " · " + des(d); }],
  [/^(\d+) (magnets?) · \$([\d.]+)(?: \(\$([\d.]+) each\))?$/, function (_, n, m, p, e) { return mag(n) + " · $" + p + (e ? " ($" + e + " للقطعة)" : ""); }],
  [/^From \$(\d+) a magnet$/, "ابتداءً من $$$1 للمغناطيس"],
  [/^\$([\d.]+) · sent to your email$/, "$$$1 · يُرسل إلى بريدك"],
  [/^Hundreds of designs to make yours: change the words and colors, add a photo\. From \$(\d+)\.$/, "مئات التصاميم لتجعلها لك: غيّر الكلمات والألوان، وأضف صورة. ابتداءً من $$$1."],
  [/^Every magnet is made just for you\. Want only the design\? \$([\d.]+) for the file, free with any magnet\.$/, "كل مغناطيس يُصنع لك وحدك. تريد التصميم فقط؟ $$$1 للملف، ومجانًا مع أي مغناطيس."],
  [/^Yes\. Tap the design, make it yours and choose “Only want the file”: \$([\d.]+), sent to your email right away, no magnet\. It is free with any magnet order\.$/, "نعم. اضغط على التصميم، اجعله لك واختر \"تريد الملف فقط\": $$$1، يُرسل إلى بريدك فورًا، بلا مغناطيس. ومجاني مع أي طلب مغناطيسات."],
  [/^([^·<]{2,40}) · ([^·<]{2,40})$/, function (_, a, b) { var x = tr(a), y = tr(b); return x !== a || y !== b ? x + " · " + y : null; }],
  [/^1 magnet$/, "مغناطيس واحد"],
  [/^(\d+) photo designs with names, dates and captions$/, function (_, n) { return cnt(n, ["تصميم صور واحد", "تصميما صور", "تصاميم صور", "تصميم صور", "تصميم صور"]) + " بالأسماء والتواريخ والتعليقات"; }],
  [/^\$(\d+) · \$([\d.]+) each$/, "$$$1 · $$$2 للقطعة"],
  [/^Photo ([\d, ]+) didn't finish uploading\. Please try again\.$/, "الصورة $1 لم يكتمل رفعها. حاول مرة أخرى."],
  [/^Photo (\d+) didn't upload correctly\. Please remove it and add it again\.$/, "الصورة $1 لم تُرفع بشكل صحيح. أزِلها وأضفها مرة أخرى."],
  [/^Photo (\d+) is too big or empty\.$/, "الصورة $1 كبيرة جدًا أو فارغة."],
  [/^Cart <span>(\d+)<\/span>$/, "السلة <span>$1</span>"],
  [/^Order today and it arrives about (.+) in the US\. <a>Shipping details<\/a>$/, function (_, d) { return "اطلب اليوم ويصلك داخل أمريكا نحو " + date(d) + ". <a>تفاصيل الشحن</a>"; }],
  // cart, photo builder, checkout (assets/site.js, custom.js, checkout.js)
  [/^One less (.+)$/, function (_, x) { return "واحد أقل: " + iso(x); }],
  [/^One more (.+)$/, function (_, x) { return "واحد إضافي: " + iso(x); }],
  [/^Add (\d+) more magnets for (\d+)% off your whole order\.$/, function (_, k, p) { return "أضف " + mag(k) + " أخرى واحصل على خصم " + p + "% على الطلب كله."; }],
  [/^Order today and it arrives about (.+) in the US\.$/, function (_, d) { return "اطلب اليوم ويصلك داخل أمريكا نحو " + date(d) + "."; }],
  [/^Custom photo magnets$/, "مغناطيسات صور مخصّصة"],
  [/^(.+) added to cart$/, function (_, x) { return "أُضيف إلى السلة: " + iso(tr(x)); }],
  [/^Your (\d+) magnets are in the cart$/, function (_, n) { return "في سلتك الآن: " + mag(n); }],
  [/^(\d+) magnets · we plan the design with you by email after checkout$/, function (_, n) { return mag(n) + " · نخطط للتصميم معك بالبريد بعد الدفع"; }],
  // bulk-order pages (business, weddings, graduation, parties): packs, the mailing service, the QR maker
  [/^(\d+) magnets · \$([\d.,]+) \(\$([\d.,]+) each\)$/, function (_, n, p, e) { return mag(n) + " · $" + p + " ($" + e + " للقطعة)"; }],
  [/^(\d+) addresses$/, function (_, n) { return cnt(n, ADDR); }],
  [/^(\d+) addresses · we ask for your list after checkout$/, function (_, n) { return cnt(n, ADDR) + " · نطلب قائمتك بعد الدفع"; }],
  [/^(\d+) magnets · style: (.+) · we plan the design with you by email after checkout$/, function (_, n, s) { return mag(n) + " · النمط: " + tr(s) + " · نخطط للتصميم معك بالبريد بعد الدفع"; }],
  [/^(\d+) QR magnets · (.+) · proof before we print$/, function (_, n, x) { return cnt(n, ["مغناطيس QR واحد", "مغناطيسا QR", "مغناطيسات QR", "مغناطيس QR", "مغناطيس QR"]) + " · " + x + " · نموذج قبل الطباعة"; }],
  [/^Mailed to your list, (\d+) addresses$/, function (_, n) { return "يُرسل بالبريد إلى قائمتك، " + cnt(n, ADDR); }],
  [/^Graduation & college, (\d+) magnets$/, function (_, n) { return "التخرج والجامعة، " + mag(n); }],
  [/^(\d+) magnets · (\d+) photos? · (\d+) frames$/, function (_, a, b, f) { return mag(a) + " · " + pho(b) + " · " + cnt(f, FRM); }],
  [/^(\d+) magnets · (\d+) photos? · (.+)$/, function (_, a, b, f) { return mag(a) + " · " + pho(b) + " · " + fr(f); }],
  [/^2 × 2 in · (.+)$/, function (_, c) { return "2 × 2 إنش · " + col(c); }],
  [/^(.+) magnet$/, function (_, x) { return "مغناطيس " + iso(x); }],
  [/^Remove photo (\d+)$/, "إزالة الصورة $1"],
  [/^1 photo is too small and may print blurry\. (.+)$/, "صورة واحدة صغيرة جدًا وقد تُطبع ضبابية. للحصول على مغناطيس واضح، استخدم الصورة الأصلية من ألبوم الكاميرا، لا لقطة شاشة أو صورة محفوظة من تطبيق محادثة."],
  [/^(\d+) photos are too small and may print blurry\. (.+)$/, function (_, n) { return "عدد الصور الصغيرة جدًا: " + n + "، وقد تُطبع ضبابية. للحصول على مغناطيس واضح، استخدم الصورة الأصلية من ألبوم الكاميرا، لا لقطة شاشة أو صورة محفوظة من تطبيق محادثة."; }],
  [/^(\d+) photos added\. This pack holds (\d+), so remove (\d+) or pick a bigger pack\.$/, "أضفت $1 صورة. هذه الباقة تتسع لـ $2، لذا أزِل $3 أو اختر باقة أكبر."],
  [/^(\d+) of (\d+) photos added\. We will repeat your favorites to fill the pack, or tell us in the notes\.$/, "أُضيفت $1 من $2 صورة. سنكرر صورك المفضلة لملء الباقة، أو أخبرنا في الملاحظات."],
  [/^Frame for photo (\d+)$/, "إطار الصورة $1"],
  [/^Photo (\d+): (.+) frame(, caption (.+?))?(, low resolution)?\. Choose frame$/, function (_, k, f, c1, c, low) { return "الصورة " + k + ": إطار " + fr(f) + (c ? "، التعليق " + c : "") + (low ? "، دقة منخفضة" : "") + ". اختر الإطار"; }],
  [/^Preview of photo (\d+) with the (.+?) frame( and the caption (.+))?$/, function (_, k, f, c1, c) { return "معاينة الصورة " + k + " بإطار " + fr(f) + (c ? " والتعليق " + c : ""); }],
  [/^Apply this frame to all (\d+) photos$/, "طبّق هذا الإطار على كل الصور ($1)"],
  [/^(.+) is now on all (\d+) photos\.$/, function (_, f, k) { return "إطار " + fr(f) + " الآن على كل الصور (" + k + ")."; }],
  [/^Caption added to all (\d+) photos\. It prints on photos with a caption frame\.$/, "أُضيف التعليق إلى كل الصور ($1). يُطبع على الصور ذات إطار التعليق."],
  [/^All (\d+) photos uploaded$/, "رُفعت كل الصور ($1)"],
  [/^Uploading your photo · (\d+)%$/, "جارٍ رفع صورتك · $1%"],
  [/^Uploading your (\d+) photos · (\d+)%$/, "جارٍ رفع صورك ($1) · $2%"],
  // orders, account, returns (assets/orders.js, account.js, return.js)
  [/^Tracking history \((\d+) scans?\)$/, "سجل التتبّع ($1)"],
  [/^(.+) has your package out for delivery\. Keep an eye on the porch!$/, "طردك خرج للتوصيل مع $1. راقب باب البيت!"],
  [/^Your package is with (.+?)\.( It shipped on (.+?)\.)?( We’ll email you when it’s out for delivery and when it arrives\.)?$/, function (_, c, s1, d, tail) { return "طردك لدى " + c + "." + (d ? " شُحن في " + d + "." : "") + (tail ? " سنراسلك عندما يخرج للتوصيل وعندما يصل." : ""); }],
  [/^Delivered on (.+?)\. We hope you love them!$/, "تم التوصيل في $1. نتمنى أن تعجبك!"],
  [/^We hope you love them!$/, "نتمنى أن تعجبك!"],
  [/^We refunded (\$[\d.,]+)\. Refunds take 5 to 10 business days to show on your statement\.$/, "استرددنا لك $1. يستغرق ظهور الاسترداد في كشف حسابك من 5 إلى 10 أيام عمل."],
  [/^Rating for (.+)$/, function (_, x) { return "تقييم " + iso(x); }],
  [/^Thank you, (.+)!$/, function (_, x) { return "شكرًا، " + iso(x) + "!"; }],
  [/^Order (LHH-\d+) is confirmed\. We emailed you a receipt, so keep it handy for tracking\.$/, "تم تأكيد الطلب $1. أرسلنا لك إيصالًا بالبريد، احتفظ به للتتبّع."],
  [/^Check your inbox\. If there’s an account for (.+?), we just sent a link to choose a new password\.( It can take a minute, and sometimes lands in spam\.)?$/, function (_, e, tail) { return "تفقّد بريدك الوارد. إن كان هناك حساب لـ " + e + "، فقد أرسلنا للتو رابطًا لاختيار كلمة مرور جديدة." + (tail ? " قد يستغرق دقيقة، وأحيانًا يصل إلى البريد العشوائي." : ""); }],
  [/^See all (\d+) orders$/, "عرض كل الطلبات ($1)"],
  [/^We found (\d+) earlier orders with your email and added them to your account\.$/, function (_, n) { return "وجدنا " + cnt(n, ["طلبًا سابقًا واحدًا", "طلبين سابقين", "طلبات سابقة", "طلبًا سابقًا", "طلب سابق"]) + " ببريدك وأضفناها إلى حسابك."; }],
  [/^Signed in as (.+)\.$/, "مسجّل الدخول باسم $1."],
  [/^We emailed (.+) a link to choose a new password\.$/, "أرسلنا إلى $1 رابطًا لاختيار كلمة مرور جديدة."],
  [/^Your account and orders \(signed in as (.+)\)$/, "حسابك وطلباتك (مسجّل الدخول باسم $1)"],
  [/^(.+) saved to your favorites$/, function (_, x) { return "حُفظ في المفضلة: " + iso(tr(x)); }],
  [/^(.+) removed from favorites$/, function (_, x) { return "أُزيل من المفضلة: " + iso(tr(x)); }],
  [/^Refunded (\$[\d.,]+) on (.+)\.$/, "استُرد $1 في $2."],
  [/^(\$[\d.,]+) back to your card on (.+)$/, "عاد $1 إلى بطاقتك في $2"],
  [/^Your refund: (\$[\d.,]+) \((\$[\d.,]+) for the magnets − (\$[\d.,]+) return shipping\)\.$/, "المبلغ المسترد: $1 ($2 للمغناطيسات − $3 شحن الإرجاع)."],
  [/^(\d+) magnets · (\$[\d.,]+) each$/, function (_, n, e) { return mag(n) + " · " + e + " للقطعة"; }],
  [/^(\$[\d.,]+) each$/, "$1 للقطعة"],
  [/^This account is turned off\. Email (.+) and we’ll sort it out\.$/, "هذا الحساب معطّل. راسل $1 وسنحل الأمر."],
  [/^We couldn’t save one of your photos\. (.+?) or email (.+?)\.?$/, "تعذّر حفظ إحدى صورك. جرّب صورة عادية أقل من 25 ميغابايت (JPG أو PNG أو HEIC أو WebP)، أو راسل $2."],
  [/^We can’t take photo uploads right now\. Please email (.+)$/, "لا يمكننا استقبال الصور الآن. راسل $1"],
  [/^Something went wrong on our side\. Please try again, or email (.+)$/, "حدث خطأ من جهتنا. حاول مرة أخرى، أو راسل $1"],
  [/^This link has expired or is incomplete\. Email (.+) and we’ll remove you by hand\.$/, "هذا الرابط منتهي الصلاحية أو ناقص. راسل $1 وسنزيلك يدويًا."],
  [/^Your email app should open now\. If it doesn't, write to us at (.+)$/, "سيُفتح تطبيق البريد الآن. إن لم يُفتح، راسلنا على $1"],
  [/^Ordering today\? Most US orders arrive <strong>about (.+)<\/strong>\.$/, function (_, d) { return "تطلب اليوم؟ معظم الطلبات داخل أمريكا تصل <strong>نحو " + date(d) + "</strong>."; }],
  [/^(\d+) photos? added, (\$[\d.,]+) each$/, function (_, n, e) { return "أُضيفت " + pho(n) + "، " + e + " للصورة"; }],
  [/^Add 1 to 3 photos, (\$[\d.,]+) each$/, "أضف من 1 إلى 3 صور، $1 للصورة"],
  [/^Add 1 more photo and get the pack of 4 for (\$[\d.,]+)\.$/, "أضف صورة واحدة أخرى واحصل على باقة الـ 4 بـ $1."],
  [/^(\d+) photos: pack of (\d+) \+ (\d+) extra photos? \((\$[\d.,]+) each\)$/, "$1 صورة: باقة $2 + $3 إضافية ($4 للصورة)"],
  [/^Only want (\d+) magnets?\? Make just these for (\$[\d.,]+)$/, function (_, n, p) { return "تريد " + mag(n) + " فقط؟ اصنع هذه فقط بـ " + p; }],
  [/^Add (\d+) more photos? at no extra cost: they fit in your pack of (\d+)\.$/, "أضف $1 صورة أخرى بلا تكلفة إضافية: تتسع لها باقتك ذات الـ $2."],
  [/^Want more\? Add 1 more photo for (\$[\d.,]+), or 2 for (\$[\d.,]+)\.$/, "تريد المزيد؟ أضف صورة أخرى بـ $1، أو صورتين بـ $2."],
  [/^Same price, more room: we moved you to the pack of (\d+)\. Add (\d+) more photos? at no extra cost\.$/, "السعر نفسه ومساحة أكبر: نقلناك إلى باقة الـ $1. أضف $2 صورة أخرى بلا تكلفة إضافية."],
  [/^A photo order holds up to (\d+) photos, so (\d+) (?:was|were) not added\.$/, "طلب الصور يتسع حتى $1 صورة، لذا لم تُضف $2."],
  [/^(\d+) of (\d+) photos added$/, "أُضيفت $1 من $2 صورة"],
  [/^Photo (\d+) of (\d+)$/, "الصورة $1 من $2"],
  [/^<span>(\d+\/\d+)<\/span> · Optional, leave empty for none$/, "<span>$1</span> · اختياري، اتركه فارغًا إن لم ترده"],
  [/^(\d+) designs · \$5 each$/, function (_, n) { return des(n) + " · $5 للقطعة"; }],
  [/^(\d+) countries · (\d+) designs · \$5 each$/, function (_, c, n) { return cnt(c, CTRY) + " · " + des(n) + " · $5 للقطعة"; }],
  [/^See all (\d+)$/, "عرض الكل ($1)"],
  [/^Add all (\d+) to cart$/, "أضف الكل إلى السلة ($1)"],
  [/^Ships in 1–2 business days\. Order today and it arrives <strong>about (.+)<\/strong> in the US\.$/, function (_, d) { return "يُشحن خلال 1–2 يوم عمل. اطلب اليوم ويصلك داخل أمريكا <strong>نحو " + date(d) + "</strong>."; }],
  [/^\$([\d.,]+) each$/, "$$$1 للقطعة"],
  [/^Buy now · \$([\d.,]+)$/, "اشترِ الآن · $$$1"],
  [/^Digital file · (.+) · sent to your email · no magnet$/, function (_, t) { return "ملف رقمي · " + iso(tr(t)) + " · يُرسل إلى بريدك · بلا مغناطيس"; }],
  [/^Service (\d)$/, "الخدمة $1"],
  [/^Line (\d+)$/, "السطر $1"],
  [/^Line (\d+), right side$/, "السطر $1، الجهة اليمنى"],
  [/^(\d+) ready-made designs for your (business|wedding|graduation|party)\. Tap one to change the colors and the words, add your logo and see it right away\.$/, function (_, n, w) { return "تصاميم جاهزة " + FOR[w] + ": " + n + ". اضغط على أي منها لتغيّر الألوان والكلمات، وتضيف شعارك وتشاهد النتيجة فورًا."; }],
  [/^Pack size for (.+)$/, function (_, c) { return "حجم الباقة: " + tr(c); }],
  [/^(.+?) <small>([\d,]+\+?)<\/small>$/, function (_, c, k) { return (c === "All" ? "الكل" : tr(c)) + " <small>" + k + "</small>"; }],
  [/^(.+) · (\d+) countries · (\d+) designs$/, function (_, a, k, d) { return tr(a) + " · " + cnt(k, CTRY) + " · " + des(d); }],
  [/^(.+) · (\d+) designs$/, function (_, a, k) { return tr(a) + " · " + des(k); }],
  // design pages and lists
  [/^See (.+) larger$/, function (_, x) { return "تكبير: " + iso(x); }],
  [/^Favorite: (.+)$/, function (_, x) { return "إلى المفضلة: " + iso(x); }],
  [/^Remove from favorites: (.+)$/, function (_, x) { return "إزالة من المفضلة: " + iso(x); }],
  [/^(.+) fridge magnet$/, function (_, x) { return "مغناطيس ثلاجة " + iso(x); }],
  [/^(.+) magnet · Little Hive House$/, function (_, x) { return "مغناطيس " + iso(x) + " · Little Hive House"; }],
  [/^(.+) magnets · Little Hive House$/, function (_, c) { return "مغناطيسات " + col(c) + " · Little Hive House"; }],
  [/^(.+) · Little Hive House$/, function (_, c) { var x = COL[c] || (window.LHH_I18N && LHH_I18N.t(c)) || c; return x !== c || known(c) ? x + " · Little Hive House" : null; }],
  [/^All (.{1,40}) designs$/, function (_, c) { return known(c) ? "كل تصاميم " + col(c) : null; }],
  [/^More from (.{1,40})$/, function (_, c) { return known(c) ? "المزيد من " + col(c) : null; }],
  [/^(.{1,40}) on the fridge$/, function (_, c) { return known(c) ? col(c) + " على الثلاجة" : null; }],
  [/^(.+) on the fridge · (\d+) designs$/, function (_, c, k) { return known(c) ? col(c) + " على الثلاجة · " + des(k) : null; }],
  [/^(\d[\d,]*) designs?$/, function (_, n) { return des(n); }],
  [/^(\d[\d,]*)\+ designs$/, "أكثر من $1 تصميم"],
  [/^(\d+) magnets?$/, function (_, n) { return mag(n); }],
  [/^(\d+) items?$/, function (_, n) { return cnt(n, ["منتج واحد", "منتجان", "منتجات", "منتجًا", "منتج"]); }],
  [/^(\d+) photos?$/, function (_, n) { return pho(n); }],
  [/^(\d+) collections$/, function (_, n) { return cnt(n, ["مجموعة واحدة", "مجموعتان", "مجموعات", "مجموعة", "مجموعة"]); }],
  [/^See all (\d+) designs$/, function (_, n) { return "عرض كل التصاميم (" + n + ")"; }],
  [/^See (\d+) more designs?$/, function (_, n) { return "عرض " + des(n) + " أخرى"; }],
  [/^Show (\d+) more$/, "عرض $1 أخرى"],
  [/^Big order, (\d+) magnets \((\d+)% off\)$/, function (_, k, p) { return "طلب كبير، " + mag(k) + " (خصم " + p + "%)"; }],
  [/^Add \$([\d.]+) more for free US shipping\.$/, "أضف $$$1 أخرى للحصول على شحن مجاني داخل أمريكا."],
  [/^Order today, it arrives <strong>about (.+)<\/strong> in the US · <a>Shipping details<\/a>$/, function (_, d) { return "اطلب اليوم ويصلك داخل أمريكا <strong>نحو " + date(d) + "</strong> · <a>تفاصيل الشحن</a>"; }],
  [/^about (.+\d.*)$/, function (_, d) { return "نحو " + date(d); }],
  [/^Updated (.+)$/, function (_, d) { return "حُدّث في " + date(d); }],
  [/^Ordered (.+)$/, function (_, d) { return "طُلب في " + date(d); }],
  [/^Delivered (.+)$/, function (_, d) { return "وصل في " + date(d); }],
  [/^Shipped (.+)$/, function (_, d) { return "شُحن في " + date(d); }],
  [/^Order (LHH-\d+)$/, "الطلب $1"],
  [/^Qty (\d+)$/, "الكمية $1"],
  [/^Magnet (\d+)$/, "المغناطيس $1"],
  [/^Photo (\d+)$/, "الصورة $1"],
  [/^Step (\d+) of (\d+)$/, "الخطوة $1 من $2"],
  [/^(\d+)% off everything, or buy (\d+) designs, get (\d+) free(.*)$/, function (_, p, b, g, rest) { return "خصم " + p + "% على كل شيء، أو اشترِ " + b + " واحصل على " + g + " مجانًا" + saleEnd(rest); }],
  [/^today only: (\d+)% off everything( \+ free shipping)?(.*)$/, function (_, p, f, rest) { return "اليوم فقط: خصم " + p + "% على كل شيء" + (f ? " + شحن مجاني" : "") + saleEnd(rest); }],
  [/^(Black Friday|Cyber Monday), (\d+)% off$/, function (_, n, p) { return ev(n) + "، خصم " + p + "%"; }],
  [/^(Black Friday|Cyber Monday), (\d+) designs? free$/, function (_, n, k) { return ev(n) + ": " + k + " مجانًا"; }],
  [/^(Black Friday|Cyber Monday): add (\d+) more designs? and (\d+) of them (?:is|are) free\.$/, function (_, n, a, f) { return ev(n) + ": أضف " + des(a) + " أخرى ويكون " + f + " منها مجانًا."; }],
  [/^(Black Friday|Cyber Monday): free shipping on every order today\.$/, function (_, n) { return ev(n) + ": شحن مجاني لكل الطلبات اليوم."; }],
  [/^(\d+) of (\d+)$/, "$1 من $2"],
  /* photo swap on the order pages (assets/orders.js, functions/photoswap.js) */
  [/^Change photo (\d+)$/, "تغيير الصورة $1"],
  [/^Photo (\d+) was changed for a new one\.$/, "تم استبدال الصورة $1 بصورة جديدة."],
  [/^Photo (\d+) \(pack (\d+)\) was changed for a new one\.$/, "تم استبدال الصورة $1 (المجموعة $2) بصورة جديدة."],
  [/^Pack (\d+)$/, "المجموعة $1"],
  [/^Photo (\d+): change or remove$/, "الصورة $1: تبديل أو إزالة"],
  [/^Remove photo (\d+)\?$/, "إزالة الصورة $1؟"],
  [/^You’ll get (\d+) magnets and pay (\$[\d.,]+) less\.$/, "ستحصل على $1 مغناطيس وتدفع أقل بمقدار $2."],
  [/^Swap it for another photo \(same price\), or remove it \((\$[\d.,]+) less\)\.$/, "استبدلها بصورة أخرى (بالسعر نفسه) أو أزلها (أقل بمقدار $1)."],
  [/^Removing photo (\d+)…$/, "جارٍ إزالة الصورة $1…"],
  [/^Done! Photo (\d+) was removed\. You now have (\d+) magnets and your new total is (\$[\d.,]+)\.$/, "تم! أُزيلت الصورة $1. لديك الآن $2 مغناطيس والإجمالي الجديد $3."],
  [/^Done! Photo (\d+) was removed\. You now have (\d+) magnets and we refunded (\$[\d.,]+) to your card\.$/, "تم! أُزيلت الصورة $1. لديك الآن $2 مغناطيس وأعدنا $3 إلى بطاقتك."],
  [/^Photo (\d+) was removed\. (\d+) magnets now\.$/, "أُزيلت الصورة $1. الآن $2 مغناطيس."],
  [/^Photo (\d+) \(pack (\d+)\) was removed\. (\d+) magnets now\.$/, "أُزيلت الصورة $1 (المجموعة $2). الآن $3 مغناطيس."]
];
/* the end of the sale bar's text: " · through Cyber Monday" or " · ends in 5h 12m" */
function saleEnd(rest) {
  if (!rest) return "";
  if (/through Cyber Monday/.test(rest)) return " · حتى الاثنين الإلكتروني";
  var m = /ends in (.*)$/.exec(rest);
  return m ? " · ينتهي خلال " + m[1].replace(/(\d+)d\b/, "$1 يوم").replace(/(\d+)h\b/, "$1 س").replace(/(\d+)m\b/, "$1 د") : rest;
}
