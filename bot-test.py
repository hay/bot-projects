# Just a testbot to see if things are still working
from util.wikidata import Props, WikidataItem
import pywikibot

def main():
    # Mariniersbrug
    qid = "Q2461755"
    item = WikidataItem(qid)
    claims = item.get_claims()
    monument_id = claims[Props.RIJKSMONUMENT_ID]
    print(f"monument_id: {monument_id}")

if __name__ == "__main__":
    main()