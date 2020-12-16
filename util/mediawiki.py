import requests

class MediawikiApi:
    def __init__(self, project, lang):
        self.lang = lang
        self.endpoint = f"https://{lang}.{project}.org"
        self.api_endpoint = f"{self.endpoint}/w/api.php"

    def call(self, params):
        # For the lazy peoples
        if "format" not in params:
            params["format"] = "json"

        req = requests.get(self.api_endpoint, params = params)
        print(f"[MediawikiApi] did call {req.url}")

        if req.status_code != 200:
            raise Exception(f"Invalid status code: {req.status_code}")

        return req.json()

    def check_query(self, key, data):
        if "query" not in data:
            raise Exception("No query")

        if key not in data["query"]:
            raise Exception("No categorymembers")

    def iterate_list(self, list_key, continue_key, payload):
        is_continue = None

        while True:
            if is_continue:
                payload[continue_key] = is_continue

            data = self.call(payload)
            self.check_query(list_key, data)

            for page in data["query"][list_key]:
                yield page

            if "continue" in data:
                is_continue = data["continue"][continue_key]
            else:
                print("Seems we're done!")
                break

class AllPages(MediawikiApi):
    def __init__(self, endpoint):
        self.api_endpoint = endpoint

    def iterate_pages(self):
        apcontinue = None

        while True:
            payload = {
                "action" : "query",
                "list" : "allpages",
                "apfilterredir" : "nonredirects",
                "aplimit" : 500,
                "format" : "json"
            }

            if apcontinue:
                payload["apcontinue"] = apcontinue

            data = self.call(payload)
            self.check_query("allpages", data)

            for page in data["query"]["allpages"]:
                yield page

            if "continue" in data:
                apcontinue = data["continue"]["apcontinue"]
            else:
                print("seems we're done")
                break

class CategoryMembers(MediawikiApi):
    def __init__(self, project, lang, category):
        super().__init__(project, lang)
        self.category = category
        self.data = []
        self.populate()

    def members(self):
        for item in self.data:
            title = item["title"]

            yield {
                "fullhref" : f"{self.endpoint}/wiki/{title}",
                "href" : f"/wiki/{title}",
                "pageid" : item["pageid"],
                "title" : item["title"],
            }

    def populate(self):
        data = self.call({
            "action" : "query",
            "list" : "categorymembers",
            "cmtitle" : self.category,
            "cmlimit" : 500
        })

        self.check_query("categorymembers", data)
        self.data = data["query"]["categorymembers"]