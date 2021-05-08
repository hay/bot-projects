#!/usr/bin/env python3
from bs4 import BeautifulSoup
from dataknead import Knead
from pathlib import Path
import requests
import sys

BASE = "data/kos-nijmegen"
BASE_URL = "https://www.nijmegen.nl/kos/kunstwerk.aspx?id="

def dedupe():
    dupes = []

    def parse(item):
        title = item["title"]

        if title not in dupes:
            dupes.append(title)
            return item
        else:
            if item["location_clean"] == "":
                raise Exception(item, "NO location!")

            location = item["location_clean"]
            new_title = f"{title} ({location})"
            item["title"] = new_title
            print(new_title)
            return item

    Knead(f"{BASE}/kos-parsed.csv").map(parse).write(f"{BASE}/kos-parsed-deduped.csv")

def parse():
    data = []

    for path in Path(f"{BASE}/html/").glob("*.html"):
        print(f"Parsing {path}")
        kid = path.stem

        with open(path) as f:
            soup = BeautifulSoup(f, "lxml")

        year_el = soup.select_one('a[href^="jaartal"]')

        if not year_el:
            year = None
        else:
            year = year_el.get_text()
            print(year)

        # Get ownership
        owner = None

        for label in  soup.select(".lbl"):
            if label.get_text() == "eigendom van:":
                owner = label.parent.select_one(".val").get_text()

        data.append({
            "id" : kid,
            "year" : year,
            "owner" : owner
        })

    Knead(data).write(f"{BASE}/scraped-data.csv")

def scrape():
    for item in Knead(BASE + "/kos-parsed.csv").data():
        kid = item["id"]
        path = Path(f"{BASE}/html/{kid}.html")

        if path.is_file():
            print(f"Exists skipping: {path}")
            continue

        url = BASE_URL + kid
        req = requests.get(url)

        with open(path, "w") as f:
            f.write(req.text)
            print(f"Wrote {path}")

def transform():
    def parse(item):
        d = item["properties"]

        return {
            "title" : d["KunstwerkN"],
            "creator" : d["Kunstenaar"],
            "location" : d["LokatieBee"],
            "lat" : d["Breedtegra"].replace(",", "."),
            "lon" : d["Lengtegraa"].replace(",", "."),
            "id" : d["KunstwerkI"],
            "url" : d["Websitever"]
        }

    k = Knead("data/kos-nijmegen/kos.json").apply(lambda f:f["features"]).map(parse)
    k.write("data/kos-nijmegen/kos-parsed.csv", fieldnames = [
        "id", "title", "creator", "location", "lat", "lon", "url"
    ])

def wptable():
    items = Knead("data/kos-nijmegen/wd-query.csv", has_header = True).data()

    def parse(row):
        street = row["Straat"]

        hits = []

        for item in items:
            if street == item["street"]:
                hits.append(item)

        if len(hits) == 1:
            print(hits)
            row["match"] = 1
            row.update(hits[0])
        else:
            row["match"] = 0

        return row

    Knead(f"{BASE}/wp-beelden.csv", has_header = True).map(parse).write(f"{BASE}/wp-beelden-matched.csv")

def wptable2():
    def parse(item):
        wd = item["itemLabel"].strip()
        kos = item["Omschrijving"].strip()

        if wd.lower() != kos.lower():
            print(wd, " - ", kos)
            item["alias"] = item["Omschrijving"][0].upper() + item["Omschrijving"][1:]

        return item

    Knead(f"{BASE}/wp-beelden-matched.csv", has_header = True).map(parse).write(f"{BASE}/wp-beelden-matched2.csv")

globals()[sys.argv[1]]()