from datetime import timedelta

import just
import pandas as pd

from nostalgia.ndf import NDF
from nostalgia.times import datetime_from_format

flatten = lambda l: [item for sublist in l for item in sublist]

class Spotify(NDF):
    @classmethod
    def load(cls, nrows=None):
        files = "~/nostalgia_data/input/spotify/StreamingHistory*.json"
        spotify = pd.DataFrame(
            [
                (
                    datetime_from_format(x["endTime"], "%Y-%m-%d %H:%M") - timedelta(milliseconds=x["msPlayed"]),
                    datetime_from_format(x["endTime"], "%Y-%m-%d %H:%M"),
                    x["trackName"],
                    x["artistName"],
                    x["msPlayed"] / 1000
                )
                for x in flatten(just.multi_read(files).values())
            ],
            columns=["time_start", "time_end", "title", "artist", "seconds"],
        )
        return cls(spotify)


if __name__ == "__main__":
    j = Spotify.load()
    print(j.create_sample_data())
