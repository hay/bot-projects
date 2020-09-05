from .utils import chunk
from .mediawiki import MediawikiApi
from .mediawiki import CategoryMembers as MediawikiCategoryMembers
from bs4 import BeautifulSoup
from dataknead import Knead
import json
import unicodedata
import requests

def get_permalink(lang, title):
    api = MediawikiApi("wikipedia", lang)

    data = api.call({
        "action" : "query",
        "prop" : "info",
        "titles" : title
    })

    pages = data["query"]["pages"]

    if "-1" in pages:
        raise Exception("Page not found")

    val = pages[list(pages.keys())[0]]
    curid = val["pageid"]
    oldid = val["lastrevid"]

    return f"https://{lang}.wikipedia.org/w/index.php?curid={curid}&oldid={oldid}"

def get_qids(lang, titles):
    api = MediawikiApi("wikipedia", lang)
    print(f"Getting {len(titles)} titles")
    qids = {}

    for title_set in chunk(titles, 50):
        data = api.call({
            "action" : "query",
            "prop" : "pageprops",
            "titles" : "|".join(titles)
        })

        pages = data["query"]["pages"]

        if "-1" in pages:
            raise Exception("Page not found")

        val = pages[list(pages.keys())[0]]
        curid = val["pageid"]
        oldid = val["lastrevid"]

    return qids

class CategoryMembers(MediawikiCategoryMembers):
    def __init__(self, lang, category):
        super().__init__("wikipedia", lang, category)

class InfoboxBox:
    # lol
    def __init__(self, el, endpoint):
        self.el = el
        self.endpoint = endpoint
        self.box = {}
        self.parse()

    def __repr__(self):
        return self.box

    def __str__(self):
        return json.dumps(self.box)

    def get_text(self, key):
        if key in self.box:
            return self.box[key]["fulltext"]
        else:
            return None

    def parse(self):
        for tr in self.el.select("tr"):
            cells = tr.select("td")

            if len(cells) != 2:
                # Probably a heading or something
                continue

            key = cells[0].get_text().strip()
            val = cells[1]

            self.box[key] = {
                "fulltext" : val.get_text().strip(),
                "links" : [self.parse_link(l) for l in val.select("a")]
            }

    def parse_link(self, link):
        href = link.get("href", None)

        return {
            "fullhref" : f"{self.endpoint}{href}",
            "href" : href,
            "link" : href.replace("/wiki/", ""),
            "text" : link.get_text().strip(),
            "title" : link.get("title", None)
        }

class Infobox(MediawikiApi):
    def __init__(self, lang, page):
        super().__init__("wikipedia", lang)
        self.pageTitle = page
        self.infoboxes = []
        self.apidata = None

    def get_data(self, apidata = None):
        if apidata:
            print("Using cached data")
            self.parsed = apidata["parse"]
        else:
            print("Doing an API request")
            self.call_api()

        self.parse()

        return {
            "infoboxes" : self.infoboxes,
            "parsed" : self.parsed
        }

    def call_api(self):
        data = self.call({
            "action" : "parse",
            "page" : self.pageTitle,
            "format" : "json"
        })

        if "parse" not in data:
            raise Exception("No parse data found")

        self.apidata = data
        self.parsed = data["parse"]

    def parse(self):
        soup = BeautifulSoup(self.parsed["text"]["*"], "html.parser")
        boxes = soup.select(".infobox")
        self.infoboxes = [InfoboxBox(el, self.endpoint) for el in boxes]

if __name__ == "__main__":
    print(get_permalink("nl", "Noorderkerzk"))