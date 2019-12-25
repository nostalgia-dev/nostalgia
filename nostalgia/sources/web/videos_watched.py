import just
from nostalgia.ndf import NDF
from nostalgia.times import datetime_from_timestamp
from nostalgia.file_caching import save, load
import just


class VideosWatched(NDF):
    vendor = "web"

    @classmethod
    def handle_dataframe_per_file(cls, data, fname):
        data["playingSince"] = [
            datetime_from_timestamp(x, "utc", divide_by_1000=False) for x in data["playingSince"]
        ]
        data["playingUntil"] = [
            datetime_from_timestamp(x, "utc", divide_by_1000=False) for x in data["playingUntil"]
        ]
        return data

    @classmethod
    def load(cls, nrows=None):
        data = cls.load_data_file_modified_time("~/nostalgia_data/videos_watched.jsonl")
        return cls(data.reset_index())
