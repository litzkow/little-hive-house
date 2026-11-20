"""The style gallery for the bulk pages (business, weddings, graduation, parties): example magnets for many kinds
of businesses and events. Fictional names, 555 phone numbers; every sample QR opens our own page.

  python3 tools/biz_designs.py            renders every design missing in assets/occasions/ (600x600 webp)
  python3 tools/biz_designs.py all        renders all of them again
  python3 tools/biz_designs.py a b c      renders only these slugs
  python3 tools/biz_designs.py sheet      also writes /tmp/biz_sheet_<page>.png contact sheets to review

build.py reads GALLERY (slug, page, group, title) to show the gallery and the style picker. Rendering needs
google-chrome and node (for the real QR codes, assets/qr.js); building the site does not."""
import hashlib
import os, sys, json, subprocess, tempfile, pathlib, html
from concurrent.futures import ThreadPoolExecutor

ROOT = pathlib.Path(__file__).resolve().parent.parent
F = ROOT / "tools" / "fonts"
OUT = ROOT / "assets" / "occasions"
SC = ROOT / "assets" / "showcase"
E = html.escape

SITE = "https://littlehivehouse.com/"

# ---------------------------------------------------------------- palettes
P = {
    "navy":   dict(bg="#13294B", ink="#FFFFFF", ac="#F2A81D", soft="#21406B"),
    "teal":   dict(bg="#E5F3F1", ink="#18423C", ac="#1F8A7A", soft="#BFE3DD"),
    "mint":   dict(bg="#F1FAF6", ink="#1C3D35", ac="#2EA37A", soft="#CDEEDF"),
    "sky":    dict(bg="#EAF4FB", ink="#12324D", ac="#2B7BBF", soft="#C9E2F4"),
    "red":    dict(bg="#B3261E", ink="#FFF6E8", ac="#FFD166", soft="#C9473E"),
    "brick":  dict(bg="#7A2E1F", ink="#FBEFD9", ac="#E9B44C", soft="#8E3C2A"),
    "cream":  dict(bg="#FBF4E6", ink="#2B2118", ac="#B5462F", soft="#EBDDC2"),
    "sage":   dict(bg="#EEF0E6", ink="#2E3B2B", ac="#5B7A4E", soft="#D6DEC8"),
    "forest": dict(bg="#173B2C", ink="#F4EFE3", ac="#C9A227", soft="#245040"),
    "black":  dict(bg="#151515", ink="#F5F0E6", ac="#D9B26F", soft="#2A2A2A"),
    "blush":  dict(bg="#F7E8E4", ink="#4A2F2B", ac="#C0756A", soft="#EDD2CB"),
    "plum":   dict(bg="#3D1E3B", ink="#FBEFF5", ac="#E8A0BF", soft="#552A52"),
    "lilac":  dict(bg="#F1EBF8", ink="#33224D", ac="#7B5BB0", soft="#DCD0EE"),
    "sun":    dict(bg="#FFD23F", ink="#1D1D1D", ac="#1D1D1D", soft="#FFE48A"),
    "orange": dict(bg="#FFF1E2", ink="#2A1A0E", ac="#E8641B", soft="#FFD9B5"),
    "lime":   dict(bg="#F4F9E3", ink="#25331A", ac="#5E8C1F", soft="#DDEBB5"),
    "gold":   dict(bg="#FFF8E7", ink="#2B2118", ac="#B8860B", soft="#F1E2BB"),
    "pink":   dict(bg="#FF5C8A", ink="#FFFFFF", ac="#2A0E1A", soft="#FF85A6"),
    "aqua":   dict(bg="#DFF6FB", ink="#0B3A4A", ac="#0096B4", soft="#B5E9F3"),
    "slate":  dict(bg="#2F3B48", ink="#F2F4F7", ac="#7FD1B9", soft="#3D4C5C"),
    "burgundy": dict(bg="#5B2333", ink="#F7EBDD", ac="#D9B26F", soft="#6E2E40"),
    "ivory":  dict(bg="#FAF6EF", ink="#3B3027", ac="#9A7B4F", soft="#E9DFCC"),
    "dusty":  dict(bg="#E9EEF2", ink="#2E3A46", ac="#6E8BA3", soft="#D3DDE5"),
    "terracotta": dict(bg="#F6E7DC", ink="#4A2A1C", ac="#C0603A", soft="#ECCFBC"),
}


def D(slug, page, group, title, layout, pal, **kw):
    d = dict(kw); d.update(slug=slug, page=page, group=group, title=title, layout=layout, pal=pal)
    return d


