from pathlib import Path
from pywikibot import WbTime
from util.bot import Bot, CreateBot
from util.utils import dd
from util.wikidata import Props, Items

PATH = Path(__file__).parent.resolve()

def get_ref(job):
    return [
        job.item.get_url_claim(Props.REF_URL, job.data["url"]),
        job.item.get_claim(Props.RETRIEVED, WbTime(
            year = 2021, month = 11, day = 15
        )),
        job.item.get_item_claim(Props.LANGUAGE_WORK, Items.DUTCH)
    ]

def get_safe_value(val):
    if is_empty(val):
        return None
    else:
        return val

def has_duplicate_item(bot):
    # Get the title, and check if it's unique in combination with artist/year
    job = bot.current_job
    title = job.data["title"]
    inventory_nr = job.data["inventory"]
    creator_qid = get_safe_value(job.data["creator_qid"])
    year = get_safe_value(job.data["date"])
    has_duplicate = False

    for item in bot.data:
        if inventory_nr == item["inventory"]:
            # Current item, skip
            continue

        if all([
            title == item["title"],
            creator_qid == get_safe_value(item["creator_qid"]),
            year == get_safe_value(item["date"])
        ]):
            has_duplicate = True
            break

    return has_duplicate

def is_empty(val):
    val = val.strip()
    return val == "0" or val == "#N/A" or val ==""

def run_bot():
    DATA_PATH  = PATH / "data" / "vbvd"

    bot = CreateBot(
        "vbvd2",
        run_once = False,
        datapath = str(DATA_PATH / "export-met-urls.csv"),
        key = "inventory"
    )

    for job in bot.iterate():
        inventory = job.data["inventory"]
        title = job.data["title"]
        creator_name = job.data["creator_name"]
        inventory_nr = job.data["inventory"]

        # If the job has a qid, skip because this already exists
        if not is_empty(job.data["item_qid"]):
            job.abort(f"Skipping {inventory}/{title}, item already is on Wikidata")
            continue



        summary = f"Adding new artwork '{title}' in Museum van Bommel van Dom in Venlo, the Netherlands"

        labels = {
            "nl" : title
        }

        descriptions = {}

        if is_empty(job.data["type"]):
            descriptions["nl"] = f"kunstwerk van {creator_name}"
        else:
            type_nl = job.data["type"]
            descriptions["nl"] = f"{type_nl} van {creator_name}"

        if is_empty(job.data["type_en"]):
            descriptions["en"] = f"work of art by {creator_name}"
        else:
            type_en = job.data["type_en"]
            descriptions["en"] = f"{type_en} by {creator_name}"

        if not is_empty(job.data["date"]):
            year = job.data["date"]
            descriptions["en"] = f"{year} " + descriptions["en"]
            descriptions["nl"] = descriptions["nl"] + f" uit {year}"

        # Check for duplicate item, and if it's there, create a description with
        # the inventory number
        if has_duplicate_item(bot):
            print("Duplicate title/description, return a description with inventory suffix")
            descriptions["nl"] = f"{descriptions['nl']} (objectnummer {inventory_nr})"
            dd(descriptions)

        aliases = {
            "en" : [ title ]
        }

        job.create_item(summary, labels, descriptions, aliases)

        if is_empty(job.data["type_qid"]):
            job.item.add_item_claim(Props.INSTANCE_OF, Items.WORK_OF_ART)
        else:
            job.item.add_item_claim(Props.INSTANCE_OF, job.data["type_qid"])

        job.item.add_item_claim(
            Props.LOCATION,
            Items.MUS_BOMMELVDAM,
            references = get_ref(job)
        )

        if is_empty(job.data["collection_qid"]):
            collection_qid = None
            collection_qualifers = []
        else:
            collection_qid = job.data["collection_qid"]
            collection_qualifers = [
                job.item.get_item_claim(Props.COLLECTION, Items.MUS_BOMMELVDAM)
            ]

        job.item.add_string_claim(
            Props.INVENTORY_NR,
            inventory_nr,
            qualifiers = collection_qualifers,
            references = get_ref(job)
        )

        job.item.add_url_claim(
            Props.DESCRIBED_AT_URL,
            job.data["url"],
            qualifiers = [
                job.item.get_item_claim(Props.LANGUAGE_WORK, Items.DUTCH)
            ]
        )

        if not is_empty(job.data["creator_qid"]):
            job.item.add_item_claim(
                Props.CREATOR,
                job.data["creator_qid"],
                references = get_ref(job)
            )

        if not is_empty(job.data["date"]):
            job.item.add_time_claim(
                Props.INCEPTION,
                WbTime(year = int(job.data["date"])),
                references = get_ref(job)
            )

        if job.data["collection_qid"]:
            if is_empty(job.data["aquirement_qid"]):
                cause_qualifers = []
            else:
                cause_qualifers = [
                    job.item.get_item_claim(Props.HAS_CAUSE, job.data["aquirement_qid"])
                ]

            job.item.add_item_claim(
                Props.COLLECTION,
                job.data["collection_qid"],
                qualifiers = cause_qualifers,
                references = get_ref(job)
            )

        if not is_empty(job.data["material_qid"]):
            job.item.add_item_claim(
                Props.MATERIAL_USED,
                job.data["material_qid"],
                references = get_ref(job)
            )

        if not is_empty(job.data["height"]):
            job.item.add_quantity_claim(
                Props.HEIGHT,
                job.data["height"],
                unit = "http://www.wikidata.org/entity/Q174728",
                references = get_ref(job)
            )

if __name__ == "__main__":
    run_bot()