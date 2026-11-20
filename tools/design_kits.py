"""The big design catalog: ~60 kinds of business, the Personalize themes (family, home, pets, baby...) and more event
designs, made from kits (the words a kind of business uses) and recipes (which layout, which words go where). Each
design is the same shape as tools/biz_designs.py makes, so assets/designer.js draws them all.

Sets: every design belongs to one set (a kind of business, a Personalize theme or an event kind); a page shows its sets
(build.py studio_html), and the studio loads a set's designs when the customer opens it (assets/designs/<set>.json).
Rows (the purpose of a design) group them inside a set, like the rows of a streaming app."""
import hashlib

ROWS = [("promo", "Bring customers back"), ("number", "Keep your number on the fridge"), ("qr", "Scan me"), ("photo", "With a photo"),
        ("useful", "Useful every day"), ("brand", "Your brand, beautifully"), ("thanks", "Thank-yous & holidays")]
PROWS = [("name", "With your name"), ("photo", "With a photo"), ("useful", "Useful at home"), ("fun", "Just for fun"), ("gift", "Gifts & keepsakes")]
EROWS = [("date", "Save the date"), ("photo", "With a photo"), ("thanks", "Thank-yous & favors"), ("qr", "Scan me"), ("party", "Party time")]


def phone(seed):
    n = int(hashlib.md5(seed.encode()).hexdigest()[:6], 16)
    return f"(555) {200 + n % 700:03d}-{1000 + (n >> 10) % 9000:04d}"


def web(name):
    return "".join(c for c in name.lower() if c.isalnum())[:18] + ".com"


# ---------------------------------------------------------------- kinds of business
# key, name, group, line icon, illustration, palettes, names, tagline, services, bold headlines, offer, photos, extra
G_FOOD, G_HEALTH, G_HOME, G_MONEY, G_BEAUTY, G_PETS, G_AUTO, G_COMM, G_SHOPS, G_OTHER = (
    "Restaurants & food", "Health & dental", "Home services", "Real estate & finance", "Beauty & fitness", "Pets", "Auto",
    "Churches, schools & teams", "Shops & studios", "Other & any business")
K = []


def kit(key, name, group, icon, il, pals, names, sub, services, heads, offer, photos=(), **x):
    K.append(dict(key=key, name=name, group=group, icon=icon, il=il, pals=pals, names=names, sub=sub, services=services, heads=heads,
                  offer=offer, photos=list(photos), **x))


kit("pizza", "Pizzeria", G_FOOD, "pizza", "pizza", ["red", "cream", "black", "forest"], ["Tony’s Slice", "Nonna Lucia Pizzeria", "Brooklyn Bros Pizza"],
    "WOOD-FIRED · DELIVERY", ["Pizza by the slice", "Wings & salads", "Family deals", "Catering"], ["Pizza\nnight?", "Hot & fresh\nin 30 min."],
    ("ON THE FRIDGE = ON THE TABLE", "$5 OFF", "any large pizza"), ["pizza-1", "pizza-2", "pizza-3", "pizza-4"], menu=[("Large cheese", "$12.99"), ("Pepperoni", "$14.99"), ("Wings (10)", "$11.99"), ("Family deal", "$29.99")])
kit("mexican", "Mexican restaurant", G_FOOD, "taco", "taco", ["orange", "terracotta", "sun", "forest"], ["El Sol Taquería", "La Cocina", "Casa Jalisco"],
    "AUTHENTIC MEXICAN KITCHEN", ["Street tacos", "Burritos & bowls", "Margaritas", "Catering"], ["Taco\nTuesday!", "¡Buen\nprovecho!"],
    ("TACO TUESDAY", "$2", "street tacos, all day"), ["food-1", "food-3"], menu=[("Street tacos", "$2.50"), ("Burrito", "$10.99"), ("Quesadilla", "$9.50"), ("Taco plate", "$12.99")])
kit("burger", "Burgers & diner", G_FOOD, "plate", "burger", ["red", "sun", "navy", "black"], ["Smash Shack", "Route 66 Diner", "The Burger Joint"],
    "BURGERS · SHAKES · FRIES", ["Smash burgers", "Milkshakes", "Breakfast all day", "Kids menu"], ["Burger\ncraving?", "Open late."],
    ("FREE FRIES", "FREE", "fries with any burger"), ["food-1"], menu=[("Classic smash", "$9.99"), ("Double bacon", "$12.99"), ("Shake", "$5.50"), ("Fries", "$3.50")])
kit("cafe", "Coffee shop", G_FOOD, "cup", "coffee", ["forest", "cream", "sage", "black"], ["Little Fern Café", "Daily Grind", "Bean & Bloom"],
    "COFFEE · TEA · PASTRIES", ["Espresso bar", "Fresh pastries", "Breakfast", "Free Wi-Fi"], ["But first,\ncoffee.", "Your daily\nhappy place."],
    ("BUY 9, GET 1", "FREE", "coffee on your 10th visit"), ["coffee-1", "coffee-2", "coffee-3", "coffee-4"], menu=[("Latte", "$4.50"), ("Cold brew", "$4.25"), ("Croissant", "$3.75"), ("Breakfast sandwich", "$7.50")])
kit("bakery", "Bakery", G_FOOD, "cake", "cake", ["blush", "cream", "lilac", "terracotta"], ["Sweet Crumb", "Rise & Shine Bakery", "Sugar Bee Cakes"],
    "CAKES · COOKIES · BREAD", ["Custom cakes", "Cookies & cupcakes", "Fresh bread", "Party orders"], ["Life is\nsweet.", "Baked fresh\nat 6 am."],
    ("YOUR NEXT CAKE", "$10 OFF", "any custom cake"), ["bakery-1", "bakery-2", "bakery-3", "bakery-4"], menu=[("Sourdough loaf", "$8"), ("Dozen cookies", "$18"), ("Cupcakes (6)", "$15"), ("Custom cake", "from $45")])
kit("sushi", "Sushi & Asian", G_FOOD, "bowl", "sushi", ["black", "slate", "red", "cream"], ["Kai Sushi", "Noodle House", "Golden Dragon"],
    "SUSHI · RAMEN · TAKEOUT", ["Sushi rolls", "Ramen", "Bento boxes", "Takeout"], ["Roll\nwith us.", "Slurp\nhappy."],
    ("LUNCH SPECIAL", "$11.99", "any 2 rolls + miso"), ["food-2"], menu=[("California roll", "$7.50"), ("Spicy tuna", "$8.50"), ("Tonkotsu ramen", "$14"), ("Bento box", "$15.99")])
kit("bbq", "BBQ & food truck", G_FOOD, "truck", "burger", ["black", "red", "sun", "terracotta"], ["Smokin’ Wheels BBQ", "Low & Slow", "Big Pit BBQ"],
    "SMOKED LOW & SLOW", ["Brisket", "Pulled pork", "Ribs", "Catering"], ["Smoke\nshow.", "Find the\ntruck!"],
    ("BRING THIS MAGNET", "FREE", "side with any plate"), ["food-4"], menu=[("Brisket plate", "$16"), ("Pulled pork", "$12"), ("Half rack", "$18"), ("Mac & cheese", "$4")])
kit("icecream", "Ice cream & sweets", G_FOOD, "heart", "icecream", ["pink", "aqua", "sun", "blush"], ["Scoops & Smiles", "The Sweet Spot", "Polar Treats"],
    "ICE CREAM · SHAKES · CONES", ["32 flavors", "Sundaes", "Shakes", "Ice cream cakes"], ["I scream,\nyou scream!", "Treat\nyourself."],
    ("KIDS EAT", "FREE", "kids’ cone with any sundae"), [], menu=[("Single scoop", "$3.50"), ("Double", "$5.50"), ("Sundae", "$7"), ("Shake", "$6")])
kit("restaurant", "Restaurant", G_FOOD, "chef", "burger", ["navy", "burgundy", "forest", "cream"], ["The Corner Table", "Oak & Ember", "Harbor Grill"],
    "AMERICAN KITCHEN & BAR", ["Lunch & dinner", "Weekend brunch", "Private events", "Takeout"], ["Dinner\nis served.", "Your table\nis ready."],
    ("BIRTHDAY MONTH", "FREE", "dessert on your birthday"), ["food-2", "food-4", "chef-1", "chef-2"], menu=[("Monday", "Burger + fries $12"), ("Wednesday", "Wing night"), ("Friday", "Fish fry"), ("Sunday", "Kids eat free")])
kit("catering", "Catering", G_FOOD, "chef", None, ["ivory", "black", "sage", "burgundy"], ["Silver Spoon Catering", "Fiesta Catering Co.", "Table for All"],
    "WEDDINGS · OFFICES · PARTIES", ["Weddings", "Office lunches", "Parties", "Food trucks"], ["We cater,\nyou celebrate.", "Feed the\nwhole crew."],
    ("BOOK BY MARCH", "10% OFF", "any event over 50 guests"), ["chef-1", "food-4"])
kit("dentist", "Dentist", G_HEALTH, "tooth", "tooth", ["teal", "sky", "mint", "navy"], ["Bright Side Dental", "Summit Family Dental", "Happy Teeth Kids"],
    "FAMILY & COSMETIC DENTISTRY", ["Cleanings", "Whitening", "Implants", "Kids welcome"], ["Smile\nbrighter.", "Your smile,\nour passion."],
    ("NEW PATIENT SPECIAL", "$99", "exam, X-rays and cleaning"), ["dentist-1", "dentist-2", "dentist-3", "dentist-4"], appt=True)
kit("ortho", "Orthodontist", G_HEALTH, "tooth", "tooth", ["aqua", "lilac", "teal", "sun"], ["Clear Path Ortho", "Straight Up Orthodontics", "Smile Studio Ortho"],
    "BRACES · CLEAR ALIGNERS", ["Braces", "Clear aligners", "Retainers", "Free consults"], ["Smile\nbigger.", "Straight to\nthe point."],
    ("FREE CONSULTATION", "FREE", "consult + 3D scan"), ["dentist-2", "dentist-4"], appt=True)
kit("doctor", "Family doctor", G_HEALTH, "steth", "clinic", ["dusty", "sky", "teal", "navy"], ["Oakwood Family Medicine", "Riverside Primary Care", "Westside Clinic"],
    "FAMILY MEDICINE", ["Checkups", "Sick visits", "Vaccines", "Telehealth"], ["We’re here\nfor you.", "Care that\nfeels like home."],
    ("FLU SHOTS", "NO WAIT", "walk in for your flu shot"), [], appt=True)
kit("pediatrics", "Pediatrician", G_HEALTH, "baby", "baby", ["lilac", "sky", "sun", "mint"], ["Little Sprouts Pediatrics", "Happy Kids Clinic", "Tiny Toes Pediatrics"],
    "PEDIATRICS · NEWBORN TO 18", ["Well-child visits", "Sick visits", "Vaccines", "Sports physicals"], ["Little ones,\nbig care.", "Happy, healthy\nkids."],
    ("BACK TO SCHOOL", "$35", "sports physical"), ["toddler-1", "kids-1"], appt=True)
kit("chiro", "Chiropractor", G_HEALTH, "heart", "clinic", ["slate", "teal", "sage", "navy"], ["Align Chiropractic", "Back in Motion", "Spine & Wellness"],
    "FEEL BETTER, MOVE BETTER", ["Back & neck pain", "Sports injuries", "Massage", "Same-day visits"], ["Back pain?\nWe got you.", "Move\nfreely."],
    ("FIRST VISIT", "$49", "exam + adjustment"), ["yoga-1"], appt=True)
kit("pt", "Physical therapy", G_HEALTH, "dumbbell", "fitness", ["sky", "teal", "orange", "slate"], ["Motion PT", "Peak Physical Therapy", "Restore PT"],
    "PHYSICAL THERAPY · SPORTS REHAB", ["Sports rehab", "After surgery", "Back pain", "Balance"], ["Back in\nthe game.", "Stronger\nevery day."],
    ("FREE SCREEN", "FREE", "15-minute injury screen"), ["gym-2"], appt=True)
