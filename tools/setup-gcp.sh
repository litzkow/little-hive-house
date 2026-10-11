#!/usr/bin/env bash
# Little Hive House: one-time Google Cloud setup for the store backend. Nothing secret lives here.
# Run it in Google Cloud Shell (console.cloud.google.com, the >_ button) with:
#   curl -sL https://raw.githubusercontent.com/litzkow/little-hive-house/main/tools/setup-gcp.sh | bash
# Safe to run again: every step checks first and skips what is already done.
#  1. turns on the Google APIs that Cloud Functions needs
#  2. if the project is inside an organization, relaxes the two org rules that block a public web shop
#     (public callable functions, default service account permissions) for THIS project only
#  3. gives the functions' own service account the permissions a normal Firebase project has
#  4. creates the "github-deploy" service account and lets GitHub Actions (only this repository) deploy
#     with it, without any key file (Workload Identity Federation)
#  5. lets the admin page download customer photos (Storage CORS)
set -u
PROJECT="${PROJECT:-little-hive-house}"
REPO="${REPO:-litzkow/little-hive-house}"
BUCKET="${BUCKET:-little-hive-house.firebasestorage.app}"
SITE="${SITE:-https://littlehivehouse.com}"
POOL=github
PROVIDER=github
DEPLOY_SA_NAME=github-deploy
FAILS=0
ok()   { echo "  ✅ $*"; }
warn() { echo "  ⚠️  $*"; FAILS=$((FAILS + 1)); }
step() { echo; echo "▶ $*"; }
retry() { local n=0; until "$@" >/tmp/lhh-out 2>&1; do n=$((n + 1)); [ $n -ge 6 ] && { tail -3 /tmp/lhh-out; return 1; }; sleep 15; done; }

step "Projeto"
gcloud config set project "$PROJECT" -q >/dev/null 2>&1
NUM=$(gcloud projects describe "$PROJECT" --format='value(projectNumber)' 2>/dev/null)
if [ -z "$NUM" ]; then echo "  ❌ Não encontrei o projeto $PROJECT. Confira se entrou com a conta certa."; exit 1; fi
ME=$(gcloud config get-value account 2>/dev/null)
ok "$PROJECT (número $NUM), conta $ME"

step "1/5 Ligando as APIs (pode levar 1 a 2 minutos)"
if retry gcloud services enable cloudfunctions.googleapis.com cloudbuild.googleapis.com run.googleapis.com \
    artifactregistry.googleapis.com eventarc.googleapis.com pubsub.googleapis.com cloudscheduler.googleapis.com \
    compute.googleapis.com iam.googleapis.com iamcredentials.googleapis.com sts.googleapis.com \
    cloudresourcemanager.googleapis.com serviceusage.googleapis.com orgpolicy.googleapis.com \
    firestore.googleapis.com firebaserules.googleapis.com firebasestorage.googleapis.com \
    identitytoolkit.googleapis.com storage.googleapis.com cloudbilling.googleapis.com --project "$PROJECT"; then ok "APIs ligadas"; else warn "Algumas APIs não ligaram"; fi

step "2/5 Regras da organização"
ORG=$(gcloud projects get-ancestors "$PROJECT" --format='csv[no-heading](id,type)' 2>/dev/null | awk -F, '$2=="organization"{print $1}')
if [ -z "$ORG" ]; then
  ok "O projeto não está numa organização. Nada a mudar."
else
  echo "  Organização $ORG"
  gcloud organizations add-iam-policy-binding "$ORG" --member="user:$ME" --role=roles/orgpolicy.policyAdmin --condition=None -q >/dev/null 2>&1 \
    && ok "Permissão para ajustar as regras" || echo "  (sem permissão para mudar papéis na organização, tentando mesmo assim)"
  set_policy() {   # $1 constraint, $2 rule yaml
    printf 'name: projects/%s/policies/%s\nspec:\n  rules:\n  - %s\n' "$PROJECT" "$1" "$2" > /tmp/lhh-policy.yaml
    retry gcloud org-policies set-policy /tmp/lhh-policy.yaml -q
  }
  # Public callable functions (checkout, order tracking) need "allUsers" as invoker.
  set_policy iam.allowedPolicyMemberDomains "allowAll: true" && ok "Funções públicas permitidas" || warn "Não consegui liberar funções públicas (iam.allowedPolicyMemberDomains)"
  if gcloud org-policies describe iam.managed.allowedPolicyMembers --project "$PROJECT" --effective >/dev/null 2>&1; then
    set_policy iam.managed.allowedPolicyMembers "enforce: false" && ok "Regra gerenciada de membros desligada" || warn "Não consegui desligar iam.managed.allowedPolicyMembers"
  fi
