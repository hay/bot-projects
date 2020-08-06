from datetime import datetime
from pathlib import Path
import pywikibot, time, json, os, re

site = pywikibot.Site("wikidata", "wikidata")
test_site = pywikibot.Site("test", "wikidata")

PATH = os.path.realpath(
    os.path.join(
        os.getcwd(), os.path.dirname(__file__)
    )
)

def chunk(lst, size):
    return [ lst[i:i + size] for i in range(0, len(lst), size) ]

def wbtime_now():
    now = datetime.now()

    return pywikibot.WbTime(
        year = now.year, month = now.month, day = now.day
    )

def sleep(seconds = 20):
    # Sleep for a bit
    print("Sleep for %s seconds" % seconds)
    time.sleep(seconds)

def dd(obj):
    print(json.dumps(obj, indent = 4))