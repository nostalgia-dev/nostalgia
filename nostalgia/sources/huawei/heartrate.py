from nostalgia.sources.huawei import Huawei
from nostalgia.times import datetime_from_timestamp


class Heartrate(Huawei):
    @classmethod
    def load(cls, nrows=None):
        return cls(
            [
                {
                    "start": datetime_from_timestamp(row["startTime"]),
                    "end": datetime_from_timestamp(row["endTime"]),
                    "value": float(row["value"]),
                }
                for row in cls.yield_rows("HEARTRATE", nrows)
            ]
        )
