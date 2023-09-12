import re
import os
import pandas as pd
import just
from nostalgia.times import tz
from nostalgia.times import parse_datetime
from nostalgia.interfaces.places import PlacesInterface


def get_city_country(formatted_address):
    formatted_address = re.sub("\d,\d", "", formatted_address)
    if formatted_address.count(",") == 0:
        return "", formatted_address
    if formatted_address.count(",") == 1:
        x, country = formatted_address.split(", ")
    elif formatted_address.count(",") == 2:
        _, x, country = formatted_address.split(", ")
    elif formatted_address.count(",") == 3:
        _, x, _, country = formatted_address.split(", ")
    elif formatted_address.count(",") == 4:
        if formatted_address.endswith("Nederland"):
            _, _, _, x, country = formatted_address.split(", ")
        else:
            _, x, _, _, country = formatted_address.split(", ")
    elif formatted_address.count(",") == 5:
        _, x, _, _, _, country = formatted_address.split(", ")
    elif formatted_address.count(",") == 6:
        x, _, _, _, _, _, country = formatted_address.split(", ")
    else:
        print("zzz", formatted_address)
    if "ة" in formatted_address:
        return "", ""
    if country[:1].isdigit():
        country = " ".join(country.split()[1:])
    if x[:1].isdigit():
        x = " ".join(x.split()[1:])
    if country in {"Nederland", "Netherlands"}:
        return " ".join(x.split()[1:]), "Netherlands"
    if country in {"Deutschland", "Germany"}:
        return x, "Germany"
    if country in {"Norge", "Norway"}:
        return x, "Norway"
    if country in {"Magyarország", "Hungary"}:
        return x, "Hungary"
    if country in {"Espanya", "España", "Spain"}:
        return x, "Spain"
    if country in {"Österreich", "Austria"}:
        return x, "Austria"
    if country in {"Portugal"}:
        return x, "Portugal"
    if country in {"België", "Belgium"}:
        return x, "Portugal"
    if country in {"Costa Rica"}:
        return x, "Costa Rica"
    if country in {"Србија", "Serbia", "Srbija"}:
        if x[-1:].isdigit():
            return " ".join(x.split()[:-1]), "Serbia"
        return x, "Serbia"
    if country == "USA":
        return x, country
    return "", ""
    # raise ValueError(f"No idea how to parse {formatted_address}")


def extract_place(x: dict):
    loc, dur = x["location"], x["duration"]
    if "latitudeE7" in loc:
        lat = loc["latitudeE7"] / 1e7
        lon = loc["longitudeE7"] / 1e7
    elif "otherCandidateLocations" in x:
        lat = pd.Series([y["latitudeE7"] for y in x["otherCandidateLocations"]]).mean() / 1e7
        lon = pd.Series([y["longitudeE7"] for y in x["otherCandidateLocations"]]).mean() / 1e7
    else:
        lat, lon = 0, 0
    city, country = get_city_country(loc["address"]) if "address" in loc else ("", "")
    return {
        "start": parse_datetime(dur["startTimestamp"]),
        "end": parse_datetime(dur["endTimestamp"]),
        "name": loc.get("name", loc.get("address", "")),
        "lat": lat,
        "lon": lon,
        "city": city,
        "country": country,
        "formatted_address": loc.get("address"),
    }


def extract_activity(x):
    loc, dur = x.get("location", x["startLocation"]), x["duration"]
    end_loc = x.get("endLocation", {})
    return {
        "start": parse_datetime(dur["startTimestamp"]),
        "end": parse_datetime(dur["endTimestamp"]),
        "name": x.get("activityType", ""),
        "lat": loc.get("latitudeE7", 0) / 1e7,
        "lon": loc.get("longitudeE7", 0) / 1e7,
        "lat_end": end_loc.get("latitudeE7", 0) / 1e7,
        "lon_end": end_loc.get("longitudeE7", 0) / 1e7,
        "distance": x.get("distance"),
    }


class GooglePlaces(PlacesInterface):
    nlp_columns = ["name", "city", "country"]
    selected_columns = ["date", "name", "city", "_office_hours"]

    @classmethod
    def handle_json_per_file(cls, fname):
        data = just.read(fname)
        activities = [x.get("activitySegment") for x in data["timelineObjects"] if x.get("activitySegment")]
        places = [x.get("placeVisit") for x in data["timelineObjects"] if x.get("placeVisit")]
        tmp = [extract_activity(x) for x in activities] + [extract_place(x) for x in places]
        return pd.DataFrame(tmp)

    @classmethod
    def load(cls, nrows=None, **kwargs):
        df = cls.load_dataframe_per_json_file(
            "~/nostalgia_data/input/google/Takeout/Location History/Semantic Location History/*/*.json",
            nrows=nrows,
            json=True,
        )
        return cls(df)
