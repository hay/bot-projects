#!/usr/bin/env python3
from bs4 import BeautifulSoup
from dataknead import Knead
from pathlib import Path
import requests
import sys

BASE = "data/kor-utrecht"
#BASE_URL = "https://www.nijmegen.nl/kos/kunstwerk.aspx?id="

# def parse_items():
#     Knead(f"{BASE}/items.json")

# globals()[sys.argv[1]]()

items = Knead(f"{BASE}/items.json").data()["data"]["searchAPISearch"]["documents"]
Knead(items).map("kunstenaar_naam").write(f"{BASE}/artists.csv")
