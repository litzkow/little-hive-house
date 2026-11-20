"use strict";
/* Anúncios: quais nomes de público existem no Meta com o nome exato (interesses, comportamentos, momentos de vida,
   família), com o tamanho de cada um nos EUA. Para montar os grupos de público do robô sem chute. */
const { Firestore } = require("@google-cloud/firestore");
const db = new Firestore({ projectId: process.env.PROJECT || "little-hive-house" });
const say = (s) => console.log(`::warning title=publico::${String(s).replace(/\n/g, " ").slice(0, 950)}`);
const INTERESTS = ["Gift", "Gifts", "Christmas gifts", "Gift shop", "Shopping", "Online shopping", "Etsy", "Handicraft", "Handmade", "Arts and crafts",
  "Interior design", "Home décor", "Home decor", "Farmhouse style", "Cottagecore", "Hygge", "Kitchen", "Cooking", "Baking", "Home improvement",
  "Photography", "Family", "Parenting", "Motherhood", "Grandparents", "Scrapbooking", "Photo book", "Shutterfly", "Snapfish", "Wedding", "Weddings", "Bride",
  "Dogs", "Cats", "Pet", "Pets", "Dog lover", "Pet adoption", "Graduation",
  "Travel", "Tourism", "Road trip", "Souvenir", "Collecting", "Collectables", "National park", "Backpacking", "Lonely Planet", "Airbnb", "TripAdvisor", "Vacations", "Cruise ship",
  "Christmas", "Christmas decoration", "Holiday shopping", "Halloween", "Thanksgiving", "Autumn", "Pumpkin spice", "Summer", "Beach",
  "Brazil", "Brazilian cuisine", "Mexican cuisine", "Mexico", "Ireland", "Irish people", "Italian cuisine", "Italy", "Puerto Rico", "Philippines", "Filipino cuisine",
  "India", "Indian cuisine", "Korean drama", "K-pop", "Korean cuisine", "Japanese cuisine", "Japan", "Anime", "Greece", "Greek mythology", "Greek cuisine", "France", "French cuisine", "Paris",
  "Art", "Fine art", "Museums", "Vincent van Gogh", "Claude Monet", "Impressionism", "Books", "Reading", "Classic literature", "Fairy tale", "Mythology", "Horror films", "Astronomy", "Astrology",
  "Bees", "Beekeeping", "Honey", "Flowers", "Gardening", "Inspirational quotes", "Positive thinking", "Bumper sticker", "Refrigerator magnet", "Magnets", "Pinterest"];
const BEHAVIORS = ["Engaged Shoppers", "Frequent Travelers", "Frequent international travelers", "Returned from travels 1 week ago", "Returned from travels 2 weeks ago",
  "Currently traveling", "Commuters", "Small business owners"];
(async () => {
  const meta = ((await db.collection("ads").doc("auth").get()).data() || {}).meta;
  const get = async (q) => (await (await fetch(`https://graph.facebook.com/v26.0/search?${new URLSearchParams({ ...q, access_token: meta.token })}`)).json());
  const found = [], miss = [];
  for (const n of INTERESTS) {
    const j = await get({ type: "adinterest", q: n, limit: "10" });
    const hit = (j.data || []).find((x) => String(x.name).trim().toLowerCase() === n.toLowerCase());
    if (hit) found.push(`${hit.name}=${hit.id}:${Math.round((hit.audience_size_upper_bound || hit.audience_size || 0) / 1e6)}M`); else miss.push(n);
  }
  say(`interesses OK (${found.length}): ${found.join(" | ")}`.slice(0, 950));
  if (found.join(" | ").length > 900) say(`... ${found.join(" | ").slice(900, 1850)}`);
  say(`não existem: ${miss.join(", ")}`);
  for (const cls of ["behaviors", "life_events", "family_statuses"]) {
    const j = await get({ type: "adTargetingCategory", class: cls, limit: "1000" });
    const all = j.data || [];
    const pick = cls === "behaviors" ? all.filter((x) => BEHAVIORS.some((b) => b.toLowerCase() === String(x.name).toLowerCase()))
      : all.filter((x) => /engag|newlywed|anniversary|birthday|new job|moved|parent|baby|toddler|preschool|grade|teen/i.test(x.name));
    say(`${cls} (${all.length}): ${pick.map((x) => `${x.name}=${x.id}:${Math.round((x.audience_size_upper_bound || 0) / 1e6)}M`).join(" | ")}`.slice(0, 950));
  }
})().catch((e) => { console.log(`::error::${e.message}`); process.exit(1); });
