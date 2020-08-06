from dataknead import Knead
from bs4 import BeautifulSoup
import dateparser

def get_qid(href):
    for row in Knead("data/zomergasten/guests-matched.csv").data():
        if row["query"] == href:
            return row["id"]

    raise Exception(f"Could not find {href}")

def get_link(el):
    a = el.select_one("a")
    href = a.get("href").strip().replace("https://nl.wikipedia.org/wiki/", "")

    return {
        "href" : href,
        "link" : a.get("href"),
        "qid" : get_qid(href),
        "text" : el.get_text().strip().replace("\n", "").replace("  ", " "),
        "title" : a.get("title")
    }

def transform():
    with open("data/zomergasten/zomergasten.html") as f:
        soup = BeautifulSoup(f.read(), "lxml")

    seasons = []
    season = None
    guests = []
    presenters = []

    for tr in soup.select("tr"):
        tds = tr.select("td")

        if (len(tds) < 3):
            continue

        cells = [td.get_text().strip() for td in tds]

        if cells[0].startswith("Seizoen"):
            if season:
                seasons.append(season)

            presenter = get_link(tds[1])
            presenters.append(presenter["href"])
            year = int(presenter["text"][0:4])

            season = {
                "season" : cells[0],
                "season_nr" : int(cells[0].replace("Seizoen ", "")),
                "presenter" : presenter,
                "year" : year,
                "guests" : []
            }
        else:
            guest = get_link(tds[1])
            guests.append(guest["href"])
            date = cells[0]
            date_parsed = dateparser.parse(date).isoformat("T")[0:10]

            season["guests"].append({
                "date" : date,
                "date_parsed" : date_parsed,
                "guest" : guest
            })

    seasons.append(season)
    Knead(guests).write("data/zomergasten/guests.txt")
    Knead(presenters).write("data/zomergasten/presenters.txt")
    Knead(seasons).write("data/zomergasten/zomergasten.json", indent = 4)

if __name__ == "__main__":
    transform()