B = "business"
DESIGNS = [
    # ---- restaurants & food
    D("pizza-night", B, "Restaurants & food", "Pizza · Pizza night", "L_word", "red", icon="pizza", sub="FRESH FROM THE OVEN", head="Pizza<br>night?", line="Two large pizzas and garlic knots for $29, every Tuesday.", name="Tony’s Slice", phone="(555) 214-0190", word_c="#FFFFFF"),
    D("pizza-badge", B, "Restaurants & food", "Pizza · Retro badge", "L_badge", "cream", icon="pizza", name="Brooklyn Bros", sub="PIZZA · SINCE 1987", since="WOOD FIRED", line="Delivery & pickup until midnight", phone="(555) 214-0144"),
    D("pizza-coupon", B, "Restaurants & food", "Pizza · Fridge coupon", "L_coupon", "cream", icon="pizza", kicker="ON THE FRIDGE = ON THE TABLE", offer="$5 OFF", head="any large pizza, any day", name="Nonna Lucia", phone="(555) 214-0187", line="Show this magnet or use code FRIDGE5 · Expires 12/31/2027"),
    D("taco-tuesday", B, "Restaurants & food", "Mexican · Taco Tuesday", "L_word", "orange", icon="taco", sub="TAQUERÍA · FAMILY RECIPES", head="Taco<br>Tuesday", line="$2 street tacos all day. Catering for any party.", name="El Sol", phone="(555) 318-2024", word_c="#E8641B"),
    D("taco-hours", B, "Restaurants & food", "Mexican · Hours & menu", "L_hours", "terracotta", icon="taco", name="La Cocina", sub="AUTHENTIC MEXICAN KITCHEN", head="We’re open", rows=[("Mon – Thu", "11 am – 9 pm"), ("Fri – Sat", "11 am – 11 pm"), ("Sunday", "10 am – 8 pm"), ("Brunch", "Sat & Sun")], phone="(555) 318-7710", line="Order online", font="400 54px/1 DMSerif"),
    D("sushi-zen", B, "Restaurants & food", "Sushi & Asian · Minimal", "L_mono", "black", mono="鮨", ms=104, name="KAI SUSHI", sub="Omakase · Rolls · Ramen", phone="(555) 702-3388", web="kaisushibar.com"),
    D("ramen-qr", B, "Restaurants & food", "Asian · Scan for menu", "L_qr", "slate", icon="bowl", name="Noodle House", line="Hungry tonight?", head="Scan<br>for our<br>menu", phone="(555) 702-1150", web="noodlehouse.co"),
    D("cafe-punch", B, "Restaurants & food", "Café · Loyalty card", "L_punch", "sage", icon="cup", name="Little Fern Café", sub="COFFEE · TEA · PASTRIES", head="Buy 9, the 10th is on us", line="Show this magnet at the counter · (555) 410-7788"),
    D("cafe-badge", B, "Restaurants & food", "Café · Retro badge", "L_badge", "forest", icon="cup", name="Daily Grind", sub="COFFEE ROASTERS", since="EST. 2012", line="Open every day at 6 am", phone="(555) 410-2290"),
    D("bakery-classic", B, "Restaurants & food", "Bakery · Classic", "L_classic", "blush", icon="cake", name="Sweet Crumb", sub="CAKES · COOKIES · PIES", line="Custom cakes for every celebration", phone="(555) 266-1408", font="400 76px/1 Dancing"),
    D("bakery-punch", B, "Restaurants & food", "Bakery · Dozen club", "L_punch", "cream", icon="bread", name="Rise & Shine", sub="BAKERY · SOURDOUGH · COFFEE", head="Your 10th loaf is free", line="Fresh bread daily from 7 am · (555) 266-3317", font="400 52px/1 DMSerif"),
    D("foodtruck-qr", B, "Restaurants & food", "Food truck · Find us", "L_qr", "sun", icon="truck", name="Smokin’ Wheels BBQ", line="Where are we parked this week?", head="Scan to<br>find us", phone="(555) 909-4427", web="@smokinwheels", font="400 44px/1 Anton"),
    D("restaurant-hours", B, "Restaurants & food", "Restaurant · Specials", "L_hours", "navy", icon="chef", name="The Corner Table", sub="AMERICAN KITCHEN & BAR", head="This week’s specials", rows=[("Mon", "Burger + fries $12"), ("Wed", "Wing night 60¢"), ("Fri", "Fish fry"), ("Sun", "Kids eat free")], phone="(555) 830-4410", line="Reservations", font="400 50px/1 DMSerif"),

    # ---- health & dental
    D("dental-chart", B, "Health & dental", "Dental · Kids’ brushing chart", "L_useful", "sky", icon="tooth", head="2 minutes, twice a day", line="Check a box every time you brush!", rows=[("Mon", "☐ ☐"), ("Tue", "☐ ☐"), ("Wed", "☐ ☐"), ("Thu", "☐ ☐"), ("Fri", "☐ ☐")], vf="400 34px/1 Jost", pen="#2B7BBF", name="Happy Teeth Kids", phone="(555) 742-0190"),
    D("dental-coupon", B, "Health & dental", "Dental · New patient offer", "L_coupon", "teal", icon="tooth", kicker="NEW PATIENT SPECIAL", offer="$99", head="exam, X-rays and cleaning", name="Bright Side Dental", phone="(555) 742-1180", line="Most insurance accepted · Bring a friend, get $50 credit"),
    D("dental-qr", B, "Health & dental", "Dental · Book online", "L_qr", "mint", icon="tooth", name="Summit Family Dental", line="Time for your checkup?", head="Scan to<br>book", phone="(555) 742-3300", web="summitsmiles.com", font="400 40px/1 DMSerif"),
    D("ortho-word", B, "Health & dental", "Orthodontist · Smile", "L_word", "aqua", icon="tooth", sub="ORTHODONTICS · BRACES · ALIGNERS", head="Smile<br>bigger.", line="Free consultation and flexible payment plans.", name="Clear Path Ortho", phone="(555) 742-6006", word_c="#0096B4"),
    D("clinic-appt", B, "Health & dental", "Clinic · Next appointment", "L_appt", "dusty", icon="steth", name="OAKWOOD", sub="FAMILY MEDICINE", head="Your next visit", hand=("Thu, June 3", "9:15 am"), line="Need to reschedule? Call", phone="(555) 610-2044"),
    D("peds-appt", B, "Health & dental", "Pediatrics · Checkup", "L_appt", "lilac", icon="baby", name="Little Sprouts", sub="PEDIATRICS", head="Next checkup", hand=("Aug 12", "3:00 pm"), line="Nurse line, 24/7", phone="(555) 610-7878", font="400 46px/1 Dancing"),
    D("chiro-split", B, "Health & dental", "Chiropractor · Services", "L_split", "slate", icon="heart", since="EST. 2009", name="Align Chiropractic", sub="FEEL BETTER, MOVE BETTER", items=["Back & neck pain", "Sports injuries", "Massage therapy", "Same-day visits"], phone="(555) 610-9091", web="alignchiro.com"),
    D("eye-mono", B, "Health & dental", "Eye care · Elegant", "L_mono", "ivory", mono="CV", name="CLEARVIEW", sub="Eye care & eyewear", phone="(555) 610-3355", web="clearvieweyes.com"),

    # ---- home services
    D("clean-word", B, "Home services", "House cleaning · Sparkle", "L_word", "aqua", icon="sparkle", sub="HOUSE CLEANING · MOVE-OUT · OFFICES", head="Come home<br>to clean.", line="Weekly, every two weeks or once. Insured and background checked.", name="Sparkle & Co.", phone="(555) 377-2500", ws=104, word_c="#0B3A4A"),
    D("clean-coupon", B, "Home services", "House cleaning · First clean", "L_coupon", "lilac", icon="spray", kicker="NEW CLIENTS", offer="$40 OFF", head="your first deep clean", name="Fresh Nest Cleaning", phone="(555) 377-8181", line="Mention this magnet when you book · Expires 12/31/2027"),
    D("clean-split", B, "Home services", "House cleaning · Services", "L_split", "mint", icon="spray", since="LOCALLY OWNED", name="Maria’s Maids", sub="WE CLEAN, YOU RELAX", items=["Weekly & biweekly", "Deep cleaning", "Move-in, move-out", "Airbnb turnovers"], phone="(555) 377-6060", web="mariasmaids.com"),
    D("clean-useful", B, "Home services", "House cleaning · Checklist", "L_useful", "blush", icon="sparkle", head="Weekly reset", line="Our 10-minute-a-day list", rows=[("Mon", "Kitchen counters"), ("Tue", "Bathrooms"), ("Wed", "Dust & vacuum"), ("Thu", "Laundry"), ("Fri", "Floors")], vf="400 31px/1 Caveat", name="Shine Home Co.", phone="(555) 377-4422"),
    D("hvac-bar", B, "Home services", "HVAC · 24/7", "L_bar", "navy", icon="snow", name="Peach Valley Air", sub="HEATING · COOLING", head="No heat?<br>No AC?", line="We answer 24/7, holidays too.", phone="(555) 600-0198"),
    D("hvac-filter", B, "Home services", "HVAC · Filter log", "L_useful", "sky", icon="snow", head="Filter changes", line="Every 90 days. Write the date here.", rows=[("Size", "20 × 25 × 1"), ("Changed", "Jan 4"), ("Changed", "Apr 2"), ("Changed", ""), ("Tune-up", "Every spring")], kw=140, name="CoolBreeze HVAC", phone="(555) 600-2110"),
    D("plumber-hazard", B, "Home services", "Plumbing · Keep this number", "L_hazard", "sun", icon="drop", name="Rapid Rooter", sub="PLUMBING · DRAINS · WATER HEATERS", head="Leak? Clog? Flood?", phone="(555) 600-7700", line="24/7 emergency service · Licensed & insured", ac="#1D1D1D"),
    D("plumber-coupon", B, "Home services", "Plumbing · Coupon", "L_coupon", "sky", icon="wrench", kicker="SAVE ON YOUR NEXT CALL", offer="$50 OFF", head="any repair over $250", name="Blue Pipe Plumbing", phone="(555) 600-4410", line="Show this magnet to your technician · One per visit"),
    D("electric-bar", B, "Home services", "Electrician · Bold", "L_bar", "black", icon="bolt", name="Live Wire Electric", sub="RESIDENTIAL · COMMERCIAL", head="Lights out?<br>We’re on.", line="Panels, outlets, EV chargers, generators.", phone="(555) 600-3398", icon_c="#151515"),
    D("roof-split", B, "Home services", "Roofing · Services", "L_split", "brick", icon="roof", since="SINCE 1998", name="Summit Roofing", sub="FREE INSPECTIONS", items=["Storm damage", "Insurance claims", "Repairs & leaks", "New roofs"], phone="(555) 600-5151", web="summitroofs.com"),
    D("lawn-useful", B, "Home services", "Lawn care · Yearly calendar", "L_useful", "lime", icon="leaf", head="Lawn calendar", line="Your yard, season by season", rows=[("Spring", "Aerate & seed"), ("Summer", "Mow high, water deep"), ("Fall", "Leaves & fertilize"), ("Winter", "Rest & plan")], vf="500 26px Jost", pen="#25331A", kw=130, name="GreenLeaf Lawns", phone="(555) 620-3300"),
    D("lawn-word", B, "Home services", "Landscaping · Bold", "L_word", "forest", icon="tree", sub="LAWN CARE · LANDSCAPING · MULCH", head="Best lawn<br>on the block.", line="Weekly mowing from $35. Free estimates.", name="Oak & Acre", phone="(555) 620-8811", ws=96, word_c="#F4EFE3", ph_c="#173B2C"),
    D("pest-hazard", B, "Home services", "Pest control · Bugs", "L_hazard", "orange", icon="bug", name="Bug Busters", sub="PEST CONTROL · TERMITES · MOSQUITOES", head="Uninvited guests?", phone="(555) 620-2847", line="Kid and pet friendly treatments", ac="#E8641B", head_c="#E8641B"),
    D("pool-bar", B, "Home services", "Pool service · Summer", "L_bar", "aqua", icon="pool", name="Blue Lagoon Pools", sub="CLEANING · REPAIRS", head="Pool ready<br>all summer.", line="Weekly service plans and openings.", phone="(555) 620-7665", ink="#0B3A4A", icon_c="#FFFFFF", bar_ink="#FFFFFF"),
    D("moving-bar", B, "Home services", "Movers · Bold", "L_bar", "orange", icon="truck", name="Two Brothers Moving", sub="LOCAL · LONG DISTANCE", head="We lift.<br>You relax.", line="Free quotes. Boxes and packing too.", phone="(555) 620-6683", icon_c="#FFFFFF", bar_ink="#FFFFFF"),
    D("handyman-split", B, "Home services", "Handyman · Services", "L_split", "terracotta", icon="hammer", since="NO JOB TOO SMALL", name="Fix-It Frank", sub="HANDYMAN SERVICES", items=["Drywall & paint", "Doors & shelves", "TV mounting", "Honey-do lists"], phone="(555) 620-1919", web="fixitfrank.com"),
    D("locksmith-hazard", B, "Home services", "Locksmith · Locked out", "L_hazard", "sun", icon="lock", name="Key Master", sub="LOCKSMITH · HOME · AUTO", head="Locked out?", phone="(555) 620-5397", line="At your door in 30 minutes, 24/7", ac="#1D1D1D"),

    # ---- real estate & finance
    D("realtor-photo", B, "Real estate & finance", "Realtor · Photo", "L_photo", "ivory", photo="stock:house-1", pos="center 60%", sub="YOUR NEIGHBORHOOD REALTOR", name="Maria Santos", line="Magnolia & Main Realty", phone="(555) 381-2290"),
    D("realtor-qr", B, "Real estate & finance", "Realtor · Home value", "L_qr", "navy", icon="house", name="Jenna Park Homes", line="What is your home worth today?", head="Scan for<br>a free<br>estimate", phone="(555) 381-7766", web="jennaparkhomes.com", qr_c="#13294B"),
    D("realtor-useful", B, "Real estate & finance", "Realtor · Home care", "L_useful", "sage", icon="house", head="Home checklist", line="A gift from your realtor", rows=[("Monthly", "HVAC filter"), ("Spring", "Gutters & roof"), ("Summer", "Deck & AC"), ("Fall", "Furnace check"), ("Yearly", "Smoke detectors")], vf="500 25px Jost", pen="#2E3B2B", kw=140, name="The Reyes Team", phone="(555) 381-4040"),
    D("realtor-mono", B, "Real estate & finance", "Realtor · Luxury", "L_mono", "black", mono="LH", name="LAURA HAYES", sub="Luxury homes & estates", phone="(555) 381-9000", web="laurahayes.com"),
    D("insurance-useful", B, "Real estate & finance", "Insurance · Important numbers", "L_useful", "navy", icon="shield", head="Important numbers", line="Keep them where everyone can see", rows=[("Emergency", "911"), ("Poison control", "1-800-222-1222"), ("Your agent", "(555) 410-2276"), ("Claims, 24/7", "(555) 410-0000")], vf="600 25px Jost", pen="#FFFFFF", kw=190, name="Blue Oak Insurance", phone="(555) 410-2276", soft="#21406B"),
    D("insurance-split", B, "Real estate & finance", "Insurance · Services", "L_split", "sky", icon="shield", since="SINCE 1994", name="Harbor Insurance", sub="LOCAL AGENT, REAL PEOPLE", items=["Home & auto", "Life insurance", "Small business", "Free reviews"], phone="(555) 410-8808", web="harborins.com"),
    D("tax-word", B, "Real estate & finance", "Taxes · Tax season", "L_word", "lime", icon="calc", sub="TAX PREP · BOOKKEEPING · PAYROLL", head="Tax season?<br>Relax.", line="Personal and small business returns. Done right, on time.", name="Ledger & Co.", phone="(555) 410-3030", ws=104, word_c="#5E8C1F"),
    D("lawyer-mono", B, "Real estate & finance", "Law firm · Classic", "L_mono", "ivory", mono="R&amp;L", ms=76, name="REED &amp; LOWE", sub="Attorneys at law", phone="(555) 410-6600", web="reedlowelaw.com"),
    D("lawyer-split", B, "Real estate & finance", "Law firm · Practice areas", "L_split", "burgundy", icon="scale", since="FREE CONSULTATION", name="Morales Law", sub="WE FIGHT FOR YOU", items=["Car accidents", "Injury at work", "Immigration", "Family law"], phone="(555) 410-1212", web="moraleslaw.com"),
    D("mortgage-qr", B, "Real estate & finance", "Mortgage · Pre-approval", "L_qr", "teal", icon="key", name="Keystone Lending", line="Buying your first home?", head="Scan to<br>get pre-<br>approved", phone="(555) 410-5500", web="keystonelend.com"),

    # ---- beauty & fitness
    D("salon-appt", B, "Beauty & fitness", "Salon · Next appointment", "L_appt", "blush", icon="scissors", name="Velvet Salon", sub="HAIR · COLOR · NAILS", head="See you soon", hand=("Sat, May 8", "2:30 pm"), line="Book online or call", phone="(555) 290-7711", font="italic 700 44px/1 Playfair"),
    D("salon-punch", B, "Beauty & fitness", "Salon · Loyalty card", "L_punch", "plum", icon="scissors", name="Glow Studio", sub="HAIR · LASHES · BROWS", head="Your 10th visit is free", line="Show this magnet at checkout · (555) 290-4545"),
    D("barber-badge", B, "Beauty & fitness", "Barber · Retro badge", "L_badge", "black", icon="comb", name="Sharp & Co. Barbers", sub="CUTS · SHAVES · BEARDS", since="EST. 2015", line="Walk-ins welcome · Tue – Sat", phone="(555) 290-1001"),
    D("barber-word", B, "Beauty & fitness", "Barber · Fresh cut", "L_word", "sun", icon="scissors", sub="BARBERSHOP · WALK-INS WELCOME", head="Fresh<br>cut?", line="Book your chair in 30 seconds.", name="Kings Barbershop", phone="(555) 290-2232"),
    D("nails-mono", B, "Beauty & fitness", "Nails & spa · Elegant", "L_mono", "blush", mono="LN", name="LUXE NAILS", sub="Manicure · Pedicure · Spa", phone="(555) 290-3434", web="luxenails.spa"),
    D("medspa-qr", B, "Beauty & fitness", "Med spa · Book", "L_qr", "lilac", icon="lotus", name="Aura Med Spa", line="Botox, facials and laser.", head="Scan<br>to book", phone="(555) 290-8899", web="auramedspa.com"),
    D("gym-word", B, "Beauty & fitness", "Gym · No excuses", "L_word", "black", icon="dumbbell", sub="24/7 GYM · CLASSES · TRAINERS", head="No<br>excuses.", line="First week free. No contract.", name="Iron Republic", phone="(555) 290-6060", word_c="#D9B26F", ph_c="#151515"),
    D("gym-hours", B, "Beauty & fitness", "Gym · Class schedule", "L_hours", "orange", icon="dumbbell", name="Pulse Fitness", sub="GROUP CLASSES", head="This week", rows=[("Mon & Wed", "HIIT · 6 am"), ("Tue & Thu", "Spin · 6 pm"), ("Saturday", "Bootcamp · 9 am"), ("Sunday", "Stretch · 10 am")], phone="(555) 290-5050", line="First class free", font="400 52px/1 Anton"),
    D("yoga-classic", B, "Beauty & fitness", "Yoga & pilates · Calm", "L_classic", "sage", icon="lotus", name="Breathe Studio", sub="YOGA · PILATES · MEDITATION", line="Your first class is on us", phone="(555) 290-9642", font="400 70px/1 Dancing"),
    D("trainer-qr", B, "Beauty & fitness", "Personal trainer · Free week", "L_qr", "red", icon="dumbbell", name="Coach Dee", line="Ready to start?", head="Scan for<br>a free<br>week", phone="(555) 290-7272", web="@coachdee", font="400 46px/1 Anton", star_c="#FFD166"),

    # ---- pets
    D("vet-appt", B, "Pets", "Vet · Next visit", "L_appt", "teal", icon="paw", name="Sunny Paws", sub="VETERINARY CLINIC", head="Vaccines due", hand=("Buddy · Rabies", "Sept 14"), line="After hours emergency", phone="(555) 450-7387"),
    D("vet-useful", B, "Pets", "Vet · My pet’s info", "L_useful", "orange", icon="paw", head="My pet’s info", line="For the sitter, the walker and you", rows=[("Name", "Luna"), ("Microchip", "985 112 004 377"), ("Food", "1 cup, twice a day"), ("Our vet", "(555) 450-1122")], kw=170, name="Happy Tails Vet", phone="(555) 450-1122"),
    D("groomer-punch", B, "Pets", "Groomer · Loyalty card", "L_punch", "aqua", icon="paw", name="Suds & Pups", sub="DOG GROOMING · BATH · NAILS", head="Your 10th groom is free", line="Book online · (555) 450-3366", font="400 52px/1 DMSerif"),
    D("petsit-word", B, "Pets", "Pet sitter · Bold", "L_word", "pink", icon="bone", sub="DOG WALKING · PET SITTING · BOARDING", head="Good<br>dogs only.", line="Daily walks, drop-ins and overnight stays.", name="Wag Squad", phone="(555) 450-9247", word_c="#FFFFFF"),

    # ---- auto
    D("auto-useful", B, "Auto", "Auto repair · Oil change log", "L_useful", "black", icon="car", head="Oil change log", line="Next one is due at the mileage below", rows=[("Date", "Mar 3"), ("Mileage", "48,200"), ("Next due", "53,200"), ("Tires rotated", "✓")], kw=190, pen="#D9B26F", vf="400 34px/1 Caveat", name="Precision Auto", phone="(555) 530-2886"),
    D("auto-coupon", B, "Auto", "Auto repair · Coupon", "L_coupon", "red", icon="wrench", kicker="OIL CHANGE SPECIAL", offer="$29.99", os=128, head="oil change and free inspection", name="Main St. Garage", phone="(555) 530-4277", line="Most cars · Show this magnet · Expires 12/31/2027"),
    D("tow-hazard", B, "Auto", "Towing · Keep this number", "L_hazard", "sun", icon="hook", name="Big Dan’s Towing", sub="TOWING · JUMP STARTS · LOCKOUTS", head="Stuck on the road?", phone="(555) 530-8697", line="24/7 · Fast, fair and friendly", ac="#1D1D1D"),
    D("detail-badge", B, "Auto", "Car detailing · Badge", "L_badge", "slate", icon="car", name="Gloss Boss Detailing", sub="MOBILE · WE COME TO YOU", since="EST. 2019", line="Ceramic coating · Interior · Wash", phone="(555) 530-1234"),
    D("tires-bar", B, "Auto", "Tires & service · Bold", "L_bar", "red", icon="car", name="Rubber Road Tires", sub="TIRES · BRAKES · ALIGNMENT", head="Flat tire?<br>Come on in.", line="No appointment needed.", phone="(555) 530-8473"),

    # ---- community
    D("church-classic", B, "Churches & nonprofits", "Church · Sunday services", "L_classic", "ivory", icon="church", name="Grace Community", sub="CHURCH · ALL ARE WELCOME", line="Sundays at 9:00 and 11:00 am", phone="(555) 700-4673", font="400 64px/1 DMSerif"),
    D("church-qr", B, "Churches & nonprofits", "Church · Events", "L_qr", "sage", icon="cross", name="New Hope Church", line="Youth group, events and more.", head="Scan to<br>join us", phone="(555) 700-2200", web="newhope.church"),
    D("school-word", B, "Schools & teams", "Daycare & school · Bright", "L_word", "sun", icon="apple", sub="DAYCARE · PRE-K · AFTER SCHOOL", head="Little minds,<br>big days.", line="Now enrolling for fall. Ages 6 weeks to 12.", name="Bright Start Academy", phone="(555) 700-5437", ws=88),
    D("tutor-qr", B, "Schools & teams", "Tutoring · Book a session", "L_qr", "lilac", icon="book", name="A+ Tutoring", line="Math, reading and test prep.", head="Scan to<br>book", phone="(555) 700-2867", web="aplustutoring.com"),
    D("team-useful", B, "Schools & teams", "Team sponsor · Game schedule", "L_useful", "forest", icon="star", head="Wildcats 2027", line="Thanks to our sponsor, Nonna Lucia Pizzeria", rows=[("Sep 6", "vs Eagles · Home"), ("Sep 13", "at Falcons"), ("Sep 20", "vs Comets · Home"), ("Sep 27", "at Rangers"), ("Oct 4", "Homecoming!")], vf="500 25px Jost", pen="#F4EFE3", name="Go Wildcats!", phone="(555) 214-0187"),
    D("nonprofit-thanks", B, "Churches & nonprofits", "Nonprofit · Thank you", "L_thanks", "teal", icon="heart", head="Thank you!", line="Because of you, 1,200 families had dinner this year.", name="Harvest Food Bank", phone="harvestfoodbank.org"),
    D("photog-photo", B, "Florists & photographers", "Photographer · Portfolio", "L_photo", "black", photo="stock:family-3", pos="center 35%", sub="FAMILY · WEDDINGS · NEWBORN", name="Golden Hour Photo", line="Book your fall mini session", phone="(555) 700-7468"),
    D("florist-classic", B, "Florists & photographers", "Florist · Classic", "L_classic", "blush", icon="flower", name="Petal & Stem", sub="FLOWERS FOR EVERY DAY", line="Same-day delivery in town", phone="(555) 700-3567", font="italic 700 64px/1 Playfair", icon_c="#C0756A"),

    # ---- holidays & thank-yous (any business)
    D("thanks-fall", B, "Holidays & thank-yous", "Thanksgiving · Thankful", "L_thanks", "terracotta", icon="leaf", head="Thankful for you", line="Thank you for choosing a small, local business.", name="Peach Valley Air", phone="(555) 600-0198", font="400 76px/1 Dancing"),
    D("thanks-xmas", B, "Holidays & thank-yous", "Christmas · Merry", "L_thanks", "forest", icon="star", head="Merry & bright", line="Wishing you a cozy season, from all of us.", name="Harbor Insurance", phone="(555) 410-8808", font="400 84px/1 Dancing", head_c="#C9A227", ac="#B3261E", bar_ink="#FFFFFF"),
    D("thanks-valentine", B, "Holidays & thank-yous", "Valentine’s · We love our clients", "L_thanks", "pink", icon="heart", head="We love<br>our clients", line="Happy Valentine’s Day from your favorite salon.", name="Velvet Salon", phone="(555) 290-7711", font="400 70px/1 Anton", ac="#2A0E1A", icon_c="#FFFFFF"),
    D("thanks-july", B, "Holidays & thank-yous", "4th of July · Stars", "L_thanks", "navy", icon="star", head="Happy 4th!", line="Proudly serving our neighbors since 1998.", name="Summit Roofing", phone="(555) 600-5151", font="400 96px/1 Anton", ac="#B3261E", head_c="#FFFFFF", bar_ink="#FFFFFF"),
    D("thanks-school", B, "Holidays & thank-yous", "Back to school · A+", "L_thanks", "sun", icon="apple", head="Have an A+ year!", line="Back-to-school checkups are open now.", name="Little Sprouts Pediatrics", phone="(555) 610-7878", font="400 70px/1 Anton", ac="#B3261E", icon_c="#B3261E", bar_ink="#FFFFFF"),
    D("thanks-newyear", B, "Holidays & thank-yous", "New Year · Cheers", "L_thanks", "black", icon="cheers", head="Cheers to 2027", line="Thank you for a wonderful year together.", name="Ledger & Co.", phone="(555) 410-3030", font="400 74px/1 Dancing", head_c="#D9B26F", ac="#D9B26F"),

    # ---- photo designs (stock photos: Pixabay Content License, assets/stock/credits.json)
    D("barber-photo", B, "Beauty & fitness", "Barber · Photo", "L_photo", "black", photo="stock:barber-2", pos="center 30%", sub="FADES · BEARDS · HOT TOWEL", name="Kings Barbershop", line="Walk-ins welcome", phone="(555) 290-2232"),
    D("salon-photo", B, "Beauty & fitness", "Salon · Photo", "L_photo", "blush", photo="stock:salon-4", pos="center 30%", sub="CUT · COLOR · BLOWOUT", name="Velvet Salon", line="Book online anytime", phone="(555) 290-7711", font="italic 700 52px/1.1 Playfair"),
    D("gym-photo", B, "Beauty & fitness", "Gym · Photo", "L_photo", "black", photo="stock:gym-1", pos="center 40%", sub="FIRST WEEK FREE", name="Iron Republic Gym", line="Open 24/7", phone="(555) 290-6060"),
    D("yoga-photo", B, "Beauty & fitness", "Yoga · Photo", "L_photo", "sage", photo="stock:yoga-4", pos="center 40%", sub="YOGA · PILATES · BREATHE", name="Breathe Studio", line="Your first class is free", phone="(555) 290-9642"),
    D("bakery-photo", B, "Restaurants & food", "Bakery · Photo", "L_photo", "cream", photo="stock:bakery-2", sub="BAKED FRESH EVERY MORNING", name="Rise & Shine Bakery", line="Open daily from 7 am", phone="(555) 266-3317"),
    D("pizza-photo", B, "Restaurants & food", "Pizza · Photo", "L_photo", "red", photo="stock:pizza-3", sub="WOOD-FIRED · DELIVERY", name="Nonna Lucia Pizzeria", line="Order online or call", phone="(555) 214-0187"),
    D("coffee-photo", B, "Restaurants & food", "Café · Photo", "L_photo", "forest", photo="stock:coffee-1", sub="COFFEE · TEA · PASTRIES", name="Little Fern Café", line="Open every day at 6 am", phone="(555) 410-7788"),
    D("food-photo", B, "Restaurants & food", "Restaurant · Photo", "L_photo", "navy", photo="stock:food-2", sub="LUNCH · DINNER · CATERING", name="The Corner Table", line="Reservations", phone="(555) 830-4410"),
    D("dental-photo", B, "Health & dental", "Dental · Smile photo", "L_photo", "teal", photo="stock:dentist-2", pos="center 30%", sub="NEW PATIENTS WELCOME", name="Bright Side Dental", line="Most insurance accepted", phone="(555) 742-1180"),
    D("clean-photo", B, "Home services", "House cleaning · Photo", "L_photo", "aqua", photo="stock:kitchen-1", sub="WEEKLY · DEEP · MOVE-OUT", name="Sparkle & Co.", line="Insured and bonded", phone="(555) 377-2500"),
    D("lawn-photo", B, "Home services", "Lawn care · Photo", "L_photo", "forest", photo="stock:garden-1", sub="MOWING · MULCH · CLEANUPS", name="Oak & Acre Lawns", line="Free estimates", phone="(555) 620-8811"),
    D("realtor-sold", B, "Real estate & finance", "Realtor · Just sold", "W_photo", "navy", photo="stock:house-2", pos="center 50%", head="Just sold!", line="JENNA PARK HOMES · (555) 381-7766", font="400 84px/1.1 Anton"),
    D("auto-photo", B, "Auto", "Auto repair · Photo", "L_photo", "slate", photo="stock:mechanic-1", sub="ENGINES · BRAKES · A/C", name="Precision Auto", line="Honest work since 2004", phone="(555) 530-2886"),
    D("car-photo", B, "Auto", "Car detailing · Photo", "L_photo", "black", photo="stock:car-3", sub="MOBILE DETAILING", name="Gloss Boss", line="We come to you", phone="(555) 530-1234"),
    D("vet-photo", B, "Pets", "Vet · Photo", "L_photo", "teal", photo="stock:vet-1", sub="DOGS · CATS · EXOTICS", name="Sunny Paws Vet", line="Same-day sick visits", phone="(555) 450-7387"),
    D("groomer-photo", B, "Pets", "Groomer · Photo", "W_photo", "aqua", photo="stock:puppy-2", pos="center 40%", head="Fresh & fluffy", line="SUDS & PUPS · (555) 450-3366", font="400 76px/1.1 Dancing"),
    D("florist-photo", B, "Florists & photographers", "Florist · Photo", "L_photo", "blush", photo="stock:flowers-1", sub="SAME-DAY DELIVERY", name="Petal & Stem", line="Flowers for every day", phone="(555) 700-3567", font="italic 700 52px/1.1 Playfair"),
    D("team-photo", B, "Schools & teams", "Team sponsor · Photo", "W_photo", "forest", photo="stock:football-2", pos="center 40%", head="Go Tigers!", line="PROUD SPONSOR · NONNA LUCIA PIZZERIA", font="400 90px/1.1 Anton"),
    D("church-photo", B, "Churches & nonprofits", "Church · Photo", "L_photo", "ivory", photo="stock:church-2", sub="ALL ARE WELCOME", name="Grace Community Church", line="Sundays 9 & 11 am", phone="(555) 700-4673"),

    # ---- weddings
    D("wed-arch", "weddings", "Save the date", "Save the date · Arch", "W_names", "ivory", sub="SAVE THE DATE", a="Olivia", b="Mateo", date="09 · 18 · 2027", place="Charleston, South Carolina"),
    D("wed-arch-sage", "weddings", "Save the date", "Save the date · Sage arch", "W_names", "sage", sub="WE’RE GETTING MARRIED", a="Hannah", b="Luke", date="05 · 22 · 2027", place="Napa Valley, California"),
    D("wed-botanical", "weddings", "Save the date", "Save the date · Botanical", "W_botanical", "ivory", ac="#7D8F76", sub="SAVE THE DATE", a="Sofia", b="Daniel", date="10 · 02 · 2027", place="Asheville, North Carolina"),
    D("wed-bigdate", "weddings", "Save the date", "Save the date · Big date", "W_bigdate", "black", sub="Save the date", a="Ava", b="Noah", date="06.12.27", place="The Grand Hotel · Chicago", line="INVITATION TO FOLLOW"),
    D("wed-bigdate-blush", "weddings", "Save the date", "Save the date · Blush date", "W_bigdate", "blush", sub="We’re getting married", a="Camila", b="Lucas", date="04.24.27", place="Miami Beach, Florida", line="FORMAL INVITATION TO FOLLOW"),
    D("wed-photo", "weddings", "Save the date", "Save the date · Full photo", "W_photo", "black", bg="rgba(20,16,12,.85)", photo="stock:wedding-2", pos="center 35%", head="Save the date", line="EMILY &amp; JAMES · 10.09.27"),
    D("wed-polaroid", "weddings", "Save the date", "Save the date · Instant photo", "W_polaroid", "terracotta", photo="stock:engagement-3", pos="center 40%", head="We said yes!", date="11.13.27", line="SAVANNAH, GA"),
    D("wed-qr", "weddings", "Save the date", "RSVP · QR code", "E_qr", "ivory", head="Kate &amp; Ben", sub="RSVP · REGISTRY · DETAILS", line="Scan to RSVP"),
    D("wed-favor-gold", "weddings", "Favors & thank-yous", "Favor · Gold monogram", "L_mono", "black", mono="A&amp;J", ms=72, name="ALEX &amp; JORDAN", sub="Thank you for celebrating with us", phone="08 · 21 · 2027", web="Lake Tahoe"),
    D("wed-favor-script", "weddings", "Favors & thank-yous", "Favor · Love is sweet", "L_thanks", "blush", icon="heart", head="Love is sweet", line="Thank you for sharing our day!", name="Mia &amp; Carlos", phone="May 15, 2027", font="400 90px/1 Dancing"),
    D("wed-favor-cheers", "weddings", "Favors & thank-yous", "Favor · Cheers", "L_thanks", "forest", icon="cheers", head="Cheers!", line="To love, laughter and happily ever after.", name="Grace &amp; Owen", phone="10 · 30 · 2027", font="400 100px/1 Dancing", head_c="#C9A227"),
    D("wed-anniv", "weddings", "Favors & thank-yous", "Anniversary · 50 years", "W_bigdate", "gold", sub="Fifty golden years", a="Rosa", b="Antonio", date="1977.2027.50", place="Thank you for celebrating with us", line="THE MARTINEZ FAMILY"),
    D("wed-shower", "weddings", "Favors & thank-yous", "Bridal shower · Script", "E_party", "blush", conf=["#C0756A", "#E9C46A", "#FFFFFF"], sub="BRIDAL SHOWER", head="Bride to be", font="400 104px/1 Dancing", tt="none", line="Celebrating Isabella", date="SATURDAY · MARCH 6, 2027"),

    D("wed-sunset", "weddings", "Save the date", "Save the date · Sunset photo", "W_photo", "black", photo="stock:wedding-4", pos="center 40%", head="Save the date", line="NINA & MARCO · 08.14.27"),
    D("wed-engaged", "weddings", "Save the date", "Engaged · Instant photo", "W_polaroid", "blush", photo="stock:couple-2", pos="center 35%", head="She said yes!", date="06.05.27", line="SAVE THE DATE"),
    D("wed-rings", "weddings", "Favors & thank-yous", "Thank you · Rings photo", "W_photo", "ivory", photo="stock:engagement-2", pos="center 50%", head="Thank you", line="LUCY & SAM · 05.29.27", shade="rgba(59,48,39,.8)"),
    D("wed-bride", "weddings", "Save the date", "Save the date · Bride photo", "W_photo", "black", photo="stock:bride-1", pos="center 25%", head="Save the date", line="ELLA & JAMES · 09.25.27"),
    D("grad-photo2", "graduation", "Graduation", "Graduation · Caps photo", "W_photo", "navy", photo="stock:grad-2", pos="center 40%", head="Class of 2027", line="CONGRATS, GRADS!", font="400 80px/1.1 Anton", shade="rgba(19,41,75,.9)"),
    D("grad-photo3", "graduation", "Graduation", "Graduation · Proud photo", "W_polaroid", "burgundy", photo="stock:grad-girl-5", pos="center 25%", head="So proud of you!", date="CLASS OF 2027", line="MARIA · NURSING", ink="#F7EBDD"),
    D("party-photo", "parties", "Birthdays", "Birthday · Photo", "W_photo", "pink", photo="stock:birthday-2", pos="center 50%", head="Happy birthday, Mia!", line="SWEET SIXTEEN · 06.19.27", font="400 64px/1.1 Dancing", shade="rgba(120,20,60,.82)"),
    D("party-baby-photo", "parties", "Baby showers", "Baby · Welcome photo", "W_polaroid", "mint", photo="stock:baby-2", pos="center 40%", head="Welcome, Olivia", date="03.14.27", line="7 LB 2 OZ · 20 IN"),
    D("party-pet", "parties", "Big celebrations", "Pet · Photo", "W_polaroid", "sun", photo="stock:dog-2", pos="center 40%", head="Best boy, Max", date="GOTCHA DAY", line="ADOPTED 2026"),
    D("party-beach", "parties", "Big celebrations", "Family trip · Photo", "W_photo", "aqua", photo="stock:beach-3", pos="center 50%", head="Garcia Beach Week", line="OUTER BANKS · SUMMER 2027", font="400 60px/1.1 Dancing", shade="rgba(11,58,74,.85)"),

    # ---- graduation & college
    D("grad-year-navy", "graduation", "Graduation", "Graduation · Big year", "G_year", "navy", sub="CONGRATULATIONS", year="2027", head="Jordan Ellis", line="LINCOLN HIGH SCHOOL"),
    D("grad-year-black", "graduation", "Graduation", "Graduation · Black & gold", "G_year", "black", sub="THE GRADUATE", year="’27", head="Mia Thompson", line="UNIVERSITY OF GEORGIA"),
    D("grad-year-burgundy", "graduation", "Graduation", "Graduation · Burgundy", "G_year", "burgundy", sub="CLASS OF", year="2027", head="Ethan Brooks", line="NURSING · BSN"),
    D("grad-photo", "graduation", "Graduation", "Graduation · Photo", "W_photo", "navy", bg="rgba(19,41,75,.92)", photo="stock:grad-girl-3", pos="center 25%", head="Congrats, Grad!", line="SOPHIA · CLASS OF 2027", font="400 70px/1 Anton"),
    D("grad-polaroid", "graduation", "Graduation", "Graduation · Instant photo", "W_polaroid", "sky", photo="stock:grad-girl-2", pos="center 30%", head="We did it!", date="CLASS OF 2027", line="JEFFERSON HIGH"),
    D("grad-party-qr", "graduation", "Graduation", "Grad party · QR details", "E_qr", "sun", head="Party time!", sub="MAYA’S GRADUATION PARTY", line="Scan for details", font="400 76px/1 Anton"),
    D("grad-party", "graduation", "Graduation", "Grad party · Confetti", "E_party", "navy", conf=["#F2A81D", "#FFFFFF", "#2B7BBF"], sub="YOU’RE INVITED", head="Grad<br>party", line="Celebrating Marcus · Class of 2027", date="SAT · JUNE 5 · 4 PM"),
    D("college-pennant", "graduation", "College & school spirit", "College · Pennant", "G_pennant", "cream", school="Maple Hill", head="Welcome home", line="CLASS OF 2031", sub="Welcome Week · August 23–27"),
    D("college-pennant-red", "graduation", "College & school spirit", "School spirit · Pennant", "G_pennant", "red", ink="#FFF6E8", ac="#FFD166", school="Go Tigers", ps=74, head="Roar louder!", line="CENTRAL HIGH BOOSTER CLUB", sub="Thanks for cheering with us"),
    D("college-orient", "graduation", "College & school spirit", "Orientation · Scan the map", "E_qr", "burgundy", head="Welcome, Class of 2031", sub="CAMPUS MAP · EVENTS · HELP", line="Scan for the map", font="400 46px/1 DMSerif"),
    D("greek-mono", "graduation", "College & school spirit", "Sorority & fraternity · Crest", "L_mono", "lilac", mono="ΑΔΠ", ms=74, name="ALPHA DELTA PI", sub="Big Little Reveal · Fall 2027", phone="Love, your Big", web="Maple Hill College"),
    D("reunion-word", "graduation", "College & school spirit", "Reunion · 20 years", "L_word", "gold", icon="star", sub="CLASS OF 2007 REUNION", head="20 years<br>later.", line="Saturday, July 17, 2027 · The Lakeside Club", name="Westview High", phone="See you there!", ws=104),

    # ---- parties & events
    D("party-birthday", "parties", "Birthdays", "Birthday · Confetti", "E_party", "pink", conf=["#FFD166", "#FFFFFF", "#2A0E1A"], sub="LET’S CELEBRATE", head="Emma<br>turns 30", line="Thanks for partying with us!", date="MARCH 12, 2027"),
    D("party-kid", "parties", "Birthdays", "Kid’s birthday · Balloons", "L_thanks", "sky", icon="balloon", head="Leo is 5!", line="Thanks for coming to my party!", name="Leo’s Dino Party", phone="April 3, 2027", font="400 104px/1 Anton", head_c="#2B7BBF"),
    D("party-sweet16", "parties", "Birthdays", "Sweet 16 · Glam", "L_mono", "plum", mono="16", ms=110, name="SWEET SIXTEEN", sub="Chloe · June 19, 2027", phone="Thank you for celebrating", web="with me!"),
    D("party-milestone", "parties", "Birthdays", "Milestone · 50th", "G_year", "black", icon="cheers", sub="CHEERS TO", year="50", head="Robert", line="FIFTY AND FABULOUS · 2027"),
    D("party-baby", "parties", "Baby showers", "Baby shower · Sweet", "L_thanks", "mint", icon="baby", head="Oh, baby!", line="Thank you for showering us with love.", name="Baby Johnson", phone="Coming May 2027", font="400 96px/1 Dancing"),
    D("party-babyboy", "parties", "Baby showers", "Baby shower · Confetti", "E_party", "sky", conf=["#2B7BBF", "#FFFFFF", "#F2A81D"], sub="BABY SHOWER", head="Little one<br>on the way", font="400 82px/.98 Anton", line="Celebrating Ana & Felipe", date="SUNDAY · FEBRUARY 21, 2027"),
    D("party-retire", "parties", "Work events", "Retirement · Party", "E_party", "gold", conf=["#B8860B", "#2B2118", "#F1E2BB"], sub="HAPPY RETIREMENT", head="Officially<br>off the clock", font="400 82px/.98 Anton", line="Thank you, Linda, for 32 amazing years", date="FRIDAY · MAY 28, 2027"),
    D("party-office", "parties", "Work events", "Holiday party · Team", "L_thanks", "burgundy", icon="gift", head="Happy Holidays", line="Thanks for an amazing year, team!", name="Brightline Holiday Party", phone="December 17, 2026", font="400 80px/1 Dancing", head_c="#D9B26F"),
    D("party-conference", "parties", "Work events", "Conference · Scan the agenda", "E_qr", "slate", head="Summit 2027", sub="AGENDA · SPEAKERS · WI-FI", line="Scan for the agenda", font="400 76px/1 Anton"),
    D("party-quince", "parties", "Big celebrations", "Quinceañera · Gold", "L_mono", "lilac", mono="XV", ms=92, name="ISABELLA", sub="Mis quince años", phone="March 20, 2027", web="Houston, Texas"),
    D("party-family", "parties", "Big celebrations", "Family reunion · Photo", "W_polaroid", "lime", photo="stock:family-6", pos="center 40%", head="The Garcia Family", date="SUMMER 2027", line="LAKE LANIER, GA"),
    D("party-fiesta", "parties", "Big celebrations", "Fiesta · Bold", "E_party", "orange", conf=["#E8641B", "#2EA37A", "#FFD23F", "#B3261E"], sub="¡VAMOS A CELEBRAR!", head="Fiesta!", line="Thank you for coming", date="CINCO DE MAYO · 2027", font="400 140px/1 Anton"),
    D("party-vbs", "parties", "Big celebrations", "Church & VBS · Summer", "L_word", "sun", icon="sun", sub="VACATION BIBLE SCHOOL", head="Shine<br>bright!", line="June 14 – 18, 2027 · Ages 4 to 12 · Free", name="Grace Community", phone="(555) 700-4673"),
]

