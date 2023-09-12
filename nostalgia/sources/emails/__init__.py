import os

import dotenv
import pandas as pd
from nostalgia.ndf import NDF
from nostalgia.sources.emails.export import ImapExport

dotenv.load_dotenv(".env")
dotenv.load_dotenv("email/.env")


class Email(NDF):
    me = []
    vendor = "email"

    @classmethod
    def download(cls):
        hostname = os.environ["IMAP_HOSTNAME"]
        username = os.environ["IMAP_USERNAME"]
        password = os.environ["IMAP_PASSWORD"]

        imap_export = ImapExport(hostname, username, password)
        imap_export.walk_folders()

    @classmethod
    def handle_dataframe_per_file(cls, data, fname):
        if data.empty:
            return pd.DataFrame(columns=["text"])

        data["subject"] = data["subject"].astype(str)
        data["to"] = data["to"].astype(str)

        data["sender"] = data["from"].str.extract("<([^>]+)>")
        data.loc[data["sender"].isnull(), "sender"] = data[data["sender"].isnull()]["from"].str.strip('"')
        data["sent"] = data.sender.str.contains("|".join(cls.me), na=False)

        data["receiver"] = data["to"].str.extract("<([^>]+)>")
        data.loc[data["receiver"].isnull(), "receiver"] = data[data["receiver"].isnull()]["to"].str.strip('"')
        data["received"] = data.receiver.str.contains("|".join(cls.me), na=False)

        data["timestamp"] = pd.to_datetime(data["sent_date"], utc=True)
        cls.save_df(data)
        return data

    @classmethod
    def load(cls, nrows=None, from_cache=True, **kwargs):
        file_glob = "~/nostalgia_data/input/imap/**/**/*.json"
        dfs = [cls.load_dataframe_per_json_file(file_glob, nrows=nrows)]
        dfs = [x for x in dfs if not x.empty]
        return cls(pd.concat(dfs))
