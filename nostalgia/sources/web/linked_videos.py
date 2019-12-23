import re
import just

import urllib.parse

import pandas as pd

from auto_extract import parse_article

from nostalgia.cache import get_cache

from datetime import datetime
from nostalgia.times import tz
from nostalgia.ndf import NDF
from nostalgia.nlp import nlp

CACHE = get_cache("linked_data_videos")


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
    if "youtube" not in art.domain:
        return None
    title = re.sub(" - YouTube$", "", art.tree.xpath("//title/text()")[0])
    if title == "YouTube":
        CACHE[path] = None
        return None
    if not title:
        return None
    vc = art.tree.xpath("//span[contains(@class, 'view-count')]/text()")
    vc = re.sub("[^0-9]", "", vc[0]) if vc else None
    watch_part = urllib.parse.parse_qs(urllib.parse.urlparse(x["url"]).query)["v"]
    if watch_part:
        image = "http://i3.ytimg.com/vi/{}/maxresdefault.jpg".format(watch_part[0])
    else:
        image = None
    channel = art.tree.xpath("//ytd-video-owner-renderer//a/text()")
    if not channel:
        channel = art.tree.xpath("//ytd-channel-name//a/text()")
    channel = " ".join(channel)
    linked_data = {
        "title": title,
        "type": "video",
        "source": "youtube",
        "image": image,
        "view_count": vc,
        "channel": channel,
    }
    CACHE[path] = linked_data
    return linked_data


class Videos(NDF):
    vendor = "web"

    keywords = ["watch", "viewers", "listen", "video", "music video", "youtube"]
    nlp_columns = ["title", "channel"]
    selected_columns = ["time", "title", "view_count", "url"]

    @classmethod
    def object_to_row(cls, obj):
        url = str(obj["url"])
        if "youtub" not in url or "watch" not in url or "search_query" in url:
            return None
        row = get_linked_data(obj)
        if row is not None:
            row["time"] = datetime.fromtimestamp(float(obj["time"]), tz=tz)
            row["url"] = obj["url"]
            row["path"] = obj["path"]
            row["keywords"] = ""
            return row

    @classmethod
    def load(cls, fname="~/nostalgia_data/meta.jsonl", nrows=None):
        data = cls.load_object_per_newline(fname, nrows)
        return cls(data)

    @nlp("end", "how many views")
    def sum(self):
        return self.view_count.sum()