HAND_COUNT = len(DESIGNS)

# ---------------------------------------------------------------- the big catalog (tools/design_kits.py)
import design_kits as KITS   # noqa: E402

HAND_SET = {"pizza": "pizza", "taco": "mexican", "sushi": "sushi", "ramen": "sushi", "cafe": "cafe", "bakery": "bakery", "foodtruck": "bbq", "restaurant": "restaurant",
            "dental": "dentist", "ortho": "ortho", "clinic": "doctor", "peds": "pediatrics", "chiro": "chiro", "eye": "eyes", "clean": "cleaning", "hvac": "hvac",
            "plumber": "plumber", "electric": "electric", "roof": "roofing", "lawn": "lawn", "pest": "pest", "pool": "pool", "moving": "moving", "handyman": "handyman",
            "locksmith": "locksmith", "realtor": "realtor", "insurance": "insurance", "tax": "tax", "lawyer": "lawyer", "mortgage": "mortgage", "salon": "salon",
            "barber": "barber", "nails": "nails", "medspa": "medspa", "gym": "gym", "yoga": "yoga", "trainer": "trainer", "vet": "vet", "groomer": "groomer",
            "petsit": "petsitter", "auto": "autorepair", "tow": "towing", "detail": "detailing", "tires": "tires", "church": "church", "school": "school",
            "tutor": "tutor", "team": "team", "nonprofit": "nonprofit", "photog": "photographer", "florist": "florist", "car": "detailing", "coffee": "cafe",
            "food": "restaurant"}
