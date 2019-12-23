import json
from datetime import datetime
import just
import pandas as pd

from nostalgia.times import tz

from auto_extract import parse_article

from nostalgia.cache import get_cache
from nostalgia.ndf import NDF

from nostalgia.utils import normalize_name

CACHE = get_cache("linked_events")


def getter(dc, key, default=None):
    res = dc.get(key, default)
    if isinstance(res, list):
        res = res[0]
    elif isinstance(res, dict):
        res = json.dumps(res)
    return res


def get_linked_data_jd(art):
    data = None
    try:
        jdata = art.jsonld
    except json.JSONDecodeError:
        return None
    for y in jdata:
        if not y:
            continue
        if isinstance(y, list):
            y = y[0]
        if y.get("@type") != "Event":
            continue
        return {
            'description': getter(y, "description"),
            'startDate': getter(y, "startDate"),
            'endDate': getter(y, "endDate"),
            'location': getter(y, "location"),
            "source": "jsonld",
        }


def get_linked_data_md(art):
    data = None
    for y in art.microdata:
        props = y.get("properties")
        if props is None:
            continue
        tp = str(y.get("type", ""))
        if not tp.endswith("/Event"):
            continue
        return {
            "startDate": getter(props, "startDate"),
            "endDate": getter(props, "endDate"),
            "description": getter(props, "description"),
            "name": "".join(getter(props, "name", "")),
            "location": getter(props, "location"),
            "source": "md",
        }


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
    art = parse_article(html, x["url"])
    linked_data = get_linked_data_md(art)
    if linked_data is None:
        linked_data = get_linked_data_jd(art)
    CACHE[path] = linked_data
    return linked_data


class Events(NDF):
    vendor = "web"

    @classmethod
    def object_to_row(cls, obj):
        row = get_linked_data(obj)
        if row is not None:
            row["time"] = datetime.fromtimestamp(float(obj["time"]), tz=tz)
            row["url"] = obj["url"]
            row["path"] = obj["path"]
            row["keywords"] = ""
            return row

    @classmethod
    def load(cls, file_path="~/nostalgia_data/meta.jsonl", nrows=None, **kwargs):
        events = cls.load_object_per_newline(file_path, nrows)
        return cls(events)
