import json
from nostalgia.sources.huawei import Huawei
from nostalgia.times import datetime_from_timestamp


class Oxygen(Huawei):
    @classmethod
    def load(cls, nrows=None):
        return cls(
            [
                {
                    "start": datetime_from_timestamp(row["startTime"]),
                    "end": datetime_from_timestamp(row["endTime"]),
                    "value": float(json.loads(row["value"])["avgSaturation"]),
                }
                for row in cls.yield_rows("BLOOD_OXYGEN_SATURATION", nrows)
            ]
        )
