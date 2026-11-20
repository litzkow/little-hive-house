"""Etsy listings for the design studio's designs (Nov 2026): one listing per kind of business (tools/design_kits.py K)
and one per Personalize theme. The buyer picks a pack size; in the personalization box they write the design number
(from the numbered guide photos) and their words; the owners send a proof before printing.

Photos (etsy/img/<listing>/<n>.jpg): the designs on a fridge, the numbered design guide(s), the real size, how it
works with the prices, and the shop's "good to know". Texts in English (the shop is in English).
Usage:  python3 tools/etsy_custom.py [listing ...]     (then publish with the maintenance task etsy-publish)"""
import json
import pathlib
import sys
import tempfile

from PIL import Image, ImageDraw

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import biz_designs as B          # noqa: E402
import design_kits as K          # noqa: E402
import etsy_photos as EP         # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
ART = pathlib.Path(tempfile.gettempdir()) / "lhh-etsy-custom"
ART.mkdir(exist_ok=True)
HAND = {d["slug"] for d in B.DESIGNS[:B.HAND_COUNT]}

# Etsy prices (each channel has its own price; Etsy's fees are higher than the site's)
BIZ_PACKS = [("50 magnets", 99.0), ("100 magnets", 176.0), ("250 magnets", 385.0), ("500 magnets", 715.0)]
PERSONAL_PACKS = [("1 magnet", 6.99), ("2 magnets", 10.99), ("4 magnets", 19.99), ("10 magnets", 42.99)]

