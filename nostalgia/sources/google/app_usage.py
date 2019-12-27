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


class AppUsage(Google):
    @classmethod
    def handle_dataframe_per_file(cls, data, file_path):
        data["time"] = [custom_parse(x) for x in data["time"]]
        data = data.rename(columns={"header": "name"})
        return data[["name", "time"]]

    @classmethod
    def load(cls, nrows=None, from_cache=True, **kwargs):
        file_path = "~/nostalgia_data/input/google/Takeout/My Activity/Android/My Activity.json"
        data = cls.load_data_file_modified_time(file_path, nrows=nrows, from_cache=from_cache)
        return cls(data)
