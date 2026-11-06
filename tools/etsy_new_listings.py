"""Adds the site's other collections to functions/etsy-listings.json as Etsy listings (one listing per collection, the
designs as the "Design" menu), and puts all listings in the site's order. Texts are in English (the shop is in
English). The menu and the photos are filled by tools/etsy_photos.py. Run once; running again changes nothing."""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
P = ROOT / "functions" / "etsy-listings.json"

# the site's order (tools/catalog.py DISPLAY, as the collection pages show it in November), photo magnets first
SITE_ORDER = ["photo-magnets", "pet-photo-magnets", "family-photo-magnets",
              "places", "world", "ink-cities", "city-sketches",
              "fall", "halloween", "christmas", "holidays", "summer",
              "americana", "mexico", "ireland", "italia", "puerto-rico", "philippines", "india", "korea", "japan", "brasil",
              "greece", "france",
              "bee-kind", "furry-friends", "kitchen-words", "bumper-stickers", "night-sky", "great-masters", "horror",
              "mythology", "home-notes", "birth-flowers", "storybook-classics", "fairy-tales", "wise-words"]

NEW = {
    "places": ("USA Places", "Places",
               "US Travel Poster Magnets, National Park Magnet, City Souvenir Fridge Magnet, Road Trip Gift, Vintage Travel Art, Handmade 2x2",
               "Painted travel posters of the American cities, national parks and coastlines people love most, from the Grand Canyon to New York, Miami Beach and San Francisco. A little souvenir of a trip, or of home.",
               ["travel magnet", "national park gift", "city magnet", "road trip gift", "travel poster", "usa souvenir",
                "vintage travel art", "fridge magnets", "grand canyon", "new york magnet", "housewarming gift", "travel lover gift", "state magnet"]),
    "world": ("World Places", "Places",
              "World Travel Poster Magnets, Paris Magnet, Santorini Souvenir, Kyoto Fridge Magnet, Wanderlust Gift, Travel Art, Handmade 2x2",
              "Our colorful travel posters go abroad: Paris at sunset, Mount Fuji in cherry blossom season, the blue domes of Santorini, Rio, Venice and more. For the trips you took and the ones still on the list.",
              ["travel magnet", "paris magnet", "santorini gift", "world travel", "wanderlust gift", "travel poster",
               "souvenir magnet", "fridge magnets", "kyoto magnet", "venice magnet", "travel lover gift", "bucket list gift", "europe travel"]),
    "ink-cities": ("Ink Cities", "Places",
                   "Pen and Ink City Magnets, Engraving Style Travel Art, New York Paris City Sketch, Architecture Gift, Fridge Magnet, Handmade 2x2",
                   "Richly drawn pen and ink scenes of the world's great cities, shaded like old engravings on warm paper. New York, Paris, Amsterdam, Barcelona, Kyoto, Edinburgh and more.",
                   ["city magnet", "pen and ink art", "engraving art", "architecture gift", "travel magnet", "new york magnet",
                    "paris magnet", "fridge magnets", "city sketch", "travel lover gift", "black and white", "vintage city art", "souvenir magnet"]),
    "city-sketches": ("City Sketches", "Places",
                      "City Line Drawing Magnets, Minimalist Travel Sketch, London New York Lisbon Magnet, Modern Fridge Magnet, Handmade 2x2",
                      "Crisp black line drawings of the cities we love, framed like pages from a travel sketchbook. Simple, graphic and easy to mix: London, New York, Lisbon, Kyoto, Prague, Chicago and more.",
                      ["city magnet", "line drawing", "minimalist magnet", "travel sketch", "london magnet", "new york magnet",
                       "lisbon gift", "fridge magnets", "modern decor", "travel lover gift", "black and white", "city skyline", "souvenir magnet"]),
    "fall": ("Fall", "Seasonal",
             "Fall Fridge Magnets, Pumpkin Spice Magnet, Autumn Kitchen Decor, Thanksgiving Hostess Gift, Cozy Sweater Weather, Handmade 2x2",
             "Warm rust, mustard and olive for the coziest season of the year: pumpkin patches, falling leaves, sweater weather and a lot of pumpkin spice.",
             ["fall magnet", "pumpkin spice", "autumn decor", "thanksgiving gift", "hostess gift", "sweater weather",
              "fall kitchen decor", "fridge magnets", "pumpkin magnet", "cozy gift", "fall decor", "harvest decor", "teacher gift"]),
    "halloween": ("Halloween", "Seasonal",
                  "Halloween Fridge Magnets, Cute Spooky Magnet, Black Cat Ghost Magnet, Boo Basket Filler, Halloween Decor, Handmade 2x2",
                  "Ghosts, bats, black cats and a few bad puns. Spooky, never scary, and just right for a boo basket.",
                  ["halloween magnet", "spooky season", "boo basket", "cute halloween", "black cat magnet", "ghost magnet",
                   "witch magnet", "fridge magnets", "halloween decor", "trick or treat", "spooky gift", "october decor", "pumpkin magnet"]),
    "holidays": ("Holidays & Dates", "Seasonal",
                 "Holiday Fridge Magnets, Valentine Magnet, Mother's Day Gift, Graduation Gift, Teacher Thank You, Birthday Magnet, Handmade 2x2",
                 "Little gifts for every date on the calendar: New Year, Valentine's, Easter, Mother's and Father's Day, graduation, the 4th, Thanksgiving and birthdays.",
                 ["holiday magnet", "valentine gift", "mothers day gift", "graduation gift", "teacher gift", "birthday magnet",
                  "easter gift", "fridge magnets", "galentines gift", "fathers day gift", "small gift", "card insert gift", "new year magnet"]),
    "summer": ("Summer", "Seasonal",
               "Summer Beach Fridge Magnets, Vitamin Sea Magnet, Beach House Decor, Coastal Kitchen Magnet, Vacation Gift, Handmade 2x2",
               "Bright, beachy colors for long days, salty hair and endless sunsets. Vitamin sea for the fridge.",
               ["beach magnet", "summer magnet", "vitamin sea", "beach house decor", "coastal decor", "vacation gift",
                "ocean magnet", "fridge magnets", "lake house gift", "beach lover gift", "tropical magnet", "summer decor", "sunset magnet"]),
    "india": ("India", "Heritage",
              "Indian Fridge Magnets, Desi Gift, Chai Magnet, Diwali Gift, Masala Dabba Magnet, Indian Kitchen Decor, Handmade 2x2",
              "From cutting chai and Nani's kitchen to Diwali diyas and three pressure-cooker whistles, little painted pieces of ghar for every desi fridge.",
              ["indian gift", "desi gift", "chai magnet", "diwali gift", "indian kitchen", "masala magnet",
               "india magnet", "fridge magnets", "gift for indian", "rakhi gift", "indian decor", "desi kitchen", "bollywood gift"]),
    "korea": ("Korea", "Heritage",
              "Korean Fridge Magnets, Korean Gift, Kimchi Magnet, Halmeoni Gift, Korean Food Magnet, Korean Kitchen Decor, Handmade 2x2",
              "Hand-painted love letters to Korea: halmeoni's kitchen, bubbling tteokbokki, bibimbap, Jeju's sea women and the warm feeling of jeong.",
              ["korean gift", "korea magnet", "korean food", "kimchi magnet", "halmeoni gift", "korean kitchen",
               "saranghae", "fridge magnets", "gift for korean", "seoul magnet", "korean decor", "kdrama fan gift", "bibimbap magnet"]),
    "japan": ("Japan", "Heritage",
              "Japanese Fridge Magnets, Japan Gift, Ramen Magnet, Lucky Cat Magnet, Kyoto Souvenir, Japanese Kitchen Decor, Handmade 2x2",
              "Hand-painted everyday Japan, from onigiri and steaming ramen to lantern-lit Kyoto alleys, snow monkeys in the onsen and a beckoning lucky cat.",
              ["japanese gift", "japan magnet", "ramen magnet", "lucky cat", "kyoto souvenir", "japanese kitchen",
               "onigiri magnet", "fridge magnets", "gift for japanese", "japan travel", "japanese decor", "tokyo magnet", "maneki neko"]),
    "greece": ("Greece", "Heritage",
               "Greek Fridge Magnets, Greek Gift, Yiayia Magnet, Evil Eye Magnet, Santorini Souvenir, Greek Kitchen Decor, Handmade 2x2",
               "From yiayia's tapsi of spanakopita and the evil-eye mati by the door to blue domes, red Easter eggs and a frappe on the beach. Kali orexi, and siga siga!",
               ["greek gift", "greece magnet", "yiayia gift", "evil eye magnet", "santorini magnet", "greek kitchen",
                "opa magnet", "fridge magnets", "gift for greek", "greek decor", "mati magnet", "greek easter", "mediterranean"]),
    "france": ("France", "Heritage",
               "French Fridge Magnets, France Gift, Baguette Magnet, Bonjour Magnet, Paris Kitchen Decor, Francophile Gift, Handmade 2x2",
               "Everyday French life in hand-painted gouache: the morning baguette, a cafe creme au comptoir, Mamie's cocotte and l'heure de l'apero, for every family that signs off with bisous.",
               ["french gift", "france magnet", "baguette magnet", "francophile gift", "paris kitchen", "bonjour magnet",
                "french kitchen", "fridge magnets", "gift for french", "french decor", "croissant magnet", "oh la la", "paris gift"]),
    "bumper-stickers": ("Bumper Stickers", "Sayings",
                        "Funny Fridge Magnets, Retro Bumper Sticker Magnet, Dad Joke Magnet, Coffee Lover Gift, Funny Gift, Handmade 2x2",
                        "Retro bumper sticker sayings that are way too good for a car. Funny, sweet and a little sassy, for the fridge, the office or a gift bag.",
                        ["funny magnet", "bumper sticker", "retro magnet", "dad joke gift", "coffee lover gift", "funny gift",
                         "white elephant", "fridge magnets", "coworker gift", "gag gift", "office magnet", "sassy magnet", "stocking stuffer"]),
    "night-sky": ("Night Sky", "Signature",
                  "Zodiac Constellation Magnets, Star Sign Gift, Astrology Fridge Magnet, Birthday Zodiac Gift, Celestial Decor, Handmade 2x2",
                  "Every sign of the zodiac drawn as its real constellation, in gold and starlight on a deep night sky. A sweet birthday gift that fits in a card.",
                  ["zodiac magnet", "constellation", "star sign gift", "astrology gift", "birthday gift", "celestial decor",
                   "zodiac gift", "fridge magnets", "horoscope gift", "moon and stars", "night sky", "personalized zodiac", "small gift"]),
    "great-masters": ("Great Masters", "Art & Stories",
                      "Famous Painting Magnets, Starry Night Magnet, Great Wave Magnet, Art Lover Gift, Museum Fridge Magnet, Handmade 2x2",
                      "The world's most beloved paintings, from Van Gogh's starry skies to Hokusai's Great Wave and Klimt's gold, hand-painted in each master's own brushwork. A tiny museum on your fridge.",
                      ["art magnet", "starry night", "great wave", "van gogh gift", "art lover gift", "famous painting",
                       "museum gift", "fridge magnets", "art teacher gift", "monet magnet", "klimt magnet", "art history", "fine art gift"]),
    "horror": ("Horror Classics", "Art & Stories",
               "Horror Classics Fridge Magnets, Dracula Magnet, Gothic Literature Gift, Edgar Allan Poe, Vintage Horror Art, Handmade 2x2",
               "The great tales of terror and old folklore monsters, painted like vintage pulp covers, silent-film cards and penny dreadfuls: moonlight, fog and candle glow, all dread and no gore.",
               ["horror magnet", "dracula magnet", "gothic gift", "edgar allan poe", "horror fan gift", "vintage horror",
                "spooky magnet", "fridge magnets", "gothic decor", "halloween magnet", "book lover gift", "monster magnet", "dark academia"]),
    "mythology": ("Mythology", "Art & Stories",
                  "Mythology Fridge Magnets, Greek Myth Magnet, Norse Mythology Gift, Medusa Magnet, Ancient Legends Art, Handmade 2x2",
                  "The world's great myths, from Medusa's shield and Odin's ravens to the Boat of Ra and Maui's fishhook, painted like the plates of an old illustrated book of legends.",
                  ["mythology magnet", "greek mythology", "norse mythology", "medusa magnet", "myth lover gift", "ancient legends",
                   "history teacher", "fridge magnets", "egyptian myth", "book lover gift", "dark academia", "classics gift", "legend magnet"]),
    "home-notes": ("Home Notes", "Sayings",
                   "Home Sweet Home Magnet, Kind Words Fridge Magnet, Housewarming Gift, Gift for Mom, Sunshine Magnet, Handmade 2x2",
                   "Gentle words in soft colors for moms, grandmas and anyone who needs a little sunshine. A sweet housewarming gift.",
                   ["home magnet", "housewarming gift", "gift for mom", "kind words", "sunshine magnet", "new home gift",
                    "grandma gift", "fridge magnets", "love lives here", "family magnet", "cozy home decor", "encouragement", "small gift"]),
    "birth-flowers": ("Birth Flowers", "Signature",
                      "Birth Flower Magnet, Birth Month Gift, Floral Fridge Magnet, Birthday Gift for Her, Botanical Line Art, Handmade 2x2",
                      "Delicate line drawings of the flower for each birth month, January carnation to December narcissus. A sweet birthday gift that fits in a card.",
                      ["birth flower", "birth month gift", "birthday gift", "floral magnet", "gift for her", "botanical art",
                       "flower magnet", "fridge magnets", "bridesmaid gift", "line art flower", "mom birthday", "card insert gift", "small gift"]),
    "storybook-classics": ("Storybook Classics", "Art & Stories",
                           "Classic Book Magnets, Book Lover Gift, Literary Fridge Magnet, Peter Pan Alice Magnet, Bookworm Gift, Handmade 2x2",
                           "Hand-painted book-plate magnets for bookworms: beloved classics from Alice and Peter Pan to Dracula and Gatsby, each with its own painted scene and a favorite line.",
                           ["book lover gift", "bookworm gift", "literary gift", "classic books", "reading gift", "library magnet",
                            "teacher gift", "fridge magnets", "book club gift", "librarian gift", "english teacher", "dark academia", "story magnet"]),
    "fairy-tales": ("Fairy Tales & Myths", "Art & Stories",
                    "Fairy Tale Fridge Magnets, Storybook Magnet, Little Red Riding Hood, Rapunzel Magnet, Whimsical Gift, Handmade 2x2",
                    "The old stories, freshly painted: Grimm and Andersen fairy tales, Aesop's fables, the Arabian Nights and the great myths of Greece and the North. Once upon a fridge.",
                    ["fairy tale magnet", "storybook gift", "grimm fairy tales", "rapunzel magnet", "whimsical gift", "nursery decor",
                     "book lover gift", "fridge magnets", "once upon a time", "aesop fables", "teacher gift", "enchanted decor", "story magnet"]),
    "wise-words": ("Wise Words", "Sayings",
                   "Inspirational Quote Magnets, Philosophy Gift, Carpe Diem Magnet, Stoic Quote, Motivational Fridge Magnet, Handmade 2x2",
                   "Timeless lines from the world's great thinkers, from Lao Tzu and Socrates to Seneca and Shakespeare, each painted as a little scene.",
                   ["quote magnet", "philosophy gift", "carpe diem", "stoic quote", "motivational gift", "inspirational",
                    "graduation gift", "fridge magnets", "shakespeare gift", "teacher gift", "wisdom quote", "office magnet", "encouragement"]),
}


def main():
    data = json.loads(P.read_text())
    tmpl = next(l for l in data["listings"] if l["id"] == "christmas")
    rest = tmpl["description"][tmpl["description"].index("\n\nWHAT YOU GET"):]
    have = {l["id"] for l in data["listings"]}
    for lid, (name, section, title, intro, tags) in NEW.items():
        assert len(title) <= 140, lid
        assert len(tags) == 13 and all(len(t) <= 20 for t in tags), lid
        if lid in have:
            continue
        data["listings"].append({
            "id": lid, "kind": "design", "name": name, "section": section, "title": title, "tags": tags,
            "price": tmpl["price"], "variations": [{"name": "Design", "options": []}], "images": 0,
            "description": intro + rest, "alt": f"{name} fridge magnet by Little Hive House",
        })
    by = {l["id"]: l for l in data["listings"]}
    assert set(by) == set(SITE_ORDER), set(by) ^ set(SITE_ORDER)
    data["listings"] = [by[i] for i in SITE_ORDER]
    P.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n")
    print(len(data["listings"]), "listings")


if __name__ == "__main__":
    main()
