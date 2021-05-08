import pywikibot
import requests

class Props:
    APPLIES_TO_PART = "P518"
    ARCHITECT = "P84"
    BAG_BUILDING = "P5208"
    BAG_PUBSPACE = "P5207"
    BASED_ON_HEURISTIC = "P887"
    CAPACITY = "P1083"
    CATALOG = "P972"
    CATALOG_CODE = "P528"
    CCONTEXT = "P8296"
    CCREATOR = "P6241"
    COLLECTION = "P195"
    COMMEMORATES = "P547"
    COORDINATES = "P625"
    COORDINATES_POV = "P1259"
    COUNTRY = "P17"
    COUNTRY_OF_ORIGIN = "P495"
    CREATOR = "P170"
    DESCRIBED_AT_URL = "P973"
    DATE_OF_BIRTH = "P569"
    DATE_OF_DEATH = "P570"
    DISSOLVED = "P576"
    DISTRIBUTED_BY = "P750"
    EDUCATED_AT = "P69"
    END_TIME = "P582"
    FOLLOWS = "P155"
    FOLLOWED_BY = "P156"
    GENDER = "P21"
    GENRE = "P136"
    GTAA = "P1741"
    HAS_WORKS_IN_COLLECTION = "P6379"
    IMAGE = "P18"
    IMPORTED_FROM = "P143"
    INCEPTION = "P571"
    INFERRED_FROM = "P3452"
    INSCRIPTION = "P1684"
    INSTANCE_OF = "P31"
    INVENTORY_NR = "P217"
    ISBN_10 = "P957"
    ISBN_13 = "P212"
    LANGUAGE_SHOW = "P364"
    LANGUAGE_WORK = "P407"
    LEGISLATIVE_BODY = "P194"
    LOCATED_IN = "P131"
    LOCATED_IN_ADMIN = "P131"
    LOCATED_ON_STREET = "P669"
    MATERIAL_USED = "P186"
    NAME = "P2561"
    NAMED_AFTER = "P138"
    NR_OF_EPISODES = "P1113"
    NR_OF_RECORDS = "P4876"
    NR_OF_PAGES = "P1104"
    NR_OF_SEATS = "P1410"
    OBJECT_HAS_ROLE = "P3831"
    OCCUPATION = "P106"
    OFFICIAL_WEBSITE = "P856"
    ORIGINAL_BROADCASTER = "P449"
    OWNED_BY = "P127"
    PART_OF = "P361"
    PART_OF_SERIES = "P179"
    PAYMENT_ACCEPTED = "P2851"
    PHONE_NUMBER = "P1329"
    PLACE_OF_BIRTH = "P19"
    PLACE_OF_DEATH = "P20"
    POINT_IN_TIME = "P585"
    POSTAL_CODE = "P281"
    PRECISION = "P1480"
    PRESENTER = "P371"
    PUB_DATE = "P577"
    REF_URL = "P854"
    RELIGION = "P140"
    RELIWIKI = "P8897"
    RETRIEVED = "P813"
    RKD_ARTISTS = "P650"
    RKD_IMAGES = "P350"
    SEASON = "P4908"
    SERIES_ORDINAL = "P1545"
    SIG_EVENT = "P793"
    SONNEVELD = "P8911"
    START_TIME = "P580"
    STATED_IN = "P248"
    STREET_ADDRESS = "P6375"
    STREET_KEY = "P1945"
    STREET_NUMBER = "P670"
    STUDENT_OF = "P1066"
    TALK_SHOW_GUEST = "P5030"
    TITLE = "P1476"
    WM_IMPORT_URL = "P4656"
    ZIP = "P281"

class TestProps:
    CATALOG = "P73793"
    COORDINATES = "P125"
    COUNTRY = "P17"
    INSTANCE_OF = "P82"
    LOCATED_IN = "P769"
    NAMED_AFTER = "P74108"
    POSTAL_CODE = "P73778"
    STREET_KEY = "P73779"

