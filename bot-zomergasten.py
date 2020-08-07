from dataknead import Knead
from pathlib import Path
from pywikibot import WbTime
from util.dates import parse_isodate
from util.skiplist import Skiplist
from util.wikidata import Props, Items, WikidataItem
import pywikibot
import sys

def get_ref(item):
    return [
        item.get_item_claim(Props.IMPORTED_FROM, Items.WIKIPEDIA_NL),
        item.get_url_claim(Props.WM_IMPORT_URL, "https://nl.wikipedia.org/w/index.php?title=Lijst_van_seizoenen_van_Zomergasten&oldid=56861509")
    ]

def match_seasons():
    PATH = str(Path(__file__).parent)
    seasons = Knead(PATH + "/data/zomergasten/seasons.csv").data()
    episodes = Knead(PATH + "/data/zomergasten/episodes.csv").data()
    skiplist = Skiplist(PATH + "/skiplists/zomergasten-seasons.txt")

    def get_season_by_year(year):
        for season in seasons:
            if season["year"] == year:
                return season

        return None

    prev_ep = None
    next_ep = None
    cur_year = "1988"
    ep_index = 1

    for index, episode in enumerate(episodes):
        ep_qid = episode["item"]
        ep_year = episode["year"]
        ep_title = episode["itemLabel"]
        season = get_season_by_year(ep_year)
        season_qid = season["item"]
        season_title = season["itemLabel"]

        if skiplist.has(ep_qid):
            print(f"{ep_qid} ({ep_title}) in skiplist, skipping")
            if season["year"] != cur_year:
                print("reset")
                ep_index = 1
                cur_year = season["year"]

            prev_ep = episode
            ep_index += 1

            continue

        if season["year"] != cur_year:
            ep_index = 1
            cur_year = season["year"]

        try:
            next_ep = episodes[index + 1]
        except:
            next_ep = None

        print("---" * 20)
        print(f"{ep_qid} - {ep_title} / #{ep_index} {season_qid} {season_title}")
        print(f"{prev_ep} / {next_ep}")
        print("---" * 20)
        print()

        item = WikidataItem(ep_qid)

        item.add_item_claim(Props.SEASON, season_qid,
            qualifiers = [
                item.get_string_claim(Props.SERIES_ORDINAL, str(ep_index))
            ]
        )

        if prev_ep:
            item.add_item_claim(Props.FOLLOWS, prev_ep["item"])

        if next_ep:
            item.add_item_claim(Props.FOLLOWED_BY, next_ep["item"])

        skiplist.add(ep_qid)

        prev_ep = episode
        ep_index += 1

def create_seasons():
    PATH = str(Path(__file__).parent)
    seasons = Knead(PATH + "/data/zomergasten/zomergasten.json").data()

    # Sort seasons by season_nr
    seasons.sort(key = lambda i:i["season_nr"])

    for season in seasons:
        season_nr = season["season_nr"]
        print("----" * 20)
        print()
        print(f"Handling season #{season_nr}")

        year = season["year"]
        presenter_name = season["presenter"]["title"]
        presenter_qid = season["presenter"]["qid"]
        episodes_count = len(season["guests"])

        if season_nr < 4:
            print("Existing season, skipping")
            continue

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

        # sys.exit()

def create_episodes():
    PATH = str(Path(__file__).parent)
    seasons = Knead(PATH + "/data/zomergasten/zomergasten.json").data()

    # Sort seasons by season_nr
    seasons.sort(key = lambda i:i["season_nr"])
    episode_nr = 0

    for season in seasons:
        print()
        print(f"Handling season #{season['season_nr']}")

        handle_season(season)

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
            date = parse_isodate(guest["date_parsed"])

            if episode_nr < 8:
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

if __name__ == "__main__":
    match_seasons()