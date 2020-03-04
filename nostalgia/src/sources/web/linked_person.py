import json
from datetime import datetime
import just
import pandas as pd

from nostalgia.times import tz

from auto_extract import parse_article

from nostalgia.cache import get_cache
from nostalgia.ndf import NDF

from nostalgia.utils import normalize_name

CACHE = get_cache("linked_person")


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
        if y.get("@type") != "Person":
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
        if not tp.endswith("/Person"):
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


class Person(NDF):
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
        person = cls.load_object_per_newline(file_path, nrows)
        return cls(person)


if __name__ == "__main__":
    person = Person.load(nrows=5)

    # https://schema.org/Blog
    # "http://schema.org/blogPost"
    # http://schema.org/WebPage # http://schema.org/BlogPosting

    # exlclude http://schema.org/QAPage

    it = 0
    imo = 0
    nice = 0
    wrong = 0
    from collections import Counter
    import just

    c = Counter()

    for x in just.iread("/home/pascal/nostal_tmp/person.jsonl"):
        if "/Person" in (str(x.get("microdata"))):
            it += 1
            y = x
            score = 0
            mc_count = 0
            for mc in y["microdata"]:
                if mc.get("type") in [
                    'http://schema.org/ImageObject',
                    'http://schema.org/QAPage',
                    'http://schema.org/Movie',
                    'http://schema.org/videoObject',
                    'http://schema.org/Organization',
                    'http://schema.org/VideoObject',
                    'http://schema.org/Question',
                    'http://schema.org/CreativeWork',
                    'http://schema.org/Code',
                ]:
                    continue
                mc_count += 1
                for opt in [
                    'mc["properties"]["author"]',
                    'mc["properties"]["author"]["properties"]["name"]',
                    'mc["properties"]["author"]["value"]',
                    'mc["properties"]["author"][0]["value"]',
                    'mc["properties"]["author"][0]["properties"]["name"]',
                    'mc["properties"]["author"]["properties"]["author"]["properties"]["name"][0]',
                    'mc["properties"]["creator"]["properties"]["name"]',
                    'mc["properties"]["author"][0]["value"]',
                    'mc["properties"]["mainEntity"]["properties"]["author"]["properties"]["name"]',
                    'mc["properties"]["blogPost"]["properties"]["author"]["properties"]["name"]',
                ]:
                    try:
                        x = eval(opt).strip()
                        if not x or x.startswith("http") or "\n" in x:
                            continue
                        print(x)
                        score += 1
                        c[mc["type"].split("/")[-1]] += 1
                        break
                    except KeyboardInterrupt:
                        "a" + 1
                    except:
                        pass
            if mc_count and score == 0:
                if len(y["microdata"]) == 1 and list(y["microdata"][0]) == ["value"]:
                    continue
                wrong += 1
                continue
            if score:
                nice += 1
