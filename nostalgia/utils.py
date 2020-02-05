import os
import sys
import re
import just
import pandas as pd
import numpy as np


from tok import word_tokenize

if sys.argv[-1].endswith("ipython"):
    pd.set_option("display.precision", 10)
    pd.set_option("precision", 10)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.max_colwidth', -1)

has_alpha = re.compile("[a-zA-Z]")
num = re.compile("[0-9]")


class MockCredentials:
    def __init__(self, credential_dict):
        for k, v in credential_dict.items():
            setattr(self, k, v)


def get_tokens(sentence, lower=True):
    if not isinstance(sentence, str):
        return []
    if sentence is None:
        return []
    return [
        x
        for x in word_tokenize(sentence, to_lower=lower)
        if len(x) > 2 and has_alpha.search(x) and not num.search(x)
    ]


def get_token_set(iterable_of_sentences, lower=True):
    words = set()
    for x in iterable_of_sentences:
        words.update(get_tokens(x, lower))
    return words


def format_latlng(latlng):
    if isinstance(latlng, str):
        latlng = latlng.replace(",", " ").split()
    return "{:0.7f}, {:0.7f}".format(*map(float, latlng))


def view(path):
    if path.endswith("gz"):
        from requests_viewer import view_html

        view_html(just.read(path))
    else:
        import webbrowser

        webbrowser.open("file://" + path)


def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    currently in meters
    """

    # Convert decimal degrees to Radians:
    lon1 = np.radians(lon1)
    lat1 = np.radians(lat1)
    lon2 = np.radians(lon2)
    lat2 = np.radians(lat2)

    # Implementing Haversine Formula:
    dlon = np.subtract(lon2, lon1)
    dlat = np.subtract(lat2, lat1)

    a = np.add(
        np.power(np.sin(np.divide(dlat, 2)), 2),
        np.multiply(
            np.cos(lat1), np.multiply(np.cos(lat2), np.power(np.sin(np.divide(dlon, 2)), 2))
        ),
    )
    c = np.multiply(2, np.arcsin(np.sqrt(a)))
    # km
    r = 6371
    # meters
    r *= 1000

    return c * r


seps = [".", ","]


def parse_price(x):
    if x is None:
        return None
    if isinstance(x, list):
        x = "".join(x)
    if isinstance(x, (int, float)):
        if x != x:
            return None
        return x
    x = x.replace(" ", "")
    try:
        return float(x)
    except ValueError:
        pass
    result = np.nan
    for decimal_sep in seps:
        for thousand_sep in seps:
            if decimal_sep == thousand_sep:
                continue
            regex = "^[+-]?"
            regex += "[0-9]{1,3}"
            regex += "(?:[" + thousand_sep + "]?[0-9]{3})*"
            regex += "([" + decimal_sep + "][0-9]{1,2})?"
            regex += "$"
            if re.match(regex, x):
                try:
                    result = float(x.replace(thousand_sep, "").replace(decimal_sep, "."))
                except ValueError:
                    continue
                return result
    return result


def normalize_name(name):
    return re.sub("([A-Z])", r"_\1", name).lstrip("_").lower()


def clean_df(df, dc):
    for k, v in dc.items():
        df[k] = [v(x) for x in df[k]]
    return df


def load_entry():
    import sys

    just.write("", "~/nostalgia_data/__init__.py")

    sys.path.append(os.path.expanduser("~/nostalgia_data/"))
    import nostalgia_entry

    return nostalgia_entry
