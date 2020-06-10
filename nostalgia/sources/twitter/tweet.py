import os

import pandas as pd
from nostalgia.sources.twitter import Twitter


class Tweet(Twitter):
    @classmethod
    def handle_dataframe_per_file(cls, data, *args, **kwargs):
        if data.empty:
            return pd.DataFrame(columns=["start"])

        result = []
        for tweet in data.values.tolist():
            tweet = tweet[0]
            result.append(
                {
                    "text": tweet.get("full_text", ""),
                    "created_at": pd.to_datetime(tweet.get("created_at", 0), utc=True),
                    "source": tweet.get("source", "Unknown"),
                    "lang": tweet.get("lang", "Unknown"),
                }
            )

        cls.save_df(result)
        return pd.DataFrame(result)

    @classmethod
    def load(cls, nrows=None, from_cache=True, **kwargs):
        file_path = os.path.expanduser("~/nostalgia_data/input/twitter/data/tweet.json")
        dfs = []
        dfs.append(cls.load_data_file_modified_time(file_path, nrows=nrows, from_cache=from_cache))
        dfs = [x for x in dfs if not x.empty]
        return cls(pd.concat(dfs))
