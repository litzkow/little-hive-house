"""What the shop shows: the owners' selection (Karina, 12 Oct 2026, from versions/escolher.html).

Every collection in catalog.py stays as the full archive; only the designs listed here appear on the site. The rest are
kept (SVGs, renders, prices) and can be brought back by adding them here.

"<slug>-classic" designs are first-version artwork (commit 93c81d3), copied into designs/<collection>/ by
tools/import_classics.py from versions/v3/designs/<old collection>/<old slug>.svg.
"""

# (collection, slug) -> (old collection, old slug, title). Title says "Classic" only when the newer version is also shown.
CLASSICS = {
    ("places", "grand-canyon-classic"): ("places", "grand-canyon", "Grand Canyon Classic"),
    ("places", "new-york-classic"): ("places", "new-york", "New York Classic"),
    ("places", "san-francisco-classic"): ("places", "san-francisco", "San Francisco Classic"),
    ("places", "miami-beach-classic"): ("places", "miami-beach", "Miami Beach"),
    ("world", "rio-classic"): ("places", "rio", "Rio de Janeiro Classic"),
    ("fall", "pumpkin-spice-classic"): ("fall", "pumpkin-spice", "Pumpkin Spice & Everything Nice"),
    ("fall", "falling-for-you-classic"): ("fall", "falling-for-you", "Falling for You"),
    ("halloween", "witch-please-classic"): ("halloween", "witch-please", "Witch Please"),
    ("halloween", "stay-spooky-classic"): ("halloween", "stay-spooky", "Stay Spooky"),
    ("christmas", "naughty-or-nice-classic"): ("christmas", "naughty-or-nice", "Naughty or Nice"),
    ("christmas", "merry-and-bright-classic"): ("christmas", "merry-and-bright", "Merry & Bright"),
    ("summer", "salty-air-sandy-hair-classic"): ("summer", "salty-air-sandy-hair", "Salty Air, Sandy Hair"),
    ("summer", "lifes-a-beach-classic"): ("summer", "lifes-a-beach", "Life's a Beach"),
    ("summer", "vitamin-sea-classic"): ("summer", "vitamin-sea", "Vitamin Sea Classic"),
    ("brasil", "saudade-classic"): ("brasil", "saudade", "Saudade"),
    ("brasil", "cafune-classic"): ("brasil", "cafune", "Cafuné"),
    ("bee-kind", "bee-kind-classic"): ("bee-kind", "bee-kind", "Bee Kind"),
    ("bee-kind", "queen-bee-classic"): ("bee-kind", "queen-bee", "Queen Bee"),
    ("bee-kind", "bee-happy-classic"): ("bee-kind", "bee-happy", "Bee Happy"),
    ("bee-kind", "hive-sweet-hive-classic"): ("bee-kind", "hive-sweet-hive", "Hive Sweet Hive"),
    ("bee-kind", "bee-mine-classic"): ("bee-kind", "bee-mine", "Bee Mine"),
    ("bee-kind", "bee-brave-classic"): ("bee-kind", "bee-brave", "Bee Brave"),
    ("bee-kind", "busy-bee-classic"): ("bee-kind", "busy-bee", "Busy Bee"),
    ("bee-kind", "sweet-as-honey-classic"): ("bee-kind", "sweet-as-honey", "Sweet as Honey"),
    ("bee-kind", "bees-knees-classic"): ("bee-kind", "bees-knees", "The Bee's Knees"),
    ("furry-friends", "dog-mom-classic"): ("furry-friends", "dog-mom", "Dog Mom"),
    ("furry-friends", "cat-mom-classic"): ("furry-friends", "cat-mom", "Cat Mom"),
    ("furry-friends", "crazy-cat-lady-classic"): ("furry-friends", "crazy-cat-lady", "Crazy Cat Lady"),
    ("furry-friends", "who-rescued-who-classic"): ("furry-friends", "who-rescued-who", "Who Rescued Who?"),
    ("furry-friends", "adopt-dont-shop-classic"): ("furry-friends", "adopt-dont-shop", "Adopt, Don't Shop"),
    ("kitchen-words", "bless-this-mess-classic"): ("kitchen-words", "bless-this-mess", "Bless This Mess"),
    ("kitchen-words", "but-first-coffee-classic"): ("kitchen-words", "but-first-coffee", "But First, Coffee"),
    ("kitchen-words", "home-sweet-home-classic"): ("kitchen-words", "home-sweet-home", "Home Sweet Home"),
    ("kitchen-words", "stay-cozy-classic"): ("kitchen-words", "stay-cozy", "Stay Cozy"),
}

