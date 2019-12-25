import os
import just
from datetime import datetime
import pandas as pd
from nostalgia.times import tz
from nostalgia.utils import format_latlng
from nostalgia.sources.google import Google


class Photos(Google):
    @classmethod
    def load(cls, nrows=None):
        photo_glob = "~/nostalgia_data/input/google/Takeout/Google Photos/*/*"
        pics = []
        nrows = nrows or float("inf")
        rows = 0
        for fname in just.glob(photo_glob):
            if fname.endswith(".json"):
                continue
            try:
                meta = just.read(fname + ".json")
            except FileNotFoundError:
                continue
            if rows == nrows:
                break
            date = datetime.fromtimestamp(int(meta['photoTakenTime']['timestamp']), tz)
            lat, lon = format_latlng(
                (meta['geoData']['latitude'], meta['geoData']['longitude'])
            ).split(", ")
            title = meta["title"]
            pics.append(
                {"path": "file://" + fname, "lat": lat, "lon": lon, "title": title, "time": date}
            )
            rows += 1

        pics = pd.DataFrame(pics)
        return cls(pics)