kit("eyes", "Eye doctor", G_HEALTH, "glasses", None, ["ivory", "navy", "black", "sky"], ["ClearView Eye Care", "Focus Optometry", "See Well Eyewear"],
    "EYE EXAMS · GLASSES · CONTACTS", ["Eye exams", "Glasses", "Contacts", "Kids’ vision"], ["See\nclearly.", "Look good,\nsee better."],
    ("SECOND PAIR", "50% OFF", "your second pair of glasses"), [], appt=True)
kit("pharmacy", "Pharmacy", G_HEALTH, "cross", "clinic", ["teal", "red", "sky", "mint"], ["Main Street Pharmacy", "CareRx", "Hometown Drug"],
    "PRESCRIPTIONS · VACCINES", ["Prescriptions", "Flu shots", "Free delivery", "Compounding"], ["We know\nyour name.", "Refills made\neasy."],
    ("FREE DELIVERY", "FREE", "prescription delivery in town"), [])
kit("cleaning", "House cleaning", G_HOME, "spray", "spray", ["aqua", "lilac", "mint", "blush"], ["Sparkle & Co.", "Fresh Nest Cleaning", "Maria’s Maids"],
    "HOUSE CLEANING · MOVE-OUT · OFFICES", ["Weekly & biweekly", "Deep cleaning", "Move-in, move-out", "Airbnb turnovers"], ["Come home\nto clean.", "We clean,\nyou relax."],
    ("NEW CLIENTS", "$40 OFF", "your first deep clean"), ["cleaning-1", "cleaning-3", "cleaning-4", "kitchen-1"], checklist=[("Kitchen counters", "Mon"), ("Bathrooms", "Tue"), ("Dust & vacuum", "Wed"), ("Laundry", "Thu"), ("Floors", "Fri")])
kit("hvac", "Heating & air", G_HOME, "snow", "tools", ["navy", "sky", "red", "slate"], ["Peach Valley Air", "CoolBreeze HVAC", "Comfort Zone Heating"],
    "HEATING · COOLING · 24/7", ["AC repair", "Furnaces", "Tune-ups", "Duct cleaning"], ["No heat?\nNo AC?", "Cool home,\nhappy home."],
    ("TUNE-UP SPECIAL", "$49", "AC or furnace tune-up"), ["house-1"], remind=("FILTER CHANGE", "Change your filter today"), emergency=True)
kit("plumber", "Plumber", G_HOME, "drop", "tools", ["sky", "sun", "navy", "aqua"], ["Rapid Rooter", "Blue Pipe Plumbing", "Joe the Plumber"],
    "PLUMBING · DRAINS · WATER HEATERS", ["Leaks & clogs", "Water heaters", "Drain cleaning", "Remodels"], ["Leak?\nClog?", "We fix\nit fast."],
    ("SAVE ON YOUR NEXT CALL", "$50 OFF", "any repair over $250"), [], emergency=True)
kit("electric", "Electrician", G_HOME, "bolt", "bolt", ["black", "sun", "navy", "slate"], ["Live Wire Electric", "Bright Spark Electric", "Volt Bros"],
    "RESIDENTIAL · COMMERCIAL", ["Panels", "Lighting", "EV chargers", "Generators"], ["Lights out?\nWe’re on.", "Powered\nby pros."],
    ("EV CHARGER", "$100 OFF", "EV charger installation"), [], emergency=True)
kit("roofing", "Roofing", G_HOME, "roof", "house", ["brick", "slate", "navy", "black"], ["Summit Roofing", "Top Notch Roofs", "Shield Roofing Co."],
    "FREE INSPECTIONS · INSURANCE CLAIMS", ["Storm damage", "Repairs & leaks", "New roofs", "Gutters"], ["Storm\ndamage?", "Solid roof,\nsound sleep."],
    ("FREE INSPECTION", "FREE", "roof inspection + photos"), ["house-1", "house-2"], emergency=True)
kit("lawn", "Lawn & landscaping", G_HOME, "leaf", "sprout", ["forest", "lime", "sage", "black"], ["Oak & Acre Lawns", "GreenLeaf Landscaping", "Cut Above Lawn Care"],
    "MOWING · MULCH · CLEANUPS", ["Weekly mowing", "Mulch & beds", "Leaf cleanup", "Irrigation"], ["Best lawn\non the block.", "Green\nmade easy."],
    ("FIRST MOW", "FREE", "with a season plan"), ["garden-1", "garden-2", "garden-3"], checklist=[("Aerate & seed", "Spring"), ("Mow high, water deep", "Summer"), ("Leaves & fertilize", "Fall"), ("Rest & plan", "Winter")])
kit("pest", "Pest control", G_HOME, "bug", None, ["orange", "sun", "forest", "black"], ["Bug Busters", "Shield Pest Control", "No More Pests"],
    "PEST CONTROL · TERMITES · MOSQUITOES", ["Ants & roaches", "Termites", "Mosquitoes", "Rodents"], ["Uninvited\nguests?", "Bug off!"],
    ("FIRST SERVICE", "$50 OFF", "quarterly pest plan"), [], emergency=True)
kit("pool", "Pool service", G_HOME, "pool", "pool", ["aqua", "sky", "navy", "sun"], ["Blue Lagoon Pools", "Crystal Clear Pools", "Splash Pool Care"],
    "CLEANING · REPAIRS · OPENINGS", ["Weekly cleaning", "Openings & closings", "Repairs", "Green-to-clean"], ["Pool ready\nall summer.", "Dive in."],
    ("POOL OPENING", "$75 OFF", "spring opening"), [])
kit("moving", "Movers", G_HOME, "truck", "moving", ["orange", "navy", "red", "sun"], ["Two Brothers Moving", "Easy Move Co.", "Box & Go Movers"],
    "LOCAL · LONG DISTANCE", ["Local moves", "Long distance", "Packing", "Storage"], ["We lift.\nYou relax.", "Moving made\neasy."],
    ("FREE BOXES", "FREE", "boxes with any move"), [])
kit("handyman", "Handyman", G_HOME, "hammer", "tools", ["terracotta", "slate", "sun", "navy"], ["Fix-It Frank", "Handy Hank", "Honey-Do Pros"],
    "NO JOB TOO SMALL", ["Drywall & paint", "Doors & shelves", "TV mounting", "Honey-do lists"], ["Honey-do\nlist? Done.", "We fix\nthe little things."],
    ("FIRST HOUR", "$25 OFF", "any job"), [], checklist=[("Smoke detector batteries", ""), ("Leaky faucet", ""), ("Squeaky door", ""), ("Hang the shelves", ""), ("Touch-up paint", "")])
kit("painter", "Painters", G_HOME, "brush", "paint", ["sky", "sun", "slate", "terracotta"], ["Fresh Coat Painting", "True Color Painters", "Brush Strokes Co."],
    "INTERIOR · EXTERIOR · CABINETS", ["Interior", "Exterior", "Cabinets", "Decks"], ["Fresh coat,\nfresh start.", "Color your\nworld."],
    ("ONE ROOM", "$100 OFF", "when you paint 3 rooms"), ["home-interior-1", "home-interior-2"])
kit("locksmith", "Locksmith", G_HOME, "lock", None, ["sun", "black", "navy", "red"], ["Key Master", "Quick Lock & Key", "SafeHome Locksmith"],
    "HOME · AUTO · 24/7", ["Lockouts", "Rekeying", "Smart locks", "Car keys"], ["Locked\nout?", "We open\ndoors."],
    ("REKEY SPECIAL", "$20 OFF", "rekey your new home"), [], emergency=True)
kit("realtor", "Realtor", G_MONEY, "house", "keyhouse", ["navy", "ivory", "sage", "black"], ["Maria Santos Realty", "Jenna Park Homes", "The Reyes Team"],
    "YOUR NEIGHBORHOOD REALTOR", ["Buying", "Selling", "First-time buyers", "Free home value"], ["Thinking of\nmoving?", "Home is\nwhere we start."],
    ("WHAT’S YOUR HOME WORTH?", "FREE", "home value report"), ["house-1", "house-2", "house-3", "house-4", "realtor-1", "home-interior-3"], checklist=[("HVAC filter", "Monthly"), ("Gutters & roof", "Spring"), ("Deck & AC", "Summer"), ("Furnace check", "Fall"), ("Smoke detectors", "Yearly")])
kit("mortgage", "Mortgage", G_MONEY, "key", "keyhouse", ["teal", "navy", "forest", "black"], ["Keystone Lending", "Home Path Mortgage", "First Key Loans"],
    "MORTGAGES · REFINANCE", ["First-time buyers", "Refinance", "FHA & VA", "Pre-approval"], ["Keys to your\nfirst home.", "Rates on\nyour side."],
    ("PRE-APPROVAL", "24 HRS", "get pre-approved fast"), ["house-2", "handshake-1"])
kit("insurance", "Insurance", G_MONEY, "shield", "shield", ["navy", "sky", "forest", "slate"], ["Blue Oak Insurance", "Harbor Insurance", "Shield Family Agency"],
    "HOME · AUTO · LIFE", ["Home", "Auto", "Life", "Business"], ["Covered,\nlike family.", "Peace of\nmind."],
    ("FREE QUOTE", "SAVE 15%", "bundle home + auto"), ["family-1", "handshake-2"], emergency=True)
kit("tax", "Tax & accounting", G_MONEY, "calc", None, ["lime", "navy", "slate", "ivory"], ["Ledger & Co.", "Smart Tax Pros", "Bright Books"],
    "TAX PREP · BOOKKEEPING · PAYROLL", ["Personal taxes", "Small business", "Bookkeeping", "Payroll"], ["Tax season?\nRelax.", "Numbers,\nhandled."],
    ("REFER A FRIEND", "$25", "for you and for them"), ["team-1"], remind=("TAX DAY", "April 15 is coming"))
kit("lawyer", "Law firm", G_MONEY, "scale", None, ["burgundy", "ivory", "navy", "black"], ["Reed & Lowe", "Morales Law", "Carter Legal"],
    "ATTORNEYS AT LAW", ["Car accidents", "Family law", "Immigration", "Wills & estates"], ["We fight\nfor you.", "Justice\nfirst."],
    ("FREE CONSULTATION", "FREE", "case review"), ["handshake-1"])
kit("financial", "Financial advisor", G_MONEY, "calc", None, ["forest", "navy", "gold", "black"], ["North Star Wealth", "Evergreen Financial", "Summit Advisors"],
    "RETIREMENT · INVESTING · PLANNING", ["Retirement", "Investing", "College savings", "Insurance"], ["Plan today,\nrelax later.", "Your future,\nfocused."],
    ("FREE REVIEW", "FREE", "retirement check-up"), ["team-3"])
kit("salon", "Hair salon", G_BEAUTY, "scissors", "salon", ["blush", "plum", "black", "lilac"], ["Velvet Salon", "Glow Studio", "Bella Hair"],
    "HAIR · COLOR · BLOWOUTS", ["Cuts", "Color", "Blowouts", "Bridal"], ["Good hair\nday, every day.", "Fresh look,\nnew you."],
    ("NEW CLIENTS", "20% OFF", "your first color"), ["salon-1", "salon-2", "salon-3", "salon-4"], appt=True)
kit("barber", "Barbershop", G_BEAUTY, "comb", "salon", ["black", "red", "navy", "sun"], ["Kings Barbershop", "Sharp & Co. Barbers", "Fade Factory"],
    "CUTS · FADES · BEARDS", ["Fades", "Beard trims", "Hot towel shaves", "Kids cuts"], ["Fresh\ncut?", "Look sharp."],
    ("YOUR 10TH CUT", "FREE", "show this magnet each visit"), ["barber-1", "barber-2", "barber-3", "barber-4"], appt=True)
kit("nails", "Nail salon", G_BEAUTY, "polish", None, ["pink", "blush", "lilac", "black"], ["Luxe Nails", "Polished Nail Bar", "Pink Tips Spa"],
    "MANICURE · PEDICURE · SPA", ["Gel manicure", "Pedicure", "Acrylics", "Nail art"], ["Nailed\nit.", "Treat\nyourself."],
    ("MANI + PEDI", "$45", "every Tuesday"), [], appt=True)