HAND_THANKS = {"thanks-fall": "hvac", "thanks-xmas": "insurance", "thanks-valentine": "salon", "thanks-july": "roofing", "thanks-school": "pediatrics", "thanks-newyear": "tax"}
HAND_ROW = {"L_coupon": "promo", "L_punch": "promo", "L_bar": "number", "L_hazard": "number", "L_word": "number", "L_qr": "qr", "L_photo": "photo", "W_photo": "photo",
            "L_useful": "useful", "L_hours": "useful", "L_appt": "useful", "L_classic": "brand", "L_mono": "brand", "L_badge": "brand", "L_split": "brand", "L_thanks": "thanks"}
EVENT_ROW = {"Save the date": "date", "Favors & thank-yous": "thanks", "Graduation": "date", "College & school spirit": "date", "Birthdays": "party",
             "Baby showers": "party", "Work events": "party", "Big celebrations": "party"}
for _d in DESIGNS:
    if _d["page"] == "business":
        _d["set"] = HAND_THANKS.get(_d["slug"]) or HAND_SET.get(_d["slug"].split("-")[0], "restaurant")
        _d["row"] = HAND_ROW.get(_d["layout"], "brand")
    else:
        _d["set"] = {"weddings": "w-main", "graduation": "g-main", "parties": "x-main"}[_d["page"]]
        _d["row"] = "photo" if _d["layout"] in ("W_photo", "W_polaroid") else "qr" if _d["layout"] == "E_qr" else EVENT_ROW.get(_d["group"], "date")

