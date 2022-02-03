from util.config import WEBHOOK_ENDPOINT
from dataknead import Knead
from datetime import datetime
from pathlib import Path
from urllib import parse
import json
import os
import requests

# site = pywikibot.Site("wikidata", "wikidata")
# test_site = pywikibot.Site("test", "wikidata")

PATH = os.path.realpath(
    os.path.join(
        os.getcwd(), os.path.dirname(__file__)
    )
)

def chunk(lst, size):
    return [ lst[i:i + size] for i in range(0, len(lst), size) ]

def dd(obj):
    print(json.dumps(obj, indent = 4))

def parse_urlargs(url):
    query = parse.parse_qs(parse.urlparse(url).query)
    return {k:v[0] if v and len(v) == 1 else v for k,v in query.items()}

def send_im_message(message):
    print(f"Sending IM message '{message}'")

    req = requests.get(WEBHOOK_ENDPOINT, params = {
        "event" : "im_message",
        "value1" : "HuskyBot",
        "value2" : message
    })

def sleep(seconds = 20):
    # Sleep for a bit
    print("Sleep for %s seconds" % seconds)
    time.sleep(seconds)

class Datasheet:
    def __init__(self, path, index):
        self.path = path
        self.data = Knead(path, has_header = True).data()
        self.keys = {i[index]:i for i in self.data}

    def __getitem__(self, key):
        if key in self.keys:
            return self.keys[key]
        else:
            return None

    def append(self, row):
        self.data.append(row)
        self.save()

    def save(self):
        print("Saving")
        Knead(self.data).write(self.path)