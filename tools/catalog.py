"""The shop's collections, in display order. Each design is designs/<collection>/<slug>.svg."""

PRICE = 5          # every ready-made design
BUNDLE = (3, 12)   # any 3 designs for $12

COLLECTIONS = [
    {
        "slug": "places", "name": "Places", "tag": "Colorful travel posters",
        "blurb": "Bright, poster-style illustrations of the cities, parks and beaches people love most.",
        "titles": {"rio": "Rio de Janeiro", "washington-dc": "Washington, DC", "st-augustine": "St. Augustine"},
        "order": ["new-york", "san-francisco", "grand-canyon", "washington-dc", "miami-beach", "honolulu",
                  "savannah", "st-augustine", "rio"],
    },
    {
        "slug": "ink-cities", "name": "Ink Cities", "tag": "Black & white skylines",
        "blurb": "Fine-line drawings of famous skylines in black ink on warm paper. Quiet, classic and easy to mix.",
        "titles": {"rio": "Rio de Janeiro"},
        "order": ["atlanta", "new-york", "chicago", "miami", "nashville", "boston", "seattle", "san-francisco",
                  "paris", "london", "rome", "rio"],
    },
    {
        "slug": "kitchen-words", "name": "Kitchen Words", "tag": "Little sayings for the fridge",
        "blurb": "Bold black and white type for the room where everyone ends up. Coffee, cake, tacos and a little chaos.",
        "titles": {"wine-oclock": "Wine O'Clock", "life-happens-coffee-helps": "Life Happens, Coffee Helps",
                   "pizza-love-language": "Pizza Is My Love Language", "but-first-coffee": "But First, Coffee",
                   "good-food-good-mood": "Good Food, Good Mood"},
        "order": ["bless-this-mess", "but-first-coffee", "home-sweet-home", "good-food-good-mood", "kiss-the-cook",
                  "wine-oclock", "life-happens-coffee-helps", "taco-tuesday", "eat-cake", "gather",
                  "pizza-love-language", "stay-cozy"],
    },
    {
        "slug": "night-sky", "name": "Night Sky", "tag": "Zodiac constellations",
        "blurb": "Every sign of the zodiac drawn as its real constellation, in gold and starlight on a deep night sky.",
        "titles": {},
        "order": ["aries", "taurus", "gemini", "cancer", "leo", "virgo", "libra", "scorpio", "sagittarius",
                  "capricorn", "aquarius", "pisces"],
    },
    {
        "slug": "birth-flowers", "name": "Birth Flowers", "tag": "A flower for every month",
        "blurb": "Delicate line drawings of the flower for each birth month. A sweet birthday gift that fits in a card.",
        "titles": {"may-lily-of-the-valley": "May · Lily of the Valley"},
        "order": ["january-carnation", "february-violet", "march-daffodil", "april-daisy", "may-lily-of-the-valley",
                  "june-rose", "july-larkspur", "august-poppy", "september-aster", "october-cosmos",
                  "november-chrysanthemum", "december-holly"],
    },
    {
        "slug": "bee-kind", "name": "Bee Kind", "tag": "Our honey-sweet signature",
        "blurb": "The house collection: happy bees, dripping honey and a few cheeky puns in our honey and black colors.",
        "titles": {"bees-knees": "The Bee's Knees", "mind-your-own-beeswax": "Mind Your Own Beeswax"},
        "order": ["bee-kind", "queen-bee", "mind-your-own-beeswax", "bee-happy", "sweet-as-honey",
                  "hive-sweet-hive", "bees-knees", "bee-mine", "bee-brave", "busy-bee"],
    },
    {
        "slug": "furry-friends", "name": "Furry Friends", "tag": "For dog and cat people",
        "blurb": "For the people whose fridge is really a photo wall of their pets.",
        "titles": {"adopt-dont-shop": "Adopt, Don't Shop", "who-rescued-who": "Who Rescued Who?"},
        "order": ["dog-mom", "cat-mom", "good-boy", "crazy-cat-lady", "adopt-dont-shop", "who-rescued-who"],
    },
    {
        "slug": "brasil", "name": "Brasil", "tag": "Saudade on the fridge",
        "blurb": "Our roots, in green and yellow. Little Brazilian words that don't fit in any other language.",
        "titles": {"cafe-com-leite": "Café com Leite", "cafune": "Cafuné", "bom-dia": "Bom Dia"},
        "order": ["saudade", "bom-dia", "cafe-com-leite", "tamo-junto", "brasil", "cafune"],
    },
    {
        "slug": "holidays", "name": "Holidays", "tag": "Seasonal favorites",
        "blurb": "Small, cheerful gifts for every holiday of the year, from Valentine's Day to Christmas.",
        "titles": {"merry-and-bright": "Merry & Bright", "boo": "Boo!", "happy-4th": "Happy 4th", "xoxo": "XOXO"},
        "order": ["merry-and-bright", "boo", "thankful", "cheers", "xoxo", "happy-4th"],
    },
    {
        "slug": "home-notes", "name": "Home Notes", "tag": "Soft colors, kind words",
        "blurb": "Gentle words in soft colors for moms, grandmas and anyone who needs a little sunshine.",
        "titles": {"grandmas-kitchen": "Grandma's Kitchen"},
        "order": ["love-you-more", "blessed", "family", "grandmas-kitchen", "hello-sunshine", "choose-joy"],
    },
]

FEATURED = [("ink-cities", "atlanta"), ("bee-kind", "bee-kind"), ("night-sky", "leo"), ("kitchen-words", "bless-this-mess"),
            ("holidays", "merry-and-bright"), ("birth-flowers", "october-cosmos"), ("places", "savannah"),
            ("brasil", "saudade")]


def title_for(col, slug):
    if slug in col["titles"]:
        return col["titles"][slug]
    if col["slug"] == "birth-flowers":
        month, flower = slug.split("-", 1)
        return f"{month.title()} · {flower.replace('-', ' ').title()}"
    return slug.replace("-", " ").title()