# what people search on Etsy for each kind of business: (the word for it, two more tags)
WORD = {
    "pizza": ("pizzeria", "pizza magnet", "restaurant magnet"), "mexican": ("mexican food", "taco magnet", "restaurant magnet"),
    "burger": ("burger joint", "diner magnet", "restaurant magnet"), "cafe": ("coffee shop", "cafe magnet", "loyalty card"),
    "bakery": ("bakery", "bakery magnet", "cake shop"), "sushi": ("sushi bar", "asian restaurant", "restaurant magnet"),
    "bbq": ("bbq food truck", "food truck magnet", "bbq magnet"), "icecream": ("ice cream shop", "ice cream magnet", "dessert shop"),
    "restaurant": ("restaurant", "restaurant magnet", "menu magnet"), "catering": ("catering", "caterer gift", "event catering"),
    "dentist": ("dentist", "dental office", "dentist magnet"), "ortho": ("orthodontist", "braces magnet", "dental office"),
    "doctor": ("doctor office", "clinic magnet", "medical office"), "pediatrics": ("pediatrician", "pediatric office", "kids doctor"),
    "chiro": ("chiropractor", "chiropractic", "wellness clinic"), "pt": ("physical therapy", "pt clinic", "rehab clinic"),
    "eyes": ("optometrist", "eye doctor", "optical shop"), "pharmacy": ("pharmacy", "drugstore magnet", "pharmacist gift"),
    "cleaning": ("house cleaning", "cleaning business", "maid service"), "hvac": ("hvac", "hvac magnet", "ac repair"),
    "plumber": ("plumber", "plumbing magnet", "plumbing business"), "electric": ("electrician", "electrical service", "contractor magnet"),
    "roofing": ("roofing", "roofer magnet", "contractor magnet"), "lawn": ("lawn care", "landscaping", "lawn service"),
    "pest": ("pest control", "exterminator", "pest service"), "pool": ("pool service", "pool cleaning", "pool company"),
    "moving": ("moving company", "movers magnet", "moving business"), "handyman": ("handyman", "handyman magnet", "home repair"),
    "painter": ("painting company", "house painter", "painter magnet"), "locksmith": ("locksmith", "locksmith magnet", "emergency number"),
    "realtor": ("realtor", "real estate magnet", "closing gift"), "mortgage": ("mortgage", "loan officer", "real estate gift"),
    "insurance": ("insurance agent", "insurance magnet", "agency magnet"), "tax": ("tax preparer", "accountant", "cpa magnet"),
    "lawyer": ("law firm", "attorney magnet", "lawyer gift"), "financial": ("financial advisor", "financial planner", "advisor magnet"),
    "salon": ("hair salon", "salon magnet", "hair stylist"), "barber": ("barbershop", "barber magnet", "barber loyalty"),
    "nails": ("nail salon", "nail tech", "manicure magnet"), "medspa": ("med spa", "esthetician", "spa magnet"),
    "massage": ("massage therapist", "massage magnet", "spa magnet"), "gym": ("gym", "fitness magnet", "gym promo"),
    "yoga": ("yoga studio", "pilates studio", "yoga magnet"), "trainer": ("personal trainer", "fitness coach", "trainer magnet"),
    "tattoo": ("tattoo shop", "tattoo studio", "tattoo magnet"), "vet": ("veterinarian", "vet clinic", "vet magnet"),
    "groomer": ("dog groomer", "pet grooming", "groomer magnet"), "petsitter": ("dog walker", "pet sitter", "pet business"),
    "dogtrainer": ("dog trainer", "dog training", "puppy class"), "autorepair": ("auto repair", "mechanic magnet", "oil change"),
    "tires": ("tire shop", "auto shop", "mechanic magnet"), "detailing": ("car detailing", "car wash", "auto detailing"),
    "towing": ("towing", "tow truck", "roadside service"), "church": ("church", "church magnet", "ministry gift"),
    "nonprofit": ("nonprofit", "charity magnet", "fundraiser"), "school": ("daycare", "preschool magnet", "school magnet"),
    "tutor": ("tutoring", "tutor magnet", "learning center"), "team": ("sports team", "team schedule", "sponsor magnet"),
    "dance": ("dance studio", "music lessons", "dance school"), "florist": ("florist", "flower shop", "florist magnet"),
    "photographer": ("photographer", "photography", "photographer gift"), "boutique": ("boutique", "gift shop", "shop small"),
    "eventvenue": ("event venue", "wedding planner", "venue magnet"), "dj": ("dj", "dj business", "event dj"),
    "general": ("small business", "any business", "company magnet"), "startup": ("small business", "side hustle", "shop small"),
}
PERSONAL = {   # theme: (title, tags, a line for the description)
    "p-photo": ("Custom Photo Magnet with Words, Personalized Picture Magnet with Name and Date, Polaroid Style Photo Gift, Handmade 2x2",
                ["photo magnet", "custom photo magnet", "picture magnet", "polaroid magnet", "photo with name", "personalized gift",
                 "family photo gift", "fridge magnet", "photo gift", "keepsake magnet", "gift for mom", "pet photo magnet", "baby photo gift"],
                "Your photo in a design with your words: a name, a date, a place or a little caption."),
    "p-family": ("Custom Family Name Magnet, Personalized Last Name Fridge Magnet, Established Sign Gift, Housewarming Gift, Handmade 2x2",
                 ["family name magnet", "last name sign", "established sign", "personalized magnet", "housewarming gift", "family gift",
                  "custom magnet", "fridge magnet", "monogram magnet", "wedding gift", "new home gift", "family established", "home decor"],
                 "Your family name and the year you started, in a design you love."),
    "p-home": ("New Home Magnet, Personalized Housewarming Gift, Custom Address Fridge Magnet, First Home Keepsake, Realtor Closing Gift, Handmade 2x2",
               ["new home gift", "housewarming gift", "address magnet", "first home gift", "closing gift", "realtor gift", "custom magnet",
                "fridge magnet", "home sweet home", "wifi magnet", "new homeowner", "moving gift", "personalized gift"],
               "Your new address, your first home, house rules or the guest Wi-Fi."),
    "p-pets": ("Custom Pet Name Magnet, Personalized Dog Fridge Magnet, Cat Mom Gift, Pet Info Magnet for Sitter, Pet Photo Magnet, Handmade 2x2",
               ["pet magnet", "dog name magnet", "cat mom gift", "dog mom gift", "pet info magnet", "pet sitter info", "custom pet gift",
                "fridge magnet", "dog lover gift", "pet photo magnet", "gotcha day", "pet memorial", "personalized pet"],
               "Your pet's name, their photo, the sitter's info or who fed the dog."),
    "p-baby": ("Baby Birth Announcement Magnet, Personalized Newborn Keepsake, Kids Chore Chart Magnet, Babysitter Info Magnet, Handmade 2x2",
               ["birth announcement", "baby keepsake", "newborn gift", "baby stats magnet", "chore chart", "babysitter info", "kids magnet",
                "fridge magnet", "baby shower gift", "new baby gift", "custom baby gift", "toddler gift", "personalized gift"],
               "Birth stats, a first birthday, a chore chart or the babysitter's numbers."),
    "p-grandparents": ("Grandma's Kitchen Magnet, Personalized Grandparents Gift, Nana and Papa Fridge Magnet, Abuela Gift, Handmade 2x2",
                       ["grandma gift", "grandparents gift", "nana gift", "grandma kitchen", "abuela gift", "papa gift", "custom magnet",
                        "fridge magnet", "mothers day gift", "grandparents day", "kitchen magnet", "family gift", "personalized gift"],
                       "Grandma's kitchen, Nana and Papa's house, or the grandkids' names."),
    "p-kitchen": ("Personalized Kitchen Magnet, Family Recipe Fridge Magnet, Taco Tuesday Pizza Friday Sign, Meal Plan Magnet, Handmade 2x2",
                  ["kitchen magnet", "family recipe", "taco tuesday", "pizza night", "meal plan magnet", "grocery list", "custom magnet",
                   "fridge magnet", "moms kitchen", "family tradition", "foodie gift", "kitchen decor", "personalized gift"],
                  "Your family's Pizza Friday, Mom's kitchen, the weekly menu or the grocery list."),
    "p-love": ("Custom Couple Magnet, Personalized Anniversary Gift, Names and Date Fridge Magnet, Wedding Date Keepsake, Valentine Gift, Handmade 2x2",
               ["couple gift", "anniversary gift", "names and date", "wedding date", "valentine gift", "boyfriend gift", "girlfriend gift",
                "fridge magnet", "custom magnet", "love magnet", "mr and mrs", "wife gift", "personalized gift"],
               "Your names, your date and a little line that is just yours."),
    "p-faith": ("Bless This Home Magnet, Personalized Christian Gift, Bible Verse Fridge Magnet, Baptism Keepsake, First Communion Gift, Handmade 2x2",
                ["bless this home", "christian gift", "bible verse magnet", "baptism gift", "first communion", "faith gift", "scripture magnet",
                 "fridge magnet", "custom magnet", "religious gift", "church gift", "housewarming gift", "personalized gift"],
                "A verse, a blessing for the home, a baptism or a first communion."),
    "p-teacher": ("Personalized Teacher Gift Magnet, Thank You Teacher, Coach Gift, End of Year Teacher Appreciation, Classroom Magnet, Handmade 2x2",
                  ["teacher gift", "teacher appreciation", "thank you teacher", "coach gift", "end of year gift", "classroom magnet",
                   "teacher magnet", "fridge magnet", "custom magnet", "school gift", "daycare teacher", "small gift", "personalized gift"],
                  "A thank-you for a teacher or a coach, with their name and the class."),
    "p-sports": ("Custom Sports Team Magnet, Personalized Jersey Name Number Magnet, Game Schedule Fridge Magnet, Soccer Mom Gift, Handmade 2x2",
                 ["team magnet", "jersey magnet", "game schedule", "soccer mom", "football mom", "sports gift", "team name magnet",
                  "fridge magnet", "custom magnet", "baseball mom", "player gift", "coach gift", "personalized gift"],
                 "Your player's name and number, the team or the season's game schedule."),
    "p-holidays": ("Personalized Christmas Magnet, Family Holiday Fridge Magnet, Custom Christmas Card Alternative, Thanksgiving Easter Gift, Handmade 2x2",
                   ["christmas magnet", "family christmas", "holiday magnet", "christmas card", "stocking stuffer", "thanksgiving gift",
                    "easter gift", "fridge magnet", "custom magnet", "holiday gift", "new year magnet", "photo christmas", "personalized gift"],
                   "A Christmas card that stays on the fridge, a Thanksgiving thank-you or Easter."),
    "p-travel": ("Custom Vacation Magnet, Personalized Travel Souvenir, Family Trip Fridge Magnet, Beach Trip Keepsake, Photo Travel Magnet, Handmade 2x2",
                 ["vacation magnet", "travel souvenir", "family trip", "beach trip", "travel magnet", "trip keepsake", "road trip gift",
                  "fridge magnet", "custom magnet", "photo magnet", "honeymoon gift", "travel gift", "personalized gift"],
                 "The trip you just came back from: the place, the year and your family's name."),
}

