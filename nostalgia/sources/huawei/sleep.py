from nostalgia.sources.huawei import Huawei
from nostalgia.times import datetime_from_timestamp


class Sleep(Huawei):
    @classmethod
    def load(cls, nrows=None):
        encoding = {
            "PROFESSIONAL_SLEEP_WAKE": "awake",
            "PROFESSIONAL_SLEEP_SHALLOW": "light",
            "PROFESSIONAL_SLEEP_DEEP": "deep",
            "PROFESSIONAL_SLEEP_DREAM": "rem",
            "PROFESSIONAL_SLEEP_NOON": "nap",
        }
        return cls(
            [
                {
                    "start": datetime_from_timestamp(row["startTime"]),
                    "end": datetime_from_timestamp(row["endTime"]),
                    "value": encoding[row["key"]],
                }
                for row in cls.yield_rows("PROFESSIONAL_SLEEP", nrows)
            ]
        )
