import os
import json
from collections import Counter
from datetime import datetime
from urllib.parse import urljoin
import just
import pandas as pd

from nostalgia.utils import parse_price
from nostalgia.times import tz
from nostalgia.nlp import nlp
from nostalgia.ndf import NDF

from auto_extract import parse_article
from nostalgia.sources.web.get_keywords_for_product import get_keywords_for_product

from nostalgia.cache import get_cache

CACHE = get_cache("linked_offers")


def getter(dc, key, default=None):
    res = dc.get(key, default)
    if isinstance(res, list):
        res = res[0]
    elif isinstance(res, dict):
        res = json.dumps(res)
    return res


from natura import Finder

finder = Finder()


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
        if y.get("@type") != "Product":
            continue
        offers = y.get("offers", [])
        if isinstance(offers, dict):
            offers = [offers]
        brand = y.get("brand", {})
        if isinstance(brand, dict):
            brand = brand.get("name")
        for offer in offers:
            currency = offer.get('priceCurrency')
            if currency is None:
                continue
            price = offer.get("price") or offer.get("lowPrice")
            price = parse_price(price)
            if price is None or price == 0:
                continue
            name = getter(y, "name")
            if isinstance(name, list):
                name = "".join(name[:1])
            data = {
                "currency": currency,
                "price": price,
                "name": name,
                "origin": art.url,
                "image": getter(y, "image"),
                "brand": brand,
                "description": getter(y, "description"),
                "source": "jsonld",
            }
            return data


def deeper_price_md(art):
    data = None
    for y in art.microdata:
        tp = str(y.get("type", ""))
        if not tp.endswith("/Product"):
            continue
        props = y.get("properties")
        if props is None:
            continue
        name = y.get("properties", {}).get("name") or " ".join(art.title.split())
        if isinstance(name, list):
            name = name[0]
        offers = y.get("properties", {}).get("offers", {})
        offers = props.get("offers", [])
        if isinstance(offers, dict):
            offers = [offers]
        for offer in offers:
            offer = offer.get("properties", offer)
            price = offer.get("price") or offer.get("lowPrice")
            price = parse_price(price)
            if price is None or price == 0:
                continue
            currency = offer.get("priceCurrency")
            if currency is None:
                continue
            brand = y.get("brand") or props.get("brand") or offer.get("brand")
            if isinstance(brand, dict):
                brand = brand.get("properties", {}).get("name")
            image = y.get("image") or props.get("image") or offer.get("image")
            if isinstance(image, list):
                image = image[0]
            if isinstance(image, dict):
                prop = image.get("properties", image)
                image = [v for k, v in prop.items() if "url" in k.lower()]
                if image:
                    image = image[0]
            description = (
                y.get("description") or props.get("description") or offer.get("description")
            )
            if isinstance(description, list):
                description = description[0]
            elif isinstance(description, dict):
                description = json.dumps(description)
            return {
                "currency": currency,
                "price": price,
                "name": name,
                "origin": art.url,
                "image": urljoin(art.url, image),
                "brand": brand,
                "description": description,
                "source": "md",
            }


def get_linked_data_md(art):
    data = None
    for y in art.microdata:
        props = y.get("properties")
        if props is None:
            continue
        tp = str(y.get("type", ""))
        if tp.endswith("/Offer") or tp.endswith("/AggregateOffer"):
            price = props.get("price") or props.get("lowPrice")
            price = parse_price(price)
            if price is None or price == 0:
                continue
            currency = props.get("priceCurrency")
            if currency is None:
                continue
            return {
                "currency": currency,
                "price": price,
                "name": " ".join(art.title.split()),
                "origin": art.url,
                "image": getter(y, "image"),
                "brand": None,
                "description": y.get("description"),
                "source": "md",
            }

        if tp.endswith("/Product"):
            data = deeper_price_md(art)
            if data is not None:
                return data
            continue
        offers = props.get("offers", [])
        if isinstance(offers, dict):
            offers = [offers]
        brand = props.get("brand", {})
        if isinstance(brand, dict):
            brand = brand.get("properties", {}).get("name")
        for offer in offers:
            offer_properties = offer.get("properties")
            if offer_properties is None:
                continue
            currency = offer_properties.get('priceCurrency')
            if currency is None:
                continue
            price = offer_properties.get("price") or offer_properties.get("lowPrice")
            price = parse_price(price)
            if price is None or price == 0:
                continue
            data = {
                "currency": currency,
                "price": price,
                "name": "".join(props.get("name", "")),
                "origin": art.url,
                "image": getter(props, "image"),
                "brand": brand,
                "description": getter(props, "description"),
                "source": "md",
            }
            return data


def get_linked_amazon(art):
    if "www.amazon.com" not in str(art.url):
        return None
    for x in ["account", "cart"]:
        if x in art.url:
            return None
    paths = [
        "//span[@id='priceblock_ourprice']",
        "//div[@id='buyNewSection']",
        "//form//span[contains(@class, 'offer-price')]",
        "//div[@id='olp-upd-new']//span/a",
        "//div[@id='olp-upd-used']//span/a",
        "//div[@id='olp_feature_div']//span/a",
        "//span[contains(@class, 'header-price')]",
    ]
    price = None
    for path in paths:
        res = art.tree.xpath(path)
        if res:
            price = res[0].text_content()
            break
    if price is not None:
        brand = art.tree.xpath("//a[@id='bylineInfo']")
        brand = brand[0].text_content() if brand else None
        if brand is None:
            br = art.tree.xpath("//div[@id='bylineInfo']")
            if br:
                brand = " ".join(br[0].text_content().split()[1:])
        features = art.tree.xpath("//div[@id='feature-bullets']")
        features = features[0].text_content() if features else None
        data = {
            "currency": "USD",
            "price": max([x.value for x in finder.findall(price)]),
            "name": " ".join(art.title.split()),
            "origin": art.url,
            "image": None,
            "brand": brand,
            "description": features,
            "source": "custom_amazon",
        }
        return data


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
    linked_data = get_linked_amazon(art)
    if linked_data is None:
        linked_data = get_linked_data_md(art)
        if linked_data is None:
            linked_data = get_linked_data_jd(art)
    CACHE[path] = linked_data
    return linked_data


class Offers(NDF):
    vendor = "web"

    keywords = [
        "product",
        "offer",
        "office",
        "did i see",
        "did i look",
        "did i search",
        "looked at",
        "searched for",
        "did i google",
        "cost",
    ]
    nlp_columns = ["name", "brand", "keywords"]
    selected_columns = ["time", "name", "price", "url"]

    @nlp("end", "how much")
    def sum(self):
        return self.price.sum()

    @classmethod
    def object_to_row(cls, obj):
        row = get_linked_data(obj)
        if row is not None:
            row["time"] = datetime.fromtimestamp(float(obj["time"]), tz=tz)
            row["url"] = obj["url"]
            row["path"] = obj["path"]
            if row.get("name"):
                row["keywords"] = " ".join([x[0] for x in get_keywords_for_product(row["name"])])
            else:
                row["keywords"] = ""
            if "image" in row:
                img = row["image"]
                row["image"] = img if isinstance(img, str) or img is None else img["url"]
            return row

    @classmethod
    def load(cls, file_path="~/nostalgia_data/meta.jsonl", nrows=None, **kwargs):
        offers = cls.load_object_per_newline(file_path, nrows)
        return cls(offers)