PERSO_BIZ = "Design number + your business name, phone, website and any words to change. Send your logo in Etsy messages. We send a proof first."
PERSO_ME = "Design number + your words (names, date, place). For photo designs, send your photo in Etsy messages. We send a proof first."


def tags_ok(tags):
    out = []
    for t in tags:
        t = t.strip().lower()[:20].strip()
        if t and t not in out:
            out.append(t)
    return out[:13]


def business_listing(k, n):
    w, a, b = WORD.get(k["key"], (k["name"].lower(), "business magnet", "promo magnet"))
    name = k["name"]
    if k["key"] in ("general", "startup"):
        title = (f"Custom Business Magnet, Personalized Logo Fridge Magnet for Any Small Business, Promo Magnet with Phone Number, Bulk 2x2"
                 if k["key"] == "general" else
                 "Small Business Magnet, Custom Logo Fridge Magnet for Shops and Side Hustles, Thank You Magnet, Coupon Magnet, Bulk 2x2")
    else:
        title = f"Custom {name} Magnet, Personalized {w.title()} Fridge Magnet with Logo, Business Promo Magnet, Coupon or QR Code, Bulk 2x2"
    if len(title) > 140:
        title = f"Custom {name} Magnet, Personalized {w.title()} Fridge Magnet with Logo, Promo Magnet, Bulk 2x2"
    title = title[:140]
    tags = tags_ok([f"{w} magnet" if len(w) <= 13 else w, a, b, "business magnet", "custom magnet", "logo magnet", "promo magnet",
                    "fridge magnet", "client gift", "marketing magnet", "qr code magnet", "coupon magnet", "small business"])
    desc = (f"Your {name.lower()} on your customers' fridge all year. A business card gets lost in a drawer; a magnet with your name, "
            f"number and a reason to call stays on the fridge.\n\n"
            f"{n} ready-made designs for a {name.lower()}: coupons that bring customers back, your number in big letters, QR codes "
            f"for your menu, reviews or booking, photo designs, useful checklists and elegant logo designs.\n\n"
            "HOW IT WORKS\n1. Pick a pack size.\n2. In the personalization box, write the design number (from the numbered photos) and your "
            "words: business name, phone, website, offer.\n3. Send your logo in Etsy messages (PNG or JPG). No logo? We use a drawing that fits.\n"
            "4. We send you a proof within one business day. Change anything you want: colors, words, the drawing.\n5. We print, press and "
            "pack every magnet by hand and ship in 3 to 5 business days after you approve.\n\n"
            "WHAT YOU GET\n2 x 2 inch square magnets with square corners, a glossy wipe-clean front and a strong magnet back. All the "
            "magnets in a pack are the same design.\n\nGOOD TO KNOW\nQR codes are tested before printing. Want a different design for "
            "each location or a design you don't see here? Message us; we design it for free.\n\nLittle Hive House is a small family "
            "studio: we design, print and press every magnet ourselves.")
    return dict(id=f"biz-{k['key']}", kind="custom", name=name, section="Business Magnets", title=title, tags=tags,
                price=BIZ_PACKS[0][1], variations=[{"name": "Pack size", "options": [o for o, _ in BIZ_PACKS], "prices": [p for _, p in BIZ_PACKS]}],
                description=desc, personalization=PERSO_BIZ, alt=f"Custom {name.lower()} magnet by Little Hive House")


