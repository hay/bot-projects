from dataknead import Knead
from pywikibot import WbTime
from util.skiplist import Skiplist
from util.wikidata import Props, Items, WikidataItem
from util.wikipedia import get_permalink
import pywikibot
import sys

def main():
    items = Knead("projects/data/churchseats/seats-qids.csv").data()
    skiplist = Skiplist("projects/skiplists/churchseats.txt")
    permalink = "https://nl.wikipedia.org/w/index.php?title=Lijst_van_grootste_Nederlandse_kerkgebouwen_naar_zitplaatsen&oldid=56777124"

    for index, item in enumerate(items):
        qid = item["qid"]
        title = item["name"]
        seats = item["seats"]
        print()
        print(f"#{index} / #{len(items)}")
        print(f"Handling {qid} / {title} / {seats} seats")

        print(item)

        if skiplist.has(qid):
            print(f"{qid} in skiplist, skipping")
            continue

        wd_item = WikidataItem(qid)
        claims = wd_item.get_claims()

        if Props.CAPACITY in claims:
            print("This item already has capacity, skipping")
            continue

        wd_item.add_quantity_claim(
            Props.CAPACITY,
            seats,
            references = [
                wd_item.get_item_claim(Props.IMPORTED_FROM, Items.WIKIPEDIA_NL),
                wd_item.get_url_claim(Props.WM_IMPORT_URL, permalink)
            ]
        )

        skiplist.add(qid)

if __name__ == "__main__":
    main()