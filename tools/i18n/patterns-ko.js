/* Patterns: English text with a number, a date or a name in it. Each is [regex, Korean] where the Korean is a
   replacement string ($1…) or a function of the match. Checked in order, after the exact dictionary.
   Polite 해요체. Prices keep the US format ($5.49, 1,200). Names go before a colon so no particle (은/는, 을/를) is needed. */
var COL = {
  "USA Places": "미국 명소", "World Places": "세계 명소", "Ink Cities": "잉크로 그린 도시",
  "City Sketches": "도시 스케치", "Fall": "가을", "Halloween": "핼러윈", "Horror Classics": "고전 호러",
  "Furry Friends": "털복숭이 친구들", "Kitchen Words": "주방 문구", "Americana": "아메리카나", "México": "멕시코",
  "Ireland": "아일랜드", "Italia": "이탈리아", "Puerto Rico": "푸에르토리코", "Pilipinas": "필리핀", "India": "인도",
  "Korea": "한국", "Japan": "일본", "Brasil": "브라질", "Greece": "그리스", "France": "프랑스",
  "Great Masters": "거장의 명화", "Mythology": "신화", "Home Notes": "집 안 메모", "Bee Kind": "Bee Kind",
  "Night Sky": "밤하늘", "Birth Flowers": "탄생화", "Storybook Classics": "고전 문학",
  "Fairy Tales & Myths": "동화와 신화", "Wise Words": "명언", "Holidays & Dates": "기념일",
  "Bumper Stickers": "범퍼 스티커", "Christmas": "크리스마스", "Summer": "여름", "Heritage": "뿌리",
  "Photo magnets": "사진 자석", "Custom photo magnets": "맞춤 사진 자석"
};
var FRAME = { "Arch": "아치", "Art deco": "아르데코", "Autumn": "가을", "Birthday": "생일", "Botanical": "보태니컬",
  "Circle": "원형", "Classic": "클래식", "Crisp white mat": "흰색 매트", "Date stamp": "날짜 도장",
  "Eucalyptus wreath": "유칼립투스 리스", "Film frame": "필름 프레임", "Full photo": "사진 전체",
  "Gallery mat": "갤러리 매트", "Gallery with caption": "캡션 있는 갤러리", "Gold line": "골드 라인",
  "Graduation": "졸업", "Handwritten": "손글씨", "Holiday": "명절", "Honeycomb": "벌집",
  "Instant print": "즉석 사진", "Love": "사랑", "Modern": "모던", "Name band": "이름 띠",
  "Postage stamp": "우표", "Postcard": "엽서", "Rounded modern": "둥근 모던",
  "Scalloped lace": "물결 레이스", "Script": "필기체", "Sweet dreams": "좋은 꿈 꿔", "Team": "팀",
  "Thin white border": "얇은 흰 테두리", "Tropical leaves": "열대 잎사귀", "Vintage ornate gold": "빈티지 골드 장식",
  "Watercolour peonies": "수채화 작약", "Wedding": "웨딩", "Winter": "겨울", "No border": "테두리 없음" };
function fr(s) { return FRAME[s] || s; }
function col(s) { return COL[s] || s; }
/** only for the shop's own collection names: anything else is left to the dictionary */
function known(s) { return Object.prototype.hasOwnProperty.call(COL, s) || /^(Americana|México|Brasil|Halloween|Bee Kind)$/.test(s); }
var MON = { Jan: 1, Feb: 2, Mar: 3, Apr: 4, May: 5, Jun: 6, Jul: 7, Aug: 8, Sep: 9, Oct: 10, Nov: 11, Dec: 12,
  January: 1, February: 2, March: 3, April: 4, June: 6, July: 7, August: 8, September: 9, October: 10, November: 11, December: 12 };
var DAY = { Mon: "월", Tue: "화", Wed: "수", Thu: "목", Fri: "금", Sat: "토", Sun: "일",
  Monday: "월", Tuesday: "화", Wednesday: "수", Thursday: "목", Friday: "금", Saturday: "토", Sunday: "일" };
var D = "(Mon|Tue|Wed|Thu|Fri|Sat|Sun|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)";
var M = "(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)";
/* "Nov 17–20" → "11월 17–20일"; "Nov 28–Dec 2" → "11월 28일–12월 2일"; "November 3, 2026" → "2026년 11월 3일";
   "Tue, Nov 17" → "11월 17일 (화)" */
