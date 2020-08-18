# Wikimedia Bot Projects
This repo contains code i'm using for my Wikimedia bots, mostly the one on [Wikidata](https://www.wikidata.org/wiki/Special:Contributions/HuskyBot).

Some general remarks:
* Scripts prefixed with `bot` are bots i run with Pywikibot.
* Scripts prefixed with `scrape` are standalone Python scripts that are used for data cleanup and scraping.
* `util` contains code i reuse in many of these projects. The `wikidata.py` is especially interesting, this contains a general class i use for all my Wikidata bots.
* `skiplists` is a directory i use to story lists for items i've already edited, not pushed to Git.
* `data` contains the scraped data, but this is not pushed to Git.

## License
MIT &copy; [Hay Kranen](http://www.haykranen.nl)