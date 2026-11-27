/* Patterns: English text with a number, a date or a name in it. Each is [regex, Simplified Chinese] where the Chinese is a
   replacement string ($1…) or a function of the match. Checked in order, after the exact dictionary.
   Prices keep the US format ($5.49, 1,200); discounts read as 折 (20% off → 8 折). */
var COL = {
  "USA Places": "美国风景", "World Places": "世界风景", "Ink Cities": "水墨城市",
  "City Sketches": "城市速写", "Fall": "秋天", "Halloween": "万圣节", "Horror Classics": "经典恐怖",
  "Furry Friends": "毛茸茸的朋友", "Kitchen Words": "厨房小语", "Americana": "美国风情", "México": "墨西哥",
  "Ireland": "爱尔兰", "Italia": "意大利", "Puerto Rico": "波多黎各", "Pilipinas": "菲律宾", "India": "印度",
  "Korea": "韩国", "Japan": "日本", "Brasil": "巴西", "Greece": "希腊", "France": "法国",
  "Great Masters": "艺术大师", "Mythology": "神话", "Home Notes": "家庭便条", "Bee Kind": "Bee Kind",
  "Night Sky": "夜空", "Birth Flowers": "生日花", "Storybook Classics": "经典文学",
  "Fairy Tales & Myths": "童话与神话", "Wise Words": "智慧语录", "Holidays & Dates": "节日与纪念日",
  "Bumper Stickers": "车尾贴", "Christmas": "圣诞节", "Summer": "夏天", "Heritage": "文化传承",
  "Photo magnets": "照片冰箱贴", "Custom photo magnets": "定制照片冰箱贴"
};
var FRAME = { "Arch": "拱形", "Art deco": "装饰艺术", "Autumn": "秋天", "Birthday": "生日", "Botanical": "植物",
  "Circle": "圆形", "Classic": "经典", "Crisp white mat": "白色卡纸", "Date stamp": "日期印章",
  "Eucalyptus wreath": "尤加利花环", "Film frame": "胶片框", "Full photo": "整张照片",
  "Gallery mat": "画廊卡纸", "Gallery with caption": "画廊带文字", "Gold line": "金线",
  "Graduation": "毕业", "Handwritten": "手写", "Holiday": "节日", "Honeycomb": "蜂巢",
  "Instant print": "拍立得", "Love": "爱心", "Modern": "现代", "Name band": "名字横条",
  "Postage stamp": "邮票", "Postcard": "明信片", "Rounded modern": "现代圆角",
  "Scalloped lace": "蕾丝花边", "Script": "花体字", "Sweet dreams": "甜梦", "Team": "球队",
  "Thin white border": "细白边", "Tropical leaves": "热带树叶", "Vintage ornate gold": "复古金边",
  "Watercolour peonies": "水彩牡丹", "Wedding": "婚礼", "Winter": "冬天", "No border": "无边框" };
function fr(s) { return FRAME[s] || s; }
function col(s) { return COL[s] || s; }
/** only for the shop's own collection names: anything else is left to the dictionary */
function known(s) { return Object.prototype.hasOwnProperty.call(COL, s) || /^(Americana|México|Brasil|Halloween|Bee Kind)$/.test(s); }
var MON = { Jan: 1, Feb: 2, Mar: 3, Apr: 4, May: 5, Jun: 6, Jul: 7, Aug: 8, Sep: 9, Oct: 10, Nov: 11, Dec: 12,
  January: 1, February: 2, March: 3, April: 4, June: 6, July: 7, August: 8, September: 9, October: 10, November: 11, December: 12 };
var DAY = { Mon: "周一", Tue: "周二", Wed: "周三", Thu: "周四", Fri: "周五", Sat: "周六", Sun: "周日",
  Monday: "星期一", Tuesday: "星期二", Wednesday: "星期三", Thursday: "星期四", Friday: "星期五", Saturday: "星期六", Sunday: "星期日" };
var M = "(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)";
/* "Nov 17–20" → "11月17–20日"; "Nov 28–Dec 2" → "11月28日–12月2日"; "November 3, 2026" → "2026年11月3日";
   "Tue, Nov 17" → "周二，11月17日" */
