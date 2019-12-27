import re
import os
import pandas as pd
import just
from datetime import datetime
from nostalgia.ndf import NDF
from nostalgia.times import datetime_from_format


def get_day(fname):
    return " ".join(re.sub(".partial_[0-9]+.[0-9]+", "", os.path.basename(fname)).split(".")[1:-1])


class FitbitHeartrate(NDF):
    vendor = "fitbit"

    @classmethod
    def handle_dataframe_per_file(cls, df, fname):
        if df.empty:
            return None
        day = get_day(fname)
        df["time"] = [datetime_from_format(day + " " + x, "%Y %m %d %H:%M:%S") for x in df.time]
        return df

    @classmethod
    def download(cls):
        from nostalgia_fitbit.__main__ import main

        main()

    @classmethod
    def load(cls, nrows=None, **kwargs):
        file_glob = "~/nostalgia_data/input/fitbit/*/heartrate_intraday/**/*.json"
        heartrate = cls.load_dataframe_per_json_file(file_glob, nrows=nrows)
        start = heartrate.time.iloc[:-1]
        end = heartrate.time.iloc[1:]
        interval_index = pd.IntervalIndex.from_arrays(start, end)
        heartrate = pd.DataFrame(heartrate.iloc[:-1])
        heartrate = heartrate.set_index(interval_index)
        heartrate["end"] = heartrate.index.right - pd.Timedelta(seconds=1)
        heartrate = heartrate[heartrate.time != heartrate.end]
        heartrate = heartrate[heartrate.time <= heartrate.end]
        # if nrows is not None:
        #     heartrate = heartrate.iloc[:nrows]
        return cls(heartrate)
