from bs4 import BeautifulSoup
from dataknead import Knead
from pathlib import Path
import requests

DATA_PATH  = Path.cwd() / "data/verzekeraars/"
OVERVIEW_PATH = DATA_PATH / "html-overview/"

def parse_overviews():
    items = []

    for path in OVERVIEW_PATH.glob("*.html"):
        with open(path) as f:
            soup = BeautifulSoup(f.read(), "lxml")

        print(f"Parsing {path}")

        for row in soup.select("table.list tbody tr"):
            cells = row.select("td")
            idx = cells[0].select_one("a").get("href").replace("detail.jsp?id=", "")

            items.append({
                "id" : idx,
                "stat_name" : cells[0].select_one("a").get_text(),
                "handelsnaam" : cells[1].select_one("a").get_text(),
                "plaats" : cells[2].select_one("a").get_text()
            })

    parsed_path = str(DATA_PATH / "overview.csv")

    Knead(items).write(parsed_path, fieldnames = ["id", "stat_name", "handelsnaam", "plaats"])

def scrape_overviews():
    for index in range(1, 125):
        path = OVERVIEW_PATH / f"{index}.html"

        if path.exists():
            print(f"Path exists, skipping: {path}")
            continue

        url = f"https://www.dnb.nl/toezichtprofessioneel/openbaar-register/WFTVE/index.jsp?&page={index}"
        print(f"Now getting: <{url}>")

        req = requests.get(url)

        with open(path, "w") as f:
            f.write(req.text)
            print(f"Wrote {path}")

if __name__ == "__main__":
    # scrape_overviews()
    parse_overviews()