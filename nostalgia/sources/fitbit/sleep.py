import os
import pandas as pd
import just
from metadate import parse_date
from datetime import datetime
from nostalgia.ndf import NDF
from nostalgia.times import datetime_from_format


class FitbitSleep(NDF):
    vendor = "fitbit"

    @classmethod
    def load(cls, nrows=None):
        file_glob = "~/nostalgia_data/input/fitbit/*/sleep/*.json"
        objects = []
        for d in just.multi_read(file_glob).values():
            if not d:
                continue
            for x in d:
                data = pd.DataFrame(
                    x["levels"]["data"]
                    + [{'dateTime': x['endTime'], 'level': None, 'seconds': None}]
                )
                data["dateTime"] = [
                    datetime_from_format(x, "%Y-%m-%dT%H:%M:%S.%f") for x in data.dateTime
                ]
                start = data.dateTime.iloc[:-1]
                end = data.dateTime.iloc[1:]
                interval_index = pd.IntervalIndex.from_arrays(start, end)
                data = pd.DataFrame(data.iloc[:-1])
                data = data.set_index(interval_index)
                data["start"] = data.index.left
                data["end"] = data.index.right
                objects.append(data)
                if nrows is not None and data.shape[0] > nrows:
                    break

        data = pd.concat(objects).drop("dateTime", axis=1)

        return cls(data)

    @property
    def asleep(self):
        return self.query("level != 'wake'")
