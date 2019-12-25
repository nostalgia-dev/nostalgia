import just
from nostalgia.times import datetime_from_format
from nostalgia.sources.samsung import Samsung


class SamsungSleep(Samsung):
    @classmethod
    def handle_dataframe_per_file(cls, data, fname):
        data = data[["start_time", "end_time", "stage"]]
        encoding = {40001: "awake", 40002: "light", 40003: "deep", 40004: "rem"}
        data["stage"] = data.stage.replace(encoding)
        return data

    @classmethod
    def load(cls, nrows=None):
        path = "~/nostalgia_data/input/samsung/samsunghealth_*/com.samsung.health.sleep_stage.*.csv"
        fname = just.glob(path)[0]
        data = cls.load_data_file_modified_time(fname, nrows=nrows, skiprows=1)
        data["start_time"] = [
            datetime_from_format(x, "%Y-%m-%d %H:%M:%S.%f") for x in data["start_time"]
        ]
        data["end_time"] = [
            datetime_from_format(x, "%Y-%m-%d %H:%M:%S.%f") for x in data["end_time"]
        ]
        return cls(data)

    @property
    def asleep(self):
        return self.query("stage != 'awake'")
