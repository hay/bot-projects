# Add missing country and administrative division based on coordinates
from util.bot import Bot
from util.wikidata import Props, Items

# Add country=nl to architectural structures with coordinates in a 5km radius from Dam square
def add_nl_to_amsterdam():
    SPARQL = """
    select ?qid where {
      hint:Query hint:optimizer "None".

      wd:Q839050 wdt:P625 ?damCoord.
      service wikibase:around {
        ?qid wdt:P625 ?coord.
        bd:serviceParam wikibase:center ?damCoord;
                        wikibase:radius "5".
      }

      minus { ?qid wdt:P17 []. }

      ?qid wdt:P31/wdt:P279* wd:Q811979
    }
    """

    bot = Bot("add_nl_to_amsterdam", run_once = False , sparql = SPARQL)

    for job in bot.iterate():
        if job.item.has_prop(Props.COUNTRY):
            print("Has property, skipping")
            continue

        job.item.add_item_claim(
            Props.COUNTRY, Items.NETHERLANDS,
            references = [
                job.item.get_item_claim(
                    Props.BASED_ON_HEURISTIC, Items.DEDUCED_FROM_COORDINATES
                )
            ]
        )

if __name__ == "__main__":
    add_nl_to_amsterdam()