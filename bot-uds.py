from dataknead import Knead
from pathlib import Path
from util.skiplist import Skiplist
from util.wikidata import Props, Items, WikidataItem
import pywikibot

PATH = str(Path(__file__).parent.resolve())

def main():
    items = Knead(PATH + "/data/uds/monuments-with-qids.csv").data()
    skiplist = Skiplist("projects/skiplists/uds.txt")

    for index, item in enumerate(items):
        print(item)
        qid = item["qid"]
        bag = item["bag_ok"]
        url = item["url"]
        print()
        print(f"#{index} / #{len(items)}")
        print(f"Handling {qid} / {bag} / {url}")

        if skiplist.has(qid):
            print(f"{qid} in skiplist, skipping")
            continue

        wd_item = WikidataItem(qid)
        claims = wd_item.get_claims()

        if Props.BAG_BUILDING in claims:
            print("This item already has a BAG building ID, skipping")
            continue

        wd_item.add_string_claim(
            Props.BAG_BUILDING,
            bag,
            references = [
                wd_item.get_item_claim(Props.STATED_IN, Items.UDS_DOC),
                wd_item.get_url_claim(Props.REF_URL, url),
                wd_item.get_item_claim(Props.LANGUAGE_WORK, Items.DUTCH)
            ]
        )

        skiplist.add(qid)

if __name__ == "__main__":
    main()