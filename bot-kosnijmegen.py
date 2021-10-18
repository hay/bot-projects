from dataknead import Knead
from pathlib import Path
from pywikibot import WbTime
from util.skiplist import Skiplist
from util.wikidata import WikidataItem, Props, Items
from util.dates import wbtime_now
import pywikibot
import sys

PATH = str(Path(__file__).parent.resolve())
skiplist = Skiplist(PATH + "/skiplists/kos-nijmegen.txt")
WP_PERMALINK = "https://nl.wikipedia.org/w/index.php?title=Lijst_van_beelden_in_Nijmegen&oldid=58187301"

def get_refs(item, url):
    return [
        item.get_item_claim(Props.STATED_IN, Items.PUBLIC_ART_IN_NIJMEGEN),
        item.get_url_claim(Props.REF_URL, url),
        item.get_claim(Props.RETRIEVED, WbTime(
            year = 2021, month = 1, day = 31
        )),
        item.get_item_claim(Props.LANGUAGE_WORK, Items.DUTCH)
    ]

def add_image_alias(item):
    qid = item["item"]
    img = item["Afbeelding"]
    alias = item["alias"]

    item = WikidataItem(qid)
    claims = item.get_claims()
    aliases = item.get_aliases("nl")

    if img != "" and Props.IMAGE not in claims:
        item.add_commonsmedia(
            Props.IMAGE, img,
            references = [
                item.get_item_claim(Props.IMPORTED_FROM, Items.WIKIPEDIA_NL),
                item.get_url_claim(Props.WM_IMPORT_URL, WP_PERMALINK)
            ]
        )
    else:
        print("has an image already")

    if (alias != "") and (not aliases):
        print(f"Setting alias: {alias}")
        item.edit_aliases({
            "nl" : [ alias ]
        })
    else:
        print("Already has aliases")

    # sys.exit()

def add_inventory(item):
    qid = item["item"]
    url = item["url"]

    if "https://www.nijmegen.nl/kos/kunstwerk" not in url:
        return

    kid = url.replace("https://www.nijmegen.nl/kos/kunstwerk.aspx?id=", "")

    item = WikidataItem(qid)

    if Props.INVENTORY_NR in item.get_claims():
        print("has inventory!")
        return

    item.add_string_claim(
        Props.INVENTORY_NR, kid,
        qualifiers = [
            item.get_item_claim(Props.COLLECTION, Items.PUBLIC_ART_IN_NIJMEGEN)
        ],
        references = get_refs(item, url)
    )

def add_item(data):
    print("----" * 20)
    print()
    print(data)

    title = data["title"]
    url = data["url"]
    kid = data["id"]

    # if kid != "50":
    #     return

    print(f"Handling {title}")

    if skiplist.has(kid):
        print(f"In skiplist, skipping")
        return

    creator = data["creator"]

    if creator == "":
        desc_nl = "kunstwerk in de openbare ruimte te Nijmegen"
        desc_en = "public artwork in Nijmegen, the Netherlands"
    elif creator == "Onbekend":
        desc_nl = "kunstwerk in de openbare ruimte van een onbekende maker te Nijmegen"
        desc_en = "public artwork by an unknown artist in Nijmegen, the Netherlands"
    else:
        desc_nl = f"kunstwerk van {creator} in de openbare ruimte te Nijmegen"
        desc_en = f"public artwork by {creator} in Nijmegen, the Netherlands"

    item = WikidataItem(
        summary = f"public artwork '{title}' in Nijmegen, the Netherlands",
        labels = {
            "nl" : title
        }
    )

    item.edit_descriptions({
            "de" : f"Kunst im öffentlichen Raum in Nijmegen (Niederlande)",
            "en" : desc_en,
            "es" : f"arte público en Nijmegen (Holanda)",
            "fr" : f"art public à Nimègue (Pays-Bas)",
            "nl" : desc_nl
    })

    item.edit_aliases({
        "en" : title
    })

    # Basics
    item.add_item_claim(Props.INSTANCE_OF, Items.SCULPTURE)
    item.add_item_claim(Props.COUNTRY, Items.NETHERLANDS)
    item.add_item_claim(Props.LOCATED_IN_ADMIN, Items.NIJMEGEN_MUNIP)
    item.add_item_claim(Props.GENRE, Items.PUBLIC_ART)


    # Actual data
    coord = [data["lat"], data["lon"]]
    item.add_coordinate(
        Props.COORDINATES, coord, references = get_refs(item, url)
    )

    item.add_string_claim(
        Props.INVENTORY_NR, kid,
        qualifiers = [
            item.get_item_claim(Props.COLLECTION, Items.PUBLIC_ART_IN_NIJMEGEN)
        ],
        references = get_refs(item, url)
    )

    item.add_string_claim(
        Props.DESCRIBED_AT_URL,
        url,
        qualifiers = [
            item.get_item_claim(Props.LANGUAGE_WORK, Items.DUTCH)
        ]
    )

    if data["year"] != "":
        year = int(data["year"])
        item.add_time_claim(
            Props.INCEPTION, WbTime(year = year), references = get_refs(item, url)
        )

    if data["creator_qid"] != "":
        item.add_item_claim(
            Props.CREATOR, data["creator_qid"], references = get_refs(item, url)
        )
    elif data["creator"] == "Onbekend":
        item.add_item_claim(
            Props.CREATOR, "somevalue", references = get_refs(item, url)
        )

    if data["owner"] == "gemeente":
        item.add_item_claim(
            Props.COLLECTION, Items.NIJMEGEN_MUNIP, references = get_refs(item, url)
        )
    elif data["owner"] == "particulier":
        item.add_item_claim(
            Props.COLLECTION, Items.PRIVATE_COLLECTION, references = get_refs(item, url)
        )

    if data["location_clean"] != "":
        item.add_monoling_claim(
            Props.STREET_ADDRESS, data["location_clean"], "nl", references = get_refs(item, url)
        )

    skiplist.add(kid)
    # sys.exit()

if __name__ == "__main__":

    data = Knead(f"{PATH}/data/kos-nijmegen/wp-beelden-matched2.csv", has_header = True).data()
    for item in data:
        try:
            add_image_alias(item)
        except:
            print(f"Went wrong!")