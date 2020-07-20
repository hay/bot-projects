import sys
sys.path.append("../../")

from dataknead import Knead
from pathlib import Path
from util.wikipedia import Infobox
from util.dates import parse_year_nl
import dateparser

pages = Knead("list.json").data()

def get_all():
    churches = []

    for index, page in enumerate(pages):
        pid = page["id"]
        qid = page.get("q", None)
        title = page["title"]
        print(f"#{index} '{title}'' ({pid} / {qid})")

        path = DATA_PATH / f"{pid}.json"
        ibox = Infobox("nl", title)

        if path.exists():
            print(f"{path} exists, using that")
            apidata = Knead(str(path), read_as = "json").data()
            data = ibox.get_data(apidata)
        else:
            data = ibox.get_data()
            # Write cached data
            print(f"Writing cache data to {path}")
            Knead(ibox.apidata).write(path.resolve())

        boxes = data["infoboxes"]

        if len(boxes) == 0:
            print("No infobox")
            continue

        if len(boxes) > 1:
            print("More than one infobox, picking the first")

        churches.append({
            "pid" : pid,
            "qid" : qid,
            "title" : title,
            "data" : boxes[0].box
        })

    Knead(churches).write("parsed.json")

def year(string):
    if not string:
        return None

    dates = parse_year_nl(string)

    if not dates:
        return None

    def mapyear(date):
        value = date[0]
        dtype = date[1]

        if dtype == "range":
            # Check if we can do something here
            start = value[0]
            end = value[1]

            if start[0:3] == end[0:3]:
                return {
                    "start" : start,
                    "end" : end,
                    "value" : start[0:3] + "0",
                    "type" : "decade"
                }
            elif start[0:2] == end[0:2]:
                return {
                    "start" : start,
                    "end" : end,
                    "value" : start[0:2] + "00",
                    "type" : "century"
                }

        return {
            "value" : value,
            "type" : dtype
        }

    return [mapyear(y) for y in dates]

def parse_all():
    items = []
    index = 0

    for item in Knead("parsed.json").data():
        def get(key):
            if key in item["data"]:
                return item["data"][key]["fulltext"]
            else:
                return None

        items.append({
            "qid" : item["qid"],
            "pid" : item["pid"],
            "title" : item["title"],
            "religion" : get("Denominatie"),
            "inception" : year(get("Gebouwd in")),
            "restored" : year(get("Restauratie(s)")),
            "demolished" : year(get("Gesloopt in")),
            "expanded" : year(get("Uitbreiding(en)"))
        })

    Knead(items).write("import.json", indent = 4)

parse_all()