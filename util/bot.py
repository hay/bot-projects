from dataknead import Knead
from util.wikidata import WikidataItem, Query
from util.skiplist import Skiplist
import sys

class BotJob:
    def __init__(self, data, item):
        self.data = data
        self.item = item

class Bot:
    def __init__(self, botid, datapath = None, sparql = None, run_once = False, qid_key = "qid"):
        print(f"Setting up new bot '{botid}'")

        if (not datapath) and (not sparql):
            raise Error("No datapath and no sparql")

        self.id = botid
        self.run_once = run_once
        self.skiplist = Skiplist(f"projects/skiplists/{self.id}.txt")

        if datapath:
            self.data = Knead(datapath).data()
        elif sparql:
            query = Query(sparql)
            self.data = list(query.iter_results())

    def iterate(self):
        for index, item in enumerate(self.data):
            if "qid" not in item or item["qid"] == "":
                print(f"This item has no QID, skipping, {item}")
                continue

            qid = item["qid"]
            print()
            print(f"#{index + 1}/{len(self.data)} / {qid}")
            print(f"Data: {item}")
            print()

            if self.skiplist.has(qid):
                print(f"{qid} in skiplist, skipping")
                continue

            try:
                wd_item = WikidataItem(qid)
            except Exception as e:
                print(f"Exception, not yielding this job: {e}")
                continue

            job = BotJob(data = item, item = wd_item)
            yield job

            self.skiplist.add(qid)

            if self.run_once:
                print("Only running once...")
                sys.exit()