from bs4 import BeautifulSoup
from dataknead import Knead
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

def parse_page(path):
    print(f"Parsing {path}")

    with open(path) as f:
        soup = BeautifulSoup(f.read(), "lxml")

    # I guess the first table in mw-content-text is always the infobox
    table = soup.select_one("#mw-content-text table")
    infobox = {
        "coordinates" : None,
        "pageid" : Path(path).stem,
        "rijksmonument" : []
    }

    for tr in table.select('tr[valign="top"]'):
        td = tr.select("td")
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

    for path in Path("data/reliwiki/html").glob("*.html"):
        data = parse_page(path)
        churches.append(data)

    Knead(churches).write("data/reliwiki/churches_data.csv")

def scrape_pages():
    churches = []
    api = AllPages(API_ENDPOINT)

    for page in api.iterate_pages():
        print(page["title"])
        churches.append(page)

    Knead(churches).write("data/reliwiki/pages.json")

process_pages();