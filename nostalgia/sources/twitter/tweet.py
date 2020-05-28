import just
import pandas as pd
from nostalgia.sources.twitter import Twitter

class Tweet(Twitter):
    @classmethod
    def handle_dataframe_per_file(cls, data, *args, **kwargs):
        if data.empty:
            return pd.DataFrame(columns=["start"])

        tweets = data.get("tweet", None)
        if tweets is None:
            return pd.DataFrame(columns=["start"])

        result = []
        for tweet in tweets:
            result.append({
                "text": tweet.get("full_text", ""),
                "start": pd.to_datetime(tweet.get("created_at", 0), utc=True),
                "source": tweet.get("source", "Unknown"),
                "lang": tweet.get("lang", "Unknown")
            })

        return pd.DataFrame(result)

    @classmethod
    def load(cls, nrows=None, from_cache=True, **kwargs):
        dfs = [
            cls.load_data_file_modified_time(file_path, nrows=nrows, from_cache=from_cache)
            for file_path in just.glob("~/nostalgia_data/input/twitter/data/*.json")
        ]
        dfs = [x for x in dfs if not x.empty]
        return cls(pd.concat(dfs))