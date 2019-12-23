import just
import numpy as np
import pandas as pd
from nostalgia.ndf import NDF
from datetime import datetime
from nostalgia.times import tz
import lxml.html
import diskcache
from auto_extract import parse_article
from nostalgia.nlp import nlp
from nostalgia.cache import get_cache
from nostalgia.utils import read_array_of_dict_from_json
from nostalgia.source_to_fast import get_newline_count, save_newline_count, save, load

CACHE = get_cache("chrome_history")


def get_title(x):
    if not x.get("domain"):
        return ""
    if x["path"] in CACHE:
        return CACHE[x["path"]]
    tree = lxml.html.fromstring(just.read(x["path"]))
    title = tree.xpath("/html/head/title/text()") or tree.xpath("//title/text()") or [""]
    title = title[0]
    CACHE[x["path"]] = title
    return title


class WebHistory(NDF):
    keywords = ["website", "page", "site", "web history", "page history", "visit"]
    nlp_columns = ["domain", "domain_and_suffix", "title"]
    # selected_columns = ["time", "name", "price", "url"]

    @nlp("filter", "watch", "see", "view")
    def shows(self):
        return self[np.array(self.title.str.extract("Watch (.+) Full Movie").notna())]

    @nlp("filter", "show", "series")
    def series(self):
        shows = self.shows()
        return shows[shows.title.str.contains("Season")]

    @nlp("filter", "movies", "films")
    def movies(self):
        shows = self.shows()
        return shows[~shows.title.str.contains("Season")]

    @classmethod
    def object_to_row(cls, x):
        import tldextract

        if x["url"]:
            extract = tldextract.extract(x["url"])
            x["domain"] = extract.domain
            x["domain_and_suffix"] = extract.domain + "." + extract.suffix
        x["url"] = x["url"] or "_".join(x["path"].split("_")[1:])
        x["title"] = get_title(x)
        return x

    @classmethod
    def load(cls, file_path="~/nostalgia_data/meta.jsonl", nrows=None, **kwargs):
        web_history = cls.load_object_per_newline(file_path, nrows)
        web_history["time"] = web_history.time.apply(lambda x: datetime.fromtimestamp(float(x), tz))
        return cls(web_history)
