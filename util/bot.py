from dataknead import Knead
from util.wikidata import WikidataItem, Query
from util.skiplist import Skiplist
from util.utils import dd
import sys

class BotJob:
    def __init__(self, data, item = None):
        self.is_aborted = False
        self.data = data
        self.item = item

    def abort(self, message):
        print(f"Abort: {message}")
        self.is_aborted = True

    def create_item(self, summary, labels, descriptions = None, aliases = None):
        if self.item:
            raise Exception("Job already has an item")

        print(f"Creating new item")

        dd({
            "summary" : summary,
            "labels" : labels,
            "descriptions" : descriptions,
            "aliases" : aliases
        })

        try:
            self.item = WikidataItem(
                summary = summary,
                labels = labels,
                descriptions = descriptions,
                aliases = aliases
            )
        except Exception as e:
            print("Excepting while creating new item", e)

        print("Okay, created a new item")

    def has_prop(self, pid):
        claims = self.item.get_claims()
        return pid in claims

class CreateBot:
    def __init__(self, botid, datapath, run_once = False, key = "id"):
        print(f"Setting up new bot '{botid}'")
        print(f"Data path: {datapath}")

        self.id = botid
        self.run_once = run_once
        self.skiplist = Skiplist(f"projects/skiplists/{self.id}.txt")
        self.key = key
        self.data = Knead(datapath).data()

    def iterate(self):
        for index, item in enumerate(self.data):
            if self.key not in item or item[self.key] == "":
                print(f"This item has no key, skipping, {item}")
                continue

            item_id = item[self.key]

            print()
            print(f"#{index + 1} / {len(self.data)} / id:{item_id}")
            dd(item)
            print()

            if self.skiplist.has(item_id):
                print(f"{item_id} in skiplist, skipping")
                continue

            job = BotJob(data = item)
            yield job

            if job.is_aborted:
                continue

            if not job.item:
                raise Exception("Still no item for this job, aborting")

            self.skiplist.add(item_id)

            if self.run_once:
                print("Only running once...")
                sys.exit()

        print("Bot is done")

class Bot:
    def __init__(self, botid, datapath = None, sparql = None, run_once = False, qid_key = "qid"):
        print(f"Setting up new bot '{botid}'")

        if (not datapath) and (not sparql):
            raise Error("No datapath and no sparql")

        self.id = botid
        self.run_once = run_once
        self.skiplist = Skiplist(f"projects/skiplists/{self.id}.txt")

        if datapath:
            self.data = Knead(datapath, has_header = True).data()
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