SETS = {}   # key -> {page, name, group, icon, rows}
for _k in KITS.K:
    SETS[_k["key"]] = dict(page="business", name=_k["name"], group=_k["group"], icon=_k["icon"], il=_k.get("il") or "", words=KITS.words_for(_k), rows=[r for r, _ in KITS.ROWS])
SETS.update({"w-main": dict(page="weddings", name="Weddings", group="Weddings", icon="rings", rows=[r for r, _ in KITS.EROWS]),
             "g-main": dict(page="graduation", name="Graduation", group="Graduation", icon="cap", rows=[r for r, _ in KITS.EROWS]),
             "x-main": dict(page="parties", name="Parties & events", group="Parties", icon="balloon", rows=[r for r, _ in KITS.EROWS])})
for _p in KITS.PSETS:
    SETS[_p["key"]] = dict(page="personalize", name=_p["name"], group="Personalize", icon=_p["icon"], il=KITS.PICON.get(_p["key"], "")[3:] if KITS.PICON.get(_p["key"], "").startswith("il:") else "",
                           words=_p["name"] + " " + KITS.PT.get(_p["key"], ""), rows=[r for r, _ in KITS.PROWS])
for _e in KITS.ESETS:
    SETS[_e["key"]] = dict(page=_e["page"], name=_e["name"], group=SETS[{"weddings": "w-main", "graduation": "g-main", "parties": "x-main"}[_e["page"]]]["group"], icon=_e["icon"], rows=[r for r, _ in KITS.EROWS])