kit("medspa", "Med spa", G_BEAUTY, "lotus", "spa", ["lilac", "ivory", "black", "blush"], ["Aura Med Spa", "Glow Aesthetics", "Pure Skin Studio"],
    "BOTOX · FACIALS · LASER", ["Botox", "Facials", "Laser", "Skin care"], ["Glow\nup.", "Your best\nskin."],
    ("FIRST FACIAL", "$50 OFF", "any facial"), ["salon-2"], appt=True)
kit("massage", "Massage", G_BEAUTY, "lotus", "spa", ["sage", "terracotta", "ivory", "plum"], ["Breathe Massage", "Knead to Relax", "Calm Hands Spa"],
    "MASSAGE · BODYWORK", ["Swedish", "Deep tissue", "Prenatal", "Couples"], ["Relax.\nRepeat.", "You deserve\nthis."],
    ("FIRST MASSAGE", "$20 OFF", "60-minute massage"), ["yoga-2"], appt=True)
kit("gym", "Gym", G_BEAUTY, "dumbbell", "fitness", ["black", "orange", "red", "slate"], ["Iron Republic", "Pulse Fitness", "Core Strength Gym"],
    "24/7 GYM · CLASSES · TRAINERS", ["24/7 access", "Group classes", "Personal training", "Kids club"], ["No\nexcuses.", "Stronger\nevery day."],
    ("FIRST WEEK", "FREE", "no contract"), ["gym-1", "gym-2", "gym-3", "gym-4"], hours=[("Mon – Fri", "5 am – 11 pm"), ("Saturday", "7 am – 9 pm"), ("Sunday", "8 am – 6 pm"), ("Members", "24/7")])
kit("yoga", "Yoga & pilates", G_BEAUTY, "lotus", "spa", ["sage", "blush", "ivory", "teal"], ["Breathe Studio", "Flow Yoga", "Core Pilates"],
    "YOGA · PILATES · MEDITATION", ["Yoga", "Pilates", "Meditation", "Private sessions"], ["Breathe\nin.", "Find your\nflow."],
    ("FIRST CLASS", "FREE", "any class"), ["yoga-1", "yoga-2", "yoga-3", "yoga-4"], hours=[("Mon & Wed", "Vinyasa 6 pm"), ("Tue & Thu", "Pilates 7 am"), ("Saturday", "Flow 9 am"), ("Sunday", "Restore 10 am")])
kit("trainer", "Personal trainer", G_BEAUTY, "dumbbell", "fitness", ["red", "black", "sun", "navy"], ["Coach Dee Fitness", "Train with Tony", "Fit Life Coaching"],
    "1-ON-1 TRAINING · NUTRITION", ["1-on-1 training", "Nutrition", "Online coaching", "Small groups"], ["Ready to\nstart?", "Your goals,\nmy plan."],
    ("FREE WEEK", "FREE", "first week of training"), ["gym-2", "gym-4"])
kit("tattoo", "Tattoo studio", G_BEAUTY, "star", None, ["black", "red", "slate", "plum"], ["Black Rose Tattoo", "Ink & Iron", "Sacred Art Studio"],
    "CUSTOM TATTOOS · PIERCING", ["Custom art", "Cover-ups", "Fine line", "Piercing"], ["Ink your\nstory.", "Art that\nlasts."],
    ("FLASH FRIDAY", "$60", "flash tattoos"), [])
kit("vet", "Veterinarian", G_PETS, "paw", "vet", ["teal", "orange", "sky", "mint"], ["Sunny Paws Vet", "Happy Tails Animal Hospital", "Oak Creek Vet"],
    "DOGS · CATS · EXOTICS", ["Wellness exams", "Vaccines", "Dental", "Surgery"], ["Happy pets,\nhappy home.", "Care for\nevery tail."],
    ("NEW PATIENTS", "FREE", "first exam"), ["vet-1", "vet-2", "dog-1", "cat-1"], appt=True, petinfo=True)
kit("groomer", "Pet groomer", G_PETS, "paw", "dog", ["aqua", "pink", "sun", "lilac"], ["Suds & Pups", "Fluffy Cuts", "Pampered Paws"],
    "DOG GROOMING · BATH · NAILS", ["Full groom", "Bath & brush", "Nail trims", "Teeth"], ["Fresh &\nfluffy.", "Good dog,\ngreat hair."],
    ("YOUR 10TH GROOM", "FREE", "show this magnet each visit"), ["dog-2", "puppy-2", "dog-small-1", "dog-small-3"], appt=True)
kit("petsitter", "Dog walker & sitter", G_PETS, "bone", "dog", ["pink", "sun", "forest", "aqua"], ["Wag Squad", "Happy Trails Dog Walking", "Paws & Play"],
    "WALKS · DROP-INS · OVERNIGHTS", ["Daily walks", "Drop-in visits", "Overnight stays", "Cat care"], ["Good dogs\nonly.", "We walk,\nthey wag."],
    ("FIRST WALK", "FREE", "meet & greet + walk"), ["dog-3", "dog-4", "puppy-1", "puppy-3"], petinfo=True)
kit("dogtrainer", "Dog trainer", G_PETS, "bone", "dog", ["forest", "orange", "navy", "sun"], ["Good Boy Training", "Sit Stay Academy", "Pawsitive Training"],
    "PUPPY · OBEDIENCE · BEHAVIOR", ["Puppy classes", "Obedience", "Behavior", "Private lessons"], ["Sit.\nStay. Love.", "Good dog\nguaranteed."],
    ("PUPPY CLASS", "$25 OFF", "6-week puppy class"), ["puppy-4", "dog-5"])
kit("autorepair", "Auto repair", G_AUTO, "wrench", "tools", ["black", "red", "slate", "navy"], ["Precision Auto", "Main St. Garage", "Honest Wrench"],
    "ENGINES · BRAKES · A/C", ["Oil changes", "Brakes", "Check engine", "A/C"], ["Check engine\nlight?", "Honest work,\nfair price."],
    ("OIL CHANGE", "$29.99", "oil change + inspection"), ["mechanic-1", "mechanic-2", "mechanic-3"], oil=True)
kit("tires", "Tires", G_AUTO, "car", "car", ["red", "black", "sun", "slate"], ["Rubber Road Tires", "Tire Town", "Grip & Go"],
    "TIRES · BRAKES · ALIGNMENT", ["New tires", "Flat repair", "Alignment", "Rotation"], ["Flat tire?\nCome on in.", "Roll with\nconfidence."],
    ("BUY 3", "GET 1", "on select tires"), ["car-1"], oil=True)
kit("detailing", "Car detailing & wash", G_AUTO, "car", "car", ["slate", "black", "aqua", "navy"], ["Gloss Boss Detailing", "Shine On Car Wash", "Mobile Detail Pros"],
    "MOBILE · WE COME TO YOU", ["Full detail", "Ceramic coating", "Interior", "Wash club"], ["Showroom\nshine.", "Clean car,\nhappy life."],
    ("WASH CLUB", "$19/MO", "unlimited washes"), ["car-2", "car-3", "car-4"])
kit("towing", "Towing", G_AUTO, "hook", "car", ["sun", "black", "red", "navy"], ["Big Dan’s Towing", "24/7 Tow Pros", "Roadside Rescue"],
    "TOWING · JUMP STARTS · LOCKOUTS", ["Towing", "Jump starts", "Lockouts", "Flat tires"], ["Stuck on\nthe road?", "We’ll get\nyou home."],
    ("KEEP THIS NUMBER", "24/7", "fast, fair, friendly"), [], emergency=True)
kit("church", "Church", G_COMM, "church", "church", ["ivory", "navy", "sage", "burgundy"], ["Grace Community Church", "New Hope Church", "Faith Fellowship"],
    "ALL ARE WELCOME", ["Sunday services", "Kids ministry", "Youth group", "Bible study"], ["You belong\nhere.", "Come as\nyou are."],
    ("BRING A FRIEND", "FREE", "coffee & donuts Sunday"), ["church-1", "church-2"], hours=[("Sunday", "9:00 & 11:00 am"), ("Wednesday", "Bible study 7 pm"), ("Friday", "Youth 6:30 pm"), ("Kids", "During services")])
kit("nonprofit", "Nonprofit", G_COMM, "heart", None, ["teal", "orange", "forest", "navy"], ["Harvest Food Bank", "Helping Hands", "Hope House"],
    "TOGETHER WE GIVE", ["Volunteer", "Donate", "Food drives", "Events"], ["Thank\nyou!", "Every gift\nmatters."],
    ("GIVE TODAY", "$25", "feeds a family for a week"), ["team-2"])
kit("school", "School & daycare", G_COMM, "apple", "school", ["sun", "sky", "red", "mint"], ["Bright Start Academy", "Little Learners Daycare", "Sunshine Preschool"],
    "DAYCARE · PRE-K · AFTER SCHOOL", ["Infants", "Pre-K", "After school", "Summer camp"], ["Little minds,\nbig days.", "Now\nenrolling!"],
    ("ENROLL BY MAY", "FREE", "registration"), ["school-1", "kids-1", "toddler-2"], hours=[("Drop-off", "7:00 am"), ("Pick-up", "6:00 pm"), ("Lunch", "11:30 am"), ("Nap", "1:00 pm")])
kit("tutor", "Tutoring", G_COMM, "book", "school", ["lilac", "navy", "sun", "teal"], ["A+ Tutoring", "Smart Start Learning", "Bright Minds Tutors"],
    "MATH · READING · TEST PREP", ["Math", "Reading", "SAT & ACT", "Homework help"], ["Grades\nup!", "Learning\nmade fun."],
    ("FIRST SESSION", "FREE", "assessment + session"), ["school-1", "school-3"])
kit("team", "Sports team", G_COMM, "star", None, ["forest", "navy", "red", "black"], ["Riverside Tigers", "Westview Wildcats", "Central Eagles"],
    "SPRING 2027 SEASON", ["Games", "Practices", "Tournaments", "Fundraisers"], ["Go\nTigers!", "Game\nday!"],
    ("THANKS TO OUR SPONSOR", "GO!", "Nonna Lucia Pizzeria"), ["football-1", "football-2", "football-3"], schedule=[("Sep 6", "vs Eagles"), ("Sep 13", "at Falcons"), ("Sep 20", "vs Comets"), ("Sep 27", "at Rangers")])
kit("dance", "Dance & music lessons", G_COMM, "music", None, ["pink", "plum", "sun", "lilac"], ["Twirl Dance Studio", "Rhythm Music School", "Star Steps Dance"],
    "DANCE · PIANO · GUITAR · VOICE", ["Ballet", "Hip hop", "Piano", "Guitar"], ["Dance like\neveryone’s\nwatching.", "Find your\nrhythm."],
    ("FIRST CLASS", "FREE", "any class"), ["kids-1"], hours=[("Mon", "Ballet 4 pm"), ("Tue", "Hip hop 5 pm"), ("Wed", "Piano 4 pm"), ("Sat", "Tiny tots 10 am")])
kit("florist", "Florist", G_SHOPS, "flower", "flowers", ["blush", "ivory", "sage", "plum"], ["Petal & Stem", "Bloom Room", "Wild Rose Florist"],
    "FLOWERS FOR EVERY DAY", ["Bouquets", "Weddings", "Sympathy", "Same-day delivery"], ["Say it with\nflowers.", "Bloom\nwhere you are."],
    ("FREE DELIVERY", "FREE", "in town, any bouquet"), ["flowers-1", "flowers-2", "flowers-3", "flowers-4"])
kit("photographer", "Photographer", G_SHOPS, "camera", "camera", ["black", "ivory", "sage", "blush"], ["Golden Hour Photo", "Lens & Light", "Little Moments Photography"],
    "FAMILY · WEDDINGS · NEWBORN", ["Family", "Weddings", "Newborn", "Headshots"], ["Moments\nthat last.", "Say\ncheese!"],
    ("MINI SESSION", "$150", "fall mini sessions"), ["family-1", "family-3", "wedding-1", "baby-1", "beach-1", "engagement-1"])
kit("boutique", "Boutique & gifts", G_SHOPS, "tag", None, ["blush", "black", "terracotta", "sage"], ["Rose & Thread", "The Gift Nook", "Mabel’s Boutique"],
    "CLOTHES · GIFTS · HOME", ["New arrivals", "Gifts", "Home decor", "Accessories"], ["Shop\nlocal.", "Something\nfor everyone."],
    ("YOUR NEXT VISIT", "15% OFF", "show this magnet"), [])
