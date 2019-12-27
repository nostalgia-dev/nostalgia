import re
import os
import pandas as pd
import just
from nostalgia.times import datetime_from_timestamp, tz
from nostalgia.ndf import NDF
from nostalgia.sources.samsung import Samsung


class SamsungStress(Samsung, NDF):
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
        file_glob = "~/nostalgia_data/input/samsung/samsunghealth_*/jsons/com.samsung.shealth.stress/*.binning_data.json"
        print(file_glob)
        # TODO FIX
        stress = cls.load_dataframe_per_json_file(file_glob, nrows=nrows)
        start = stress["start"]
        end = stress["end"]
        interval_index = pd.IntervalIndex.from_arrays(start, end)
        stress = pd.DataFrame(stress)
        stress = stress.set_index(interval_index).sort_index()
        stress["end"] = stress.index.right - pd.Timedelta(seconds=1)
        # if nrows is not None:
        #     stress = stress.iloc[:nrows]
        stress["value"] = stress.score
        del stress["score"]
        return cls(stress)
