from nostalgia.times import parse_datetime
from nostalgia.sources.google import Google


class AppUsage(Google):
    @classmethod
    def handle_dataframe_per_file(cls, data, file_path):
        data["time"] = [parse_datetime(x) if isinstance(x, str) else x for x in data["time"]]
        data = data.rename(columns={"header": "name"})
        return data[["name", "time"]]

    @classmethod
    def load(cls, nrows=None, from_cache=True, **kwargs):
        file_path = "~/nostalgia_data/input/google/Takeout/My Activity/Android/My Activity.json"
        data = cls.load_data_file_modified_time(file_path, nrows=nrows, from_cache=from_cache)
        return cls(data)
