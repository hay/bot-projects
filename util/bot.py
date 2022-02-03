from dataknead import Knead
from util.wikidata import WikidataItem, Query
from util.skiplist import Skiplist
from util.utils import dd, send_im_message
import pywikibot
import requests
import sys

class BotJob:
    def __init__(self, data, item = None, dry_run = False):
        self.is_aborted = False
        self.data = data
        self.dry_run = dry_run
        self.item = item

    def abort(self, message):
        print(f"Abort: {message}")
        self.is_aborted = True

    # Lifted from https://github.com/multichill/toollabs/blob/master/bot/wikidata/artdatabot.py
    def archive_url(self, url):
        """
        Links to paintings are subject to link rot. When creating a new item, have the Wayback Machine make a snapshot.
        That way always have a copy of the page we used to source a bunch of statements.

        See also https://www.wikidata.org/wiki/Wikidata:WikiProject_sum_of_all_paintings/Link_rot
        """

        print(f"Backing up to the Wayback Machine: {url}")
        wayback_url = f"https://web.archive.org/save/{url}"

        try:
            requests.post(wayback_url)
        except requests.exceptions.RequestException:
            print(f"Wayback Machine save failed")

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
            print("Got an exception while creating item", e)
            # Re-raise
            raise(e)

        print("Okay, created a new item")

    def has_prop(self, pid):
        claims = self.item.get_claims()
        return pid in claims

    def set_item_by_qid(self, qid):
        self.item = WikidataItem(qid)

class CreateBot:
    def __init__(
        self, botid, datapath, key = "id",
        required_fields = [],
        empty_check = lambda x: x == None
    ):
        print(f"Setting up new bot '{botid}'")
        print(f"Data path: {datapath}")

        # Parse command line arguments and play it safe, assume
        # run_once and dry_run by default, except when they're
        # disabled
        args = pywikibot.handle_args()
        run_once = "-run-all" not in args
        dry_run = "-run-live" not in args
        print(f"Running once? {run_once}")
        print(f"Dry run? {dry_run}")

        self.id = botid
        self.run_once = run_once
        self.dry_run = dry_run
        self.skiplist = Skiplist(f"projects/skiplists/{self.id}.txt")
        self.key = key
        self.current_job = None
        self.data = Knead(datapath).data()
        self.required_fields = required_fields
        self.empty_check = empty_check

    def has_required_fields(self, item):
        for field in self.required_fields:
            if self.empty_check(item[field]):
                print(f"'{field}' is empty, aborting")
                return False

        return True

    def iterate(self):
        for index, item in enumerate(self.data):
            if self.key not in item or item[self.key] == "":
                print(f"This item has no key, skipping, {item}")
                continue

            item_id = item[self.key]

            print()
            print(f"#{index + 1} / {len(self.data)} / id:{item_id}")

            if self.skiplist.has(item_id):
                print(f"{item_id} in skiplist, skipping")
                continue

            dd(item)
            print()

            if not self.has_required_fields(item):
                continue

            if self.dry_run:
                print("Dry run, skip the actual creating")
                continue

            job = BotJob(data = item)
            self.current_job = job
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
        send_im_message(f"CreateBot finished running: {self.id}")

class Bot:
    def __init__(
        self, botid, datapath = None, sparql = None, run_once = False,
        qid_key = "qid",
        empty_check = lambda x: x == None or x == ""
    ):
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
            if self.qid_key not in item or self.empty_check(item[self.qid_key]):
                print(f"This item has no QID, skipping, {item}")
                continue

            qid = item[self.qid_key]
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

        send_im_message(f"Bot finished running: {self.id}")