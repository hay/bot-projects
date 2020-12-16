from dataknead import Knead
from pathlib import Path
from pywikibot import WbTime
from util.bot import Bot
from util.utils import Datasheet
from util.wikidata import Props, Items, Query
from util.wikipedia import get_permalink
import pywikibot
import re
import sys

PATH = str(Path(__file__).parent.resolve())
RETRIEVED_DATE = pywikibot.WbTime(year = 2020, month = 12, day = 2)
YEAR = re.compile("^\d{4}")

def get_refs(item, reliwiki_id):
    return [
        item.get_item_claim(Props.LANGUAGE_WORK, Items.DUTCH),
        item.get_item_claim(Props.STATED_IN, Items.RELIWIKI),
        item.get_claim(Props.RETRIEVED, RETRIEVED_DATE),
        item.get_url_claim(Props.REF_URL, f"https://reliwiki.nl/index.php?curid={reliwiki_id}")
    ]

def check_prop(data, key, claims, prop):
    if prop in claims:
        print(f"Property {prop} already in claims")
        return False
    elif not data[key]:
        print(f"No {key} ({prop}) in data")
        return False
    else:
        print(f"Adding {key}")
        return True

def add_architect(job):
    data = job.data

    if not data["arch1_qid"]:
        print(f"No architect, skipping")
        return

    claims = job.item.get_claims()

    if Props.ARCHITECT in claims:
        print("Already has an architect, skipping")
        return

    # Add the actual data
    for index in ["1", "2", "3"]:
        prefix = f"arch{index}"

        if data[f"{prefix}_qid"] == "":
            continue

        qid = data[f"{prefix}_qid"]
        qualifiers = []

        if data[f"{prefix}_role_qid"]:
            qualifiers.append(
                job.item.get_item_claim(Props.OBJECT_HAS_ROLE, data[f"{prefix}_role_qid"])
            )

        if data[f"{prefix}_role_date"]:
            date = data[f"{prefix}_role_date"]
            yearstr = YEAR.match(date)

            if yearstr:
                year = int(yearstr[0])

                qualifiers.append(
                    job.item.get_claim(Props.POINT_IN_TIME, WbTime(year = year))
                )
            else:
                print(f"Unparsable year: {date}")

        job.item.add_item_claim(
            Props.ARCHITECT,
            qid,
            qualifiers = qualifiers,
            references = get_refs(job.item, data["pageid"])
        )

def add_architects():
    datapath = f"{PATH}/data/reliwiki/architects.csv"
    bot = Bot("reliwiki-architects", datapath = datapath, run_once = False)

    for job in bot.iterate():
        try:
            add_architect(job)
        except Exception as e:
            print(f"Could not finish this job because of an exception: {e}")

def add_info():
    # Only church buildings for now
    SPARQL = "select ?qid ?reliwiki where { ?qid wdt:P8897 ?reliwiki; wdt:P31 wd:Q16970. }"

    churches = Datasheet(PATH + "/data/reliwiki/churches_clean.csv", "pageid")
    bot = Bot("reliwiki-info", run_once = False , sparql = SPARQL)

    for job in bot.iterate():
        # First get the church
        reliwiki = job.data["reliwiki"]
        church = churches[reliwiki]
        claims = job.item.get_claims()

        if not church:
            print(f"Could not find church with ID {reliwiki}, skipping")
            continue
        else:
            print(f"Found church data: {church}")

        if ("name" in church) and (church["name"].strip() != ""):
            # Check if this name already exists in labels and aliases
            name = church["name"].strip()

            item_names = job.item.get_labels_aliases()
            print("Item is known as:", item_names)

            if name not in item_names:
                print(f"Name {name} does not occur in the list, adding...")
                job.item.add_alias(name, "nl")
            else:
                print(f"Name {name} is already in this list.")

        if check_prop(data = church, key = "sonneveld", prop = Props.SONNEVELD, claims = claims):
            job.item.add_string_claim(
                Props.SONNEVELD, church["sonneveld"], references = get_refs(job.item, reliwiki)
            )

        if check_prop(data = church, key = "coordinates", prop = Props.COORDINATES, claims = claims):
            coord = church["coordinates"].split(",")
            job.item.add_coordinate(
                Props.COORDINATES, coord, references = get_refs(job.item, reliwiki)
            )

        if check_prop(data = church, key = "zipcode", prop = Props.ZIP, claims = claims):
            job.item.add_string_claim(
                Props.ZIP, church["zipcode"], references = get_refs(job.item, reliwiki)
            )

        if check_prop(data = church, key = "address", prop = Props.STREET_ADDRESS, claims = claims):
            job.item.add_monoling_claim(
                Props.STREET_ADDRESS, church["address"], "nl", references = get_refs(job.item, reliwiki)
            )

        if check_prop(data = church, key = "denomination_qid", prop = Props.RELIGION, claims = claims):
            job.item.add_item_claim(
                Props.RELIGION, church["denomination_qid"], references = get_refs(job.item, reliwiki)
            )

def add_prop_extlink():
    csvpath = PATH + "/data/reliwiki/extlinks-clean.csv"
    bot = Bot("reliwiki-extlink", datapath = csvpath, run_once = False)

    for job in bot.iterate():
        reliwiki = job.data["pageid"]
        nlwiki = job.data["nlwiki"]
        claims = job.item.get_claims()

        if Props.RELIWIKI in claims:
            print("This item already has a Reliwiki ID, skipping")
            continue

        job.item.add_string_claim(
            Props.RELIWIKI,
            reliwiki,
            references = [
                job.item.get_item_claim(Props.IMPORTED_FROM, Items.WIKIPEDIA_NL),
                job.item.get_url_claim(Props.WM_IMPORT_URL, get_permalink("nl", job.data["nlwiki"]))
            ]
        )

def add_prop_rmm():
    csvpath = PATH + "/data/reliwiki/rmm.csv"
    bot = Bot("reliwiki-rmm", datapath = csvpath, run_once = False)

    for job in bot.iterate():
        reliwiki = job.data["pageid"]
        claims = job.item.get_claims()

        if Props.RELIWIKI in claims:
            print("This item already has a Reliwiki ID, skipping")
            continue

        job.item.add_string_claim(
            Props.RELIWIKI,
            reliwiki,
            references = [
                job.item.get_item_claim(Props.INFERRED_FROM, Items.RIJKSMONUMENT_ID)
            ]
        )

if __name__ == "__main__":
    add_info()