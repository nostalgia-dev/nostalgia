import just
import numpy as np
import pandas as pd
from nostalgia.base_df import DF
from datetime import datetime
from nostalgia.utils import tz
import lxml.html
import diskcache
from auto_extract import parse_article
from nostalgia.nlp import nlp
from nostalgia.cache import get_cache
from nostalgia.utils import read_array_of_dict_from_json, datetime_from_format
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


class WebHistory(DF):
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
    def load(cls, file_path="~/.nostalgia/meta.jsonl", nrows=None, **kwargs):
        web_history = cls.load_object_per_newline(file_path, nrows)
        web_history["time"] = web_history.time.apply(lambda x: datetime.fromtimestamp(float(x), tz))
        return cls(web_history)


def custom_parse(x):
    try:
        return datetime_from_format(x, "%Y-%m-%dT%H:%M:%SZ", in_utc=True)
    except:
        return datetime_from_format(x, "%Y-%m-%dT%H:%M:%S.%fZ", in_utc=True)


# class PageVisit(DF):
#     @classmethod
#     def handle_dataframe_per_file(cls, data, file_path):
#         data["time"] = pd.to_datetime(data.time_usec, utc=True, unit="us").dt.tz_convert(tz)
#         del data["time_usec"]
#         return data

#     # refactor to use "google_takeout" as target
#     @classmethod
#     def load(
#         cls,
#         file_path="~/Downloads/Takeout_02-09-2018/Chrome/BrowserHistory.json",
#         nrows=None,
#         from_cache=True,
#         **kwargs
#     ):
#         page_visit = cls.load_data_file_modified_time(file_path, nrows=nrows, from_cache=from_cache)
#         if nrows is not None:
#             page_visit = page_visit.iloc[:5]
#         return cls(page_visit)


class PageVisit(DF):
    @classmethod
    def handle_dataframe_per_file(cls, data, file_path):
        data["time"] = [custom_parse(x) for x in data["time"]]
        return data

    # refactor to use "google_takeout" as target
    @classmethod
    def load(cls, takeout_folder, nrows=None, from_cache=True, **kwargs):
        if not takeout_folder.endswith("/"):
            takeout_folder += "/"
        file_path = takeout_folder + "My Activity/Chrome/My Activity.json"

        page_visit = cls.load_data_file_modified_time(file_path, nrows=nrows, from_cache=from_cache)
        if nrows is not None:
            page_visit = page_visit.iloc[:5]
        return cls(page_visit)
