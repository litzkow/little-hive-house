# Ligar a loja (fazer uma vez só)

**Importante:** nunca cole chaves secretas (`sk_live_…`, `sk_test_…`, `whsec_…`, `re_…`, a Consumer Key/Secret do USPS, a chave do Shippo, o `UNSUBSCRIBE_SECRET` ou o arquivo `.json` da conta de serviço) em chats, e-mails, mensagens ou no código. Elas vão **só** no secret `FUNCTIONS_ENV` do GitHub (parte 4).

Enquanto a parte 1 não estiver pronta, o site continua funcionando como hoje ("Checkout opens soon").

## 1. Firebase

1. Entre em https://console.firebase.google.com com a conta Google da loja.
2. Clique em **Adicionar projeto** e use o nome `little-hive-house`. Anote o **ID do projeto** que aparece embaixo do nome.
3. Pode desligar o Google Analytics.
4. Engrenagem → **Uso e faturamento** → mude para o plano **Blaze** (paga só o que passar do grátis; a loja fica no grátis).
5. Crie um alerta de gasto: https://console.cloud.google.com/billing → **Orçamentos e alertas** → **Criar orçamento** → US$ 5 → alertas em 50%, 90% e 100%.
6. **Authentication** → **Começar** → **Método de login** → ative **E-mail/senha**.
7. Ainda em **Método de login**, ative também **Anônimo** (é o que deixa visitantes enviarem fotos).
8. **Authentication** → **Configurações** → **Domínios autorizados** → **Adicionar domínio** → `littlehivehouse.com`.
9. **Firestore Database** → **Criar banco de dados** → local **us-east1** → **modo de produção**.
10. **Storage** → **Começar** → **modo de produção** → mesma região (**us-east1**).
11. Engrenagem → **Configurações do projeto** → **Seus apps** → ícone **Web** (`</>`) → apelido `site` → **Registrar app** (não marque Hosting).
12. Copie `apiKey`, `authDomain`, `projectId`, `storageBucket` e `appId` para o arquivo `assets/firebase-config.js` e publique. Esses valores não são secretos.

## 2. Stripe (pagamentos)

1. Crie a conta em https://dashboard.stripe.com e preencha os dados do negócio e do banco.
2. Para testar primeiro, ligue o **Modo de teste** (botão no topo).
3. **Desenvolvedores** → **Chaves de API** → copie a **Chave secreta** (`sk_test_…` no teste, `sk_live_…` de verdade). Guarde para a parte 4.
4. **Desenvolvedores** → **Webhooks** → **Adicionar endpoint**.
5. URL do endpoint: `https://us-east1-little-hive-house.cloudfunctions.net/stripeWebhook` (troque `little-hive-house` pelo ID do projeto, se for diferente). Depois da parte 4, o endereço certo também aparece em Firebase → **Functions** → `stripeWebhook`.
6. Em **Selecionar eventos**, marque só: `checkout.session.completed`, `checkout.session.expired`, `charge.refunded`, `charge.dispute.created`.
7. Salve, clique em **Revelar** no **Segredo de assinatura** e copie (`whsec_…`). Guarde para a parte 4.

## 3. Resend (e-mails)

1. Crie a conta em https://resend.com.
2. **Domains** → **Add Domain** → `littlehivehouse.com`.
3. Copie os registros DNS que o Resend mostrar para onde o domínio está registrado e clique em **Verify**.
4. **API Keys** → **Create API Key** → permissão **Sending access** → copie (`re_…`). Guarde para a parte 4.

## 3b. USPS (rastreamento automático, grátis)

Com isso, depois que você digita o número de rastreio no Admin, o cliente recebe sozinho os e-mails "saiu para entrega" e "entregue".