def personal_listing(key, name, n):
    title, tags, line = PERSONAL[key]
    desc = (f"{line} Made just for you, by hand.\n\n{n} designs to choose from, numbered in the photos.\n\n"
            "HOW IT WORKS\n1. Pick how many magnets.\n2. In the personalization box, write the design number and your words: names, "
            "a date, a place, a little line.\n3. Photo designs: send your photo in Etsy messages (the original from your phone is best).\n"
            "4. We send you a proof within one business day. Change anything you want: colors, words.\n5. We print, press and pack every "
            "magnet by hand and ship in 3 to 5 business days after you approve.\n\n"
            "WHAT YOU GET\n2 x 2 inch square magnets with square corners, a glossy wipe-clean front and a strong magnet back. All the "
            "magnets in a pack are the same design (a pack of 4 makes lovely gifts for the whole family).\n\n"
            "Little Hive House is a small family studio: we design, print and press every magnet ourselves.")
    return dict(id=key, kind="custom", name=name, section="Personalized Magnets", title=title[:140], tags=tags_ok(tags),
                price=PERSONAL_PACKS[0][1], variations=[{"name": "Pack size", "options": [o for o, _ in PERSONAL_PACKS], "prices": [p for _, p in PERSONAL_PACKS]}],
                description=desc, personalization=PERSO_ME, alt=f"Personalized {name.lower()} magnet by Little Hive House")


