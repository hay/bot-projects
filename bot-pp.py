from dataknead import Knead
from pathlib import Path
from pywikibot import WbTime
from util.skiplist import Skiplist
from util.wikidata import WikidataItem, Props, Items
from util.dates import wbtime_now
import pywikibot
import sys

PATH = str(Path(__file__).parent.resolve())
skiplist = Skiplist(PATH + "/skiplists/pp.txt")
WP_PERMALINK = "https://nl.wikipedia.org/w/index.php?title=Historische_zetelverdeling_Tweede_Kamer&oldid=58661500"

def add_party_data(row):
    print("----" * 20)
    print()
    print(row)

    title = row["title"]
    qid = row["qid"]

    if skiplist.has(qid):
        print(f"In skiplist, skipping")
        return

    item = WikidataItem(qid)

    if Props.NR_OF_SEATS in item.get_claims():
        print("Got seats already, skipping party")
        return

    for key, val in row.items():
        if not key.isdigit():
            continue

        year = int(key)

        if val == "":
            continue

        seats = int(val)

        print(f"{title} ({qid}) had {seats} seats in {year}")

        item.add_quantity_claim(
            Props.NR_OF_SEATS, seats,
            qualifiers = [
                item.get_item_claim(Props.LEGISLATIVE_BODY, Items.NL_LOWER_HOUSE),
                item.get_claim(Props.START_TIME, WbTime(year = year))
            ],
            references = [
                item.get_item_claim(Props.IMPORTED_FROM, Items.WIKIPEDIA_NL),
                item.get_url_claim(Props.WM_IMPORT_URL, WP_PERMALINK)
            ]
        )

    skiplist.add(qid)

if __name__ == "__main__":
    data = Knead(f"{PATH}/data/pp/pp.csv", has_header = True).data()

    for item in data:
        try:
            add_party_data(item)
        except Exception as e:
            print("Exception:")
            print(e)
            print()