# the event pages show their two sets as one
MERGE = {"w-more": "w-main", "g-more": "g-main", "x-more": "x-main", **{_p["key"] + "x": _p["key"] for _p in KITS.PSETS}}

_ROWNAME = dict(KITS.ROWS + KITS.PROWS + KITS.EROWS)


def _gen(set_key, page, recipes, pals, label):
    n = 0
    for i, (row, lay, words, opt) in enumerate(recipes):
        opt = dict(opt)
        pal = opt.pop("pal", None) or pals[(i * 7 + len(set_key)) % len(pals)]
        if lay in ("neon", "chalk") and P[pal]["bg"] in ("#FBF4E6", "#FAF6EF", "#EEF0E6", "#F7E8E4", "#FFF8E7", "#F1EBF8", "#E5F3F1"):
            pal = "black"
        n += 1
        slug = f"{set_key}-{n}"
        title = f"{label} · {_ROWNAME.get(row, row)}"
        d = dict(words); d.update(opt)
        if "items" in d and isinstance(d["items"], list):
            pass
        DESIGNS.append(D(slug, page, SETS[MERGE.get(set_key, set_key)]["name"], title, lay, pal, set=MERGE.get(set_key, set_key), row=row, **d))


QUOTA = {"promo": 3, "number": 4, "qr": 3, "photo": 4, "useful": 4, "brand": 6, "thanks": 2}