# ---------------------------------------------------------------- photos
def how_it_works(business, packs):
    im = EP.cream_bg()
    d = ImageDraw.Draw(im)
    EP.header(d, "Made just for you", "How it works", y=150)
    steps = ([("Pick a pack", "50 to 500 magnets"), ("Write the design number", "and your words in the box"),
              ("Send your logo", "in Etsy messages"), ("Approve the proof", "within one business day")] if business else
             [("Pick how many", "1 to 10 magnets"), ("Write the design number", "and your words in the box"),
              ("Photo designs", "send your photo in messages"), ("Approve the proof", "within one business day")])
    x0, gap = 330, 780
    for i, (a, b) in enumerate(steps):
        x = x0 + i * gap
        d.ellipse([x - 95, 520, x + 95, 710], fill=EP.HONEY)
        EP.text_center(d, (x, 650), str(i + 1), EP.font("josefin", 110, 700), "#FFFFFF")
        EP.text_center(d, (x, 830), a, EP.font("josefin", 50, 700), EP.BROWN)
        EP.text_center(d, (x, 905), b, EP.font("jost", 44, 420), EP.BROWN_SOFT)
    # the prices
    EP.text_center(d, (EP.W / 2, 1150), "PRICES", EP.font("josefin", 46, 600), EP.BROWN_SOFT, spacing=9)
    cw = 560
    left = EP.W / 2 - (len(packs) - 1) * cw / 2
    for i, (o, p) in enumerate(packs):
        x = left + i * cw
        d.rounded_rectangle([x - 240, 1220, x + 240, 1560], radius=36, fill="#FFFCF4", outline=EP.LINES, width=4)
        EP.text_center(d, (x, 1360), o.split()[0], EP.font("josefin", 120, 700), EP.BROWN)
        EP.text_center(d, (x, 1430), o.split()[1], EP.font("jost", 44, 420), EP.BROWN_SOFT)
        EP.text_center(d, (x, 1515), f"${p:,.2f}".replace(".00", ""), EP.font("jost", 54, 600), EP.HONEY)
    EP.text_center(d, (EP.W / 2, 1750), "All the magnets in a pack are the same design. Want a design that isn't here? Message us.", EP.font("jost", 46, 400), EP.BROWN_SOFT)
    EP.text_center(d, (EP.W / 2, 1880), "2 x 2 in, square corners, pressed by hand", EP.font("caveat", 74), "#C57A0A")
    return im


