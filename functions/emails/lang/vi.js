// Little Hive House emails (and the Stripe checkout page) in Vietnamese.
// look(key): the exact dictionary (functions/emails/vi.json), the collection names, then the patterns below.
"use strict";

let DICT = null;
function dict() {
  if (!DICT) { try { DICT = require("../vi.json"); } catch (e) { DICT = {}; } }
  return DICT;
}
const MON = { Jan: 1, Feb: 2, Mar: 3, Apr: 4, May: 5, Jun: 6, Jul: 7, Aug: 8, Sep: 9, Oct: 10, Nov: 11, Dec: 12,
  January: 1, February: 2, March: 3, April: 4, June: 6, July: 7, August: 8, September: 9, October: 10, November: 11, December: 12 };
const M = "(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)";
/** "Nov 17–20" → "17–20 tháng 11"; "Nov 28–Dec 2" → "28 tháng 11–2 tháng 12"; "November 3, 2026" → "3 tháng 11, 2026" */
function date(s) {
  return String(s)
    .replace(new RegExp(M + " (\\d{1,2}), (\\d{4})", "g"), (_, m, d, y) => `${d} tháng ${MON[m]}, ${y}`)
    .replace(new RegExp(M + " (\\d{1,2})[–-](\\d{1,2})\\b", "g"), (_, m, a, b) => `${a}–${b} tháng ${MON[m]}`)
    .replace(new RegExp(M + " (\\d{1,2})[–-]" + M + " (\\d{1,2})", "g"), (_, m1, a, m2, b) => `${a} tháng ${MON[m1]}–${b} tháng ${MON[m2]}`)
    .replace(new RegExp(M + " (\\d{1,2})\\b", "g"), (_, m, d) => `${d} tháng ${MON[m]}`);
}
/** "15% off" → "giảm 15%"; "$5.00 off" → "giảm $5.00" */
function off(s) {
  const m = /^(\d+%|\$[\d.,]+) off$/.exec(String(s));
  return m ? `giảm ${m[1]}` : String(s).replace(/^a little something off$/, "một chút ưu đãi");
}
/** "1 hour" → "1 giờ"; "30 minutes" → "30 phút" */
function dur(s) { return String(s).replace(/\b1 hour\b/, "1 giờ").replace(/(\d+) hours/, "$1 giờ").replace(/(\d+) minutes/, "$1 phút"); }
const ord = (n) => (n === "your order" ? "đơn của bạn" : "đơn " + n);
const COL = {
  "USA Places": "Địa danh nước Mỹ", "World Places": "Địa danh thế giới", "Ink Cities": "Thành phố bút mực", "City Sketches": "Ký họa thành phố",
  "Fall": "Mùa thu", "Horror Classics": "Kinh dị cổ điển", "Furry Friends": "Bạn bốn chân", "Kitchen Words": "Lời nhắn nhà bếp",
  "Americana": "Phong cách Mỹ", "México": "Mexico", "Italia": "Ý", "Pilipinas": "Philippines", "India": "Ấn Độ", "Korea": "Hàn Quốc",
  "Japan": "Nhật Bản", "Brasil": "Brazil", "Greece": "Hy Lạp", "France": "Pháp", "Great Masters": "Danh họa", "Mythology": "Thần thoại",
  "Home Notes": "Lời nhắn trong nhà", "Night Sky": "Bầu trời đêm", "Birth Flowers": "Hoa tháng sinh", "Storybook Classics": "Truyện kinh điển",
  "Fairy Tales & Myths": "Cổ tích và thần thoại", "Wise Words": "Lời hay ý đẹp", "Holidays & Dates": "Ngày lễ và dịp đặc biệt",
  "Bumper Stickers": "Sticker xe hơi", "Christmas": "Giáng Sinh", "Summer": "Mùa hè", "Heritage": "Cội nguồn",
};
const DATE_ONLY = new RegExp("^(about )?" + M + " \\d{1,2}([–-](" + M + " )?\\d{1,2})?(, \\d{4})?$");
const P = [
  [/^Here's everything that's coming your way, ordered (.+)\.$/, (_, d) => `Đây là tất cả những gì đang đến với bạn, đặt ngày ${date(d)}.`],
  [/^Here's everything that's coming your way\.$/, "Đây là tất cả những gì đang đến với bạn."],
  [/^(\d+) magnets? coming your way\. We'll start making them by hand right away\.$/, "$1 nam châm đang đến với bạn. Chúng tôi sẽ bắt tay làm ngay."],
  [/^Thank you! Order (.+) is confirmed$/, "Cảm ơn! Đơn $1 đã được xác nhận"],
  [/^Estimated arrival: about 1 to 2 weeks after you approve the proof$/, "Dự kiến nhận hàng: khoảng 1 đến 2 tuần sau khi bạn duyệt bản mẫu"],
  [/^Estimated arrival: (.+)$/, (_, d) => `Dự kiến nhận hàng: ${d.startsWith("about ") ? "khoảng " + date(d.slice(6)) : date(d)}`],
  [/^Your magnets are on the way!( \((.+)\))?$/, (_, x, n) => `Nam châm đang trên đường đến!${n ? ` (${n})` : ""}`],
  [/^(.+?)( tracking (.+))?\. Follow your package all the way to your door\.$/, (_, c, x, t) => `${c}${t ? `, mã theo dõi ${t}` : ""}. Theo dõi kiện hàng đến tận cửa nhà bạn.`],
  [/^Charged to your card today, when your order shipped( \(order (.+)\))?\. Keep this email as your receipt\.$/, (_, x, n) => `Đã trừ tiền vào thẻ hôm nay, khi đơn được gửi${n ? ` (đơn ${n})` : ""}. Hãy giữ email này làm biên nhận.`],
  [/^Carrier: (.+)$/, "Hãng vận chuyển: $1"],
  [/^Tracking number: see the tracking page$/, "Mã theo dõi: xem trang theo dõi"],
  [/^Tracking number: (.+)$/, "Mã theo dõi: $1"],
  [/^Order (.+) · Out for delivery$/, "Đơn $1 · Đang giao"],
  [/^Order (.+) · Delivered$/, "Đơn $1 · Đã giao"],
  [/^(.+), your magnets arrive today!$/, "$1 ơi, nam châm đến hôm nay!"],
  [/^(.+) has your package out for delivery\. Keep an eye on the porch and the mailbox\.$/, "$1 đang giao kiện hàng của bạn. Để ý trước cửa và hộp thư nhé."],
  [/^(.+) has your package out for delivery( \(order (.+)\))?\. Keep an eye on the porch!$/, (_, c, x, n) => `${c} đang giao kiện hàng của bạn${n ? ` (đơn ${n})` : ""}. Để ý trước cửa nhé!`],
  [/^Latest scan: (.+)$/, "Cập nhật mới nhất: $1"],
  [/^(.+), how do they look on your fridge\?$/, "$1 ơi, trên tủ lạnh trông thế nào?"],
  [/^for your next order: (.+?) until (.+)\.$/, (_, o, d) => `cho đơn tiếp theo: ${off(o)} đến ${date(d)}.`],
  [/^for your next order: (.+)\.$/, (_, o) => `cho đơn tiếp theo: ${off(o)}.`],
  [/^Show us your fridge! Share a photo on Instagram and tag (.+)$/, "Khoe tủ lạnh với chúng tôi nhé! Chia sẻ ảnh trên Instagram và gắn thẻ $1"],
  [/^Return · (.+)$/, "Đổi trả · $1"],
  [/^Hi (.+?)[.!]$/, "Chào $1!"],
  [/^Your return label for (.+)$/, (_, n) => `Nhãn gửi trả cho ${ord(n)}`],
  [/^We got your return request \((.+)\)$/, (_, n) => `Chúng tôi đã nhận yêu cầu đổi trả (${ord(n)})`],
  [/^We're reprinting your magnets \((.+)\)$/, (_, n) => `Chúng tôi đang in lại nam châm (${ord(n)})`],
  [/^About your return for (.+)$/, (_, n) => `Về yêu cầu đổi trả ${ord(n)}`],
  [/^No printer\? Show this QR code at the Post Office: (.+)$/, "Không có máy in? Đưa mã QR này ở bưu điện: $1"],
  [/^In this return:\n([\s\S]+)$/, "Trong lần đổi trả này:\n$1"],
  [/^A note from us: ([\s\S]+)$/, "Lời nhắn từ chúng tôi: $1"],
  [/^A partial refund of (\$[\d.,]+) for (.+)$/, (_, a, n) => `Hoàn một phần ${a} cho ${ord(n)}`],
  [/^Your refund for (.+) is on its way$/, (_, n) => `Tiền hoàn cho ${ord(n)} đang về`],
  [/^(\$[\d.,]+) is heading back to you\. Banks usually show it within 5 to 10 business days\.$/, "$1 đang về với bạn. Ngân hàng thường hiển thị trong 5 đến 10 ngày làm việc."],
  [/^(Full|Partial) refund: (\$[\d.,]+)(.*)$/, (_, k, a, rest) => `${k === "Full" ? "Hoàn toàn bộ" : "Hoàn một phần"}: ${a}${rest.replace(/ for order /g, " cho đơn ")}`],
  [/^Back to your original payment method( for order (.+))?$/, (_, x, n) => `Về phương thức thanh toán ban đầu${n ? ` cho đơn ${n}` : ""}`],
  [/^Refunded on this order so far: (\$[\d.,]+) of (\$[\d.,]+)\.$/, "Đã hoàn cho đơn này đến nay: $1 trên $2."],
  [/^Welcome to the hive, (.+)!$/, "Chào mừng $1 đến tổ ong!"],
  [/^(\d+% off|\$[\d.,]+ off|a little something off) your first order( until (.+))?\.?$/, (_, o, x, d) => `${off(o)} cho đơn đầu tiên${d ? ` đến ${date(d)}` : ""}.`],
  [/^Your account is ready, and (.+) your first order is waiting\.$/, (_, o) => `Tài khoản đã sẵn sàng, và ưu đãi ${off(o)} cho đơn đầu tiên đang chờ bạn.`],
  [/^Thanks for joining! Here's (.+) your first order\.$/, (_, o) => `Cảm ơn bạn đã tham gia! Tặng bạn ưu đãi ${off(o)} cho đơn đầu tiên.`],
  [/^One quick tap, (.+)!$/, "Chỉ một chạm thôi, $1!"],
  [/^For your security this link expires in (.+) and works only once\. If it has expired, you can$/, (_, e) => `Vì an toàn, link này hết hạn sau ${dur(e)} và chỉ dùng được một lần. Nếu đã hết hạn, bạn có thể`],
  [/^Tap the button to choose a new password\. The link works for (.+)\.$/, (_, e) => `Bấm nút để chọn mật khẩu mới. Link có hiệu lực trong ${dur(e)}.`],
  [/^(.+), your magnets are still waiting$/, "$1 ơi, nam châm vẫn đang chờ bạn"],
  [/^We saved your (\d+) magnets?\. Pick up right where you left off\.$/, "Chúng tôi đã lưu $1 nam châm của bạn. Tiếp tục ngay chỗ bạn dừng."],
  [/^Thanks for writing, (.+)!$/, "Cảm ơn $1 đã viết!"],
  [/^You wrote · (.+)$/, (_, t) => `Bạn đã viết · ${look(t) || t}`],
  [/^Thanks! We'll reply within 1 business day with ideas, a price for (\d+) magnets and next steps\.$/, "Cảm ơn! Chúng tôi sẽ trả lời trong 1 ngày làm việc với ý tưởng, giá cho $1 nam châm và các bước tiếp theo."],
  [/^Thanks! We'll reply within 1 business day with ideas, a price and next steps\.$/, "Cảm ơn! Chúng tôi sẽ trả lời trong 1 ngày làm việc với ý tưởng, giá và các bước tiếp theo."],
  [/^Here's your link, (.+)$/, "Link của bạn đây, $1"],
  [/^Your payment link for (.+)$/, "Link thanh toán cho $1"],
  [/^(\$[\d.,]+) for (.+)\. Pay securely by card, Apple Pay or Google Pay\.$/, "$1 cho $2. Thanh toán an toàn bằng thẻ, Apple Pay hoặc Google Pay."],
  [/^Payments are processed by Stripe\. We never see or store your card number\.( This link works until (.+)\.)?$/, (_, x, d) => `Thanh toán do Stripe xử lý. Chúng tôi không bao giờ thấy hay lưu số thẻ của bạn.${d ? ` Link có hiệu lực đến ${date(d)}.` : ""}`],
  // the Stripe checkout page (functions/checkout.js)
  [/^(\d+) custom photo magnets, 2 × 2 in$/, "$1 nam châm ảnh theo yêu cầu, 2 × 2 inch (5 cm)"],
  [/^(\d+) custom magnets\. We email you about your design after checkout\.$/, "$1 nam châm đặt riêng. Sau khi thanh toán, chúng tôi sẽ email về thiết kế của bạn."],
  [/^(.+) discount included$/, "đã gồm giảm giá $1"],
  [/^(\d+) photo magnets$/, "$1 nam châm ảnh"],
  [/^(\d+) photos?$/, "$1 ảnh"],
  [/^(\d+) frames$/, "$1 khung"],
  [/^(\d+) packs$/, "$1 gói"],
  [/^(.+) frame$/, (_, f) => `Khung ${(look(f) || f).toLowerCase()}`],
  [/^(.+) magnet$/, "Nam châm $1"],
  [DATE_ONLY, (s) => (s.startsWith("about ") ? "khoảng " + date(s.slice(6)) : date(s))],
  [/^Good news, (.+)!$/, "Tin vui, $1!"],
  [/^Thank you, (.+)!$/, "Cảm ơn $1!"],
  [/^Thanks, (.+)!$/, "Cảm ơn $1!"],
  [/^Hi (.+),$/, "Chào $1,"],
  [/^Order (LHH-\d+)$/, "Đơn $1"],
  [/^Qty (\d+)$/, "SL $1"],
  [/^(\d+) magnets( × (\d+))?$/, (_, n, x, q) => `${n} nam châm${q ? ` × ${q}` : ""}`],
  [/^Volume discount \((\d+)% off\)$/, "Giảm giá theo số lượng (giảm $1%)"],
  [/^Promo code (.+)$/, "Mã khuyến mãi $1"],
  [/^(.+), (\d+)% off$/, "$1, giảm $2%"],
  [/^(.+), (\d+) designs? free$/, "$1, tặng $2 mẫu"],
  [/^Captions: (.+)$/, "Chú thích: $1"],
  [/^Note: (.+)$/, "Ghi chú: $1"],
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
