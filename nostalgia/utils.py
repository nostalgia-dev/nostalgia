import os
import sys
import re
import just
import pandas as pd
import numpy as np
from pytz import timezone
from metadate import parse_date, Units
from datetime import datetime
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
import dateutil

from tok import word_tokenize

if sys.argv[-1].endswith("ipython"):
    pd.set_option("display.precision", 10)
    pd.set_option("precision", 10)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.max_colwidth', -1)

has_alpha = re.compile("[a-zA-Z]")
num = re.compile("[0-9]")


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


tz = timezone('Europe/Amsterdam')
utc = timezone('UTC')


def format_latlng(latlng):
    if isinstance(latlng, str):
        latlng = latlng.replace(",", " ").split()
    return "{:0.7f}, {:0.7f}".format(*map(float, latlng))


def last_days(days):
    return now(days=days).replace(hour=0, minute=0, second=0, microsecond=0)


def today():
    return last_days(0)


def yesterday():
    return last_days(1)


def last_week():
    return now(days=7).replace(hour=0, minute=0, second=0, microsecond=0)


def last_month():
    return now(months=1).replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def last_year():
    return now(years=1).replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)


def now(**kwargs):
    return datetime.now(tz=tz) - relativedelta(**kwargs)


# from textsearch import TextSearch, TSResult


def week_ago(weeks):
    begin = now(days=7 * weeks).date()
    end = now(days=7 * (weeks - 1)).date()
    return begin, end


def days_ago(days):
    begin = now(days=days).date()
    end = now(days=days - 1).date()
    return lambda: (begin, end)


def months_ago(months):
    begin = now(months=months).date()
    end = now(months=months - 1).date()
    return lambda: (begin, end)


def years_ago(years):
    begin = now(years=years).date()
    end = now(years=years - 1).date()
    return lambda: (begin, end)


def in_month(month):
    year = now().year - 1 if now().month <= month else now().year
    return lambda: (
        datetime(year, month, 1).date(),
        datetime(year, month, 1).date() + relativedelta(month=month + 1),
    )


def in_year(year):
    return lambda: (datetime(year, 1, 1).date(), datetime(year + 1, 1, 1).date())


def try_date(x, min_level=None, max_level=None):
    try:
        # apparently one col is dayfirst, the other isnt
        mps = parse_date(x, multi=True)
        for mp in mps:
            if mp is None:
                continue
            if Units.DAY not in mp.levels:
                continue
            if min_level is not None and mp.min_level > min_level:  # above minute level
                continue
            if max_level is not None and mp.max_level < max_level:
                continue
            date = mp.start_date
            if date.tzinfo is None:
                date = tz.localize(date)
            return date
    except:
        return None


def view(path):
    from requests_viewer import view_html

    view_html(just.read(path))


def parse_date_tz(text):
    mp = parse_date(text)
    if mp is not None:
        if mp.start_date.tzinfo is None:
            mp.start_date = tz.localize(mp.start_date)
        if mp.end_date.tzinfo is None:
            mp.end_date = tz.localize(mp.end_date)
        return mp


def datetime_tz(*args):
    return tz.localize(datetime(*args))


def datetime_from_timestamp(x, tzone=tz, divide_by_1000=True):
    if divide_by_1000:
        x = x // 1000
    if isinstance(tzone, str):
        tzone = timezone(tzone)
    x = datetime.fromtimestamp(x, tz=tzone)
    if tzone != tz:
        x = x.astimezone(tz)
    return x


def datetime_from_format(s, fmt, in_utc=False):
    base = datetime.strptime(s, fmt)
    if in_utc:
        return utc.localize(base).astimezone(tz)
    else:
        return tz.localize(base)


def haversine(lon1, lat1, lon2, lat2):
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


def read_array_of_dict_from_json(fname, key_name=None, nrows=None):
    if nrows is None:
        if not key_name:
            return pd.read_json(fname, lines=fname.endswith(".jsonl"))
        else:
            return pd.DataFrame(just.read(fname)[key_name])

    import ijson

    with open(just.make_path(fname)) as f:
        parser = ijson.parse(f)
        capture = False
        rows = []
        row = {}
        map_key = ""
        num = 0
        for prefix, event, value in parser:
            if num > nrows:
                break
            if prefix == key_name and event == "start_array":
                capture = True
            if not capture:
                continue
            if event == "start_map":
                continue
            elif event == "map_key":
                map_key = value
            elif event == "end_map":
                rows.append(row)
                row = {}
                num += 1
            elif map_key:
                row[map_key] = value
        return pd.DataFrame(rows)


def normalize_name(name):
    return re.sub("([A-Z])", r"_\1", name).lstrip("_").lower()


def print_mixed(df):
    from collections import Counter

    for x in df:
        ls = [y for y in df[x] if isinstance(y, list)]
        if ls:
            print(ls[0])
        dc = [y for y in df[x] if isinstance(y, dict)]
        if dc:
            print(dc[0])
        print(x, Counter([type(y) for y in df[x]]))
        print()


def take(key):
    def fn(value):
        if isinstance(value, list):
            value = value[0]
        if isinstance(value, dict):
            value = value.get(key)
        return value

    return fn


def clean_df(df, dc):
    for k, v in dc.items():
        df[k] = [v(x) for x in df[k]]
    return df


def load_entry():
    import sys

    just.write("", "~/.nostalgia/__init__.py")

    sys.path.append(os.path.expanduser("~/.nostalgia/"))
    import nostalgia_entry

    return nostalgia_entry
