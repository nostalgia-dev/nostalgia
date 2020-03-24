import os
import requests
import dotenv
from nostalgia.cache import get_cache

CACHE = get_cache("darksky_weather")

dotenv.load_dotenv(".env")
dotenv.load_dotenv("~/nostalgia_data/.env")


def _historic_weather(latitude, longitude, epoch_time):
    q = f"{latitude},{longitude},{epoch_time}"
    if q in CACHE:
        return CACHE[q]
    key = os.environ["DARKSKY_WEATHER_KEY"]
    resp = requests.get(f"https://api.darksky.net/forecast/{key}/{q}?units=si")
    json_response = resp.json()
    if "error" not in json_response:
        CACHE[q] = json_response
    return json_response


def get_weather_at_nearest_hour(latitude, longitude, dt):
    day_timestamp = int(dt.replace(hour=0, minute=0, second=1).timestamp())
    json_response = _historic_weather(latitude, longitude, day_timestamp)
    t = dt.timestamp()
    try:
        return min([(abs(x["time"] - t), x) for x in json_response["hourly"]["data"]])[
            1
        ]
    except (IndexError, KeyError) as e:
        print("ERROR with get_weather_at_nearest_hour:", e)
        return {}


def get_weather_hourly(latitude, longitude, date):
    day_timestamp = int(date.replace(hour=0, minute=0, second=1).timestamp())
    json_response = _historic_weather(latitude, longitude, day_timestamp)
    try:
        return json_response["hourly"]["data"]
    except (IndexError, KeyError) as e:
        print("ERROR with get_weather_at_nearest_hour:", e)
        return {}
