from datetime import datetime
import os
import requests
import diskcache
import dotenv
import hashlib
import pandas as pd
from pytz import timezone
import just
from nostalgia.times import tz
from nostalgia.utils import format_latlng
from nostalgia.cache import get_cache
from nostalgia.interfaces.places import Places


def api_call(url, params):
    key = get_hash(url, params)
    status = CACHE.get(key, {}).get("status")
    if status == "ZERO_RESULTS":
        return None
    if status == "OK":
        return CACHE[key]
    jdata = s.get(url, params=params).json()
    jdata["meta"] = {
        "time": str(datetime.utcnow()),
        "url": url,
        "params": {k: v for k, v in params.items() if k != "key"},
    }
    if jdata.get("status") == "ZERO_RESULTS":
        CACHE[key] = jdata
        return None
    if jdata.get("status") != "OK":
        print("status", url, params, key, jdata.get("status"))
        raise ValueError("not ok")
    CACHE[key] = jdata
    return jdata


def get_nearby(latlng, name, excluded_transport_names):
    latlng = format_latlng(latlng)
    if latlng == "nan, nan":
        return None
    params = {"location": latlng, "radius": 100, "key": KEY}
    if name not in excluded_transport_names:
        params["query"] = name
    return api_call(NEARBY_URL, params)


def get_nearby_results(latlng, name, excluded_transport_names):
    near = get_nearby(latlng, name, excluded_transport_names)
    if near is None:
        return None
    res = [x for x in near["results"] if name in excluded_transport_names or x["name"] == name]
    for x in res:
        if "opening_hours" in x:
            return x
    if res:
        return res[0]
    if not near["results"]:
        return None
    return near["results"][0]


def get_details(place_id):
    params = {'placeid': place_id, 'sensor': 'false', 'key': KEY}
    return api_call(DETAILS_URL, params).get("result", {})


def get_(details, *types):
    for tp in types:
        for addr in details.get('address_components', []):
            if tp in addr["types"]:
                return addr["long_name"]


def get_hash(url, params):
    data = {k: v for k, v in params.items() if k != "key"}
    data["url"] = url
    data = sorted(data.items())
    return hashlib.sha256(str(data).encode("utf8")).hexdigest()


GEOCODE_URL = "https://maps.googleapis.com/maps/api/geocode/json"


def get_address(json_response):
    for res in json_response.get("results", []):
        addr = res.get('formatted_address')
        if addr:
            return addr


def geo_get_(json_response, *types):
    for res in json_response.get("results", []):
        for tp in types:
            for addr in res.get('address_components', []):
                if tp in addr["types"]:
                    return addr["long_name"]


def geo_get_info(latlng):
    latlng = format_latlng(latlng)
    if latlng == "nan, nan":
        return None
    params = {"method": "reverse", "latlng": latlng, "key": KEY}
    json_response = api_call(GEOCODE_URL, params=params)
    city = geo_get_(json_response, "locality", "postal_town")
    # place_id = json_response.get("results", [{}])[0].get("place_id")
    country = geo_get_(json_response, "country")
    address = get_address(json_response)
    return {"city": city, "country": country, "formatted_address": address}


dotenv.load_dotenv("google/.env")
dotenv.load_dotenv(".env")

PYTHON_ENV = os.environ.get("PYTHON_ENV", "dev")
if PYTHON_ENV != "prod":
    KEY = None
else:
    KEY = os.environ.get("GOOGLE_API_KEY", None)

CACHE = get_cache("google_timeline")

DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"
NEARBY_URL = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'

s = requests.Session()
# {'Boating', 'Cycling', 'Driving', 'Flying', 'In transit', 'Moving', 'On a bus', 'On a ferry', 'On a train', 'On a tram', 'On the subway', 'Running', 'Walking'}


def get_results(latlng, name, excluded_transport_names):
    if name in excluded_transport_names:
        return geo_get_info(latlng)
    near_result = get_nearby_results(latlng, name, excluded_transport_names)
    if near_result is None:
        return None
    details = get_details(near_result["place_id"])
    if details is None:
        return None
    return {
        "city": get_(details, "locality", "postal_town"),
        "country": get_(details, "country"),
        "rating": details,
        "details_name": details.get("name"),
        "formatted_address": details.get("formatted_address"),
        'international_phone_number': details.get('international_phone_number'),
        'opening_hours': details.get('opening_hours'),
        'user_ratings_total': details.get('user_ratings_total'),
        'rating': details.get('rating'),
        'website': details.get('website'),
    }


def process(df, excluded_transport_names, home_regex, work_regex, hometown_regex):
    df["start"] = pd.to_datetime(df.start)
    df["end"] = pd.to_datetime(df.end)
    df["around_noon"] = (df.start.dt.hour < 12) & (df.end.dt.hour > 12)
    df["week"] = df.start.dt.weekday < 5
    df["city"] = df.city.fillna("")
    df["transporting"] = df.category.isin(excluded_transport_names)

    if work_regex:
        df.loc[df.name.str.contains(work_regex, regex=True, na=False), "category"] = "Work"
    if home_regex:
        df.loc[df.name.str.contains(home_regex, regex=True, na=False), "category"] = "Home"
    # if hometown_regex:
    #     df.loc[
    #         df.name.str.contains(hometown_regex, regex=True, na=False), "category"
    #     ] = "Hometown"

    df = df.sort_values("start").reset_index(drop=True)
    if "Unnamed: 0" in df.columns:
        del df["Unnamed: 0"]
    df["start"] = df["start"].dt.tz_convert(tz)
    df["end"] = df["end"].dt.tz_convert(tz)
    df.index = pd.IntervalIndex.from_arrays(df['start'], df['end'])
    return df


class GooglePlaces(Places):
    nlp_columns = ["name", "city", "country", "category", "website"]
    selected_columns = ["date", "name", "city", "_office_hours"]

    @classmethod
    def load(cls, file_glob="~/Downloads/timeline_data-*", nrows=None):
        df = pd.read_csv(max(just.glob(file_glob)), nrows=nrows)

        unique_locs = set([((y, z), x) for x, y, z in zip(df.name, df.lat, df.lon) if y != "nan"])

        excluded_transport_names = set(df[df.name == df.category].name)

        details_data = []
        for (lat, lon), name in unique_locs:
            d = get_results((lat, lon), name, excluded_transport_names)
            if d is None:
                continue
            d["lat"] = lat
            d["lon"] = lon
            d["name"] = name
            details_data.append(d)

        details_data = pd.DataFrame(details_data)

        # all_loc = df.merge(details_data, on=["name", "lat", "lon"], how="outer")
        places = df.merge(details_data, on=["name", "lat", "lon"], how="inner")

        # all_loc = process(all_loc, excluded_transport_names)

        home_regex = "|".join(cls.home)
        work_regex = "|".join(cls.work)
        hometown_regex = "|".join(cls.hometown)
        places = process(places, excluded_transport_names, home_regex, work_regex, hometown_regex)

        return cls(places)


GooglePlaces.work = ["Jibes", "Sleepboot", "De Meerpaal", "Papendorp", "Vektis", "Work "]


# at_work = places.at_work()
#
# places.travel_by_car()\
#       .duration_longer_than(minutes=30)\
#       .at_day(at_work)
#       .at_time("november 2019")\
#       .during_weekdays\

# cat_str = ", ".join(["{}: {}".format(i, x) for i, x in enumerate(places.category)])
# [places.iloc[[int(y) for y in x]] for x in re.findall(", ".join(["([0-9]+): {}".format(x) for x in pats]), cat_str)]
