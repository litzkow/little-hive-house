/* Patterns: English text with a number, a date or a name in it. Each is [regex, Spanish] where the Spanish is a
   replacement string ($1…) or a function of the match. Checked in order, after the exact dictionary.
   Neutral Latin American Spanish, "tú". Prices keep the US format ($5.49, 1,200). */
var COL = {
  "USA Places": "Lugares de EE. UU.", "World Places": "Lugares del Mundo", "Ink Cities": "Ciudades en Tinta",
  "City Sketches": "Ciudades en Trazo", "Fall": "Otoño", "Halloween": "Halloween", "Horror Classics": "Clásicos del Terror",
  "Furry Friends": "Amigos Peludos", "Kitchen Words": "Frases de Cocina", "Americana": "Americana", "México": "México",
  "Ireland": "Irlanda", "Italia": "Italia", "Puerto Rico": "Puerto Rico", "Pilipinas": "Filipinas", "India": "India",
  "Korea": "Corea", "Japan": "Japón", "Brasil": "Brasil", "Greece": "Grecia", "France": "Francia",
  "Great Masters": "Grandes Maestros", "Mythology": "Mitología", "Home Notes": "Notitas de Casa", "Bee Kind": "Bee Kind",
  "Night Sky": "Cielo Nocturno", "Birth Flowers": "Flores del Mes", "Storybook Classics": "Clásicos de la Literatura",
  "Fairy Tales & Myths": "Cuentos de Hadas y Mitos", "Wise Words": "Palabras Sabias", "Holidays & Dates": "Fechas Especiales",
  "Bumper Stickers": "Calcomanías de Defensa", "Christmas": "Navidad", "Summer": "Verano", "Heritage": "Raíces",
  "Photo magnets": "Imanes con foto", "Custom photo magnets": "Imanes con foto personalizados"
};
var FRAME = { "Arch": "Arco", "Art deco": "Art déco", "Autumn": "Otoño", "Birthday": "Cumpleaños", "Botanical": "Botánico",
  "Circle": "Círculo", "Classic": "Clásico", "Crisp white mat": "Paspartú blanco", "Date stamp": "Sello de fecha",
  "Eucalyptus wreath": "Corona de eucalipto", "Film frame": "Película fotográfica", "Full photo": "Foto completa",
  "Gallery mat": "Paspartú de galería", "Gallery with caption": "Galería con texto", "Gold line": "Línea dorada",
  "Graduation": "Graduación", "Handwritten": "Escrito a mano", "Holiday": "Fiestas", "Honeycomb": "Panal",
  "Instant print": "Foto instantánea", "Love": "Amor", "Modern": "Moderno", "Name band": "Banda con nombre",
  "Postage stamp": "Estampilla", "Postcard": "Postal", "Rounded modern": "Moderno redondeado",
  "Scalloped lace": "Encaje", "Script": "Letra cursiva", "Sweet dreams": "Dulces sueños", "Team": "Equipo",
  "Thin white border": "Borde blanco delgado", "Tropical leaves": "Hojas tropicales", "Vintage ornate gold": "Dorado vintage",
  "Watercolour peonies": "Peonías en acuarela", "Wedding": "Boda", "Winter": "Invierno", "No border": "Sin borde" };
function fr(s) { return FRAME[s] || s; }
function col(s) { return COL[s] || s; }
/** only for the shop's own collection names: anything else is left to the dictionary */
function known(s) { return Object.prototype.hasOwnProperty.call(COL, s) || /^(Americana|México|Brasil|Halloween|Bee Kind)$/.test(s); }
var MON = { Jan: "ene", Feb: "feb", Mar: "mar", Apr: "abr", May: "may", Jun: "jun", Jul: "jul", Aug: "ago", Sep: "sep", Oct: "oct", Nov: "nov", Dec: "dic",
  January: "enero", February: "febrero", March: "marzo", April: "abril", June: "junio", July: "julio", August: "agosto",
  September: "septiembre", October: "octubre", November: "noviembre", December: "diciembre" };
