import just
import pandas as pd
from nostalgia.sources.google import Google


class Calendar(Google):
    @classmethod
    def handle_dataframe_per_file(cls, data, file_path):
        if data.empty:
            return pd.DataFrame(columns=["start", "end"])
        data["calendar"] = file_path.split("/")[-1]
        data["start"] = pd.to_datetime(data["start"], utc=True)
        data["end"] = pd.to_datetime(data["end"], utc=True)
        return data

    @classmethod
    def load(cls, nrows=None, from_cache=True, **kwargs):
        dfs = [
            cls.load_data_file_modified_time(file_path, nrows=nrows, from_cache=from_cache)
            for file_path in just.glob("~/nostalgia_data/input/google/Takeout/*/*.ics")
        ]
        dfs = [x for x in dfs if not x.empty]
        return cls(pd.concat(dfs))
