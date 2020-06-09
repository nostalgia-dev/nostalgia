import os

import pandas as pd
from nostalgia.sources.twitter import Twitter


class DirectMessage(Twitter):
    @classmethod
    def handle_dataframe_per_file(cls, data, *args, **kwargs):
        if data.empty:
            return pd.DataFrame(columns=["start"])

        result = []
        for contact in data.values.tolist():
            contact = contact[0]
            for dm in contact.get("messages", []):
                message = dm.get("messageCreate", None)

                if message is None:
                    continue

                result.append(
                    {
                        "text": message.get("text", ""),
                        "title": message.get("text", None),
                        "created_at": pd.to_datetime(message.get("createdAt", 0), utc=True),
                    }
                )

        cls.save_df(result)
        return pd.DataFrame(result)

    @classmethod
    def load(cls, nrows=None, from_cache=False, **kwargs):
        file_path = os.path.expanduser("~/nostalgia_data/input/twitter/data/direct-messages.json")
        dfs = []
        dfs.append(cls.load_data_file_modified_time(file_path, nrows=nrows, from_cache=from_cache))
        dfs = [x for x in dfs if not x.empty]
        return cls(pd.concat(dfs))