class Items:
    ADAMLINK = "Q54371815"
    ALBUM_COVER = "Q1333350"
    AMSTERDAM_MUNIP = "Q9899"
    BAG_BOOK = "Q52084601"
    BRASS = "Q39782"
    BRIDGE = "Q12280"
    BUILDING_EXPANSION = "Q19841649"
    CHURCH_BUILDING = "Q16970"
    CIRCA = "Q5727902"
    DAM_SQUARE = "Q839050"
    DEDUCED_FROM_COORDINATES = "Q96623327"
    DUTCH = "Q7411"
    FEMALE = "Q6581072"
    GUNTER_DEMNIG = "Q195796"
    H_SIERADEN = "Q89929597"
    HUMAN = "Q5"
    JAPANESE_WIKIPEDIA = "Q177837"
    JEWEL_DESIGNER = "Q2519376"
    MALE = "Q6581097"
    MONUMENT_REGISTER = "Q7477362"
    MUSEUM = "Q33506"
    MUSEUMKAART = "Q2237462"
    MUSICBRAINZ = "Q14005"
    MUSICAL_MAPS = "Q80590524"
    NETHERLANDS = "Q55"
    NIJMEGEN_MUNIP = "Q47887"
    NL_LOWER_HOUSE = "Q233262"
    NPO = "Q15991875"
    OPENING_CEREMONY = "Q3010369"
    PARK = "Q22698"
    PRIVATE_COLLECTION = "Q768717"
    PUBLIC_ART = "Q557141"
    PUBLIC_ART_IN_NIJMEGEN = "Q105138564"
    RECONSTRUCTION = "Q1370468"
    RELIWIKI = "Q1920729"
    RIJKSMONUMENT_ID = "Q103567620"
    RKD = "Q758610"
    SCULPTURE = "Q860861"
    SQUARE = "Q174782"
    STOLPERSTEIN = "Q26703203"
    STOLPERSTEINE_PROJECT = "Q314003"
    STREET = "Q79007"
    TALK_SHOW = "Q622812"
    TUNNEL = "Q44377"
    TV_SERIES_EPISODE = "Q21191270"
    TV_SERIES_SEASON = "Q3464665"
    UDS_DOC = "Q101684921"
    VPRO = "Q1282036"
    WIKIPEDIA_NL = "Q10000"
    WP_ARTICLE_PAGE = "Q50081413"
    ZOMERGASTEN = "Q2330424"

class TestItems(Items):
    BAG_BOOK = "Q56403"
    SQUARE = "Q17478"

"""
If an item is iterable, return it as it is, otherwise convert to list
"""
def to_iterable(val):
    try:
        iter(val)
    except TypeError:
        return [val]
    else:
        return val

class Query:
    ENDPOINT = "https://query.wikidata.org/sparql"
    NAMESPACE = "http://www.wikidata.org/entity/"

    def __init__(self, query):
        self.query = query
        self.items = []
        self.results = []

    @classmethod
    def fromClaim(cls, prop, value):
        query = f"select ?item where {{ ?item wdt:{prop} {value}. }}"
        print(f"Query: <{query}>")
        return cls(query)

    @classmethod
    def getQid(cls, uri):
        return uri.replace(cls.NAMESPACE, "")

    def iter_results(self):
        results = self._run()

        for result in results:
            item = {}

            for key, data in result.items():
                val = data.get("value", None)

                if isinstance(val, str) and val.startswith("http://www.wikidata.org/entity/"):
                    val = self.getQid(val)

                item[key] = val

            yield item

    def _run(self):
        print(f"Running a SPARQL Query")

        req = requests.get(self.ENDPOINT, params = {
            "format" : "json",
            "query" : self.query
        })

        print(f"Did SPARQL request: <{req.url}>")

        data = req.json()

        return data["results"]["bindings"]

    def run(self):
        self.results = self._run()

        self.items = [
            self.getQid(i["item"]["value"]) for i in self.results
        ]

        print(f"Got {len(self.items)} items")

def claim_exists(prop, value):
    query = Query.fromClaim(prop, value)
    query.run()
    return len(query.items) > 0

class Done:
    def __init__(self, path):
        self.path = path

        with open(self.path) as f:
            self.qids = [qid.strip() for qid in f.read().splitlines()]

    def add(self, qid):
        if not self.has(qid):
            with open(self.path, "a") as f:
                f.write(qid + "\n")

    def has(self, qid):
        return qid in self.qids

