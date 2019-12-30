import re
import just
import numpy as np
import pandas as pd
from nostalgia.ndf import NDF
import lxml.html
import diskcache
from auto_extract import parse_article
from nostalgia.nlp import nlp
from nostalgia.cache import get_cache
from nostalgia.data_loading import read_array_of_dict_from_json
from nostalgia.times import datetime_from_timestamp

CACHE = get_cache("chrome_history")


# def destroy_tree(tree):
#     node_tracker = {tree: [0, None]}

#     for node in tree.iterdescendants():
#         parent = node.getparent()
#         node_tracker[node] = [node_tracker[parent][0] + 1, parent]

#     node_tracker = sorted(
#         [(depth, parent, child) for child, (depth, parent) in node_tracker.items()],
#         key=lambda x: x[0],
#         reverse=True,
#     )

#     for _, parent, child in node_tracker:
#         if parent is None:
#             break
#         parent.remove(child)

#     del tree


def get_title(x):
    if not x.get("domain"):
        return ""
    if x["path"] in CACHE:
        return CACHE[x["path"]]
    # tree = lxml.html.fromstring(just.read(x["path"]))
    # title = tree.xpath("/html/head/title/text()") or tree.xpath("//title/text()") or [""]
    # destroy_tree(tree)
    # title = title[0]
    match = re.search("<title>([^<]+)</title", just.read(x["path"]), re.MULTILINE)
    title = match.groups()[0].strip() if match is not None else ""
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
        x["time"] = datetime_from_timestamp(x["time"])
        x["title"] = get_title(x)
        return x

    @classmethod
    def load(cls, file_path="~/nostalgia_data/meta.jsonl", nrows=None, **kwargs):
        web_history = cls.load_object_per_newline(file_path, nrows)
        return cls(web_history)
