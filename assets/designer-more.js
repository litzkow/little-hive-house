/* Little Hive House: more magnet layouts and full-colour illustrations for the design studio (assets/designer.js draws
   them; tools/design_kits.py makes the designs that use them). Each layout gets p: the design's colors (bg, ink, ac,
   soft), its words and options; it returns the html of a 600 x 600 magnet. Words that must stay on one line use one(),
   which shrinks them to fit. */
(function () {
  'use strict';
  var D = window.LHHDesigner;
  if (!D || !D.h) return;
  var h = D.h, F = h.F, T = h.T, one = h.one, def = h.def, ic = h.ic, esc = h.esc, SQ = h.SQ, star = h.star, mix = h.mix;
  var L = D.layouts, IL = D.illus;
  var A = F.A, BE = F.BE, JO = F.JO, JT = F.JT, CA = F.CA, PL = F.PL, DS = F.DS, CI = F.CI, CO = F.CO, DA = F.DA;
  function lines(t) { return T(t); }
  function rgba(hex, a) { hex = String(hex || '#000000').replace('#', ''); var n = parseInt(hex.length === 3 ? hex.split('').map(function (c) { return c + c; }).join('') : hex, 16); return 'rgba(' + (n >> 16 & 255) + ',' + (n >> 8 & 255) + ',' + (n & 255) + ',' + a + ')'; }
  function photoBg(p, pos) { return "url('" + String(p.photo || '').replace(/'/g, '%27') + "') " + (pos || def(p.pos, 'center')) + '/cover'; }
  function phoneIc(size, c) { return ic('phone', size, c).replace(/<img[^>]*>/, '') || ''; }

  /* ---------------------------------------------------------------- illustrations (100 x 100, full colour) */
  var I = {
    pizza: '<path d="M50 8 92 82Q50 98 8 82Z" fill="#F7C548"/><path d="M8 82Q50 98 92 82l-3-6Q50 90 11 76Z" fill="#D9822B"/><path d="M14 74Q50 87 86 74" stroke="#B5651D" stroke-width="5" fill="none" stroke-linecap="round"/><g fill="#C0392B"><circle cx="50" cy="34" r="7"/><circle cx="37" cy="58" r="7"/><circle cx="62" cy="60" r="7"/><circle cx="50" cy="74" r="5"/></g><g fill="#3E8E41"><ellipse cx="44" cy="46" rx="4" ry="2.5" transform="rotate(-30 44 46)"/><ellipse cx="58" cy="44" rx="4" ry="2.5" transform="rotate(25 58 44)"/><ellipse cx="50" cy="62" rx="4" ry="2.5"/></g><path d="M26 66c2 6 0 10-3 12M70 50c3 4 3 9 1 12" stroke="#F7C548" stroke-width="4" stroke-linecap="round"/>',
    coffee: '<ellipse cx="50" cy="84" rx="38" ry="8" fill="#E8D5B5"/><path d="M20 40h56v20c0 16-12 26-28 26S20 76 20 60z" fill="#FFFFFF" stroke="#6B4423" stroke-width="3"/><path d="M76 46c12 0 12 20 0 20" fill="none" stroke="#6B4423" stroke-width="5"/><ellipse cx="48" cy="40" rx="28" ry="6" fill="#8B5A2B"/><path d="M48 37c-4-4-10-1-7 3 2 3 7 4 7 4s5-1 7-4c3-4-3-7-7-3z" fill="#F3E3C8"/><path d="M38 28c-4-6 4-8 0-14M50 26c-4-6 4-8 0-14M62 28c-4-6 4-8 0-14" stroke="#B9A48A" stroke-width="3" fill="none" stroke-linecap="round"/>',
    tooth: '<circle cx="50" cy="52" r="42" fill="#D8F1EC"/><path d="M34 22c-12 0-16 12-12 24 4 11 6 16 7 28 1 10 9 11 10 1 1-8 4-12 11-12s10 4 11 12c1 10 9 9 10-1 1-12 3-17 7-28 4-12 0-24-12-24-8 0-10 4-16 4s-8-4-16-4z" fill="#FFFFFF" stroke="#2A7F78" stroke-width="3"/><path d="M58 30c5 1 8 4 8 9" stroke="#9ED8D0" stroke-width="4" fill="none" stroke-linecap="round"/><path d="M80 18l2 6 6 2-6 2-2 6-2-6-6-2 6-2z" fill="#F2B632"/><path d="M18 70l1.5 4 4 1.5-4 1.5-1.5 4-1.5-4-4-1.5 4-1.5z" fill="#F2B632"/>',
    house: '<rect x="0" y="80" width="100" height="20" fill="#9BC48A"/><path d="M12 48 50 18l38 30" fill="#C2553F"/><rect x="20" y="46" width="60" height="38" fill="#FBEFD9"/><rect x="44" y="60" width="12" height="24" fill="#3E6B5A"/><rect x="26" y="54" width="12" height="11" fill="#9CC9DE" stroke="#fff" stroke-width="2"/><rect x="62" y="54" width="12" height="11" fill="#9CC9DE" stroke="#fff" stroke-width="2"/><rect x="66" y="22" width="7" height="14" fill="#8E3B2C"/><circle cx="90" cy="70" r="10" fill="#5E8C4E"/><rect x="88.5" y="76" width="3" height="8" fill="#6B4423"/><path d="M50 84 46 100h8z" fill="#E8D5B5"/>',
    salon: '<circle cx="50" cy="50" r="44" fill="#F8DDE3"/><g stroke="#4A2F2B" stroke-width="4" fill="none"><circle cx="32" cy="70" r="9"/><circle cx="54" cy="74" r="9"/><path d="M38 63 74 18M48 66 34 24"/></g><rect x="62" y="40" width="26" height="9" rx="2" fill="#C0756A"/><path d="M64 49v10M68 49v10M72 49v10M76 49v10M80 49v10M84 49v10" stroke="#C0756A" stroke-width="2.5"/><path d="M14 30c10-6 20 2 14 10" stroke="#E7A9B6" stroke-width="4" fill="none" stroke-linecap="round"/>',
    dog: '<circle cx="50" cy="52" r="42" fill="#FCE9C8"/><path d="M22 30c-8 6-8 26 2 30l8-26z" fill="#8B5A2B"/><path d="M78 30c8 6 8 26-2 30l-8-26z" fill="#8B5A2B"/><ellipse cx="50" cy="52" rx="28" ry="30" fill="#D9A066"/><ellipse cx="50" cy="66" rx="16" ry="12" fill="#F3D9B1"/><circle cx="40" cy="48" r="4" fill="#2B2118"/><circle cx="60" cy="48" r="4" fill="#2B2118"/><ellipse cx="50" cy="60" rx="6" ry="4.5" fill="#2B2118"/><path d="M44 68c3 4 9 4 12 0" stroke="#2B2118" stroke-width="2.5" fill="none" stroke-linecap="round"/><path d="M50 72v6" stroke="#E86A6A" stroke-width="5" stroke-linecap="round"/>',
    car: '<rect x="0" y="82" width="100" height="18" fill="#D6D6D6"/><path d="M10 70v-12l10-18h60l10 18v12z" fill="#D64541"/><path d="M26 42h48l7 14H19z" fill="#BFE0F2"/><rect x="8" y="66" width="84" height="12" rx="4" fill="#B03A36"/><circle cx="26" cy="80" r="9" fill="#2B2118"/><circle cx="74" cy="80" r="9" fill="#2B2118"/><circle cx="26" cy="80" r="4" fill="#BDBDBD"/><circle cx="74" cy="80" r="4" fill="#BDBDBD"/><rect x="12" y="62" width="10" height="5" rx="2" fill="#FFE08A"/><rect x="78" y="62" width="10" height="5" rx="2" fill="#FFE08A"/>',
    cake: '<ellipse cx="50" cy="88" rx="40" ry="6" fill="#E8D5B5"/><rect x="16" y="56" width="68" height="30" rx="4" fill="#F7B7C4"/><rect x="22" y="36" width="56" height="22" rx="4" fill="#FFF3E6"/><path d="M16 60c6 6 11 6 17 0 6 6 11 6 17 0 6 6 11 6 17 0 6 6 11 6 17 0" fill="none" stroke="#FFF3E6" stroke-width="5"/><path d="M22 40c5 5 9 5 14 0 5 5 9 5 14 0 5 5 9 5 14 0 5 5 9 5 14 0" fill="none" stroke="#E86A8A" stroke-width="4"/><g fill="#7ABBE0"><rect x="34" y="20" width="4" height="16"/><rect x="48" y="18" width="4" height="18"/><rect x="62" y="20" width="4" height="16"/></g><g fill="#F2B632"><path d="M36 18c-3-4 0-8 0-8s3 4 0 8z"/><path d="M50 16c-3-4 0-8 0-8s3 4 0 8z"/><path d="M64 18c-3-4 0-8 0-8s3 4 0 8z"/></g>',
    flowers: '<path d="M50 92 36 56h28z" fill="#E8D5B5"/><path d="M42 56l8 36 8-36" fill="#D9C2A0"/><g fill="#5E8C4E"><path d="M50 58 30 34" stroke="#5E8C4E" stroke-width="3"/><path d="M50 58 70 32" stroke="#5E8C4E" stroke-width="3"/><path d="M50 58V28" stroke="#5E8C4E" stroke-width="3"/><ellipse cx="38" cy="46" rx="8" ry="4" transform="rotate(40 38 46)"/><ellipse cx="62" cy="46" rx="8" ry="4" transform="rotate(-40 62 46)"/></g><g fill="#E86A8A"><circle cx="30" cy="30" r="10"/><circle cx="70" cy="28" r="10"/></g><g fill="#F7C548"><circle cx="50" cy="22" r="11"/></g><g fill="#fff" opacity=".6"><circle cx="30" cy="30" r="4"/><circle cx="70" cy="28" r="4"/><circle cx="50" cy="22" r="4"/></g>',
    church: '<rect x="0" y="86" width="100" height="14" fill="#9BC48A"/><path d="M50 4v14M44 10h12" stroke="#B8860B" stroke-width="4" stroke-linecap="round"/><path d="M38 34 50 18l12 16z" fill="#8E3B2C"/><rect x="40" y="34" width="20" height="18" fill="#FBEFD9"/><path d="M18 56 50 36l32 20z" fill="#A04A36"/><rect x="24" y="54" width="52" height="32" fill="#FBEFD9"/><path d="M44 86V70a6 6 0 0 1 12 0v16z" fill="#6B4423"/><circle cx="50" cy="44" r="4" fill="#9CC9DE"/><rect x="30" y="62" width="8" height="12" rx="4" fill="#9CC9DE"/><rect x="62" y="62" width="8" height="12" rx="4" fill="#9CC9DE"/>',
    cap: '<circle cx="50" cy="52" r="42" fill="#E3EAF5"/><path d="M50 22 92 40 50 58 8 40z" fill="#1B2A4A"/><path d="M28 48v16c0 8 44 8 44 0V48L50 58z" fill="#24365E"/><path d="M84 43v20" stroke="#F2B632" stroke-width="3"/><circle cx="84" cy="66" r="4" fill="#F2B632"/><rect x="24" y="70" width="40" height="12" rx="6" fill="#FFF8E7" stroke="#B8860B" stroke-width="2" transform="rotate(-12 44 76)"/><path d="M42 72l-2 12" stroke="#C0392B" stroke-width="3" transform="rotate(-12 44 76)"/>',
    rings: '<circle cx="50" cy="52" r="42" fill="#FBF1DC"/><circle cx="40" cy="60" r="18" fill="none" stroke="#D4A537" stroke-width="7"/><circle cx="62" cy="60" r="18" fill="none" stroke="#E6C46A" stroke-width="7"/><path d="M62 42l-6-8h12z" fill="#BFE6F2"/><path d="M56 34l6-6 6 6z" fill="#E6F7FC"/><path d="M78 20l2 5 5 2-5 2-2 5-2-5-5-2 5-2z" fill="#F2B632"/>',
    tools: '<circle cx="50" cy="50" r="44" fill="#E3EAF0"/><path d="M28 74 66 36" stroke="#5B6B7A" stroke-width="10" stroke-linecap="round"/><circle cx="70" cy="30" r="12" fill="none" stroke="#5B6B7A" stroke-width="8"/><path d="M70 18v8" stroke="#E3EAF0" stroke-width="8"/><path d="M30 30 72 72" stroke="#E8641B" stroke-width="10" stroke-linecap="round"/><rect x="18" y="18" width="20" height="14" rx="3" fill="#E8641B" transform="rotate(45 28 25)"/>',
    spray: '<circle cx="50" cy="50" r="44" fill="#DFF6FB"/><path d="M36 44h26v38a6 6 0 0 1-6 6H42a6 6 0 0 1-6-6z" fill="#0096B4"/><rect x="40" y="56" width="18" height="14" rx="2" fill="#fff"/><path d="M40 44V34h18v10" fill="#0B3A4A"/><path d="M44 34v-8h20l6 8" fill="#0B3A4A"/><g fill="#9EE3F0"><circle cx="78" cy="24" r="5"/><circle cx="84" cy="38" r="3.5"/><circle cx="72" cy="40" r="3"/><circle cx="24" cy="28" r="6"/><circle cx="18" cy="44" r="3"/></g><path d="M80 52l2 5 5 2-5 2-2 5-2-5-5-2 5-2z" fill="#F2B632"/>',
    burger: '<path d="M18 46c0-18 64-18 64 0z" fill="#E09A3E"/><g fill="#FBEFD9"><ellipse cx="38" cy="36" rx="2" ry="1.2"/><ellipse cx="52" cy="32" rx="2" ry="1.2"/><ellipse cx="62" cy="38" rx="2" ry="1.2"/></g><path d="M14 50h72l-6 6H20z" fill="#5E9E4A"/><rect x="16" y="56" width="68" height="10" rx="5" fill="#7A3E22"/><path d="M16 66h68l-4 6H20z" fill="#F2C14E"/><path d="M18 72h64c0 10-64 10-64 0z" fill="#E09A3E"/>',
    icecream: '<path d="M34 50 50 94 66 50z" fill="#E0A458"/><path d="M38 56l22 0M42 66l14 0M36 54l20 26M64 54 44 80" stroke="#C17E35" stroke-width="2"/><circle cx="50" cy="40" r="18" fill="#F7B7C4"/><circle cx="36" cy="48" r="12" fill="#FFF3E6"/><circle cx="64" cy="48" r="12" fill="#B07A4F"/><circle cx="50" cy="20" r="6" fill="#C0392B"/><g fill="#7ABBE0"><rect x="44" y="34" width="5" height="2" rx="1"/><rect x="54" y="40" width="5" height="2" rx="1" transform="rotate(30 56 41)"/></g>',
    fitness: '<circle cx="50" cy="50" r="44" fill="#FFE4CC"/><path d="M38 28a12 12 0 0 1 24 0v6H38z" fill="none" stroke="#2B2118" stroke-width="7"/><path d="M28 50c0-12 10-18 22-18s22 6 22 18c0 16-10 28-22 28S28 66 28 50z" fill="#2B2118"/><text x="50" y="62" font-family="Anton" font-size="18" fill="#E8641B" text-anchor="middle">24</text>',
    spa: '<circle cx="50" cy="50" r="44" fill="#EEF0E6"/><ellipse cx="50" cy="80" rx="30" ry="8" fill="#9AA58A"/><ellipse cx="50" cy="68" rx="22" ry="7" fill="#7D8F76"/><ellipse cx="50" cy="58" rx="14" ry="5" fill="#5B7A4E"/><path d="M50 50c-6-8-6-20 0-30 6 10 6 22 0 30zM50 50c-8 0-16-6-18-16 8 0 14 4 18 16zM50 50c8 0 16-6 18-16-8 0-14 4-18 16z" fill="#E8A0BF"/>',
    school: '<circle cx="50" cy="50" r="44" fill="#FFF1C7"/><rect x="18" y="58" width="56" height="10" rx="2" fill="#2B7BBF"/><rect x="22" y="48" width="52" height="10" rx="2" fill="#5E9E4A"/><rect x="20" y="68" width="58" height="10" rx="2" fill="#E8641B"/><path d="M64 46c-8-6-20-2-18 10 2 10 8 16 16 12 8 4 14-2 16-12 2-12-10-16-18-10z" fill="#D64541" transform="translate(-4 -18)"/><path d="M60 28c0-4 3-7 6-8" stroke="#3E8E41" stroke-width="3" fill="none"/><path d="M78 20 88 10" stroke="#F2B632" stroke-width="6" stroke-linecap="round"/>',
    shield: '<circle cx="50" cy="50" r="44" fill="#E3EAF5"/><path d="M50 14l30 12v22c0 20-14 34-30 40-16-6-30-20-30-40V26z" fill="#13294B"/><path d="M50 22l22 9v17c0 15-10 26-22 31z" fill="#21406B"/><path d="M38 50l9 9 17-19" stroke="#F2A81D" stroke-width="6" fill="none" stroke-linecap="round" stroke-linejoin="round"/>',
    keyhouse: '<circle cx="50" cy="50" r="44" fill="#E5F3F1"/><path d="M14 52 50 22l36 30" fill="none" stroke="#18423C" stroke-width="7" stroke-linejoin="round"/><rect x="24" y="48" width="52" height="34" fill="#1F8A7A"/><circle cx="50" cy="60" r="8" fill="#F2B632"/><rect x="47" y="64" width="6" height="14" fill="#F2B632"/><rect x="53" y="72" width="6" height="3" fill="#F2B632"/>',
    vet: '<circle cx="50" cy="50" r="44" fill="#E5F3F1"/><path d="M50 82C30 68 20 58 22 44c2-10 16-14 28-2 12-12 26-8 28 2 2 14-8 24-28 38z" fill="#E86A6A"/><g fill="#fff"><ellipse cx="50" cy="56" rx="8" ry="7"/><ellipse cx="39" cy="46" rx="3.5" ry="4.5"/><ellipse cx="46" cy="40" rx="3.5" ry="4.5"/><ellipse cx="54" cy="40" rx="3.5" ry="4.5"/><ellipse cx="61" cy="46" rx="3.5" ry="4.5"/></g>',
    moving: '<rect x="0" y="84" width="100" height="16" fill="#D6D6D6"/><rect x="8" y="34" width="54" height="44" fill="#E8641B"/><path d="M62 46h18l12 14v18H62z" fill="#C2511A"/><rect x="68" y="50" width="12" height="10" fill="#BFE0F2"/><circle cx="24" cy="82" r="8" fill="#2B2118"/><circle cx="76" cy="82" r="8" fill="#2B2118"/><rect x="16" y="42" width="16" height="14" fill="#E0A458"/><rect x="34" y="46" width="18" height="18" fill="#C17E35"/><path d="M16 49h16M43 46v18" stroke="#8B5A2B" stroke-width="2"/>',
    bolt: '<circle cx="50" cy="50" r="44" fill="#2B2B2B"/><path d="M56 12 26 54h20l-6 34 34-46H52z" fill="#F7C548"/><path d="M56 12 46 40h10z" fill="#FFE08A"/>',
    sprout: '<circle cx="50" cy="50" r="44" fill="#E6F2D9"/><path d="M28 64h44l-6 24H34z" fill="#C2553F"/><rect x="24" y="58" width="52" height="8" rx="2" fill="#A04A36"/><path d="M50 58V36" stroke="#3E8E41" stroke-width="4"/><path d="M50 42c-16 0-22-10-20-22 14 0 22 8 20 22zM50 36c12 0 18-8 18-18-12 0-18 8-18 18z" fill="#5E9E4A"/>',
    clinic: '<circle cx="50" cy="50" r="44" fill="#E9EEF2"/><rect x="38" y="18" width="24" height="64" rx="4" fill="#C0392B"/><rect x="18" y="38" width="64" height="24" rx="4" fill="#C0392B"/><rect x="42" y="22" width="16" height="56" rx="3" fill="#E85D50"/>',
    camera: '<circle cx="50" cy="50" r="44" fill="#2F3B48"/><rect x="16" y="34" width="68" height="44" rx="8" fill="#F2F4F7"/><path d="M36 34l6-10h16l6 10z" fill="#F2F4F7"/><circle cx="50" cy="56" r="16" fill="#2F3B48"/><circle cx="50" cy="56" r="10" fill="#7FD1B9"/><circle cx="46" cy="52" r="3" fill="#fff"/><rect x="70" y="40" width="8" height="5" rx="2" fill="#E8641B"/>',
    balloons: '<path d="M38 60c-4 10 4 18 0 30M62 58c4 12-4 20 0 32M50 62v28" stroke="#9A9A9A" stroke-width="1.5" fill="none"/><ellipse cx="36" cy="38" rx="16" ry="20" fill="#E86A8A"/><ellipse cx="64" cy="36" rx="16" ry="20" fill="#7ABBE0"/><ellipse cx="50" cy="44" rx="16" ry="20" fill="#F7C548"/><g fill="#fff" opacity=".5"><ellipse cx="30" cy="30" rx="4" ry="6"/><ellipse cx="58" cy="28" rx="4" ry="6"/><ellipse cx="44" cy="36" rx="4" ry="6"/></g>',
    baby: '<circle cx="50" cy="50" r="44" fill="#E7F3FB"/><rect x="38" y="30" width="24" height="52" rx="10" fill="#FFFFFF" stroke="#7ABBE0" stroke-width="3"/><rect x="40" y="22" width="20" height="10" rx="3" fill="#F7B7C4"/><path d="M46 22c0-10 8-10 8 0" fill="#F2C14E"/><path d="M40 50h20M40 60h20M40 70h20" stroke="#BFE0F2" stroke-width="3"/>',
    gift: '<circle cx="50" cy="50" r="44" fill="#FDE8EC"/><rect x="20" y="44" width="60" height="40" rx="3" fill="#C0392B"/><rect x="16" y="34" width="68" height="14" rx="3" fill="#D64541"/><rect x="45" y="34" width="10" height="50" fill="#F2B632"/><path d="M50 34c-8-14-22-12-18-2 2 4 10 3 18 2zM50 34c8-14 22-12 18-2-2 4-10 3-18 2z" fill="#F2B632"/>',
    taco: '<path d="M10 74a40 40 0 0 1 80 0z" fill="#F2C14E"/><path d="M16 60c6-8 10-2 16-8s10 2 16-4 10 2 16-4 10 4 12 10" fill="none" stroke="#5E9E4A" stroke-width="7" stroke-linecap="round"/><g fill="#D64541"><circle cx="30" cy="62" r="4"/><circle cx="52" cy="56" r="4"/><circle cx="70" cy="62" r="4"/></g><path d="M10 74h80" stroke="#D9A33B" stroke-width="4"/>',
    sushi: '<ellipse cx="50" cy="80" rx="40" ry="8" fill="#2B2B2B"/><rect x="18" y="52" width="30" height="22" rx="6" fill="#FFFFFF"/><path d="M18 52h30l-4-10H22z" fill="#F08A5D"/><path d="M20 47h26" stroke="#fff" stroke-width="2"/><circle cx="68" cy="62" r="14" fill="#1F2D1F"/><circle cx="68" cy="62" r="10" fill="#fff"/><circle cx="68" cy="62" r="5" fill="#F08A5D"/><path d="M14 30 86 16M14 36 86 24" stroke="#C17E35" stroke-width="3" stroke-linecap="round"/>',
    paint: '<circle cx="50" cy="50" r="44" fill="#FFF1E2"/><rect x="24" y="22" width="46" height="22" rx="4" fill="#2B7BBF"/><path d="M70 30h8v18H50v10" stroke="#5B6B7A" stroke-width="4" fill="none"/><rect x="46" y="58" width="8" height="28" rx="3" fill="#8B5A2B"/><path d="M24 44c0 8 8 6 8 14" stroke="#2B7BBF" stroke-width="5" fill="none" stroke-linecap="round"/>',
    pool: '<rect x="0" y="0" width="100" height="100" fill="#DFF6FB"/><rect x="0" y="52" width="100" height="48" fill="#4FC3E3"/><path d="M0 58c10-6 20-6 30 0s20 6 30 0 20-6 30 0 10 4 10 4M0 74c10-6 20-6 30 0s20 6 30 0 20-6 30 0" stroke="#fff" stroke-width="3" fill="none"/><path d="M60 52V22a8 8 0 0 1 16 0M76 52V22a8 8 0 0 1 16 0" stroke="#5B6B7A" stroke-width="4" fill="none"/><path d="M60 32h32M60 44h32" stroke="#5B6B7A" stroke-width="4"/><circle cx="24" cy="22" r="12" fill="#F7C548"/>'
  };
  Object.keys(I).forEach(function (k) { IL[k] = I[k]; });

  /* ---------------------------------------------------------------- layouts */
  function bottomBar(p, left, right, h0, bg, fg) {
    return '<div style="position:absolute;left:0;right:0;bottom:0;height:' + (h0 || 88) + 'px;background:' + (bg || p.ac) + ';color:' + (fg || p.bg) + ';display:flex;align-items:center;justify-content:space-between;gap:18px;padding:0 36px">' +
      one('min-width:0;flex:1;font:400 34px/1.1 ' + DS, left) + one('flex:none;max-width:60%;font:400 50px/1 ' + BE + ';letter-spacing:1px;padding-top:6px', right) + '</div>';
  }

  /* neon sign on a dark wall */
  L.neon = function (p) {
    var glow = function (c) { return 'text-shadow:0 0 6px ' + c + ',0 0 18px ' + c + ',0 0 38px ' + c; };
    return '<div style="' + SQ + 'background:radial-gradient(circle at 50% 40%,' + mix(p.bg, '#FFFFFF', .08) + ',' + p.bg + ' 70%);color:' + p.ink + ';text-align:center;padding:52px 40px">' +
      '<div style="position:absolute;inset:22px;border:3px solid ' + p.ac + ';border-radius:26px;box-shadow:0 0 12px ' + p.ac + ',inset 0 0 12px ' + p.ac + '"></div>' +
      one('font:700 20px ' + JO + ';letter-spacing:8px;color:' + p.ac + ';' + glow(p.ac), T(p.sub)) +
      one('font:400 96px/1.15 ' + DA + ';margin-top:20px;color:#FFFFFF;' + glow(p.ac), T(p.name)) +
      one('font:400 54px/1.1 ' + A + ';text-transform:uppercase;margin-top:12px;color:' + p.ac + ';' + glow(p.ac), T(p.head)) +
      '<div style="font:500 24px ' + JT + ';margin-top:16px;opacity:.9">' + T(p.line) + '</div>' +
      one('font:400 60px/1 ' + BE + ';letter-spacing:3px;margin-top:22px;color:#FFFFFF;' + glow(p.ac), T(p.phone)) + '</div>';
  };
  /* kraft paper with a stamp */
  L.kraft = function (p) {
    var paper = 'background:#C9A27A repeating-linear-gradient(35deg,rgba(255,255,255,.04) 0 2px,transparent 2px 6px),radial-gradient(circle at 20% 30%,rgba(255,255,255,.12),transparent 50%),radial-gradient(circle at 80% 70%,rgba(0,0,0,.08),transparent 45%);background-blend-mode:overlay';
    return '<div style="' + SQ + paper + ';background-color:#C9A27A;color:#3A2A1A;text-align:center;padding:46px 46px 0">' +
      '<div style="position:absolute;left:0;right:0;top:82px;height:3px;background:repeating-linear-gradient(90deg,#3A2A1A 0 10px,transparent 10px 18px);opacity:.5"></div>' +
      '<div style="display:inline-block;border:4px solid ' + p.ac + ';color:' + p.ac + ';padding:10px 22px;transform:rotate(-4deg);margin-top:44px;border-radius:8px">' + one('font:400 52px/1.1 ' + A + ';text-transform:uppercase;letter-spacing:2px', T(p.name)) + '</div>' +
      one('font:700 18px ' + JO + ';letter-spacing:6px;margin-top:22px', T(p.sub)) +
      '<div style="font:400 44px/1.15 ' + CA + ';margin-top:24px">' + T(p.head) + '</div>' +
      '<div style="font:500 22px ' + JT + ';margin-top:10px;opacity:.85">' + T(p.line) + '</div>' +
      one('font:400 54px/1 ' + BE + ';letter-spacing:2px;margin-top:20px', T(p.phone)) + '</div>';
  };
  /* chalkboard menu */
  L.chalk = function (p) {
    var rows = (p.rows || []).slice(0, 5).map(function (r) {
      return '<div style="display:flex;justify-content:space-between;gap:14px;font:400 33px/1.15 ' + CA + ';padding:5px 0;border-bottom:2px dashed rgba(255,255,255,.25)"><span style="white-space:nowrap">' + T(r[0]) + '</span>' + one('min-width:0;text-align:right;color:' + p.ac, T(r[1])) + '</div>';
    }).join('');
    return '<div style="' + SQ + 'background:radial-gradient(circle at 30% 20%,#3B4A40,#22302A 60%,#1A241F);color:#F4F1E8;padding:28px 40px 0;border:16px solid #8B5A2B">' +
      '<div style="display:flex;align-items:center;justify-content:center;gap:12px">' + ic(p.icon, 54, '#F4F1E8') + one('min-width:0;font:400 54px/1.1 ' + DA, T(p.name)) + '</div>' +
      one('text-align:center;font:400 44px/1.1 ' + CA + ';color:' + p.ac + ';margin-top:2px', T(p.head)) + '<div style="margin-top:6px">' + rows + '</div>' +
      one('text-align:center;font:400 40px/1 ' + BE + ';letter-spacing:2px;margin-top:12px', T(p.phone)) + '</div>';
  };
  /* watercolor wash */
  L.watercolor = function (p) {
    var wash = 'radial-gradient(circle at 18% 22%,' + rgba(p.ac, .45) + ',transparent 38%),radial-gradient(circle at 82% 28%,' + rgba(p.soft, .9) + ',transparent 42%),radial-gradient(circle at 70% 85%,' + rgba(p.ac, .3) + ',transparent 40%),radial-gradient(circle at 20% 80%,' + rgba(p.soft, .8) + ',transparent 38%)';
    return '<div style="' + SQ + 'background:' + wash + ',' + p.bg + ';color:' + p.ink + ';text-align:center;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:40px 50px">' +
      ic(p.icon, p.logo ? 110 : 84, p.ac) + one('font:400 84px/1.15 ' + DA + ';margin-top:10px;max-width:100%', T(p.name)) +
      one('font:700 18px ' + JO + ';letter-spacing:7px;margin-top:8px;max-width:100%;color:' + mix(p.ac, p.ink, .3), T(p.sub)) +
      '<div style="font:400 30px/1.25 ' + CO + ';margin-top:22px">' + T(p.line) + '</div>' +
      one('font:500 30px ' + JT + ';letter-spacing:2px;margin-top:18px;max-width:100%', T(p.phone)) + one('font:500 20px ' + JT + ';letter-spacing:3px;opacity:.75;margin-top:4px;max-width:100%', T(p.web)) + '</div>';
  };
  /* admission ticket */
  L.ticket = function (p) {
    var notch = 'radial-gradient(circle at 0 50%,' + p.soft + ' 22px,transparent 23px),radial-gradient(circle at 100% 50%,' + p.soft + ' 22px,transparent 23px)';
    return '<div style="' + SQ + 'background:' + p.soft + ';padding:70px 26px">' +
      '<div style="height:460px;background:' + notch + ',' + p.bg + ';color:' + p.ink + ';border-radius:18px;display:flex;overflow:hidden">' +
      '<div style="flex:1;min-width:0;padding:34px 30px;display:flex;flex-direction:column;justify-content:center">' +
      one('font:700 18px ' + JO + ';letter-spacing:6px;color:' + p.ac, T(p.kicker)) + one('font:400 120px/1 ' + A + ';margin-top:8px;color:' + p.ac, T(p.offer)) +
      one('font:600 28px ' + JT + ';margin-top:6px', T(p.head)) +
      '<div style="display:flex;align-items:center;gap:12px;margin-top:20px">' + ic(p.icon, p.logo ? 70 : 52, p.ink) + '<div style="min-width:0;flex:1">' + one('font:400 32px/1.1 ' + DS, T(p.name)) + one('font:600 24px ' + JT, T(p.phone)) + '</div></div>' +
      '<div style="font:500 16px ' + JT + ';opacity:.7;margin-top:14px">' + T(p.line) + '</div></div>' +
      '<div style="width:96px;border-left:4px dashed ' + p.soft + ';display:flex;align-items:center;justify-content:center;background:' + p.ac + '"><div style="writing-mode:vertical-rl;font:400 40px ' + A + ';letter-spacing:6px;color:' + p.bg + ';white-space:nowrap">ADMIT ONE</div></div></div></div>';
  };
  /* business card on the fridge */
  L.bizcard = function (p) {
    var row = function (icon, txt, big) { return txt ? '<div style="display:flex;align-items:center;gap:18px;margin:12px 0">' + '<span style="width:56px;height:56px;border-radius:50%;background:' + p.ac + ';display:grid;place-items:center;flex:none">' + h.ic(icon, 28, p.bg).replace(/<img[^>]*>/, '') + '</span>' + one('min-width:0;flex:1;font:' + (big ? '400 44px ' + BE + ';letter-spacing:2px' : '500 28px ' + JT), T(txt)) + '</div>' : ''; };
    var saved = h.cur(); var logo = saved && saved.logo;
    return '<div style="' + SQ + 'background:' + p.bg + ';color:' + p.ink + '">' +
      '<div style="height:210px;background:' + p.ac + ';display:flex;align-items:center;gap:20px;padding:0 40px;color:' + p.bg + '">' +
      '<div style="width:130px;height:130px;border-radius:50%;background:' + p.bg + ';display:grid;place-items:center;flex:none">' + ic(p.icon, logo ? 110 : 80, p.ac) + '</div>' +
      '<div style="min-width:0;flex:1">' + one('font:400 44px/1.1 ' + DS, T(p.name)) + one('font:700 17px ' + JO + ';letter-spacing:5px;margin-top:8px;opacity:.9', T(p.sub)) + '</div></div>' +
      '<div style="height:350px;padding:0 50px;display:flex;flex-direction:column;justify-content:center">' + row('phone', p.phone, 1) + row('pin', p.line) + row('clock', p.web) + '</div>' +
      '<div style="position:absolute;left:0;right:0;bottom:0;height:40px;background:repeating-linear-gradient(90deg,' + p.ac + ' 0 40px,' + mix(p.ac, p.bg, .55) + ' 40px 80px)"></div></div>';
  };
  /* 70s sunset stripes */
  L.retro = function (p) {
    var c = [p.ac, mix(p.ac, p.ink, .25), mix(p.ac, '#FFFFFF', .35), mix(p.ac, p.bg, .55)];
    var arcs = c.map(function (col, i) { return '<div style="position:absolute;left:50%;bottom:-' + (400 - i * 34) + 'px;width:' + (760 - i * 120) + 'px;height:' + (760 - i * 120) + 'px;margin-left:-' + (380 - i * 60) + 'px;border-radius:50%;background:' + col + '"></div>'; }).join('');
    return '<div style="' + SQ + 'background:' + p.bg + ';color:' + p.ink + ';text-align:center">' + arcs +
      '<div style="position:relative;padding:54px 40px 0">' + one('font:700 20px ' + JO + ';letter-spacing:8px', T(p.sub)) +
      one('font:italic 900 86px/1.05 ' + PL + ';margin-top:14px', T(p.name)) +
      '<div style="font:500 26px ' + JT + ';margin-top:12px">' + T(p.line) + '</div></div>' +
      '<div style="position:absolute;left:0;right:0;bottom:40px;display:flex;justify-content:center;padding:0 60px"><div style="max-width:100%;background:' + p.ink + ';color:' + p.bg + ';border-radius:999px;padding:12px 34px 6px">' + one('font:400 60px/1 ' + BE + ';letter-spacing:3px', T(p.phone)) + '</div></div></div>';
  };
  /* postage stamp */
  L.stamp = function (p) {
    var edge = 'radial-gradient(circle,' + p.soft + ' 9px,transparent 10px) -12px -12px/26px 26px';
    return '<div style="' + SQ + 'background:' + p.soft + ';padding:30px">' +
      '<div style="position:absolute;inset:30px;background:' + edge + '"></div>' +
      '<div style="position:absolute;inset:44px;background:' + p.bg + ';color:' + p.ink + ';text-align:center;padding:30px 30px 0;border:3px solid ' + p.ac + '">' +
      '<div style="display:flex;justify-content:space-between;font:700 18px ' + JO + ';letter-spacing:4px;color:' + p.ac + '"><span>' + esc(def(p.since, 'USA')) + '</span><span>★ ★ ★</span></div>' +
      '<div style="margin:16px auto 0;display:flex;justify-content:center">' + ic(p.icon, p.logo ? 170 : 150, p.ac) + '</div>' +
      one('font:400 54px/1.1 ' + A + ';text-transform:uppercase;letter-spacing:2px;margin-top:14px', T(p.name)) +
      one('font:400 28px ' + CO + ';margin-top:2px', T(p.sub)) + one('font:400 46px/1 ' + BE + ';letter-spacing:2px;margin-top:10px;color:' + p.ac, T(p.phone)) + '</div></div>';
  };
  /* vintage label with ornate frame */
  L.label = function (p) {
    return '<div style="' + SQ + 'background:' + p.soft + ';display:grid;place-items:center">' +
      '<div style="width:520px;height:440px;background:' + p.bg + ';color:' + p.ink + ';border-radius:60px;border:6px double ' + p.ac + ';box-shadow:0 0 0 10px ' + p.bg + ',0 0 0 13px ' + p.ac + ';text-align:center;padding:40px 40px 0;position:relative">' +
      '<div style="display:flex;align-items:center;justify-content:center;gap:14px;color:' + p.ac + '"><span style="height:2px;width:70px;background:' + p.ac + '"></span>' + one('font:700 18px ' + JO + ';letter-spacing:6px', T(p.since)) + '<span style="height:2px;width:70px;background:' + p.ac + '"></span></div>' +
      one('font:500 76px/1.1 ' + CI + ';margin-top:20px', T(p.name)) +
      '<div style="margin:14px auto;width:260px;height:44px;background:' + p.ac + ';color:' + p.bg + ';clip-path:polygon(0 0,100% 0,92% 50%,100% 100%,0 100%,8% 50%);display:grid;place-items:center">' + one('font:700 17px ' + JO + ';letter-spacing:5px;max-width:200px', T(p.sub)) + '</div>' +
      '<div style="font:400 28px ' + CO + '">' + T(p.line) + '</div>' + one('font:400 52px/1 ' + BE + ';letter-spacing:2px;margin-top:12px', T(p.phone)) + '</div></div>';
  };
  /* giant phone number */
  L.bignum = function (p) {
    var digits = String(p.phone || '').replace(/^\(?(\d{3})\)?[\s.-]*/, function (m, a) { return '<span style="font-size:.55em;opacity:.85">(' + a + ')</span><br>'; });
    return '<div style="' + SQ + 'background:' + p.bg + ';color:' + p.ink + ';padding:40px 44px">' +
      '<div style="display:flex;align-items:center;gap:16px">' + ic(p.icon, p.logo ? 90 : 64, p.ac) + '<div style="min-width:0;flex:1">' + one('font:400 44px/1.1 ' + A + ';text-transform:uppercase', T(p.name)) + one('font:700 17px ' + JO + ';letter-spacing:5px;color:' + p.ac, T(p.sub)) + '</div></div>' +
      one('font:400 40px/1.1 ' + A + ';text-transform:uppercase;margin-top:30px;color:' + p.ac, T(p.head)) +
      '<div style="font:400 150px/.9 ' + BE + ';letter-spacing:4px;margin-top:10px">' + digits + '</div>' +
      '<div style="font:600 22px ' + JT + ';margin-top:14px;opacity:.85">' + T(p.line) + '</div></div>';
  };
  /* speech bubble */
  L.bubble = function (p) {
    return '<div style="' + SQ + 'background:' + p.ac + ';color:' + p.ink + ';padding:40px">' +
      '<div style="position:relative;background:' + p.bg + ';border-radius:40px;padding:36px 36px 30px;text-align:center">' +
      one('font:400 68px/1.05 ' + A + ';text-transform:uppercase', T(p.head)) + '<div style="font:500 26px/1.25 ' + JT + ';margin-top:12px">' + T(p.line) + '</div>' +
      '<div style="position:absolute;left:80px;bottom:-40px;width:0;height:0;border-left:30px solid transparent;border-right:30px solid transparent;border-top:44px solid ' + p.bg + '"></div></div>' +
      '<div style="display:flex;align-items:center;gap:16px;margin-top:56px;color:' + p.bg + '">' + '<div style="width:110px;height:110px;border-radius:50%;background:' + p.bg + ';display:grid;place-items:center;flex:none">' + ic(p.icon, p.logo ? 92 : 70, p.ac) + '</div>' +
      '<div style="min-width:0;flex:1">' + one('font:400 38px/1.1 ' + DS, T(p.name)) + one('font:400 58px/1 ' + BE + ';letter-spacing:2px', T(p.phone)) + '</div></div></div>';
  };
  /* sticky note on the fridge */
  L.sticky = function (p) {
    return '<div style="' + SQ + 'background:' + p.soft + '">' +
      '<div style="position:absolute;left:58px;top:46px;width:484px;height:470px;background:#FFE680;transform:rotate(-2.5deg);box-shadow:0 18px 30px rgba(0,0,0,.18);padding:56px 42px 0;color:#2B2118">' +
      '<div style="position:absolute;left:170px;top:-18px;width:140px;height:36px;background:' + rgba(p.ac, .75) + ';transform:rotate(3deg)"></div>' +
      '<div style="font:400 50px/1.15 ' + CA + '">' + T(p.head) + '</div>' +
      '<div style="font:400 34px/1.25 ' + CA + ';margin-top:14px;color:#1F3B73">' + T(p.line) + '</div>' +
      '<div style="position:absolute;left:30px;right:30px;bottom:26px;display:flex;align-items:center;gap:12px;border-top:2px solid rgba(0,0,0,.15);padding-top:14px">' + ic(p.icon, p.logo ? 70 : 50, p.ac) +
      '<div style="min-width:0;flex:1">' + one('font:400 30px/1.1 ' + DS, T(p.name)) + one('font:600 24px ' + JT, T(p.phone)) + '</div></div></div></div>';
  };
  /* magazine cover with a photo */
  L.magazine = function (p) {
    return '<div style="' + SQ + 'background:' + photoBg(p) + ';color:#FFFFFF">' +
      '<div style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.45),transparent 30%,transparent 55%,rgba(0,0,0,.65))"></div>' +
      '<div style="position:absolute;left:30px;right:30px;top:34px;text-align:center">' + one('font:400 94px/1.1 ' + DS + ';letter-spacing:-1px', T(p.name)) + '</div>' +
      '<div style="position:absolute;left:30px;bottom:30px;right:30px">' + '<div style="display:inline-block;background:' + p.ac + ';color:' + p.bg + ';padding:6px 12px 3px;font:700 17px ' + JO + ';letter-spacing:4px">' + esc(p.sub) + '</div>' +
      one('font:400 58px/1.05 ' + A + ';text-transform:uppercase;margin-top:10px', T(p.head)) + '<div style="display:flex;justify-content:space-between;gap:14px;margin-top:6px">' + one('font:500 22px ' + JT + ';min-width:0;flex:1', T(p.line)) + one('font:700 26px ' + JT + ';flex:none', T(p.phone)) + '</div></div></div>';
  };
  /* half photo, half text */
  L.halfphoto = function (p) {
    return '<div style="' + SQ + 'background:' + p.bg + ';color:' + p.ink + ';display:flex">' +
      '<div style="width:270px;flex:none;background:' + photoBg(p) + '"></div>' +
      '<div style="flex:1;min-width:0;padding:44px 30px 0;display:flex;flex-direction:column">' + ic(p.icon, p.logo ? 90 : 60, p.ac) +
      '<div style="font:400 46px/1.05 ' + DS + ';margin-top:16px">' + T(p.name) + '</div>' + one('font:700 15px ' + JO + ';letter-spacing:4px;margin-top:10px;color:' + p.ac, T(p.sub)) +
      '<div style="font:500 22px/1.3 ' + JT + ';margin-top:18px">' + T(p.line) + '</div>' +
      '<div style="margin-top:auto;margin-bottom:40px">' + one('font:400 50px/1 ' + BE + ';letter-spacing:1px', T(p.phone)) + one('font:500 18px ' + JT + ';opacity:.75', T(p.web)) + '</div></div></div>';
  };
  /* photo in a thick coloured frame, name on the frame */
  L.frame = function (p) {
    return '<div style="' + SQ + 'background:' + p.ac + ';padding:36px 36px 0;color:' + p.bg + '">' +
      '<div style="height:400px;background:' + photoBg(p) + ';border-radius:6px"></div>' +
      '<div style="display:flex;justify-content:space-between;align-items:center;gap:16px;height:128px">' + '<div style="min-width:0;flex:1">' + one('font:400 46px/1.1 ' + DS, T(p.name)) + one('font:700 16px ' + JO + ';letter-spacing:5px;margin-top:4px', T(p.sub)) + '</div>' +
      one('font:400 46px/1 ' + BE + ';letter-spacing:1px;flex:none;max-width:55%', T(p.phone)) + '</div></div>';
  };
  /* arch window */
  L.archphoto = function (p) {
    return '<div style="' + SQ + 'background:' + p.bg + ';color:' + p.ink + ';text-align:center;padding-top:34px">' +
      '<div style="margin:0 auto;width:330px;height:330px;border-radius:165px 165px 0 0;background:' + photoBg(p) + ';box-shadow:0 0 0 8px ' + p.bg + ',0 0 0 11px ' + p.ac + '"></div>' +
      '<div style="padding:0 40px">' + one('font:400 60px/1.15 ' + DA + ';margin-top:22px', T(p.name)) + one('font:700 17px ' + JO + ';letter-spacing:6px;color:' + p.ac + ';margin-top:2px', T(p.sub)) +
      one('font:500 26px ' + JT + ';letter-spacing:2px;margin-top:12px', T(p.phone)) + '</div></div>';
  };
  /* diagonal split */
  L.diagonal = function (p) {
    return '<div style="' + SQ + 'background:' + p.bg + ';color:' + p.ink + '">' +
      '<div style="position:absolute;inset:0;background:' + p.ac + ';clip-path:polygon(0 62%,100% 38%,100% 100%,0 100%)"></div>' +
      '<div style="position:relative;padding:44px 42px 0">' + '<div style="display:flex;align-items:center;gap:14px">' + ic(p.icon, p.logo ? 84 : 60, p.ac) + one('min-width:0;flex:1;font:400 40px/1.1 ' + A + ';text-transform:uppercase', T(p.name)) + '</div>' +
      one('font:400 92px/1 ' + A + ';text-transform:uppercase;margin-top:24px', T(p.head)) + '<div style="font:500 24px ' + JT + ';margin-top:10px;max-width:430px">' + T(p.line) + '</div></div>' +
      '<div style="position:absolute;right:42px;bottom:40px;left:42px;text-align:right;color:' + p.bg + '">' + one('font:700 17px ' + JO + ';letter-spacing:5px', T(p.sub)) + one('font:400 74px/1 ' + BE + ';letter-spacing:2px', T(p.phone)) + '</div></div>';
  };
  /* big QR with an arrow */
  L.qrbig = function (p) {
    return '<div style="' + SQ + 'background:' + p.bg + ';color:' + p.ink + ';text-align:center;padding-top:30px">' +
      one('font:400 62px/1.05 ' + A + ';text-transform:uppercase;color:' + p.ac + ';padding:0 40px', T(p.head)) + '<div style="font:500 22px ' + JT + ';margin-top:4px;padding:0 40px">' + T(p.line) + '</div>' +
      '<div style="display:inline-block;margin-top:18px;background:#fff;padding:16px;border-radius:20px;border:5px solid ' + p.ink + '">' + h.qr(p.url, 250, '#111111') + '</div>' +
      '<div style="display:flex;align-items:center;justify-content:center;gap:12px;margin-top:16px;padding:0 40px">' + ic(p.icon, p.logo ? 64 : 44, p.ac) + one('min-width:0;font:400 34px/1.1 ' + DS, T(p.name)) + '</div></div>';
  };
  /* QR inside a phone */
  L.qrphone = function (p) {
    return '<div style="' + SQ + 'background:' + p.ac + ';color:' + p.bg + ';display:flex;align-items:center;gap:20px;padding:0 36px">' +
      '<div style="flex:1;min-width:0">' + ic(p.icon, p.logo ? 90 : 62, p.bg) + '<div style="font:400 64px/1 ' + A + ';text-transform:uppercase;margin-top:18px">' + T(p.head) + '</div>' +
      '<div style="font:500 24px/1.25 ' + JT + ';margin-top:14px">' + T(p.line) + '</div>' + one('font:400 32px/1.1 ' + DS + ';margin-top:20px', T(p.name)) + one('font:600 22px ' + JT, T(p.web || p.phone)) + '</div>' +
      '<div style="width:236px;height:450px;flex:none;border-radius:38px;background:#111;padding:14px;box-shadow:0 14px 30px rgba(0,0,0,.3)"><div style="height:100%;border-radius:28px;background:#fff;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px;color:#111">' +
      h.qr(p.url, 180, '#111111') + '<div style="font:700 15px ' + JO + ';letter-spacing:4px">SCAN ME</div></div></div></div>';
  };
  /* reviews: stars and QR */
  L.review = function (p) {
    return '<div style="' + SQ + 'background:' + p.bg + ';color:' + p.ink + ';text-align:center;padding:34px 40px 0">' +
      '<div style="font:400 64px ' + JT + ';letter-spacing:6px;color:#E0A526;line-height:1">★★★★★</div>' + one('font:400 60px/1.1 ' + DA + ';margin-top:6px', T(p.head)) +
      '<div style="font:500 24px ' + JT + ';margin-top:6px">' + T(p.line) + '</div>' +
      '<div style="display:flex;align-items:center;justify-content:center;gap:24px;margin-top:22px">' + '<div style="background:#fff;padding:12px;border-radius:14px;box-shadow:0 0 0 4px ' + p.ac + '">' + h.qr(p.url, 190, '#111111') + '</div>' +
      '<div style="text-align:left;max-width:220px">' + ic(p.icon, p.logo ? 90 : 60, p.ac) + '<div style="font:400 32px/1.1 ' + DS + ';margin-top:10px">' + T(p.name) + '</div></div></div></div>';
  };
  /* refer a friend */
  L.referral = function (p) {
    return '<div style="' + SQ + 'background:' + p.ac + ';color:' + p.bg + ';text-align:center;padding:40px 40px 0">' +
      one('font:700 20px ' + JO + ';letter-spacing:8px', T(p.kicker)) + '<div style="display:flex;justify-content:center;gap:18px;margin-top:20px">' +
      [0, 1].map(function (i) { return '<div style="width:200px;height:200px;border-radius:50%;background:' + p.bg + ';color:' + p.ac + ';display:grid;place-items:center"><div>' + one('font:400 74px/1 ' + A, T(p.offer)) + '<div style="font:700 17px ' + JO + ';letter-spacing:4px;margin-top:4px">' + (i ? 'FOR THEM' : 'FOR YOU') + '</div></div></div>'; }).join('') + '</div>' +
      '<div style="font:500 26px/1.25 ' + JT + ';margin-top:20px">' + T(p.head) + '</div>' +
      '<div style="display:flex;align-items:center;justify-content:center;gap:12px;margin-top:18px">' + ic(p.icon, p.logo ? 70 : 48, p.bg) + '<div style="text-align:left;min-width:0">' + one('font:400 32px/1.1 ' + DS, T(p.name)) + one('font:600 22px ' + JT, T(p.phone)) + '</div></div></div>';
  };
  /* in case of emergency */
  L.emergency = function (p) {
    var rows = (p.rows || []).slice(0, 5).map(function (r) {
      return '<div style="display:flex;justify-content:space-between;gap:12px;padding:10px 0;border-bottom:2px solid ' + rgba(p.ink, .15) + ';font:600 26px ' + JT + '"><span style="white-space:nowrap">' + T(r[0]) + '</span>' + one('min-width:0;text-align:right;font:400 34px/1 ' + BE + ';letter-spacing:1px', T(r[1]) || '&nbsp;') + '</div>';
    }).join('');
    return '<div style="' + SQ + 'background:' + p.bg + ';color:' + p.ink + ';padding:0 40px">' +
      '<div style="margin:0 -40px;background:#C62828;color:#fff;padding:22px 40px 16px;display:flex;align-items:center;gap:14px"><svg width="54" height="54" viewBox="0 0 64 64"><path d="M32 6 60 56H4z" fill="#fff"/><path d="M32 24v16" stroke="#C62828" stroke-width="6" stroke-linecap="round"/><circle cx="32" cy="48" r="3.5" fill="#C62828"/></svg>' +
      '<div style="min-width:0;flex:1">' + one('font:400 46px/1.05 ' + A + ';text-transform:uppercase', T(p.head)) + one('font:600 18px ' + JT + ';opacity:.9', T(p.line)) + '</div></div>' +
      '<div style="margin-top:8px">' + rows + '</div>' +
      '<div style="position:absolute;left:0;right:0;bottom:0;height:86px;background:' + p.ac + ';color:' + p.bg + ';display:flex;align-items:center;gap:14px;padding:0 40px">' + ic(p.icon, p.logo ? 64 : 46, p.bg) + one('min-width:0;flex:1;font:400 30px/1.1 ' + DS, T(p.name)) + one('flex:none;font:400 44px/1 ' + BE + ';letter-spacing:1px', T(p.phone)) + '</div></div>';
  };
  /* modern gradient */
  L.gradient = function (p) {
    return '<div style="' + SQ + 'background:linear-gradient(135deg,' + p.ac + ',' + mix(p.ac, p.ink, .45) + ');color:#FFFFFF;padding:46px 44px">' +
      '<div style="position:absolute;right:-80px;top:-80px;width:320px;height:320px;border-radius:50%;background:rgba(255,255,255,.12)"></div><div style="position:absolute;left:-60px;bottom:-60px;width:240px;height:240px;border-radius:50%;background:rgba(255,255,255,.08)"></div>' +
      '<div style="position:relative">' + ic(p.icon, p.logo ? 100 : 72, '#FFFFFF') + '<div style="font:800 64px/1.02 ' + JO + ';margin-top:22px;letter-spacing:-1px">' + T(p.head) + '</div>' +
      '<div style="font:500 26px/1.3 ' + JT + ';margin-top:16px;opacity:.92;max-width:470px">' + T(p.line) + '</div></div>' +
      '<div style="position:absolute;left:44px;right:44px;bottom:40px;display:flex;justify-content:space-between;align-items:flex-end;gap:16px">' + '<div style="min-width:0;flex:1">' + one('font:700 30px ' + JO, T(p.name)) + one('font:500 20px ' + JT + ';opacity:.85', T(p.web)) + '</div>' +
      '<div style="flex:none;background:#fff;color:' + p.ac + ';border-radius:999px;padding:12px 22px 8px">' + one('font:400 38px/1 ' + BE + ';letter-spacing:1px', T(p.phone)) + '</div></div></div>';
  };
  /* minimal line art */
  L.minimal = function (p) {
    return '<div style="' + SQ + 'background:' + p.bg + ';color:' + p.ink + ';padding:60px 56px;display:flex;flex-direction:column">' +
      ic(p.icon, p.logo ? 110 : 70, p.ac) + '<div style="flex:1"></div>' +
      one('font:300 64px/1.1 ' + JO + ';letter-spacing:2px', T(p.name)) + '<div style="width:60px;height:3px;background:' + p.ac + ';margin:20px 0"></div>' +
      one('font:500 24px ' + JT + ';letter-spacing:3px;opacity:.8', T(p.sub)) + one('font:500 26px ' + JT + ';letter-spacing:2px;margin-top:22px', T(p.phone)) + one('font:500 20px ' + JT + ';letter-spacing:2px;opacity:.65;margin-top:4px', T(p.web)) + '</div>';
  };
  /* laurel crest */
  L.crest = function (p) {
    var leaf = function (side) {
      var g = '';
      var sg = side ? -1 : 1;
      g += '<path d="M0,150 A150,150 0 0 ' + (side ? 1 : 0) + ' ' + (sg * 129.9) + ',-75" fill="none" stroke="' + p.ac + '" stroke-width="4"/>';
      for (var i = 0; i < 9; i++) {
        var a = sg * (175 - i * 13);
        g += '<g transform="rotate(' + a + ')"><ellipse cx="0" cy="-166" rx="9" ry="23" fill="' + p.ac + '" transform="rotate(' + (-sg * 38) + ' 0 -152)"/>' +
          '<ellipse cx="0" cy="-134" rx="8" ry="20" fill="' + mix(p.ac, p.bg, .25) + '" transform="rotate(' + (sg * 38) + ' 0 -148)"/></g>';
      }
      return g;
    };
    return '<div style="' + SQ + 'background:' + p.bg + ';color:' + p.ink + ';text-align:center">' +
      (p.logo ? '' : '<svg width="600" height="360" style="position:absolute;left:0;top:0"><g transform="translate(300 222) scale(.82)">' + leaf(0) + leaf(1) + '</g></svg>') +
      '<div style="position:relative;padding-top:' + (p.logo ? 120 : 168) + 'px">' + (p.logo ? '<div style="display:flex;justify-content:center">' + ic(p.icon, 130, p.ac) + '</div>' : one('font:500 100px/1.05 ' + CI + ';letter-spacing:4px;color:' + p.ac + ';padding:0 212px', T(p.mono))) +
      '<div style="padding:0 50px">' + one('font:600 30px ' + JO + ';letter-spacing:9px;margin-top:' + (p.logo ? 30 : 104) + 'px', T(p.name)) + one('font:400 30px ' + CO + ';margin-top:6px', T(p.sub)) +
      one('font:500 24px ' + JT + ';letter-spacing:3px;margin-top:16px', T(p.phone)) + '</div></div></div>';
  };
  /* comic starburst */
  L.burst = function (p) {
    var pts = [];
    for (var i = 0; i < 32; i++) { var r = i % 2 ? 150 : 200, a = Math.PI * i / 16; pts.push((300 + r * Math.cos(a)).toFixed(1) + ',' + (275 + r * Math.sin(a)).toFixed(1)); }
    return '<div style="' + SQ + 'background:' + p.bg + ';color:' + p.ink + ';text-align:center">' +
      '<svg width="600" height="520" style="position:absolute;inset:0"><polygon points="' + pts.join(' ') + '" fill="' + p.ac + '" stroke="' + p.ink + '" stroke-width="6"/></svg>' +
      '<div style="position:absolute;left:30px;right:30px;top:18px">' + one('font:700 20px ' + JO + ';letter-spacing:5px', T(p.kicker)) + '</div>' +
      '<div style="position:relative;padding:178px 150px 0;color:' + p.bg + '">' + one('font:400 120px/1 ' + A, T(p.offer)) + one('font:600 26px ' + JT, T(p.head)) + '</div>' +
      '<div style="position:absolute;left:0;right:0;bottom:22px;display:flex;align-items:center;justify-content:center;gap:12px;padding:0 30px">' + ic(p.icon, p.logo ? 64 : 44, p.ac) + one('min-width:0;font:400 32px/1.1 ' + DS, T(p.name)) + one('flex:none;font:600 26px ' + JT, T(p.phone)) + '</div></div>';
  };
  /* receipt */
  L.receipt = function (p) {
    var rows = (p.rows || []).slice(0, 4).map(function (r) { return '<div style="display:flex;justify-content:space-between;gap:10px"><span style="white-space:nowrap">' + T(r[0]) + '</span>' + one('min-width:0;text-align:right', T(r[1])) + '</div>'; }).join('');
    var zig = 'linear-gradient(-45deg,' + p.soft + ' 12px,transparent 0),linear-gradient(45deg,' + p.soft + ' 12px,transparent 0)';
    return '<div style="' + SQ + 'background:' + p.soft + ';display:flex;justify-content:center;padding-top:26px">' +
      '<div style="width:400px;height:550px;background:#FFFFFF;color:#222;padding:30px 32px;font:500 21px/1.55 \'DM Mono\',monospace;position:relative">' +
      '<div style="text-align:center">' + ic(p.icon, p.logo ? 80 : 54, p.ac) + '</div>' + one('text-align:center;font:400 34px/1.15 ' + A + ';text-transform:uppercase;margin-top:8px;color:' + p.ac, T(p.name)) +
      one('text-align:center;font-size:17px', T(p.sub)) + '<div style="border-top:2px dashed #999;margin:12px 0"></div>' + rows +
      '<div style="border-top:2px dashed #999;margin:12px 0"></div><div style="text-align:center;font:400 30px/1.2 ' + CA + '">' + T(p.head) + '</div>' + one('text-align:center;margin-top:6px', T(p.phone)) +
      '<div style="position:absolute;left:0;right:0;bottom:-12px;height:24px;background:' + zig + ';background-size:24px 24px"></div></div></div>';
  };
  /* hanging price tag */
  L.tag = function (p) {
    return '<div style="' + SQ + 'background:' + p.soft + '">' +
      '<svg width="600" height="600" style="position:absolute;inset:0"><path d="M300 0 C 300 60 330 70 330 110" stroke="' + p.ink + '" stroke-width="4" fill="none"/></svg>' +
      '<div style="position:absolute;left:80px;top:96px;width:440px;height:470px;background:' + p.bg + ';color:' + p.ink + ';clip-path:polygon(50% 0,100% 16%,100% 100%,0 100%,0 16%);transform:rotate(4deg);text-align:center;padding:96px 40px 0">' +
      '<div style="position:absolute;left:204px;top:24px;width:32px;height:32px;border-radius:50%;background:' + p.soft + '"></div>' +
      one('font:700 18px ' + JO + ';letter-spacing:6px;color:' + p.ac, T(p.kicker)) + one('font:400 120px/1 ' + A + ';color:' + p.ac + ';margin-top:6px', T(p.offer)) + one('font:600 26px ' + JT, T(p.head)) +
      '<div style="margin-top:18px;display:flex;justify-content:center">' + ic(p.icon, p.logo ? 70 : 50, p.ink) + '</div>' + one('font:400 32px/1.1 ' + DS + ';margin-top:8px', T(p.name)) + one('font:600 22px ' + JT, T(p.phone)) + '</div></div>';
  };
  /* map pin: find us */
  L.pin = function (p) {
    return '<div style="' + SQ + 'background:' + p.bg + ';color:' + p.ink + ';background-image:linear-gradient(' + rgba(p.ink, .06) + ' 2px,transparent 2px),linear-gradient(90deg,' + rgba(p.ink, .06) + ' 2px,transparent 2px);background-size:40px 40px;text-align:center;padding-top:30px">' +
      '<svg width="200" height="230" viewBox="0 0 64 74"><path d="M32 72S6 46 6 28a26 26 0 0 1 52 0c0 18-26 44-26 44z" fill="' + p.ac + '"/><circle cx="32" cy="28" r="16" fill="' + p.bg + '"/></svg>' +
      '<div style="position:absolute;left:220px;top:72px;width:160px;height:160px;display:grid;place-items:center">' + ic(p.icon, p.logo ? 120 : 76, p.ac) + '</div>' +
      '<div style="padding:0 40px">' + one('font:400 52px/1.1 ' + A + ';text-transform:uppercase', T(p.head)) + one('font:400 40px/1.1 ' + DS + ';margin-top:6px', T(p.name)) +
      '<div style="font:500 24px ' + JT + ';margin-top:8px">' + T(p.line) + '</div>' + one('font:400 46px/1 ' + BE + ';letter-spacing:2px;margin-top:10px;color:' + p.ac, T(p.phone)) + '</div></div>';
  };
  /* hours on a clock */
  L.clock = function (p) {
    var rows = (p.rows || []).slice(0, 4).map(function (r) { return '<div style="display:flex;justify-content:space-between;gap:10px;padding:6px 0;border-bottom:2px solid ' + rgba(p.ink, .12) + '"><b style="white-space:nowrap">' + T(r[0]) + '</b>' + one('min-width:0;text-align:right', T(r[1])) + '</div>'; }).join('');
    var ticks = '';
    for (var i = 0; i < 12; i++) ticks += '<rect x="58" y="6" width="4" height="12" rx="2" fill="' + p.bg + '" transform="rotate(' + i * 30 + ' 60 60)"/>';
    return '<div style="' + SQ + 'background:' + p.bg + ';color:' + p.ink + ';padding:40px 40px 0">' +
      '<div style="display:flex;align-items:center;gap:22px"><svg width="150" height="150" viewBox="0 0 120 120" style="flex:none"><circle cx="60" cy="60" r="58" fill="' + p.ac + '"/>' + ticks + '<path d="M60 60V26M60 60l24 14" stroke="' + p.bg + '" stroke-width="7" stroke-linecap="round"/><circle cx="60" cy="60" r="6" fill="' + p.bg + '"/></svg>' +
      '<div style="min-width:0;flex:1">' + one('font:400 44px/1.1 ' + DS, T(p.name)) + one('font:400 40px/1.1 ' + A + ';text-transform:uppercase;color:' + p.ac + ';margin-top:6px', T(p.head)) + '</div></div>' +
      '<div style="font:500 26px ' + JT + ';margin-top:20px">' + rows + '</div>' +
      '<div style="position:absolute;left:40px;right:40px;bottom:30px;display:flex;justify-content:space-between;gap:14px">' + one('font:400 46px/1 ' + BE + ';letter-spacing:1px;flex:none', T(p.phone)) + one('min-width:0;font:600 20px ' + JT + ';text-align:right;align-self:center', T(p.line)) + '</div></div>';
  };
  /* diner: checker floor and script */
  L.diner = function (p) {
    return '<div style="' + SQ + 'background:' + p.bg + ';color:' + p.ink + ';text-align:center">' +
      '<div style="position:absolute;left:0;right:0;bottom:0;height:150px;background:conic-gradient(' + p.ink + ' 25%,' + p.bg + ' 0 50%,' + p.ink + ' 0 75%,' + p.bg + ' 0) 0 0/50px 50px;opacity:.9"></div>' +
      '<div style="position:relative;padding:40px 40px 0">' + '<div style="display:inline-block;background:' + p.ac + ';color:' + p.bg + ';border-radius:999px;padding:8px 24px 5px">' + one('font:700 18px ' + JO + ';letter-spacing:6px', T(p.sub)) + '</div>' +
      one('font:italic 900 90px/1.1 ' + PL + ';color:' + p.ac + ';margin-top:14px;text-shadow:4px 4px 0 ' + p.ink, T(p.name)) +
      '<div style="font:500 26px ' + JT + ';margin-top:12px">' + T(p.line) + '</div>' +
      '<div style="display:inline-block;margin-top:18px;background:' + p.ink + ';color:' + p.bg + ';padding:10px 26px 4px;border-radius:12px">' + one('font:400 56px/1 ' + BE + ';letter-spacing:2px', T(p.phone)) + '</div></div></div>';
  };
  /* flowers in the corners */
  L.floral = function (p) {
    var bloom = function (x, y, s, rot) {
      var g = '<g transform="translate(' + x + ' ' + y + ') scale(' + s + ') rotate(' + rot + ')">';
      for (var i = 0; i < 5; i++) g += '<ellipse cx="0" cy="-16" rx="11" ry="17" fill="' + mix(p.ac, '#FFFFFF', .25) + '" transform="rotate(' + i * 72 + ')"/>';
      g += '<circle r="8" fill="' + mix(p.ac, '#F2B632', .5) + '"/>';
      for (var j = 0; j < 3; j++) g += '<ellipse cx="' + (30 + j * 14) + '" cy="' + (16 + j * 8) + '" rx="13" ry="6" fill="' + mix(p.ink, '#5E8C4E', .6) + '" opacity=".75" transform="rotate(' + (25 + j * 15) + ')"/>';
      return g + '</g>';
    };
    return '<div style="' + SQ + 'background:' + p.bg + ';color:' + p.ink + ';text-align:center;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:0 90px">' +
      '<svg width="600" height="600" style="position:absolute;inset:0">' + bloom(56, 56, 2.2, 20) + bloom(140, 26, 1.1, -10) + bloom(26, 140, 1, 60) + bloom(544, 544, 2.2, 200) + bloom(460, 574, 1.1, 170) + bloom(574, 460, 1, 240) + '</svg>' +
      '<div style="position:relative">' + one('font:700 19px ' + JO + ';letter-spacing:7px;color:' + p.ac, T(p.sub)) + one('font:400 96px/1.15 ' + DA + ';margin-top:12px', T(p.name)) +
      '<div style="font:400 34px/1.25 ' + CO + ';margin-top:12px">' + T(p.line) + '</div>' + one('font:500 30px ' + JT + ';letter-spacing:2px;margin-top:18px', T(p.phone)) + '</div></div>';
  };
  /* wave at the bottom */
  L.wave = function (p) {
    return '<div style="' + SQ + 'background:' + p.bg + ';color:' + p.ink + ';padding:44px 44px 0">' +
      '<svg width="600" height="250" viewBox="0 0 600 250" style="position:absolute;left:0;bottom:0"><path d="M0 70 C120 10 220 120 330 60 S520 20 600 60 V250 H0Z" fill="' + mix(p.ac, '#FFFFFF', .45) + '"/><path d="M0 110 C130 50 240 160 350 100 S530 60 600 100 V250 H0Z" fill="' + p.ac + '"/></svg>' +
      '<div style="position:relative;display:flex;align-items:center;gap:16px">' + ic(p.icon, p.logo ? 96 : 70, p.ac) + '<div style="min-width:0;flex:1">' + one('font:400 46px/1.1 ' + DS, T(p.name)) + one('font:700 17px ' + JO + ';letter-spacing:5px;color:' + p.ac, T(p.sub)) + '</div></div>' +
      '<div style="position:relative;font:400 66px/1.02 ' + A + ';text-transform:uppercase;margin-top:28px">' + T(p.head) + '</div>' +
      '<div style="position:absolute;left:44px;right:44px;bottom:36px;color:' + p.bg + ';display:flex;justify-content:space-between;align-items:flex-end;gap:14px">' + one('min-width:0;flex:1;font:600 22px ' + JT, T(p.line)) + one('flex:none;font:400 58px/1 ' + BE + ';letter-spacing:2px', T(p.phone)) + '</div></div>';
  };
  /* geometric pattern */
  L.geo = function (p) {
    var tri = 'linear-gradient(135deg,' + rgba(p.ac, .9) + ' 25%,transparent 25%) -40px 0/80px 80px,linear-gradient(225deg,' + rgba(p.ac, .55) + ' 25%,transparent 25%) -40px 0/80px 80px';
    return '<div style="' + SQ + 'background:' + tri + ',' + p.bg + ';color:' + p.ink + ';display:grid;place-items:center">' +
      '<div style="width:440px;background:' + p.bg + ';border:5px solid ' + p.ink + ';padding:36px 30px;text-align:center;box-shadow:12px 12px 0 ' + p.ink + '">' +
      '<div style="display:flex;justify-content:center">' + ic(p.icon, p.logo ? 100 : 70, p.ac) + '</div>' + one('font:400 54px/1.1 ' + A + ';text-transform:uppercase;margin-top:12px', T(p.name)) +
      one('font:700 16px ' + JO + ';letter-spacing:5px;color:' + p.ac, T(p.sub)) + '<div style="font:500 22px ' + JT + ';margin-top:12px">' + T(p.line) + '</div>' + one('font:400 52px/1 ' + BE + ';letter-spacing:2px;margin-top:12px', T(p.phone)) + '</div></div>';
  };
  /* playful blobs (kids, daycare, parties) */
  L.blobs = function (p) {
    var b = function (x, y, s, c) { return '<div style="position:absolute;left:' + x + 'px;top:' + y + 'px;width:' + s + 'px;height:' + s + 'px;background:' + c + ';border-radius:42% 58% 63% 37% / 41% 44% 56% 59%"></div>'; };
    return '<div style="' + SQ + 'background:' + p.bg + ';color:' + p.ink + ';text-align:center">' +
      b(-40, -30, 220, p.ac) + b(440, 40, 180, mix(p.ac, '#7ABBE0', .5)) + b(-30, 430, 200, mix(p.ac, '#F7C548', .6)) + b(420, 430, 230, p.soft) +
      '<div style="position:relative;padding:120px 60px 0">' + '<div style="display:flex;justify-content:center">' + ic(p.icon, p.logo ? 110 : 90, p.ink) + '</div>' +
      '<div style="font:400 74px/1.02 ' + A + ';margin-top:10px">' + T(p.head) + '</div>' + '<div style="font:500 26px/1.25 ' + JT + ';margin-top:12px">' + T(p.line) + '</div>' +
      one('font:400 34px/1.1 ' + DS + ';margin-top:14px', T(p.name)) + one('font:600 26px ' + JT, T(p.phone)) + '</div></div>';
  };
  /* sports jersey */
  L.jersey = function (p) {
    return '<div style="' + SQ + 'background:' + p.soft + ';color:' + p.bg + ';text-align:center">' +
      '<svg width="600" height="600" viewBox="0 0 600 600" style="position:absolute;inset:0"><path d="M190 60 L250 40 Q300 90 350 40 L410 60 L540 140 L490 250 L430 220 L430 570 L170 570 L170 220 L110 250 L60 140 Z" fill="' + p.ac + '" stroke="' + p.ink + '" stroke-width="6" stroke-linejoin="round"/></svg>' +
      '<div style="position:relative;padding:110px 190px 0">' + one('font:400 46px/1.1 ' + A + ';text-transform:uppercase;letter-spacing:3px', T(p.name)) + one('font:400 190px/1 ' + A, T(p.year || '27')) +
      one('font:700 17px ' + JO + ';letter-spacing:4px', T(p.sub)) + one('font:600 20px ' + JT + ';margin-top:8px', T(p.line)) + '</div></div>';
  };
  /* blueprint grid */
  L.blueprint = function (p) {
    return '<div style="' + SQ + 'background:#1E4E8C;background-image:linear-gradient(rgba(255,255,255,.12) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.12) 1px,transparent 1px),linear-gradient(rgba(255,255,255,.22) 2px,transparent 2px),linear-gradient(90deg,rgba(255,255,255,.22) 2px,transparent 2px);background-size:20px 20px,20px 20px,100px 100px,100px 100px;color:#FFFFFF;padding:44px">' +
      '<div style="border:3px solid #FFFFFF;height:100%;padding:28px 26px;position:relative">' + '<div style="display:flex;align-items:center;gap:14px">' + ic(p.icon, p.logo ? 90 : 64, '#FFFFFF') + '<div style="min-width:0;flex:1">' + one('font:400 42px/1.1 ' + A + ';text-transform:uppercase;letter-spacing:2px', T(p.name)) + one('font:500 16px \'DM Mono\',monospace;letter-spacing:3px', T(p.sub)) + '</div></div>' +
      '<div style="font:400 56px/1.05 ' + A + ';text-transform:uppercase;margin-top:28px;color:' + mix(p.ac, '#FFFFFF', .3) + '">' + T(p.head) + '</div>' + '<div style="font:500 20px/1.4 \'DM Mono\',monospace;margin-top:12px">' + T(p.line) + '</div>' +
      '<div style="position:absolute;left:26px;right:26px;bottom:20px;border-top:2px solid #fff;padding-top:12px;display:flex;justify-content:space-between;gap:12px;font:500 18px \'DM Mono\',monospace"><span>' + esc(def(p.since, 'LICENSED · INSURED')) + '</span>' + one('font:400 40px/1 ' + BE + ';letter-spacing:2px;flex:none', T(p.phone)) + '</div></div></div>';
  };
  /* barber-pole border */
  L.pole = function (p) {
    var stripes = 'repeating-linear-gradient(45deg,' + p.ac + ' 0 18px,#FFFFFF 18px 36px,' + mix(p.ac, '#13294B', .7) + ' 36px 54px,#FFFFFF 54px 72px)';
    return '<div style="' + SQ + 'background:' + stripes + ';padding:30px">' +
      '<div style="height:100%;background:' + p.bg + ';color:' + p.ink + ';text-align:center;padding:40px 36px 0;display:flex;flex-direction:column;align-items:center">' +
      ic(p.icon, p.logo ? 110 : 86, p.ac) + one('font:400 60px/1.1 ' + A + ';text-transform:uppercase;margin-top:12px;max-width:100%', T(p.name)) +
      one('font:700 17px ' + JO + ';letter-spacing:6px;color:' + p.ac + ';max-width:100%', T(p.sub)) + '<div style="font:500 24px ' + JT + ';margin-top:16px">' + T(p.line) + '</div>' +
      one('font:400 60px/1 ' + BE + ';letter-spacing:2px;margin-top:14px;max-width:100%', T(p.phone)) + '</div></div>';
  };
  /* paw prints all over */
  L.paws = function (p) {
    var paw = function (x, y, r) { return '<g transform="translate(' + x + ' ' + y + ') rotate(' + r + ')" fill="' + rgba(p.ac, .18) + '"><ellipse cx="0" cy="10" rx="13" ry="11"/><ellipse cx="-14" cy="-6" rx="5" ry="7"/><ellipse cx="-5" cy="-14" rx="5" ry="7"/><ellipse cx="6" cy="-14" rx="5" ry="7"/><ellipse cx="15" cy="-6" rx="5" ry="7"/></g>'; };
    var g = '';
    [[60, 70, -20], [520, 60, 25], [80, 520, 15], [540, 520, -30], [300, 40, 0], [40, 300, 40], [560, 300, -40]].forEach(function (a) { g += paw(a[0], a[1], a[2]); });
    return '<div style="' + SQ + 'background:' + p.bg + ';color:' + p.ink + ';text-align:center"><svg width="600" height="600" style="position:absolute;inset:0">' + g + '</svg>' +
      '<div style="position:relative;padding:80px 70px 0;display:flex;flex-direction:column;align-items:center">' + ic(p.icon, p.logo ? 140 : 130, p.ac) +
      one('font:400 60px/1.1 ' + DA + ';margin-top:10px;max-width:100%', T(p.name)) + one('font:700 17px ' + JO + ';letter-spacing:6px;color:' + p.ac + ';max-width:100%', T(p.sub)) +
      '<div style="font:500 24px ' + JT + ';margin-top:12px">' + T(p.line) + '</div>' + one('font:400 52px/1 ' + BE + ';letter-spacing:2px;margin-top:12px;max-width:100%', T(p.phone)) + '</div></div>';
  };
  /* art deco gold lines */
  L.deco = function (p) {
    var fan = '';
    for (var i = 0; i < 9; i++) fan += '<path d="M300 300 L' + (300 + 260 * Math.cos(Math.PI + i * Math.PI / 8)).toFixed(0) + ' ' + (300 + 260 * Math.sin(Math.PI + i * Math.PI / 8)).toFixed(0) + '" stroke="' + p.ac + '" stroke-width="2" opacity=".5"/>';
    return '<div style="' + SQ + 'background:' + p.bg + ';color:' + p.ink + ';text-align:center">' +
      '<svg width="600" height="600" style="position:absolute;inset:0">' + fan + '<rect x="24" y="24" width="552" height="552" fill="none" stroke="' + p.ac + '" stroke-width="3"/><rect x="36" y="36" width="528" height="528" fill="none" stroke="' + p.ac + '" stroke-width="1"/>' +
      '<path d="M24 120 L120 24 M576 120 L480 24 M24 480 L120 576 M576 480 L480 576" stroke="' + p.ac + '" stroke-width="3"/><circle cx="300" cy="300" r="70" fill="' + p.bg + '" stroke="' + p.ac + '" stroke-width="3"/></svg>' +
      '<div style="position:absolute;left:230px;top:230px;width:140px;height:140px;display:grid;place-items:center">' + (p.logo ? ic(p.icon, 110, p.ac) : one('font:500 64px/1 ' + CI + ';color:' + p.ac + ';max-width:120px', T(p.mono))) + '</div>' +
      '<div style="position:absolute;left:60px;right:60px;top:398px">' + one('font:600 34px ' + CI + ';letter-spacing:6px', T(p.name)) + one('font:400 28px ' + CO + ';margin-top:4px', T(p.sub)) + one('font:500 24px ' + JT + ';letter-spacing:3px;margin-top:10px;color:' + p.ac, T(p.phone)) + '</div></div>';
  };
  /* ribbon banner across */
  L.ribbon = function (p) {
    return '<div style="' + SQ + 'background:' + p.bg + ';color:' + p.ink + ';text-align:center;padding-top:50px">' +
      '<div style="display:flex;justify-content:center">' + ic(p.icon, p.logo ? 130 : 120, p.ac) + '</div>' +
      '<div style="position:relative;margin:26px -10px 0;height:110px">' + '<div style="position:absolute;left:0;top:22px;width:90px;height:90px;background:' + mix(p.ac, '#000000', .25) + ';clip-path:polygon(0 0,100% 0,100% 100%,0 100%,25% 50%)"></div><div style="position:absolute;right:0;top:22px;width:90px;height:90px;background:' + mix(p.ac, '#000000', .25) + ';clip-path:polygon(0 0,100% 0,75% 50%,100% 100%,0 100%)"></div>' +
      '<div style="position:absolute;left:50px;right:50px;top:0;height:92px;background:' + p.ac + ';color:' + p.bg + ';display:grid;place-items:center;padding:0 30px">' + one('font:400 56px/1 ' + A + ';text-transform:uppercase;letter-spacing:2px;max-width:100%', T(p.name)) + '</div></div>' +
      '<div style="padding:0 50px">' + one('font:700 18px ' + JO + ';letter-spacing:6px;margin-top:20px', T(p.sub)) + '<div style="font:500 24px ' + JT + ';margin-top:10px">' + T(p.line) + '</div>' + one('font:400 56px/1 ' + BE + ';letter-spacing:2px;margin-top:12px;color:' + p.ac, T(p.phone)) + '</div></div>';
  };
  /* reminder: big month and day */
  L.remind = function (p) {
    var hnd = p.hand || ['', ''];
    return '<div style="' + SQ + 'background:' + p.bg + ';color:' + p.ink + ';padding:40px 44px">' +
      '<div style="display:flex;align-items:center;gap:14px">' + ic(p.icon, p.logo ? 84 : 58, p.ac) + '<div style="min-width:0;flex:1">' + one('font:400 38px/1.1 ' + DS, T(p.name)) + one('font:700 16px ' + JO + ';letter-spacing:5px;color:' + p.ac, T(p.sub)) + '</div></div>' +
      '<div style="display:flex;gap:24px;align-items:center;margin-top:30px"><div style="width:200px;flex:none;border-radius:20px;overflow:hidden;box-shadow:0 8px 20px rgba(0,0,0,.15)"><div style="background:' + p.ac + ';color:' + p.bg + ';text-align:center;padding:10px 0 6px;font:400 34px ' + A + ';letter-spacing:3px">' + esc(def(p.month, 'NEXT')) + '</div>' +
      '<div style="background:#fff;color:#222;text-align:center;font:400 120px/1.1 ' + BE + ';height:150px;display:grid;place-items:center;padding-top:10px">' + (T(hnd[0]) || '&nbsp;') + '</div></div>' +
      '<div style="min-width:0;flex:1"><div style="font:italic 700 40px/1.1 ' + PL + '">' + T(p.head) + '</div><div style="font:400 40px/1.1 ' + CA + ';color:#1F3B73;margin-top:12px;border-bottom:2px solid ' + p.ink + '">' + (T(hnd[1]) || '&nbsp;') + '</div></div></div>' +
      '<div style="position:absolute;left:0;right:0;bottom:0;height:80px;background:' + p.ac + ';color:' + p.bg + ';display:flex;align-items:center;justify-content:space-between;gap:16px;padding:0 44px">' + one('min-width:0;flex:1;font:600 22px ' + JT, T(p.line)) + one('flex:none;font:400 44px/1 ' + BE + ';letter-spacing:1px;padding-top:6px', T(p.phone)) + '</div></div>';
  };
  /* checklist with boxes */
  L.checklist = function (p) {
    var rows = (p.rows || []).slice(0, 6).map(function (r) {
      return '<div style="display:flex;align-items:center;gap:14px;padding:8px 0"><span style="width:34px;height:34px;border:3px solid ' + p.ac + ';border-radius:8px;flex:none"></span>' + one('min-width:0;flex:1;font:500 26px ' + JT, T(r[0])) + (r[1] ? one('flex:none;max-width:40%;font:400 26px ' + CA + ';color:' + p.ac, T(r[1])) : '') + '</div>';
    }).join('');
    return '<div style="' + SQ + 'background:' + p.bg + ';color:' + p.ink + ';padding:38px 44px 0">' +
      one('font:400 52px/1.1 ' + A + ';text-transform:uppercase', T(p.head)) + one('font:600 20px ' + JT + ';opacity:.8;margin-top:2px', T(p.line)) + '<div style="margin-top:12px">' + rows + '</div>' +
      '<div style="position:absolute;left:44px;right:44px;bottom:30px;display:flex;align-items:center;gap:14px;border-top:3px solid ' + p.ac + ';padding-top:14px">' + ic(p.icon, p.logo ? 70 : 46, p.ac) + one('min-width:0;flex:1;font:400 32px/1.1 ' + DS, T(p.name)) + one('flex:none;font:700 26px ' + JT, T(p.phone)) + '</div></div>';
  };
  /* circle badge with photo inside */
  L.circlephoto = function (p) {
    return '<div style="' + SQ + 'background:' + p.bg + ';color:' + p.ink + ';text-align:center;padding-top:36px">' +
      '<div style="margin:0 auto;width:330px;height:330px;border-radius:50%;background:' + photoBg(p) + ';border:10px solid ' + p.ac + ';box-shadow:0 10px 26px rgba(0,0,0,.2)"></div>' +
      '<div style="padding:0 40px">' + one('font:400 52px/1.1 ' + A + ';text-transform:uppercase;margin-top:18px', T(p.name)) + one('font:700 17px ' + JO + ';letter-spacing:6px;color:' + p.ac, T(p.sub)) + one('font:600 28px ' + JT + ';margin-top:10px', T(p.phone)) + '</div></div>';
  };
  /* polaroid of the business */
  L.snapshot = function (p) {
    return '<div style="' + SQ + 'background:' + p.ac + ';color:' + p.bg + '">' +
      '<div style="position:absolute;left:60px;top:40px;width:420px;background:#fff;padding:18px 18px 0;transform:rotate(-3deg);box-shadow:0 14px 30px rgba(0,0,0,.28)"><div style="height:300px;background:' + photoBg(p) + '"></div>' + one('font:400 40px/1.2 ' + CA + ';color:#2B2118;text-align:center;padding:10px 0 12px', T(String(p.head || '').replace(/\n/g, ' '))) + '</div>' +
      '<div style="position:absolute;right:36px;bottom:26px;left:110px;text-align:right">' + one('font:400 38px/1.1 ' + DS, T(p.name)) + one('font:400 46px/1 ' + BE + ';letter-spacing:2px', T(p.phone)) + '</div></div>';
  };
  /* stripes and a box (sale, construction) */
  L.stripes = function (p) {
    return '<div style="' + SQ + 'background:repeating-linear-gradient(-45deg,' + p.ac + ' 0 30px,' + mix(p.ac, '#FFFFFF', .25) + ' 30px 60px);display:grid;place-items:center">' +
      '<div style="width:470px;background:' + p.bg + ';color:' + p.ink + ';padding:34px 30px;text-align:center;border-radius:10px;box-shadow:0 16px 36px rgba(0,0,0,.25)">' +
      one('font:700 18px ' + JO + ';letter-spacing:6px;color:' + p.ac, T(p.kicker)) + one('font:400 110px/1 ' + A, T(p.offer)) + one('font:600 26px ' + JT, T(p.head)) +
      '<div style="display:flex;align-items:center;justify-content:center;gap:12px;margin-top:16px">' + ic(p.icon, p.logo ? 64 : 44, p.ac) + one('min-width:0;font:400 30px/1.1 ' + DS, T(p.name)) + '</div>' + one('font:400 46px/1 ' + BE + ';letter-spacing:2px;margin-top:6px', T(p.phone)) + '</div></div>';
  };
  /* seasonal wreath thank-you */
  L.wreath = function (p) {
    var g = '';
    for (var i = 0; i < 26; i++) { var a = i * Math.PI / 13, x = 300 + 200 * Math.cos(a), y = 250 + 200 * Math.sin(a); g += '<ellipse cx="' + x.toFixed(1) + '" cy="' + y.toFixed(1) + '" rx="26" ry="11" fill="' + (i % 2 ? '#2E6B3A' : '#3E8E41') + '" transform="rotate(' + (a * 180 / Math.PI + 90).toFixed(0) + ' ' + x.toFixed(1) + ' ' + y.toFixed(1) + ')"/>'; if (i % 4 === 0) g += '<circle cx="' + x.toFixed(1) + '" cy="' + y.toFixed(1) + '" r="9" fill="#C62828"/>'; }
    return '<div style="' + SQ + 'background:' + p.bg + ';color:' + p.ink + ';text-align:center"><svg width="600" height="600" style="position:absolute;inset:0">' + g + '<path d="M270 440 l30 -20 l30 20 l-10 60 l-20 -30 l-20 30z" fill="#C62828"/></svg>' +
      '<div style="position:absolute;left:150px;right:150px;top:150px">' + one('font:400 70px/1.1 ' + DA + ';color:' + p.ac, T(p.head)) + '<div style="font:500 22px/1.3 ' + JT + ';margin-top:10px">' + T(p.line) + '</div>' + one('font:400 32px/1.1 ' + DS + ';margin-top:14px', T(p.name)) + one('font:600 20px ' + JT, T(p.phone)) + '</div></div>';
  };
  /* menu card: specials with prices */
  L.menu = function (p) {
    var rows = (p.rows || []).slice(0, 5).map(function (r) {
      return '<div style="display:flex;align-items:baseline;gap:8px;padding:6px 0;font:500 26px ' + JT + '"><span style="white-space:nowrap">' + T(r[0]) + '</span><span style="flex:1;border-bottom:3px dotted ' + rgba(p.ink, .35) + ';transform:translateY(-6px)"></span>' + one('flex:none;max-width:45%;font:700 26px ' + JT + ';color:' + p.ac, T(r[1])) + '</div>';
    }).join('');
    return '<div style="' + SQ + 'background:' + p.bg + ';color:' + p.ink + ';padding:36px 46px 0">' +
      '<div style="text-align:center">' + one('font:italic 700 58px/1.15 ' + PL, T(p.name)) + one('font:700 17px ' + JO + ';letter-spacing:6px;color:' + p.ac + ';margin-top:4px', T(p.sub)) + '</div>' +
      '<div style="text-align:center;margin:10px 0 4px;color:' + p.ac + '">— ' + esc(String(p.head || '').replace(/\n/g, ' ')) + ' —</div>' + rows +
      bottomBar(p, T(p.line), T(p.phone), 80) + '</div>';
  };
  /* scalloped seal */
  L.seal = function (p) {
    var pts = [];
    for (var i = 0; i < 48; i++) { var r = i % 2 ? 236 : 250, a = Math.PI * i / 24; pts.push((300 + r * Math.cos(a)).toFixed(1) + ',' + (300 + r * Math.sin(a)).toFixed(1)); }
    return '<div style="' + SQ + 'background:' + p.soft + ';color:' + p.bg + ';text-align:center">' +
      '<svg width="600" height="600" style="position:absolute;inset:0"><polygon points="' + pts.join(' ') + '" fill="' + p.ac + '"/><circle cx="300" cy="300" r="212" fill="none" stroke="' + p.bg + '" stroke-width="3" stroke-dasharray="6 8"/></svg>' +
      '<div style="position:relative;padding:118px 120px 0;display:flex;flex-direction:column;align-items:center">' + ic(p.icon, p.logo ? 110 : 92, p.bg) +
      one('font:400 54px/1.1 ' + A + ';text-transform:uppercase;letter-spacing:2px;margin-top:10px;max-width:100%', T(p.name)) + one('font:700 16px ' + JO + ';letter-spacing:5px;max-width:100%', T(p.sub)) +
      one('font:400 44px/1 ' + BE + ';letter-spacing:2px;margin-top:12px;max-width:100%', T(p.phone)) + '</div></div>';
  };
  /* big illustration on top, name below (bright, friendly) */
  L.hero = function (p) {
    return '<div style="' + SQ + 'background:' + p.bg + ';color:' + p.ink + ';text-align:center">' +
      '<div style="height:330px;background:' + p.soft + ';display:grid;place-items:center;border-radius:0 0 50% 50% / 0 0 18% 18%">' + ic(p.icon, p.logo ? 230 : 250, p.ac) + '</div>' +
      '<div style="padding:0 40px">' + one('font:400 56px/1.1 ' + A + ';text-transform:uppercase;margin-top:22px', T(p.name)) + one('font:700 17px ' + JO + ';letter-spacing:6px;color:' + p.ac, T(p.sub)) +
      one('font:400 58px/1 ' + BE + ';letter-spacing:2px;margin-top:12px', T(p.phone)) + '</div></div>';
  };
  /* two-tone card: top colour block with headline, bottom contact */
  L.duo = function (p) {
    return '<div style="' + SQ + 'background:' + p.bg + ';color:' + p.ink + '">' +
      '<div style="height:330px;background:' + p.ac + ';color:' + p.bg + ';padding:40px 40px 0;position:relative">' + one('font:700 18px ' + JO + ';letter-spacing:6px', T(p.sub)) +
      '<div style="font:400 84px/1 ' + A + ';text-transform:uppercase;margin-top:18px">' + T(p.head) + '</div>' +
      '<div style="position:absolute;right:30px;bottom:-60px;width:150px;height:150px;border-radius:50%;background:' + p.bg + ';display:grid;place-items:center;box-shadow:0 8px 20px rgba(0,0,0,.18)">' + ic(p.icon, p.logo ? 120 : 92, p.ac) + '</div></div>' +
      '<div style="padding:30px 200px 0 40px"><div style="font:500 24px/1.3 ' + JT + '">' + T(p.line) + '</div></div>' +
      '<div style="position:absolute;left:40px;right:40px;bottom:34px">' + one('font:400 36px/1.1 ' + DS, T(p.name)) + one('font:400 54px/1 ' + BE + ';letter-spacing:2px;color:' + p.ac, T(p.phone)) + '</div></div>';
  };
  /* event: elegant invitation card with border */
  L.invite = function (p) {
    return '<div style="' + SQ + 'background:' + p.soft + ';display:grid;place-items:center">' +
      '<div style="width:500px;height:500px;background:' + p.bg + ';color:' + p.ink + ';border:2px solid ' + p.ac + ';outline:8px solid ' + p.bg + ';outline-offset:-20px;box-shadow:0 14px 34px rgba(0,0,0,.15);text-align:center;padding:66px 50px 0">' +
      one('font:600 16px ' + JO + ';letter-spacing:7px;color:' + p.ac, T(p.sub)) + one('font:400 74px/1.15 ' + DA + ';margin-top:20px', T(p.head)) +
      '<div style="display:flex;align-items:center;justify-content:center;gap:12px;margin:14px 0;color:' + p.ac + '"><span style="height:1px;width:70px;background:' + p.ac + '"></span>' + star(14, p.ac) + '<span style="height:1px;width:70px;background:' + p.ac + '"></span></div>' +
      one('font:500 30px ' + CI + ';letter-spacing:5px', T(p.date)) + '<div style="font:400 28px/1.25 ' + CO + ';margin-top:10px">' + T(p.line) + '</div></div></div>';
  };
  /* event: big photo circle with names */
  L.photocircle = function (p) {
    return '<div style="' + SQ + 'background:' + p.bg + ';color:' + p.ink + ';text-align:center;padding-top:30px">' +
      '<div style="margin:0 auto;width:340px;height:340px;border-radius:50%;background:' + photoBg(p) + ';box-shadow:0 0 0 6px ' + p.bg + ',0 0 0 9px ' + p.ac + '"></div>' +
      '<div style="padding:0 40px">' + one('font:400 62px/1.15 ' + DA + ';margin-top:18px', T(p.head)) + one('font:600 20px ' + JO + ';letter-spacing:7px;color:' + p.ac + ';margin-top:2px', T(p.line)) + '</div></div>';
  };
  /* event: film strip of three photo frames */
  L.film = function (p) {
    var holes = 'repeating-linear-gradient(90deg,#fff 0 14px,transparent 14px 30px)';
    return '<div style="' + SQ + 'background:' + p.bg + ';color:' + p.ink + ';text-align:center;padding-top:48px">' +
      '<div style="background:#1A1A1A;padding:22px 0;transform:rotate(-3deg);margin:0 -20px"><div style="height:10px;background:' + holes + '"></div>' +
      '<div style="height:240px;margin:12px 30px;background:' + photoBg(p) + '"></div><div style="height:10px;background:' + holes + '"></div></div>' +
      '<div style="padding:0 40px">' + one('font:400 64px/1.15 ' + DA + ';margin-top:24px', T(p.head)) + one('font:600 20px ' + JO + ';letter-spacing:7px;color:' + p.ac, T(p.line)) + '</div></div>';
  };
  /* event: big monogram with date banner */
  L.monodate = function (p) {
    return '<div style="' + SQ + 'background:' + p.bg + ';color:' + p.ink + ';text-align:center;padding-top:60px">' +
      one('font:600 17px ' + JO + ';letter-spacing:8px;color:' + p.ac + ';padding:0 50px', T(p.sub)) +
      '<div style="font:500 170px/1 ' + CI + ';margin-top:26px;color:' + p.ac + '">' + esc(String(p.a || '').charAt(0)) + '<span style="font-size:.45em;vertical-align:middle;margin:0 10px;color:' + p.ink + '">&amp;</span>' + esc(String(p.b || '').charAt(0)) + '</div>' +
      '<div style="padding:0 50px">' + one('font:600 30px ' + JO + ';letter-spacing:8px;margin-top:20px', T(String(p.a || '').toUpperCase()) + ' &amp; ' + T(String(p.b || '').toUpperCase())) +
      '<div style="display:inline-block;margin-top:18px;background:' + p.ac + ';color:' + p.bg + ';padding:10px 28px 6px">' + one('font:500 26px ' + CI + ';letter-spacing:5px', T(p.date)) + '</div>' + one('font:400 28px ' + CO + ';margin-top:12px', T(p.place)) + '</div></div>';
  };
  /* event: confetti-free bold typography */
  L.bigtype = function (p) {
    return '<div style="' + SQ + 'background:' + p.ac + ';color:' + p.bg + ';padding:50px 46px">' +
      one('font:700 20px ' + JO + ';letter-spacing:8px', T(p.sub)) + '<div style="font:400 128px/.92 ' + A + ';text-transform:uppercase;margin-top:20px">' + T(p.head) + '</div>' +
      '<div style="position:absolute;left:46px;right:46px;bottom:44px;border-top:4px solid ' + p.bg + ';padding-top:14px;display:flex;justify-content:space-between;gap:12px">' + one('min-width:0;flex:1;font:500 24px ' + JT, T(p.line)) + one('flex:none;font:600 24px ' + JO + ';letter-spacing:3px', T(p.date)) + '</div></div>';
  };
})();
