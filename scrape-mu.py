from dataknead import Knead
from pathlib import Path


PATH = Path(__file__).parent.resolve()
DATA_PATH = PATH / "data" / "mu"

def parse(item):
    return {
        "url" : "https://mu.nl/en/exhibitions/" + item["address"],
        "start" : item["date_start"],
        "end" : item["date_end"],
        "title_nl" : item["title_nl"],
        "title_en" : item["title_en"],
        "subtitle_nl" : item["subtitle_nl"],
        "subtitle_en" : item["subtitle_en"],
    }

expos = Knead(str(DATA_PATH / "expos.json")).map(parse)
expos.write(str(DATA_PATH / "expos-clean.json"), indent = 4)
expos.write(str(DATA_PATH / "expos-clean.csv"))