kit("eventvenue", "Event venue & planner", G_SHOPS, "rings", "rings", ["ivory", "black", "sage", "blush"], ["The Willow Barn", "Belle Events", "Magnolia Hall"],
    "WEDDINGS · PARTIES · CORPORATE", ["Weddings", "Showers", "Corporate", "Quinceañeras"], ["Celebrate\nhere.", "Your day,\nperfectly planned."],
    ("BOOK A TOUR", "10% OFF", "2027 dates booked this month"), ["wedding-3", "party-2"])
kit("dj", "DJ & entertainment", G_SHOPS, "music", None, ["black", "plum", "pink", "navy"], ["DJ Nova", "Party Starters", "Beat Box Events"],
    "WEDDINGS · PARTIES · EVENTS", ["Weddings", "Quinceañeras", "Corporate", "Photo booth"], ["Let’s get\nthis party\nstarted!", "Press play."],
    ("PHOTO BOOTH", "FREE", "with any wedding package"), ["party-1", "party-3"])


# any business at all: plain words they change to their own (every recipe, no limit per row)
kit("general", "Any business", G_OTHER, "star", None, ["navy", "forest", "red", "teal", "black", "terracotta", "lilac", "sun", "sage", "orange"],
    ["Your Business Name", "Main Street Co.", "Smith & Sons"], "YOUR SERVICES · YOUR CITY", ["Quality service", "Fair prices", "Locally owned", "Free estimates"],
    ["Here to\nhelp.", "Proudly\nlocal."], ("SHOW THIS MAGNET", "10% OFF", "your next visit"), ["handshake-1", "team-1", "team-3", "handshake-2"],
    appt=True, emergency=True, hours=[("Mon – Fri", "9 am – 6 pm"), ("Saturday", "10 am – 4 pm"), ("Sunday", "Closed"), ("Holidays", "Call us")],
    checklist=[("Call us", ""), ("Visit us", ""), ("Follow us", ""), ("Tell a friend", ""), ("Leave a review", "")])
kit("startup", "New business & side hustle", G_OTHER, "star", None, ["pink", "aqua", "lilac", "sun", "black", "orange"],
    ["Your Brand", "Bright Idea Co.", "Made by Maya"], "SMALL BUSINESS · BIG HEART", ["Handmade", "Custom orders", "Local delivery", "Gift sets"],
    ["Shop\nsmall.", "Thanks for\nsupporting us!"], ("FIRST ORDER", "15% OFF", "use code FRIDGE15"), ["team-2", "handshake-1"])

# ---------------------------------------------------------------- recipes: one layout, the words it needs
def T(*a):
    return a


def recipes_business(k):
    """(row, layout, words, options) for a kind of business: every recipe that fits its kit."""
    n0, n1, n2 = (k["names"] + k["names"] * 2)[:3]
    sub, svc, heads, (kick, off, offh) = k["sub"], k["services"], k["heads"], k["offer"]
    ph = lambda nm: phone(k["key"] + nm)
    il = ("il:" + k["il"]) if k.get("il") else k["icon"]
    out = []
    add = lambda row, lay, words, **opt: out.append((row, lay, words, opt))
    rows_info = k.get("menu") or k.get("hours")
    # bring customers back
    add("promo", "L_coupon", dict(kicker=kick, offer=off, head=offh, name=n0, phone=ph(n0), line="Show this magnet · Expires 12/31/2027"), icon=k["icon"])
    add("promo", "ticket", dict(kicker=kick, offer=off, head=offh, name=n1, phone=ph(n1), line="One per visit · Mention this magnet"), icon=k["icon"])
    add("promo", "burst" if k["group"] in (G_FOOD, G_AUTO, G_SHOPS, G_HOME) else "tag", dict(kicker=kick, offer=off, head=offh, name=n2, phone=ph(n2)), icon=il)
    add("promo", "L_punch", dict(name=n0, sub=sub, head="Your 10th visit is free", line=f"Show this magnet · {ph(n0)}"), icon=k["icon"])
    add("promo", "referral", dict(kicker="REFER A FRIEND", offer="$20", head="Send a friend our way and you both save.", name=n1, phone=ph(n1)), icon=k["icon"])
    # keep the number
    add("number", "L_word", dict(sub=sub, head=heads[0], line=f"{svc[0]}, {svc[1].lower()} and more. Call or text anytime.", name=n0, phone=ph(n0)), icon=il)
    add("number", "duo", dict(sub=sub, head=heads[1 % len(heads)], line=f"{svc[0]} · {svc[1]} · {svc[2]}", name=n1, phone=ph(n1)), icon=il)
    add("number", "bubble", dict(head=heads[0].replace("\n", " "), line=f"{svc[0]}, {svc[2].lower()} and more.", name=n2, phone=ph(n2)), icon=il)
    add("number", "hero", dict(name=n1, sub=sub, phone=ph(n1)), icon=il)
    if k.get("emergency"):
        add("number", "L_hazard", dict(name=n0, sub=sub, head=heads[0].replace("\n", " "), phone=ph(n0), line="Fast, friendly, licensed & insured"), icon=k["icon"])
        add("number", "bignum", dict(name=n2, sub=sub, head="Keep this number", phone=ph(n2), line="Day or night, we pick up."), icon=k["icon"])
        add("number", "L_bar", dict(name=n1, sub=sub, head=heads[0], line="We answer 24/7, holidays too.", phone=ph(n1)), icon=k["icon"])
    else:
        add("number", "diagonal", dict(name=n0, head=heads[0], line=f"{svc[0]}, {svc[1].lower()} and more.", sub=sub, phone=ph(n0)), icon=il)
        add("number", "wave", dict(name=n2, sub=sub, head=heads[1 % len(heads)], line=svc[0] + " · " + svc[1], phone=ph(n2)), icon=il)
    # scan me
    add("qr", "L_qr", dict(name=n0, line="Book, order or say hi.", head="Scan\nme", phone=ph(n0), web=web(n0)), icon=k["icon"])
    add("qr", "qrphone", dict(head="Scan to\nbook", line=f"{svc[0]} and more, one tap away.", name=n1, web=web(n1)), icon=il)
    add("qr", "review", dict(head="Love us?", line="Scan and leave us a review.", name=n2), icon=il)
    add("qr", "qrbig", dict(head="Scan me!", line="Our menu, booking and hours.", name=n0), icon=il)
    # with a photo
    for i, p in enumerate(k["photos"][:4]):
        lay = ["L_photo", "magazine", "halfphoto", "frame", "archphoto", "circlephoto", "snapshot"][(i + len(k["key"])) % 7]
        nm = [n0, n1, n2][i % 3]
        add("photo", lay, dict(sub=sub, name=nm, head=heads[i % len(heads)], line=svc[i % 4], phone=ph(nm), web=web(nm)), icon=il, photo="stock:" + p, pos="center 40%")
    # useful every day
    if k.get("menu"):
        add("useful", "menu", dict(name=n0, sub=sub, head="Our favorites", line="Order online", phone=ph(n0)), icon=k["icon"], rows=k["menu"])
        add("useful", "chalk", dict(name=n1, head="Today’s specials", phone=ph(n1)), icon=k["icon"], rows=k["menu"])
        add("useful", "receipt", dict(name=n2, sub=sub, head="Thank you, come again!", phone=ph(n2)), icon=k["icon"], rows=k["menu"])
    if k.get("hours"):
        add("useful", "clock", dict(name=n0, head="Our hours", phone=ph(n0), line=web(n0)), icon=k["icon"], rows=k["hours"])
        add("useful", "L_hours", dict(name=n1, sub=sub, head="This week", phone=ph(n1), line="See you soon"), icon=k["icon"], rows=k["hours"])
    if k.get("appt"):
        add("useful", "L_appt", dict(name=n0, sub=sub, head="Your next visit", line="Need to reschedule? Call", phone=ph(n0)), icon=k["icon"], hand=("Tue, March 9", "10:30 am"))
        add("useful", "remind", dict(name=n1, sub=sub, head="Your next visit", line="Need to change it? Call", phone=ph(n1)), icon=il, month="MARCH", hand=("9", "10:30 am"))
        add("useful", "sticky", dict(head="Don’t forget!", line=f"Your next {svc[0].lower()} is on ______", name=n2, phone=ph(n2)), icon=k["icon"])
    if k.get("checklist"):
        add("useful", "checklist", dict(head="Checklist", line="A little help from your friends at " + n0, name=n0, phone=ph(n0)), icon=k["icon"], rows=k["checklist"])
        add("useful", "L_useful", dict(head="Good to know", line="Keep it on the fridge", name=n1, phone=ph(n1)), icon=k["icon"], rows=[(b or "·", a) for a, b in k["checklist"]][:5], kw=0, vf="500 25px Jost")
    if k.get("emergency"):
        add("useful", "emergency", dict(head="In case of emergency", line="Keep it where everyone can see", name=n0, phone=ph(n0)), icon=k["icon"],
            rows=[("Emergency", "911"), ("Poison control", "1-800-222-1222"), (k["name"], ph(n0)), ("Neighbor", "")])
    if k.get("remind"):
        t, line = k["remind"]
        add("useful", "remind", dict(name=n0, sub=sub, head=line, line="Questions? Call", phone=ph(n0)), icon=il, month=t.split()[0][:6], hand=("1", "Write the date here"))
    if k.get("oil"):
        add("useful", "L_useful", dict(head="Oil change log", line="Next one is due at the mileage below", name=n0, phone=ph(n0)), icon=k["icon"], rows=[("Date", ""), ("Mileage", ""), ("Next due", ""), ("Tires rotated", "")], kw=190)
    if k.get("petinfo"):
        add("useful", "L_useful", dict(head="My pet’s info", line="For the sitter, the walker and you", name=n0, phone=ph(n0)), icon=k["icon"], rows=[("Name", ""), ("Microchip", ""), ("Food", ""), ("Our vet", ph(n0))], kw=170)
    if k.get("schedule"):
        add("useful", "L_useful", dict(head=n0.split()[-1] + " 2027", line="Thanks to our sponsor, " + "Nonna Lucia Pizzeria", name="Go " + n0.split()[-1] + "!", phone=ph(n0)), icon="star", rows=k["schedule"], vf="500 25px Jost")
        add("useful", "jersey", dict(name=n0.split()[-1], sub=sub, line="Proud sponsor · Nonna Lucia Pizzeria"), icon="star", year="27")
    # your brand, beautifully
    brand = [("L_classic", dict(name=n0, sub=sub, line=svc[0] + " · " + svc[1], phone=ph(n0)), {}),
             ("L_mono", dict(mono="".join(w[0] for w in n1.replace("&", "").split()[:2]).upper(), name=n1.upper(), sub=sub.title(), phone=ph(n1), web=web(n1)), {}),
             ("L_badge", dict(name=n2, sub=sub[:28], since="EST. 2012", line=svc[0] + " · " + svc[1], phone=ph(n2)), {}),
             ("label", dict(name=n0, sub=svc[0].upper(), since="EST. 2009", line=sub.title(), phone=ph(n0)), {}),
             ("minimal", dict(name=n1, sub=sub.title(), phone=ph(n1), web=web(n1)), {}),
             ("bizcard", dict(name=n2, sub=sub, phone=ph(n2), line="123 Main Street", web="Mon – Sat · 9 am – 6 pm"), {}),
             ("L_split", dict(name=n0, sub=sub[:30], items0=svc[0], phone=ph(n0), web=web(n0), since="LOCALLY OWNED"), {"items": svc}),
             ("seal", dict(name=n1, sub=sub[:30], phone=ph(n1)), {}),
             ("ribbon", dict(name=n2, sub=sub, line=svc[0] + " · " + svc[1] + " · " + svc[2], phone=ph(n2)), {}),
             ("gradient", dict(head=heads[1 % len(heads)], line=f"{svc[0]}, {svc[1].lower()} and {svc[2].lower()}.", name=n0, web=web(n0), phone=ph(n0)), {}),
             ("geo", dict(name=n1, sub=sub, line=svc[0] + " · " + svc[1], phone=ph(n1)), {}),
             ("stamp", dict(name=n2, sub=sub.title()[:26], since="EST. 2015", phone=ph(n2)), {}),
             ("crest", dict(mono="".join(w[0] for w in n0.replace("&", "").split()[:2]).upper(), name=n0.upper(), sub=sub.title(), phone=ph(n0)), {}),
             ("watercolor", dict(name=n1, sub=sub, line=svc[0] + ", " + svc[1].lower() + " and more", phone=ph(n1), web=web(n1)), {})]
    g = k["group"]
    if g in (G_FOOD, G_BEAUTY, G_SHOPS):
        brand.append(("neon", dict(sub=sub, name=n2, head=heads[0].replace("\n", " "), line=svc[0] + " · " + svc[1], phone=ph(n2)), {}))
    if g in (G_FOOD, G_SHOPS) or k["key"] in ("florist", "cafe", "bakery"):
        brand.append(("kraft", dict(name=n0, sub=sub, head=heads[0], line=svc[0] + " · " + svc[1], phone=ph(n0)), {}))
        brand.append(("diner", dict(sub=sub, name=n1, line=svc[0] + " · " + svc[1] + " · " + svc[2], phone=ph(n1)), {}))
    if g in (G_HOME,):
        brand.append(("blueprint", dict(name=n0, sub=sub, head=heads[0], line=svc[0] + " · " + svc[1] + " · " + svc[2], phone=ph(n0), since="LICENSED · INSURED"), {}))
        brand.append(("stripes", dict(kicker=kick, offer=off, head=offh, name=n2, phone=ph(n2)), {}))
    if k["key"] == "barber":
        brand.append(("pole", dict(name=n0, sub=sub, line="Walk-ins welcome", phone=ph(n0)), {}))
    if g == G_PETS:
        brand.append(("paws", dict(name=n1, sub=sub, line=svc[0] + " · " + svc[1], phone=ph(n1)), {}))
    if k["key"] in ("florist", "salon", "nails", "medspa", "massage", "yoga", "eventvenue", "bakery", "boutique"):
        brand.append(("floral", dict(sub=sub, name=n2, line=svc[0] + " · " + svc[1], phone=ph(n2)), {}))
    if g in (G_MONEY,) or k["key"] in ("eventvenue", "medspa", "lawyer"):
        brand.append(("deco", dict(mono="".join(w[0] for w in n2.replace("&", "").split()[:2]).upper(), name=n2.upper(), sub=sub.title(), phone=ph(n2)), {}))
    if g in (G_COMM,) and k["key"] in ("school", "dance", "tutor"):
        brand.append(("blobs", dict(head=heads[0], line=svc[0] + " · " + svc[1], name=n0, phone=ph(n0)), {}))
    if g in (G_FOOD, G_BEAUTY, G_SHOPS) or k["key"] in ("pool", "cleaning"):
        brand.append(("retro", dict(sub=sub, name=n0, line=svc[0] + " · " + svc[1], phone=ph(n0)), {}))
    for lay, words, extra in brand:
        add("brand", lay, words, icon=(k["icon"] if lay in ("L_classic", "L_split", "L_badge", "stamp", "minimal") else il), **extra)
    # thank-yous & holidays
    add("thanks", "L_thanks", dict(head="Thank you!", line="We’re grateful for neighbors like you.", name=n0, phone=ph(n0)), icon="heart", font="400 92px/1.1 'Dancing Script'")
    add("thanks", "wreath", dict(head="Merry & bright", line="Happy holidays from all of us.", name=n1, phone=ph(n1)), icon="star")
    add("thanks", "L_thanks", dict(head="Cheers to 2027", line="Thank you for a wonderful year together.", name=n2, phone=ph(n2)), icon="cheers", font="400 74px/1.1 'Dancing Script'", pal="black")
    return out


