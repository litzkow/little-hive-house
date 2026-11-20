// Little Hive House emails (and the Stripe checkout page) in Simplified Chinese.
// look(key): the exact dictionary (functions/emails/zh.json), the collection names, then the patterns below.
"use strict";

let DICT = null;
function dict() {
  if (!DICT) { try { DICT = require("../zh.json"); } catch (e) { DICT = {}; } }
  return DICT;
}
const MON = { Jan: 1, Feb: 2, Mar: 3, Apr: 4, May: 5, Jun: 6, Jul: 7, Aug: 8, Sep: 9, Oct: 10, Nov: 11, Dec: 12,
  January: 1, February: 2, March: 3, April: 4, June: 6, July: 7, August: 8, September: 9, October: 10, November: 11, December: 12 };
const M = "(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)";
/** "Nov 17–20" → "11月17–20日"; "Nov 28–Dec 2" → "11月28日–12月2日"; "November 3, 2026" → "2026年11月3日" */
function date(s) {
  return String(s)
    .replace(new RegExp(M + " (\\d{1,2}), (\\d{4})", "g"), (_, m, d, y) => `${y}年${MON[m]}月${d}日`)
    .replace(new RegExp(M + " (\\d{1,2})[–-](\\d{1,2})\\b", "g"), (_, m, a, b) => `${MON[m]}月${a}–${b}日`)
    .replace(new RegExp(M + " (\\d{1,2})[–-]" + M + " (\\d{1,2})", "g"), (_, m1, a, m2, b) => `${MON[m1]}月${a}日–${MON[m2]}月${b}日`)
    .replace(new RegExp(M + " (\\d{1,2})\\b", "g"), (_, m, d) => `${MON[m]}月${d}日`);
}
/** 20 → "8 折", 25 → "75 折" */
function zhe(p) { const r = 100 - Number(p); return `${r % 10 ? r : r / 10} 折`; }
/** "15% off" → "85 折优惠"; "$5.00 off" → "减 $5.00" */
function off(s) {
  s = String(s);
  let m = /^(\d+)% off$/.exec(s); if (m) return `${zhe(m[1])}优惠`;
  m = /^(\$[\d.,]+) off$/.exec(s); if (m) return `减 ${m[1]}`;
  return s === "a little something off" ? "一点小优惠" : s;
}
/** "1 hour" → "1 小时"; "30 minutes" → "30 分钟" */
function dur(s) { return String(s).replace(/\b1 hour\b/, "1 小时").replace(/(\d+) hours/, "$1 小时").replace(/(\d+) minutes/, "$1 分钟"); }
const ord = (n) => (n === "your order" ? "你的订单" : `订单 ${n} `);   // a space before the 的 that follows
const ev = (n) => (n === "Black Friday" ? "黑色星期五" : n === "Cyber Monday" ? "网络星期一" : n);
const COL = {
  "USA Places": "美国风景", "World Places": "世界风景", "Ink Cities": "水墨城市", "City Sketches": "城市速写",
  "Fall": "秋天", "Halloween": "万圣节", "Horror Classics": "经典恐怖", "Furry Friends": "毛茸茸的朋友", "Kitchen Words": "厨房小语",
  "Americana": "美国风情", "México": "墨西哥", "Ireland": "爱尔兰", "Italia": "意大利", "Puerto Rico": "波多黎各", "Pilipinas": "菲律宾",
  "India": "印度", "Korea": "韩国", "Japan": "日本", "Brasil": "巴西", "Greece": "希腊", "France": "法国",
  "Great Masters": "艺术大师", "Mythology": "神话", "Home Notes": "家庭便条", "Night Sky": "夜空",
  "Birth Flowers": "生日花", "Storybook Classics": "经典文学", "Fairy Tales & Myths": "童话与神话",
  "Wise Words": "智慧语录", "Holidays & Dates": "节日与纪念日", "Bumper Stickers": "车尾贴",
  "Christmas": "圣诞节", "Summer": "夏天", "Heritage": "文化传承",
};
const DATE_ONLY = new RegExp("^(about )?" + M + " \\d{1,2}([–-](" + M + " )?\\d{1,2})?(, \\d{4})?$");
const P = [
  [/^Here's everything that's coming your way, ordered (.+)\.$/, (_, d) => `这是要寄给你的所有东西，下单于 ${date(d)}。`],
  [/^Here's everything that's coming your way\.$/, "这是要寄给你的所有东西。"],
  [/^(\d+) magnets? coming your way\. We'll start making them by hand right away\.$/, "$1 个冰箱贴正在路上。我们马上开始手工制作。"],
  [/^Thank you! Order (.+) is confirmed$/, "谢谢！订单 $1 已确认"],
  [/^Estimated arrival: about 1 to 2 weeks after you approve the proof$/, "预计送达：确认样稿后大约 1 到 2 周"],
  [/^Estimated arrival: (.+)$/, (_, d) => `预计送达：${d.startsWith("about ") ? date(d.slice(6)) + " 左右" : date(d)}`],
  [/^Your magnets are on the way!( \((.+)\))?$/, (_, x, n) => `你的冰箱贴已经上路！${n ? `（${n}）` : ""}`],
  [/^(.+?)( tracking (.+))?\. Follow your package all the way to your door\.$/, (_, c, x, t) => `${c}${t ? `，物流单号 ${t}` : ""}。一路跟踪你的包裹到家门口。`],
  [/^Charged to your card today, when your order shipped( \(order (.+)\))?\. Keep this email as your receipt\.$/, (_, x, n) => `订单发货时，已于今天从你的卡扣款${n ? `（订单 ${n}）` : ""}。请保存这封邮件作为收据。`],
  [/^Carrier: (.+)$/, "承运商：$1"],
  [/^Tracking number: see the tracking page$/, "物流单号：请查看物流页面"],
  [/^Tracking number: (.+)$/, "物流单号：$1"],
  [/^Order (.+) · Out for delivery$/, "订单 $1 · 派送中"],
  [/^Order (.+) · Delivered$/, "订单 $1 · 已送达"],
  [/^(.+), your magnets arrive today!$/, "$1，你的冰箱贴今天送达！"],
  [/^(.+) has your package out for delivery\. Keep an eye on the porch and the mailbox\.$/, "$1 正在派送你的包裹。留意门口和信箱。"],
  [/^(.+) has your package out for delivery( \(order (.+)\))?\. Keep an eye on the porch!$/, (_, c, x, n) => `${c} 正在派送你的包裹${n ? `（订单 ${n}）` : ""}。留意门口哦！`],
  [/^Latest scan: (.+)$/, "最新物流：$1"],
  [/^(.+), how do they look on your fridge\?$/, "$1，贴在你的冰箱上好看吗？"],
  [/^for your next order: (.+?) until (.+)\.$/, (_, o, d) => `下次订单享${off(o)}，有效期至 ${date(d)}。`],
  [/^for your next order: (.+)\.$/, (_, o) => `下次订单享${off(o)}。`],
  [/^Show us your fridge! Share a photo on Instagram and tag (.+)$/, "给我们看看你的冰箱！在 Instagram 分享照片并标记 $1"],
  [/^Return · (.+)$/, "退货 · $1"],
  [/^Hi (.+?)[.!]$/, "$1，你好！"],
  [/^Your return label for (.+)$/, (_, n) => `${ord(n)}的退货运单`],
  [/^We got your return request \((.+)\)$/, (_, n) => `我们已收到你的退货申请（${ord(n).trim()}）`],
  [/^We're reprinting your magnets \((.+)\)$/, (_, n) => `我们正在重印你的冰箱贴（${ord(n).trim()}）`],
  [/^About your return for (.+)$/, (_, n) => `关于${ord(n)}的退货`],
  [/^No printer\? Show this QR code at the Post Office: (.+)$/, "没有打印机？在邮局出示这个二维码：$1"],
  [/^In this return:\n([\s\S]+)$/, "本次退货：\n$1"],
  [/^A note from us: ([\s\S]+)$/, "我们的留言：$1"],
  [/^A partial refund of (\$[\d.,]+) for (.+)$/, (_, a, n) => `${ord(n)}部分退款 ${a}`],
  [/^Your refund for (.+) is on its way$/, (_, n) => `${ord(n)}的退款正在路上`],
  [/^(\$[\d.,]+) is heading back to you\. Banks usually show it within 5 to 10 business days\.$/, "$1 正在退回给你。银行通常会在 5 到 10 个工作日内显示。"],
  [/^(Full|Partial) refund: (\$[\d.,]+)(.*)$/, (_, k, a, rest) => `${k === "Full" ? "全额退款" : "部分退款"}：${a}${rest.replace(/ for order /g, "，订单 ").replace(/order/g, "订单")}`],
  [/^Back to your original payment method( for order (.+))?$/, (_, x, n) => `${n ? `订单 ${n} ` : ""}退回原付款方式`],
  [/^Refunded on this order so far: (\$[\d.,]+) of (\$[\d.,]+)\.$/, "这个订单目前已退款：$1 / $2。"],
  [/^Welcome to the hive, (.+)!$/, "欢迎来到蜂巢，$1！"],
  [/^(\d+% off|\$[\d.,]+ off|a little something off) your first order( until (.+))?\.?$/, (_, o, x, d) => `首单享${off(o)}${d ? `，有效期至 ${date(d)}` : ""}。`],
  [/^Your account is ready, and (.+) your first order is waiting\.$/, (_, o) => `你的账户已就绪，首单${off(o)}在等你。`],
  [/^Thanks for joining! Here's (.+) your first order\.$/, (_, o) => `谢谢加入！送你首单${off(o)}。`],
  [/^One quick tap, (.+)!$/, "$1，只要点一下！"],
  [/^For your security this link expires in (.+) and works only once\. If it has expired, you can$/, (_, e) => `为了安全，这个链接 ${dur(e)}后失效，且只能用一次。如果已经失效，你可以`],
  [/^Tap the button to choose a new password\. The link works for (.+)\.$/, (_, e) => `点按钮设置新密码。链接 ${dur(e)}内有效。`],
  [/^(.+), your magnets are still waiting$/, "$1，你的冰箱贴还在等你"],
  [/^We saved your (\d+) magnets?\. Pick up right where you left off\.$/, "我们保留了你的 $1 个冰箱贴。从上次的地方继续吧。"],
  [/^Thanks for writing, (.+)!$/, "$1，谢谢你的来信！"],
  [/^You wrote · (.+)$/, (_, t) => `你写道 · ${look(t) || t}`],
  [/^Thanks! We'll reply within 1 business day with ideas, a price for (\d+) magnets and next steps\.$/, "谢谢！我们会在 1 个工作日内回复创意、$1 个冰箱贴的报价和下一步安排。"],
  [/^Thanks! We'll reply within 1 business day with ideas, a price and next steps\.$/, "谢谢！我们会在 1 个工作日内回复创意、报价和下一步安排。"],
  [/^Here's your link, (.+)$/, "$1，这是你的链接"],
  [/^Your payment link for (.+)$/, "你的付款链接：$1"],
  [/^(\$[\d.,]+) for (.+)\. Pay securely by card, Apple Pay or Google Pay\.$/, "$2：$1。可用银行卡、Apple Pay 或 Google Pay 安全付款。"],
  [/^Payments are processed by Stripe\. We never see or store your card number\.( This link works until (.+)\.)?$/, (_, x, d) => `付款由 Stripe 处理。我们从不查看或保存你的卡号。${d ? `这个链接有效期至 ${date(d)}。` : ""}`],
  // the Stripe checkout page (functions/checkout.js)
  [/^(\d+) custom photo magnets, 2 × 2 in$/, "$1 个定制照片冰箱贴，2 × 2 英寸（5 厘米）"],
  [/^(\d+) custom magnets\. We email you about your design after checkout\.$/, "$1 个定制冰箱贴。付款后我们会发邮件和你沟通设计。"],
  [/^(.+) discount included$/, (_, n) => `已含${ev(n)}折扣`],
  [/^(\d+) photo magnets$/, "$1 个照片冰箱贴"],
  [/^(\d+) photos?$/, "$1 张照片"],
  [/^(\d+) frames$/, "$1 种相框"],
  [/^(\d+) packs$/, "$1 个套餐"],
  [/^(.+) frame$/, (_, f) => `${look(f) || f}相框`],
  [/^(.+) magnet$/, "$1 冰箱贴"],
  [DATE_ONLY, (s) => (s.startsWith("about ") ? date(s.slice(6)) + " 左右" : date(s))],
  [/^Good news, (.+)!$/, "$1，好消息！"],
  [/^Thank you, (.+)!$/, "谢谢你，$1！"],
  [/^Thanks, (.+)!$/, "谢谢你，$1！"],
  [/^Hi (.+),$/, "$1，你好："],
  [/^Order (LHH-\d+)$/, "订单 $1"],
  [/^Qty (\d+)$/, "数量 $1"],
  [/^(\d+) magnets( × (\d+))?$/, (_, n, x, q) => `${n} 个冰箱贴${q ? ` × ${q}` : ""}`],
  [/^Volume discount \((\d+)% off\)$/, (_, p) => `批量折扣（${zhe(p)}）`],
  [/^Promo code (.+)$/, "优惠码 $1"],
  [/^(.+), (\d+)% off$/, (_, n, p) => `${ev(n)}，${zhe(p)}`],
  [/^(.+), (\d+) designs? free$/, (_, n, k) => `${ev(n)}，免费送 ${k} 款设计`],
  [/^Captions: (.+)$/, "文字：$1"],
  [/^Note: (.+)$/, "备注：$1"],
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