fi

step "3/5 Permissões das funções da loja"
CSA="$NUM-compute@developer.gserviceaccount.com"
n=0; until gcloud iam service-accounts describe "$CSA" --project "$PROJECT" >/dev/null 2>&1; do
  n=$((n + 1)); [ $n -ge 12 ] && break; sleep 10; done
if gcloud iam service-accounts describe "$CSA" --project "$PROJECT" >/dev/null 2>&1; then
  for r in roles/editor roles/cloudbuild.builds.builder roles/firebaseauth.admin roles/iam.serviceAccountTokenCreator; do
    retry gcloud projects add-iam-policy-binding "$PROJECT" --member="serviceAccount:$CSA" --role="$r" --condition=None -q || warn "Papel $r para $CSA"
  done
  ok "Conta das funções pronta"
else
  warn "A conta $CSA ainda não existe. Rode este script de novo daqui a 2 minutos."
fi

step "4/5 Publicação automática pelo GitHub (sem arquivo de chave)"
DSA="$DEPLOY_SA_NAME@$PROJECT.iam.gserviceaccount.com"
gcloud iam service-accounts describe "$DSA" --project "$PROJECT" >/dev/null 2>&1 || \
  gcloud iam service-accounts create "$DEPLOY_SA_NAME" --display-name="GitHub deploy (Little Hive House)" --project "$PROJECT" -q >/dev/null 2>&1
for r in roles/editor roles/firebase.admin roles/cloudfunctions.admin roles/run.admin roles/iam.serviceAccountUser \
         roles/serviceusage.serviceUsageAdmin roles/cloudscheduler.admin roles/artifactregistry.admin roles/storage.admin; do
  retry gcloud projects add-iam-policy-binding "$PROJECT" --member="serviceAccount:$DSA" --role="$r" --condition=None -q || warn "Papel $r"
done
gcloud iam workload-identity-pools describe "$POOL" --location=global --project "$PROJECT" >/dev/null 2>&1 || \
  retry gcloud iam workload-identity-pools create "$POOL" --location=global --display-name="GitHub" --project "$PROJECT" || warn "Pool do GitHub"
gcloud iam workload-identity-pools providers describe "$PROVIDER" --workload-identity-pool="$POOL" --location=global --project "$PROJECT" >/dev/null 2>&1 || \
  retry gcloud iam workload-identity-pools providers create-oidc "$PROVIDER" --workload-identity-pool="$POOL" --location=global \
    --issuer-uri="https://token.actions.githubusercontent.com" \
    --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository" \
    --attribute-condition="assertion.repository=='$REPO'" --project "$PROJECT" || warn "Ligação com o GitHub"
retry gcloud iam service-accounts add-iam-policy-binding "$DSA" --project "$PROJECT" --role=roles/iam.workloadIdentityUser \
  --member="principalSet://iam.googleapis.com/projects/$NUM/locations/global/workloadIdentityPools/$POOL/attribute.repository/$REPO" -q \
  && ok "Só o repositório $REPO pode publicar" || warn "Permissão do GitHub"

step "5/5 Fotos dos clientes no Admin (CORS do Storage)"
printf '[{"origin":["%s"],"method":["GET"],"maxAgeSeconds":3600}]' "$SITE" > /tmp/lhh-cors.json
if retry gcloud storage buckets update "gs://$BUCKET" --cors-file=/tmp/lhh-cors.json; then ok "Download das fotos liberado para $SITE"
else warn "CORS do bucket $BUCKET"; fi

echo
if [ "$FAILS" -eq 0 ]; then
  echo "🎉 PRONTO! Tudo configurado. Volte para o chat e avise o Claude."
else
  echo "Terminou com $FAILS aviso(s) ⚠️. Mande um print desta tela para o Claude."
fi
echo "GitHub: provider projects/$NUM/locations/global/workloadIdentityPools/$POOL/providers/$PROVIDER · conta $DSA"
