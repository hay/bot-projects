from dataknead import Knead
from pathlib import Path
from util.skiplist import Skiplist
from util.wikidata import Props, Items, WikidataItem
import pywikibot
import sys

PATH = str(Path(__file__).parent.resolve())

def main():
    items = Knead(PATH + "/data/reliwiki/rmm.csv").data()
    skiplist = Skiplist("projects/skiplists/reliwiki-rmm.txt")

    for index, item in enumerate(items):
        print(item)
        qid = item["qid"]
        reliwiki = item["pageid"]
        print()
        print(f"#{index} / #{len(items)}")
        print(f"Handling {qid} / {reliwiki}")

        if skiplist.has(qid):
            print(f"{qid} in skiplist, skipping")
            continue

        wd_item = WikidataItem(qid)
        claims = wd_item.get_claims()

        if Props.RELIWIKI in claims:
            print("This item already has a Reliwiki ID, skipping")
            continue

        wd_item.add_string_claim(
            Props.RELIWIKI,
            reliwiki,
            references = [
                wd_item.get_item_claim(Props.INFERRED_FROM, Items.RIJKSMONUMENT_ID)
            ]
        )

        skiplist.add(qid)
        sys.exit()

if __name__ == "__main__":
    main()