var DAY = { Mon: "lun", Tue: "mar", Wed: "mié", Thu: "jue", Fri: "vie", Sat: "sáb", Sun: "dom",
  Monday: "lunes", Tuesday: "martes", Wednesday: "miércoles", Thursday: "jueves", Friday: "viernes", Saturday: "sábado", Sunday: "domingo" };
var M = "(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)";
/* "Nov 17–20" → "17–20 de nov"; "Nov 28–Dec 2" → "28 de nov–2 de dic"; "November 3, 2026" → "3 de noviembre de 2026";
   "Tue, Nov 17" → "mar, 17 de nov" */
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
function pl(k, one, many) { return k + " " + (k === "1" ? one : many); }
var PATTERNS = [
  [/^([\d,]+) ready-made designs for (your business|your wedding|your graduation|your party or event|your home)\. Tap one to change the colors and the words, add your (logo|photo) and see it right away\.$/, function (_, n, w, x) { return n + " diseños listos para " + { "your business": "tu negocio", "your wedding": "tu boda", "your graduation": "tu graduación", "your party or event": "tu fiesta o evento", "your home": "tu casa" }[w] + ". Toca uno para cambiar los colores y los textos, poner " + (x === "logo" ? "tu logo" : "tu foto") + " y verlo al instante."; }],
  [/^(\d+) kinds · ([\d,]+) designs$/, "$1 tipos · $2 diseños"],
  [/^(\d+) (magnets?) · \$([\d.]+)(?: \(\$([\d.]+) each\))?$/, function (_, n, m, p, e) { return pl(n, "imán", "imanes") + " · $" + p + (e ? " ($" + e + " c/u)" : ""); }],
  [/^From \$(\d+) a magnet$/, "Desde $$$1 por imán"],
  [/^\$([\d.]+) · sent to your email$/, "$$$1 · llega a tu correo"],
  [/^Hundreds of designs to make yours: change the words and colors, add a photo\. From \$(\d+)\.$/, "Cientos de diseños para hacer tuyos: cambia los textos y los colores, pon una foto. Desde $$$1."],
  [/^Every magnet is made just for you\. Want only the design\? \$([\d.]+) for the file, free with any magnet\.$/, "Cada imán se hace solo para ti. ¿Solo quieres el diseño? $$$1 por el archivo, gratis con cualquier imán."],
  [/^Yes\. Tap the design, make it yours and choose “Only want the file”: \$([\d.]+), sent to your email right away, no magnet\. It is free with any magnet order\.$/, "Sí. Toca el diseño, personalízalo y elige “Solo quiero el archivo”: $$$1, llega a tu correo al instante, sin imán. Es gratis con cualquier pedido de imanes."],
  [/^([^·<]{2,40}) · ([^·<]{2,40})$/, function (_, a, b) { var x = tr(a), y = tr(b); return x !== a || y !== b ? x + " · " + y : null; }],
  [/^1 magnet$/, "1 imán"],
  [/^(\d+) photo designs with names, dates and captions$/, "$1 diseños con foto con nombres, fechas y frases"],
  [/^\$(\d+) · \$([\d.]+) each$/, "$$$1 · $$$2 c/u"],
  [/^Photo ([\d, ]+) didn't finish uploading\. Please try again\.$/, "La foto $1 no terminó de subir. Inténtalo de nuevo."],
  [/^Photo (\d+) didn't upload correctly\. Please remove it and add it again\.$/, "La foto $1 no se subió bien. Quítala y agrégala otra vez."],
  [/^Photo (\d+) is too big or empty\.$/, "La foto $1 es demasiado grande o está vacía."],
  [/^Cart <span>(\d+)<\/span>$/, "Carrito <span>$1</span>"],
  [/^Order today and it arrives about (.+) in the US\. <a>Shipping details<\/a>$/, function (_, d) { return "Si pides hoy, llega alrededor del " + date(d) + " en EE. UU. <a>Detalles del envío</a>"; }],
  // cart, photo builder, checkout (assets/site.js, custom.js, checkout.js)
  [/^One less (.+)$/, "Uno menos: $1"],
  [/^One more (.+)$/, "Uno más: $1"],
  [/^Add (\d+) more magnets for (\d+)% off your whole order\.$/, "Agrega $1 imanes más y obtén $2% de descuento en todo el pedido."],
  [/^Order today and it arrives about (.+) in the US\.$/, function (_, d) { return "Si pides hoy, llega alrededor del " + date(d) + " en EE. UU."; }],
  [/^Custom photo magnets$/, "Imanes con foto personalizados"],
  [/^(.+) added to cart$/, function (_, x) { return tr(x) + " en el carrito"; }],
  [/^Your (\d+) magnets are in the cart$/, "Tus $1 imanes están en el carrito"],
  [/^(\d+) magnets · we plan the design with you by email after checkout$/, "$1 imanes · planeamos el diseño contigo por correo después del pago"],
  // bulk-order pages (business, weddings, graduation, parties): packs, the mailing service, the QR maker
  [/^(\d+) magnets · \$([\d.,]+) \(\$([\d.,]+) each\)$/, "$1 imanes · $$$2 ($$$3 c/u)"],
  [/^(\d+) addresses$/, "$1 direcciones"],
  [/^(\d+) addresses · we ask for your list after checkout$/, "$1 direcciones · te pedimos la lista después del pago"],
  [/^(\d+) magnets · style: (.+) · we plan the design with you by email after checkout$/, function (_, n, s) { return n + " imanes · estilo: " + tr(s) + " · planeamos el diseño contigo por correo después del pago"; }],
  [/^(\d+) QR magnets · (.+) · proof before we print$/, "$1 imanes con QR · $2 · prueba antes de imprimir"],
  [/^Mailed to your list, (\d+) addresses$/, "Enviado por correo a tu lista, $1 direcciones"],
  [/^Graduation & college, (\d+) magnets$/, "Graduación y universidad, $1 imanes"],
  [/^(\d+) magnets · (\d+) photos? · (\d+) frames$/, function (_, a, b, c) { return a + " imanes · " + pl(b, "foto", "fotos") + " · " + c + " marcos"; }],
  [/^(\d+) magnets · (\d+) photos? · (.+)$/, function (_, a, b, f) { return a + " imanes · " + pl(b, "foto", "fotos") + " · " + fr(f); }],
  [/^2 × 2 in · (.+)$/, function (_, c) { return "2 × 2 pulg. · " + col(c); }],
  [/^(.+) magnet$/, "Imán $1"],
  [/^Remove photo (\d+)$/, "Quitar la foto $1"],
  [/^1 photo is too small and may print blurry\. (.+)$/, "1 foto es demasiado pequeña y puede salir borrosa. Para imanes nítidos, usa la foto original de la galería de tu celular, no una captura de pantalla ni una foto guardada de una app de mensajes."],
  [/^(\d+) photos are too small and may print blurry\. (.+)$/, "$1 fotos son demasiado pequeñas y pueden salir borrosas. Para imanes nítidos, usa la foto original de la galería de tu celular, no una captura de pantalla ni una foto guardada de una app de mensajes."],
  [/^(\d+) photos added\. This pack holds (\d+), so remove (\d+) or pick a bigger pack\.$/, "Agregaste $1 fotos. Este paquete lleva $2, así que quita $3 o elige un paquete más grande."],
  [/^(\d+) of (\d+) photos added\. We will repeat your favorites to fill the pack, or tell us in the notes\.$/, "Agregaste $1 de $2 fotos. Repetiremos tus favoritas para completar el paquete, o dinos en las notas cómo lo prefieres."],
  [/^Frame for photo (\d+)$/, "Marco de la foto $1"],
  [/^Photo (\d+): (.+) frame(, caption (.+?))?(, low resolution)?\. Choose frame$/, function (_, k, f, c1, c, low) { return "Foto " + k + ": marco " + fr(f) + (c ? ", texto " + c : "") + (low ? ", baja resolución" : "") + ". Elegir marco"; }],
  [/^Preview of photo (\d+) with the (.+?) frame( and the caption (.+))?$/, function (_, k, f, c1, c) { return "Vista previa de la foto " + k + " con el marco " + fr(f) + (c ? " y el texto " + c : ""); }],
  [/^Apply this frame to all (\d+) photos$/, "Usar este marco en las $1 fotos"],
  [/^(.+) is now on all (\d+) photos\.$/, function (_, f, k) { return "El marco " + fr(f) + " ya está en las " + k + " fotos."; }],
  [/^Caption added to all (\d+) photos\. It prints on photos with a caption frame\.$/, "Texto agregado a las $1 fotos. Se imprime en las fotos con marco de texto."],
  [/^All (\d+) photos uploaded$/, "Se subieron las $1 fotos"],
  [/^Uploading your photo · (\d+)%$/, "Subiendo tu foto · $1%"],
  [/^Uploading your (\d+) photos · (\d+)%$/, "Subiendo tus $1 fotos · $2%"],
  // orders, account, returns (assets/orders.js, account.js, return.js)
  [/^Tracking history \((\d+) scans?\)$/, function (_, k) { return "Historial de rastreo (" + pl(k, "registro", "registros") + ")"; }],
  [/^(.+) has your package out for delivery\. Keep an eye on the porch!$/, "$1 ya salió a entregar tu paquete. ¡Pendiente de la puerta!"],
  [/^Your package is with (.+?)\.( It shipped on (.+?)\.)?( We’ll email you when it’s out for delivery and when it arrives\.)?$/, function (_, c, s1, d, tail) { return "Tu paquete está con " + c + "." + (d ? " Salió el " + d + "." : "") + (tail ? " Te avisamos por correo cuando salga a entrega y cuando llegue." : ""); }],
  [/^Delivered on (.+?)\. We hope you love them!$/, "Entregado el $1. ¡Esperamos que te encanten!"],
  [/^We hope you love them!$/, "¡Esperamos que te encanten!"],
  [/^We refunded (\$[\d.,]+)\. Refunds take 5 to 10 business days to show on your statement\.$/, "Te devolvimos $1. Los reembolsos tardan de 5 a 10 días hábiles en aparecer en tu estado de cuenta."],
  [/^Rating for (.+)$/, "Calificación para $1"],
  [/^Thank you, (.+)!$/, "¡Gracias, $1!"],
  [/^Order (LHH-\d+) is confirmed\. We emailed you a receipt, so keep it handy for tracking\.$/, "El pedido $1 está confirmado. Te mandamos el recibo por correo, guárdalo para el rastreo."],
  [/^Check your inbox\. If there’s an account for (.+?), we just sent a link to choose a new password\.( It can take a minute, and sometimes lands in spam\.)?$/, function (_, e, tail) { return "Revisa tu bandeja de entrada. Si hay una cuenta para " + e + ", acabamos de mandar un enlace para elegir una contraseña nueva." + (tail ? " Puede tardar un minuto, y a veces llega a spam." : ""); }],
  [/^See all (\d+) orders$/, "Ver los $1 pedidos"],
  [/^We found (\d+) earlier orders with your email and added them to your account\.$/, "Encontramos $1 pedidos anteriores con tu correo y los agregamos a tu cuenta."],
  [/^Signed in as (.+)\.$/, "Sesión iniciada como $1."],
  [/^We emailed (.+) a link to choose a new password\.$/, "Mandamos a $1 un enlace para elegir una contraseña nueva."],
  [/^Your account and orders \(signed in as (.+)\)$/, "Tu cuenta y tus pedidos (sesión iniciada como $1)"],
  [/^(.+) saved to your favorites$/, function (_, x) { return tr(x) + " guardado en favoritos"; }],
  [/^(.+) removed from favorites$/, function (_, x) { return tr(x) + " quitado de favoritos"; }],
  [/^Refunded (\$[\d.,]+) on (.+)\.$/, "Te devolvimos $1 el $2."],
  [/^(\$[\d.,]+) back to your card on (.+)$/, "$1 de vuelta a tu tarjeta el $2"],
  [/^Your refund: (\$[\d.,]+) \((\$[\d.,]+) for the magnets − (\$[\d.,]+) return shipping\)\.$/, "Tu reembolso: $1 ($2 de los imanes − $3 del envío de devolución)."],
  [/^(\d+) magnets · (\$[\d.,]+) each$/, "$1 imanes · $2 c/u"],
  [/^(\$[\d.,]+) each$/, "$1 c/u"],
  [/^This account is turned off\. Email (.+) and we’ll sort it out\.$/, "Esta cuenta está desactivada. Escribe a $1 y lo resolvemos."],
  [/^We couldn’t save one of your photos\. (.+?) or email (.+?)\.?$/, "No pudimos guardar una de tus fotos. Usa fotos normales de menos de 25 MB (JPG, PNG, HEIC o WebP) e inténtalo de nuevo, o escribe a $2."],
  [/^We can’t take photo uploads right now\. Please email (.+)$/, "No estamos recibiendo fotos ahora. Escribe a $1"],
  [/^Something went wrong on our side\. Please try again, or email (.+)$/, "Algo salió mal de nuestro lado. Inténtalo de nuevo o escribe a $1"],
  [/^This link has expired or is incomplete\. Email (.+) and we’ll remove you by hand\.$/, "Este enlace venció o está incompleto. Escribe a $1 y te quitamos de la lista a mano."],
  [/^Your email app should open now\. If it doesn't, write to us at (.+)$/, "Tu app de correo debería abrirse ahora. Si no se abre, escríbenos a $1"],
  [/^Ordering today\? Most US orders arrive <strong>about (.+)<\/strong>\.$/, function (_, d) { return "¿Pides hoy? La mayoría de los pedidos en EE. UU. llegan <strong>alrededor del " + date(d) + "</strong>."; }],
  [/^(\d+) photos? added, (\$[\d.,]+) each$/, function (_, k, v) { return (k === "1" ? "1 foto agregada" : k + " fotos agregadas") + ", " + v + " c/u"; }],
  [/^Add 1 to 3 photos, (\$[\d.,]+) each$/, "Agrega de 1 a 3 fotos, $1 c/u"],
  [/^Add 1 more photo and get the pack of 4 for (\$[\d.,]+)\.$/, "Agrega 1 foto más y llévate el paquete de 4 por $1."],
  [/^(\d+) photos: pack of (\d+) \+ (\d+) extra photos? \((\$[\d.,]+) each\)$/, function (_, n, s, k, r) { return n + " fotos: paquete de " + s + " + " + pl(k, "foto extra", "fotos extra") + " (" + r + " c/u)"; }],
  [/^Only want (\d+) magnets?\? Make just these for (\$[\d.,]+)$/, function (_, n, v) { return "¿Solo quieres " + pl(n, "imán", "imanes") + "? Haz solo estos por " + v; }],
  [/^Add (\d+) more photos? at no extra cost: they fit in your pack of (\d+)\.$/, function (_, k, p) { return "Agrega " + pl(k, "foto", "fotos") + " más sin costo extra: " + (k === "1" ? "cabe" : "caben") + " en tu paquete de " + p + "."; }],
  [/^Want more\? Add 1 more photo for (\$[\d.,]+), or 2 for (\$[\d.,]+)\.$/, "¿Quieres más? Agrega 1 foto más por $1, o 2 por $2."],
  [/^Same price, more room: we moved you to the pack of (\d+)\. Add (\d+) more photos? at no extra cost\.$/, function (_, p, k) { return "Mismo precio, más espacio: te pasamos al paquete de " + p + ". Agrega " + pl(k, "foto", "fotos") + " más sin costo extra."; }],
  [/^A photo order holds up to (\d+) photos, so (\d+) (?:was|were) not added\.$/, function (_, m, k) { return "Un pedido de fotos lleva hasta " + m + " fotos, así que " + k + (k === "1" ? " no se agregó." : " no se agregaron."); }],
  [/^(\d+) of (\d+) photos added$/, "$1 de $2 fotos agregadas"],
  [/^Photo (\d+) of (\d+)$/, "Foto $1 de $2"],
  [/^<span>(\d+\/\d+)<\/span> · Optional, leave empty for none$/, "<span>$1</span> · Opcional, déjalo vacío si no quieres"],
  [/^(\d+) designs · \$5 each$/, "$1 diseños · $$5 c/u"],
  [/^(\d+) countries · (\d+) designs · \$5 each$/, "$1 países · $2 diseños · $$5 c/u"],
  [/^See all (\d+)$/, "Ver los $1"],
  [/^Add all (\d+) to cart$/, "Agregar los $1 al carrito"],
  [/^Ships in 1–2 business days\. Order today and it arrives <strong>about (.+)<\/strong> in the US\.$/, function (_, d) { return "Se envía en 1 a 2 días hábiles. Si pides hoy, llega <strong>alrededor del " + date(d) + "</strong> en EE. UU."; }],
  [/^\$([\d.,]+) each$/, "$$$1 c/u"],
  [/^Buy now · \$([\d.,]+)$/, "Comprar ahora · $$$1"],
  [/^Digital file · (.+) · sent to your email · no magnet$/, function (_, t) { return "Archivo digital · " + tr(t) + " · llega a tu correo · sin imán"; }],
  [/^Service (\d)$/, "Servicio $1"],
  [/^Line (\d+)$/, "Línea $1"],
  [/^Line (\d+), right side$/, "Línea $1, lado derecho"],
  [/^(\d+) ready-made designs for your (business|wedding|graduation|party)\. Tap one to change the colors and the words, add your logo and see it right away\.$/, function (_, n, w) { return n + " diseños listos para " + { business: "tu negocio", wedding: "tu boda", graduation: "tu graduación", party: "tu fiesta" }[w] + ". Toca uno para cambiar los colores y los textos, poner tu logo y verlo al instante."; }],
  [/^Pack size for (.+)$/, function (_, c) { return "Tamaño del paquete para " + tr(c); }],
  [/^(.+?) <small>([\d,]+\+?)<\/small>$/, function (_, c, k) { return (c === "All" ? "Todos" : tr(c)) + " <small>" + k + "</small>"; }],
  [/^(.+) · (\d+) countries · (\d+) designs$/, function (_, a, k, d) { return tr(a) + " · " + k + " países · " + d + " diseños"; }],
  [/^(.+) · (\d+) designs$/, function (_, a, k) { return tr(a) + " · " + k + " diseños"; }],
  // design pages and lists
  [/^See (.+) larger$/, "Ver $1 más grande"],
  [/^Favorite: (.+)$/, "Agregar a favoritos: $1"],
  [/^Remove from favorites: (.+)$/, "Quitar de favoritos: $1"],
  [/^(.+) fridge magnet$/, "Imán para refri $1"],
  [/^(.+) magnet · Little Hive House$/, "Imán $1 · Little Hive House"],
  [/^(.+) magnets · Little Hive House$/, function (_, c) { return "Imanes " + col(c) + " · Little Hive House"; }],
  [/^(.+) · Little Hive House$/, function (_, c) { var x = COL[c] || (window.LHH_I18N && LHH_I18N.t(c)) || c; return x !== c || known(c) ? x + " · Little Hive House" : null; }],
  [/^All (.{1,40}) designs$/, function (_, c) { return known(c) ? "Todos los diseños de " + col(c) : null; }],
  [/^More from (.{1,40})$/, function (_, c) { return known(c) ? "Más de " + col(c) : null; }],
  [/^(.{1,40}) on the fridge$/, function (_, c) { return known(c) ? col(c) + " en el refri" : null; }],
  [/^(.+) on the fridge · (\d+) designs$/, function (_, c, k) { return known(c) ? col(c) + " en el refri · " + k + " diseños" : null; }],
  [/^(\d[\d,]*) designs?$/, function (_, k) { return pl(k, "diseño", "diseños"); }],
  [/^(\d[\d,]*)\+ designs$/, "$1+ diseños"],
  [/^(\d+) magnets?$/, function (_, k) { return pl(k, "imán", "imanes"); }],
  [/^(\d+) items?$/, function (_, k) { return pl(k, "artículo", "artículos"); }],
  [/^(\d+) photos?$/, function (_, k) { return pl(k, "foto", "fotos"); }],
  [/^(\d+) collections$/, "$1 colecciones"],
  [/^See all (\d+) designs$/, "Ver los $1 diseños"],
  [/^See (\d+) more designs?$/, function (_, k) { return "Ver " + pl(k, "diseño", "diseños") + " más"; }],
  [/^Show (\d+) more$/, "Mostrar $1 más"],
  [/^Big order, (\d+) magnets \((\d+)% off\)$/, "Pedido grande, $1 imanes ($2% de descuento)"],
  [/^Add \$([\d.]+) more for free US shipping\.$/, "Te faltan $$$1 para el envío gratis en EE. UU."],
  [/^Order today, it arrives <strong>about (.+)<\/strong> in the US · <a>Shipping details<\/a>$/, function (_, d) { return "Si pides hoy, llega <strong>alrededor del " + date(d) + "</strong> en EE. UU. · <a>Detalles del envío</a>"; }],
  [/^about (.+\d.*)$/, function (_, d) { return "alrededor del " + date(d); }],
  [/^Updated (.+)$/, function (_, d) { return "Actualizado el " + date(d); }],
  [/^Ordered (.+)$/, function (_, d) { return "Pedido el " + date(d); }],
  [/^Delivered (.+)$/, function (_, d) { return "Entregado el " + date(d); }],
  [/^Shipped (.+)$/, function (_, d) { return "Enviado el " + date(d); }],
  [/^Order (LHH-\d+)$/, "Pedido $1"],
  [/^Qty (\d+)$/, "Cant. $1"],
  [/^Magnet (\d+)$/, "Imán $1"],
  [/^Photo (\d+)$/, "Foto $1"],
  [/^Step (\d+) of (\d+)$/, "Paso $1 de $2"],
  [/^(\d+)% off everything, or buy (\d+) designs, get (\d+) free(.*)$/, function (_, p, b, g, rest) { return p + "% de descuento en todo, o compra " + b + " diseños y llévate " + g + " gratis" + saleEnd(rest); }],
  [/^today only: (\d+)% off everything( \+ free shipping)?(.*)$/, function (_, p, f, rest) { return "solo hoy: " + p + "% de descuento en todo" + (f ? " + envío gratis" : "") + saleEnd(rest); }],
  [/^(Black Friday|Cyber Monday), (\d+)% off$/, "$1, $2% de descuento"],
  [/^(Black Friday|Cyber Monday), (\d+) designs? free$/, function (_, n, k) { return n + ", " + pl(k, "diseño gratis", "diseños gratis"); }],
  [/^(Black Friday|Cyber Monday): add (\d+) more designs? and (\d+) of them (?:is|are) free\.$/, function (_, n, a, f) { return n + ": agrega " + pl(a, "diseño", "diseños") + " más y " + f + (f === "1" ? " te sale gratis." : " te salen gratis."); }],
  [/^(Black Friday|Cyber Monday): free shipping on every order today\.$/, "$1: envío gratis en todos los pedidos hoy."],
  [/^(\d+) of (\d+)$/, "$1 de $2"],
  /* photo swap on the order pages (assets/orders.js, functions/photoswap.js) */
  [/^Change photo (\d+)$/, "Cambiar la foto $1"],
  [/^Photo (\d+) was changed for a new one\.$/, "La foto $1 se cambió por una nueva."],
  [/^Photo (\d+) \(pack (\d+)\) was changed for a new one\.$/, "La foto $1 (paquete $2) se cambió por una nueva."],
  [/^Pack (\d+)$/, "Paquete $1"],
];
/* the end of the sale bar's text: " · through Cyber Monday" or " · ends in 5h 12m" */
function saleEnd(rest) {
  if (!rest) return "";
  if (/through Cyber Monday/.test(rest)) return " · hasta el Cyber Monday";
  var m = /ends in (.*)$/.exec(rest);
  return m ? " · termina en " + m[1] : rest;
}
