import re
from collections import Counter
import just
import requests
from nearnlp.nearnlp import is_noun, is_verb, singularize
import functools
from tok import Tokenizer
from nltk.corpus import stopwords
from nostalgia.enrichers.google.custom_search import google_custom_search

ENGLISH_STOP = set(stopwords.words("english"))

t = Tokenizer(True)
t.drop("<b>", "remove html")
t.drop("<b/>", "remove html")

# can also use qoogle

interesting_keys = set()
for prefix in ["og:", "twitter:", ""]:
    for key in [
        "title",
        "description",
        "name",
        'manufacturer_name',
        'category_name_singular',
        'long_description',
        'snippet',
    ]:
        interesting_keys.add(prefix + key)


def recurse_json(json_data, results=None):
    if results is None:
        results = []
    if isinstance(json_data, dict):
        for k, v in json_data.items():
            if k in interesting_keys and isinstance(v, str) and v:
                results.append(v)
            elif isinstance(v, (dict, list)):
                recurse_json(v, results)
    elif isinstance(json_data, list):
        for x in json_data:
            recurse_json(x, results)
    return results


@functools.lru_cache(2000)
def get_keywords_for_product(product_string):
    # json = {"searchString": product_string}
    # res = requests.get("https://icecat.biz/search/rest/get-products-list", json=json).json()
    res = google_custom_search(product_string)
    zzz = recurse_json(res)
    c = Counter()
    for x in zzz:
        c.update(
            set(
                [
                    singularize(y.lower())
                    for y in t.word_tokenize(x)
                    if re.search("^[a-z]+$", y.lower())
                ]
            )
        )
    # print([(k,v) for k,v in c.most_common(1000) if is_noun(k) and is_verb(k)])
    return [
        x
        for i, x in enumerate(c.most_common(1000))
        if x[0] not in ENGLISH_STOP and len(x[0]) > 2 and x[1] > 1 and is_noun(x[0])
        # if a verb would occur often then probably it is still important
        and (not is_verb(x[0]) or i < 5)
    ]