# ---------------------------------------------------------------- Personalize: the family's own magnets
PSETS = []


def pset(key, name, icon, pals, recipes):
    PSETS.append(dict(key=key, name=name, icon=icon, pals=pals, recipes=recipes))


FAM = "The Garcia Family"
pset("p-family", "Family name", "house", ["ivory", "sage", "navy", "blush", "black", "terracotta"], [
    ("name", "L_classic", dict(name=FAM, sub="EST. 2015", line="Love lives here", phone="★"), dict(icon="il:house", font="400 60px/1.1 'Dancing Script'")),
    ("name", "crest", dict(mono="G", name="THE GARCIAS", sub="Established 2015", phone="Love · Laughter · Home"), {}),
    ("name", "deco", dict(mono="G", name="THE GARCIAS", sub="Est. 2015", phone="1412 Magnolia Lane"), {}),
    ("name", "label", dict(name="The Garcias", sub="EST. 2015", since="HOME SWEET HOME", line="Love lives here", phone="★ ★ ★"), {}),
    ("name", "ribbon", dict(name="The Garcias", sub="EST. 2015", line="Home is wherever we are together", phone="♥"), dict(icon="il:house")),
    ("name", "L_mono", dict(mono="G", name="THE GARCIA FAMILY", sub="Established 2015", phone="Love lives here", web="♥"), {}),
    ("name", "seal", dict(name="The Garcias", sub="EST. 2015 · HOME", phone="♥"), dict(icon="il:house")),
    ("name", "watercolor", dict(name="The Garcias", sub="EST. 2015", line="Together is our favorite place to be", phone="♥", web=""), dict(icon="heart")),
    ("name", "floral", dict(sub="WELCOME TO", name="The Garcias’", line="Home sweet home", phone="EST. 2015"), {}),
    ("name", "minimal", dict(name="The Garcias", sub="Established 2015", phone="Home sweet home", web=""), dict(icon="house")),
    ("name", "kraft", dict(name="The Garcias", sub="EST. 2015", head="Love lives\nhere.", line="Home sweet home", phone="♥"), {}),
    ("name", "stamp", dict(name="The Garcias", sub="Est. 2015", since="HOME", phone="♥ ♥ ♥"), dict(icon="il:house")),
    ("name", "retro", dict(sub="THE GARCIA FAMILY", name="Est. 2015", line="Good vibes only", phone="♥"), {}),
    ("name", "neon", dict(sub="WELCOME TO", name="The Garcias", head="Home sweet home", line="", phone="EST. 2015"), {}),
    ("name", "geo", dict(name="The Garcias", sub="EST. 2015", line="Home sweet home", phone="♥"), dict(icon="il:house")),
    ("name", "monodate", dict(sub="EST.", a="Ana", b="Carlos", date="06 · 14 · 2015", place="The Garcia Family"), {}),
])
pset("p-home", "New home", "key", ["sage", "navy", "terracotta", "ivory", "teal"], [
    ("name", "hero", dict(name="Our first home", sub="1412 MAGNOLIA LANE · 2026", phone="The Parkers"), dict(icon="il:house")),
    ("name", "L_classic", dict(name="Home Sweet Home", sub="1412 MAGNOLIA LANE", line="The Parker Family", phone="2026"), dict(icon="il:keyhouse", font="400 64px/1.1 'Dancing Script'")),
    ("name", "label", dict(name="1412", sub="MAGNOLIA LANE", since="EST. 2026", line="The Parker Family", phone="♥"), {}),
    ("name", "stamp", dict(name="New home", sub="Magnolia Lane", since="2026", phone="THE PARKERS"), dict(icon="il:keyhouse")),
    ("name", "seal", dict(name="The Parkers", sub="NEW HOME · 2026", phone="1412 MAGNOLIA LN"), dict(icon="il:keyhouse")),
    ("photo", "snapshot", dict(head="We bought a house!", name="The Parkers", phone="2026"), dict(photo="stock:house-1")),
    ("photo", "archphoto", dict(name="Home sweet home", sub="THE PARKERS · 2026", phone="1412 Magnolia Lane"), dict(photo="stock:house-2")),
    ("photo", "W_photo", dict(head="Welcome home", line="1412 MAGNOLIA LANE · 2026"), dict(photo="stock:house-4", font="400 70px/1.1 'Dancing Script'")),
    ("useful", "L_qr", dict(name="Guest Wi-Fi", line="Scan to join our Wi-Fi.", head="Free\nWi-Fi", phone="Parker Home", web="Password inside"), dict(icon="house", url="WIFI:T:WPA;S:ParkerHome;P:welcome123;;")),
    ("useful", "checklist", dict(head="House rules", line="The Parker home", name="The Parkers", phone="♥"), dict(icon="house", rows=[("Be kind", ""), ("Say please", ""), ("Clean up after you", ""), ("Hug often", ""), ("Laugh a lot", "")])),
    ("useful", "emergency", dict(head="Important numbers", line="1412 Magnolia Lane", name="The Parkers", phone=""), dict(icon="house", rows=[("Emergency", "911"), ("Poison control", "1-800-222-1222"), ("Mom", ""), ("Dad", ""), ("Neighbor", "")])),
    ("gift", "L_thanks", dict(head="Welcome home!", line="So happy for you. Love, the Reyes family", name="The Parkers", phone="2026"), dict(icon="il:house", font="400 84px/1.1 'Dancing Script'")),
])
pset("p-pets", "Pets", "paw", ["sun", "aqua", "pink", "forest", "orange", "blush"], [
    ("photo", "L_photo", dict(sub="GOOD BOY", name="Max", line="Adopted 2024", phone="♥"), dict(photo="stock:dog-1")),
    ("photo", "circlephoto", dict(name="Luna", sub="QUEEN OF THE HOUSE", phone="♥ since 2022"), dict(photo="stock:cat-2")),
    ("photo", "snapshot", dict(head="Best boy, Max", name="Gotcha day", phone="05.12.24"), dict(photo="stock:puppy-3")),
    ("photo", "frame", dict(name="Bella", sub="GOOD GIRL", phone="EST. 2021"), dict(photo="stock:dog-small-2")),
    ("photo", "archphoto", dict(name="Charlie", sub="BEST FRIEND", phone="2019 – forever"), dict(photo="stock:dog-4")),
    ("photo", "magazine", dict(name="Cooper", sub="PET OF THE YEAR", head="Good boy\nalert!", line="Treats accepted", phone="♥"), dict(photo="stock:dog-3")),
    ("photo", "W_polaroid", dict(head="Our little furball", date="GOTCHA DAY", line="MILO · 2025"), dict(photo="stock:cat-4")),
    ("photo", "photocircle", dict(head="Daisy", line="BEST DOG EVER"), dict(photo="stock:puppy-5")),
    ("useful", "L_useful", dict(head="My pet’s info", line="For the sitter, the walker and you", name="Max", phone=""), dict(icon="paw", rows=[("Name", "Max"), ("Microchip", ""), ("Food", "1 cup, twice a day"), ("Our vet", "")], kw=170)),
    ("useful", "checklist", dict(head="Who fed the dog?", line="Check it off!", name="Max", phone="♥"), dict(icon="paw", rows=[("Breakfast", "Mon"), ("Dinner", "Mon"), ("Walk", ""), ("Fresh water", ""), ("Belly rubs", "always")])),
    ("name", "paws", dict(name="Max", sub="GOOD BOY", line="Treats are always welcome", phone="♥"), dict(icon="il:dog")),
    ("name", "seal", dict(name="Spoiled", sub="AND PROUD OF IT", phone="LUNA"), dict(icon="il:dog")),
    ("fun", "bubble", dict(head="Did someone say treat?", line="Signed, Max", name="Max", phone="♥"), dict(icon="il:dog")),
    ("fun", "bigtype", dict(sub="HOUSE RULES", head="The dog\nis in\ncharge.", line="Sorry, we tried.", date="♥"), {}),
])
pset("p-baby", "Baby & kids", "baby", ["sky", "blush", "mint", "lilac", "sun", "ivory"], [
    ("gift", "remind", dict(name="Welcome, Olivia", sub="BORN MARCH 14, 2026", head="7 lb 2 oz · 20 in", line="Love, Mom & Dad", phone="♥"), dict(icon="il:baby", month="MARCH", hand=("14", "4:12 am"))),
    ("photo", "W_polaroid", dict(head="Welcome, Olivia", date="03.14.26", line="7 LB 2 OZ · 20 IN"), dict(photo="stock:baby-1")),
    ("photo", "photocircle", dict(head="Hello, world!", line="LEO · 03.14.26"), dict(photo="stock:baby-3")),
    ("photo", "archphoto", dict(name="Olivia Rose", sub="BORN 03.14.26", phone="7 lb 2 oz"), dict(photo="stock:baby-4")),
    ("photo", "frame", dict(name="Our little one", sub="EST. 2026", phone="♥"), dict(photo="stock:toddler-1")),
    ("photo", "film", dict(head="First birthday", line="OLIVIA · 2027"), dict(photo="stock:toddler-3")),
    ("useful", "checklist", dict(head="Chore chart", line="Emma’s jobs this week", name="Emma", phone="★"), dict(icon="star", rows=[("Make your bed", ""), ("Feed the dog", ""), ("Brush teeth", ""), ("Homework", ""), ("Help with dinner", "")])),
    ("useful", "L_useful", dict(head="2 minutes, twice a day", line="Check a box every time you brush!", name="Emma", phone="★"), dict(icon="tooth", rows=[("Mon", "☐ ☐"), ("Tue", "☐ ☐"), ("Wed", "☐ ☐"), ("Thu", "☐ ☐"), ("Fri", "☐ ☐")], vf="400 34px/1 Jost")),
    ("useful", "emergency", dict(head="Babysitter info", line="Thank you for watching our kids!", name="The Garcias", phone=""), dict(icon="baby", rows=[("Mom", ""), ("Dad", ""), ("Doctor", ""), ("Bedtime", "8 pm"), ("Allergies", "")])),
    ("fun", "blobs", dict(head="Emma’s\nart gallery", line="Masterpieces on display", name="Artist: Emma, age 6", phone="★"), dict(icon="brush")),
    ("fun", "jersey", dict(name="Leo", sub="RIVERSIDE TIGERS", line="#1 fan: Mom"), dict(year="7")),
    ("name", "L_classic", dict(name="Olivia", sub="OUR LITTLE BLESSING", line="March 14, 2026", phone="♥"), dict(icon="il:baby", font="400 80px/1.1 'Dancing Script'")),
])
pset("p-grandparents", "Grandparents", "heart", ["blush", "sage", "ivory", "terracotta", "navy"], [
    ("name", "L_classic", dict(name="Grandma’s Kitchen", sub="LOVE IS THE SECRET INGREDIENT", line="Open all day, every day", phone="♥"), dict(icon="il:cake", font="400 58px/1.1 'Dancing Script'")),
    ("name", "kraft", dict(name="Nana & Papa", sub="EST. 1972", head="Spoiling\ngrandkids\nsince 2010.", line="", phone="♥"), {}),
    ("name", "label", dict(name="Grandpa’s Rules", sub="NO RULES HERE", since="EST. 1970", line="Ask Grandma for everything", phone="♥"), {}),
    ("name", "floral", dict(sub="WELCOME TO", name="Abuela’s House", line="Where cookies are always ready", phone="♥"), {}),
    ("name", "diner", dict(sub="OPEN 24/7", name="Grandma’s Diner", line="Hugs free · Cookies free · Love free", phone="Since 1972"), {}),
    ("photo", "W_polaroid", dict(head="Grandma & Grandpa", date="SINCE 1972", line="OUR FAVORITE PEOPLE"), dict(photo="stock:grandparents-1")),
    ("photo", "archphoto", dict(name="Nana & Papa", sub="LOVE YOU BIG", phone="♥"), dict(photo="stock:grandparents-2")),
    ("photo", "frame", dict(name="Best grandparents ever", sub="LOVE, THE GRANDKIDS", phone="2026"), dict(photo="stock:grandparents-3")),
    ("gift", "L_thanks", dict(head="We love you, Grandma!", line="Happy Grandparents Day", name="Emma, Leo & Sofia", phone="2026"), dict(icon="heart", font="400 64px/1.1 'Dancing Script'")),
    ("useful", "emergency", dict(head="Important numbers", line="For Grandma & Grandpa", name="Family", phone=""), dict(icon="heart", rows=[("Emergency", "911"), ("Maria (daughter)", ""), ("Dr. Patel", ""), ("Pharmacy", ""), ("Neighbor", "")])),
])
pset("p-kitchen", "Kitchen & family traditions", "plate", ["red", "sun", "terracotta", "cream", "forest", "orange"], [
    ("fun", "L_word", dict(sub="AT THE GARCIAS’", head="Pizza\nFriday!", line="Every Friday since forever.", name="The Garcias", phone="★"), dict(icon="il:pizza")),
    ("fun", "L_word", dict(sub="AT THE REYES HOUSE", head="Taco\nTuesday", line="Bring your appetite.", name="The Reyes", phone="★"), dict(icon="il:taco")),
    ("fun", "diner", dict(sub="FAMILY RECIPE", name="Mom’s Kitchen", line="Best food in town, no reservations", phone="Since 1998"), {}),
    ("fun", "neon", dict(sub="OPEN", name="Kitchen", head="Mom’s rules", line="", phone="EAT · LOVE · REPEAT"), {}),
    ("fun", "chalk", dict(name="Family menu", head="This week", phone="♥"), dict(icon="chef", rows=[("Monday", "Tacos"), ("Tuesday", "Pasta"), ("Wednesday", "Leftovers"), ("Thursday", "Soup"), ("Friday", "Pizza!")])),
    ("useful", "menu", dict(name="Dinner plan", sub="THE GARCIA KITCHEN", head="This week", line="Grocery day: Sunday", phone="♥"), dict(icon="chef", rows=[("Mon", ""), ("Tue", ""), ("Wed", ""), ("Thu", ""), ("Fri", "")])),
    ("useful", "receipt", dict(name="Grocery list", sub="DON’T FORGET", head="Thanks, love!", phone=""), dict(icon="tag", rows=[("Milk", ""), ("Eggs", ""), ("Bread", ""), ("Coffee", "")])),
    ("fun", "kraft", dict(name="Grandma’s Recipe", sub="SECRET INGREDIENT", head="Love", line="And a little butter", phone="♥"), {}),
    ("fun", "bubble", dict(head="What’s for dinner?", line="Ask the cook. Nicely.", name="The Chef", phone="Mom"), dict(icon="il:burger")),
    ("fun", "burst", dict(kicker="TODAY ONLY", offer="FREE", head="hugs from the cook", name="Mom’s Kitchen", phone="♥"), dict(icon="il:cake")),
])
pset("p-love", "Love & couples", "heart", ["blush", "black", "burgundy", "ivory", "plum"], [
    ("name", "monodate", dict(sub="MR & MRS", a="Ana", b="Leo", date="06 · 14 · 2025", place="Our forever starts here"), {}),
    ("name", "L_mono", dict(mono="A&L", name="ANA & LEO", sub="Est. 2025", phone="06 · 14 · 2025", web="♥"), dict(ms=72)),
    ("name", "invite", dict(sub="HAPPY ANNIVERSARY", head="Ana & Leo", date="10 YEARS", line="Still my favorite"), {}),
    ("photo", "W_polaroid", dict(head="Us. Always.", date="06.14.25", line="ANA & LEO"), dict(photo="stock:couple-1")),
    ("photo", "photocircle", dict(head="Ana & Leo", line="EST. 2025"), dict(photo="stock:couple-3")),
    ("photo", "film", dict(head="Our story", line="2019 · 2025 · FOREVER"), dict(photo="stock:couple-4")),
    ("photo", "magazine", dict(name="Us", sub="ANNIVERSARY ISSUE", head="10 years\nof love", line="And counting", phone="♥"), dict(photo="stock:engagement-4")),
    ("fun", "neon", dict(sub="SINCE 2019", name="You & me", head="Always", line="", phone="♥"), {}),
    ("gift", "L_thanks", dict(head="I love you", line="More than coffee. And that’s a lot.", name="Your favorite person", phone="♥"), dict(icon="heart", font="400 90px/1.1 'Dancing Script'")),
])
pset("p-faith", "Faith & home blessings", "cross", ["ivory", "sage", "navy", "blush", "terracotta"], [
    ("name", "L_classic", dict(name="Bless this home", sub="THE GARCIA FAMILY", line="As for me and my house, we will serve the Lord", phone="Joshua 24:15"), dict(icon="cross", font="400 64px/1.1 'Dancing Script'")),
    ("name", "floral", dict(sub="BLESSED", name="Grateful & thankful", line="Give thanks in all circumstances", phone="1 Thess. 5:18"), {}),
    ("name", "watercolor", dict(name="Be still", sub="PSALM 46:10", line="and know that I am God", phone="♥", web=""), dict(icon="il:flowers")),
    ("name", "kraft", dict(name="Faith", sub="HOPE · LOVE", head="The greatest\nof these\nis love.", line="1 Corinthians 13:13", phone="♥"), {}),
    ("name", "crest", dict(mono="†", name="THE GARCIAS", sub="Bless this home", phone="Est. 2015"), {}),
    ("gift", "L_thanks", dict(head="Happy Baptism", line="Sofia · April 2027", name="With love, Godmother", phone="♥"), dict(icon="cross", font="400 74px/1.1 'Dancing Script'")),
    ("gift", "invite", dict(sub="FIRST COMMUNION", head="Mateo", date="05 · 02 · 2027", line="St. Mary’s Church"), {}),
])
pset("p-teacher", "Teachers & coaches", "apple", ["sun", "red", "sky", "forest", "navy"], [
    ("gift", "L_thanks", dict(head="Thank you, Ms. Rivera!", line="For a wonderful year. Love, Emma", name="2nd grade · 2026–27", phone="★"), dict(icon="il:school", font="400 60px/1.1 'Dancing Script'")),
    ("gift", "blobs", dict(head="Best teacher\never!", line="Thank you for everything", name="Love, Room 12", phone="★"), dict(icon="il:school")),
    ("gift", "jersey", dict(name="Coach Mike", sub="THANKS, COACH!", line="Riverside Tigers · 2027"), dict(year="1")),
    ("gift", "seal", dict(name="Ms. Rivera", sub="TEACHER OF THE YEAR", phone="Room 12"), dict(icon="il:school")),
    ("useful", "checklist", dict(head="Classroom rules", line="Room 12 · Ms. Rivera", name="Ms. Rivera", phone="★"), dict(icon="apple", rows=[("Be kind", ""), ("Raise your hand", ""), ("Try your best", ""), ("Clean up", ""), ("Have fun", "")])),
    ("gift", "ticket", dict(kicker="COUPON", offer="1 FREE", head="homework pass", name="Ms. Rivera", phone="Room 12", line="Valid any day"), dict(icon="apple")),
])
pset("p-sports", "Sports fans", "star", ["navy", "red", "forest", "black", "orange"], [
    ("fun", "jersey", dict(name="Garcia", sub="RIVERSIDE TIGERS", line="#1 fan"), dict(year="10")),
    ("fun", "L_useful", dict(head="Tigers 2027", line="Game days, all season", name="Go Tigers!", phone="Leo #10"), dict(icon="star", rows=[("Sep 6", "vs Eagles"), ("Sep 13", "at Falcons"), ("Sep 20", "vs Comets"), ("Sep 27", "at Rangers")], vf="500 25px Jost")),
    ("fun", "bigtype", dict(sub="GAME DAY", head="Go\nTigers!", line="Riverside · Fall 2027", date="#10"), {}),
    ("photo", "magazine", dict(name="Leo #10", sub="ALL-STAR", head="Player of\nthe week", line="Riverside Tigers", phone="2027"), dict(photo="stock:football-2")),
    ("photo", "frame", dict(name="Sofia · #7", sub="SOCCER STAR", phone="2027"), dict(photo="stock:football-4")),
])
pset("p-holidays", "Holidays & seasons", "gift", ["forest", "red", "navy", "black", "orange"], [
    ("gift", "wreath", dict(head="Merry Christmas", line="Love, the Garcia family", name="2026", phone="♥"), {}),
    ("gift", "L_thanks", dict(head="Happy Thanksgiving", line="Grateful for family and pie.", name="The Garcias", phone="2026"), dict(icon="leaf", font="400 66px/1.1 'Dancing Script'", pal="terracotta")),
    ("gift", "L_thanks", dict(head="Cheers to 2027", line="Happy New Year from our family to yours.", name="The Garcias", phone="♥"), dict(icon="cheers", font="400 74px/1.1 'Dancing Script'", pal="black")),
    ("gift", "W_photo", dict(head="Merry & bright", line="THE GARCIAS · 2026"), dict(photo="stock:christmas-family-1")),
    ("gift", "film", dict(head="Happy holidays", line="THE GARCIA FAMILY · 2026"), dict(photo="stock:christmas-family-3")),
    ("fun", "bigtype", dict(sub="DEAR SANTA", head="We were\ngood.\nMostly.", line="The Garcia kids", date="2026"), dict(pal="red")),
])
pset("p-travel", "Trips & places", "pin", ["aqua", "sky", "sun", "terracotta", "navy"], [
    ("photo", "W_photo", dict(head="Garcia Beach Week", line="OUTER BANKS · SUMMER 2027"), dict(photo="stock:beach-3", font="400 60px/1.1 'Dancing Script'")),
    ("photo", "stamp", dict(name="Outer Banks", sub="Summer 2027", since="NC", phone="THE GARCIAS"), dict(icon="sun")),
    ("photo", "W_polaroid", dict(head="Best trip ever", date="07 · 2027", line="TULUM, MEXICO"), dict(photo="stock:travel-2")),
    ("photo", "magazine", dict(name="Vacation", sub="FAMILY EDITION", head="Sun, sand\n& us", line="Outer Banks 2027", phone="♥"), dict(photo="stock:beach-1")),
    ("fun", "pin", dict(head="We were here", name="Outer Banks", line="The Garcia family · 2027", phone="35.5°N 75.5°W"), dict(icon="sun")),
    ("fun", "retro", dict(sub="GREETINGS FROM", name="Florida", line="The Garcias · Summer 2027", phone="☀"), {}),
])


