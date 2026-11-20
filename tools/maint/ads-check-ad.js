"use strict";
/* Anúncios: o estado real no Meta de cada impulso ativo (anúncio, conjunto e campanha): análise, entrega, orçamento, problemas. */
const { Firestore } = require("@google-cloud/firestore");
const db = new Firestore({ projectId: process.env.PROJECT || "little-hive-house" });
const say = (s) => console.log(`::warning title=anuncio::${String(s).replace(/\n/g, " ").slice(0, 900)}`);
(async () => {
  const meta = ((await db.collection("ads").doc("auth").get()).data() || {}).meta;
  const st = (await db.collection("ads").doc("state").get()).data() || {};
  const cfg = (await db.collection("ads").doc("config").get()).data() || {};
  say(`config: teto $${cfg.monthCap} · auto ${cfg.auto} · canais ${JSON.stringify(cfg.channels || {})} · regras ${JSON.stringify(cfg.rules || {})}`);
  const V = "v26.0";
  const get = async (id, fields) => { const r = await fetch(`https://graph.facebook.com/${V}/${id}?fields=${fields}&access_token=${encodeURIComponent(meta.token)}`); return r.json(); };
  say(`conjunto compartilhado: ${st.adsetId || "-"} · $${st.adsetDaily || 0} · ${st.adsetStatus || ""} · próximo Reel: ${JSON.stringify(st.nextReel || null)}`);
  for (const [id, b] of Object.entries(st.boosts || {})) {
    if (b.status !== "active") continue;
    const ad = await get(b.adId, "name,status,effective_status,configured_status,issues_info,ad_review_feedback,created_time");
    say(`anúncio ${b.adId} (post ${id}): ${JSON.stringify(ad).slice(0, 700)}`);
    const as = await get(b.adsetId, "name,status,effective_status,daily_budget,optimization_goal,issues_info,learning_stage_info,targeting");
    say(`conjunto ${b.adsetId}: ${JSON.stringify(as).slice(0, 700)}`);
    const cr = await get(b.creativeId, "status,effective_object_story_id,instagram_permalink_url,call_to_action_type");
    say(`criativo: ${JSON.stringify(cr).slice(0, 400)}`);
    const ins = await get(`${b.adId}/insights`, "spend,impressions,reach,inline_link_clicks").catch(() => ({}));
    say(`números: ${JSON.stringify(ins).slice(0, 300)}`);
    const byCountry = await get(`${b.adId}/insights`, "spend,impressions,reach&breakdowns=country&date_preset=maximum");
    say(`por país: ${JSON.stringify(byCountry.data || byCountry).slice(0, 500)}`);
    const byAge = await get(`${b.adId}/insights`, "impressions,inline_link_clicks&breakdowns=age,gender&date_preset=maximum");
    say(`por idade: ${JSON.stringify((byAge.data || []).map((x) => [x.age, x.gender, x.impressions, x.inline_link_clicks])).slice(0, 700)}`);
  }
  if (st.metaCampaignId) say(`campanha: ${JSON.stringify(await get(st.metaCampaignId, "name,status,effective_status,objective,issues_info")).slice(0, 500)}`);
  const acc = await get(meta.adAccountId, "account_status,disable_reason,amount_spent,balance,funding_source_details");
  say(`conta: ${JSON.stringify(acc).slice(0, 500)}`);
})().catch((e) => { console.log(`::error::${e.message}`); process.exit(1); });
