#!/usr/bin/env python3
from bs4 import BeautifulSoup
from dataknead import Knead
from geopy.distance import distance as geodistance
from multiprocessing.dummy import Pool
from pathlib import Path
from time import sleep
from util.geo import find_shortest_distance, ShapeFinder
from util.mediawiki import AllPages, MediawikiApi
from util.utils import dd, Datasheet
import json
import random
import re
import requests
import sys

API_ENDPOINT = "http://reliwiki.nl/api.php"
RMM_ID = re.compile("https://monumentenregister.cultureelerfgoed.nl/monumenten/(\d{1,6})")
TITLE = re.compile("([^,]+),([^-–]+)[-|–](.+)")

def check_coordinates():
    # Go over all Reliwiki items with coordinates, check the gemeente
    # and then write back to a new file
    finder = ShapeFinder("./data/gemeentes-nl-2019/gemeentes-nl-2019.shp")

    def find_gemeente(item):
        lat, lon = item["coordinates"].split(",")

        coord = finder.find_coordinate(float(lat), float(lon))
        item["coord_matched"] = coord != None

        if coord:
            item["matched_code"] = coord["properties"]["Gemeenteco"]
            item["matched_label"] = coord["properties"]["Gemeentena"]

        return item

    in_path = "data/reliwiki/reliwiki-with-coordinates.csv"
    out_path = "data/reliwiki/reliwiki-with-coordinates-gemeentes.csv"
    Knead(in_path).map(find_gemeente).write(out_path)

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

def match_sitelinks():
    api = MediawikiApi("wikipedia", "nl")
    extlinks = Datasheet("data/reliwiki/extlinks.csv", "sitelink")

    for item in Knead("data/reliwiki/sitelinks.csv").data():
        qid = item["item"]
        sitelink = item["sitelink"]

        if sitelink == "":
            continue

        if extlinks[sitelink]:
            print(f"<{sitelink}> exists, skipping")
            continue

        print()
        print(f"Parsing {sitelink}")

        article = sitelink.replace("https://nl.wikipedia.org/wiki/", "")

        links = api.call({
            "action" : "query",
            "prop" : "extlinks",
            "ellimit" : 500,
            "titles" : article
        })

        pages = links["query"]["pages"]

        if "-1" in pages:
            print("Could not find title")
            continue

        # Get the first hit and loop through all extlinks
        page = pages[list(pages.keys())[0]]

        found_link = False

        if "extlinks" in page:
            for link in page["extlinks"]:
                link_url = link["*"]

                if "reliwiki" in link_url:
                    print("Found reliwiki")

                    extlinks.append({
                        "pageid" : page["pageid"],
                        "title" : page["title"],
                        "sitelink" : sitelink,
                        "ext_url" : link_url
                    })

                    found_link = True
                else:
                    print(f"No reliwiki...: {link_url}")
        else:
            print("No external links!")

        if not found_link:
            extlinks.append({
                "sitelink" : sitelink
            })

        sleep(1)

def get_exturls():
    # Nice approach, but this doesn't return web.archive.org urls :(
    api = MediawikiApi("wikipedia", "nl")

    iterator = api.iterate_list("exturlusage", "eucontinue", {
        "action" : "query",
        "list" : "exturlusage",
        "euquery" : "reliwiki.nl",
        "eunamespace" : "0",
        "eulimit" : "500"
    })

    urls = []

    for page in iterator:
        print(page)
        urls.append(page)

    Knead(urls).write("data/reliwiki/exturls.csv")

def get_pagenames():
    items = []
    RE_PAGENAME = re.compile("wgPageName\":\"([^\"]+)")

    for path in Path("data/reliwiki/html").glob("*.html"):
        print(path)

        f = open(path)

        for line in f:
            if "wgPageName" in line:
                matches = RE_PAGENAME.findall(line)

                if matches:
                    items.append({
                        "pageid" : path.stem,
                        "pagename" : matches[0]
                    })

                break

        f.close()

    Knead(items).write("data/reliwiki/extlinks-reliwiki.csv")

def match_coordinates():
    RE_POINT = re.compile("\(([^ ]+) ([^ ]+)\)")

    def parse_reliwiki(item):
        if "coordinates" in item and item["coordinates"] != "":
            lat, lon = item["coordinates"].split(",")
            item["location"] = (lat, lon)
        else:
            item["location"] = None

        item["label"] = f"{item['name']} ({item['place']}, {item['address']})"

        return item

    def parse_wikidata(item):
        if "coord" in item and item["coord"] != "":
            lon, lat = RE_POINT.findall(item["coord"])[0]
            item["location"] = (lat, lon)
        else:
            item["location"] = None

        location_label = item["locationLabel"] + ", " + item["adminLabel"]
        item["label"] = f"{item['itemLabel']} ({location_label})"

        return item

    reliwiki = Knead("data/reliwiki/reliwiki-with-coordinates.csv").map(parse_reliwiki).data()
    reliwiki_coords = [ i["location"] for i in reliwiki ]
    wikidata = Knead("data/reliwiki/wd-with-coordinates.csv", has_header = True).map(parse_wikidata).data()

    matches = []

    # Loop through all Wikidata items, and extract coordinates
    for nr, w_item in enumerate(wikidata):
        print(f"Parsing {w_item['label']}")

        try:
            index, distance = find_shortest_distance(
                w_item["location"],
                reliwiki_coords,
                rough = True
            )
        except Exception as e:
            print(f"Woops: {e}")
            continue

        r_item = reliwiki[index]

        print(f"The best candidate ({distance}) for this item is: ", r_item)

        matches.append({
            "qid" : w_item["item"],
            "reliwiki_id" : r_item["pageid"],
            "wd_label" : w_item["label"],
            "reliwiki_label" : r_item["label"],
            "distance" : distance
        })

    Knead(matches).write("data/reliwiki/coordinates-matched.csv", fieldnames = [
        "qid", "reliwiki_id", "wd_label", "reliwiki_label", "distance"
    ])

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

globals()[sys.argv[1]]()