# ---------------------------------------------------------------- more for the event pages
ESETS = []


def eset(key, page, name, icon, pals, recipes):
    ESETS.append(dict(key=key, page=page, name=name, icon=icon, pals=pals, recipes=recipes))


eset("w-more", "weddings", "More wedding designs", "rings", ["ivory", "blush", "sage", "black", "burgundy", "dusty"], [
    ("date", "invite", dict(sub="SAVE THE DATE", head="Olivia & Mateo", date="09 · 18 · 2027", line="Charleston, South Carolina"), {}),
    ("date", "monodate", dict(sub="SAVE THE DATE", a="Hannah", b="Luke", date="05 · 22 · 2027", place="Napa Valley, California"), {}),
    ("date", "floral", dict(sub="SAVE THE DATE", name="Sofia & Daniel", line="October 2, 2027 · Asheville", phone="Invitation to follow"), {}),
    ("date", "watercolor", dict(name="Ava & Noah", sub="SAVE THE DATE", line="June 12, 2027 · Chicago", phone="Invitation to follow", web=""), dict(icon="il:rings")),
    ("date", "deco", dict(mono="A&J", name="ALEX & JORDAN", sub="August 21, 2027", phone="Lake Tahoe"), dict(ms=60)),
    ("date", "crest", dict(mono="C&L", name="CAMILA & LUCAS", sub="Save the date", phone="04 · 24 · 2027"), {}),
    ("date", "neon", dict(sub="SAVE THE DATE", name="Mia & Carlos", head="We’re getting married!", line="", phone="05.15.27"), {}),
    ("date", "kraft", dict(name="Grace & Owen", sub="SAVE THE DATE", head="We’re tying\nthe knot!", line="10 · 30 · 2027 · Nashville", phone="♥"), {}),
    ("date", "retro", dict(sub="SAVE THE DATE", name="Kate & Ben", line="09 · 09 · 2027 · Austin, TX", phone="♥"), {}),
    ("photo", "photocircle", dict(head="Save the date", line="NINA & MARCO · 08.14.27"), dict(photo="stock:wedding-1")),
    ("photo", "film", dict(head="We said yes!", line="LUCY & SAM · 05.29.27"), dict(photo="stock:engagement-1")),
    ("photo", "archphoto", dict(name="Ella & James", sub="SAVE THE DATE", phone="09 · 25 · 2027"), dict(photo="stock:wedding-5")),
    ("photo", "magazine", dict(name="Just Married", sub="THE WEDDING ISSUE", head="Ana & Leo", line="June 14, 2027", phone="♥"), dict(photo="stock:wedding-3")),
    ("thanks", "L_thanks", dict(head="Thank you", line="For celebrating our day with us.", name="Mia & Carlos", phone="05 · 15 · 2027"), dict(icon="heart", font="400 96px/1.1 'Dancing Script'")),
    ("thanks", "seal", dict(name="Thank you", sub="ANA & LEO · 2027", phone="06 · 14 · 27"), dict(icon="il:rings")),
    ("thanks", "label", dict(name="Ana & Leo", sub="THANK YOU", since="06 · 14 · 2027", line="Love is sweet, take a treat", phone="♥"), {}),
    ("qr", "qrbig", dict(head="RSVP here", line="Scan for details, registry and RSVP.", name="Kate & Ben"), dict(icon="il:rings")),
    ("qr", "qrphone", dict(head="Share your\nphotos!", line="Scan to add your pictures to our album.", name="Ana & Leo", web="#AnaAndLeo2027"), dict(icon="il:rings")),
    ("party", "bigtype", dict(sub="BRIDAL SHOWER", head="Bride\nto be", line="Celebrating Isabella", date="03 · 06 · 27"), {}),
    ("party", "blobs", dict(head="Bachelorette\nweekend!", line="Nashville · May 2027", name="Team Bride", phone="♥"), dict(icon="cheers")),
])
eset("g-more", "graduation", "More graduation designs", "cap", ["navy", "black", "burgundy", "forest", "red", "sun"], [
    ("date", "jersey", dict(name="Ellis", sub="CLASS OF 2027", line="Lincoln High School"), dict(year="27")),
    ("date", "seal", dict(name="Class of 2027", sub="CONGRATULATIONS", phone="JORDAN ELLIS"), dict(icon="il:cap")),
    ("date", "crest", dict(mono="27", name="JORDAN ELLIS", sub="Class of 2027", phone="Lincoln High School"), {}),
    ("date", "deco", dict(mono="’27", name="MIA THOMPSON", sub="University of Georgia", phone="Class of 2027"), {}),
    ("date", "ribbon", dict(name="Class of 2027", sub="CONGRATULATIONS, GRAD!", line="Ethan Brooks · Nursing BSN", phone="★"), dict(icon="il:cap")),
    ("date", "neon", dict(sub="CLASS OF", name="Sophia", head="2027", line="", phone="WE DID IT!"), {}),
    ("photo", "photocircle", dict(head="Congrats, Grad!", line="SOPHIA · CLASS OF 2027"), dict(photo="stock:grad-girl-1")),
    ("photo", "magazine", dict(name="Grad 2027", sub="THE GRADUATE", head="Marcus did\nit!", line="Jefferson High", phone="★"), dict(photo="stock:grad-3")),
    ("photo", "film", dict(head="Proud of you!", line="MARIA · CLASS OF 2027"), dict(photo="stock:grad-girl-4")),
    ("photo", "archphoto", dict(name="Jordan Ellis", sub="CLASS OF 2027", phone="Lincoln High"), dict(photo="stock:grad-1")),
    ("party", "bigtype", dict(sub="YOU’RE INVITED", head="Grad\nparty!", line="Celebrating Marcus", date="06 · 05 · 27"), {}),
    ("party", "blobs", dict(head="Party time!", line="Maya’s graduation party · June 12", name="Garcia home", phone="4 pm"), dict(icon="il:cap")),
    ("thanks", "L_thanks", dict(head="Thank you!", line="For celebrating with me.", name="Jordan · Class of 2027", phone="★"), dict(icon="il:cap", font="400 92px/1.1 'Dancing Script'")),
    ("qr", "qrbig", dict(head="Party details", line="Scan for time, place and the map.", name="Maya’s grad party"), dict(icon="il:cap")),
])
eset("x-more", "parties", "More party designs", "balloon", ["pink", "sky", "sun", "black", "lilac", "orange", "mint"], [
    ("party", "blobs", dict(head="Leo is 5!", line="Thanks for coming to my party!", name="Leo’s Dino Party", phone="April 3"), dict(icon="il:balloons")),
    ("party", "neon", dict(sub="LET’S PARTY", name="Emma turns 30", head="Dirty thirty", line="", phone="03.12.27"), {}),
    ("party", "bigtype", dict(sub="SWEET SIXTEEN", head="Chloe\nturns 16!", line="Thank you for coming", date="06 · 19 · 27"), {}),
    ("party", "retro", dict(sub="CHEERS TO", name="50 years", line="Robert’s birthday bash · 2027", phone="★"), {}),
    ("party", "diner", dict(sub="CELEBRATING", name="Grandma Rosa", line="90 years young · Thank you for coming", phone="2027"), {}),
    ("photo", "W_polaroid", dict(head="Welcome, baby Mia", date="02.21.27", line="BABY SHOWER"), dict(photo="stock:baby-4")),
    ("photo", "film", dict(head="Garcia Reunion", line="LAKE LANIER · 2027"), dict(photo="stock:family-6")),
    ("photo", "photocircle", dict(head="Happy retirement, Linda!", line="32 YEARS · 2027"), dict(photo="stock:party-2")),
    ("photo", "magazine", dict(name="Fiesta!", sub="FAMILY REUNION", head="The Garcias\n2027", line="Thanks for coming", phone="♥"), dict(photo="stock:party-1")),
    ("thanks", "seal", dict(name="Thank you", sub="BABY JOHNSON · 2027", phone="With love"), dict(icon="il:baby")),
    ("thanks", "L_thanks", dict(head="Happy holidays", line="Thanks for an amazing year, team!", name="Brightline Holiday Party", phone="December 17"), dict(icon="gift", font="400 80px/1.1 'Dancing Script'")),
    ("qr", "qrphone", dict(head="Share your\nphotos!", line="Scan and add your pictures to the party album.", name="Summit 2027", web="#Summit2027"), dict(icon="il:balloons")),
    ("qr", "qrbig", dict(head="The agenda", line="Speakers, Wi-Fi and the map.", name="Summit 2027"), dict(icon="building")),
])


