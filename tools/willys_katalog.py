"""Hämtar ett brett urval av Willys sortiment med aktuella priser och kampanjer.

Användning:  python tools/willys_katalog.py [utfil.json]

För varje sökord sparas de billigaste varorna (per jämförpris) plus varor med kampanj.
Resultatet är en kompakt JSON-lista som matplaneraren använder.
"""
import json
import sys
import time
import urllib.parse
import urllib.request
from datetime import date

SOKORD = """
mjölk|filmjölk|yoghurt naturell|grekisk yoghurt|kvarg|smör|bregott|matlagningsgrädde|vispgrädde|crème fraiche|
gräddfil|ost hushållsost|riven ost|fetaost|halloumi|mozzarella|keso|parmesan|ägg|havredryck|laktosfri mjölk|
kycklingfilé|kycklinglårfilé|hel kyckling|nötfärs|blandfärs|fläskfärs|kycklingfärs|fläskfilé|fläskkarré|
bacon|falukorv|prinskorv|grillkorv|kassler|skinka pålägg|kalkon pålägg|högrevsgryta|entrecote|
laxfilé|torskfilé|sejfilé|fiskpinnar|räkor|tonfisk konserv|makrill i tomat|sill|
tofu|vegofärs|quorn|bönor kidney|kikärtor|svarta bönor|linser röda|vita bönor|
potatis|sötpotatis|morötter|lök gul|rödlök|vitlök|purjolök|broccoli|blomkål|vitkål|spetskål|
zucchini|aubergine|paprika|gurka|tomat|körsbärstomater|isbergssallad|spenat|ruccola|champinjoner|
avokado|majs|ärtor frysta|grönsaksblandning fryst|wokgrönsaker|haricots verts|rödbetor|selleri|ingefära|
banan|äpple|päron|apelsin|citron|lime|vindruvor|frysta bär|blåbär frysta|hallon frysta|
pasta|spaghetti|glutenfri pasta|ris jasmin|basmatiris|fullkornsris|bulgur|couscous|quinoa|nudlar|
glutenfria nudlar|risnudlar|havregryn|glutenfria havregryn|müsli|cornflakes|
bröd|fullkornsbröd|glutenfritt bröd|knäckebröd|glutenfritt knäckebröd|tortilla|glutenfria tortillas|
hamburgerbröd|pitabröd|vetemjöl|glutenfri mjölmix|majsstärkelse|
krossade tomater|passerade tomater|tomatpuré|kokosmjölk|buljong|fond|soja|glutenfri soja|
pesto|ketchup|senap|majonnäs|salsa|tacokrydda|curry|olivolja|rapsolja|vinäger|honung|socker|
salt|svartpeppar|paprikapulver|oregano|basilika|kanel|chiliflakes|
jordnötssmör|nötter|cashewnötter|mandel|solroskärnor|russin|
fryst pizza|frysta köttbullar|färdiga pannkakor|pommes frites|fryst lax|
juice|kaffe|te|mineralvatten|knäckebröd glutenfri|risgrynsgröt|kakao
"""


def hamta(q, size=40):
    url = "https://www.willys.se/search/clean?" + urllib.parse.urlencode({"q": q, "size": size})
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r).get("results", [])


def jmf(x):
    try:
        return float((x.get("comparePrice") or "").replace(" kr", "").replace(",", ".").replace("\xa0", ""))
    except ValueError:
        return x.get("priceValue") or 9e9


def kompakt(x, sok):
    promo = None
    for p in x.get("potentialPromotions") or []:
        pv = (p.get("price") or {}).get("value")
        if pv:
            antal = p.get("qualifyingCount") or 1
            promo = {"styckpris": pv, "minAntal": antal, "text": f"{p.get('conditionLabel') or ''} {p.get('rewardLabel') or ''}".strip()}
            break
    return {
        "kod": x["code"],
        "namn": x.get("name", ""),
        "info": x.get("productLine2", ""),
        "pris": x.get("priceValue"),
        "enhet": x.get("priceUnit", ""),
        "jmf": f"{x.get('comparePrice', '')}/{x.get('comparePriceUnit', '')}",
        "eko": "ecological" in (x.get("labels") or []),
        "kampanj": promo,
        "kategori": sok,
    }


def main():
    ut = sys.argv[1] if len(sys.argv) > 1 else "willys_katalog.json"
    ord_ = [s.strip() for s in SOKORD.replace("\n", "").split("|") if s.strip()]
    varor = {}
    for i, q in enumerate(ord_, 1):
        try:
            res = [x for x in hamta(q) if x.get("online") and not x.get("outOfStock") and x.get("priceValue")]
        except Exception as e:  # nätverksfel: hoppa över sökordet
            print(f"  ✗ {q}: {e}")
            continue
        billigast = sorted(res, key=jmf)[:6]
        kampanj = [x for x in res if x.get("potentialPromotions")][:3]
        for x in billigast + kampanj:
            varor.setdefault(x["code"], kompakt(x, q))
        print(f"{i}/{len(ord_)} {q}: {len(res)} träffar")
        time.sleep(0.3)
    data = {"hamtad": date.today().isoformat(), "antal": len(varor), "varor": list(varor.values())}
    with open(ut, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    print(f"Klart: {len(varor)} varor -> {ut}")


if __name__ == "__main__":
    main()
