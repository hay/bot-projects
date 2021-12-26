#!/usr/bin/env python3
from bs4 import BeautifulSoup
from dataknead import Knead
from pathlib import Path
from time import sleep
from util.utils import dd, Datasheet
import requests

DATA_PATH  = Path.cwd() / "data/vbvd/"
ENDPOINT = "https://www.vanbommelvandam.nl/collectie/"

def get(soup, selector, attr):
    el = soup.select_one(selector)

    if el:
        return el.get(attr)
    else:
        return ""

def text(soup, selector):
    el = soup.select_one(selector)

    if el:
        return el.get_text().strip()
    else:
        return ""

def clean_artist(artist):
    return artist.replace(",", "").replace("  ", " ")

def fetch_items():
    for item in Knead(str(DATA_PATH / "overview.csv"), has_header = True).data():
        if item["artist"] == "":
            continue

        url = item["href"]
        basename = url.replace("https://www.vanbommelvandam.nl/collectie/", "").replace("/", "")

        print(f"Getting {url}")
        path = DATA_PATH / "html" / f"item-{basename}.html"
        req = requests.get(url)

        with open(path, "w") as f:
            f.write(req.text)

        sleep(1)

def parse_all_items():
    items = []

    for path in (DATA_PATH / "html").glob("item-*.html"):
        with open(path) as f:
            item = parse_item(f.read())
            items.append(item)

    Knead(items).write(DATA_PATH / "items.json", indent = 4)

def parse_all_overviews():
    items = []

    for path in (DATA_PATH / "html").glob("*.html"):
        with open(path) as f:
            items = items + parse_overview(f.read())

    Knead(items).write(DATA_PATH / "overview.csv", fieldnames = [
        "artist", "title", "href"
    ])

def parse_item(html):
    soup = BeautifulSoup(html, "lxml")

    data = {
        "artist" : clean_artist(text(soup, 'a[href*="zoeken/kunstenaar"]')),
        "href" : get(soup, 'link[rel="canonical"]', "href"),
        "title" : soup.select("h2.font-medium")[0].get_text()
    }

    # Get all metadata fields out of dl
    keys = soup.select("dl.text-sm > dt")
    vals = soup.select("dl.text-sm > dd")

    for index, key in enumerate(keys):
        key = key.get_text().strip().lower()
        val = vals[index].get_text().strip()
        data[key] = val

    return data

def parse_json_items():
    qid_artists = Datasheet(str(DATA_PATH / "qid-artists.csv"), "label")
    qid_collections = Datasheet(str(DATA_PATH / "qid-collections.csv"), "label")
    items = []

    def get_qid(datasheet, key):
        if datasheet[key]:
            return datasheet[key]["qid"]
        else:
            return None

    for item in Knead(str(DATA_PATH / "items.json")).data():
        print(item.get("title", None))
        year = None

        if item["jaar"].isdigit():
            year = int(item["jaar"])

        collection_label = item.get("collectie", None)
        artist_label = item.get("artist", None)

        items.append({
            "inventory_nr" : item["objectnummer"],
            "title" : item.get("title", None),
            "year" : year,
            "url" : item["href"],
            "artist_label" : artist_label,
            "artist_qid" : get_qid(qid_artists, artist_label),
            "collection_label" : collection_label,
            "collection_qid" : get_qid(qid_collections, collection_label)
        })

    Knead(items).write(str(DATA_PATH / "items2.csv"))

def parse_overview(html):
    soup = BeautifulSoup(html, "lxml")

    items = []

    for el in soup.select("a.h-full"):
        if "collectie" not in el.get("href"):
            continue

        items.append({
            "artist" : clean_artist(text(el, ".font-light")),
            "href" : el.get("href"),
            "title" : text(el, ".font-medium")
        })

    return items

def fetch_overviews():
    for i in range(1, 16):
        url = f"{ENDPOINT}p{i}"
        req = requests.get(url)

        print(f"Getting <{url}>")

        with open(DATA_PATH / f"p{i}.html", "w") as f:
            f.write(req.text)

def switch_name(name):
    print(name)

    name = name.strip()

    if "," in name:
        parts = [p.strip() for p in name.split(",")]
        return parts[1] + " " + parts[0]

    else:
        return name

if __name__ == "__main__":
    Knead("names.csv", read_as = "txt").map(switch_name).write("names-fixed.csv")