# ---------------------------------------------------------------- Personalize: each theme's words in many more layouts
# (name, small line, sentence, signature or date, initials): every field different, so nothing repeats on a magnet
PWORDS = {
    "p-family": [("The Garcias", "EST. 2015", "Love lives here", "Ana · Carlos · Sofia · Leo", "G"),
                 ("The Johnson Family", "EST. 2009", "Home is where our story begins", "Mike & Jen", "J"),
                 ("Familia Silva", "DESDE 2012", "Aqui mora o amor", "Paulo & Rita", "S"),
                 ("The Nguyens", "EST. 2018", "Together is our favorite place", "Ben · Mai · Lily", "N"),
                 ("The Millers", "HOME SWEET HOME", "Kind words, warm hugs, full plates", "Since 2004", "M")],
    "p-home": [("Home Sweet Home", "1412 MAGNOLIA LANE", "Where our story begins", "The Parkers · 2026", "P"),
               ("Our First Home", "OAK STREET · 2026", "Keys, boxes and a whole lot of love", "Josh & Emily", "K"),
               ("The Smiths", "12 MAPLE AVENUE", "Welcome, friends", "Est. 2024", "S"),
               ("Welcome Home", "LAKE COTTAGE", "Kick off your shoes and stay a while", "The Kims", "K")],
    "p-pets": [("Max", "GOOD BOY", "Treats accepted at all times", "Adopted 2024", "M"),
               ("Luna", "QUEEN OF THE HOUSE", "Spoiled and proud of it", "Since 2022", "L"),
               ("Bella", "BEST FRIEND", "Home is where my dog is", "Gotcha day · 05.12.23", "B"),
               ("Oliver", "THE CAT IN CHARGE", "We just live here", "Est. 2021", "O"),
               ("Cooper & Daisy", "PARTNERS IN CRIME", "Two tails, one couch", "The Garcia pups", "CD")],
    "p-baby": [("Olivia Rose", "BORN 03.14.26", "7 lb 2 oz · 20 inches of love", "Welcome to the world", "OR"),
               ("Baby Leo", "OUR LITTLE BLESSING", "The newest Garcia has arrived", "June 2, 2026", "L"),
               ("Emma’s Room", "ARTIST AT WORK", "Masterpieces on display", "Emma, age 6", "E"),
               ("Hello, Noah", "BORN 11.20.26", "Tiny hands, big love", "Love, Mom & Dad", "N")],
    "p-grandparents": [("Grandma’s Kitchen", "LOVE IS THE SECRET INGREDIENT", "Cookies always in the oven", "Since 1972", "G"),
                       ("Nana & Papa", "EST. 1972", "Spoiling grandkids since 2010", "Emma · Leo · Sofia", "NP"),
                       ("Abuela’s House", "CON MUCHO AMOR", "Where the coffee is always on", "Familia Garcia", "A"),
                       ("Grandpa’s Garage", "FIXING THINGS SINCE 1965", "Ask him, he knows", "Love, the grandkids", "G")],
    "p-kitchen": [("Pizza Friday", "AT THE GARCIAS’", "Every Friday since forever", "Extra cheese, always", "P"),
                  ("Mom’s Kitchen", "FAMILY RECIPES", "No reservations needed", "Est. 1998", "M"),
                  ("Taco Tuesday", "AT THE REYES HOUSE", "Bring your appetite", "Salsa on the side", "T"),
                  ("Sunday Supper", "THE MILLER TABLE", "Everyone welcome, nobody leaves hungry", "Every week since 1990", "S")],
    "p-love": [("Ana & Leo", "EST. 2025", "Our forever starts here", "06 · 14 · 2025", "A&L"),
               ("Mr & Mrs Park", "JUST MARRIED", "Still my favorite", "09 · 20 · 2026", "P"),
               ("You & Me", "SINCE 2019", "Always and forever", "Kate & Sam", "K&S"),
               ("Happy Anniversary", "10 YEARS", "And I’d choose you again", "Love, Mark", "10")],
    "p-faith": [("Bless This Home", "THE GARCIA FAMILY", "As for me and my house, we will serve the Lord", "Joshua 24:15", "†"),
                ("Grateful", "THANKFUL · BLESSED", "Give thanks in all circumstances", "1 Thess. 5:18", "G"),
                ("Faith Over Fear", "ISAIAH 41:10", "Do not fear, for I am with you", "The Johnsons", "F"),
                ("Be Still", "PSALM 46:10", "and know that I am God", "Bless this home", "†")],
    "p-teacher": [("Ms. Rivera", "ROOM 12 · 2026–27", "Thank you for a wonderful year", "Love, Emma", "R"),
                  ("Coach Mike", "RIVERSIDE TIGERS", "Thanks for believing in us", "Team 2027", "M"),
                  ("Mrs. Lee", "TEACHER OF THE YEAR", "You make learning fun", "Love, Room 4", "L")],
    "p-sports": [("Go Tigers!", "RIVERSIDE · FALL 2027", "Loud and proud in the stands", "#10 Leo Garcia", "T"),
                 ("Soccer Mom", "WESTVIEW WILDCATS", "Snacks, cheers and a cold coffee", "#7 Sofia", "W"),
                 ("Game Day", "CENTRAL EAGLES", "Let’s go, Eagles!", "Season 2027", "E")],
    "p-holidays": [("Merry Christmas", "THE GARCIAS · 2026", "Peace, love and cookies", "Ana · Carlos · Sofia · Leo", "G"),
                   ("Happy Thanksgiving", "GRATEFUL · 2026", "Pass the pie, please", "The Millers", "M"),
                   ("Happy Easter", "HE IS RISEN", "Hope, joy and chocolate", "Love, the Garcias", "G"),
                   ("Happy New Year", "CHEERS TO 2027", "Here’s to another year together", "The Johnsons", "27")],
    "p-travel": [("Outer Banks", "SUMMER 2027", "Sun, sand and us", "The Garcia family", "OB"),
                 ("Disney 2027", "OUR FAMILY TRIP", "The best week ever", "The Johnsons", "D"),
                 ("Tulum", "MEXICO · 2027", "Salt in the air, sand in our hair", "Ana & Leo", "T"),
                 ("Grand Canyon", "ROAD TRIP 2027", "2,000 miles and zero regrets", "The Parkers", "GC")],
}
PICON = {"p-family": "il:house", "p-home": "il:keyhouse", "p-pets": "il:dog", "p-baby": "il:baby", "p-grandparents": "heart", "p-kitchen": "il:pizza", "p-love": "heart",
         "p-faith": "cross", "p-teacher": "il:school", "p-sports": "star", "p-holidays": "gift", "p-travel": "sun"}


