"""The shop's collections, in display order. Each design is designs/<collection>/<slug>.svg."""

PRICE = 5          # every ready-made design
BUNDLE = (3, 12)   # any 3 designs for $12
VOLUME = [(100, 25), (50, 20), (20, 10)]   # magnets in the cart -> % off, designs and photos mixed

COLLECTIONS = [
    {
        "slug": "places", "name": "USA Places", "tag": "Travel posters across the United States",
        "blurb": "Painted travel posters of the cities, national parks and coastlines people love most across the United States of America.",
        "titles": {"washington-dc": "Washington, DC", "st-augustine": "St. Augustine", "st-louis": "St. Louis",
                  "blue-ridge": "Blue Ridge Parkway", "glacier": "Glacier National Park"},
        "order": ["new-york", "san-francisco", "nashville", "yellowstone", "las-vegas", "chicago", "grand-canyon",
                 "washington-dc", "new-orleans", "miami-beach", "savannah", "atlanta", "honolulu", "seattle",
                 "boston", "charleston", "st-augustine", "philadelphia", "yosemite", "napa-valley", "rocky-mountains",
                 "big-sur", "florida-keys", "key-west", "outer-banks", "maine-coast", "tybee-island", "cape-cod",
                 "niagara-falls", "cape-canaveral", "austin", "san-antonio", "santa-fe", "sedona", "arches",
                 "monument-valley", "memphis", "lake-tahoe", "glacier", "grand-teton", "denali",
                 "great-smoky-mountains", "blue-ridge", "los-angeles", "san-diego", "portland", "maui", "st-louis",
                 "brooklyn", "annapolis", "mount-rushmore"],
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
        "slug": "holidays", "name": "Holidays & Dates", "tag": "A magnet for every date",
        "blurb": "Little gifts for every date on the calendar: New Year, Valentine's, Easter, Mother's and Father's Day, graduation, the 4th, Thanksgiving and birthdays.",
        "titles": {"happy-4th": "Happy 4th", "xoxo": "XOXO", "lucky": "Lucky", "congrats-grad": "Congrats, Grad!"},
        "order": ["cheers", "xoxo", "lucky", "hoppy-easter", "best-mom-ever", "best-dad-ever", "congrats-grad",
                  "happy-4th", "thankful", "happy-birthday"],
    },
    {
        "slug": "world", "name": "World Places", "tag": "Travel posters from around the globe",
        "blurb": "Our colorful travel posters go abroad: Paris at sunset, Mount Fuji in cherry blossom season, the blue domes of Santorini and more.",
        "titles": {},
        "order": ["paris", "santorini", "japan", "iceland", "florence", "budapest", "london", "venice", "amsterdam",
                 "edinburgh", "rome", "swiss-alps", "sydney", "cinque-terre", "berlin", "lisbon", "prague",
                 "amalfi-coast", "provence", "cairo", "dublin", "athens", "norway", "porto", "barcelona", "pisa",
                 "dubrovnik", "vienna"],
    },
    {
        "slug": "fall", "name": "Fall", "tag": "Pumpkins, leaves and cozy sweaters",
        "blurb": "Warm rust, mustard and olive for the coziest season of the year.",
        "titles": {"oh-my-gourd": "Oh My Gourd!", "pumpkin-spice": "Pumpkin Spice & Everything Nice",
                  "autumn-is-calling": "Autumn Is Calling", "rainy-days-good-books": "Rainy Days & Good Books",
                  "whooo-loves-fall": "Whooo Loves Fall?",
                  "autumn-leaves-pumpkins-please": "Autumn Leaves & Pumpkins Please",
                  "save-room-for-pie": "Save Room for Pie", "scenic-route": "Take the Scenic Route",
                  "happy-fall-yall": "Happy Fall, Y'all", "stick-with-me": "Stick With Me",
                  "boots-and-blankets": "Boots & Blankets"},
        "order": ["cozy-season", "pumpkin-patch", "whooo-loves-fall", "cat-nap-season", "gather-together", "harvest",
                 "hello-fall", "save-room-for-pie", "harvest-moon", "autumn-leaves-pumpkins-please", "cider-mill",
                 "scarf-season", "forage", "stick-with-me", "farmers-market", "oh-my-gourd", "happy-fall-yall",
                 "apple-picking", "scenic-route", "autumn-is-calling", "leaf-me-alone", "falling-for-you",
                 "give-thanks", "pumpkin-spice", "pick-your-own", "misty-mornings", "sunflower-fields",
                 "sweater-weather", "rainy-days-good-books", "boots-and-blankets"],
    },
    {
        "slug": "halloween", "name": "Halloween", "tag": "Spooky season",
        "blurb": "Ghosts, bats, black cats and a few bad puns. Spooky, never scary.",
        "titles": {"boo": "Boo!", "here-for-the-boos": "Here for the Boos", "witches-brew": "Witches' Brew",
                  "whooos-there": "Whooo's There?", "ghouls-night-out": "Ghouls' Night Out",
                  "broom-with-a-view": "Broom with a View", "eye-of-newt": "Eye of Newt",
                  "trick-or-treat": "Trick or Treat", "sweet-and-spooky": "Sweet & Spooky",
                  "just-chillin": "Just Chillin'", "witch-way": "Witch Way?", "enter-if-you-dare": "Enter If You Dare"},
        "order": ["purrfectly-spooky", "official-candy-inspector", "whooos-there", "witch-way", "enter-if-you-dare",
                 "just-chillin", "witches-brew", "carve-out-some-fun", "here-for-the-boos", "nevermore",
                 "happy-haunting", "broom-with-a-view", "haunted-hotel", "spooky-season", "sweet-and-spooky",
                 "trick-or-treat", "too-cute-to-spook", "glow-getter", "happy-halloween", "boo", "wrap-it-up",
                 "witch-please", "eye-of-newt", "hang-in-there", "home-sweet-haunt", "stay-spooky", "the-witch-is-in",
                 "creep-it-real", "full-moon-club", "ghouls-night-out"],
    },
    {
        "slug": "christmas", "name": "Christmas", "tag": "Merry little magnets",
        "blurb": "Stocking stuffers and gift toppers for the merriest time of the year, including a little Feliz Natal.",
        "titles": {"merry-and-bright": "Merry & Bright", "ho-ho-ho": "Ho Ho Ho!", "tis-the-season": "'Tis the Season",
                  "seasons-greetings": "Season's Greetings", "peace-on-earth": "Peace on Earth",
                  "hung-with-care": "Hung with Care", "wrapped-with-love": "Wrapped with Love",
                  "cookies-for-santa": "Cookies for Santa", "trim-the-tree": "Trim the Tree",
                  "hes-been-here": "He's Been Here", "warm-and-cozy": "Warm & Cozy", "noel": "Noël",
                  "north-pole-post-office": "North Pole Post Office"},
        "order": ["home-for-christmas", "merry-christmas", "let-it-snow", "seasons-greetings", "peace-on-earth",
                 "silent-night", "feliz-natal", "chill-out", "hung-with-care", "sleigh-all-day", "warmest-wishes",
                 "winter-wonder", "believe", "hes-been-here", "cookies-for-santa", "warm-and-cozy",
                 "hot-cocoa-season", "gingerbread-lane", "noel", "tis-the-season", "trim-the-tree",
                 "north-pole-post-office", "merry-and-bright", "joy-to-the-world", "snow-much-fun", "ho-ho-ho",
                 "oh-deer", "naughty-or-nice", "fresh-cut-trees", "wrapped-with-love"],
    },
    {
        "slug": "summer", "name": "Summer", "tag": "Sun, sea and good vibes",
        "blurb": "Bright, beachy colors for long days, salty hair and endless sunsets.",
        "titles": {"lifes-a-beach": "Life's a Beach", "salty-air-sandy-hair": "Salty Air, Sandy Hair"},
        "order": ["endless-summer", "beach-please", "vitamin-sea", "good-vibes-only", "lifes-a-beach",
                  "sunshine-state-of-mind", "chill-out", "salty-air-sandy-hair"],
    },
    {
        "slug": "bumper-stickers", "name": "Bumper Stickers", "tag": "Retro sayings, fridge edition",
        "blurb": "Retro bumper sticker sayings that are way too good for a car. Funny, sweet and a little sassy.",
        "titles": {"honk-if-youre-happy": "Honk If You're Happy", "moms-taxi": "Mom's Taxi",
                   "powered-by-coffee": "Powered by Coffee & Chaos"},
        "order": ["i-brake-for-coffee", "honk-if-youre-happy", "moms-taxi", "powered-by-coffee",
                  "my-other-car-is-a-broom", "work-hard-nap-harder", "normal-is-boring", "good-things-take-time",
                  "do-more-of-what-makes-you-happy", "be-the-good"],
    },
    {
        "slug": "home-notes", "name": "Home Notes", "tag": "Soft colors, kind words",
        "blurb": "Gentle words in soft colors for moms, grandmas and anyone who needs a little sunshine.",
        "titles": {"grandmas-kitchen": "Grandma's Kitchen"},
        "order": ["love-you-more", "blessed", "family", "grandmas-kitchen", "hello-sunshine", "choose-joy"],
    },
]