class WikidataItem:
    def __init__(
        self,
        qid = None, labels = None, descriptions = None, summary = None,
        follow_redirect = False, aliases = None
    ):
        self.site = pywikibot.Site("wikidata", "wikidata")
        self.repo = self.site.data_repository()

        if not qid and not labels:
            raise TypeError("Labels are required when creating a new item")

        if not qid:
            print("Creating item")
            self.item = pywikibot.ItemPage(self.site)

            if labels:
                self.edit_labels(labels, summary)

            if descriptions:
                self.edit_descriptions(descriptions, summary)

            if aliases:
                self.edit_aliases(aliases, summary)

            qid = self.item.getID()
            print("Item created: %s" % qid)

        self.qid = qid
        print(f"Getting item {self.qid}")
        self.item = pywikibot.ItemPage(self.repo, self.qid)

        if follow_redirect and self.item.isRedirectPage():
            # Check if this is a redirect, and if so, get the real item
            print("This is a redirect item, get the target")
            self.item = self.item.getRedirectTarget()
        elif self.item.isRedirectPage():
            raise Exception("Redirect page, and follow redirect is not one. Can't edit")

        self.item.get()

        self.properties = self.item.claims.keys()

        if labels:
            self.edit_labels(labels, summary)

        if descriptions:
            self.edit_descriptions(descriptions, summary)

        if aliases:
            self.edit_aliases(aliases, summary)

    def add_alias(self, alias, lang):
        aliases = self.get_aliases(lang)

        if not aliases:
            aliases = []

        aliases.append(alias)

        print(f"Setting these aliases: {aliases})")

        self.edit_aliases({
            lang : aliases
        }, f"Adding an extra alias to this item: '{alias}' (language: {lang})")

    def add_claim(self, claim, qualifiers = None, references = None):
        print(f'Adding claim {claim}')
        self.item.addClaim(claim)

        # Note that qualifiers need to be added *after* the claim has been
        # added!
        if qualifiers:
            print(f"Adding qualifiers to claim {qualifiers}")
            for q in to_iterable(qualifiers):
                claim.addQualifier(q)

        if references:
            print(f"Adding references to this claim: {references}")
            claim.addSources(to_iterable(references))

    def add_commonsmedia(self, prop, filename, qualifiers = None, references = None):
        claim = pywikibot.Claim(self.repo, prop)
        commons = pywikibot.Site("commons", "commons")
        imagelink = pywikibot.Link(filename, source = commons, defaultNamespace = 6)
        image = pywikibot.FilePage(imagelink)

        if image.isRedirectPage():
            image = pywikibot.page.ImagePage(image.getRedirectTarget())

        if not image.exists():
            raise Exception(f"Could not find image: {filename}")

        claim.setTarget(image)
        self.add_claim(claim, qualifiers, references)

    def add_coordinate(self, prop, latlon, precision = 0.00001, qualifiers = None, references = None):
        print(f"Adding coordinate: {prop} -> {latlon}")
        claim = self.get_coordinate(prop, latlon, precision)
        self.add_claim(claim, qualifiers, references)

    def add_item_claim(self, prop, target, qualifiers = None, references = None):
        print(f"Adding item claim: {prop} -> {target}")
        claim = self.get_item_claim(prop, target)
        self.add_claim(claim, qualifiers, references)

    def add_monoling_claim(self, prop, string, lang, qualifiers = None, references = None):
        print(f"Adding monoling claim: {prop} -> {string}@{lang}")
        claim = self.get_monoling_claim(prop, string, lang)
        self.add_claim(claim, qualifiers, references)

    def add_quantity_claim(self, prop, quantity, qualifiers = None, references = None):
        print(f"Adding quantity claim: {prop} -> {quantity}")
        claim = self.get_claim(prop, pywikibot.WbQuantity(quantity, site = self.repo))
        self.add_claim(claim, qualifiers, references)

    def add_string_claim(
        self, prop, string, qualifiers = None, references = None,
        skip_propexists = False
    ):
        if self.has_prop(prop):
            print(f"Item already has property {prop} and skip_propexists is set to True")
            return

        print(f"Adding string claim: {prop} -> {string}")
        claim = self.get_string_claim(prop, string)
        self.add_claim(claim, qualifiers, references)

    def add_time_claim(self, prop, time, qualifiers = None, references = None):
        print(f"Adding time claim: {prop} -> {time}")
        # TODO: make time more easier to enter instead of passing wbtime
        claim = self.get_claim(prop, time)
        self.add_claim(claim, qualifiers, references)

    def add_url_claim(self, prop, url, qualifiers = None, references = None):
        print(f"Adding url claim: {prop} -> {url}")
        claim = self.get_url_claim(prop, url)
        self.add_claim(claim, qualifiers, references)

    def edit_aliases(self, aliases, summary = None):
        print("Setting aliases")

        # Make sure aliases are in a list
        for key, val in aliases.items():
            if not isinstance(val, list):
                raise Exception(f"Aliases should be in a list!")

        self.item.editAliases(aliases = aliases, summary = summary)

    def edit_descriptions(self, descriptions, summary = None):
            summaryText = "Setting the descriptions"

            if summary:
                summaryText = f"{summaryText} for {summary}"

            self.item.editDescriptions(descriptions = descriptions, summary = summaryText)

    def edit_labels(self, labels, summary = None):
            self.item.editLabels(labels = labels, summary = summary)

    def get_aliases(self, lang = None):
        if lang:
            return self.item.aliases.get(lang, None)
        else:
            return self.item.aliases

    def get_claim(self, prop, target):
        print(f"Adding general claim: {prop} -> {target}")
        claim = pywikibot.Claim(self.repo, prop)
        claim.setTarget(target)
        return claim

    def get_claims(self):
        return self.item.claims

    def get_coordinate(self, prop, latlon, precision):
        print(f"Get coordinate: {prop} -> {latlon} ({precision})")

        # If latlon is a string, otherwise we assume its an iterable
        if isinstance(latlon, str):
            lat, lon = latlon.split(",")
        else:
            lat, lon = latlon[0], latlon[1]

        claim = pywikibot.Claim(self.repo, prop)
        coord = pywikibot.Coordinate(
            lat = float(lat),
            lon = float(lon),
            precision = precision,
            globe = "earth"
        )
        claim.setTarget(coord)
        return claim

    def get_descriptions(self):
        return self.item.descriptions

    def get_item_claim(self, prop, target):
        print(f"Getting item claim: {prop} -> {target}")
        claim = pywikibot.Claim(self.repo, prop)

        # Special case: 'somevalue' and 'novalue' are allowed too
        if target in ["somevalue", "novalue"]:
            claim.setSnakType(target)
        else:
            targetItem = pywikibot.ItemPage(self.repo, target)
            claim.setTarget(targetItem)

        return claim

    def get_label(self, lang):
        return self.item.labels.get(lang, None)

    def get_labels(self):
        return self.item.labels

    def get_labels_aliases(self):
        labels = set(self.item.labels.values())
        aliases = sum(self.item.aliases.values(), [])
        labels.update(set(aliases))
        return labels

    def get_monoling_claim(self, prop, string, lang):
        print(f"Get monoling claim: {prop} -> {string}@{lang}")
        claim = pywikibot.Claim(self.repo, prop)
        text = pywikibot.WbMonolingualText(string, lang)
        claim.setTarget(text)
        return claim

    def get_string_claim(self, prop, string):
        print(f"Get string claim: {prop} -> {string}")
        claim = pywikibot.Claim(self.repo, prop)
        claim.setTarget(string)
        return claim

    def get_url_claim(self, prop, url):
        print(f"Get URL claim: {prop} -> {url}")
        claim = pywikibot.Claim(self.repo, prop, datatype='url')
        claim.setTarget(url)
        return claim

    def has_itemclaim(self, prop, item):
        if prop not in self.item.claims:
            return None

        for claim in self.item.claims[prop]:
            if claim.type != "wikibase-item":
                continue

            if claim.getTarget().id == item:
                return True

        return False

    def has_prop(self, prop):
        return prop in self.item.claims

    def remove_claim_by_prop(self, prop):
        print(f"Removing item claim by prop: {prop}")
        for prop_id, claim in self.item.claims.items():
            if prop_id == prop:
                print("Found the property, removing")
                self.item.removeClaims(claim)