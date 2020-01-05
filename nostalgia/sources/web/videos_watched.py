from nostalgia.ndf import NDF
from nostalgia.times import datetime_from_timestamp
import urllib.parse


def get_thumbnail(url):
    img = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
    return "http://i3.ytimg.com/vi/{}/maxresdefault.jpg".format(img["v"][0]) if "v" in img else None


class VideosWatched(NDF):
    vendor = "web"

    @classmethod
    def handle_dataframe_per_file(cls, data, fname):
        data["playingSince"] = [datetime_from_timestamp(x, "utc") for x in data["playingSince"]]
        data["playingUntil"] = [datetime_from_timestamp(x, "utc") for x in data["playingUntil"]]
        return data

    @classmethod
    def load(cls, nrows=None):
        data = cls.load_data_file_modified_time(
            "~/nostalgia_data/videos_watched.jsonl", nrows=nrows
        )
        data["image"] = [get_thumbnail(x) for x in data["loc"]]

        return cls(data.reset_index())
