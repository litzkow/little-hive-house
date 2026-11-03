/* Little Hive House admin: Growth plan. What each sale leaves, how many sales each goal takes and how far the shop can grow,
   always with today's prices (functions/catalog.json) and the costs in Settings (reports.js planProducts / planSoFar).
   The screen picks its own language (T(en, pt)) and is marked translate="no". */
(function () {
  'use strict';
  var A = window.LHHAdmin, S = A.S, R = A.R, h = A.h, V = A.VIEWS;
  var esc = h.esc, money = h.money, icon = h.icon;
  function T(en, pt) { return h.LANG() === 'pt' ? pt : en; }
  function n0(v) { return isFinite(v) ? Math.round(v).toLocaleString(h.LANG() === 'pt' ? 'pt-BR' : 'en-US') : '—'; }

  var catalog = null, loading = false;
  function loadCatalog() {
    if (catalog || loading) return;
    loading = true;
    fetch('../functions/catalog.json', { cache: 'no-cache' }).then(function (r) { return r.ok ? r.json() : null; })
      .then(function (c) { catalog = c && c.rules && c.packs ? c : R.PLAN_CATALOG; })
      .catch(function () { catalog = R.PLAN_CATALOG; })
      .then(function () { loading = false; if (A.parseHash().view === 'plan') h.route(); });
  }

  function name(p) {
    if (p.kind === 'design') return p.n === 1 ? T('1 design magnet', '1 ímã de design') : T(p.n + ' design magnets', p.n + ' ímãs de design');
    return T('Photo pack of ' + p.n, 'Pacote de ' + p.n + ' fotos');
  }
  function priceNote(p) {
    var bits = [];
    if (p.price < p.list) bits.push(p.volPct ? T(p.volPct + '% volume discount', p.volPct + '% de desconto por quantidade') : T('bundle price', 'preço do combo'));
    bits.push(p.shipCharged ? T('+ ' + money(p.shipCharged) + ' shipping', '+ ' + money(p.shipCharged) + ' de frete') : T('free shipping', 'frete grátis'));
    return bits.join(' · ');
  }
  function mixName(p) { return p.kind === 'design' ? T('Designs, ' + p.n + ' at a time', 'Design, de ' + p.n + ' em ' + p.n) : T('Packs of ' + p.n + ' photos', 'Pacotes de ' + p.n + ' fotos'); }
  function card(title, sub, body) {
    return '<section class="card gap-top"><div class="card-head"><div><h2>' + esc(title) + '</h2>' + (sub ? '<p class="sub">' + sub + '</p>' : '') + '</div></div>' + body + '</section>';
  }
  function table(headRow, rows) {
    return '<div class="table-wrap"><table class="t compact"><thead><tr>' + headRow.map(function (c, i) { return '<th' + (i ? ' class="num"' : '') + '>' + esc(c) + '</th>'; }).join('') +
      '</tr></thead><tbody>' + rows.map(function (r) { return '<tr>' + r.map(function (c, i) { return i ? '<td class="num" data-label="' + esc(headRow[i]) + '"><div class="v">' + c + '</div></td>' : '<td>' + c + '</td>'; }).join('') + '</tr>'; }).join('') + '</tbody></table></div>';
  }

  V.plan = function () {
    if (!catalog) loadCatalog();
    var s = S.settings, P = R.planProducts(s, catalog || R.PLAN_CATALOG), so = R.planSoFar(S.orders, s);
    var by = {}; P.forEach(function (p) { by[p.key] = p; });
    var mixes = [by.design3 || P[0], by.pack9 || P[0], by.pack50 || P[P.length - 1]].filter(Boolean);
    var perToday = (by.pack9 || P[0]).perMagnet, perBig = 1.40;

    /* 1. paying back */
    var payback = '<div class="tiles">' +
      h.tile(T('Put into the shop', 'Investido na loja'), money(so.invested), T('Change it in Settings', 'Mude em Configurações'), false, '#settings') +
      h.tile(T('Profit so far', 'Lucro até agora'), '<span class="' + (so.profit < 0 ? 'neg' : '') + '">' + h.signedMoney(so.profit) + '</span>',
        so.orders ? T(n0(so.orders) + ' orders · ' + n0(so.magnets) + ' magnets', n0(so.orders) + ' pedidos · ' + n0(so.magnets) + ' ímãs') : T('No sales yet', 'Nenhuma venda ainda'), true) +
      h.tile(T('Still to pay back', 'Falta recuperar'), money(so.left), T(Math.round(so.paidPct) + '% paid back', Math.round(so.paidPct) + '% recuperado')) +
      h.tile(T('Real profit per magnet', 'Lucro real por ímã'), so.perMagnet == null ? '—' : h.signedMoney(so.perMagnet), T('From your real orders', 'Dos pedidos de verdade')) +
      '</div><div class="plan-bar" role="img" aria-label="' + esc(T(Math.round(so.paidPct) + '% paid back', Math.round(so.paidPct) + '% recuperado')) + '"><span style="width:' + so.paidPct + '%"></span></div>';

    /* 2. each sale */
    var each = table([T('Product', 'Produto'), T('Customer pays', 'Cliente paga'), T('Left over', 'Sobra'), T('Per magnet', 'Por ímã')],
      P.map(function (p) {
        var costs = T('costs: magnets + packaging ' + money(p.make) + ', label ' + money(p.label) + ', Stripe ' + money(p.fee),
                      'custos: ímãs + embalagem ' + money(p.make) + ', etiqueta ' + money(p.label) + ', Stripe ' + money(p.fee));
        return ['<b>' + esc(name(p)) + '</b><span class="plan-why">' + esc(priceNote(p)) + '</span><span class="plan-why">' + esc(costs) + '</span>', money(p.total),
                '<b class="' + (p.left < 0 ? 'neg' : '') + '">' + h.signedMoney(p.left) + '</b>', h.signedMoney(p.perMagnet)];
      }));

    /* 3. goals */
    var goals = [[0, T('Pay back the investment', 'Recuperar o investimento')], [500, T('Then profit $500', 'Depois lucrar US$ 500')], [1000, T('Then profit $1,000', 'Depois lucrar US$ 1.000')],
      [2500, T('Then profit $2,500', 'Depois lucrar US$ 2.500')], [5000, T('Then profit $5,000', 'Depois lucrar US$ 5.000')], [10000, T('Then profit $10,000', 'Depois lucrar US$ 10.000')],
      [25000, T('Then profit $25,000', 'Depois lucrar US$ 25.000')]];
    var goalRows = goals.filter(function (g) { return g[0] || so.left > 0; }).map(function (g) {
      return ['<b>' + esc(g[1]) + '</b>'].concat(mixes.map(function (p) {
        var k = R.salesFor(so.left + g[0], p);
        return isFinite(k) ? n0(k) + '<span class="plan-why">' + T(n0(k * p.n) + ' magnets', n0(k * p.n) + ' ímãs') + '</span>' : '—';
      }));
    });
    var goalTable = table([T('Goal', 'Meta')].concat(mixes.map(mixName)), goalRows);

    /* 4. per month */
    var fixed = s.monthlyFixedCosts;
    var monthRows = [30, 60, 100, 250, 500, 1000, 2000].map(function (q) {
      return ['<b>' + T(n0(q) + ' magnets', n0(q) + ' ímãs') + '</b>'].concat(mixes.map(function (p) {
        var prof = p.perMagnet * q - fixed, months = prof > 0 && so.left > 0 ? Math.ceil(so.left / prof) : null;
        return '<b class="' + (prof < 0 ? 'neg' : '') + '">' + h.signedMoney(prof) + '</b>' +
          (months ? '<span class="plan-why">' + (months === 1 ? T('paid back in 1 month', 'recupera em 1 mês') : T('paid back in ' + months + ' months', 'recupera em ' + months + ' meses')) + '</span>' : '');
      }));
    });
    var monthTable = table([T('Magnets a month', 'Ímãs por mês')].concat(mixes.map(mixName)), monthRows);

    /* 5. how far it can grow */
    var phases = [
      [10000, T('The two of you at home with 1 or 2 manual presses. Customers every day from Etsy, the site and ads.', 'Vocês dois em casa, com 1 ou 2 prensas manuais. Clientes todo dia pelo Etsy, pelo site e por anúncios.')],
      [20000, T('An electric or air press, a bigger printer, 1 helper, a room just for making, shipping in batches.', 'Prensa elétrica ou pneumática, impressora maior, 1 ajudante, um espaço só para produzir e envio em lote.')],
      [30000, T('A small workshop: 2 or 3 helpers, several presses, big orders (weddings, businesses) every week.', 'Uma pequena fábrica: 2 ou 3 ajudantes, várias prensas e pedidos grandes (casamentos, empresas) toda semana.')],
      [50000, T('Wholesale to gift and tourist shops, business orders, part of the making done by others.', 'Atacado para lojas de presente e turismo, pedidos de empresas e parte da produção terceirizada.')]
    ];
    var growRows = phases.map(function (ph) {
      var a = Math.ceil((ph[0] + fixed) / perToday), b = Math.ceil((ph[0] + fixed) / perBig);
      return ['<b>' + T(money(ph[0]).replace('.00', '') + ' a month', 'US$ ' + n0(ph[0]) + ' por mês') + '</b><span class="plan-need">' + esc(ph[1]) + '</span>',
              n0(a) + '<span class="plan-why">' + T(n0(a / 30) + ' a day', n0(a / 30) + ' por dia') + '</span>', n0(b) + '<span class="plan-why">' + T(n0(b / 30) + ' a day', n0(b / 30) + ' por dia') + '</span>'];
    });
    var growTable = table([T('Profit a month', 'Lucro por mês'), T('Magnets a month today', 'Ímãs/mês hoje'), T('With team and ads', 'Com equipe e anúncios')], growRows);
    var ideas = [
      T('Gift boxes of $40 to $60 (magnets, card, stickers, stationery): more profit per order for the same packing work.', 'Caixas de presente de US$ 40 a 60 (ímãs, cartão, adesivos, papelaria): mais lucro por pedido com o mesmo trabalho de embalar.'),
      T('Stationery (stickers, cards, bookmarks): same printer, same art.', 'Papelaria (adesivos, cartões, marcadores): a mesma impressora e as mesmas artes.'),
      T('Other magnet shapes (round, bigger, acrylic): a higher price for the same art.', 'Outros formatos de ímã (redondo, maior, acrílico): preço maior pela mesma arte.'),
      T('Big orders and wholesale: a few customers bringing hundreds of magnets.', 'Pedidos grandes e atacado: poucos clientes trazendo centenas de ímãs.'),
      T('Customers who come back (holidays, seasonal collections) cost less than new ones.', 'Clientes que voltam (datas e coleções da estação) custam menos que clientes novos.')
    ];

    var html = '<div class="plan" translate="no">' +
      '<div class="page-head"><div><p class="eyebrow">' + esc(T('Reports', 'Relatórios')) + '</p><h1>' + esc(T('Growth plan', 'Projeção')) + '</h1><p class="sub">' +
      esc(T('What each sale leaves, how many sales each goal takes and how far the shop can grow. Uses today’s prices and the costs in Settings, before income tax.',
            'Quanto sobra em cada venda, quantas vendas cada meta precisa e até onde a loja pode crescer. Usa os preços de hoje e os custos das Configurações, antes do imposto de renda.')) +
      '</p></div><div class="actions"><a class="btn btn-ghost btn-sm" href="#settings">' + icon('settings') + esc(T('Costs', 'Custos')) + '</a></div></div>' +
      payback +
      card(T('1. What each sale leaves', '1. Quanto sobra em cada venda'),
        esc(T('Costs from Settings: ' + money(s.magnetUnitCost) + ' a magnet, ' + money(s.packagingCost) + ' packaging, ' + money(s.defaultLabelCost) + ' label, Stripe ' + s.stripePct + '% + ' + money(s.stripeFixed) + '.',
              'Custos das Configurações: ' + money(s.magnetUnitCost) + ' por ímã, ' + money(s.packagingCost) + ' de embalagem, ' + money(s.defaultLabelCost) + ' de etiqueta, Stripe ' + s.stripePct + '% + ' + money(s.stripeFixed) + '.')), each) +
      card(T('2. How many sales to get there', '2. Quantas vendas para chegar lá'),
        esc(so.left > 0 ? T('Each column is selling only that way. Counted from today: first paying back the investment, then the profit of the goal.', 'Cada coluna supõe vender só daquele jeito. Conta a partir de hoje: primeiro recuperar o investimento, depois o lucro da meta.')
                        : T('The shop has paid itself back. Each column is selling only that way.', 'A loja já se pagou. Cada coluna supõe vender só daquele jeito.')), goalTable) +
      card(T('3. A month: what X magnets leave', '3. Por mês: quanto sobra vendendo X ímãs'),
        esc(fixed ? T('After the ' + money(fixed) + ' of fixed costs a month.', 'Já tirando os ' + money(fixed) + ' de custos fixos do mês.') : T('Three ways to sell the same number of magnets.', 'Três jeitos de vender a mesma quantidade de ímãs.')), monthTable) +
      card(T('4. How far it can grow', '4. Até onde dá para crescer'),
        esc(T('Today about ' + money(perToday) + ' is left per magnet. With more volume it drops to about ' + money(perBig) + ': paid helpers, ads, space and better machines. A month is 30 days.',
              'Hoje sobram uns ' + money(perToday) + ' por ímã. Com mais volume cai para uns ' + money(perBig) + ': ajudante pago, anúncios, espaço e máquinas melhores. O mês tem 30 dias.')),
        growTable + '<h3 class="plan-h3">' + esc(T('What grows it most: the value of each order', 'O que mais faz crescer: o valor de cada pedido')) + '</h3><ul class="plan-list">' +
        ideas.map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('') + '</ul><p class="small muted">' +
        esc(T('Suggested order: pay back the investment, reach $1,000 to $2,000 a month, then reinvest testing one new product at a time.', 'Ordem sugerida: recuperar o investimento, chegar a US$ 1 a 2 mil por mês e reinvestir testando um produto novo por vez.')) + '</p>') +
      '</div>';
    return { title: T('Growth plan', 'Projeção'), html: html };
  };
})();
