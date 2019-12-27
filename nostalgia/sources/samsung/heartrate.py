import re
import os
import pandas as pd
import just
from nostalgia.times import datetime_from_timestamp, tz
from nostalgia.ndf import NDF
from nostalgia.sources.samsung import Samsung


class SamsungHeartrate(Samsung, NDF):
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
        file_glob = "~/nostalgia_data/input/samsung/samsunghealth_*/jsons/com.samsung.shealth.tracker.heart_rate"
        file_glob += "/*.com.samsung.health.heart_rate.binning_data.json"
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
        # if nrows is not None:
        #     heartrate = heartrate.iloc[:nrows]
        heartrate["value"] = heartrate.heart_rate
        del heartrate["heart_rate"]
        return cls(heartrate)
