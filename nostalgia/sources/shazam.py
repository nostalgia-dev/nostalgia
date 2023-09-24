# ensure ~/nostalgia_data/input exists (e.g. "mkdir -p ~/nostalgia_data/input" on linux)
# -----
# new version is to ask for an export: https://www.shazam.com/privacy/login/download
# ---
# new incomplete version, you can find the only the date (not time) using CSV
# --
# oldest version, not working now
# goto https://shazam.com/myshazam
# login if needed
# open network tab
# login
# search for url containing "discovery"
# right click and copy as curl and replace limit=20 with limit=2000
# take that curl command and add the following: > ~/nostalgia_data/input/shazam.json and hit return
import os
import pandas as pd
import just
from nostalgia.ndf import NDF
from nostalgia.times import datetime_from_timestamp, parse_datetime


class Shazam(NDF):
    @classmethod
    def load(cls, nrows=None, from_cache=True, **kwargs):
        return cls(
            cls.latest_file_is_historic(
                "~/Downloads/shazamlibrary*.csv",
                "~/nostalgia_data/input/SyncedShazams.csv",
                "~/Downloads/SyncedShazams.csv",
                nrows=nrows,
                from_cache=from_cache,
            )
        )

    @classmethod
    def handle_dataframe_per_file(cls, data, file_path):
        if "SyncedShazams" in file_path:
            data["time"] = [parse_datetime(x) for x in data.date]
        elif "shazamlibrary" in file_path:
            data = pd.read_csv(file_path, skiprows=1)
            data["time"] = [parse_datetime(x + "+00:00") for x in data.TagTime]
            data["title"] = data.Title
            data["artist"] = data.Artist
        return data[["time", "title", "artist"]]
