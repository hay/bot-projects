from dataknead import Knead
from pathlib import Path
from pywikibot import WbTime
from util.bot import Bot
from util.wikidata import Props, Items, WikidataItem
import sys

PATH = str(Path(__file__).parent.resolve())
coords = Knead(f"{PATH}/data/plantages/plantages.geojson", read_as = "json").data()
ids = Knead(f"{PATH}/data/plantages/ids.csv").data()

def get_refs(item, pid):
    url = f"https://pointer.kro-ncrv.nl/het-slavernijverleden-van-suriname-op-de-kaart-gezet#/plantage/{pid}"

    return [
        item.get_url_claim(Props.REF_URL, url),
        item.get_claim(Props.RETRIEVED, WbTime(
            year = 2021, month = 2, day = 20
        )),
        item.get_item_claim(Props.LANGUAGE_WORK, Items.DUTCH)
    ]

def get_plantage(pid):
    for row in ids:
        if int(pid) == int(row["id"]):
            return row

    return None

def parse():
    for feature in coords["features"]:
        pid = feature["properties"]["id"]
        coord = feature["geometry"]["coordinates"]
        coord.reverse()
        plantage = get_plantage(pid)
        qid = plantage["qid"]
        name = plantage["name"]

        if not qid:
            continue

        print()
        print("---" * 20)
        print(pid, coord, name, qid)

        item = WikidataItem(qid)
        claims = item.get_claims()

        if Props.COORDINATES in claims:
            print("Already has coordinates, skipping!")
            continue

        item.add_coordinate(
            Props.COORDINATES, coord, references = get_refs(item, pid)
        )

if __name__ == "__main__":
    parse()