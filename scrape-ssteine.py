#!/usr/bin/env python3.6
from bs4 import BeautifulSoup
from dataknead import Knead
from pathlib import Path
from util.mediawiki import CategoryMembers
from util.utils import parse_urlargs
import requests
import sys

BASE_PATH = Path.cwd() / "data/stolpersteine"
DEFAULT_CAT = "Category:Stolpersteine_without_Wikidata_item"

def get_category_pages(path, category = DEFAULT_CAT):
    html_path = BASE_PATH / path
    html_path.mkdir(exist_ok = True)
    catmembers = CategoryMembers("wikimedia", "commons", category)

    for member in catmembers.members():
        get_page_by_id(member["pageid"], html_path)

def get_page_by_id(pid, html_path):
    pid_path = html_path / f"{pid}.html"

    if pid_path.exists():
        print(f"{pid_path} exists, skipping")
        return

    url = f"https://commons.wikimedia.org/wiki/?curid={pid}"
    req = requests.get(url)

    with open(pid_path, "w") as f:
        f.write(req.text)
        print(f"Wrote {pid_path}")

def get_pages_by_csv(csv_path):
    stem = Path(csv_path).stem
    html_path = BASE_PATH / stem
    print("Saving to: " + str(html_path))

    html_path.mkdir(exist_ok = True)

    for item in Knead(csv_path).data():
        get_page_by_id(item["pid"], html_path)

def parse_pages(html_path):
    items = []

    for path in Path(html_path).glob("*.html"):
        print()
        print(f"Scraping {path}")

        with open(path) as f:
            soup = BeautifulSoup(f.read(), "lxml")

        url = soup.select_one('[rel="canonical"]').get("href")
        description = soup.select_one('.commons-file-information-table div.description')
        description = description.get_text().replace("Nederlands: ", "").strip()
        geolink = soup.select_one('[href*="wikimap.toolforge.org"]').get("href")
        geolink = parse_urlargs(geolink)

        items.append({
            "url" : url,
            "name" : None,
            "image" : url.replace("https://commons.wikimedia.org/wiki/", ""),
            "inscription" : description,
            "lat" : geolink["lat"],
            "lon" : geolink["lon"],
            "location" : None,
            "location_qid" : None,
            "inception" : None,
            "street" : None,
            "street_qid" : None,
            "street_nr" : None,
            "url" : None
        })

    filename = Path(html_path).stem + "-parsed.csv"
    out_path = str(Path(html_path).parent / filename)
    Knead(items).write(out_path)

if __name__ == "__main__":
    action, arg = sys.argv[1], sys.argv[2]

    if len(sys.argv) == 4:
        arg2 = sys.argv[3]
    else:
        arg2 = None

    if action == "scrape":
        get_category_pages(arg, arg2)
    elif action == "parse":
        path = BASE_PATH / arg
        parse_pages(path)
    else:
        raise Exception(f"Unknown action: {action}")