DISPLAY = ["places", "world", "ink-cities", "fall", "halloween", "christmas", "holidays", "summer", "kitchen-words",
           "bumper-stickers", "night-sky", "birth-flowers", "bee-kind", "furry-friends", "brasil", "home-notes"]
COLLECTIONS.sort(key=lambda c: DISPLAY.index(c["slug"]))

# The home page spotlight changes with the calendar. (start MM-DD, end MM-DD), first match wins.
SEASONS = [
    ("12-26", "01-03", "Cheers to a new year", "New Year", "Start the year with a little sparkle on the fridge.", "holidays",
     [("holidays", "cheers"), ("christmas", "joy-to-the-world"), ("home-notes", "choose-joy"), ("bumper-stickers", "good-things-take-time")], ("#1D2B44", "#F6EFE0", "#E2B857")),
    ("01-04", "02-14", "Little love notes", "Valentine's Day", "Sweet little magnets for the people you love, from XOXO to Bee Mine.", "holidays",
     [("holidays", "xoxo"), ("bee-kind", "bee-mine"), ("home-notes", "love-you-more"), ("kitchen-words", "pizza-love-language")], ("#F4C7C3", "#3A2E2A", "#C2343A")),
    ("02-15", "03-17", "Feeling lucky", "St. Patrick's Day", "A little green for March, plus favorites to brighten the end of winter.", "holidays",
     [("holidays", "lucky"), ("ink-cities", "boston"), ("home-notes", "hello-sunshine"), ("bumper-stickers", "be-the-good")], ("#2E7D4F", "#F6EFE0", "#F3D27A")),
    ("03-18", "04-20", "Hello, spring", "Easter & spring", "Bunnies, daisies and daffodils for the first warm days.", "holidays",
     [("holidays", "hoppy-easter"), ("birth-flowers", "march-daffodil"), ("birth-flowers", "april-daisy"), ("home-notes", "hello-sunshine")], ("#E8E1F5", "#2B2118", "#7A5BB5")),
    ("04-21", "05-11", "For the best mom ever", "Mother's Day", "Small, thoughtful gifts for moms, grandmas and everyone who mothers us.", "holidays",
     [("holidays", "best-mom-ever"), ("home-notes", "love-you-more"), ("birth-flowers", "may-lily-of-the-valley"), ("home-notes", "grandmas-kitchen")], ("#F8D7DD", "#3A2E2A", "#C2343A")),
    ("05-12", "05-31", "Congrats, grads", "Graduation season", "Cheer on the class of the year with a little something for the fridge.", "holidays",
     [("holidays", "congrats-grad"), ("bumper-stickers", "do-more-of-what-makes-you-happy"), ("summer", "beach-please"), ("kitchen-words", "eat-cake")], ("#F6EFE0", "#1F2F4D", "#C2343A")),
    ("06-01", "06-21", "For the best dad ever", "Father's Day", "Coffee, naps and dad jokes: the essentials.", "holidays",
     [("holidays", "best-dad-ever"), ("bumper-stickers", "i-brake-for-coffee"), ("bumper-stickers", "work-hard-nap-harder"), ("kitchen-words", "but-first-coffee")], ("#1F2F4D", "#F6EFE0", "#E9B949")),
    ("06-22", "07-04", "Land of the free", "4th of July", "Stars, stripes and the American places we love.", "holidays",
     [("holidays", "happy-4th"), ("places", "washington-dc"), ("places", "new-york"), ("places", "grand-canyon")], ("#F6EFE0", "#1F2F4D", "#B23A3A")),
    ("07-05", "08-31", "Endless summer", "Summer", "Bright, beachy magnets for long days and salty hair.", "summer",
     [("summer", "endless-summer"), ("summer", "vitamin-sea"), ("summer", "beach-please"), ("places", "honolulu")], ("#FF6F59", "#FFFFFF", "#FFC93C")),
    ("09-01", "10-14", "Hello, fall", "Fall", "Pumpkins, falling leaves and sweater weather. Our coziest collection is here.", "fall",
     [("fall", "cozy-season"), ("fall", "pumpkin-patch"), ("fall", "whooo-loves-fall"), ("fall", "cat-nap-season")], ("#4A2F1E", "#F6EDE0", "#D9A23B")),
    ("10-15", "10-31", "Spooky season is here", "Halloween", "Ghosts, bats and black cats. Spooky, never scary.", "halloween",
     [("halloween", "purrfectly-spooky"), ("halloween", "whooos-there"), ("halloween", "witch-way"), ("halloween", "just-chillin")], ("#151515", "#F6EFE0", "#E8833A")),
    ("11-01", "11-27", "Gather & give thanks", "Thanksgiving", "Cozy magnets for the table, the hosts and the people we are thankful for.", "fall",
     [("fall", "gather-together"), ("fall", "harvest"), ("fall", "save-room-for-pie"), ("fall", "give-thanks")], ("#B4532A", "#F6EDE0", "#F3D27A")),
    ("11-28", "12-25", "Merry little magnets", "Christmas", "Stocking stuffers and gift toppers for the merriest time of the year.", "christmas",
     [("christmas", "home-for-christmas"), ("christmas", "merry-christmas"), ("christmas", "let-it-snow"), ("christmas", "seasons-greetings")], ("#1E4D3A", "#F6EFE0", "#E9B949")),
]

# Gift guide cards on the home page: (title, line, link inside the site)
GIFTS = [
    ("For coffee lovers", "Coffee first, everything else later.", "shop.html?q=coffee"),
    ("For travelers", "Their favorite places, near and far.", "collections/world.html"),
    ("Birthday gifts", "Their star sign or their birth flower.", "collections/birth-flowers.html"),
    ("For pet people", "Dog moms, cat ladies and rescuers.", "collections/furry-friends.html"),
    ("For the kitchen", "Bless this mess and taco Tuesdays.", "collections/kitchen-words.html"),
    ("Brazilian at heart", "Saudade, cafuné and café com leite.", "collections/brasil.html"),
]

FEATURED = [("world", "japan"), ("ink-cities", "atlanta"), ("bee-kind", "bee-kind"), ("bumper-stickers", "i-brake-for-coffee"),
            ("night-sky", "leo"), ("kitchen-words", "bless-this-mess"), ("places", "savannah"), ("brasil", "saudade")]


def title_for(col, slug):
    if slug in col["titles"]:
        return col["titles"][slug]
    if col["slug"] == "birth-flowers":
        month, flower = slug.split("-", 1)
        return f"{month.title()} · {flower.replace('-', ' ').title()}"
    return slug.replace("-", " ").title()
