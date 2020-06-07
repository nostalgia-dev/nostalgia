import os

import pandas as pd
from nostalgia.sources.twitter import Twitter


class ConnectedApplication(Twitter):
    @classmethod
    def handle_dataframe_per_file(cls, data, *args, **kwargs):
        if data.empty:
            return pd.DataFrame(columns=["start"])

        result = []
        for app in data.values.tolist():
            app = app[0]
            result.append(
                {
                    "text": app.get("description", ""),
                    "title": app.get("name", None),
                    "created_at": pd.to_datetime(app.get("approvedAt", 0), utc=True),
                }
            )

        cls.save_df(result)
        return pd.DataFrame(result)

    @classmethod
    def load(cls, nrows=None, from_cache=False, **kwargs):
        file_path = os.path.expanduser("~/nostalgia_data/input/twitter/data/connected-application.json")
        dfs = []
        dfs.append(cls.load_data_file_modified_time(file_path, nrows=nrows, from_cache=from_cache))
        dfs = [x for x in dfs if not x.empty]
        return cls(pd.concat(dfs))
