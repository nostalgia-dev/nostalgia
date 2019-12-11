import os
import just
from datetime import datetime
import pandas as pd
from nostalgia.utils import tz, format_latlng
from nostalgia.base_df import DF


class Pics(DF):
    @classmethod
    def load(cls, takeout_folder, nrows=None):
        prefix = os.path.join(takeout_folder, "Google Photos/*/*")
        pics = []
        nrows = nrows or float("inf")
        rows = 0
        for fname in just.glob(prefix):
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