def _pick(recipes, seed):
    """At most QUOTA[row] designs per row, starting at a different place for each kind of business (more variety)."""
    out = []
    for row, q in QUOTA.items():
        mine = [r for r in recipes if r[0] == row]
        if len(mine) > q:
            st = seed % len(mine)
            mine = (mine[st:] + mine[:st])[:q]
        out += mine
    return out


for _i, _k in enumerate(KITS.K):
    _all = KITS.recipes_business(_k)
    _gen(_k["key"], "business", _all if _k["group"] == KITS.G_OTHER else _pick(_all, _i * 5), _k["pals"], _k["name"])

for _p in KITS.PSETS:
    _gen(_p["key"], "personalize", _p["recipes"], _p["pals"], _p["name"])
    _gen(_p["key"] + "x", "personalize", KITS.personal_more(_p), _p["pals"], _p["name"])
for _e in KITS.ESETS:
    _gen(_e["key"], _e["page"], _e["recipes"], _e["pals"], {"weddings": "Wedding", "graduation": "Graduation", "parties": "Party"}[_e["page"]])
for _e in KITS.ESETS:
    SETS.pop(_e["key"], None)

LAYOUT = {"L_bar": "bar", "L_hazard": "hazard", "L_classic": "classic", "L_split": "split", "L_badge": "badge", "L_appt": "appt", "L_qr": "qr",
          "L_coupon": "coupon", "L_useful": "useful", "L_punch": "punch", "L_mono": "mono", "L_word": "word", "L_photo": "photo", "L_hours": "hours",
          "L_thanks": "thanks", "W_names": "names", "W_botanical": "botanical", "W_bigdate": "bigdate", "W_photo": "wphoto", "W_polaroid": "polaroid",
          "G_year": "year", "G_pennant": "pennant", "E_party": "party", "E_qr": "eqr"}
# the words a customer can change, in the order the studio asks for them
TEXT = {"bar": "name sub head line phone", "hazard": "name sub head phone line", "classic": "name sub line phone", "split": "name sub items phone web since",
        "badge": "name sub since line phone", "appt": "name sub head hand line phone", "qr": "name line head phone web", "coupon": "kicker offer head name phone line",
        "useful": "head line rows name phone", "punch": "name sub head line", "mono": "mono name sub phone web", "word": "sub head line name phone",
        "photo": "sub name line phone", "hours": "name sub head rows phone line", "thanks": "head line name phone", "names": "sub a b date place",
        "botanical": "sub a b date place", "bigdate": "sub date a b place line", "wphoto": "head line", "polaroid": "head date line", "year": "sub year head line",
        "pennant": "school head line sub", "party": "sub head line date", "eqr": "head sub line"}
NEW_TEXT = {"neon": "sub name head line phone", "kraft": "name sub head line phone", "chalk": "name head rows phone", "watercolor": "name sub line phone web",
            "ticket": "kicker offer head name phone line", "bizcard": "name sub phone line web", "retro": "sub name line phone", "stamp": "name sub since phone",
            "label": "since name sub line phone", "bignum": "name sub head phone line", "bubble": "head line name phone", "sticky": "head line name phone",
            "magazine": "name sub head line phone", "halfphoto": "name sub line phone web", "frame": "name sub phone", "archphoto": "name sub phone",
            "diagonal": "name head line sub phone", "qrbig": "head line name", "qrphone": "head line name web", "review": "head line name",
            "referral": "kicker offer head name phone", "emergency": "head line rows name phone", "gradient": "head line name web phone", "minimal": "name sub phone web",
            "crest": "mono name sub phone", "burst": "kicker offer head name phone", "receipt": "name sub rows head phone", "tag": "kicker offer head name phone",
            "pin": "head name line phone", "clock": "name head rows phone line", "diner": "sub name line phone", "floral": "sub name line phone",
            "wave": "name sub head line phone", "geo": "name sub line phone", "blobs": "head line name phone", "jersey": "name year sub line",
            "blueprint": "name sub head line since phone", "pole": "name sub line phone", "paws": "name sub line phone", "deco": "mono name sub phone",
            "ribbon": "name sub line phone", "remind": "name sub head hand line phone", "checklist": "head line rows name phone", "circlephoto": "name sub phone",
            "snapshot": "head name phone", "stripes": "kicker offer head name phone", "wreath": "head line name phone", "menu": "name sub head rows line phone",
            "seal": "name sub phone", "hero": "name sub phone", "duo": "sub head line name phone", "invite": "sub head date line",
            "photocircle": "head line", "film": "head line", "monodate": "sub a b date place", "bigtype": "sub head line date"}
for _k, _v in NEW_TEXT.items():
    TEXT[_k] = _v
    LAYOUT[_k] = _k
TWEAK = {"icon_c", "bar_ink", "word_c", "ph_c", "head_c", "star_c", "qr_c", "txt", "shade", "pen", "conf"}
META = {"slug", "page", "group", "title", "layout", "bg", "ink", "ac", "soft", "pal", "set", "row"}
FONTNAMES = [("Playfair", "'Playfair Display'"), ("Dancing", "'Dancing Script'"), ("DMSerif", "'DM Serif Display'"), ("Josefin", "'Josefin Sans'"),
             ("Bebas", "'Bebas Neue'"), ("Cormorant", "'Cormorant Garamond'")]


def plain(v):
    return str(v).replace("<br>", "\n").replace("&amp;", "&")


def export(d):
    """One design as assets/designs.js has it: colors, words (what the customer may change), options and color touches."""
    lay = LAYOUT[d["layout"]]
    text, opt, tweak = {}, {}, {}
    for k in TEXT[lay].split():
        if k == "items":
            for i, x in enumerate(d["items"]): text[f"items{i}"] = plain(x)
        elif k == "rows":
            for i, (x, y) in enumerate(d["rows"]): text[f"rows{i}a"] = plain(x); text[f"rows{i}b"] = plain(y)
        elif k == "hand":
            h = d.get("hand", ("Tue, March 9", "10:30 am")); text["hand0"] = plain(h[0]); text["hand1"] = plain(h[1])
        else:
            text[k] = plain(d.get(k, ""))
    for k, v in d.items():
        if k in META or k in text or k in ("items", "rows", "hand"):
            continue
        if k in TWEAK:
            tweak[k] = v
        elif k == "photo":
            opt["photoUrl"] = f"assets/stock/{v[6:]}.webp" if v.startswith("stock:") else (f"assets/showcase/{v}.webp" if "/" not in v else v)
        elif k == "font":
            for a, b in FONTNAMES: v = v.replace(" " + a, " " + b)
            opt[k] = v
        elif k not in TEXT[lay].split():
            opt[k] = v
    if "items" in d: opt["items"] = [plain(x) for x in d["items"]]
    if "rows" in d: opt["rows"] = [[plain(x), plain(y)] for x, y in d["rows"]]
    if lay in ("appt", "remind"): opt["hand"] = [text["hand0"], text["hand1"]]
    if lay in ("qr", "eqr", "qrbig", "qrphone", "review"): opt["url"] = d.get("url") or SITE + d.get("page", "business") + ".html"
    if lay in ("wphoto",) and isinstance(d.get("bg"), str) and d["bg"].startswith("rgba"):
        tweak["shade"] = d["bg"]
    pal = P[d["pal"]]
    colors = {k: (d[k] if isinstance(d.get(k), str) and d[k].startswith("#") else pal[k]) for k in ("bg", "ink", "ac", "soft")}
    return {"slug": d["slug"], "page": d["page"], "group": d["group"], "title": d["title"], "layout": lay, "set": d.get("set", ""), "row": d.get("row", ""),
            "colors": colors, "text": text, "opt": opt, "tweak": tweak}


FEATURED = {
    "business": [("Most loved", ["pizza-night", "dental-coupon", "clean-word", "realtor-qr", "barber-badge", "cafe-punch", "hvac-bar", "insurance-useful", "gym-word", "vet-useful", "salon-photo", "church-classic"]),
                 ("Scan me", ["realtor-qr", "dental-qr", "ramen-qr", "medspa-qr", "church-qr", "tutor-qr", "trainer-qr", "foodtruck-qr"]),
                 ("Bring customers back", ["pizza-coupon", "clean-coupon", "auto-coupon", "plumber-coupon", "salon-punch", "groomer-punch", "bakery-punch", "dental-coupon"])],
}


