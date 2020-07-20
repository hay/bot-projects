from dataknead import Knead
from pathlib import Path
from pywikibot import WbTime
# from wikidata_utils import PATH, site, wbtime_now, Skiplist
from util.skiplist import Skiplist
from util.wikidata import Props, Items, WikidataItem
from util.wikipedia import get_permalink
import pywikibot
import requests
import sys

def convert_year(year):
    ytype = year["type"]
    val = int(year["value"])

    if year["type"] == "decade":
        return WbTime(year = val, precision = "decade")
    elif year["type"] == "century":
        return WbTime(year = val, precision = "century")
    else:
        return WbTime(year = val)

def set_restored_claim(item, years, ref):
    print(f"Got {len(years)} year(s) claim for restoration")

    for year in years:
        print(f"Adding year: {year}")

        if year["type"] == "range":
            qualifiers = [
                wd_item.get_claim(Props.START_TIME, convert_year(year["value"][0])),
                wd_item.get_claim(Props.END_TIME, convert_year(year["value"][1]))
            ]
        elif year["type"] in ["century", "decade", "year"]:
            qualifiers = [
                wd_item.get_claim(Props.POINT_IN_TIME, convert_year(year["value"]))
            ]
        else:
            print("Invalid year type: " + year["type"])
            continue

        wd_item.add_item_claim(
            Props.SIG_EVENT,
            Items.RECONSTRUCTION,
            qualifiers = qualifiers,
            references = ref
        )

def set_year_claim(item, prop, years, ref):
    print(f"Got {len(years)} year(s) claim for {prop}")

    for year in years:
        print(f"Adding year: {year}")

        if year["type"] == "range":
            wd_item.add_time_claim(
                prop,
                "novalue",
                qualifiers = [
                    wd_item.get_claim(Props.START_TIME, convert_year(year["value"][0])),
                    wd_item.get_claim(Props.END_TIME, convert_year(year["value"][1]))
                ],
                references = ref
            )
        elif year["type"] in ["century", "decade"]:
            wd_item.add_time_claim(
                prop,
                convert_year(year["value"]),
                qualifiers = [
                    wd_item.get_claim(Props.START_TIME, convert_year(year["start"])),
                    wd_item.get_claim(Props.END_TIME, convert_year(year["end"]))
                ],
                references = ref
            )
        elif year["type"] == "circa":
            wd_item.add_time_claim(
                prop,
                convert_year(year["value"]),
                qualifiers = [
                    wd_item.get_item_claim(Props.PRECISION, Items.CIRCA)
                ],
                references = ref
            )
        elif year["type"] == "year":
            wd_item.add_time_claim(
                prop,
                convert_year(year["value"]),
                references = ref
            )
        else:
            print("Invalid year type: " + year["type"])
            continue

def main():
    items = Knead("projects/data/churches/churches.json").data()
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

        def reflink():
            return [
                wd_item.get_item_claim(Props.IMPORTED_FROM, Items.WIKIPEDIA_NL),
                wd_item.get_url_claim(Props.WM_IMPORT_URL, permalink)
            ]

        if item["inception"] and Props.INCEPTION not in claims:
            set_year_claim(wd_item, Props.INCEPTION, item["inception"], reflink())

        if item["demolished"] and Props.DISSOLVED not in claims:
            set_year_claim(wd_item, Props.DISSOLVED, item["demolished"], reflink())

        if item["restored"] and Props.SIG_EVENT not in claims:
            set_restored_claim(wd_item, item["restored"], reflink())

        skiplist.add(qid)
        break

if __name__ == "__main__":
    main()