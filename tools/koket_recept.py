"""Hämtar populära familjerecept från Köket.se (recept.nu) för privat bruk i matplaneraren.

Användning:  python tools/koket_recept.py [utfil.json]

För varje klassisk familjerätt letar skriptet upp kandidater i Kökets sitemap,
läser receptets strukturerade data (schema.org/Recipe) och väljer varianten
med flest betygsröster, alltså den mest populära.

Kökets villkor tillåter kopiering för eget, privat bruk men inte spridning till allmänheten.
Håll därför appen privat (dela den bara med familjen).
"""
import html
import json
import re
import sys
import time
import urllib.request

# (namn i appen, emoji, ord som ska finnas i adressen)
RATTER = [
    ("Tacos", "🌮", ["tacos"]),
    ("Köttbullar", "🧆", ["kottbullar"]),
    ("Spaghetti med köttfärssås", "🍝", ["kottfarssas"]),
    ("Lasagne", "🍝", ["lasagne"]),
    ("Pannkakor", "🥞", ["pannkakor"]),
    ("Fiskgratäng", "🐟", ["fiskgratang"]),
    ("Kycklinggryta", "🍲", ["kycklinggryta"]),
    ("Korv stroganoff", "🌭", ["korv", "stroganoff"]),
    ("Köttfärslimpa", "🍖", ["kottfarslimpa"]),
    ("Pyttipanna", "🥔", ["pytt"]),
    ("Pasta carbonara", "🍝", ["carbonara"]),
    ("Laxpasta", "🍝", ["laxpasta"]),
    ("Lax i ugn", "🐟", ["lax", "ugn"]),
    ("Kyckling i ugn", "🍗", ["kyckling", "ugn"]),
    ("Hamburgare", "🍔", ["hamburgare"]),
    ("Hemgjord pizza", "🍕", ["pizza"]),
    ("Köttgryta", "🍲", ["kottgryta"]),
    ("Tomatsoppa", "🍅", ["tomatsoppa"]),
    ("Ärtsoppa", "🥣", ["artsoppa"]),
    ("Kålpudding", "🥬", ["kalpudding"]),
    ("Falukorv i ugn", "🌭", ["falukorv"]),
    ("Potatisgratäng", "🥔", ["potatisgratang"]),
    ("Wok", "🥢", ["wok"]),
    ("Chili con carne", "🌶️", ["chili-con-carne"]),
    ("Fiskpinnar", "🐟", ["fiskpinnar"]),
    ("Pasta med pesto", "🌿", ["pesto", "pasta"]),
    ("Makaronilåda", "🧀", ["makaronilada"]),
    ("Risotto", "🍚", ["risotto"]),
    ("Kycklingcurry", "🍛", ["kycklingcurry"]),
    ("Nudlar", "🍜", ["nudlar"]),
    ("Quesadillas", "🫓", ["quesadilla"]),
    ("Enchiladas", "🌯", ["enchilada"]),
    ("Raggmunk", "🥔", ["raggmunk"]),
    ("Linsgryta", "🥘", ["linsgryta"]),
    ("Minestrone", "🥣", ["minestrone"]),
    ("Kycklingklubbor", "🍗", ["kycklingklubbor"]),
    ("Schnitzel", "🍖", ["schnitzel"]),
    ("Burritos", "🌯", ["burrito"]),
    ("Flygande Jacob", "🍌", ["flygande-jacob"]),
    ("Korvgryta", "🍲", ["korvgryta"]),
    ("Fläskpannkaka", "🥓", ["flaskpannkaka"]),
    ("Kycklingnuggets", "🍗", ["nuggets"]),
    ("Biff Stroganoff", "🥩", ["biff", "stroganoff"]),
    ("Kalops", "🍲", ["kalops"]),
    ("Dumplings", "🥟", ["dumplings"]),
]
# Rätter där adress-sökningen ger för udda varianter: välj bland dessa klassiska recept i stället
FORVAL = {
    "Lasagne": ["klassisk-lasagne", "lasagne-bolognese", "gunillas-lasagne", "tacolasagne", "lasagne-bechamel"],
    "Pasta carbonara": ["klassisk-spaghetti-carbonara", "spaghetti-carbonara", "familjens-godaste-carbonara",
                        "svensk-pasta-carbonara", "pasta-carbonara-med-gradde", "jennys-spaghetti-carbonara"],
    "Kycklingcurry": ["kycklingcurry-med-ris", "curry-nam-nam-gul-kycklingcurry", "kycklingcurry-med-apple-och-mango-chutney"],
    "Laxpasta": ["kramig-laxpasta", "kramig-laxpasta-med-tomat-och-orter", "laxpasta-med-citron-och-basilikasas"],
    "Hemgjord pizza": ["pizzadeg", "pizzadeg-2", "storpizza", "pizzabullar"],
    "Pyttipanna": ["pytt-i-panna", "skinkpytt", "gronsakspytt", "pytt-med-skinka"],
    "Hamburgare": ["klassisk-hamburgare", "hemmagjorda-hamburgare", "den-klassiska-hamburgaren", "hamburgare-med-ost"],
    "Kycklinggryta": ["kycklinggryta-med-curry", "kycklinggryta-med-kokosgradde", "allt-i-ett-kycklinggryta", "kycklinggryta-med-ananas"],
    "Risotto": ["risotto-grundrecept", "risotto-med-korv", "gronsaksrisotto", "parmesanrisotto"],
    "Falukorv i ugn": ["falukorv-i-ugn-med-bostongurka", "falukorv-med-ostsas", "falukorvskebab",
                       "stekt-falukorv-med-senapssas", "kramig-falukorvsgryta", "enkel-falukorvsgratang"],
    "Köttbullar": ["kottbullar", "svenska-kottbullar", "hemlagade-kottbullar", "husets-kottbullar", "magiska-kottbullar"],
}
SKIP = re.compile(r"(^|-)(jul|tips|sa-|har-ar|vin-till|basta-satten|guide|test|ar-)")
UA = {"User-Agent": "Mozilla/5.0 (privat receptlista)"}


