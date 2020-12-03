from pathlib import Path
from util.bot import Bot
from util.wikidata import Props, Items

PATH = str(Path(__file__).parent.resolve())

def main():
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
    main()