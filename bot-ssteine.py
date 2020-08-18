from dataknead import Knead
from pathlib import Path
from util.dates import partial_date_to_wbtime
from util.wikidata import Props, Items, WikidataItem
import pywikibot
import sys

def add_item(data):
    name = data["name"]
    location = data["location"]

    desc = {
        "label_en" : f"Stolperstein dedicated to {name}",
        "label_nl" : f"Stolperstein ter herinnering aan {name}",
        "description_en" : f"stumbling stone in {location}, the Netherlands",
        "description_nl" : f"struikelsteen in {location}",
        "aliases_nl" : [
            f"struikelsteen ter herinnering aan {name}",
        ]
    }

    print(desc)

    item = WikidataItem(
        summary = f"Creating new item for a Stolperstein for {name}",
        labels = {
            "en" : desc["label_en"],
            "nl" : desc["label_nl"]
        },
        descriptions = {
            "en" : desc["description_en"],
            "nl" : desc["description_nl"]
        },
        aliases = {
            "nl" : desc["aliases_nl"]
        }
    )

    # These are the same for all stolpersteine
    item.add_item_claim(Props.INSTANCE_OF, Items.STOLPERSTEIN)
    item.add_item_claim(Props.PART_OF, Items. STOLPERSTEINE_PROJECT)
    item.add_item_claim(Props.COUNTRY, Items.NETHERLANDS)
    item.add_item_claim(Props.CREATOR, Items.GUNTER_DEMNIG)
    item.add_item_claim(Props.MATERIAL_USED, Items.BRASS)

    # These are not
    item.add_commonsmedia(Props.IMAGE, data["image"])
    item.add_item_claim(Props.LOCATED_IN, data["location_qid"])
    item.add_coordinate(Props.COORDINATES, [data["lat"], data["lon"]])
    item.add_monoling_claim(Props.INSCRIPTION, data["inscription"], "nl")

    # Inception and opening
    date = partial_date_to_wbtime(data["inception"])
    item.add_time_claim(Props.INCEPTION, date)
    item.add_item_claim(Props.SIG_EVENT, Items.OPENING_CEREMONY,
        qualifiers = [
            item.get_claim(Props.POINT_IN_TIME, date)
        ]
    )

    # Street as item
    item.add_item_claim(Props.LOCATED_ON_STREET, data["street_qid"],
        qualifiers = [
            item.get_string_claim(Props.STREET_NUMBER, data["street_nr"])
        ]
    )

    # Street as address
    address = data["street"] + " " + data["street_nr"] + ", " + data["location"]
    item.add_monoling_claim(Props.STREET_ADDRESS, address, "nl")

    item.add_item_claim(Props.COMMEMORATES, "somevalue",
        qualifiers = [
            item.get_monoling_claim(Props.NAME, name, "nl")
        ]
    )

def main():
    PATH = str(Path(__file__).parent)
    items = Knead(PATH + "/data/stolpersteine/doesburg-images-parsed.csv").data()

    for item in items:
        add_item(item)
        # sys.exit()

if __name__ == "__main__":
    main()