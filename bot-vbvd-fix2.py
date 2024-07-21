from dataknead import Knead
from pathlib import Path
from util.bot import Bot
from util.utils import send_im_message
from util.wikidata import WikidataItem, Query, Props, Items
import sys
import traceback

PATH = Path(__file__).parent.resolve()
DATA_PATH  = PATH / "data" / "vbvd"

def fix_creator(wrongqid, goodqid):
    query = """
        select ?item where {
            ?item wdt:P276 wd:Q1994770. # Make sure item is in VBVD
            ?item wdt:P170 wd:%s
        }
    """ % wrongqid

    query = Query(query)
    query.run()

    for result in query.iter_results():
        qid = result["item"]
        item = WikidataItem(qid)
        item.replace_claim_target("P170", wrongqid, goodqid)

def fix_dirk_van_gullik():
    fix_creator("Q55076910", "Q29559503")

def fix_jan_de_boer():
    fix_creator("Q21980946", "Q111023169")

def fix_na():
    path = str(DATA_PATH / "description-na.csv")

    bot = Bot(
        botid = "vbvd-fix2",
        datapath = path,
        qid_key = "item"
    )

    for job in bot.iterate():
        descriptions = {}

        # Set new descriptions
        is_changed = False

        for lang, desc in dict(job.item.get_descriptions()).items():
            if "#N/A" in desc:
                is_changed = True
                if lang == "nl":
                    desc = desc.replace("#N/A", "een onbekende kunstenaar")
                elif lang == "en":
                    desc = desc.replace("#N/A", "an unknown artist")

                descriptions[lang] = desc

        if is_changed:
            print("Setting new descriptions", descriptions)
            job.item.edit_descriptions(descriptions, "Fixing the descriptions")
        else:
            print("Descriptions already adapted")

        # And add the anonymous claim
        if not Props.CREATOR in job.item.get_claims():
            print("Adding creator prop")
            job.item.add_item_claim(
                Props.CREATOR, "somevalue", qualifiers = [
                    job.item.get_item_claim(Props.OBJECT_HAS_ROLE, Items.ANONYMOUS)
                ]
            )
        else:
            print("Already has a creator")

if __name__ == "__main__":
    try:
        fix_na()
    except:
        print(traceback.format_exc())
        send_im_message("Bot got an exception")

    send_im_message("Bot finished running")