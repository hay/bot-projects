from pathlib import Path
from pywikibot import WbTime
from util.bot import Bot, CreateBot
from util.wikidata import Props, Items

PATH = Path(__file__).parent.resolve()

def get_ref(job):
    return [
        job.item.get_url_claim(Props.REF_URL, job.data["url"]),
        job.item.get_claim(Props.RETRIEVED, WbTime(
            year = 2021, month = 10, day = 8
        )),
        job.item.get_item_claim(Props.LANGUAGE_WORK, Items.DUTCH)
    ]

def run_bot():
    DATA_PATH  = PATH / "data" / "vbvd"

    bot = CreateBot(
        "vbvd",
        run_once = False,
        datapath = str(DATA_PATH / "items2.json"),
        key = "title"
    )

    for job in bot.iterate():
        title = job.data["title"]
        creator = job.data["artist_label"]
        year = job.data["year"]

        summary = f"artwork '{title}' in Museum van Bommel van Dom in Venlo, the Netherlands",

        labels = {
            "nl" : title
        }

        descriptions = {
            "de" : f"Kunstwerk von {creator}",
            "en" : f"work of art by {creator}",
            "es" : f"obra de arte de {creator}",
            "fr" : f"œuvre d’art de {creator}",
            "nl" : f"kunstwerk van {creator}"
        }

        if year:
            descriptions["en"] = f"{year} " + descriptions["en"]
            descriptions["nl"] = descriptions["nl"] + f" uit {year}"

        aliases = {
            "en" : [ title ]
        }

        job.create_item(summary, labels, descriptions, aliases)

        # Basics
        job.item.add_item_claim(Props.INSTANCE_OF, Items.WORK_OF_ART)
        job.item.add_item_claim(Props.LOCATION, Items.MUS_BOMMELVDAM)

        job.item.add_string_claim(
            Props.INVENTORY_NR,
            job.data["inventory_nr"],
            qualifiers = [
                job.item.get_item_claim(Props.COLLECTION, Items.MUS_BOMMELVDAM)
            ],
            references = get_ref(job)
        )

        job.item.add_url_claim(
            Props.DESCRIBED_AT_URL,
            job.data["url"],
            qualifiers = [
                job.item.get_item_claim(Props.LANGUAGE_WORK, Items.DUTCH)
            ]
        )

        if job.data["artist_qid"]:
            job.item.add_item_claim(
                Props.CREATOR,
                job.data["artist_qid"],
                references = get_ref(job)
            )

        if job.data["year"]:
            job.item.add_time_claim(
                Props.INCEPTION,
                WbTime(year = job.data["year"]),
                references = get_ref(job)
            )

        if job.data["collection_qid"]:
            job.item.add_item_claim(
                Props.COLLECTION,
                job.data["collection_qid"],
                references = get_ref(job)
            )

if __name__ == "__main__":
    run_bot()