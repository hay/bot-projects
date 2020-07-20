from dataknead import Knead
from pathlib import Path
from pywikibot import WbTime
from util.skiplist import Skiplist
from util.wikidata import Props, Items, WikidataItem
from util.wikipedia import get_permalink
import pywikibot
import requests
import sys

def get_ref(item, permalink):
    return [
        item.get_item_claim(Props.IMPORTED_FROM, Items.WIKIPEDIA_NL),
        item.get_url_claim(Props.WM_IMPORT_URL, permalink)
    ]

def convert_year(year):
    ytype = year["type"]
    val = int(year["value"])

    if year["type"] == "decade":
        return WbTime(year = val, precision = "decade")
    elif year["type"] == "century":
        return WbTime(year = val, precision = "century")
    else:
        return WbTime(year = val)

def set_sig_claim(item, qid, years, permalink):
    print(f"Got {len(years)} year(s) claim for restoration")

    for year in years:
        print(f"Adding year: {year}")

        if year["type"] == "range":
            qualifiers = [
                item.get_claim(Props.START_TIME, WbTime(year = int(year["value"][0]))),
                item.get_claim(Props.END_TIME, WbTime(year = int(year["value"][1])))
            ]
        elif year["type"] in ["century", "decade", "year"]:
            qualifiers = [
                item.get_claim(Props.POINT_IN_TIME, convert_year(year))
            ]

            if all(["start" in year, "end" in year]):
                qualifiers.extend([
                    item.get_claim(Props.START_TIME, WbTime(year = int(year["start"]))),
                    item.get_claim(Props.END_TIME, WbTime(year = int(year["end"])))
                ])
        else:
            print("Invalid year type: " + year["type"])
            continue

        item.add_item_claim(
            Props.SIG_EVENT,
            qid,
            qualifiers = qualifiers,
            references = get_ref(item, permalink)
        )

def set_year_claim(item, prop, years, permalink):
    print(f"Got {len(years)} year(s) claim for {prop}")

    for year in years:
        print(f"Adding year: {year}")

        if year["type"] == "range":
            item.add_time_claim(
                prop,
                "novalue",
                qualifiers = [
                    item.get_claim(Props.START_TIME, WbTime(year = int(year["value"][0]))),
                    item.get_claim(Props.END_TIME, WbTime(year = int(year["value"][1])))
                ],
                references = get_ref(item, permalink)
            )
        elif year["type"] in ["century", "decade"]:
            item.add_time_claim(
                prop,
                convert_year(year),
                qualifiers = [
                    item.get_claim(Props.START_TIME, WbTime(year = int(year["start"]))),
                    item.get_claim(Props.END_TIME, WbTime(year = int(year["end"])))
                ],
                references = get_ref(item, permalink)
            )
        elif year["type"] == "circa":
            item.add_time_claim(
                prop,
                convert_year(year),
                qualifiers = [
                    item.get_item_claim(Props.PRECISION, Items.CIRCA)
                ],
                references = get_ref(item, permalink)
            )
        elif year["type"] == "year":
            item.add_time_claim(
                prop,
                convert_year(year),
                references = get_ref(item, permalink)
            )
        else:
            print("Invalid year type: " + year["type"])
            continue

def main():
    items = Knead("projects/data/churches/import.json").data()
    skiplist = Skiplist("projects/skiplists/churches.txt")

    for index, item in enumerate(items):
        qid = item["qid"]
        title = item["title"]
        print()
        print(f"#{index} / #{len(items)}")
        print(f"Handling {qid} / {title}")

        if not any([
            item["inception"], item["demolished"], item["restored"]
        ]):
            print("No inception, demolished, restored, skipping")
            continue

        print(item)

        if skiplist.has(qid):
            print(f"{qid} in skiplist, skipping")
            continue

        wd_item = WikidataItem(qid)
        claims = wd_item.get_claims()
        permalink = get_permalink("nl", title)

        if item["inception"] and Props.INCEPTION not in claims:
            set_year_claim(wd_item, Props.INCEPTION, item["inception"], permalink)

        if item["demolished"] and Props.DISSOLVED not in claims:
            set_year_claim(wd_item, Props.DISSOLVED, item["demolished"], permalink)

        if item["restored"] and Props.SIG_EVENT not in claims:
            set_sig_claim(wd_item, Items.RECONSTRUCTION, item["restored"], permalink)

        if item["expanded"] and Props.SIG_EVENT not in claims:
            set_sig_claim(wd_item, Items.BUILDING_EXPANSION, item["expanded"], permalink)

        skiplist.add(qid)
        break

if __name__ == "__main__":
    main()