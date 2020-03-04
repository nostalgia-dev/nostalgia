from datetime import timedelta

import pandas as pd

from nostalgia.times import datetime_from_format
from src.common.infrastructure.utils import Functional
from src.common.meta.aspect.time import Time
from src.common.meta.aspect.title import Title
from src.common.meta.category.services.music import Music
from src.sources import Source


class Spotify(Source):

    @property
    def category(self):
        return [Music]

    @property
    def aspects(self):
        return {
            'time_start': Time,
            'time_end': Time,
            'title': Title
        }

    def ingest(self, delta_data, **kwargs):
        # how to extract and where? Download?
        return self.read_file("StreamingHistory*.json")

    @classmethod
    def load(self, data) -> pd.DataFrame:
        spotify = pd.DataFrame(
            [
                (
                    datetime_from_format(x["endTime"], "%Y-%m-%d %H:%M") - timedelta(milliseconds=x["msPlayed"]),
                    datetime_from_format(x["endTime"], "%Y-%m-%d %H:%M"),
                    x["trackName"],
                    x["artistName"],
                    x["msPlayed"] / 1000
                )
                for x in Functional.flatten(data)
            ],
            columns=["time_start", "time_end", "title", "artist", "seconds"],
        )
        return spotify




if __name__ == "__main__":
    j = Spotify().build_source_dataframe()
    pd.set_option("display.max_columns", 10)
    c = Spotify().category
    print(j.head())
