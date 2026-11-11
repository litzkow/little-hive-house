/* Patterns: English text with a number, a date or a name in it. Each is [regex, Portuguese] where the Portuguese is a
   replacement string ($1…) or a function of the match. Checked in order, after the exact dictionary. */
var COL = {
  "USA Places": "Lugares dos EUA", "World Places": "Lugares pelo Mundo", "Ink Cities": "Cidades a Nanquim",
  "City Sketches": "Cidades em Traço", "Fall": "Outono", "Halloween": "Halloween", "Horror Classics": "Clássicos do Terror",
  "Furry Friends": "Amigos Peludos", "Kitchen Words": "Frases de Cozinha", "Americana": "Americana", "México": "México",
  "Ireland": "Irlanda", "Italia": "Itália", "Puerto Rico": "Porto Rico", "Pilipinas": "Filipinas", "India": "Índia",
  "Korea": "Coreia", "Japan": "Japão", "Brasil": "Brasil", "Greece": "Grécia", "France": "França",
  "Great Masters": "Grandes Mestres", "Mythology": "Mitologia", "Home Notes": "Recadinhos de Casa", "Bee Kind": "Bee Kind",
  "Night Sky": "Céu Noturno", "Birth Flowers": "Flores do Mês", "Storybook Classics": "Clássicos da Literatura",
  "Fairy Tales & Myths": "Contos de Fadas e Mitos", "Wise Words": "Palavras Sábias", "Holidays & Dates": "Datas Comemorativas",
  "Bumper Stickers": "Adesivos de Para-choque", "Christmas": "Natal", "Summer": "Verão", "Heritage": "Raízes",
  "Photo magnets": "Ímãs com foto", "Custom photo magnets": "Ímãs com foto personalizados"
};
var FRAME = { "Arch": "Arco", "Art deco": "Art déco", "Autumn": "Outono", "Birthday": "Aniversário", "Botanical": "Botânica",
  "Circle": "Círculo", "Classic": "Clássica", "Crisp white mat": "Paspatur branco", "Date stamp": "Carimbo de data",
  "Eucalyptus wreath": "Guirlanda de eucalipto", "Film frame": "Filme fotográfico", "Full photo": "Foto inteira",
  "Gallery mat": "Paspatur de galeria", "Gallery with caption": "Galeria com legenda", "Gold line": "Fio dourado",
  "Graduation": "Formatura", "Handwritten": "Escrita à mão", "Holiday": "Festas", "Honeycomb": "Favo de mel",
  "Instant print": "Foto instantânea", "Love": "Amor", "Modern": "Moderna", "Name band": "Faixa com nome",
  "Postage stamp": "Selo postal", "Postcard": "Cartão-postal", "Rounded modern": "Moderna arredondada",
  "Scalloped lace": "Renda", "Script": "Letra cursiva", "Sweet dreams": "Bons sonhos", "Team": "Time",
  "Thin white border": "Borda branca fina", "Tropical leaves": "Folhas tropicais", "Vintage ornate gold": "Dourada vintage",
  "Watercolour peonies": "Peônias em aquarela", "Wedding": "Casamento", "Winter": "Inverno", "No border": "Sem borda" };
function fr(s) { return FRAME[s] || s; }
function col(s) { return COL[s] || s; }
/** only for the shop's own collection names: anything else is left to the dictionary */
function known(s) { return Object.prototype.hasOwnProperty.call(COL, s) || /^(Americana|México|Brasil|Halloween|Bee Kind)$/.test(s); }
var MON = { Jan: "jan", Feb: "fev", Mar: "mar", Apr: "abr", May: "mai", Jun: "jun", Jul: "jul", Aug: "ago", Sep: "set", Oct: "out", Nov: "nov", Dec: "dez",
  January: "janeiro", February: "fevereiro", March: "março", April: "abril", June: "junho", July: "julho", August: "agosto",
  September: "setembro", October: "outubro", November: "novembro", December: "dezembro" };
var DAY = { Mon: "seg", Tue: "ter", Wed: "qua", Thu: "qui", Fri: "sex", Sat: "sáb", Sun: "dom",
  Monday: "segunda", Tuesday: "terça", Wednesday: "quarta", Thursday: "quinta", Friday: "sexta", Saturday: "sábado", Sunday: "domingo" };