1. Abra https://developers.usps.com e clique em **Sign Up** (ou **Log In**, se já tiver conta de empresa no USPS).
2. Crie a conta com os dados da loja e confirme o e-mail que o USPS mandar.
3. No portal, vá em **Apps** → **Add App**.
4. Nome do app: `Little Hive House`.
5. Na lista de APIs, marque **Tracking** e salve.
6. Abra o app criado e veja **Consumer Key** e **Consumer Secret** (clique em mostrar).
7. Não copie para chat nem e-mail. Elas vão direto no `FUNCTIONS_ENV` (passo 4.6): Consumer Key em `USPS_CLIENT_ID`, Consumer Secret em `USPS_CLIENT_SECRET`.
8. Se **Tracking** não aparecer na lista, peça acesso pelo próprio portal. Enquanto isso, o rastreio fica manual (você marca "entregue" no Admin) e o lembrete diário continua chegando.

## 3c. Shippo (opcional: UPS, FedEx e DHL)

Só precisa se você mandar pacotes por UPS, FedEx ou DHL. Sem isso, esses continuam manuais.

1. Crie a conta grátis em https://goshippo.com.
2. **Settings** → **Advanced** → **API**.
3. Clique em **Generate Token** na parte **Live** (começa com `shippo_live_`).
4. Ela vai no `FUNCTIONS_ENV` (passo 4.6) como `SHIPPO_API_KEY`. Não cole em chat.

## 3d. Dois valores para os e-mails

1. `MAIL_POSTAL_ADDRESS`: o endereço postal da loja. A lei dos EUA (CAN-SPAM) exige um endereço físico nos e-mails de marketing. Pode ser uma caixa postal (PO Box) ou caixa de correio privada, se não quiserem mostrar o endereço de casa.
2. `UNSUBSCRIBE_SECRET`: uma senha longa e aleatória que assina os links de "descadastrar".
3. Para criar o `UNSUBSCRIBE_SECRET`: use o gerador de senhas do iPhone ou do Chrome e faça uma senha de uns 40 caracteres, só letras e números.
4. Defina o `UNSUBSCRIBE_SECRET` antes de abrir a loja e não troque depois (trocar invalida os links de descadastro já enviados).

## 4. GitHub (publicação automática)

1. Firebase → engrenagem → **Configurações do projeto** → **Contas de serviço** → **Gerar nova chave privada**. Baixa um arquivo `.json`.
2. Abra https://console.cloud.google.com/iam-admin/iam (projeto da loja), ache a conta `firebase-adminsdk-…` e clique no lápis.
3. Adicione os papéis: **Editor**, **Administrador do Cloud Functions**, **Administrador do Cloud Run** e **Usuário da conta de serviço**. Salve.
4. No GitHub, no repositório do site: **Settings** → **Secrets and variables** → **Actions** → **New repository secret**.
5. Nome `FIREBASE_SERVICE_ACCOUNT`, valor: todo o conteúdo do arquivo `.json`. Salve e depois apague o arquivo do computador.
6. Nome `FUNCTIONS_ENV`, valor: o texto abaixo, trocando os `…` pelas suas chaves e e-mails:

```
STRIPE_SECRET_KEY=sk_test_…
STRIPE_WEBHOOK_SECRET=whsec_…
RESEND_API_KEY=re_…
ADMIN_EMAILS=email-do-thiago@…,email-da-karina@…
SITE_URL=https://littlehivehouse.com
MAIL_FROM="Little Hive House <hello@littlehivehouse.com>"
MAIL_ADMIN=support@littlehivehouse.com
MAIL_POSTAL_ADDRESS="Little Hive House, PO Box …, Sharpsburg, GA 30277"
UNSUBSCRIBE_SECRET=…
USPS_CLIENT_ID=…
USPS_CLIENT_SECRET=…
SHIPPO_API_KEY=
```

   - `SHIPPO_API_KEY` pode ficar vazio (parte 3c é opcional).
   - Se faltar `USPS_CLIENT_ID` ou `USPS_CLIENT_SECRET`, a loja funciona, só o rastreio automático fica desligado.

