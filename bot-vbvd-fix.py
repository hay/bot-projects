from pathlib import Path
from util.bot import Bot
from util.utils import dd, send_im_message

PATH = Path(__file__).parent.resolve()

def is_empty(val):
    val = val.strip()
    return val == "0" or val == "#N/A" or val ==""

def run_bot():
    DATA_PATH  = PATH / "data" / "vbvd"

    bot = Bot(
        "vbvd-fix",
        datapath = str(DATA_PATH / "export-met-urls.csv"),
        qid_key = "item_qid",
        empty_check = is_empty
    )

    for job in bot.iterate():
        # Check if we need to fix the description, otherwise skip
        if job.data["fix_description"] == "FALSE":
            job.abort("Skip, does not needs a fix to description")
            continue

        title = job.data["title"]
        inventory_nr = job.data["inventory"]

        summary = f"Fixing description for '{title}' in Museum van Bommel van Dom in Venlo, the Netherlands"

        descriptions = {}

        # Check for empty or non-existing creator
        if is_empty(job.data["creator_name"]):
            creator_name = "een onbekende kunstenaar"
            creator_name_en = "an unknown artist"
        else:
            creator_name = job.data["creator_name"]
            creator_name_en = creator_name

        if is_empty(job.data["type"]):
            descriptions["nl"] = f"kunstwerk van {creator_name}"
        else:
            type_nl = job.data["type"]
            descriptions["nl"] = f"{type_nl} van {creator_name}"

        if is_empty(job.data["type_en"]):
            descriptions["en"] = f"work of art by {creator_name_en}"
        else:
            type_en = job.data["type_en"]
            descriptions["en"] = f"{type_en} by {creator_name_en}"

        if not is_empty(job.data["date"]):
            year = job.data["date"]
            descriptions["en"] = f"{year} " + descriptions["en"]
            descriptions["nl"] = descriptions["nl"] + f" uit {year}"

        # Check for 'inventory needed' item, and if it's there, create a description with
        # the inventory number
        if job.data["needs_inventory"] == "TRUE":
            print("Get a description with inventory suffix")
            descriptions["nl"] = f"{descriptions['nl']} (objectnummer {inventory_nr})"
            dd(descriptions)

        job.item.edit_descriptions(descriptions, summary = summary)

if __name__ == "__main__":
    try:
        run_bot()
    except:
        send_im_message("Bot got an exception")

    send_im_message("Bot finished running")