var M = "(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)";
/* "Nov 17–20" → "17–20 de nov"; "Nov 28–Dec 2" → "28 de nov–2 de dez"; "November 3, 2026" → "3 de novembro de 2026";
   "Tue, Nov 17" → "ter, 17 de nov" */
function date(s) {
  return s
    .replace(/\b(Mon|Tue|Wed|Thu|Fri|Sat|Sun|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b/g, function (d) { return DAY[d]; })
    .replace(new RegExp(M + " (\\d{1,2}), (\\d{4})", "g"), function (_, m, d, y) { return d + " de " + MON[m] + " de " + y; })
    .replace(new RegExp(M + " (\\d{1,2})[–-](\\d{1,2})\\b", "g"), function (_, m, a, b) { return a + "–" + b + " de " + MON[m]; })
    .replace(new RegExp(M + " (\\d{1,2})[–-]" + M + " (\\d{1,2})", "g"), function (_, m1, a, m2, b) { return a + " de " + MON[m1] + "–" + b + " de " + MON[m2]; })
    .replace(new RegExp(M + " (\\d{1,2})\\b", "g"), function (_, m, d) { return d + " de " + MON[m]; })
    .replace(new RegExp(M + " (\\d{4})", "g"), function (_, m, y) { return MON[m] + " de " + y; });
}
function n(x) { return x === "1" ? 1 : 2; }
function tr(s) { return COL[s] || (window.LHH_I18N ? window.LHH_I18N.t(s) : s); }
var PATTERNS = [
  [/^Photo ([\d, ]+) didn't finish uploading\. Please try again\.$/, "A foto $1 não terminou de enviar. Tente de novo."],
  [/^Photo (\d+) didn't upload correctly\. Please remove it and add it again\.$/, "A foto $1 não foi enviada direito. Tire e adicione de novo."],
  [/^Photo (\d+) is too big or empty\.$/, "A foto $1 está grande demais ou vazia."],
  [/^Cart <span>(\d+)<\/span>$/, "Carrinho <span>$1</span>"],
  [/^Order today and it arrives about (.+) in the US\. <a>Shipping details<\/a>$/, function (_, d) { return "Pedindo hoje, chega por volta de " + date(d) + " nos EUA. <a>Detalhes do frete</a>"; }],
  // cart, photo builder, checkout (assets/site.js, custom.js, checkout.js)
  [/^One less (.+)$/, "Um a menos: $1"],
  [/^One more (.+)$/, "Mais um: $1"],
  [/^Add (\d+) more magnets for (\d+)% off your whole order\.$/, "Adicione mais $1 ímãs e ganhe $2% de desconto no pedido todo."],
  [/^Order today and it arrives about (.+) in the US\.$/, function (_, d) { return "Pedindo hoje, chega por volta de " + date(d) + " nos EUA."; }],
  [/^Custom photo magnets$/, "Ímãs com foto personalizados"],
  [/^(.+) added to cart$/, function (_, x) { return tr(x) + " no carrinho"; }],
  [/^Your (\d+) magnets are in the cart$/, "Seus $1 ímãs estão no carrinho"],
  [/^(\d+) magnets · we plan the design with you by email after checkout$/, "$1 ímãs · planejamos o modelo com você por e-mail depois do pagamento"],
  [/^(\d+) magnets · (\d+) photos? · (\d+) frames$/, function (_, a, b, c) { return a + " ímãs · " + b + (b === "1" ? " foto" : " fotos") + " · " + c + " molduras"; }],
  [/^(\d+) magnets · (\d+) photos? · (.+)$/, function (_, a, b, f) { return a + " ímãs · " + b + (b === "1" ? " foto" : " fotos") + " · " + fr(f); }],
  [/^2 × 2 in · (.+)$/, function (_, c) { return "2 × 2 pol. · " + col(c); }],
  [/^(.+) magnet$/, "Ímã $1"],
  [/^Remove photo (\d+)$/, "Tirar a foto $1"],
  [/^1 photo is too small and may print blurry\. (.+)$/, "1 foto está pequena demais e pode sair borrada. Para ímãs nítidos, use a foto original da galeria do celular, não um print de tela nem uma foto salva de app de conversa."],
  [/^(\d+) photos are too small and may print blurry\. (.+)$/, "$1 fotos estão pequenas demais e podem sair borradas. Para ímãs nítidos, use a foto original da galeria do celular, não um print de tela nem uma foto salva de app de conversa."],
  [/^(\d+) photos added\. This pack holds (\d+), so remove (\d+) or pick a bigger pack\.$/, "$1 fotos adicionadas. Este pacote tem $2, então tire $3 ou escolha um pacote maior."],
  [/^(\d+) of (\d+) photos added\. We will repeat your favorites to fill the pack, or tell us in the notes\.$/, "$1 de $2 fotos adicionadas. Vamos repetir as suas favoritas para completar o pacote, ou diga nos recados como prefere."],
  [/^Frame for photo (\d+)$/, "Moldura da foto $1"],
  [/^Photo (\d+): (.+) frame(, caption (.+?))?(, low resolution)?\. Choose frame$/, function (_, k, f, c1, c, low) { return "Foto " + k + ": moldura " + fr(f) + (c ? ", legenda " + c : "") + (low ? ", baixa resolução" : "") + ". Escolher moldura"; }],
  [/^Preview of photo (\d+) with the (.+?) frame( and the caption (.+))?$/, function (_, k, f, c1, c) { return "Prévia da foto " + k + " com a moldura " + fr(f) + (c ? " e a legenda " + c : ""); }],
  [/^Apply this frame to all (\d+) photos$/, "Usar esta moldura nas $1 fotos"],
  [/^(.+) is now on all (\d+) photos\.$/, function (_, f, k) { return "A moldura " + fr(f) + " agora está nas " + k + " fotos."; }],
  [/^Caption added to all (\d+) photos\. It prints on photos with a caption frame\.$/, "Legenda colocada nas $1 fotos. Ela é impressa nas fotos com moldura de legenda."],
  [/^All (\d+) photos uploaded$/, "As $1 fotos foram enviadas"],
  [/^Uploading your photo · (\d+)%$/, "Enviando a sua foto · $1%"],
  [/^Uploading your (\d+) photos · (\d+)%$/, "Enviando as suas $1 fotos · $2%"],
  // orders, account, returns (assets/orders.js, account.js, return.js)
  [/^Tracking history \((\d+) scans?\)$/, function (_, k) { return "Histórico do rastreio (" + k + (k === "1" ? " registro)" : " registros)"); }],
  [/^(.+) has your package out for delivery\. Keep an eye on the porch!$/, "O $1 saiu para entregar o seu pacote. Fique de olho na porta!"],
  [/^Your package is with (.+?)\.( It shipped on (.+?)\.)?( We’ll email you when it’s out for delivery and when it arrives\.)?$/, function (_, c, s1, d, tail) { return "O seu pacote está com o " + c + "." + (d ? " Ele foi enviado em " + d + "." : "") + (tail ? " Avisamos por e-mail quando sair para entrega e quando chegar." : ""); }],
  [/^Delivered on (.+?)\. We hope you love them!$/, "Entregue em $1. Esperamos que você ame!"],
  [/^We hope you love them!$/, "Esperamos que você ame!"],
  [/^We refunded (\$[\d.,]+)\. Refunds take 5 to 10 business days to show on your statement\.$/, "Devolvemos $1. O reembolso leva de 5 a 10 dias úteis para aparecer na sua fatura."],
  [/^Rating for (.+)$/, "Nota para $1"],
  [/^Thank you, (.+)!$/, "Obrigado, $1!"],
  [/^Order (LHH-\d+) is confirmed\. We emailed you a receipt, so keep it handy for tracking\.$/, "O pedido $1 está confirmado. Mandamos o recibo por e-mail, guarde para acompanhar o rastreio."],
  [/^Check your inbox\. If there’s an account for (.+?), we just sent a link to choose a new password\.( It can take a minute, and sometimes lands in spam\.)?$/, function (_, e, tail) { return "Confira a sua caixa de entrada. Se existir uma conta para " + e + ", acabamos de mandar um link para escolher uma senha nova." + (tail ? " Pode levar um minuto, e às vezes cai no spam." : ""); }],
  [/^See all (\d+) orders$/, "Ver os $1 pedidos"],
  [/^We found (\d+) earlier orders with your email and added them to your account\.$/, "Encontramos $1 pedidos anteriores com o seu e-mail e colocamos na sua conta."],
  [/^Signed in as (.+)\.$/, "Conta aberta como $1."],
  [/^We emailed (.+) a link to choose a new password\.$/, "Mandamos para $1 um link para escolher uma senha nova."],
  [/^Your account and orders \(signed in as (.+)\)$/, "Sua conta e seus pedidos (conta aberta como $1)"],
  [/^(.+) saved to your favorites$/, function (_, x) { return tr(x) + " salvo nos favoritos"; }],
  [/^(.+) removed from favorites$/, function (_, x) { return tr(x) + " tirado dos favoritos"; }],
  [/^Refunded (\$[\d.,]+) on (.+)\.$/, "Devolvemos $1 em $2."],
  [/^(\$[\d.,]+) back to your card on (.+)$/, "$1 de volta no seu cartão em $2"],
  [/^Your refund: (\$[\d.,]+) \((\$[\d.,]+) for the magnets − (\$[\d.,]+) return shipping\)\.$/, "Seu reembolso: $1 ($2 dos ímãs − $3 do frete de volta)."],
  [/^(\d+) magnets · (\$[\d.,]+) each$/, "$1 ímãs · $2 cada"],
  [/^(\$[\d.,]+) each$/, "$1 cada"],
  [/^This account is turned off\. Email (.+) and we’ll sort it out\.$/, "Esta conta está desativada. Mande um e-mail para $1 que a gente resolve."],
  [/^We couldn’t save one of your photos\. (.+?) or email (.+?)\.?$/, "Não conseguimos salvar uma das suas fotos. Use fotos comuns com menos de 25 MB (JPG, PNG, HEIC ou WebP) e tente de novo, ou mande um e-mail para $2."],
  [/^We can’t take photo uploads right now\. Please email (.+)$/, "Não estamos recebendo fotos agora. Mande um e-mail para $1"],
  [/^Something went wrong on our side\. Please try again, or email (.+)$/, "Algo deu errado do nosso lado. Tente de novo ou mande um e-mail para $1"],
  [/^This link has expired or is incomplete\. Email (.+) and we’ll remove you by hand\.$/, "Este link expirou ou está incompleto. Mande um e-mail para $1 que a gente tira você da lista na mão."],
  [/^Your email app should open now\. If it doesn't, write to us at (.+)$/, "O seu app de e-mail deve abrir agora. Se não abrir, escreva para $1"],
  [/^Ordering today\? Most US orders arrive <strong>about (.+)<\/strong>\.$/, function (_, d) { return "Pedindo hoje? A maioria dos pedidos nos EUA chega <strong>por volta de " + date(d) + "</strong>."; }],
  [/^(\d+) of (\d+) photos added$/, "$1 de $2 fotos adicionadas"],
  [/^Photo (\d+) of (\d+)$/, "Foto $1 de $2"],
  [/^<span>(\d+\/\d+)<\/span> · Optional, leave empty for none$/, "<span>$1</span> · Opcional, deixe em branco se não quiser"],
  [/^(\d+) designs · \$5 each$/, "$1 modelos · $$5 cada"],
  [/^(\d+) countries · (\d+) designs · \$5 each$/, "$1 países · $2 modelos · $$5 cada"],
  [/^See all (\d+)$/, "Ver todos os $1"],
  [/^Add all (\d+) to cart$/, "Adicionar os $1 ao carrinho"],
  [/^Ships in 1–2 business days\. Order today and it arrives <strong>about (.+)<\/strong> in the US\.$/, function (_, d) { return "Enviamos em 1 a 2 dias úteis. Pedindo hoje, chega <strong>por volta de " + date(d) + "</strong> nos EUA."; }],
  [/^\$([\d.,]+) each$/, "$$$1 cada"],
  [/^Buy now · \$([\d.,]+)$/, "Comprar agora · $$$1"],
  [/^Pack size for (.+)$/, function (_, c) { return "Tamanho do pacote para " + tr(c); }],
  [/^(.+?) <small>([\d,]+\+?)<\/small>$/, function (_, c, k) { return (c === "All" ? "Todos" : tr(c)) + " <small>" + k + "</small>"; }],
  [/^(.+) · (\d+) countries · (\d+) designs$/, function (_, a, k, d) { return tr(a) + " · " + k + " países · " + d + " modelos"; }],
  [/^(.+) · (\d+) designs$/, function (_, a, k) { return tr(a) + " · " + k + " modelos"; }],
  // design pages and lists
  [/^See (.+) larger$/, "Ver $1 maior"],
  [/^Favorite: (.+)$/, "Favoritar: $1"],
  [/^Remove from favorites: (.+)$/, "Tirar dos favoritos: $1"],
  [/^(.+) fridge magnet$/, "Ímã de geladeira $1"],
  [/^(.+) magnet · Little Hive House$/, "Ímã $1 · Little Hive House"],
  [/^(.+) magnets · Little Hive House$/, function (_, c) { return "Ímãs " + col(c) + " · Little Hive House"; }],
  [/^(.+) · Little Hive House$/, function (_, c) { return (COL[c] || (window.LHH_I18N && LHH_I18N.t(c)) || c) + " · Little Hive House"; }],
  [/^All (.{1,40}) designs$/, function (_, c) { return known(c) ? "Todos os modelos de " + col(c) : null; }],
  [/^More from (.{1,40})$/, function (_, c) { return known(c) ? "Mais de " + col(c) : null; }],
  [/^(.{1,40}) on the fridge$/, function (_, c) { return known(c) ? col(c) + " na geladeira" : null; }],
  [/^(.+) on the fridge · (\d+) designs$/, function (_, c, k) { return known(c) ? col(c) + " na geladeira · " + k + " modelos" : null; }],
  [/^(\d[\d,]*) designs?$/, function (_, k) { return k + (k === "1" ? " modelo" : " modelos"); }],
  [/^(\d[\d,]*)\+ designs$/, "$1+ modelos"],
  [/^(\d+) magnets?$/, function (_, k) { return k + (k === "1" ? " ímã" : " ímãs"); }],
  [/^(\d+) items?$/, function (_, k) { return k + (k === "1" ? " item" : " itens"); }],
  [/^(\d+) photos?$/, function (_, k) { return k + (k === "1" ? " foto" : " fotos"); }],
  [/^(\d+) collections$/, "$1 coleções"],
  [/^See all (\d+) designs$/, "Ver os $1 modelos"],
  [/^See (\d+) more designs?$/, function (_, k) { return "Ver mais " + k + (k === "1" ? " modelo" : " modelos"); }],
  [/^Show (\d+) more$/, "Mostrar mais $1"],
  [/^Big order, (\d+) magnets \((\d+)% off\)$/, "Pedido grande, $1 ímãs ($2% de desconto)"],
  [/^Add \$([\d.]+) more for free US shipping\.$/, "Faltam $$$1 para o frete grátis nos EUA."],
  [/^Order today, it arrives <strong>about (.+)<\/strong> in the US · <a>Shipping details<\/a>$/, function (_, d) { return "Pedindo hoje, chega <strong>por volta de " + date(d) + "</strong> nos EUA · <a>Detalhes do frete</a>"; }],
  [/^about (.+\d.*)$/, function (_, d) { return "por volta de " + date(d); }],
  [/^Updated (.+)$/, function (_, d) { return "Atualizado em " + date(d); }],
  [/^Ordered (.+)$/, function (_, d) { return "Pedido em " + date(d); }],
  [/^Delivered (.+)$/, function (_, d) { return "Entregue em " + date(d); }],
  [/^Shipped (.+)$/, function (_, d) { return "Enviado em " + date(d); }],
  [/^Order (LHH-\d+)$/, "Pedido $1"],
  [/^Qty (\d+)$/, "Qtd. $1"],
  [/^Magnet (\d+)$/, "Ímã $1"],
  [/^Photo (\d+)$/, "Foto $1"],
  [/^Step (\d+) of (\d+)$/, "Passo $1 de $2"],
  [/^(\d+) of (\d+)$/, "$1 de $2"]
];