def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read().decode("utf-8", "ignore")


def recipe_of(url):
    t = get(url)
    for m in re.findall(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', t, re.S):
        try:
            d = json.loads(m)
        except json.JSONDecodeError:
            continue
        for x in d if isinstance(d, list) else d.get("@graph", [d]):
            if isinstance(x, dict) and x.get("@type") == "Recipe":
                return x
    return None


def minuter(iso):
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?", iso or "")
    return (int(m.group(1) or 0) * 60 + int(m.group(2) or 0)) or None if m else None


def ren(t):
    return re.sub(r"\s+", " ", html.unescape(html.unescape(t or ""))).strip()


def steg(instr):
    ut = []
    for s in instr or []:
        if isinstance(s, str):
            ut.append(s)
        elif s.get("@type") == "HowToSection":
            ut += steg(s.get("itemListElement"))
        elif s.get("text"):
            ut.append(s["text"])
    return [ren(x) for x in ut if x.strip()]


def main():
    ut = sys.argv[1] if len(sys.argv) > 1 else "koket_recept.json"
    slugs = re.findall(r"<loc>https://www\.koket\.se/([a-z0-9-]+)</loc>", get("https://www.koket.se/sitemap.xml"))
    print(f"{len(slugs)} sidor i sitemap")
    valda = []
    for namn, emoji, ord_ in RATTER:
        kand = [s for s in FORVAL[namn] if s in slugs] if namn in FORVAL else \
            sorted({s for s in slugs if all(o in s for o in ord_) and not SKIP.search(s)}, key=len)[:8]
        bast = None
        for s in kand:
            try:
                r = recipe_of(f"https://www.koket.se/{s}")
            except Exception:
                r = None
            time.sleep(0.3)
            if not r or not r.get("recipeIngredient"):
                continue
            antal = int((r.get("aggregateRating") or {}).get("ratingCount") or 0)
            if not bast or antal > bast[0]:
                bast = (antal, s, r)
        if not bast:
            print(f"  ✗ {namn}: inget recept")
            continue
        antal, s, r = bast
        ing = [ren(i) for i in r["recipeIngredient"] if i and ren(i) and ren(i).lower() != "ingredienser"]
        valda.append({
            "id": "koket-" + s[:180],
            "namn": namn, "titel": ren(r.get("name")) or namn, "emoji": emoji,
            "beskrivning": ren(r.get("description")).strip('"').strip()[:300],
            "tid": minuter(r.get("totalTime")), "portioner": r.get("recipeYield") or "",
            "ingredienser": ing, "steg": steg(r.get("recipeInstructions")),
            "betyg": (r.get("aggregateRating") or {}).get("ratingValue"), "roster": antal,
            "kalla": "Köket.se", "url": f"https://www.koket.se/{s}",
        })
        print(f"  ✓ {namn}: {r.get('name')} ({antal} röster)")
    with open(ut, "w", encoding="utf-8") as f:
        json.dump(valda, f, ensure_ascii=False, indent=1)
    print(f"Klart: {len(valda)} recept -> {ut}")


if __name__ == "__main__":
    main()
