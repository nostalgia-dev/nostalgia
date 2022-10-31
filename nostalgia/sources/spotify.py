from datetime import timedelta

import just
import pandas as pd

from nostalgia.ndf import NDF
from nostalgia.times import parse_datetime, tz


class Spotify(NDF):
    vendor = "spotify"
    ingest_settings = {
        "ingest_glob": "~/Downloads/my_spotify_data.zip",
        "recent_only": False,
        "delete_existing": False,
    }

    @classmethod
    def process_row(cls, x: dict) -> dict:
        return {
            "time_start": parse_datetime(x["endTime"]).replace(tzinfo=tz) - timedelta(milliseconds=x["msPlayed"]),
            "time_end": parse_datetime(x["endTime"]).replace(tzinfo=tz),
            "title": x["trackName"],
            "artist": x["artistName"],
            "seconds": x["msPlayed"] / 1000,
        }

    @classmethod
    def load(cls, nrows=None):
        files = "~/nostalgia_data/input/spotify/MyData/StreamingHistory*.json"
        lists_of_data = [[cls.process_row(x) for x in file_data] for _fname, file_data in just.multi_read(files)]
        df = pd.DataFrame(sum(lists_of_data, []))
        return cls(df)
