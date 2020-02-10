import just
import pandas as pd

from nostalgia.ndf import NDF
from nostalgia.times import datetime_from_format


class Spotify(NDF):
    @classmethod
    def load(cls, file_path="/Users/nikolay_vasilishin/nostalgia_data/input/spotify/StreamingHistory0.json", nrows=None):
        spotify = pd.DataFrame(
            [
                (
                    datetime_from_format(x["endTime"], "%Y-%m-%d %H:%M"),
                    x["trackName"],
                    x["artistName"],
                    x["msPlayed"] / 1000
                )
                for x in just.read(file_path)
            ],
            columns=["time", "title", "artist", "seconds"],
        )
        return cls(spotify)


if __name__ == "__main__":
    j = Spotify.load()
    print(j.as_simple())
    print(j.last_week)
