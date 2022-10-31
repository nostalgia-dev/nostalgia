# ensure ~/nostalgia_data/input exists (e.g. "mkdir -p ~/nostalgia_data/input" on linux)
# goto https://shazam.com/myshazam
# open network tab
# login
# search for url containing "discovery"
# right click and copy as curl and replace limit=20 with limit=2000
# take that curl command and add the following: > ~/nostalgia_data/input/shazam.json and hit return
# -----
# new version is to ask for an export
import os
import pandas as pd
import just
from nostalgia.ndf import NDF
from nostalgia.times import datetime_from_timestamp, parse_datetime


class Bashhub(NDF):
    @classmethod
    def handle_dataframe_per_file(cls, data, _file_path):
        data = data.dropna()
        data["exit_status"] = data["exit_status"].astype(int)
        data = data.assign(time=[parse_datetime(x.replace(" UTC", "Z")) for x in data.created])
        data.rename(columns={"command": "title"}, inplace=True)
        data = cls(data[[x for x in data.columns if "id" not in x]])

    @classmethod
    def load(cls, nrows=None, from_cache=True, **kwargs):
        for x in just.glob("~/nostalgia_data/input/bashhub_*.csv"):
            df = cls(cls.load_data_file_modified_time(x, nrows=nrows, from_cache=from_cache))
            df["exit_status"] = df["exit_status"].astype(int)
            return df

    @property
    def successful(self):
        return self.query("exit_status == 0")

    @property
    def failed(self):
        return self.query("exit_status != 0")