function date(s) {
  return s
    .replace(new RegExp("\\b" + D + "\\b,? " + M + " (\\d{1,2})(?:, (\\d{4}))?\\b", "g"), function (_, d, m, n, y) { return (y ? y + "년 " : "") + MON[m] + "월 " + n + "일 (" + DAY[d] + ")"; })
    .replace(new RegExp("\\b" + D + "\\b,? ?", "g"), function (_, d) { return DAY[d] + "요일 "; })
    .replace(new RegExp(M + " (\\d{1,2}), (\\d{4})", "g"), function (_, m, d, y) { return y + "년 " + MON[m] + "월 " + d + "일"; })
    .replace(new RegExp(M + " (\\d{1,2})[–-](\\d{1,2})\\b", "g"), function (_, m, a, b) { return MON[m] + "월 " + a + "–" + b + "일"; })
    .replace(new RegExp(M + " (\\d{1,2})[–-]" + M + " (\\d{1,2})", "g"), function (_, m1, a, m2, b) { return MON[m1] + "월 " + a + "일–" + MON[m2] + "월 " + b + "일"; })
    .replace(new RegExp(M + " (\\d{1,2})\\b", "g"), function (_, m, d) { return MON[m] + "월 " + d + "일"; })
    .replace(new RegExp(M + " (\\d{4})", "g"), function (_, m, y) { return y + "년 " + MON[m] + "월"; });
}
function off(p) { return p + "% 할인"; }
function tr(s) { return COL[s] || (window.LHH_I18N ? window.LHH_I18N.t(s) : s); }
function ev(n) { return n === "Black Friday" ? "블랙 프라이데이" : n === "Cyber Monday" ? "사이버 먼데이" : n; }
var FOR = { "your business": "비즈니스", "your wedding": "웨딩", "your graduation": "졸업", "your party or event": "파티나 행사", "your home": "집",
  business: "비즈니스", wedding: "웨딩", graduation: "졸업", party: "파티" };
