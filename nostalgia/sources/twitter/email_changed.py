import os

import pandas as pd
from nostalgia.sources.twitter import Twitter


class EmailChanged(Twitter):
    @classmethod
    def handle_dataframe_per_file(cls, data, *args, **kwargs):
        if data.empty:
            return pd.DataFrame(columns=["start"])

        result = []
        for change in data.values.tolist():
            change = change[0]
            result.append(
                {
                    "text": change["emailChange"]["changedFrom"]
                    if "changedFrom" in change["emailChange"]
                    else change["emailChange"]["changedTo"],
                    "title": change["emailChange"]["changedTo"],
                    "created_at": pd.to_datetime(change["emailChange"].get("changedAt", 0), utc=True),
                }
            )

        cls.save_df(result)
        return pd.DataFrame(result)

    @classmethod
    def load(cls, nrows=None, from_cache=False, **kwargs):
        file_path = os.path.expanduser("~/nostalgia_data/input/twitter/data/email-address-change.json")
        dfs = []
        dfs.append(cls.load_data_file_modified_time(file_path, nrows=nrows, from_cache=from_cache))
        dfs = [x for x in dfs if not x.empty]
        return cls(pd.concat(dfs))
