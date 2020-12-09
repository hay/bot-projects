#!/usr/bin/env python3
from bs4 import BeautifulSoup
from dataknead import Knead
from multiprocessing.dummy import Pool
from pathlib import Path
from time import sleep
from util.mediawiki import AllPages
from util.utils import dd
import json
import re
import requests
import sys

API_ENDPOINT = "http://reliwiki.nl/api.php"
RMM_ID = re.compile("https://monumentenregister.cultureelerfgoed.nl/monumenten/(\d{1,6})")
TITLE = re.compile("([^,]+),([^-–]+)[-|–](.+)")

def cleanup_churches():
    class Item:
        def __init__(self, item):
            self.item = item

        def get(self, keys):
            for key in keys:
                if key in self.item:
                    return self.item[key]

            return None

        def __getitem__(self, attr):
            if attr in self.item:
                return self.item[attr]

            # Two common typos are having a space before the colon and the first
            # letter not being capitalized, so accomodate for those instances
            options = [
                attr.replace(" :", ":"),
                attr.lower()
            ];

            for key in options:
                if key in self.item:
                    return self.item[key]

            return None

    def cleanup(church):
        item = Item(church)

        return {
            "pageid" : item["pageid"],
            "gemeente" : item["Gemeente:"],
            "name" : item["Naam kerk:"],
            "objectname" : item["Naam object:"],
            "zipcode" : item["Postcode:"],
            "sonneveld" : item.get([
                "Inventarisatienummer:", "ID nummer:", "Inventarisnr.:", "Sonneveld ID:",
                "Inventarisatienummer :"
            ]),
            "use" : item["Huidige bestemming:"],
            "denomination" : item["Genootschap:"],
            "rijksmonument" : item["rijksmonument"],
            "coordinates" : item["coordinates"],
            "address" : item["Adres:"],
            "architect" : item["Architect:"],
            "place" : item["Plaats:"],
            "year_use" : item.get(["Jaar ingebruikname:", "Bouwja(a)r(en):"]),
            "original_use" : item["Oorspronkelijke bestemming:"],
            "monument" : item["Monument status:"]
        }

    return Knead("data/reliwiki/churches_data.json").map(cleanup).write("data/reliwiki/churches_clean.csv")

def create_catalog():
    catalog = open("data/reliwiki/catalog.tsv", "w")

    for church in Knead("data/reliwiki/churches.csv").data():
        pageid = church["pageid"]
        place = church["place"]
        address = church["address"]
        name = church["name"]
        description = f"religious building located at {address} in {place}, the Netherlands"

        if name == "":
            print(church)
            sys.exit()

        line = f"{pageid}\t{name}\t{description}\t\n"
        catalog.write(line)

    catalog.close()

def fetch_pages():
    churches = []

    def get_path(pageid):
        return f"data/reliwiki/html/{pageid}.html"

    for church in Knead("data/reliwiki/pages.json").data():
        pageid = church["pageid"]
        path = get_path(pageid)

        if Path(path).exists():
            print(f"{path} exists, skipping")
            continue

        url = f"http://reliwiki.nl/?curid={pageid}"
        print(f"Getting {url}")
        req = requests.get(url)

        with open(path, "w") as f:
            f.write(req.text)
            print(f"Saved {path}")

        print("Sleep for 3 second")
        sleep(3)

def iter_html():
    for p in Path("data/reliwiki/html").glob("*.html"):
        yield {
            "id" : p.stem,
            "path" : str(p)
        }

def process_dupes():
    items = {}
    qids = []
    dupes = []

    # First dedupe by QID
    for item in Knead("data/reliwiki/query.csv").data():
        if item["item"] not in qids:
            reliwiki = item["reliwiki"]

            if reliwiki not in items:
                items[reliwiki] = [ item ]
            else:
                items[reliwiki].append(item)

            qids.append(item["item"])

    for values in items.values():
        if len(values) > 1:
            dupes = dupes + values

    Knead(dupes).write("data/reliwiki/dupes.csv", fieldnames = [
        "item", "reliwiki", "itemLabel", "itemDescription", "instanceLabel", "instance"
    ])

def parse_page(path):
    print(f"Parsing {path}")
    json_path = Path(path).with_suffix(".json")

    if json_path.exists():
        print(f"Got JSON file, returning that: {json_path}")
        return Knead(str(json_path)).data()

    with open(path) as f:
        soup = BeautifulSoup(f.read(), "lxml")

    # I guess the first table in mw-content-text is always the infobox
    table = soup.select_one("#mw-content-text table")

    if not table:
        print("Could not find table")
        return None

    infobox = {
        "coordinates" : None,
        "pageid" : Path(path).stem,
        "rijksmonument" : []
    }

    for tr in table.select('tr[valign="top"]'):
        td = tr.select("td")

        if len(td) < 2:
            continue

        key = td[0].get_text().strip()
        val = td[1].get_text().strip()
        infobox[key] = val

    # Extract external references
    for a in table.select("a"):
        href = a.get("href")

        if RMM_ID.match(href):
            matches = RMM_ID.findall(href)
            infobox["rijksmonument"].append(matches[0])

    # Extract geocoordinates
    el_mapdata = soup.select_one("#map_leaflet_1 .mapdata")

    if el_mapdata:
        mapdata = json.loads(el_mapdata.get_text())

        if "locations" in mapdata and len(mapdata["locations"]) > 0:
            loc = mapdata["locations"][0]
            infobox["coordinates"] = f"{loc['lat']},{loc['lon']}"

    infobox["rijksmonument"] = ",".join(infobox["rijksmonument"])

    Knead(infobox).write(json_path)
    print(f"Written {json_path}")

    return infobox

def parse_pages():
    churches = []

    for church in Knead("data/reliwiki/pages.json").data():
        title = church["title"]
        pageid = church["pageid"]
        title_parts = TITLE.findall(title)

        if not title_parts:
            continue

        parts = title_parts[0]

        churches.append({
            "pageid" : church["pageid"],
            "pagetitle" : title,
            "place" : parts[0].strip(),
            "address" : parts[1].strip(),
            "name" : parts[2].strip()
        })

    Knead(churches).write(
        "data/reliwiki/churches.csv",
        fieldnames = ["pageid", "name", "address", "place", "pagetitle"]
    )

def process_pages():
    churches = []
    for path in Path("data/reliwiki/html/").glob("*.html"):
        data = parse_page(path)

        if data:
            churches.append(data)

    Knead(churches).write("data/reliwiki/churches_data.json")

def process_rmm():
    items = []
    qids = {i["rmm"]:i["item"] for i in Knead("data/reliwiki/rmm-all.csv").data()}

    for path in iter_html():
        with open(path["path"]) as f:
            matches = list(set(RMM_ID.findall(f.read())))

        if len(matches) == 0:
            continue

        for rmm in matches:
            if rmm not in qids:
                print(f"No QID for pageid {path['id']} (RMM {rmm})")
                continue

            items.append({
                "pageid" : path["id"],
                "rmm" : rmm,
                "qid" : qids.get(rmm, None)
            })

    Knead(items).write(
        "data/reliwiki/rmm.csv",
        fieldnames = ["pageid", "rmm", "qid"]
    )

def scrape_pages():
    churches = []
    api = AllPages(API_ENDPOINT)

    for page in api.iterate_pages():
        print(page["title"])
        churches.append(page)

    Knead(churches).write("data/reliwiki/pages.json")

def test():
    print("test")

if sys.argv[1] in globals():
    globals()[sys.argv[1]]()