var PATTERNS = [
  [/^([\d,]+) ready-made designs for (your business|your wedding|your graduation|your party or event|your home)\. Tap one to change the colors and the words, add your (logo|photo) and see it right away\.$/, function (_, n, w, x) { return FOR[w] + "용 기성 디자인 " + n + "개. 하나를 눌러 색과 문구를 바꾸고 " + (x === "logo" ? "로고" : "사진") + "를 넣으면 바로 볼 수 있어요."; }],
  [/^(\d+) kinds · ([\d,]+) designs$/, "$1가지 · 디자인 $2개"],
  [/^(\d+) (magnets?) · \$([\d.]+)(?: \(\$([\d.]+) each\))?$/, function (_, n, m, p, e) { return "자석 " + n + "개 · $" + p + (e ? " (개당 $" + e + ")" : ""); }],
  [/^From \$(\d+) a magnet$/, "개당 $$$1부터"],
  [/^\$([\d.]+) · sent to your email$/, "$$$1 · 이메일로 발송"],
  [/^Hundreds of designs to make yours: change the words and colors, add a photo\. From \$(\d+)\.$/, "나만의 것으로 만들 수 있는 수백 가지 디자인: 문구와 색을 바꾸고 사진을 넣으세요. $$$1부터."],
  [/^Every magnet is made just for you\. Want only the design\? \$([\d.]+) for the file, free with any magnet\.$/, "모든 자석은 고객님만을 위해 만들어요. 디자인만 필요하세요? 파일은 $$$1, 자석을 사면 무료예요."],
  [/^Yes\. Tap the design, make it yours and choose “Only want the file”: \$([\d.]+), sent to your email right away, no magnet\. It is free with any magnet order\.$/, "네. 디자인을 눌러 나만의 것으로 만든 뒤 “파일만 필요하세요?”를 고르세요: $$$1, 바로 이메일로 보내 드리고, 자석은 포함되지 않아요. 자석을 주문하시면 무료예요."],
  [/^([^·<]{2,40}) · ([^·<]{2,40})$/, function (_, a, b) { var x = tr(a), y = tr(b); return x !== a || y !== b ? x + " · " + y : null; }],
  [/^1 magnet$/, "자석 1개"],
  [/^(\d+) photo designs with names, dates and captions$/, "이름, 날짜, 문구를 넣은 사진 디자인 $1개"],
  [/^\$(\d+) · \$([\d.]+) each$/, "$$$1 · 개당 $$$2"],
  [/^Photo ([\d, ]+) didn't finish uploading\. Please try again\.$/, "사진 $1 업로드가 끝나지 않았어요. 다시 시도해 주세요."],
  [/^Photo (\d+) didn't upload correctly\. Please remove it and add it again\.$/, "사진 $1이(가) 제대로 업로드되지 않았어요. 삭제하고 다시 추가해 주세요."],
  [/^Photo (\d+) is too big or empty\.$/, "사진 $1이(가) 너무 크거나 비어 있어요."],
  [/^Cart <span>(\d+)<\/span>$/, "장바구니 <span>$1</span>"],
  [/^Order today and it arrives about (.+) in the US\. <a>Shipping details<\/a>$/, function (_, d) { return "오늘 주문하면 미국 내 " + date(d) + "쯤 도착해요. <a>배송 안내</a>"; }],
  // cart, photo builder, checkout (assets/site.js, custom.js, checkout.js)
  [/^One less (.+)$/, "하나 빼기: $1"],
  [/^One more (.+)$/, "하나 더: $1"],
  [/^Add (\d+) more magnets for (\d+)% off your whole order\.$/, function (_, k, p) { return "자석 " + k + "개만 더 담으면 전체 주문 " + off(p) + "."; }],
  [/^Order today and it arrives about (.+) in the US\.$/, function (_, d) { return "오늘 주문하면 미국 내 " + date(d) + "쯤 도착해요."; }],
  [/^Custom photo magnets$/, "맞춤 사진 자석"],
  [/^(.+) added to cart$/, function (_, x) { return "장바구니에 담았어요: " + tr(x); }],
  [/^Your (\d+) magnets are in the cart$/, "자석 $1개를 장바구니에 담았어요"],
  [/^(\d+) magnets · we plan the design with you by email after checkout$/, "자석 $1개 · 결제 후 이메일로 함께 디자인해요"],
  // bulk-order pages (business, weddings, graduation, parties): packs, the mailing service, the QR maker
  [/^(\d+) magnets · \$([\d.,]+) \(\$([\d.,]+) each\)$/, "자석 $1개 · $$$2 (개당 $$$3)"],
  [/^(\d+) addresses$/, "주소 $1곳"],
  [/^(\d+) addresses · we ask for your list after checkout$/, "주소 $1곳 · 결제 후 명단을 받아요"],
  [/^(\d+) magnets · style: (.+) · we plan the design with you by email after checkout$/, function (_, n, s) { return "자석 " + n + "개 · 스타일: " + tr(s) + " · 결제 후 이메일로 함께 디자인해요"; }],
  [/^(\d+) QR magnets · (.+) · proof before we print$/, "QR 자석 $1개 · $2 · 인쇄 전 시안 확인"],
  [/^Mailed to your list, (\d+) addresses$/, "명단으로 우편 발송, 주소 $1곳"],
  [/^Graduation & college, (\d+) magnets$/, "졸업 & 대학, 자석 $1개"],
  [/^(\d+) magnets · (\d+) photos? · (\d+) frames$/, "자석 $1개 · 사진 $2장 · 프레임 $3가지"],
  [/^(\d+) magnets · (\d+) photos? · (.+)$/, function (_, a, b, f) { return "자석 " + a + "개 · 사진 " + b + "장 · " + fr(f); }],
  [/^2 × 2 in · (.+)$/, function (_, c) { return "2 × 2인치 · " + col(c); }],
  [/^(.+) magnet$/, "$1 자석"],
  [/^Remove photo (\d+)$/, "사진 $1 삭제"],
  [/^1 photo is too small and may print blurry\. (.+)$/, "사진 1장이 너무 작아서 흐리게 인쇄될 수 있어요. 선명한 자석을 원하시면 스크린샷이나 메신저에서 저장한 사진 말고 카메라 롤의 원본 사진을 쓰세요."],
  [/^(\d+) photos are too small and may print blurry\. (.+)$/, "사진 $1장이 너무 작아서 흐리게 인쇄될 수 있어요. 선명한 자석을 원하시면 스크린샷이나 메신저에서 저장한 사진 말고 카메라 롤의 원본 사진을 쓰세요."],
  [/^(\d+) photos added\. This pack holds (\d+), so remove (\d+) or pick a bigger pack\.$/, "사진 $1장을 추가했어요. 이 팩은 $2장까지라서 $3장을 삭제하거나 더 큰 팩을 고르세요."],
  [/^(\d+) of (\d+) photos added\. We will repeat your favorites to fill the pack, or tell us in the notes\.$/, "사진 $2장 중 $1장을 추가했어요. 좋아하는 사진을 반복해서 팩을 채우거나, 요청 사항에 알려 주세요."],
  [/^Frame for photo (\d+)$/, "사진 $1의 프레임"],
  [/^Photo (\d+): (.+) frame(, caption (.+?))?(, low resolution)?\. Choose frame$/, function (_, k, f, c1, c, low) { return "사진 " + k + ": " + fr(f) + " 프레임" + (c ? ", 문구 " + c : "") + (low ? ", 저해상도" : "") + ". 프레임 고르기"; }],
  [/^Preview of photo (\d+) with the (.+?) frame( and the caption (.+))?$/, function (_, k, f, c1, c) { return "사진 " + k + " 미리보기, " + fr(f) + " 프레임" + (c ? ", 문구 " + c : ""); }],
  [/^Apply this frame to all (\d+) photos$/, "사진 $1장 모두에 이 프레임 적용"],
  [/^(.+) is now on all (\d+) photos\.$/, function (_, f, k) { return "사진 " + k + "장 모두에 " + fr(f) + " 프레임을 적용했어요."; }],
  [/^Caption added to all (\d+) photos\. It prints on photos with a caption frame\.$/, "사진 $1장 모두에 문구를 넣었어요. 문구가 있는 프레임에서만 인쇄돼요."],
  [/^All (\d+) photos uploaded$/, "사진 $1장 모두 업로드 완료"],
  [/^Uploading your photo · (\d+)%$/, "사진 업로드 중 · $1%"],
  [/^Uploading your (\d+) photos · (\d+)%$/, "사진 $1장 업로드 중 · $2%"],
  // orders, account, returns (assets/orders.js, account.js, return.js)
  [/^Tracking history \((\d+) scans?\)$/, "배송 기록 ($1건)"],
  [/^(.+) has your package out for delivery\. Keep an eye on the porch!$/, "$1에서 상품을 배송하고 있어요. 현관을 잘 살펴보세요!"],
  [/^Your package is with (.+?)\.( It shipped on (.+?)\.)?( We’ll email you when it’s out for delivery and when it arrives\.)?$/, function (_, c, s1, d, tail) { return "상품이 " + c + "에 있어요." + (d ? " " + d + "에 발송됐어요." : "") + (tail ? " 배송을 시작하고 도착하면 이메일로 알려 드려요." : ""); }],
  [/^Delivered on (.+?)\. We hope you love them!$/, "$1에 배송 완료됐어요. 마음에 드시길 바라요!"],
  [/^We hope you love them!$/, "마음에 드시길 바라요!"],
  [/^We refunded (\$[\d.,]+)\. Refunds take 5 to 10 business days to show on your statement\.$/, "$1을(를) 환불해 드렸어요. 명세서에 표시되기까지 영업일 5–10일 걸려요."],
  [/^Rating for (.+)$/, "$1 별점"],
  [/^Thank you, (.+)!$/, "감사합니다, $1님!"],
  [/^Order (LHH-\d+) is confirmed\. We emailed you a receipt, so keep it handy for tracking\.$/, "주문 $1이(가) 확정됐어요. 영수증을 이메일로 보내 드렸으니 배송 조회할 때 쓰세요."],
  [/^Check your inbox\. If there’s an account for (.+?), we just sent a link to choose a new password\.( It can take a minute, and sometimes lands in spam\.)?$/, function (_, e, tail) { return "메일함을 확인하세요. " + e + " 계정이 있다면 새 비밀번호를 정할 수 있는 링크를 방금 보냈어요." + (tail ? " 1분쯤 걸릴 수 있고, 가끔 스팸함에 들어가요." : ""); }],
  [/^See all (\d+) orders$/, "주문 $1건 모두 보기"],
  [/^We found (\d+) earlier orders with your email and added them to your account\.$/, "회원님 이메일로 된 이전 주문 $1건을 찾아 계정에 추가했어요."],
  [/^Signed in as (.+)\.$/, "로그인: $1"],
  [/^We emailed (.+) a link to choose a new password\.$/, "새 비밀번호를 정할 수 있는 링크를 보냈어요: $1"],
  [/^Your account and orders \(signed in as (.+)\)$/, "내 계정과 주문 (로그인: $1)"],
  [/^(.+) saved to your favorites$/, function (_, x) { return "찜 목록에 저장했어요: " + tr(x); }],
  [/^(.+) removed from favorites$/, function (_, x) { return "찜 목록에서 삭제했어요: " + tr(x); }],
  [/^Refunded (\$[\d.,]+) on (.+)\.$/, "$2에 $1 환불됨."],
  [/^(\$[\d.,]+) back to your card on (.+)$/, "$2에 카드로 $1 환불"],
  [/^Your refund: (\$[\d.,]+) \((\$[\d.,]+) for the magnets − (\$[\d.,]+) return shipping\)\.$/, "환불 금액: $1 (자석 $2 − 반품 배송비 $3)."],
  [/^(\d+) magnets · (\$[\d.,]+) each$/, "자석 $1개 · 개당 $2"],
  [/^(\$[\d.,]+) each$/, "개당 $1"],
  [/^This account is turned off\. Email (.+) and we’ll sort it out\.$/, "이 계정은 사용 중지됐어요. $1으로 메일 주시면 해결해 드릴게요."],
  [/^We couldn’t save one of your photos\. (.+?) or email (.+?)\.?$/, "사진 하나를 저장하지 못했어요. 25MB 이하의 일반 사진(JPG, PNG, HEIC, WebP)으로 다시 시도하시거나 $2으로 메일 주세요."],
  [/^We can’t take photo uploads right now\. Please email (.+)$/, "지금은 사진을 업로드할 수 없어요. $1으로 메일 주세요."],
  [/^Something went wrong on our side\. Please try again, or email (.+)$/, "저희 쪽에 문제가 생겼어요. 다시 시도하시거나 $1으로 메일 주세요."],
  [/^This link has expired or is incomplete\. Email (.+) and we’ll remove you by hand\.$/, "링크가 만료됐거나 불완전해요. $1으로 메일 주시면 직접 빼 드릴게요."],
  [/^Your email app should open now\. If it doesn't, write to us at (.+)$/, "이메일 앱이 곧 열려요. 열리지 않으면 $1으로 메일 주세요."],
  [/^Ordering today\? Most US orders arrive <strong>about (.+)<\/strong>\.$/, function (_, d) { return "오늘 주문하세요? 미국 내 주문은 대부분 <strong>" + date(d) + "쯤</strong> 도착해요."; }],
  [/^(\d+) photos? added, (\$[\d.,]+) each$/, "사진 $1장 추가됨, 장당 $2"],
  [/^Add 1 to 3 photos, (\$[\d.,]+) each$/, "사진 1–3장 추가, 장당 $1"],
  [/^Add 1 more photo and get the pack of 4 for (\$[\d.,]+)\.$/, "사진 1장만 더 추가하면 4장 팩을 $1에 받아요."],
  [/^(\d+) photos: pack of (\d+) \+ (\d+) extra photos? \((\$[\d.,]+) each\)$/, "사진 $1장: $2장 팩 + 추가 $3장 (장당 $4)"],
  [/^Only want (\d+) magnets?\? Make just these for (\$[\d.,]+)$/, "자석 $1개만 필요하세요? 이것만 $2에 만들기"],
  [/^Add (\d+) more photos? at no extra cost: they fit in your pack of (\d+)\.$/, "추가 비용 없이 사진 $1장을 더 넣을 수 있어요: $2장 팩에 들어가요."],
  [/^Want more\? Add 1 more photo for (\$[\d.,]+), or 2 for (\$[\d.,]+)\.$/, "더 필요하세요? 사진 1장 추가는 $1, 2장은 $2."],
  [/^Same price, more room: we moved you to the pack of (\d+)\. Add (\d+) more photos? at no extra cost\.$/, "같은 가격에 더 넉넉하게: $1장 팩으로 바꿔 드렸어요. 추가 비용 없이 사진 $2장을 더 넣을 수 있어요."],
  [/^A photo order holds up to (\d+) photos, so (\d+) (?:was|were) not added\.$/, "사진 주문은 최대 $1장이라서 $2장은 추가되지 않았어요."],
  [/^(\d+) of (\d+) photos added$/, "사진 $2장 중 $1장 추가됨"],
  [/^Photo (\d+) of (\d+)$/, "사진 $1 / $2"],
  [/^<span>(\d+\/\d+)<\/span> · Optional, leave empty for none$/, "<span>$1</span> · 선택 사항, 없으면 비워 두세요"],
  [/^(\d+) designs · \$5 each$/, "디자인 $1개 · 개당 $$5"],
  [/^(\d+) countries · (\d+) designs · \$5 each$/, "$1개 나라 · 디자인 $2개 · 개당 $$5"],
  [/^See all (\d+)$/, "$1개 모두 보기"],
  [/^Add all (\d+) to cart$/, "$1개 모두 장바구니에 담기"],
  [/^Ships in 1–2 business days\. Order today and it arrives <strong>about (.+)<\/strong> in the US\.$/, function (_, d) { return "영업일 1–2일 안에 발송. 오늘 주문하면 미국 내 <strong>" + date(d) + "쯤</strong> 도착해요."; }],
  [/^\$([\d.,]+) each$/, "개당 $$$1"],
  [/^Buy now · \$([\d.,]+)$/, "바로 구매 · $$$1"],
  [/^Digital file · (.+) · sent to your email · no magnet$/, function (_, t) { return "디지털 파일 · " + tr(t) + " · 이메일로 발송 · 자석 없음"; }],
  [/^Service (\d)$/, "서비스 $1"],
  [/^Line (\d+)$/, "$1번 줄"],
  [/^Line (\d+), right side$/, "$1번 줄, 오른쪽"],
  [/^(\d+) ready-made designs for your (business|wedding|graduation|party)\. Tap one to change the colors and the words, add your logo and see it right away\.$/, function (_, n, w) { return FOR[w] + "용 기성 디자인 " + n + "개. 하나를 눌러 색과 문구를 바꾸고 로고를 넣으면 바로 볼 수 있어요."; }],
  [/^Pack size for (.+)$/, function (_, c) { return tr(c) + " 팩 크기"; }],
  [/^(.+?) <small>([\d,]+\+?)<\/small>$/, function (_, c, k) { return (c === "All" ? "전체" : tr(c)) + " <small>" + k + "</small>"; }],
  [/^(.+) · (\d+) countries · (\d+) designs$/, function (_, a, k, d) { return tr(a) + " · " + k + "개 나라 · 디자인 " + d + "개"; }],
  [/^(.+) · (\d+) designs$/, function (_, a, k) { return tr(a) + " · 디자인 " + k + "개"; }],
  // design pages and lists
  [/^See (.+) larger$/, "크게 보기: $1"],
  [/^Favorite: (.+)$/, "찜하기: $1"],
  [/^Remove from favorites: (.+)$/, "찜 해제: $1"],
  [/^(.+) fridge magnet$/, "$1 냉장고 자석"],
  [/^(.+) magnet · Little Hive House$/, "$1 자석 · Little Hive House"],
  [/^(.+) magnets · Little Hive House$/, function (_, c) { return col(c) + " 자석 · Little Hive House"; }],
  [/^(.+) · Little Hive House$/, function (_, c) { var x = COL[c] || (window.LHH_I18N && LHH_I18N.t(c)) || c; return x !== c || known(c) ? x + " · Little Hive House" : null; }],
  [/^All (.{1,40}) designs$/, function (_, c) { return known(c) ? col(c) + " 디자인 전체" : null; }],
  [/^More from (.{1,40})$/, function (_, c) { return known(c) ? col(c) + " 더 보기" : null; }],
  [/^(.{1,40}) on the fridge$/, function (_, c) { return known(c) ? "냉장고 위의 " + col(c) : null; }],
  [/^(.+) on the fridge · (\d+) designs$/, function (_, c, k) { return known(c) ? "냉장고 위의 " + col(c) + " · 디자인 " + k + "개" : null; }],
  [/^(\d[\d,]*) designs?$/, "디자인 $1개"],
  [/^(\d[\d,]*)\+ designs$/, "디자인 $1개 이상"],
  [/^(\d+) magnets?$/, "자석 $1개"],
  [/^(\d+) items?$/, "상품 $1개"],
  [/^(\d+) photos?$/, "사진 $1장"],
  [/^(\d+) collections$/, "컬렉션 $1개"],
  [/^See all (\d+) designs$/, "디자인 $1개 모두 보기"],
  [/^See (\d+) more designs?$/, "디자인 $1개 더 보기"],
  [/^Show (\d+) more$/, "$1개 더 보기"],
  [/^Big order, (\d+) magnets \((\d+)% off\)$/, function (_, k, p) { return "대량 주문, 자석 " + k + "개 (" + off(p) + ")"; }],
  [/^Add \$([\d.]+) more for free US shipping\.$/, "$$$1만 더 담으면 미국 내 무료 배송이에요."],
  [/^Order today, it arrives <strong>about (.+)<\/strong> in the US · <a>Shipping details<\/a>$/, function (_, d) { return "오늘 주문하면 미국 내 <strong>" + date(d) + "쯤</strong> 도착 · <a>배송 안내</a>"; }],
  [/^about (.+\d.*)$/, function (_, d) { return date(d) + "쯤"; }],
  [/^Updated (.+)$/, function (_, d) { return "업데이트: " + date(d); }],
  [/^Ordered (.+)$/, function (_, d) { return "주문일: " + date(d); }],
  [/^Delivered (.+)$/, function (_, d) { return "배송 완료: " + date(d); }],
  [/^Shipped (.+)$/, function (_, d) { return "발송일: " + date(d); }],
  [/^Order (LHH-\d+)$/, "주문 $1"],
  [/^Qty (\d+)$/, "수량 $1"],
  [/^Magnet (\d+)$/, "자석 $1"],
  [/^Photo (\d+)$/, "사진 $1"],
  [/^Step (\d+) of (\d+)$/, "$2단계 중 $1단계"],
  [/^(\d+)% off everything, or buy (\d+) designs, get (\d+) free(.*)$/, function (_, p, b, g, rest) { return "전 상품 " + off(p) + ", 또는 디자인 " + b + "개 사면 " + g + "개 무료" + saleEnd(rest); }],
  [/^today only: (\d+)% off everything( \+ free shipping)?(.*)$/, function (_, p, f, rest) { return "오늘 하루만: 전 상품 " + off(p) + (f ? " + 무료 배송" : "") + saleEnd(rest); }],
  [/^(Black Friday|Cyber Monday), (\d+)% off$/, function (_, n, p) { return ev(n) + ", " + off(p); }],
  [/^(Black Friday|Cyber Monday), (\d+) designs? free$/, function (_, n, k) { return ev(n) + ", 디자인 " + k + "개 무료"; }],
  [/^(Black Friday|Cyber Monday): add (\d+) more designs? and (\d+) of them (?:is|are) free\.$/, function (_, n, a, f) { return ev(n) + ": 디자인 " + a + "개를 더 담으면 그중 " + f + "개가 무료예요."; }],
  [/^(Black Friday|Cyber Monday): free shipping on every order today\.$/, function (_, n) { return ev(n) + ": 오늘은 모든 주문 무료 배송이에요."; }],
  [/^(\d+) of (\d+)$/, "$1 / $2"],
  /* photo swap on the order pages (assets/orders.js, functions/photoswap.js) */
  [/^Change photo (\d+)$/, "$1번 사진 바꾸기"],
  [/^Photo (\d+) was changed for a new one\.$/, "$1번 사진을 새 사진으로 바꿨어요."],
  [/^Photo (\d+) \(pack (\d+)\) was changed for a new one\.$/, "$1번 사진($2번 묶음)을 새 사진으로 바꿨어요."],
  [/^Pack (\d+)$/, "$1번 묶음"],
];
/* the end of the sale bar's text: " · through Cyber Monday" or " · ends in 5h 12m" */
function saleEnd(rest) {
  if (!rest) return "";
  if (/through Cyber Monday/.test(rest)) return " · 사이버 먼데이까지";
  var m = /ends in (.*)$/.exec(rest);
  return m ? " · " + m[1].replace(/(\d+)d\b/, "$1일").replace(/(\d+)h\b/, "$1시간").replace(/(\d+)m\b/, "$1분") + " 남음" : rest;
}
