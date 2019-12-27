import pandas as pd
from nostalgia.sources.google import Google
from nostalgia.times import datetime_from_format
from nostalgia.times import tz


class PageVisit(Google):
    @classmethod
    def handle_dataframe_per_file(cls, data, file_path):
        data["time"] = pd.to_datetime(data.time_usec, utc=True, unit="us").dt.tz_convert(tz)
        del data["time_usec"]
        return data

    # refactor to use "google_takeout" as target
    @classmethod
    def load(cls, nrows=None, from_cache=True, **kwargs):
        file_path = "~/nostalgia_data/input/google/Takeout/Chrome/BrowserHistory.json"
        page_visit = cls.load_data_file_modified_time(
            file_path, "Browser History", nrows=nrows, from_cache=from_cache
        )
        return cls(page_visit)
