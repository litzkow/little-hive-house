// Little Hive House emails (and the Stripe checkout page) in Korean (polite 해요체).
// look(key): the exact dictionary (functions/emails/ko.json), the collection names, then the patterns below.
"use strict";

let DICT = null;
function dict() {
  if (!DICT) { try { DICT = require("../ko.json"); } catch (e) { DICT = {}; } }
  return DICT;
}
const MON = { Jan: 1, Feb: 2, Mar: 3, Apr: 4, May: 5, Jun: 6, Jul: 7, Aug: 8, Sep: 9, Oct: 10, Nov: 11, Dec: 12,
  January: 1, February: 2, March: 3, April: 4, June: 6, July: 7, August: 8, September: 9, October: 10, November: 11, December: 12 };
const M = "(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)";
/** "Nov 17–20" → "11월 17–20일"; "Nov 28–Dec 2" → "11월 28일–12월 2일"; "November 3, 2026" → "2026년 11월 3일" */
function date(s) {
  return String(s)
    .replace(new RegExp(M + " (\\d{1,2}), (\\d{4})", "g"), (_, m, d, y) => `${y}년 ${MON[m]}월 ${d}일`)
    .replace(new RegExp(M + " (\\d{1,2})[–-](\\d{1,2})\\b", "g"), (_, m, a, b) => `${MON[m]}월 ${a}–${b}일`)
    .replace(new RegExp(M + " (\\d{1,2})[–-]" + M + " (\\d{1,2})", "g"), (_, m1, a, m2, b) => `${MON[m1]}월 ${a}일–${MON[m2]}월 ${b}일`)
    .replace(new RegExp(M + " (\\d{1,2})\\b", "g"), (_, m, d) => `${MON[m]}월 ${d}일`);
}
/** "15% off" → "15% 할인"; "$5.00 off" → "$5.00 할인" */
function off(s) {
  s = String(s);
  let m = /^(\d+)% off$/.exec(s); if (m) return `${m[1]}% 할인`;
  m = /^(\$[\d.,]+) off$/.exec(s); if (m) return `${m[1]} 할인`;
  return s === "a little something off" ? "작은 할인" : s;
}
/** "1 hour" → "1시간"; "30 minutes" → "30분" */
function dur(s) { return String(s).replace(/\b1 hour\b/, "1시간").replace(/(\d+) hours/, "$1시간").replace(/(\d+) minutes/, "$1분"); }
const ord = (n) => (n === "your order" ? "주문" : `주문 ${n}`);
const ev = (n) => (n === "Black Friday" ? "블랙 프라이데이" : n === "Cyber Monday" ? "사이버 먼데이" : n);
const COL = {
  "USA Places": "미국 명소", "World Places": "세계 명소", "Ink Cities": "잉크로 그린 도시", "City Sketches": "도시 스케치",
  "Fall": "가을", "Halloween": "핼러윈", "Horror Classics": "고전 호러", "Furry Friends": "털복숭이 친구들", "Kitchen Words": "주방 문구",
  "Americana": "아메리카나", "México": "멕시코", "Ireland": "아일랜드", "Italia": "이탈리아", "Puerto Rico": "푸에르토리코", "Pilipinas": "필리핀",
  "India": "인도", "Korea": "한국", "Japan": "일본", "Brasil": "브라질", "Greece": "그리스", "France": "프랑스",
  "Great Masters": "거장의 명화", "Mythology": "신화", "Home Notes": "집 안 메모", "Night Sky": "밤하늘",
  "Birth Flowers": "탄생화", "Storybook Classics": "고전 문학", "Fairy Tales & Myths": "동화와 신화",
  "Wise Words": "명언", "Holidays & Dates": "기념일", "Bumper Stickers": "범퍼 스티커",
  "Christmas": "크리스마스", "Summer": "여름", "Heritage": "뿌리",
};
const DATE_ONLY = new RegExp("^(about )?" + M + " \\d{1,2}([–-](" + M + " )?\\d{1,2})?(, \\d{4})?$");
const P = [
  [/^Here's everything that's coming your way, ordered (.+)\.$/, (_, d) => `${date(d)}에 주문하신 상품이 모두 이렇게 가고 있어요.`],
  [/^Here's everything that's coming your way\.$/, "주문하신 상품이 모두 이렇게 가고 있어요."],
  [/^(\d+) magnets? coming your way\. We'll start making them by hand right away\.$/, "자석 $1개가 곧 찾아가요. 바로 손으로 만들기 시작할게요."],
  [/^Thank you! Order (.+) is confirmed$/, "감사합니다! 주문 $1 확정"],
  [/^Estimated arrival: about 1 to 2 weeks after you approve the proof$/, "도착 예정: 시안 승인 후 약 1–2주"],
  [/^Estimated arrival: (.+)$/, (_, d) => `도착 예정: ${d.startsWith("about ") ? date(d.slice(6)) + "쯤" : date(d)}`],
  [/^Your magnets are on the way!( \((.+)\))?$/, (_, x, n) => `자석이 출발했어요!${n ? ` (${n})` : ""}`],
  [/^(.+?)( tracking (.+))?\. Follow your package all the way to your door\.$/, (_, c, x, t) => `${c}${t ? `, 운송장 번호 ${t}` : ""}. 집 앞까지 상품을 따라가 보세요.`],
  [/^Charged to your card today, when your order shipped( \(order (.+)\))?\. Keep this email as your receipt\.$/, (_, x, n) => `주문이 발송된 오늘 카드로 결제됐어요${n ? ` (주문 ${n})` : ""}. 이 이메일을 영수증으로 보관하세요.`],
  [/^Carrier: (.+)$/, "배송사: $1"],
  [/^Tracking number: see the tracking page$/, "운송장 번호: 배송 조회 페이지를 확인하세요"],
  [/^Tracking number: (.+)$/, "운송장 번호: $1"],
  [/^Order (.+) · Out for delivery$/, "주문 $1 · 오늘 배송 예정"],
  [/^Order (.+) · Delivered$/, "주문 $1 · 배송 완료"],
  [/^(.+), your magnets arrive today!$/, "$1님, 오늘 자석이 도착해요!"],
  [/^(.+) has your package out for delivery\. Keep an eye on the porch and the mailbox\.$/, "$1에서 상품을 배송하고 있어요. 현관과 우편함을 잘 살펴보세요."],
  [/^(.+) has your package out for delivery( \(order (.+)\))?\. Keep an eye on the porch!$/, (_, c, x, n) => `${c}에서 상품을 배송하고 있어요${n ? ` (주문 ${n})` : ""}. 현관을 잘 살펴보세요!`],
  [/^Latest scan: (.+)$/, "최근 배송 기록: $1"],
  [/^(.+), how do they look on your fridge\?$/, "$1님, 냉장고에 붙이니 어떤가요?"],
  [/^for your next order: (.+?) until (.+)\.$/, (_, o, d) => `다음 주문 ${off(o)}, ${date(d)}까지.`],
  [/^for your next order: (.+)\.$/, (_, o) => `다음 주문 ${off(o)}.`],
  [/^Show us your fridge! Share a photo on Instagram and tag (.+?)\.?$/, "냉장고를 보여 주세요! 인스타그램에 사진을 올리고 태그해 주세요: $1"],
  [/^Return · (.+)$/, "반품 · $1"],
  [/^Hi (.+?)[.!]$/, "$1님, 안녕하세요!"],
  [/^Your return label for (.+)$/, (_, n) => `${ord(n)} 반품 송장`],
  [/^We got your return request \((.+)\)$/, (_, n) => `반품 신청을 받았어요 (${ord(n)})`],
  [/^We're reprinting your magnets \((.+)\)$/, (_, n) => `자석을 다시 인쇄하고 있어요 (${ord(n)})`],
  [/^About your return for (.+)$/, (_, n) => `${ord(n)} 반품 안내`],
  [/^No printer\? Show this QR code at the Post Office: (.+)$/, "프린터가 없으세요? 우체국에서 이 QR 코드를 보여 주세요: $1"],
  [/^In this return:\n([\s\S]+)$/, "이번 반품:\n$1"],
  [/^A note from us: ([\s\S]+)$/, "저희가 남기는 말: $1"],
  [/^A partial refund of (\$[\d.,]+) for (.+)$/, (_, a, n) => `${ord(n)} 부분 환불 ${a}`],
  [/^Your refund for (.+) is on its way$/, (_, n) => `${ord(n)} 환불이 진행 중이에요`],
  [/^(\$[\d.,]+) is heading back to you\. Banks usually show it within 5 to 10 business days\.$/, "$1을(를) 돌려 드리고 있어요. 은행에는 보통 영업일 5–10일 안에 표시돼요."],
  [/^(Full|Partial) refund: (\$[\d.,]+)(.*)$/, (_, k, a, rest) => `${k === "Full" ? "전액 환불" : "부분 환불"}: ${a}${rest.replace(/ for order /g, ", 주문 ").replace(/order/g, "주문")}`],
  [/^Back to your original payment method( for order (.+))?$/, (_, x, n) => `${n ? `주문 ${n}, ` : ""}원래 결제 수단으로 환불`],
  [/^Refunded on this order so far: (\$[\d.,]+) of (\$[\d.,]+)\.$/, "이 주문의 지금까지 환불 금액: $2 중 $1."],
  [/^Welcome to the hive, (.+)!$/, "$1님, 벌집에 오신 걸 환영해요!"],
  [/^(\d+% off|\$[\d.,]+ off|a little something off) your first order(,? until (.+?))?\.?$/, (_, o, x, d) => `첫 주문 ${off(o)}${d ? `, ${date(d)}까지` : ""}.`],
  [/^Your account is ready, and (.+) your first order is waiting\.$/, (_, o) => `계정이 준비됐고, 첫 주문 ${off(o)} 혜택이 기다리고 있어요.`],
  [/^Thanks for joining! Here's (.+) your first order\.$/, (_, o) => `가입해 주셔서 감사해요! 첫 주문 ${off(o)} 혜택을 드려요.`],
  [/^One quick tap, (.+)!$/, "$1님, 한 번만 눌러 주세요!"],
  [/^For your security this link expires in (.+) and works only once\. If it has expired, you can$/, (_, e) => `보안을 위해 이 링크는 ${dur(e)} 후 만료되고 한 번만 쓸 수 있어요. 만료됐다면`],
  [/^Tap the button to choose a new password\. The link works for (.+)\.$/, (_, e) => `버튼을 눌러 새 비밀번호를 정하세요. 링크는 ${dur(e)} 동안 유효해요.`],
  [/^(.+), your magnets are still waiting$/, "$1님, 자석이 아직 기다리고 있어요"],
  [/^We saved your (\d+) magnets?\. Pick up right where you left off\.$/, "자석 $1개를 저장해 뒀어요. 하던 데서 바로 이어 가세요."],
  [/^Thanks for writing, (.+)!$/, "$1님, 메시지 감사해요!"],
  [/^You wrote · (.+)$/, (_, t) => `보내신 내용 · ${look(t) || t}`],
  [/^Thanks! We'll reply within 1 business day with ideas, a price for (\d+) magnets and next steps\.$/, "감사합니다! 영업일 1일 안에 아이디어, 자석 $1개 가격, 다음 단계를 보내 드릴게요."],
  [/^Thanks! We'll reply within 1 business day with ideas, a price and next steps\.$/, "감사합니다! 영업일 1일 안에 아이디어, 가격, 다음 단계를 보내 드릴게요."],
  [/^Here's your link, (.+)$/, "$1님, 링크를 보내 드려요"],
  [/^Your payment link for (.+)$/, "결제 링크: $1"],
  [/^(\$[\d.,]+) for (.+)\. Pay securely by card, Apple Pay or Google Pay\.$/, "$2: $1. 카드, Apple Pay, Google Pay로 안전하게 결제하세요."],
  [/^Payments are processed by Stripe\. We never see or store your card number\.( This link works until (.+)\.)?$/, (_, x, d) => `결제는 Stripe가 처리해요. 저희는 카드 번호를 보거나 저장하지 않아요.${d ? ` 이 링크는 ${date(d)}까지 유효해요.` : ""}`],
  // the Stripe checkout page (functions/checkout.js)
  [/^(\d+) custom photo magnets, 2 × 2 in$/, "맞춤 사진 자석 $1개, 2 × 2인치(5cm)"],
  [/^(\d+) custom magnets\. We email you about your design after checkout\.$/, "맞춤 자석 $1개. 결제 후 디자인에 대해 이메일 드려요."],
  [/^(.+) discount included$/, (_, n) => `${ev(n)} 할인 포함`],
  [/^(\d+) photo magnets$/, "사진 자석 $1개"],
  [/^(\d+) photos?$/, "사진 $1장"],
  [/^(\d+) frames$/, "프레임 $1가지"],
  [/^(\d+) packs$/, "팩 $1개"],
  [/^(.+) frame$/, (_, f) => `${look(f) || f} 프레임`],
  [/^(.+) magnet$/, "$1 자석"],
  [DATE_ONLY, (s) => (s.startsWith("about ") ? date(s.slice(6)) + "쯤" : date(s))],
  [/^Good news, (.+)!$/, "$1님, 좋은 소식이에요!"],
  [/^Thank you, (.+)!$/, "감사합니다, $1님!"],
  [/^Thanks, (.+)!$/, "감사합니다, $1님!"],
  [/^Hi (.+),$/, "$1님, 안녕하세요."],
  [/^Order (LHH-\d+)$/, "주문 $1"],
  [/^Qty (\d+)$/, "수량 $1"],
  [/^(\d+) magnets( × (\d+))?$/, (_, n, x, q) => `자석 ${n}개${q ? ` × ${q}` : ""}`],
  [/^Volume discount \((\d+)% off\)$/, (_, p) => `대량 할인 (${p}% 할인)`],
  [/^Promo code (.+)$/, "프로모션 코드 $1"],
  [/^(.+), (\d+)% off$/, (_, n, p) => `${ev(n)}, ${p}% 할인`],
  [/^(.+), (\d+) designs? free$/, (_, n, k) => `${ev(n)}, 디자인 ${k}개 무료`],
  [/^Captions: (.+)$/, "문구: $1"],
  [/^Note: (.+)$/, "요청 사항: $1"],
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
