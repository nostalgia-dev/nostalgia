import os

import pandas as pd
from nostalgia.sources.twitter import Twitter


class AdEngagements(Twitter):
    @classmethod
    def handle_dataframe_per_file(cls, data, *args, **kwargs):
        if data.empty:
            return pd.DataFrame(columns=["start"])

        result = []
        for ad in data.values.tolist():
            ad = ad[0]
            try:
                engagements = ad["adsUserData"]["adEngagements"]["engagements"]
            except KeyError:
                return pd.DataFrame(columns=["start"])

            for engagement in engagements:
                impression = engagement.get("impressionAttributes", None)

                if impression is None:
                    continue

                info = impression.get("promotedTweetInfo", impression.get("promotedTrendInfo", "N/A"))
                ad_text = info.get("tweetText", info.get("description", "N/A"))

                result.append(
                    {"text": ad_text, "created_at": pd.to_datetime(impression.get("impressionTime", 0), utc=True),}
                )

        cls.save_df(result)
        return pd.DataFrame(result)

    @classmethod
    def load(cls, nrows=None, from_cache=False, **kwargs):
        file_path = os.path.expanduser("~/nostalgia_data/input/twitter/data/ad-engagements.json")
        dfs = []
        dfs.append(cls.load_data_file_modified_time(file_path, nrows=nrows, from_cache=from_cache))
        dfs = [x for x in dfs if not x.empty]
        return cls(pd.concat(dfs))
