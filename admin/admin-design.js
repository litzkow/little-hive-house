/* Little Hive House admin: the studio designs in an order (packages made in the site's design studio).
   - make(): draws the design into the 1200 px print picture (assets/designer.js toPng: 2 in at 600 dpi, exactly like
     the site shows it), saves it at prints/<order>/<item>-<stamp>.png and has the server make the print sheet with it.
     The order page calls it by itself the first time it opens an order whose design has no print picture yet.
   - edit(): the owners change anything before printing: colors, every word, the drawing, the logo, the photo. Saving
     makes the print picture and the print sheet again (the customer's original stays in item.designOriginal).
   Borders (the paper around each magnet) keep their own place on the order page ("Border colours"). */
(function () {
  'use strict';
  var A = window.LHHAdmin, D = window.LHHDesigner;
  if (!A || !D) return;
  var h = A.h, esc = h.esc;
  function T(en, pt) { return h.LANG && h.LANG() === 'pt' ? pt : en; }

  var SDK = 'https://www.gstatic.com/firebasejs/10.14.1/firebase-storage-compat.js', storeP = null;
  function storage() {
    if (!storeP) storeP = new Promise(function (res, rej) {
      if (window.firebase && firebase.storage) return res(firebase.storage());
      var s = document.createElement('script'); s.src = SDK;
      s.onload = function () { res(firebase.storage()); }; s.onerror = function () { storeP = null; rej(new Error(T('Couldn’t load the file tools. Check the internet.', 'Não deu para carregar. Confira a internet.'))); };
      document.head.appendChild(s);
    });
    return storeP;
  }
  function urlOf(path) { return storage().then(function (s) { return s.ref(path).getDownloadURL(); }); }
  function put(path, blob) { return storage().then(function (s) { return s.ref(path).put(blob, { contentType: blob.type || 'image/png' }); }).then(function () { return path; }); }
  function stamp() { return Date.now().toString(36); }

  /* the customer's (or the owners') choices, ready to draw: their files become links */
  function choices(dg) {
    var ch = { colors: dg.colors || null, text: dg.text || {}, icon: dg.icon || '', url: dg.url || '' };
    var jobs = [];
    if (dg.logo) jobs.push(urlOf(dg.logo).then(function (u) { ch.logo = u; }));
    if (dg.photo) jobs.push(urlOf(dg.photo).then(function (u) { ch.photo = u; }));
    else if (dg.stock) ch.photo = '/assets/stock/' + dg.stock + '.webp';
    return Promise.all(jobs).then(function () { return ch; });
  }

  /* draw, save, and have the server make the print sheet with it */
  function make(o, index, design, edited) {
    var d = D.get(design.slug);
    if (!d) return Promise.reject(new Error(T('This design is not on the site anymore.', 'Esse design não está mais no site.')));
    return choices(design).then(function (ch) { return D.toPng(d, ch, 1200); }).then(function (blob) {
      return put('prints/' + o.id + '/' + index + '-' + stamp() + '.png', blob);
    }).then(function (path) {
      var face = { item: index, path: path };
      if (edited) face.design = design;
      return h.call('adminPrintSheet', { orderId: o.id, rebuild: true, faces: [face] });
    }).then(function (res) { return h.refreshOrder(o.id).then(function () { return res; }); });
  }

  /* ---------------------------------------------------------------- the editor */
  var LABEL = { name: ['Name', 'Nome'], sub: ['Small line', 'Linha pequena'], head: ['Headline', 'Título'], line: ['Message', 'Mensagem'], phone: ['Phone', 'Telefone'],
    web: ['Website or @', 'Site ou @'], since: ['Side note', 'Nota lateral'], kicker: ['Label', 'Etiqueta'], offer: ['Offer', 'Oferta'], mono: ['Initials', 'Iniciais'],
    a: ['First name', 'Primeiro nome'], b: ['Second name', 'Segundo nome'], date: ['Date', 'Data'], place: ['Place', 'Local'], year: ['Year', 'Ano'],
    school: ['School or team', 'Escola ou time'], hand0: ['Written on line 1', 'Escrito na linha 1'], hand1: ['Written on line 2', 'Escrito na linha 2'] };
  function label(k) {
    if (LABEL[k]) return T(LABEL[k][0], LABEL[k][1]);
    var m = /^items(\d)$/.exec(k); if (m) return T('Service ', 'Serviço ') + (+m[1] + 1);
    m = /^rows(\d)([ab])$/.exec(k); if (m) return T('Line ', 'Linha ') + (+m[1] + 1) + (m[2] === 'b' ? T(', right', ', direita') : '');
    return k;
  }

  function edit(o, index) {
    var it = (o.items || [])[index], dg = it && it.design;
    var d = dg && D.get(dg.slug);
    if (!d) { h.toast(T('This design can’t be opened here.', 'Esse design não abre aqui.'), true); return; }
    var work = JSON.parse(JSON.stringify(dg));
    work.text = work.text || {};
    var files = {};   /* new logo / photo picked here: {logo: blob, photo: blob} */
    var dlg = document.createElement('dialog'); dlg.className = 'modal dz-edit'; dlg.setAttribute('translate', 'no');
    var words = Object.keys(d.text).map(function (k) {
      var v = k in work.text ? work.text[k] : d.text[k], multi = /\n/.test(v) || k === 'head' || k === 'line';
      return '<label class="field"><span>' + esc(label(k)) + '</span>' + (multi ? '<textarea class="input" rows="2" data-k="' + k + '">' + esc(v) + '</textarea>' : '<input class="input" data-k="' + k + '" value="' + esc(v) + '">') + '</label>';
    }).join('');
    var pals = Object.keys(D.palettes).map(function (k) { var p = D.palettes[k]; return '<button type="button" class="dzp" data-pal="' + k + '" title="' + k + '" style="background:conic-gradient(' + p.ac + ' 0 33%,' + p.bg + ' 0 66%,' + p.ink + ' 0)"></button>'; }).join('');
    var icons = Object.keys(D.icons).map(function (k) { return '<button type="button" class="dzi" data-icon="' + k + '" title="' + k + '"><svg viewBox="0 0 64 64" width="26" height="26">' + D.icons[k].split('{c}').join('currentColor') + '</svg></button>'; }).join('');
    var photoLayout = /^(photo|wphoto|polaroid)$/.test(d.layout);
    var c0 = work.colors || d.colors;
    dlg.innerHTML = '<form method="dialog" class="in" style="max-width:980px">' +
      '<h2>' + T('Edit before printing', 'Editar antes de imprimir') + ' · ' + esc(d.title) + '</h2>' +
      '<div class="dz-ed"><div><div class="dz-ed-prev" data-prev style="width:100%;max-width:380px;aspect-ratio:1;border-radius:10px;overflow:hidden;box-shadow:0 6px 20px rgba(0,0,0,.2)"></div>' +
      '<p class="small muted">' + T('Exactly what goes on the print sheet. The paper around it (border colour) is set on the order page.', 'Exatamente o que vai para a folha de impressão. A cor da borda (o papel em volta) fica na página do pedido.') + '</p></div>' +
      '<div class="dz-ed-ctl">' +
      '<h3>' + T('Colors', 'Cores') + '</h3><div class="dz-ed-pals"><button type="button" class="btn btn-ghost btn-sm" data-orig>' + T('Original', 'Original') + '</button>' + pals + '</div>' +
      '<div class="row" style="gap:12px;flex-wrap:wrap;margin:8px 0"><label class="small">' + T('Background', 'Fundo') + ' <input type="color" data-c="bg" value="' + esc(c0.bg) + '"></label><label class="small">' + T('Text', 'Texto') + ' <input type="color" data-c="ink" value="' + esc(c0.ink) + '"></label><label class="small">' + T('Accent', 'Destaque') + ' <input type="color" data-c="ac" value="' + esc(c0.ac) + '"></label></div>' +
      '<h3>' + T('Words', 'Textos') + '</h3><div class="dz-ed-words">' + words +
      (/^(qr|eqr)$/.test(d.layout) ? '<label class="field"><span>' + T('QR link', 'Link do QR') + '</span><input class="input" data-url value="' + esc(work.url || '') + '" placeholder="https://"></label>' : '') + '</div>' +
      '<h3>' + T('Logo', 'Logo') + '</h3><div class="row" style="gap:10px;flex-wrap:wrap"><label class="btn btn-ghost btn-sm">' + T('New logo', 'Trocar logo') + '<input type="file" accept="image/*" data-file="logo" hidden></label>' +
      '<button type="button" class="btn btn-ghost btn-sm" data-nologo>' + T('No logo (use a drawing)', 'Sem logo (usar desenho)') + '</button></div>' +
      '<div class="dz-ed-icons">' + icons + '</div>' +
      (photoLayout ? '<h3>' + T('Photo', 'Foto') + '</h3><label class="btn btn-ghost btn-sm">' + T('New photo', 'Trocar foto') + '<input type="file" accept="image/*" data-file="photo" hidden></label>' +
        '<div class="dz-ed-stock">' + D.stock.map(function (n) { return '<button type="button" data-stock="' + n + '"><img src="/assets/stock/t/' + n + '.webp" alt="" loading="lazy" width="64" height="64"></button>'; }).join('') + '</div>' : '') +
      '</div></div>' +
      '<p class="small err" data-err hidden></p>' +
      '<div class="row end"><button class="btn btn-ghost" value="cancel">' + T('Cancel', 'Cancelar') + '</button><button type="button" class="btn btn-honey" data-save>' + T('Save and make the print file', 'Salvar e gerar o arquivo de impressão') + '</button></div></form>';
    document.body.appendChild(dlg);
    var prev = dlg.querySelector('[data-prev]'), ch = null;
    function redraw() {
      var c = { colors: work.colors || null, text: work.text, icon: work.icon || '', url: work.url || '', logo: files.logoUrl || ch.logo || '', photo: files.photoUrl || ch.photo || '' };
      if (work.noLogo) c.logo = '';
      D.paint(prev, d, c);
    }
    choices(dg).then(function (c) { ch = c; redraw(); }, function () { ch = {}; redraw(); });
    dlg.addEventListener('input', function (e) {
      var t = e.target;
      if (t.hasAttribute('data-k')) { work.text[t.getAttribute('data-k')] = t.value; redraw(); }
      else if (t.hasAttribute('data-url')) { work.url = t.value.trim(); redraw(); }
      else if (t.hasAttribute('data-c')) { var c = work.colors || { bg: d.colors.bg, ink: d.colors.ink, ac: d.colors.ac }; work.colors = { bg: c.bg, ink: c.ink, ac: c.ac }; work.colors[t.getAttribute('data-c')] = t.value.toUpperCase(); redraw(); }
    });
    dlg.addEventListener('change', function (e) {
      var t = e.target, k = t.getAttribute('data-file'), f = t.files && t.files[0];
      if (!k || !f) return;
      files[k] = f; files[k + 'Url'] = URL.createObjectURL(f);
      if (k === 'logo') work.noLogo = false;
      if (k === 'photo') delete work.stock;
      redraw();
    });
    dlg.addEventListener('click', function (e) {
      var t = e.target, b;
      if ((b = t.closest('.dzp'))) { var p = D.palettes[b.getAttribute('data-pal')]; work.colors = { bg: p.bg, ink: p.ink, ac: p.ac }; redraw(); return; }
      if (t.closest('[data-orig]')) { delete work.colors; redraw(); return; }
      if ((b = t.closest('.dzi'))) { work.icon = b.getAttribute('data-icon'); work.noLogo = true; files.logo = null; files.logoUrl = ''; redraw(); return; }
      if (t.closest('[data-nologo]')) { work.noLogo = true; files.logo = null; files.logoUrl = ''; redraw(); return; }
      if ((b = t.closest('[data-stock]'))) { work.stock = b.getAttribute('data-stock'); files.photo = null; files.photoUrl = '/assets/stock/' + work.stock + '.webp'; delete work.photo; redraw(); return; }
      if (t.closest('[data-save]')) save(t.closest('[data-save]'));
    });
    dlg.addEventListener('close', function () { dlg.remove(); });
    if (dlg.showModal) dlg.showModal(); else dlg.setAttribute('open', '');

    function save(btn) {
      var err = dlg.querySelector('[data-err]'); err.hidden = true;
      h.busy(btn, true, T('Making the print file…', 'Gerando o arquivo…'));
      var jobs = [];
      if (files.logo) jobs.push(put('prints/' + o.id + '/logo-' + index + '-' + stamp() + '.png', files.logo).then(function (p) { work.logo = p; }));
      if (files.photo) jobs.push(put('prints/' + o.id + '/photo-' + index + '-' + stamp() + '.jpg', files.photo).then(function (p) { work.photo = p; delete work.stock; }));
      Promise.all(jobs).then(function () {
        if (work.noLogo) delete work.logo;
        delete work.noLogo;
        var text = {};
        Object.keys(work.text).forEach(function (k) { if (work.text[k] !== d.text[k]) text[k] = work.text[k]; });
        work.text = text;
        return make(o, index, work, true);
      }).then(function () {
        h.busy(btn, false); dlg.close();
        h.toast(T('Saved. The print sheet was made again with the new design.', 'Salvo. A folha de impressão foi feita de novo com o design novo.'));
        h.route();
      }).catch(function (e) {
        h.busy(btn, false);
        err.textContent = h.friendlyError ? h.friendlyError(e) : String(e && e.message || e); err.hidden = false;
      });
    }
  }

  window.LHHAdminDesign = { make: make, edit: edit };
})();
