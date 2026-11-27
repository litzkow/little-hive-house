/* Patterns: English text with a number, a date or a name in it. Each is [regex, Russian] where the Russian is a
   replacement string ($1…) or a function of the match. Checked in order, after the exact dictionary.
   Formal «вы». Prices keep the US format ($5.49, 1,200). Counted words follow Russian plural rules (pl). */
var COL = {
  "USA Places": "Места США", "World Places": "Места мира", "Ink Cities": "Города тушью",
  "City Sketches": "Городские скетчи", "Fall": "Осень", "Halloween": "Хэллоуин", "Horror Classics": "Классика ужасов",
  "Furry Friends": "Пушистые друзья", "Kitchen Words": "Кухонные слова", "Americana": "Американа", "México": "Мексика",
  "Ireland": "Ирландия", "Italia": "Италия", "Puerto Rico": "Пуэрто-Рико", "Pilipinas": "Филиппины", "India": "Индия",
  "Korea": "Корея", "Japan": "Япония", "Brasil": "Бразилия", "Greece": "Греция", "France": "Франция",
  "Great Masters": "Великие мастера", "Mythology": "Мифология", "Home Notes": "Записки для дома", "Bee Kind": "Bee Kind",
  "Night Sky": "Ночное небо", "Birth Flowers": "Цветы месяца рождения", "Storybook Classics": "Классика литературы",
  "Fairy Tales & Myths": "Сказки и мифы", "Wise Words": "Мудрые слова", "Holidays & Dates": "Праздники и даты",
  "Bumper Stickers": "Наклейки на бампер", "Christmas": "Рождество", "Summer": "Лето", "Heritage": "Корни",
  "Photo magnets": "Фотомагниты", "Custom photo magnets": "Фотомагниты на заказ"
};
var FRAME = { "Arch": "Арка", "Art deco": "Ар-деко", "Autumn": "Осень", "Birthday": "День рождения", "Botanical": "Ботаника",
  "Circle": "Круг", "Classic": "Классика", "Crisp white mat": "Белое паспарту", "Date stamp": "Штамп с датой",
  "Eucalyptus wreath": "Венок из эвкалипта", "Film frame": "Кадр плёнки", "Full photo": "Фото целиком",
  "Gallery mat": "Галерейное паспарту", "Gallery with caption": "Галерея с подписью", "Gold line": "Золотая линия",
  "Graduation": "Выпускной", "Handwritten": "От руки", "Holiday": "Праздник", "Honeycomb": "Соты",
  "Instant print": "Моментальное фото", "Love": "Любовь", "Modern": "Модерн", "Name band": "Лента с именем",
  "Postage stamp": "Почтовая марка", "Postcard": "Открытка", "Rounded modern": "Скруглённый модерн",
  "Scalloped lace": "Кружево фестонами", "Script": "Каллиграфия", "Sweet dreams": "Сладких снов", "Team": "Команда",
  "Thin white border": "Тонкая белая рамка", "Tropical leaves": "Тропические листья", "Vintage ornate gold": "Винтажное золото",
  "Watercolour peonies": "Акварельные пионы", "Wedding": "Свадьба", "Winter": "Зима", "No border": "Без рамки" };
function fr(s) { return FRAME[s] || s; }
function col(s) { return COL[s] || s; }
/** only for the shop's own collection names: anything else is left to the dictionary */
function known(s) { return Object.prototype.hasOwnProperty.call(COL, s) || /^(Americana|México|Brasil|Halloween|Bee Kind)$/.test(s); }
/** Russian plural: pl(5, "магнит", "магнита", "магнитов") → "магнитов" */
function pl(n, one, few, many) {
  n = Math.abs(parseInt(String(n).replace(/[^\d]/g, ""), 10) || 0);
  var a = n % 10, b = n % 100;
  return a === 1 && b !== 11 ? one : a >= 2 && a <= 4 && (b < 12 || b > 14) ? few : many;
}
function nw(n, one, few, many) { return n + " " + pl(n, one, few, many); }
function mag(n) { return nw(n, "магнит", "магнита", "магнитов"); }
function des(n) { return nw(n, "дизайн", "дизайна", "дизайнов"); }
var MON = { Jan: 0, Feb: 1, Mar: 2, Apr: 3, May: 4, Jun: 5, Jul: 6, Aug: 7, Sep: 8, Oct: 9, Nov: 10, Dec: 11,
  January: 0, February: 1, March: 2, April: 3, June: 5, July: 6, August: 7, September: 8, October: 9, November: 10, December: 11 };
