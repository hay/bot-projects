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

        if req.status_code != 200:
            raise Exception(f"Invalid status code: {req.status_code}")

        return req.json()

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

        if "query" not in data:
            raise Exception("No query")

        if "categorymembers" not in data["query"]:
            raise Exception("No categorymembers")

        self.data = data["query"]["categorymembers"]