import os

import pandas as pd
from nostalgia.sources.twitter import Twitter


class IpAudit(Twitter):
    @classmethod
    def handle_dataframe_per_file(cls, data, *args, **kwargs):
        if data.empty:
            return pd.DataFrame(columns=["start"])

        result = []
        for audit in data.values.tolist():
            audit = audit[0]
            result.append(
                {
                    "text": audit.get("loginIp", ""),
                    "title": audit.get("loginIp", None),
                    "created_at": pd.to_datetime(audit.get("createdAt", 0), utc=True),
                }
            )

        cls.save_df(result)
        return pd.DataFrame(result)

    @classmethod
    def load(cls, nrows=None, from_cache=False, **kwargs):
        file_path = os.path.expanduser("~/nostalgia_data/input/twitter/data/ip-audit.json")
        dfs = []
        dfs.append(cls.load_data_file_modified_time(file_path, nrows=nrows, from_cache=from_cache))
        dfs = [x for x in dfs if not x.empty]
        return cls(pd.concat(dfs))
