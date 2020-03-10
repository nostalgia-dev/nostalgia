import pandas as pd

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
            'time_start': Time.of_duration("time_end", "seconds_listened", duration_unit='s'),
            'time_end': Time,
            'title': Title
        }

    def ingest(self, delta_data, **kwargs):
        # how to extract and where? Download?
        return self.read_file("StreamingHistory*.json")

    @classmethod
    def load(self, data) -> pd.DataFrame:
        spotify = pd.DataFrame([(
            x["endTime"],
            x["trackName"],
            x["artistName"],
            x["msPlayed"] // 1000
        ) for x in Functional.flatten(data)],
            columns=["time_end", "title", "artist", "seconds_listened"]
        )
        return spotify


if __name__ == "__main__":
    j = Spotify().build_sdf()
    pd.set_option("display.max_columns", 10)
    c = Spotify().category
    print(j.head())