def _pl(lay, n, sub, line, foot, mono):
    """The words of one Personalize wording in one layout."""
    two = n.replace(" ", "\n", 1) if len(n) > 9 and " " in n else n
    return {
        "L_classic": dict(name=n, sub=sub, line=line, phone=foot),
        "crest": dict(mono=mono, name=n.upper(), sub=line if len(line) < 34 else sub.title(), phone=foot),
        "label": dict(since=sub, name=n, sub=foot.upper()[:22], line=line, phone=""),
        "ribbon": dict(name=n, sub=sub, line=line, phone=foot),
        "seal": dict(name=n, sub=sub, phone=foot),
        "watercolor": dict(name=n, sub=sub, line=line, phone=foot, web=""),
        "floral": dict(sub=sub, name=n, line=line, phone=foot),
        "minimal": dict(name=n, sub=sub, phone=line, web=foot),
        "stamp": dict(name=n, sub=foot, since=sub, phone=""),
        "geo": dict(name=n, sub=sub, line=line, phone=foot),
        "L_mono": dict(mono=mono, name=n.upper(), sub=line if len(line) < 30 else sub.title(), phone=foot, web=""),
        "deco": dict(mono=mono, name=n.upper(), sub=sub.title(), phone=foot),
        "hero": dict(name=n, sub=sub, phone=foot),
        "retro": dict(sub=sub, name=n, line=line, phone=foot),
        "diner": dict(sub=sub, name=n, line=line, phone=foot),
        "neon": dict(sub=sub, name=n, head=foot if len(foot) <= 18 else "", line="", phone="" if len(foot) <= 18 else foot),
        "duo": dict(sub=sub, head=two, line=line, name=foot, phone=""),
        "diagonal": dict(name=sub, head=two, line=line, sub="", phone=foot),
        "wave": dict(name=foot, sub=sub, head=two, line=line, phone=""),
        "blobs": dict(head=two, line=line, name=foot, phone=sub.title()),
        "bigtype": dict(sub=sub, head=two, line=line, date=foot),
        "invite": dict(sub=sub, head=n, date=foot, line=line),
        "monodate": dict(sub=sub, a=n.split(" & ")[0] if " & " in n else n, b=n.split(" & ")[1] if " & " in n else "", date=foot, place=line),
    }[lay]


PLAYS = ["L_classic", "crest", "label", "ribbon", "seal", "watercolor", "floral", "minimal", "stamp", "geo", "L_mono", "deco", "hero", "retro", "diner",
         "neon", "duo", "diagonal", "wave", "blobs", "bigtype", "invite"]
PFUN = {"retro", "diner", "neon", "blobs", "bigtype", "diagonal"}


def personal_more(p):
    """A theme's wordings in the Personalize layouts: each wording in its own run of about 13 layouts."""
    out = []
    ic = PICON.get(p["key"], "heart")
    for wi, (n, sub, line, foot, mono) in enumerate(PWORDS.get(p["key"], [])):
        for li in range(13):
            lay = PLAYS[(wi * 9 + li * 5) % len(PLAYS)]
            if lay == "invite" and p["key"] not in ("p-love", "p-baby", "p-holidays", "p-faith"):
                lay = "monodate" if p["key"] == "p-love" else "L_classic"
            w = _pl(lay, n, sub, line, foot, mono)
            out.append(("fun" if lay in PFUN else "name", lay, w, dict(icon=ic)))
    seen, uniq = set(), []
    for r in out:   # the same wording in the same layout only once
        key = (r[1], r[2].get("name"), r[2].get("head"))
        if key not in seen:
            seen.add(key); uniq.append(r)
    return uniq


# ---------------------------------------------------------------- search words: what people type (English and Portuguese)
PT = {"pizza": "pizzaria", "mexican": "taqueria comida mexicana tacos", "burger": "hamburgueria lanchonete hamburguer", "cafe": "cafeteria cafe padaria",
      "bakery": "padaria confeitaria bolos doces", "sushi": "japones sushi chines comida asiatica", "bbq": "churrasco churrascaria food truck",
      "icecream": "sorveteria sorvete doceria", "restaurant": "restaurante comida", "catering": "buffet bufe eventos comida",
      "dentist": "dentista odontologia consultorio dentario", "ortho": "ortodontista aparelho dental", "doctor": "medico clinica consultorio",
      "pediatrics": "pediatra medico de criancas", "chiro": "quiropraxia quiropraxista coluna", "pt": "fisioterapia fisioterapeuta",
      "eyes": "oculista otica oftalmologista oculos", "pharmacy": "farmacia drogaria", "cleaning": "limpeza faxina diarista housekeeping",
      "hvac": "ar condicionado aquecimento", "plumber": "encanador bombeiro hidraulico", "electric": "eletricista", "roofing": "telhado telhadista",
      "lawn": "jardinagem jardineiro grama paisagismo", "pest": "dedetizacao dedetizadora", "pool": "piscina piscineiro", "moving": "mudanca mudancas",
      "handyman": "faz tudo marido de aluguel reparos", "painter": "pintor pintura", "locksmith": "chaveiro", "realtor": "corretor imobiliaria imoveis",
      "mortgage": "financiamento credito imobiliario", "insurance": "seguro seguros corretora de seguros", "tax": "contador contabilidade imposto",
      "lawyer": "advogado advocacia", "financial": "consultor financeiro investimentos", "salon": "salao cabeleireiro cabelo",
      "barber": "barbearia barbeiro", "nails": "manicure unhas esmalteria", "medspa": "estetica clinica de estetica botox",
      "massage": "massagem massoterapia spa", "gym": "academia", "yoga": "ioga pilates", "trainer": "personal trainer treinador",
      "tattoo": "tatuagem tatuador", "vet": "veterinario clinica veterinaria", "groomer": "banho e tosa pet shop", "petsitter": "passeador de caes pet sitter",
      "dogtrainer": "adestrador adestramento", "autorepair": "oficina mecanico mecanica", "tires": "pneus borracharia", "detailing": "lava jato estetica automotiva lavagem",
      "towing": "guincho reboque", "church": "igreja pastor ministerio culto", "nonprofit": "ong caridade instituicao", "school": "escola creche",
      "tutor": "aula particular reforco professor", "team": "time esporte futebol liga", "dance": "danca escola de musica aula de musica",
      "florist": "floricultura flores", "photographer": "fotografo fotografia", "boutique": "loja boutique presentes", "eventvenue": "salao de festas cerimonial eventos",
      "dj": "dj som festa", "general": "outro outros geral qualquer qualquer negocio empresa other any general business generic",
      "startup": "negocio novo pequeno empreendedor artesanato loja online etsy side hustle small business handmade new", "p-family": "familia sobrenome", "p-home": "casa nova lar", "p-pets": "cachorro gato pet animal", "p-baby": "bebe criancas filhos",
      "p-grandparents": "avo avos vovo vovo", "p-kitchen": "cozinha receita jantar", "p-love": "casal amor aniversario de casamento namorados",
      "p-faith": "fe religiao biblia deus", "p-teacher": "professor professora treinador", "p-sports": "esporte time torcedor",
      "p-holidays": "natal pascoa feriados ação de gracas", "p-travel": "viagem ferias praia"}


def words_for(k):
    """The words that find a kind of business in the search box."""
    return " ".join([k["key"], k["name"], k["group"], k["sub"].lower(), " ".join(k["services"]).lower(), PT.get(k["key"], "")])
