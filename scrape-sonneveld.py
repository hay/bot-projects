#!/usr/bin/env python3
from dataknead import Knead
from pathlib import Path
from util.utils import dd
import re
import sys

def get_permalink(index):
    if index < 1001:
        return f"http://reliwiki.nl/index.php/Sonneveld-index_1_-_1000#{index}"
    elif index < 2001:
        return f"http://reliwiki.nl/index.php/Sonneveld-index_1000_-_2000#{index}"
    elif index < 3001:
        return f"http://reliwiki.nl/index.php/Sonneveld-index_2000_-_3000#{index}"
    elif index < 4001:
        return f"http://reliwiki.nl/index.php/Sonneveld-index_3000_-_4000#{index}"
    elif index < 5001:
        return f"http://reliwiki.nl/index.php/Sonneveld-index_4000_-_5000#{index}"
    elif index < 6001:
        return f"http://reliwiki.nl/index.php/Sonneveld-index_5000_-_6000#{index}"

def clean(string):
    return string.strip().replace("\n", "")

def create_catalog():
    catalog = open("data/sonneveld/catalog.tsv", "w")

    for item in Knead("data/sonneveld/kerkenkaart.csv").data():
        item_id = item["kerk_id"]
        name = item["naam"]
        place = item["plaats"]
        lat = item["lat"]
        lon = item["lon"]
        label = f"{name} ({place})"
        description = f"church in {place} (the Netherlands), located at {lat},{lon}"
        link = get_permalink(int(item_id))

        line = f"{item_id}\t{clean(label)}\t{clean(description)}\tQ1370598\t{link}\n"
        catalog.write(line)

    catalog.close()

def create_csv():
    items = []
    json = Knead("data/sonneveld/kerkenkaart.json").data()

    for feature in json["features"]:
        prop = feature["properties"]
        coord = feature["geometry"]["coordinates"]
        prop["lat"] = coord[1]
        prop["lon"] = coord[0]
        items.append(prop)

    Knead(items).write("data/sonneveld/kerkenkaart.csv")


create_catalog()