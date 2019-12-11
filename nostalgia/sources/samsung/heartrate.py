import re
import os
import pandas as pd
import just
from nostalgia.utils import datetime_from_timestamp, tz
from nostalgia.base_df import DF

BASE = "~/.nostalgia/input/samsung/"


def load_from_download():
    import zipfile

    recent_file = max(
        [x for x in just.glob("~/Downloads/samsunghealth_*.zip") if "(" not in x],
        key=os.path.getctime,
    )
    just.remove(BASE, allow_recursive=True)
    with zipfile.ZipFile(recent_file, 'r') as zip_ref:
        zip_ref.extractall(os.path.expanduser(BASE))


class Heartrate(DF):
    vendor = "samsung"

    @classmethod
    def handle_dataframe_per_file(cls, df, fname):
        if df.empty:
            return None
        df["start"] = [
            datetime_from_timestamp(x) if isinstance(x, int) else tz.localize(x)
            for x in df.start_time
        ]
        df["end"] = [
            datetime_from_timestamp(x) if isinstance(x, int) else tz.localize(x)
            for x in df.end_time
        ]
        del df["start_time"]
        del df["end_time"]
        return df

    @classmethod
    def load(cls, nrows=None, **kwargs):

        file_glob = BASE + "samsunghealth_*/jsons/com.samsung.shealth.tracker.heart_rate"
        file_glob += "/*.com.samsung.health.heart_rate.binning_data.json"

        print(file_glob)
        # TODO FIX
        heartrate = cls.load_dataframe_per_json_file(file_glob, nrows=nrows)
        start = heartrate["start"]
        end = heartrate["end"]
        interval_index = pd.IntervalIndex.from_arrays(start, end)
        heartrate = pd.DataFrame(heartrate)
        heartrate = heartrate.set_index(interval_index).sort_index()
        heartrate["end"] = heartrate.index.right - pd.Timedelta(seconds=1)
        # heartrate = heartrate[heartrate.time != heartrate.end]
        # heartrate = heartrate[heartrate.time <= heartrate.end]
        if nrows is not None:
            heartrate = heartrate.iloc[:nrows]
        heartrate["value"] = heartrate.heart_rate
        del heartrate["heart_rate"]
        return cls(heartrate)