var GEN = ["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября", "октября", "ноября", "декабря"];
var NOM = ["январь", "февраль", "март", "апрель", "май", "июнь", "июль", "август", "сентябрь", "октябрь", "ноябрь", "декабрь"];
var DAY = { Mon: "пн", Tue: "вт", Wed: "ср", Thu: "чт", Fri: "пт", Sat: "сб", Sun: "вс",
  Monday: "понедельник", Tuesday: "вторник", Wednesday: "среда", Thursday: "четверг", Friday: "пятница", Saturday: "суббота", Sunday: "воскресенье" };
var M = "(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)";
/* "Nov 17–20" → "17–20 ноября"; "Nov 28–Dec 2" → "28 ноября – 2 декабря"; "November 3, 2026" → "3 ноября 2026 г.";
   "Tue, Nov 17" → "вт, 17 ноября" */
function date(s) {
  return s
    .replace(/\b(Mon|Tue|Wed|Thu|Fri|Sat|Sun|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b/g, function (_, x) { return DAY[x]; })
    .replace(new RegExp(M + " (\\d{1,2}), (\\d{4})", "g"), function (_, m, d, y) { return d + " " + GEN[MON[m]] + " " + y + " г."; })
    .replace(new RegExp(M + " (\\d{1,2})[–-](\\d{1,2})\\b", "g"), function (_, m, a, b) { return a + "–" + b + " " + GEN[MON[m]]; })
    .replace(new RegExp(M + " (\\d{1,2})[–-]" + M + " (\\d{1,2})", "g"), function (_, m1, a, m2, b) { return a + " " + GEN[MON[m1]] + " – " + b + " " + GEN[MON[m2]]; })
    .replace(new RegExp(M + " (\\d{1,2})\\b", "g"), function (_, m, d) { return d + " " + GEN[MON[m]]; })
    .replace(new RegExp(M + " (\\d{4})", "g"), function (_, m, y) { return NOM[MON[m]] + " " + y; });
}
function tr(s) { return COL[s] || (window.LHH_I18N ? window.LHH_I18N.t(s) : s); }
function ev(n) { return n === "Black Friday" ? "Чёрная пятница" : n === "Cyber Monday" ? "Киберпонедельник" : n; }
var FOR = { "your business": "вашего бизнеса", "your wedding": "вашей свадьбы", "your graduation": "вашего выпускного", "your party or event": "вашего праздника или мероприятия", "your home": "вашего дома",
  business: "вашего бизнеса", wedding: "вашей свадьбы", graduation: "вашего выпускного", party: "вашего праздника" };
var PATTERNS = [
  [/^([\d,]+) ready-made designs for (your business|your wedding|your graduation|your party or event|your home)\. Tap one to change the colors and the words, add your (logo|photo) and see it right away\.$/, function (_, n, w, x) { return n + " " + pl(n, "готовый дизайн", "готовых дизайна", "готовых дизайнов") + " для " + FOR[w] + ". Нажмите на любой, чтобы поменять цвета и слова, добавить " + (x === "logo" ? "логотип" : "фото") + " и сразу увидеть результат."; }],
  [/^(\d+) kinds · ([\d,]+) designs$/, function (_, k, d) { return nw(k, "вид", "вида", "видов") + " · " + des(d); }],
  [/^(\d+) (magnets?) · \$([\d.]+)(?: \(\$([\d.]+) each\))?$/, function (_, n, m, p, e) { return mag(n) + " · $" + p + (e ? " ($" + e + " за шт.)" : ""); }],
  [/^From \$(\d+) a magnet$/, "От $$$1 за магнит"],
  [/^\$([\d.]+) · sent to your email$/, "$$$1 · придёт на почту"],
  [/^Hundreds of designs to make yours: change the words and colors, add a photo\. From \$(\d+)\.$/, "Сотни дизайнов, которые можно сделать своими: поменяйте слова и цвета, добавьте фото. От $$$1."],
  [/^Every magnet is made just for you\. Want only the design\? \$([\d.]+) for the file, free with any magnet\.$/, "Каждый магнит делается специально для вас. Нужен только дизайн? Файл за $$$1, бесплатно с любым магнитом."],
  [/^Yes\. Tap the design, make it yours and choose “Only want the file”: \$([\d.]+), sent to your email right away, no magnet\. It is free with any magnet order\.$/, "Да. Нажмите на дизайн, сделайте его своим и выберите «Нужен только файл»: $$$1, сразу придёт на почту, без магнита. С любым заказом магнитов бесплатно."],
  [/^([^·<]{2,40}) · ([^·<]{2,40})$/, function (_, a, b) { var x = tr(a), y = tr(b); return x !== a || y !== b ? x + " · " + y : null; }],
  [/^1 magnet$/, "1 магнит"],
  [/^(\d+) photo designs with names, dates and captions$/, function (_, n) { return n + " " + pl(n, "фотодизайн", "фотодизайна", "фотодизайнов") + " с именами, датами и подписями"; }],
  [/^\$(\d+) · \$([\d.]+) each$/, "$$$1 · $$$2 за шт."],
  [/^Photo ([\d, ]+) didn't finish uploading\. Please try again\.$/, "Фото $1 не догрузилось. Попробуйте ещё раз."],
  [/^Photo (\d+) didn't upload correctly\. Please remove it and add it again\.$/, "Фото $1 загрузилось неправильно. Удалите его и добавьте снова."],
  [/^Photo (\d+) is too big or empty\.$/, "Фото $1 слишком большое или пустое."],
  [/^Cart <span>(\d+)<\/span>$/, "Корзина <span>$1</span>"],
  [/^Order today and it arrives about (.+) in the US\. <a>Shipping details<\/a>$/, function (_, d) { return "Закажите сегодня, и по США он придёт примерно " + date(d) + ". <a>О доставке</a>"; }],
  // cart, photo builder, checkout (assets/site.js, custom.js, checkout.js)
  [/^One less (.+)$/, "На один меньше: $1"],
  [/^One more (.+)$/, "Ещё один: $1"],
  [/^Add (\d+) more magnets for (\d+)% off your whole order\.$/, function (_, k, p) { return "Добавьте ещё " + mag(k) + " и получите скидку " + p + "% на весь заказ."; }],
  [/^Order today and it arrives about (.+) in the US\.$/, function (_, d) { return "Закажите сегодня, и по США он придёт примерно " + date(d) + "."; }],
  [/^Custom photo magnets$/, "Фотомагниты на заказ"],
  [/^(.+) added to cart$/, function (_, x) { return "Добавлено в корзину: " + tr(x); }],
  [/^Your (\d+) magnets are in the cart$/, function (_, n) { return "В корзине " + mag(n); }],
  [/^(\d+) magnets · we plan the design with you by email after checkout$/, function (_, n) { return mag(n) + " · после оплаты продумаем дизайн вместе с вами по почте"; }],
  // bulk-order pages (business, weddings, graduation, parties): packs, the mailing service, the QR maker
  [/^(\d+) magnets · \$([\d.,]+) \(\$([\d.,]+) each\)$/, function (_, n, p, e) { return mag(n) + " · $" + p + " ($" + e + " за шт.)"; }],
  [/^(\d+) addresses$/, function (_, n) { return nw(n, "адрес", "адреса", "адресов"); }],
  [/^(\d+) addresses · we ask for your list after checkout$/, function (_, n) { return nw(n, "адрес", "адреса", "адресов") + " · список попросим после оплаты"; }],
  [/^(\d+) magnets · style: (.+) · we plan the design with you by email after checkout$/, function (_, n, s) { return mag(n) + " · стиль: " + tr(s) + " · после оплаты продумаем дизайн вместе с вами по почте"; }],
  [/^(\d+) QR magnets · (.+) · proof before we print$/, function (_, n, x) { return n + " " + pl(n, "QR-магнит", "QR-магнита", "QR-магнитов") + " · " + x + " · макет до печати"; }],
  [/^Mailed to your list, (\d+) addresses$/, function (_, n) { return "Рассылка по вашему списку, " + nw(n, "адрес", "адреса", "адресов"); }],
  [/^Graduation & college, (\d+) magnets$/, function (_, n) { return "Выпускной и колледж, " + mag(n); }],
  [/^(\d+) magnets · (\d+) photos? · (\d+) frames$/, function (_, a, b, f) { return mag(a) + " · " + b + " фото · " + nw(f, "рамка", "рамки", "рамок"); }],
  [/^(\d+) magnets · (\d+) photos? · (.+)$/, function (_, a, b, f) { return mag(a) + " · " + b + " фото · " + fr(f); }],
  [/^2 × 2 in · (.+)$/, function (_, c) { return "2 × 2 дюйма · " + col(c); }],
  [/^(.+) magnet$/, "Магнит «$1»"],
  [/^Remove photo (\d+)$/, "Удалить фото $1"],
  [/^1 photo is too small and may print blurry\. (.+)$/, "1 фото слишком маленькое и может напечататься размыто. Для чёткого магнита используйте оригинал из галереи телефона, а не скриншот или фото, сохранённое из мессенджера."],
  [/^(\d+) photos are too small and may print blurry\. (.+)$/, "Несколько фото ($1) слишком маленькие и могут напечататься размыто. Для чёткого магнита используйте оригинал из галереи телефона, а не скриншот или фото, сохранённое из мессенджера."],
  [/^(\d+) photos added\. This pack holds (\d+), so remove (\d+) or pick a bigger pack\.$/, "Добавлено фото: $1. В этот набор помещается $2, поэтому удалите $3 или выберите набор побольше."],
  [/^(\d+) of (\d+) photos added\. We will repeat your favorites to fill the pack, or tell us in the notes\.$/, "Добавлено $1 из $2 фото. Мы повторим ваши любимые, чтобы заполнить набор, или напишите нам в записке."],
  [/^Frame for photo (\d+)$/, "Рамка для фото $1"],
  [/^Photo (\d+): (.+) frame(, caption (.+?))?(, low resolution)?\. Choose frame$/, function (_, k, f, c1, c, low) { return "Фото " + k + ": рамка «" + fr(f) + "»" + (c ? ", подпись " + c : "") + (low ? ", низкое разрешение" : "") + ". Выбрать рамку"; }],
  [/^Preview of photo (\d+) with the (.+?) frame( and the caption (.+))?$/, function (_, k, f, c1, c) { return "Превью фото " + k + " с рамкой «" + fr(f) + "»" + (c ? " и подписью " + c : ""); }],
  [/^Apply this frame to all (\d+) photos$/, "Эту рамку на все фото ($1)"],
  [/^(.+) is now on all (\d+) photos\.$/, function (_, f, k) { return "Рамка «" + fr(f) + "» теперь на всех фото (" + k + ")."; }],
  [/^Caption added to all (\d+) photos\. It prints on photos with a caption frame\.$/, "Подпись добавлена на все фото ($1). Она печатается на фото с рамкой для подписи."],
  [/^All (\d+) photos uploaded$/, "Все фото загружены ($1)"],
  [/^Uploading your photo · (\d+)%$/, "Загружаем ваше фото · $1%"],
  [/^Uploading your (\d+) photos · (\d+)%$/, "Загружаем ваши фото ($1) · $2%"],
  // orders, account, returns (assets/orders.js, account.js, return.js)
  [/^Tracking history \((\d+) scans?\)$/, function (_, n) { return "История отслеживания (" + nw(n, "запись", "записи", "записей") + ")"; }],
  [/^(.+) has your package out for delivery\. Keep an eye on the porch!$/, "$1 уже везёт вашу посылку. Поглядывайте на крыльцо!"],
  [/^Your package is with (.+?)\.( It shipped on (.+?)\.)?( We’ll email you when it’s out for delivery and when it arrives\.)?$/, function (_, c, s1, d, tail) { return "Ваша посылка у " + c + "." + (d ? " Отправлена " + d + "." : "") + (tail ? " Мы напишем, когда её повезут к вам и когда она придёт." : ""); }],
  [/^Delivered on (.+?)\. We hope you love them!$/, "Доставлено $1. Надеемся, вам понравится!"],
  [/^We hope you love them!$/, "Надеемся, вам понравится!"],
  [/^We refunded (\$[\d.,]+)\. Refunds take 5 to 10 business days to show on your statement\.$/, "Мы вернули $1. Возврат появляется в выписке через 5–10 рабочих дней."],
  [/^Rating for (.+)$/, "Оценка: $1"],
  [/^Thank you, (.+)!$/, "Спасибо, $1!"],
  [/^Order (LHH-\d+) is confirmed\. We emailed you a receipt, so keep it handy for tracking\.$/, "Заказ $1 подтверждён. Мы отправили чек на почту, сохраните его для отслеживания."],
  [/^Check your inbox\. If there’s an account for (.+?), we just sent a link to choose a new password\.( It can take a minute, and sometimes lands in spam\.)?$/, function (_, e, tail) { return "Проверьте почту. Если аккаунт " + e + " существует, мы только что отправили ссылку для нового пароля." + (tail ? " Письмо может прийти через минуту, а иногда попадает в спам." : ""); }],
  [/^See all (\d+) orders$/, function (_, n) { return "Все заказы (" + n + ")"; }],
  [/^We found (\d+) earlier orders with your email and added them to your account\.$/, function (_, n) { return "Мы нашли " + nw(n, "прошлый заказ", "прошлых заказа", "прошлых заказов") + " с вашей почтой и добавили их в аккаунт."; }],
  [/^Signed in as (.+)\.$/, "Вы вошли как $1."],
  [/^We emailed (.+) a link to choose a new password\.$/, "Мы отправили на $1 ссылку для нового пароля."],
  [/^Your account and orders \(signed in as (.+)\)$/, "Ваш аккаунт и заказы (вы вошли как $1)"],
  [/^(.+) saved to your favorites$/, function (_, x) { return "Добавлено в избранное: " + tr(x); }],
  [/^(.+) removed from favorites$/, function (_, x) { return "Удалено из избранного: " + tr(x); }],
  [/^Refunded (\$[\d.,]+) on (.+)\.$/, "Возвращено $1, $2."],
  [/^(\$[\d.,]+) back to your card on (.+)$/, "$1 вернулись на карту, $2"],
  [/^Your refund: (\$[\d.,]+) \((\$[\d.,]+) for the magnets − (\$[\d.,]+) return shipping\)\.$/, "Ваш возврат: $1 ($2 за магниты − $3 обратная доставка)."],
  [/^(\d+) magnets · (\$[\d.,]+) each$/, function (_, n, e) { return mag(n) + " · " + e + " за шт."; }],
  [/^(\$[\d.,]+) each$/, "$1 за шт."],
  [/^This account is turned off\. Email (.+) and we’ll sort it out\.$/, "Этот аккаунт отключён. Напишите на $1, и мы разберёмся."],
  [/^We couldn’t save one of your photos\. (.+?) or email (.+?)\.?$/, "Не удалось сохранить одно из ваших фото. Попробуйте обычное фото до 25 МБ (JPG, PNG, HEIC или WebP) или напишите на $2."],
  [/^We can’t take photo uploads right now\. Please email (.+)$/, "Сейчас не можем принимать загрузку фото. Напишите на $1"],
  [/^Something went wrong on our side\. Please try again, or email (.+)$/, "У нас что-то пошло не так. Попробуйте ещё раз или напишите на $1"],
  [/^This link has expired or is incomplete\. Email (.+) and we’ll remove you by hand\.$/, "Ссылка устарела или неполная. Напишите на $1, и мы уберём вас вручную."],
  [/^Your email app should open now\. If it doesn't, write to us at (.+)$/, "Сейчас откроется почтовое приложение. Если нет, напишите нам на $1"],
  [/^Ordering today\? Most US orders arrive <strong>about (.+)<\/strong>\.$/, function (_, d) { return "Заказываете сегодня? Большинство заказов по США придут <strong>примерно " + date(d) + "</strong>."; }],
  [/^(\d+) photos? added, (\$[\d.,]+) each$/, "Добавлено фото: $1, по $2 за шт."],
  [/^Add 1 to 3 photos, (\$[\d.,]+) each$/, "Добавьте от 1 до 3 фото, по $1 за шт."],
  [/^Add 1 more photo and get the pack of 4 for (\$[\d.,]+)\.$/, "Добавьте ещё 1 фото и получите набор из 4 за $1."],
  [/^(\d+) photos: pack of (\d+) \+ (\d+) extra photos? \((\$[\d.,]+) each\)$/, "$1 фото: набор из $2 + ещё $3 ($4 за шт.)"],
  [/^Only want (\d+) magnets?\? Make just these for (\$[\d.,]+)$/, function (_, n, p) { return "Нужно только " + mag(n) + "? Сделать только их за " + p; }],
  [/^Add (\d+) more photos? at no extra cost: they fit in your pack of (\d+)\.$/, "Можно добавить ещё $1 фото бесплатно: они поместятся в ваш набор из $2."],
  [/^Want more\? Add 1 more photo for (\$[\d.,]+), or 2 for (\$[\d.,]+)\.$/, "Хотите больше? Ещё 1 фото за $1 или 2 за $2."],
  [/^Same price, more room: we moved you to the pack of (\d+)\. Add (\d+) more photos? at no extra cost\.$/, "Та же цена, больше места: мы перевели вас на набор из $1. Можно добавить ещё $2 фото бесплатно."],
  [/^A photo order holds up to (\d+) photos, so (\d+) (?:was|were) not added\.$/, "В фотозаказ помещается до $1 фото, поэтому $2 не добавлено."],
  [/^(\d+) of (\d+) photos added$/, "Добавлено $1 из $2 фото"],
  [/^Photo (\d+) of (\d+)$/, "Фото $1 из $2"],
  [/^<span>(\d+\/\d+)<\/span> · Optional, leave empty for none$/, "<span>$1</span> · Необязательно, оставьте пустым, если не нужна"],
  [/^(\d+) designs · \$5 each$/, function (_, n) { return des(n) + " · $5 за шт."; }],
  [/^(\d+) countries · (\d+) designs · \$5 each$/, function (_, c, n) { return nw(c, "страна", "страны", "стран") + " · " + des(n) + " · $5 за шт."; }],
  [/^See all (\d+)$/, "Смотреть все ($1)"],
  [/^Add all (\d+) to cart$/, "Все в корзину ($1)"],
  [/^Ships in 1–2 business days\. Order today and it arrives <strong>about (.+)<\/strong> in the US\.$/, function (_, d) { return "Отправка за 1–2 рабочих дня. Закажите сегодня, и по США он придёт <strong>примерно " + date(d) + "</strong>."; }],
  [/^\$([\d.,]+) each$/, "$$$1 за шт."],
  [/^Buy now · \$([\d.,]+)$/, "Купить сейчас · $$$1"],
  [/^Digital file · (.+) · sent to your email · no magnet$/, function (_, t) { return "Цифровой файл · " + tr(t) + " · придёт на почту · без магнита"; }],
  [/^Service (\d)$/, "Услуга $1"],
  [/^Line (\d+)$/, "Строка $1"],
  [/^Line (\d+), right side$/, "Строка $1, справа"],
  [/^(\d+) ready-made designs for your (business|wedding|graduation|party)\. Tap one to change the colors and the words, add your logo and see it right away\.$/, function (_, n, w) { return n + " " + pl(n, "готовый дизайн", "готовых дизайна", "готовых дизайнов") + " для " + FOR[w] + ". Нажмите на любой, чтобы поменять цвета и слова, добавить логотип и сразу увидеть результат."; }],
  [/^Pack size for (.+)$/, function (_, c) { return "Размер набора: " + tr(c); }],
  [/^(.+?) <small>([\d,]+\+?)<\/small>$/, function (_, c, k) { return (c === "All" ? "Все" : tr(c)) + " <small>" + k + "</small>"; }],
  [/^(.+) · (\d+) countries · (\d+) designs$/, function (_, a, k, d) { return tr(a) + " · " + nw(k, "страна", "страны", "стран") + " · " + des(d); }],
  [/^(.+) · (\d+) designs$/, function (_, a, k) { return tr(a) + " · " + des(k); }],
  // design pages and lists
  [/^See (.+) larger$/, "Увеличить: $1"],
  [/^Favorite: (.+)$/, "В избранное: $1"],
  [/^Remove from favorites: (.+)$/, "Убрать из избранного: $1"],
  [/^(.+) fridge magnet$/, "Магнит на холодильник «$1»"],
  [/^(.+) magnet · Little Hive House$/, "Магнит «$1» · Little Hive House"],
  [/^(.+) magnets · Little Hive House$/, function (_, c) { return "Магниты «" + col(c) + "» · Little Hive House"; }],
  [/^(.+) · Little Hive House$/, function (_, c) { var x = COL[c] || (window.LHH_I18N && LHH_I18N.t(c)) || c; return x !== c || known(c) ? x + " · Little Hive House" : null; }],
  [/^All (.{1,40}) designs$/, function (_, c) { return known(c) ? "Все дизайны «" + col(c) + "»" : null; }],
  [/^More from (.{1,40})$/, function (_, c) { return known(c) ? "Ещё из коллекции «" + col(c) + "»" : null; }],
  [/^(.{1,40}) on the fridge$/, function (_, c) { return known(c) ? col(c) + " на холодильнике" : null; }],
  [/^(.+) on the fridge · (\d+) designs$/, function (_, c, k) { return known(c) ? col(c) + " на холодильнике · " + des(k) : null; }],
  [/^(\d[\d,]*) designs?$/, function (_, n) { return des(n); }],
  [/^(\d[\d,]*)\+ designs$/, "$1+ дизайнов"],
  [/^(\d+) magnets?$/, function (_, n) { return mag(n); }],
  [/^(\d+) items?$/, function (_, n) { return nw(n, "товар", "товара", "товаров"); }],
  [/^(\d+) photos?$/, "$1 фото"],
  [/^(\d+) collections$/, function (_, n) { return nw(n, "коллекция", "коллекции", "коллекций"); }],
  [/^See all (\d+) designs$/, function (_, n) { return "Смотреть все " + des(n); }],
  [/^See (\d+) more designs?$/, function (_, n) { return "Ещё " + des(n); }],
  [/^Show (\d+) more$/, "Показать ещё $1"],
  [/^Big order, (\d+) magnets \((\d+)% off\)$/, function (_, k, p) { return "Крупный заказ, " + mag(k) + " (скидка " + p + "%)"; }],
  [/^Add \$([\d.]+) more for free US shipping\.$/, "Добавьте ещё на $$$1 для бесплатной доставки по США."],
  [/^Order today, it arrives <strong>about (.+)<\/strong> in the US · <a>Shipping details<\/a>$/, function (_, d) { return "Закажите сегодня, и по США он придёт <strong>примерно " + date(d) + "</strong> · <a>О доставке</a>"; }],
  [/^about (.+\d.*)$/, function (_, d) { return "примерно " + date(d); }],
  [/^Updated (.+)$/, function (_, d) { return "Обновлено " + date(d); }],
  [/^Ordered (.+)$/, function (_, d) { return "Заказано " + date(d); }],
  [/^Delivered (.+)$/, function (_, d) { return "Доставлено " + date(d); }],
  [/^Shipped (.+)$/, function (_, d) { return "Отправлено " + date(d); }],
  [/^Order (LHH-\d+)$/, "Заказ $1"],
  [/^Qty (\d+)$/, "Кол-во $1"],
  [/^Magnet (\d+)$/, "Магнит $1"],
  [/^Photo (\d+)$/, "Фото $1"],
  [/^Step (\d+) of (\d+)$/, "Шаг $1 из $2"],
  [/^(\d+)% off everything, or buy (\d+) designs, get (\d+) free(.*)$/, function (_, p, b, g, rest) { return "Скидка " + p + "% на всё или " + g + " в подарок при покупке " + b + saleEnd(rest); }],
  [/^today only: (\d+)% off everything( \+ free shipping)?(.*)$/, function (_, p, f, rest) { return "только сегодня: скидка " + p + "% на всё" + (f ? " + бесплатная доставка" : "") + saleEnd(rest); }],
  [/^(Black Friday|Cyber Monday), (\d+)% off$/, function (_, n, p) { return ev(n) + ", скидка " + p + "%"; }],
  [/^(Black Friday|Cyber Monday), (\d+) designs? free$/, function (_, n, k) { return ev(n) + ": " + k + " в подарок"; }],
  [/^(Black Friday|Cyber Monday): add (\d+) more designs? and (\d+) of them (?:is|are) free\.$/, function (_, n, a, f) { return ev(n) + ": добавьте ещё " + des(a) + ", и " + f + " из них будут в подарок."; }],
  [/^(Black Friday|Cyber Monday): free shipping on every order today\.$/, function (_, n) { return ev(n) + ": сегодня бесплатная доставка для всех заказов."; }],
  [/^(\d+) of (\d+)$/, "$1 из $2"],
  /* photo swap on the order pages (assets/orders.js, functions/photoswap.js) */
  [/^Change photo (\d+)$/, "Заменить фото $1"],
  [/^Photo (\d+) was changed for a new one\.$/, "Фото $1 заменено на новое."],
  [/^Photo (\d+) \(pack (\d+)\) was changed for a new one\.$/, "Фото $1 (набор $2) заменено на новое."],
  [/^Pack (\d+)$/, "Набор $1"],
];
/* the end of the sale bar's text: " · through Cyber Monday" or " · ends in 5h 12m" */
function saleEnd(rest) {
  if (!rest) return "";
  if (/through Cyber Monday/.test(rest)) return " · до Киберпонедельника";
  var m = /ends in (.*)$/.exec(rest);
  return m ? " · осталось " + m[1].replace(/(\d+)d\b/, "$1 д").replace(/(\d+)h\b/, "$1 ч").replace(/(\d+)m\b/, "$1 мин") : rest;
}
