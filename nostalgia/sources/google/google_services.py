from nostalgia.times import parse_datetime
from datetime import timedelta
from nostalgia.sources.google import Google


class GoogleServices(Google):
    @classmethod
    def handle_dataframe_per_file(cls, data, _file_path):
        data = data.assign(
            time=[parse_datetime(x.replace(" UTC", "Z")) for x in data.activity_timestamp],
            app=[
                x.removesuffix("_APP") if not isinstance(x, float) else ""
                for x in data.user_agent_string.str.extract("App : ([^.]+)")[0]
            ],
            device=data.user_agent_string.str.extract("Device Type : ([^.]+)."),
        )
        data["title"] = ["{} ({}) on {}".format(*x) for x in zip(data.product_name, data.app, data.device)]
        return data[["time", "title", "ip_address", "app", "device", "product_name", "sub_product_name"]]

    @classmethod
    def load(cls, nrows=None, from_cache=True, **kwargs):
        file_path = "~/nostalgia_data/input/google/Takeout/Access log activity/Activities – A list of Google services accessed by.csv"
        data = cls.load_data_file_modified_time(file_path, nrows=nrows, from_cache=from_cache)
        return cls(data)
