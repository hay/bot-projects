from bs4 import BeautifulSoup
from dataknead import Knead
import re

NUMBER = re.compile("^([\d|\.]+)")

def get_number(s):
    s = s.strip()
    return int(NUMBER.findall(s)[0].replace(".", ""))

def get_reference(el, soup):
    ref = el.select_one(".reference")

    if not ref:
        return None

    ref_href = ref.select_one("a").get("href")
    ref_el = soup.select_one(ref_href)
    ref_url = ref_el.select_one("a.external")

    if ref_url:
        return ref_url.get("href")
    else:
        return None

def scrape():
    churches = []

    with open("data/churchseats/seats.html") as f:
        soup = BeautifulSoup(f.read(), "lxml")

    for table in soup.select(".wikitable"):
        for row in table.select("tr"):
            cells = row.select("td")

            if len(cells) < 4:
                continue

            name = cells[1]
            seats = cells[2]
            name_anchor = name.select_one("a")

            if not name_anchor:
                continue

            if not name_anchor.get("href").startswith("/wiki"):
                continue

            churches.append({
                "name" : name_anchor.get("title"),
                "href" : name_anchor.get("href"),
                "seats" : get_number(seats.get_text()),
                "reference" : get_reference(seats, soup)
            })

    Knead(churches).write("data/churchseats/seats.csv", fieldnames = [
        "name", "href", "seats", "reference"
    ])

scrape()