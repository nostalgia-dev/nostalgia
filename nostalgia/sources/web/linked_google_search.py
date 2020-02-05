import just

import pandas as pd
import lxml.html

from nostalgia.cache import get_cache
from nostalgia.ndf import NDF

from datetime import datetime
from nostalgia.times import tz


CACHE = get_cache("linked_google_search")


def get_linked_data(x):
    path = x["path"]
    if path in CACHE:
        return CACHE[path]
    try:
        html = just.read(path)
    except EOFError:
        CACHE[path] = None
        return None
    if not html.strip():
        CACHE[path] = None
        return None
    tree = lxml.html.fromstring(html)
    res = tree.xpath("//input[@name='q' and @type='text']")
    if not res:
        linked_data = None
    else:
        linked_data = {"title": res[0].value}
    CACHE[path] = linked_data
    return linked_data


class GoogleSearch(NDF):
    vendor = "web"
    keywords = ["search"]
    nlp_columns = ["title"]
    selected_columns = ["time", "title", "url"]

    @classmethod
    def object_to_row(cls, obj):
        if "google" not in str(obj["url"]) or "/search" not in str(obj["url"]):
            return None
        row = get_linked_data(obj)
        if row is not None:
            row["time"] = datetime.fromtimestamp(float(obj["time"]), tz=tz)
            row["path"] = obj["path"]
            row["keywords"] = ""
            return row

    @classmethod
    def load(cls, file_path="~/nostalgia_data/meta.jsonl", nrows=None):
        data = cls.load_object_per_newline(file_path, nrows)
        # google pages found more often?
        data = data[data.title != data.title.shift(1)]
        return cls(data)
