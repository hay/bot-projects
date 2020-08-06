from dataknead import Knead
from datetime import datetime
from pathlib import Path
from pywikibot import WbTime
from util.skiplist import Skiplist
from util.utils import site
from util.wikidata import Props, Items, WikidataItem
import locale
import pywikibot
import sys

def get_ref(item):
    return [
        item.get_item_claim(Props.IMPORTED_FROM, Items.WIKIPEDIA_NL),
        item.get_url_claim(Props.WM_IMPORT_URL, "https://nl.wikipedia.org/w/index.php?title=Lijst_van_seizoenen_van_Zomergasten&oldid=56861509")
    ]

def parse_date(isodate):
    date = datetime.strptime(isodate, "%Y-%m-%d")

    locale.setlocale(locale.LC_TIME, "en_US")
    en = date.strftime("%B %d, %Y")
    locale.setlocale(locale.LC_TIME, "nl_NL")
    nl = date.strftime("%d %B %Y")

    return {
        "day" : date.day,
        "en" : en,
        "iso" : isodate,
        "month" : date.month,
        "nl" : nl,
        "year" : date.year
    }

def main():
    PATH = str(Path(__file__).parent)
    seasons = Knead(PATH + "/data/zomergasten/zomergasten.json").data()

    # Sort seasons by season_nr
    seasons.sort(key = lambda i:i["season_nr"])
    episode_nr = 0

    for season in seasons:
        print()
        print(f"Handling season #{season['season_nr']}")
        year = season["year"]
        presenter_name = season["presenter"]["title"]
        presenter_qid = season["presenter"]["qid"]

        for guest in season["guests"]:
            episode_nr += 1
            guest_name = guest["guest"]["text"]
            guest_qid = guest["guest"]["qid"]
            print("----" * 20)
            print()
            print(f"Handling episode #{episode_nr}, guest {guest_name}")
            date = parse_date(guest["date_parsed"])

            if episode_nr < 2:
                print("Already handled, skipping")
                continue

            desc = {
                "label_en" : f"Zomergasten with {guest_name} ({year})",
                "label_nl" : f"Zomergasten met {guest_name} ({year})",
                "description_en" : f"episode {episode_nr} of the Dutch talk show 'Zomergasten', as broadcasted by VPRO on {date['en']}",
                "description_nl" : f"aflevering {episode_nr} van het VPRO-televisieprogramma 'Zomergasten', uitgezonden op {date['nl']}",
                "aliases_en" : [
                    f"{presenter_name} with {guest_name}",
                    f"Zomergasten episode {episode_nr}"
                ],
                "aliases_nl" : [
                    f"{presenter_name} met {guest_name}",
                    f"Zomergasten aflevering {episode_nr}"
                ]
            }

            if "qid" in guest:
                print(f"Getting a qid: {guest['qid']}")
                item = WikidataItem(guest["qid"])
            else:
                item = WikidataItem(
                    summary = f"Creating new item for the Zomergasten episode with {guest_name}",
                    labels = {
                        "en" : desc["label_en"],
                        "nl" : desc["label_nl"]
                    },
                    descriptions = {
                        "en" : desc["description_en"],
                        "nl" : desc["description_nl"]
                    },
                    aliases = {
                        "en" : desc["aliases_en"],
                        "nl" : desc["aliases_nl"]
                    }
                )

            item.add_item_claim(Props.INSTANCE_OF, Items.TV_SERIES_EPISODE)
            item.add_item_claim(Props.PART_OF_SERIES, Items.ZOMERGASTEN, qualifiers = [
                item.get_string_claim(Props.SERIES_ORDINAL, str(episode_nr))
            ])
            item.add_item_claim(Props.GENRE, Items.TALK_SHOW)
            item.add_item_claim(Props.ORIGINAL_BROADCASTER, Items.VPRO)
            item.add_item_claim(Props.COUNTRY_OF_ORIGIN, Items.NETHERLANDS)
            item.add_item_claim(Props.LANGUAGE_SHOW, Items.DUTCH)
            item.add_item_claim(Props.PRESENTER, presenter_qid,
                references = get_ref(item)
            )
            item.add_time_claim(
                Props.PUB_DATE,
                pywikibot.WbTime(
                    year = date["year"],
                    month = date["month"],
                    day = date["day"]
                ),
                references = get_ref(item)
            )
            item.add_item_claim(Props.TALK_SHOW_GUEST, guest_qid,
                references = get_ref(item)
            )
            item.add_item_claim(Props.DISTRIBUTED_BY, Items.NPO)

            sys.exit()

if __name__ == "__main__":
    main()