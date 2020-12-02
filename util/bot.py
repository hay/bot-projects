from dataknead import Knead
from util.wikidata import WikidataItem
from util.skiplist import Skiplist
import sys

class BotJob:
    def __init__(self, data, item):
        self.data = data
        self.item = item


class Bot:
    def __init__(self, botid, datapath, run_once = False):
        print(f"Setting up new bot '{botid}' with datapath '{datapath}'")
        self.id = botid
        self.datapath = datapath
        self.data = Knead(self.datapath).data()
        self.run_once = run_once
        self.skiplist = Skiplist(f"projects/skiplists/{self.id}.txt")

    def iterate(self):
        for index, item in enumerate(self.data):
            qid = item["qid"]
            print(f"#{index + 1} / #{len(self.data)} / {qid}")
            print(f"Data: {item}")
            print()

            if self.skiplist.has(qid):
                print(f"{qid} in skiplist, skipping")
                continue

            wd_item = WikidataItem(qid)
            job = BotJob(data = item, item = wd_item)
            yield job

            self.skiplist.add(qid)

            if self.run_once:
                print("Only running once...")
                sys.exit()