# Collections in the order the site shows them, each with its designs in display order.
SHOWN = {
    "places": ["grand-canyon-classic", "atlanta", "new-york-classic", "statue-of-liberty", "san-francisco-classic",
               "miami-beach-classic", "los-angeles", "las-vegas", "new-york", "san-francisco", "yellowstone", "grand-canyon", "chicago",
               "washington-dc", "savannah", "honolulu", "boston", "st-augustine", "philadelphia", "yosemite",
               "napa-valley", "big-sur", "rocky-mountains", "cape-cod", "san-antonio", "sedona", "monument-valley",
               "cape-canaveral", "san-diego"],
    "world": ["paris", "japan", "rio-de-janeiro", "santorini", "kyoto", "venice", "machu-picchu", "florence",
              "rio-classic", "amsterdam", "lisbon", "barcelona", "petra", "budapest", "marrakech", "sydney", "berlin",
              "chichen-itza", "cairo", "norway", "cape-town", "great-wall"],
    "ink-cities": ["new-york", "paris", "amsterdam", "barcelona", "kyoto", "edinburgh", "charleston", "venice", "rio",
                   "savannah", "chicago", "sydney", "istanbul", "philadelphia", "havana", "prague", "austin",
                   "washington-dc", "rome", "miami", "new-orleans", "london", "los-angeles", "san-francisco", "denver",
                   "boston", "lisbon", "seattle", "nashville", "atlanta"],
    "city-sketches": ["london", "new-york", "lisbon", "kyoto", "prague", "chicago", "rome", "washington-dc",
                      "new-orleans", "san-francisco", "austin", "savannah", "istanbul", "nashville", "miami",
                      "philadelphia", "charleston", "boston", "sydney", "venice", "rio", "havana", "atlanta", "denver",
                      "seattle", "edinburgh", "amsterdam", "barcelona", "los-angeles", "paris"],
    "fall": ["pumpkin-spice-classic", "falling-for-you-classic", "hello-fall", "pumpkin-patch", "sweater-weather",
             "happy-fall-yall", "leaf-me-alone", "scenic-route", "give-thanks"],
    "halloween": ["witch-please-classic", "stay-spooky-classic", "happy-halloween", "whooos-there",
                  "too-cute-to-spook", "wrap-it-up"],
    "christmas": ["merry-and-bright-classic", "naughty-or-nice-classic", "merry-christmas", "home-for-christmas",
                  "hung-with-care", "cookies-for-santa", "ho-ho-ho", "seasons-greetings", "north-pole-post-office"],
    "holidays": ["happy-new-year", "cheers", "be-my-valentine", "xoxo", "happy-galentines", "happy-easter",
                 "best-mom-ever", "reel-cool-dad", "thank-you-teacher", "just-married"],
    "summer": ["salty-air-sandy-hair-classic", "lifes-a-beach-classic", "vitamin-sea-classic", "vitamin-sea",
               "beach-please", "sea-you-soon", "beach-days", "lake-life", "pinch-me-im-on-vacation"],
    "brasil": ["saudade-classic", "cafune-classic", "calcadao-de-copacabana", "pao-de-queijo", "brigadeiro", "coxinha",
               "fitinha-do-bonfim", "acai-na-tigela", "feijoada-de-sabado"],
    "americana": ["land-of-the-free", "county-fair", "small-town-big-heart", "drive-in-tonight"],
    "mexico": ["dia-de-muertos", "viva-mexico", "la-chancla", "mi-casa-es-su-casa"],
    "bee-kind": ["bee-kind-classic", "queen-bee-classic", "bee-happy-classic", "hive-sweet-hive-classic",
                 "bee-mine-classic", "busy-bee-classic", "bee-brave-classic", "sweet-as-honey-classic",
                 "bees-knees-classic"],
    "furry-friends": ["dog-mom-classic", "cat-mom-classic", "crazy-cat-lady-classic", "who-rescued-who-classic",
                      "adopt-dont-shop-classic", "home-is-where-the-dog-is", "if-i-fits-i-sits", "life-is-ruff",
                      "bird-watcher"],
    "kitchen-words": ["but-first-coffee-classic", "bless-this-mess-classic", "home-sweet-home-classic",
                      "stay-cozy-classic", "kiss-the-cook", "lettuce-eat", "life-happens-coffee-helps", "wine-oclock",
                      "eat-well-laugh-often-love-much"],
    "bumper-stickers": ["if-you-can-read-this", "dont-follow-me-im-lost-too", "i-brake-for-coffee",
                        "running-on-dad-jokes", "dog-on-board", "gone-fishing", "road-trip-ready", "sunday-driver",
                        "this-car-stops-at-all-yard-sales"],
    "night-sky": ["to-the-moon-and-back", "aries", "taurus", "gemini", "cancer", "leo", "virgo", "libra", "scorpio",
                  "sagittarius", "capricorn", "aquarius", "pisces"],
    "great-masters": ["the-starry-night", "the-great-wave", "cafe-terrace-at-night", "the-kiss", "water-lilies",
                      "sunflowers", "almond-blossoms", "red-fuji", "plum-garden", "wheatfield-with-cypresses",
                      "irises", "the-scream", "tree-of-life", "impression-sunrise", "sunday-on-la-grande-jatte",
                      "the-japanese-footbridge", "the-bedroom", "the-little-street", "view-of-delft", "birch-forest",
                      "several-circles", "the-fighting-temeraire", "wanderer-above-the-sea-of-fog",
                      "hunters-in-the-snow", "still-life-with-apples", "poppy-field", "sudden-shower",
                      "tiger-in-a-tropical-storm", "walk-on-the-beach", "spring-mucha"],
}

# Heritage keeps only these countries (Brasil stands on its own).
HERITAGE = ["americana", "mexico"]

# Home page "A few of our favorites": the owners' 9 stars first, then picks to make 20.
VITRINE = [
    ("places", "grand-canyon-classic"), ("places", "atlanta"), ("world", "paris"), ("world", "japan"),
    ("world", "rio-de-janeiro"), ("ink-cities", "new-york"), ("brasil", "saudade-classic"),
    ("bee-kind", "bee-kind-classic"), ("night-sky", "to-the-moon-and-back"),
    ("places", "new-york-classic"), ("places", "statue-of-liberty"), ("world", "santorini"),
    ("city-sketches", "london"), ("fall", "pumpkin-spice-classic"), ("great-masters", "the-starry-night"),
    ("great-masters", "the-great-wave"), ("kitchen-words", "but-first-coffee-classic"),
    ("furry-friends", "dog-mom-classic"), ("bee-kind", "queen-bee-classic"), ("brasil", "pao-de-queijo"),
]
