from dataknead import Knead
from pathlib import Path
from pywikibot import WbTime
from util.dates import parse_isodate, wbtime_now
from util.skiplist import Skiplist
from util.wikidata import Props, Items, WikidataItem
import pywikibot
import sys

PATH = Path(__file__).parent
DATA_PATH = PATH / "data" / "zomergasten" / "zomergasten-2024.json"

def get_ref(item):
    return [
        item.get_item_claim(Props.IMPORTED_FROM, Items.WIKIPEDIA_NL),
        item.get_url_claim(Props.WM_IMPORT_URL, "https://nl.wikipedia.org/w/index.php?title=Lijst_van_seizoenen_van_Zomergasten&oldid=67859574")
    ]

def create_season():
    season = Knead(str(DATA_PATH)).data()

    season_nr = season["season_nr"]
    print("----" * 20)
    print()
    print(f"Handling season #{season_nr}")

    year = season["year"]
    episodes_count = len(season["guests"])

    desc = {
        "label_en" : f"Zomergasten season {season_nr} ({year})",
        "label_nl" : f"Zomergasten seizoen {season_nr} ({year})",
        "description_en" : f"Season {season_nr} of the Dutch talk show 'Zomergasten', as broadcasted by VPRO in {year}",
        "description_nl" : f"Seizoen {season_nr} van het VPRO-televisieprogramma 'Zomergasten', uitgezonden in {year}",
        "aliases_en" : [
            f"Zomergasten {year}",
            f"Zomergasten season {season_nr}"
        ],
        "aliases_nl" : [
            f"Zomergasten {year}",
            f"Zomergasten seizoen {season_nr}"
        ]
    }

    item = WikidataItem(
        summary = f"Creating new item for the Zomergasten season {season_nr}",
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

    item.add_item_claim(Props.INSTANCE_OF, Items.TV_SERIES_SEASON)
    item.add_item_claim(Props.PART_OF_SERIES, Items.ZOMERGASTEN, qualifiers = [
        item.get_string_claim(Props.SERIES_ORDINAL, str(season_nr))
    ])

    if "presenter" in season:
        presenter_qid = season["presenter"]["qid"]
        item.add_item_claim(Props.PRESENTER, presenter_qid,
            references = get_ref(item)
        )

    item.add_time_claim(
        Props.PUB_DATE,
        pywikibot.WbTime(
            year = year
        ),
        references = get_ref(item)
    )
    item.add_item_claim(Props.GENRE, Items.TALK_SHOW)
    item.add_item_claim(Props.ORIGINAL_BROADCASTER, Items.VPRO)
    item.add_item_claim(Props.COUNTRY_OF_ORIGIN, Items.NETHERLANDS)
    item.add_item_claim(Props.LANGUAGE_SHOW, Items.DUTCH)
    item.add_item_claim(Props.DISTRIBUTED_BY, Items.NPO)
    item.add_quantity_claim(Props.NR_OF_EPISODES, episodes_count,
        references = get_ref(item)
    )

def create_episodes():
    season = Knead(str(DATA_PATH)).data()
    episode_nr = 194 # last episode of previous season
    season_qid = "Q127688650"
    season_episode_ordinal = 1

    print()
    print(f"Handling season #{season['season_nr']}")

    year = season["year"]

    for guest in season["guests"]:
        # Take presenter from guest (for rotating guests), otherwise
        # take from season
        if "presenter" in guest:
            presenter_name = guest["presenter"]["name"]
            presenter_qid = guest["presenter"]["qid"]
        else:
            presenter_name = season["presenter"]["name"]
            presenter_qid = season["presenter"]["qid"]

        episode_nr += 1
        guest_name = guest["guest"]["name"]
        guest_qid = guest["guest"]["qid"]
        print("----" * 20)
        print()
        print(f"Handling episode #{episode_nr}, guest {guest_name}")
        date = parse_isodate(guest["date_parsed"])

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
                    "nl" : desc["description_nl"],
                    "de" : "Folge von Zomergasten"
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
        item.add_item_claim(Props.GENRE, Items.TALK_SHOW)
        item.add_item_claim(Props.ORIGINAL_BROADCASTER, Items.VPRO)
        item.add_item_claim(Props.COUNTRY_OF_ORIGIN, Items.NETHERLANDS)
        item.add_item_claim(Props.LANGUAGE_SHOW, Items.DUTCH)
        item.add_item_claim(Props.DISTRIBUTED_BY, Items.NPO)
        item.add_item_claim(Props.SEASON, season_qid, qualifiers = [
            item.get_string_claim(Props.SERIES_ORDINAL, str(season_episode_ordinal))
        ])

        season_episode_ordinal += 1

if __name__ == "__main__":
    # create_season()
    create_episodes()