def write_sets():
    """assets/designs/<set>.json, one per set (the studio loads a set when it opens), and the small index for designs.js."""
    out = ROOT / "assets" / "designs"
    out.mkdir(exist_ok=True)
    by = {}
    for d in DESIGNS:
        by.setdefault(d["set"], []).append(export(d))
    for k, lst in by.items():
        (out / f"{k}.json").write_text(json.dumps(lst, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    for f in out.glob("*.json"):
        if f.stem not in by:
            f.unlink()
    return by


def js():
    """assets/designs.js (build.py writes it): palettes, stock photos, the sets and where each design lives. The designs
    themselves are in assets/designs/<set>.json (write_sets)."""
    by = write_sets()
    stock = [c["name"] for c in json.loads((ROOT / "assets" / "stock" / "credits.json").read_text())]
    sets = {}
    for k, meta in SETS.items():
        lst = by.get(k, [])
        rows = {}
        for d in lst:
            rows[d["row"]] = rows.get(d["row"], 0) + 1
        sets[k] = {"page": meta["page"], "name": meta["name"], "group": meta["group"], "icon": meta["icon"], "il": meta.get("il", ""), "words": meta.get("words", ""),
                   "n": len(lst), "rows": [r for r in meta["rows"] if r in rows], "first": lst[0]["slug"] if lst else ""}
    where = {d["slug"]: d["set"] for d in DESIGNS}
    rownames = dict(KITS.ROWS + KITS.PROWS + KITS.EROWS)
    feat = dict(FEATURED)
    feat["personalize"] = [("Most loved", [by[k][i]["slug"] for i in (0, 1, 3) for k in [p["key"] for p in KITS.PSETS] if len(by.get(k, [])) > i][:16])]
    v = hashlib.md5(json.dumps(by, sort_keys=True).encode()).hexdigest()[:8]
    data = {"v": v, "pal": P, "stock": stock, "sets": sets, "where": where, "rowNames": rownames, "featured": feat,
            "groups": [KITS.G_FOOD, KITS.G_HEALTH, KITS.G_HOME, KITS.G_MONEY, KITS.G_BEAUTY, KITS.G_PETS, KITS.G_AUTO, KITS.G_COMM, KITS.G_SHOPS, KITS.G_OTHER]}
    return "window.LHHDesigns=" + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";"


GALLERY = [(d["slug"], d["page"], d["group"], d["title"]) for d in DESIGNS]
SET_N = {}
for _d in DESIGNS:
    SET_N[_d["set"]] = SET_N.get(_d["set"], 0) + 1
COUNTS = {}
for _d in DESIGNS:
    COUNTS[_d["page"]] = COUNTS.get(_d["page"], 0) + 1


RFONTS = "".join(f"@font-face{{font-family:{n};src:url('file://{F}/{f}'){x}}}" for n, f, x in [
    ("'Josefin Sans'", "JosefinSans[wght].ttf", ";font-weight:100 900"), ("Jost", "Jost[wght].ttf", ";font-weight:100 900"),
    ("Caveat", "Caveat-SemiBold.ttf", ""), ("'Playfair Display'", "PlayfairDisplay-Italic[wght].ttf", ";font-style:italic;font-weight:400 900"),
    ("'DM Serif Display'", "DMSerifDisplay-Regular.ttf", ""), ("Cinzel", "Cinzel[wght].ttf", ";font-weight:400 900"),
    ("'Bebas Neue'", "BebasNeue-Regular.ttf", ""), ("'Cormorant Garamond'", "CormorantGaramond-SemiBoldItalic.ttf", ";font-style:normal"),
    ("'Cormorant Garamond'", "CormorantGaramond-SemiBoldItalic.ttf", ";font-style:italic"),
    ("'Dancing Script'", "DancingScript-SemiBold.ttf", ""), ("Anton", "Anton-Regular.ttf", ""), ("'DM Mono'", "DMMono-Medium.ttf", ";font-weight:500")])


def render_batch(ds, cols=5, size=360):
    """Many designs on one page, one screenshot, then cut: much faster than one browser per design."""
    from PIL import Image
    tmp = pathlib.Path(tempfile.mkdtemp())
    rows = (len(ds) + cols - 1) // cols
    data = json.dumps({"pal": P, "list": [export(d) for d in ds], "stock": []}, ensure_ascii=False)
    (tmp / "p.html").write_text(f"""<!doctype html><html><head><meta charset='utf-8'><style>{RFONTS}*{{margin:0;padding:0;box-sizing:border-box}}body{{width:{cols * 600}px;display:flex;flex-wrap:wrap}}.c{{width:600px;height:600px;overflow:hidden;position:relative}}</style>
<script>window.LHHDesignBase='file://{ROOT}/';window.LHHDesigns={data};</script><script src='file://{ROOT}/assets/qr.js'></script><script src='file://{ROOT}/assets/designer.js'></script><script src='file://{ROOT}/assets/designer-more.js'></script></head>
<body><script>var D=LHHDesigner;D.designs.forEach(function(d){{var c=document.createElement('div');c.className='c';c.innerHTML=D.render(d);document.body.appendChild(c);}});
document.fonts.ready.then(function(){{document.querySelectorAll('.c').forEach(function(c){{D.fit(c)}})}});</script></body></html>""", encoding="utf-8")
    png = tmp / "o.png"
    subprocess.run(["google-chrome", "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars", "--allow-file-access-from-files",
                    f"--window-size={cols * 600},{rows * 600}", "--force-device-scale-factor=1", "--virtual-time-budget=9000",
                    f"--screenshot={png}", f"file://{tmp / 'p.html'}"], check=True, capture_output=True)
    im = Image.open(png).convert("RGB")
    for i, d in enumerate(ds):
        x, y = (i % cols) * 600, (i // cols) * 600
        im.crop((x, y, x + 600, y + 600)).resize((size, size), Image.LANCZOS).save(OUT / f"{d['slug']}.webp", quality=80, method=5)
    return len(ds)


def render(d):
    """Draws a design with assets/designer.js (the same code as the site) and saves assets/occasions/<slug>.webp."""
    tmp = pathlib.Path(tempfile.mkdtemp())
    data = js()
    (tmp / "p.html").write_text(f"""<!doctype html><html><head><meta charset='utf-8'><style>{RFONTS}*{{margin:0;padding:0;box-sizing:border-box}}html,body{{width:600px;height:600px;overflow:hidden}}</style>
<script>window.LHHDesignBase='file://{ROOT}/';</script><script src='file://{ROOT}/assets/qr.js'></script><script>{data}</script><script src='file://{ROOT}/assets/designer.js'></script><script src='file://{ROOT}/assets/designer-more.js'></script></head>
<body><div id=m></div><script>var D=LHHDesigner,m=document.getElementById('m');m.innerHTML=D.render(D.get({json.dumps(d['slug'])}));
document.fonts.ready.then(function(){{D.fit(m)}});</script></body></html>""", encoding="utf-8")
    png = tmp / "o.png"
    subprocess.run(["google-chrome", "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars", "--allow-file-access-from-files",
                    "--window-size=600,600", "--force-device-scale-factor=2", "--virtual-time-budget=4000",
                    f"--screenshot={png}", f"file://{tmp / 'p.html'}"], check=True, capture_output=True)
    from PIL import Image
    Image.open(png).convert("RGB").resize((600, 600), Image.LANCZOS).save(OUT / f"{d['slug']}.webp", quality=88, method=6)
    return d["slug"]


def sheet(page):
    from PIL import Image, ImageDraw
    ds = [d for d in DESIGNS if d["page"] == page]
    cols = 6; t = 300
    im = Image.new("RGB", (cols * (t + 10) + 10, ((len(ds) + cols - 1) // cols) * (t + 10) + 10), "#888")
    for i, d in enumerate(ds):
        x = 10 + (i % cols) * (t + 10); y = 10 + (i // cols) * (t + 10)
        im.paste(Image.open(OUT / f"{d['slug']}.webp").convert("RGB").resize((t, t)), (x, y))
    im.save(f"/tmp/biz_sheet_{page}.png")


if __name__ == "__main__" and sys.argv[1:2] == ["batch"]:
    # python3 tools/biz_designs.py batch [all]: the generated designs (the hand-made ones keep their 600 px pictures)
    hand = {d["slug"] for d in DESIGNS[:HAND_COUNT]}
    todo = [d for d in DESIGNS if d["slug"] not in hand and ("all" in sys.argv or not (OUT / f"{d['slug']}.webp").exists())]
    chunks = [todo[i:i + 25] for i in range(0, len(todo), 25)]
    with ThreadPoolExecutor(4) as ex:
        done = sum(ex.map(render_batch, chunks))
    print("rendered", done)
    sys.exit(0)

if __name__ == "__main__":
    args = sys.argv[1:]
    want = [d for d in DESIGNS if (args and args[0] == "all") or (d["slug"] in args) or (not [a for a in args if a != "sheet"] and not (OUT / f"{d['slug']}.webp").exists())]
    slugs = [d["slug"] for d in DESIGNS]
    assert len(slugs) == len(set(slugs)), "duplicate slug"
    with ThreadPoolExecutor(6) as ex:
        for s in ex.map(render, want):
            print(s)
    if "sheet" in args:
        for pg in ("business", "weddings", "graduation", "parties"):
            sheet(pg)
