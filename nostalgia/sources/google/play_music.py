import numpy as np
from nostalgia.times import datetime_from_format
from datetime import timedelta
from nostalgia.sources.google import Google


def custom_parse(x):
    if not isinstance(x, str):
        return x
    try:
        return datetime_from_format(x, "%Y-%m-%dT%H:%M:%SZ", in_utc=True)
    except:
        return datetime_from_format(x, "%Y-%m-%dT%H:%M:%S.%fZ", in_utc=True)


class PlayMusic(Google):
    @classmethod
    def handle_dataframe_per_file(cls, data, file_path):
        data["_start"] = [custom_parse(x) for x in data["time"]]

        data = data.rename(columns={"description": "artist"})
        data = data[~data.title.str.startswith("Searched for ", na=False)]
        data.loc[:, "skip"] = data.title.str.startswith("Skipped ")
        data.loc[:, "listen"] = data.title.str.startswith("Listened to ")
        data = data.sort_values("_start")
        data["skipping_this"] = data.shift(-1).skip
        data["_end"] = data.shift(-1)._start
        data["fake"] = data.skipping_this & (data._end - data._start < timedelta(seconds=15))
        data["long"] = data._end - data._start > timedelta(minutes=10)
        data.loc[data.long, "_end"] = data[data.long]["_start"] + timedelta(minutes=10)
        data = data[~data.fake & data.listen]
        # stripping "Listened to "
        data["title"] = data.title.str.slice(12, None)
        data["duration"] = data._end - data._start
        # clean up
        for d in [
            "products",
            "subtitles",
            "header",
            "titleUrl",
            "skipping_this",
            "skip",
            "listen",
            "fake",
        ]:
            if d in data:
                del data[d]
        for name, group in data.groupby(["artist", "title"]):
            if not group.long.any() or group.long.all():
                continue
            max_duration = group.duration.max()
            group.loc[group.long, "duration"] = max_duration
            group.loc[group.long, "_end"] = group._start + max_duration
            group.loc[:, "long"] = False
        # duration cannot be written to parquet, so do it in post process
        del data["duration"]
        return data

    @classmethod
    def load(cls, nrows=None, from_cache=True, **kwargs):
        file_path = (
            "~/nostalgia_data/input/google/Takeout/My Activity/Google Play Music/My Activity.json"
        )
        data = cls.load_data_file_modified_time(file_path, nrows=nrows, from_cache=from_cache)
        data["duration"] = data["_end"] - data["_start"]
        return cls(data)
