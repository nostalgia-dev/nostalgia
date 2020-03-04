# ensure ~/nostalgia_data/input exists (e.g. "mkdir -p ~/nostalgia_data/input" on linux)
# goto https://shazam.com/myshazam
# open network tab
# login
# search for url containing "discovery"
# right click and copy as curl and replace limit=20 with limit=2000
# take that curl command and add the following: > ~/nostalgia_data/input/shazam.json and hit return

import pandas as pd
import just
from nostalgia.ndf import NDF
from nostalgia.times import datetime_from_timestamp


class Shazam(NDF):
    @classmethod
    def load(cls, file_path="~/nostalgia_data/input/shazam.json", nrows=None):
        shazam = pd.DataFrame(
            [
                (
                    datetime_from_timestamp(x["timestamp"], x["timezone"]),
                    x["track"]["heading"]["title"],
                    x["track"]["heading"]["subtitle"],
                )
                for x in just.read(file_path)["tags"]
            ],
            columns=["time", "title", "artist"],
        )
        return cls(shazam)