function date(s) {
  return s
    .replace(/\b(Mon|Tue|Wed|Thu|Fri|Sat|Sun|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b,? ?/g, function (d, x) { return DAY[x] + (/,/.test(d) ? "，" : ""); })
    .replace(new RegExp(M + " (\\d{1,2}), (\\d{4})", "g"), function (_, m, d, y) { return y + "年" + MON[m] + "月" + d + "日"; })
    .replace(new RegExp(M + " (\\d{1,2})[–-](\\d{1,2})\\b", "g"), function (_, m, a, b) { return MON[m] + "月" + a + "–" + b + "日"; })
    .replace(new RegExp(M + " (\\d{1,2})[–-]" + M + " (\\d{1,2})", "g"), function (_, m1, a, m2, b) { return MON[m1] + "月" + a + "日–" + MON[m2] + "月" + b + "日"; })
    .replace(new RegExp(M + " (\\d{1,2})\\b", "g"), function (_, m, d) { return MON[m] + "月" + d + "日"; })
    .replace(new RegExp(M + " (\\d{4})", "g"), function (_, m, y) { return y + "年" + MON[m] + "月"; });
}
/** 20 → "8 折", 25 → "75 折" */
function zhe(p) { var r = 100 - Number(p); return (r % 10 ? r : r / 10) + " 折"; }
function tr(s) { return COL[s] || (window.LHH_I18N ? window.LHH_I18N.t(s) : s); }
function ev(n) { return n === "Black Friday" ? "黑色星期五" : n === "Cyber Monday" ? "网络星期一" : n; }
var PATTERNS = [
  [/^([\d,]+) ready-made designs for (your business|your wedding|your graduation|your party or event|your home)\. Tap one to change the colors and the words, add your (logo|photo) and see it right away\.$/, function (_, n, w, x) { return n + " 款现成设计，适合" + { "your business": "你的生意", "your wedding": "你的婚礼", "your graduation": "你的毕业", "your party or event": "你的派对或活动", "your home": "你的家" }[w] + "。点一个就能改颜色和文字，加上" + (x === "logo" ? "你的 logo" : "你的照片") + "，马上看到效果。"; }],
  [/^(\d+) kinds · ([\d,]+) designs$/, "$1 种 · $2 款设计"],
  [/^(\d+) (magnets?) · \$([\d.]+)(?: \(\$([\d.]+) each\))?$/, function (_, n, m, p, e) { return n + " 个冰箱贴 · $" + p + (e ? "（每个 $" + e + "）" : ""); }],
  [/^From \$(\d+) a magnet$/, "每个 $$$1 起"],
  [/^\$([\d.]+) · sent to your email$/, "$$$1 · 发到你的邮箱"],
  [/^Hundreds of designs to make yours: change the words and colors, add a photo\. From \$(\d+)\.$/, "上百款设计任你定制：改文字和颜色，加一张照片。$$$1 起。"],
  [/^Every magnet is made just for you\. Want only the design\? \$([\d.]+) for the file, free with any magnet\.$/, "每个冰箱贴都专门为你制作。只想要设计？文件 $$$1，买任何冰箱贴都免费送。"],
  [/^Yes\. Tap the design, make it yours and choose “Only want the file”: \$([\d.]+), sent to your email right away, no magnet\. It is free with any magnet order\.$/, "可以。点设计，改成你的，然后选“只要文件”：$$$1，马上发到你的邮箱，不含冰箱贴。订购任何冰箱贴都免费送。"],
  [/^([^·<]{2,40}) · ([^·<]{2,40})$/, function (_, a, b) { var x = tr(a), y = tr(b); return x !== a || y !== b ? x + " · " + y : null; }],
  [/^1 magnet$/, "1 个冰箱贴"],
  [/^(\d+) photo designs with names, dates and captions$/, "$1 款带名字、日期和文字的照片设计"],
  [/^\$(\d+) · \$([\d.]+) each$/, "$$$1 · 每个 $$$2"],
  [/^Photo ([\d, ]+) didn't finish uploading\. Please try again\.$/, "第 $1 张照片没有上传完。请再试一次。"],
  [/^Photo (\d+) didn't upload correctly\. Please remove it and add it again\.$/, "第 $1 张照片没有上传成功。请删除后重新添加。"],
  [/^Photo (\d+) is too big or empty\.$/, "第 $1 张照片太大或是空的。"],
  [/^Cart <span>(\d+)<\/span>$/, "购物车 <span>$1</span>"],
  [/^Order today and it arrives about (.+) in the US\. <a>Shipping details<\/a>$/, function (_, d) { return "今天下单，美国境内预计 " + date(d) + " 左右送达。<a>配送详情</a>"; }],
  // cart, photo builder, checkout (assets/site.js, custom.js, checkout.js)
  [/^One less (.+)$/, "减少一个：$1"],
  [/^One more (.+)$/, "增加一个：$1"],
  [/^Add (\d+) more magnets for (\d+)% off your whole order\.$/, function (_, k, p) { return "再加 " + k + " 个冰箱贴，整单享 " + zhe(p) + "。"; }],
  [/^Order today and it arrives about (.+) in the US\.$/, function (_, d) { return "今天下单，美国境内预计 " + date(d) + " 左右送达。"; }],
  [/^Custom photo magnets$/, "定制照片冰箱贴"],
  [/^(.+) added to cart$/, function (_, x) { return tr(x) + " 已加入购物车"; }],
  [/^Your (\d+) magnets are in the cart$/, "你的 $1 个冰箱贴已加入购物车"],
  [/^(\d+) magnets · we plan the design with you by email after checkout$/, "$1 个冰箱贴 · 付款后我们通过邮件和你一起规划设计"],
  // bulk-order pages (business, weddings, graduation, parties): packs, the mailing service, the QR maker
  [/^(\d+) magnets · \$([\d.,]+) \(\$([\d.,]+) each\)$/, "$1 个冰箱贴 · $$$2（每个 $$$3）"],
  [/^(\d+) addresses$/, "$1 个地址"],
  [/^(\d+) addresses · we ask for your list after checkout$/, "$1 个地址 · 付款后我们向你索取名单"],
  [/^(\d+) magnets · style: (.+) · we plan the design with you by email after checkout$/, function (_, n, s) { return n + " 个冰箱贴 · 风格：" + tr(s) + " · 付款后我们通过邮件和你一起规划设计"; }],
  [/^(\d+) QR magnets · (.+) · proof before we print$/, "$1 个二维码冰箱贴 · $2 · 印刷前先看样稿"],
  [/^Mailed to your list, (\d+) addresses$/, "寄给你的名单，$1 个地址"],
  [/^Graduation & college, (\d+) magnets$/, "毕业与大学，$1 个冰箱贴"],
  [/^(\d+) magnets · (\d+) photos? · (\d+) frames$/, "$1 个冰箱贴 · $2 张照片 · $3 种相框"],
  [/^(\d+) magnets · (\d+) photos? · (.+)$/, function (_, a, b, f) { return a + " 个冰箱贴 · " + b + " 张照片 · " + fr(f); }],
  [/^2 × 2 in · (.+)$/, function (_, c) { return "2 × 2 英寸 · " + col(c); }],
  [/^(.+) magnet$/, "$1 冰箱贴"],
  [/^Remove photo (\d+)$/, "删除第 $1 张照片"],
  [/^1 photo is too small and may print blurry\. (.+)$/, "有 1 张照片太小，印出来可能模糊。想要清晰的冰箱贴，请用手机相册里的原图，不要用截图或从聊天软件保存的照片。"],
  [/^(\d+) photos are too small and may print blurry\. (.+)$/, "有 $1 张照片太小，印出来可能模糊。想要清晰的冰箱贴，请用手机相册里的原图，不要用截图或从聊天软件保存的照片。"],
  [/^(\d+) photos added\. This pack holds (\d+), so remove (\d+) or pick a bigger pack\.$/, "已添加 $1 张照片。这个套餐只能放 $2 张，请删除 $3 张，或选更大的套餐。"],
  [/^(\d+) of (\d+) photos added\. We will repeat your favorites to fill the pack, or tell us in the notes\.$/, "已添加 $1/$2 张照片。我们会重复你最喜欢的照片来补满套餐，或者在备注里告诉我们。"],
  [/^Frame for photo (\d+)$/, "第 $1 张照片的相框"],
  [/^Photo (\d+): (.+) frame(, caption (.+?))?(, low resolution)?\. Choose frame$/, function (_, k, f, c1, c, low) { return "第 " + k + " 张照片：" + fr(f) + "相框" + (c ? "，文字 " + c : "") + (low ? "，分辨率低" : "") + "。选择相框"; }],
  [/^Preview of photo (\d+) with the (.+?) frame( and the caption (.+))?$/, function (_, k, f, c1, c) { return "第 " + k + " 张照片的预览，" + fr(f) + "相框" + (c ? "，文字 " + c : ""); }],
  [/^Apply this frame to all (\d+) photos$/, "全部 $1 张照片都用这个相框"],
  [/^(.+) is now on all (\d+) photos\.$/, function (_, f, k) { return "全部 " + k + " 张照片都已使用" + fr(f) + "相框。"; }],
  [/^Caption added to all (\d+) photos\. It prints on photos with a caption frame\.$/, "已给全部 $1 张照片加上文字。带文字的相框才会印出来。"],
  [/^All (\d+) photos uploaded$/, "全部 $1 张照片已上传"],
  [/^Uploading your photo · (\d+)%$/, "正在上传你的照片 · $1%"],
  [/^Uploading your (\d+) photos · (\d+)%$/, "正在上传你的 $1 张照片 · $2%"],
  // orders, account, returns (assets/orders.js, account.js, return.js)
  [/^Tracking history \((\d+) scans?\)$/, "物流记录（$1 条）"],
  [/^(.+) has your package out for delivery\. Keep an eye on the porch!$/, "$1 正在派送你的包裹。留意门口哦！"],
  [/^Your package is with (.+?)\.( It shipped on (.+?)\.)?( We’ll email you when it’s out for delivery and when it arrives\.)?$/, function (_, c, s1, d, tail) { return "你的包裹在 " + c + " 手上。" + (d ? "已于 " + d + " 发货。" : "") + (tail ? "开始派送和送达时我们都会发邮件通知你。" : ""); }],
  [/^Delivered on (.+?)\. We hope you love them!$/, "已于 $1 送达。希望你喜欢！"],
  [/^We hope you love them!$/, "希望你喜欢！"],
  [/^We refunded (\$[\d.,]+)\. Refunds take 5 to 10 business days to show on your statement\.$/, "我们已退款 $1。退款需要 5 到 10 个工作日才会显示在你的账单上。"],
  [/^Rating for (.+)$/, "$1 的评分"],
  [/^Thank you, (.+)!$/, "谢谢你，$1！"],
  [/^Order (LHH-\d+) is confirmed\. We emailed you a receipt, so keep it handy for tracking\.$/, "订单 $1 已确认。收据已发到你的邮箱，请保存好以便查询物流。"],
  [/^Check your inbox\. If there’s an account for (.+?), we just sent a link to choose a new password\.( It can take a minute, and sometimes lands in spam\.)?$/, function (_, e, tail) { return "请查收邮件。如果 " + e + " 有账户，我们刚刚发了一个设置新密码的链接。" + (tail ? "可能需要一分钟，有时会进垃圾邮件。" : ""); }],
  [/^See all (\d+) orders$/, "查看全部 $1 个订单"],
  [/^We found (\d+) earlier orders with your email and added them to your account\.$/, "我们找到 $1 个用你邮箱下的旧订单，已加入你的账户。"],
  [/^Signed in as (.+)\.$/, "已登录：$1。"],
  [/^We emailed (.+) a link to choose a new password\.$/, "我们已向 $1 发送设置新密码的链接。"],
  [/^Your account and orders \(signed in as (.+)\)$/, "你的账户和订单（已登录：$1）"],
  [/^(.+) saved to your favorites$/, function (_, x) { return tr(x) + " 已加入收藏"; }],
  [/^(.+) removed from favorites$/, function (_, x) { return tr(x) + " 已取消收藏"; }],
  [/^Refunded (\$[\d.,]+) on (.+)\.$/, "已于 $2 退款 $1。"],
  [/^(\$[\d.,]+) back to your card on (.+)$/, "$1 已于 $2 退回你的卡"],
  [/^Your refund: (\$[\d.,]+) \((\$[\d.,]+) for the magnets − (\$[\d.,]+) return shipping\)\.$/, "你的退款：$1（冰箱贴 $2 − 退货运费 $3）。"],
  [/^(\d+) magnets · (\$[\d.,]+) each$/, "$1 个冰箱贴 · 每个 $2"],
  [/^(\$[\d.,]+) each$/, "每个 $1"],
  [/^This account is turned off\. Email (.+) and we’ll sort it out\.$/, "这个账户已停用。发邮件到 $1，我们来处理。"],
  [/^We couldn’t save one of your photos\. (.+?) or email (.+?)\.?$/, "有一张照片没能保存。请使用 25 MB 以下的普通照片（JPG、PNG、HEIC 或 WebP）再试一次，或者发邮件到 $2。"],
  [/^We can’t take photo uploads right now\. Please email (.+)$/, "现在无法上传照片。请发邮件到 $1"],
  [/^Something went wrong on our side\. Please try again, or email (.+)$/, "我们这边出了点问题。请再试一次，或者发邮件到 $1"],
  [/^This link has expired or is incomplete\. Email (.+) and we’ll remove you by hand\.$/, "这个链接已过期或不完整。发邮件到 $1，我们会手动帮你退订。"],
  [/^Your email app should open now\. If it doesn't, write to us at (.+)$/, "你的邮件应用应该已经打开了。如果没有，请写信到 $1"],
  [/^Ordering today\? Most US orders arrive <strong>about (.+)<\/strong>\.$/, function (_, d) { return "今天下单？大多数美国境内订单预计 <strong>" + date(d) + " 左右</strong>送达。"; }],
  [/^(\d+) photos? added, (\$[\d.,]+) each$/, "已添加 $1 张照片，每张 $2"],
  [/^Add 1 to 3 photos, (\$[\d.,]+) each$/, "添加 1 到 3 张照片，每张 $1"],
  [/^Add 1 more photo and get the pack of 4 for (\$[\d.,]+)\.$/, "再加 1 张照片，就能以 $1 买 4 张套餐。"],
  [/^(\d+) photos: pack of (\d+) \+ (\d+) extra photos? \((\$[\d.,]+) each\)$/, "$1 张照片：$2 张套餐 + 额外 $3 张（每张 $4）"],
  [/^Only want (\d+) magnets?\? Make just these for (\$[\d.,]+)$/, "只想要 $1 个冰箱贴？只做这些，$2"],
  [/^Add (\d+) more photos? at no extra cost: they fit in your pack of (\d+)\.$/, "还可以免费再加 $1 张照片：你的 $2 张套餐放得下。"],
  [/^Want more\? Add 1 more photo for (\$[\d.,]+), or 2 for (\$[\d.,]+)\.$/, "想要更多？再加 1 张 $1，或 2 张 $2。"],
  [/^Same price, more room: we moved you to the pack of (\d+)\. Add (\d+) more photos? at no extra cost\.$/, "价格不变，空间更大：已为你换成 $1 张套餐。还可以免费再加 $2 张照片。"],
  [/^A photo order holds up to (\d+) photos, so (\d+) (?:was|were) not added\.$/, "一个照片订单最多 $1 张，所以有 $2 张没有添加。"],
  [/^(\d+) of (\d+) photos added$/, "已添加 $1/$2 张照片"],
  [/^Photo (\d+) of (\d+)$/, "第 $1 张，共 $2 张"],
  [/^<span>(\d+\/\d+)<\/span> · Optional, leave empty for none$/, "<span>$1</span> · 选填，不需要就留空"],
  [/^(\d+) designs · \$5 each$/, "$1 款设计 · 每个 $$5"],
  [/^(\d+) countries · (\d+) designs · \$5 each$/, "$1 个国家 · $2 款设计 · 每个 $$5"],
  [/^See all (\d+)$/, "查看全部 $1 个"],
  [/^Add all (\d+) to cart$/, "全部 $1 个加入购物车"],
  [/^Ships in 1–2 business days\. Order today and it arrives <strong>about (.+)<\/strong> in the US\.$/, function (_, d) { return "1–2 个工作日内发货。今天下单，美国境内预计 <strong>" + date(d) + " 左右</strong>送达。"; }],
  [/^\$([\d.,]+) each$/, "每个 $$$1"],
  [/^Buy now · \$([\d.,]+)$/, "立即购买 · $$$1"],
  [/^Digital file · (.+) · sent to your email · no magnet$/, function (_, t) { return "电子文件 · " + tr(t) + " · 发到你的邮箱 · 不含冰箱贴"; }],
  [/^Service (\d)$/, "服务 $1"],
  [/^Line (\d+)$/, "第 $1 行"],
  [/^Line (\d+), right side$/, "第 $1 行，右侧"],
  [/^(\d+) ready-made designs for your (business|wedding|graduation|party)\. Tap one to change the colors and the words, add your logo and see it right away\.$/, function (_, n, w) { return n + " 款现成设计，适合" + { business: "你的生意", wedding: "你的婚礼", graduation: "你的毕业", party: "你的派对" }[w] + "。点一个就能改颜色和文字，加上你的 logo，马上看到效果。"; }],
  [/^Pack size for (.+)$/, function (_, c) { return tr(c) + " 的套餐大小"; }],
  [/^(.+?) <small>([\d,]+\+?)<\/small>$/, function (_, c, k) { return (c === "All" ? "全部" : tr(c)) + " <small>" + k + "</small>"; }],
  [/^(.+) · (\d+) countries · (\d+) designs$/, function (_, a, k, d) { return tr(a) + " · " + k + " 个国家 · " + d + " 款设计"; }],
  [/^(.+) · (\d+) designs$/, function (_, a, k) { return tr(a) + " · " + k + " 款设计"; }],
  // design pages and lists
  [/^See (.+) larger$/, "查看 $1 大图"],
  [/^Favorite: (.+)$/, "收藏：$1"],
  [/^Remove from favorites: (.+)$/, "取消收藏：$1"],
  [/^(.+) fridge magnet$/, "$1 冰箱贴"],
  [/^(.+) magnet · Little Hive House$/, "$1 冰箱贴 · Little Hive House"],
  [/^(.+) magnets · Little Hive House$/, function (_, c) { return col(c) + "冰箱贴 · Little Hive House"; }],
  [/^(.+) · Little Hive House$/, function (_, c) { var x = COL[c] || (window.LHH_I18N && LHH_I18N.t(c)) || c; return x !== c || known(c) ? x + " · Little Hive House" : null; }],
  [/^All (.{1,40}) designs$/, function (_, c) { return known(c) ? "全部" + col(c) + "设计" : null; }],
  [/^More from (.{1,40})$/, function (_, c) { return known(c) ? "更多" + col(c) : null; }],
  [/^(.{1,40}) on the fridge$/, function (_, c) { return known(c) ? "冰箱上的" + col(c) : null; }],
  [/^(.+) on the fridge · (\d+) designs$/, function (_, c, k) { return known(c) ? "冰箱上的" + col(c) + " · " + k + " 款设计" : null; }],
  [/^(\d[\d,]*) designs?$/, "$1 款设计"],
  [/^(\d[\d,]*)\+ designs$/, "$1 多款设计"],
  [/^(\d+) magnets?$/, "$1 个冰箱贴"],
  [/^(\d+) items?$/, "$1 件商品"],
  [/^(\d+) photos?$/, "$1 张照片"],
  [/^(\d+) collections$/, "$1 个系列"],
  [/^See all (\d+) designs$/, "查看全部 $1 款设计"],
  [/^See (\d+) more designs?$/, "再看 $1 款设计"],
  [/^Show (\d+) more$/, "再显示 $1 个"],
  [/^Big order, (\d+) magnets \((\d+)% off\)$/, function (_, k, p) { return "大批量订单，" + k + " 个冰箱贴（" + zhe(p) + "）"; }],
  [/^Add \$([\d.]+) more for free US shipping\.$/, "再买 $$$1 就能享受美国境内免运费。"],
  [/^Order today, it arrives <strong>about (.+)<\/strong> in the US · <a>Shipping details<\/a>$/, function (_, d) { return "今天下单，美国境内预计 <strong>" + date(d) + " 左右</strong>送达 · <a>配送详情</a>"; }],
  [/^about (.+\d.*)$/, function (_, d) { return date(d) + " 左右"; }],
  [/^Updated (.+)$/, function (_, d) { return "更新于 " + date(d); }],
  [/^Ordered (.+)$/, function (_, d) { return "下单于 " + date(d); }],
  [/^Delivered (.+)$/, function (_, d) { return "送达于 " + date(d); }],
  [/^Shipped (.+)$/, function (_, d) { return "发货于 " + date(d); }],
  [/^Order (LHH-\d+)$/, "订单 $1"],
  [/^Qty (\d+)$/, "数量 $1"],
  [/^Magnet (\d+)$/, "冰箱贴 $1"],
  [/^Photo (\d+)$/, "照片 $1"],
  [/^Step (\d+) of (\d+)$/, "第 $1 步，共 $2 步"],
  [/^(\d+)% off everything, or buy (\d+) designs, get (\d+) free(.*)$/, function (_, p, b, g, rest) { return "全场 " + zhe(p) + "，或买 " + b + " 款设计送 " + g + " 款" + saleEnd(rest); }],
  [/^today only: (\d+)% off everything( \+ free shipping)?(.*)$/, function (_, p, f, rest) { return "仅限今天：全场 " + zhe(p) + (f ? " + 免运费" : "") + saleEnd(rest); }],
  [/^(Black Friday|Cyber Monday), (\d+)% off$/, function (_, n, p) { return ev(n) + "，" + zhe(p); }],
  [/^(Black Friday|Cyber Monday), (\d+) designs? free$/, function (_, n, k) { return ev(n) + "，免费送 " + k + " 款设计"; }],
  [/^(Black Friday|Cyber Monday): add (\d+) more designs? and (\d+) of them (?:is|are) free\.$/, function (_, n, a, f) { return ev(n) + "：再加 " + a + " 款设计，其中 " + f + " 款免费。"; }],
  [/^(Black Friday|Cyber Monday): free shipping on every order today\.$/, function (_, n) { return ev(n) + "：今天所有订单免运费。"; }],
  [/^(\d+) of (\d+)$/, "$1/$2"],
  /* photo swap on the order pages (assets/orders.js, functions/photoswap.js) */
  [/^Change photo (\d+)$/, "更换第 $1 张照片"],
  [/^Photo (\d+) was changed for a new one\.$/, "第 $1 张照片已换成新照片。"],
  [/^Photo (\d+) \(pack (\d+)\) was changed for a new one\.$/, "第 $1 张照片（第 $2 组）已换成新照片。"],
  [/^Pack (\d+)$/, "第 $1 组"],
  [/^Photo (\d+): change or remove$/, "第 $1 张照片：更换或移除"],
  [/^Remove photo (\d+)\?$/, "移除第 $1 张照片？"],
  [/^You’ll get (\d+) magnets and pay (\$[\d.,]+) less\.$/, "您将收到 $1 个磁贴，少付 $2。"],
  [/^Swap it for another photo \(same price\), or remove it \((\$[\d.,]+) less\)\.$/, "换成另一张照片（价格不变），或移除（少付 $1）。"],
  [/^Removing photo (\d+)…$/, "正在移除第 $1 张照片…"],
  [/^Done! Photo (\d+) was removed\. You now have (\d+) magnets and your new total is (\$[\d.,]+)\.$/, "完成！第 $1 张照片已移除。现在共 $2 个磁贴，新总额为 $3。"],
  [/^Done! Photo (\d+) was removed\. You now have (\d+) magnets and we refunded (\$[\d.,]+) to your card\.$/, "完成！第 $1 张照片已移除。现在共 $2 个磁贴，我们已将 $3 退回您的卡。"],
  [/^Photo (\d+) was removed\. (\d+) magnets now\.$/, "第 $1 张照片已移除。现在共 $2 个磁贴。"],
  [/^Photo (\d+) \(pack (\d+)\) was removed\. (\d+) magnets now\.$/, "第 $1 张照片（第 $2 组）已移除。现在共 $3 个磁贴。"]
];
/* the end of the sale bar's text: " · through Cyber Monday" or " · ends in 5h 12m" */
function saleEnd(rest) {
  if (!rest) return "";
  if (/through Cyber Monday/.test(rest)) return " · 持续到网络星期一";
  var m = /ends in (.*)$/.exec(rest);
  return m ? " · 还剩 " + m[1].replace(/(\d+)d\b/, "$1 天").replace(/(\d+)h\b/, "$1 小时").replace(/(\d+)m\b/, "$1 分钟") : rest;
}
