# goto https://shazam.com/myshazam
# open network tab
# login
# search for url containing "discovery"
# right click and copy as curl and replace limit=20 with limit=2000
# take that curl command and add the following: > shazam.json and hit return

import just
import pandas as pd
from nostalgia.base_df import DF
import pytz
from datetime import datetime
from nostalgia.nlp import nlp
from nostalgia.utils import tz


class Shazam(DF):
    @classmethod
    def load(cls, file_path, nrows=None):
        shazam = pd.DataFrame(
            [
                (
                    datetime.fromtimestamp(
                        x["timestamp"] // 1000, tz=pytz.timezone(x["timezone"])
                    ).astimezone(tz),
                    x["track"]["heading"]["title"],
                    x["track"]["heading"]["subtitle"],
                )
                for x in just.read(file_path)["tags"]
            ],
            columns=["time", "title", "artist"],
        )
        return cls(shazam)
