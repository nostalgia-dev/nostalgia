import os
import sqlite3
import pandas as pd
from nostalgia.ndf import NDF
from nostalgia.times import datetime_from_timestamp


class OpenScale(NDF):
    ingest_settings = {
        "rclone_remote": "ggdrive",
        "rclone_remote_file": "MI_scale_v2_data/openScale.db",
        "input_dir": "~/nostalgia_data/input/",
    }

    @classmethod
    def load(cls, nrows=None, **kwargs):
        db = os.path.expanduser("~/nostalgia_data/input/openScale.db")
        conn = sqlite3.connect(db)
        c = conn.cursor()
        df = pd.DataFrame(
            c.execute("SELECT userId,datetime,weight FROM scaleMeasurements;"), columns=["user_id", "ts", "weight"]
        )
        df["ts"] = [datetime_from_timestamp(x) for x in df.ts]
        df["title"] = df.weight.round(2)
        return cls(df.iloc[: nrows or 10**10])

    @classmethod
    def ingest(cls):
        rclone_remote = cls.ingest_settings["rclone_remote"]
        rclone_remote_file = cls.ingest_settings["rclone_remote_file"]
        input_dir = cls.ingest_settings["input_dir"]
        print(f"rclone copy {rclone_remote}:{rclone_remote_file} {input_dir}")
        os.system(f"rclone copy {rclone_remote}:{rclone_remote_file} {input_dir}")