7. Só se o ID do projeto não for `little-hive-house`: na aba **Variables**, crie `FIREBASE_PROJECT` com o ID certo.
8. **Actions** → **Deploy store backend (Firebase)** → **Run workflow**. Espere ficar verde (uns 5 minutos).
9. Se a primeira vez der erro de permissão, espere 5 minutos e rode de novo (o Google demora para liberar as permissões novas).

## 4b. Fotos dos clientes no Admin (CORS do Storage, uma vez só)

Sem isso, o botão **Download all (.zip)** do Admin não consegue baixar as fotos.

1. Firebase → **Storage** → copie o nome do bucket que aparece no topo (algo como `little-hive-house.firebasestorage.app`, sem o `gs://`).
2. Abra https://console.cloud.google.com com a conta da loja e escolha o projeto da loja no topo.
3. Clique no ícone **Ativar o Cloud Shell** (`>_`, no canto de cima à direita) e espere o terminal abrir embaixo.
4. Cole a linha abaixo, trocando `NOME-DO-BUCKET` pelo nome do passo 1, e aperte Enter:

```
echo '[{"origin":["https://littlehivehouse.com"],"method":["GET"],"maxAgeSeconds":3600}]' > cors.json && gsutil cors set cors.json gs://NOME-DO-BUCKET
```

5. Se pedir autorização, clique em **Autorizar**.
6. Para conferir, cole `gsutil cors get gs://NOME-DO-BUCKET` e aperte Enter: tem que aparecer `https://littlehivehouse.com`.

## 5. Primeiro acesso de admin

1. Abra https://littlehivehouse.com/account.html e crie sua conta com o e-mail que está em `ADMIN_EMAILS`. Façam isso logo, antes de divulgar a loja.
2. Abra https://littlehivehouse.com/admin/ e toque em **Activate admin access**.
3. A Karina faz o mesmo com a conta dela.
4. Observação: o acesso de admin vale para conta com senha mesmo sem o e-mail confirmado. Por isso as contas de vocês têm que ser criadas primeiro (o Firebase só aceita uma conta por e-mail).

## 5b. Admin no celular (app "Hive Admin")

No iPhone:

1. Abra https://littlehivehouse.com/admin/ no **Safari**.
2. Entre com seu e-mail e senha.
3. Toque no botão **Compartilhar** (quadrado com seta para cima).
4. Toque em **Adicionar à Tela de Início** e depois em **Adicionar**.
5. O ícone de colmeia "Hive Admin" aparece na tela. Abra por ele daqui pra frente.

No Android:

1. Abra https://littlehivehouse.com/admin/ no **Chrome**.
2. Entre com seu e-mail e senha.
3. Toque no menu **⋮** (três pontinhos).
4. Toque em **Instalar app** (ou **Adicionar à tela inicial**).

O app guarda só as telas no celular. Os pedidos sempre carregam na hora e não ficam salvos no aparelho. As mesmas instruções estão em Admin → **Settings** → **Install on your phone**.

## 6. Testar e virar a chave

1. Com as chaves de teste, compre algo no site com o cartão `4242 4242 4242 4242`, qualquer data futura e qualquer CVC.
2. Confira: o pedido aparece no Admin como **LHH-1001** e chegam os e-mails de confirmação e de pedido novo.
3. Teste um reembolso parcial pelo Admin.
4. Para vender de verdade: desligue o Modo de teste no Stripe e refaça os passos 2.3 a 2.7 (o webhook de verdade tem outro `whsec_…`).
5. Atualize o secret `FUNCTIONS_ENV` com `sk_live_…` e o novo `whsec_…` e rode o workflow de novo (passo 4.8).
6. Opcional: crie o cupom `WELCOME10` em Admin → Discounts. O e-mail de boas-vindas só fala dele se ele existir.
7. Teste o rastreio: marque um pedido como enviado no Admin com um número de rastreio USPS de verdade.
8. Em até 2 horas, abra o pedido no Admin: deve aparecer o status do USPS e "Checked automatically".
9. Se nada aparecer depois de 4 horas: Firebase → **Functions** → `trackShipments` → **Logs**, e veja a mensagem (normalmente é a Consumer Key/Secret errada).
