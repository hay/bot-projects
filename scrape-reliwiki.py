from util.mediawiki import AllPages
from dataknead import Knead
import re
import sys

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

def scrape_pages():
    churches = []
    api = AllPages("http://reliwiki.nl/api.php")

    for page in api.iterate_pages():
        print(page["title"])
        churches.append(page)

    Knead(churches).write("data/reliwiki/pages.json")

create_catalog()