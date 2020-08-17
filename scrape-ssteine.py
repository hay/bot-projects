#!/usr/bin/env python3.6
from bs4 import BeautifulSoup
from dataknead import Knead
from pathlib import Path
from util.utils import parse_urlargs
import requests
import sys

def get_pages(csv_path):
    stem = Path(csv_path).stem
    html_path = Path(".") / "data/stolpersteine/" / stem
    print("Saving to: " + str(html_path))

    html_path.mkdir(exist_ok = True)

    for item in Knead(csv_path).data():
        pid = item["pageid"]
        url = f"https://commons.wikimedia.org/wiki/?curid={pid}"
        req = requests.get(url)
        pid_path = html_path / f"{pid}.html"

        with open(pid_path, "w") as f:
            f.write(req.text)

def parse_pages(html_path):
    items = []

    for path in Path(html_path).glob("*.html"):
        print()
        print(path)

        with open(path) as f:
            soup = BeautifulSoup(f.read(), "lxml")

        url = soup.select_one('[rel="canonical"]').get("href")
        description = soup.select_one('.commons-file-information-table .description[lang="nl"]')
        description = description.get_text().replace("Nederlands: ", "").strip()
        geolink = soup.select_one('[href*="commons-on-osm"]').get("href")
        geolink = parse_urlargs(geolink)

        items.append({
            "url" : url,
            "title" : url.replace("https://commons.wikimedia.org/wiki/", ""),
            "inscription" : description,
            "lat" : geolink["lat"],
            "lon" : geolink["lon"],
            "munip" : None,
            "inception" : None,
            "street" : None,
            "street_nr" : None,
            "url" : None
        })

    filename = Path(html_path).stem + "-parsed.csv"
    out_path = str(Path(html_path).parent / filename)
    Knead(items).write(out_path)

if __name__ == "__main__":
    parse_pages(sys.argv[1])