from nostalgia.base_df import DF
from nostalgia.utils import datetime_from_format
from datetime import timedelta


def custom_parse(x):
    try:
        return datetime_from_format(x, "%Y-%m-%dT%H:%M:%SZ", in_utc=True)
    except:
        return datetime_from_format(x, "%Y-%m-%dT%H:%M:%S.%fZ", in_utc=True)


class AppUsage(DF):
    vendor = "google"

    @classmethod
    def handle_dataframe_per_file(cls, data, file_path):
        data["time"] = [custom_parse(x) for x in data["time"]]
        data = data.rename(columns={"header": "name"})
        return data[["name", "time"]]

    # refactor to use "google_takeout" as target
    @classmethod
    def load(cls, takeout_folder, nrows=None, from_cache=True, **kwargs):
        if not takeout_folder.endswith("/"):
            takeout_folder += "/"
        file_path = takeout_folder + "My Activity/Android/My Activity.json"
        data = cls.load_data_file_modified_time(file_path, nrows=nrows, from_cache=from_cache)
        if nrows is not None:
            data = data.iloc[:5]
        return cls(data)
