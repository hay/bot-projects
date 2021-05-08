# Add missing country and administrative division based on coordinates
from string import Template
from util.bot import Bot
from util.wikidata import Props, Items

class MissingPropBot:
    def __init__(
        self, title, prop, item, centre, radius, run_once = False
    ):
        SPARQL = Template("""
        select ?qid where {
          hint:Query hint:optimizer "None".

          wd:$centre wdt:P625 ?centre.
          service wikibase:around {
            ?qid wdt:P625 ?coord.
            bd:serviceParam wikibase:center ?centre;
                            wikibase:radius "$radius".
          }

          minus { ?qid wdt:$prop []. }

          ?qid wdt:P31/wdt:P279* wd:Q811979
        }
        """).substitute({ "centre" : centre, "radius" : radius, "prop" : prop})

        self.prop = prop
        self.item = item
        self.bot = Bot(title, run_once = run_once, sparql = SPARQL)

    def run(self):
        for job in self.bot.iterate():
            if job.item.has_prop(self.prop):
                print("Has property, skipping")
                continue

            job.item.add_item_claim(
                self.prop, self.item,
                references = [
                    job.item.get_item_claim(
                        Props.BASED_ON_HEURISTIC, Items.DEDUCED_FROM_COORDINATES
                    )
                ]
            )

# Add country=nl to architectural structures with coordinates in a 5km radius from Dam square
def add_nl_to_amsterdam():
    bot = MissingPropBot(
        "add_nl_to_amsterdam",
        run_once = False,
        prop = Props.COUNTRY,
        item = Items.NETHERLANDS,
        centre = Items.DAM_SQUARE,
        radius = 5
    )

    bot.run()

def add_munip_to_amsterdam():
    bot = MissingPropBot(
        "add_munip_to_amsterdam",
        run_once = False,
        prop = Props.LOCATED_IN_ADMIN,
        item = Items.AMSTERDAM_MUNIP,
        centre = Items.DAM_SQUARE,
        radius = 5
    )

    bot.run()

if __name__ == "__main__":
    add_nl_to_amsterdam()
    add_munip_to_amsterdam()