def photos_for(listing, designs, business):
    arts = {d["slug"]: ART / f"{d['slug']}.png" for d in designs}
    todo = [d for d in designs if not arts[d["slug"]].exists()]
    for i in range(0, len(todo), 25):
        B.render_batch(todo[i:i + 25], size=600, out=ART, ext="png")
    # the fridge: one design of each purpose first, so the photo shows how different they are
    seen, first = set(), []
    for d in designs:
        if d["row"] not in seen:
            seen.add(d["row"]); first.append(d)
    first = (first + [d for d in designs if d not in first])[:5]
    imgs = [Image.open(arts[d["slug"]]).convert("RGB") for d in first]
    spots, k = EP.free_layout("fridge", len(imgs), 5 + len(listing["id"]))
    out = [EP.lifestyle("fridge", [(im, x, y, a) for im, (x, y, a) in zip(imgs, spots)], seed=4, shadow=0.3, scale=k)]
    SHORT = {"promo": "Coupon", "number": "Your number", "qr": "QR code", "photo": "With a photo", "useful": "Useful", "brand": "Logo design",
             "thanks": "Thank you", "name": "With your name", "fun": "Just for fun", "gift": "Gift", "pclassic": "Classic photo",
             "psnap": "Polaroid", "pbold": "Big photo"}
    def label(d):
        t = (d.get("title") or "").split(" · ")[-1]
        hand = d["slug"] in HAND
        return t if hand and t else SHORT.get(d["row"], t or listing["name"])
    pairs = [(d["slug"], label(d)) for d in designs][:120]
    charts = EP.design_charts(listing["name"], pairs, arts)
    out += charts[:5]
    out.append(EP.size_photo(imgs[0], note="Your words,\nyour colors,\nyour magnet",
                             details=["2 x 2 inch square (5 cm)", "Square corners", "Glossy, wipe-clean front", "Strong magnet back",
                                      "Proof before we print"]))
    out.append(how_it_works(business, BIZ_PACKS if business else PERSONAL_PACKS))
    out.append(Image.open(ROOT / "tools" / "etsy_shop" / "good-to-know.jpg").convert("RGB"))
    return out[:10]


def save(listing, photos):
    out = EP.OUT / listing["id"]
    out.mkdir(parents=True, exist_ok=True)
    for f in out.glob("*.jpg"):
        f.unlink()
    for i, p in enumerate(photos):
        p = p.convert("RGB")
        p = p.resize((2000, round(2000 * p.size[1] / p.size[0])), Image.LANCZOS)   # Etsy's recommended size, lighter for the site
        p.save(out / f"{i + 1}.jpg", quality=84, optimize=True, progressive=True)
    listing["images"] = len(photos)


def main(only):
    data = json.loads(EP.LISTINGS.read_text())
    keep = [l for l in data["listings"] if l.get("kind") != "custom"]
    old = {l["id"]: l for l in data["listings"] if l.get("kind") == "custom"}
    new = []
    for k in K.K:
        ds = [d for d in B.DESIGNS if d["set"] == k["key"]]
        new.append((business_listing(k, len(ds)), ds, True))
    for key, meta in B.SETS.items():
        if meta["page"] != "personalize":
            continue
        ds = [d for d in B.DESIGNS if d["set"] == key]
        new.append((personal_listing(key, meta["name"], len(ds)), ds, False))
    out = []
    for l, ds, biz in new:
        l["designs"] = [d["slug"] for d in ds]   # design number n = designs[n-1] (for the owners' proof)
        if only and l["id"] not in only:
            if l["id"] in old:
                l["images"] = old[l["id"]].get("images", 0)
                if old[l["id"]].get("imagesVersion"): l["imagesVersion"] = old[l["id"]]["imagesVersion"]
            out.append(l)
            continue
        ph = photos_for(l, ds, biz)
        save(l, ph)
        l["imagesVersion"] = int(data.get("imagesVersion", 1)) + 1
        out.append(l)
        print(l["id"], len(ph), "photos", len(ds), "designs", flush=True)
    # right at the front of the shop, like on the site: the photo magnets, then the business and personalized sections;
    # the first 4 listings are the shop's featured ones (functions/etsy.js arrange)
    photo = [l for l in keep if l.get("kind") == "photo"]
    rest = [l for l in keep if l.get("kind") != "photo"]
    biz = [l for l in out if l["id"].startswith("biz-")]
    per = [l for l in out if not l["id"].startswith("biz-")]
    lead = [x for x in [next((l for l in biz if l["id"] == "biz-general"), None), next((l for l in per if l["id"] == "p-family"), None),
                        next((l for l in per if l["id"] == "p-photo"), None)] if x]
    first = photo[:1] + lead
    data["listings"] = first + [l for l in photo if l not in first] + [l for l in biz if l not in first] + [l for l in per if l not in first] + rest
    EP.LISTINGS.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n")


if __name__ == "__main__":
    main(sys.argv[1:])
