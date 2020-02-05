import just
import pandas as pd
from datetime import datetime
from nostalgia.times import tz, parse
from nostalgia.data_loading import read_array_of_dict_from_json
from nostalgia.sources.google import Google


def try_parse(x):
    try:
        if x.endswith("PST"):
            x = x.replace("PST", "-0800 (PST)")
        elif x.endswith("PDT"):
            x = x.replace("PDT", "-0700 (PDT)")
        d = parse(x)
        if d.tzinfo is None:
            d = d.replace(tzinfo=tz)
        return d
    except:
        return datetime(1970, 1, 1, 0, 0, 0, tzinfo=tz)


# class MBox:
#     ingest_settings = {
#         "ingest_glob": "~/Downloads/*.mbox",
#         "recent_only": False,
#         "delete_existing": False,
#     }


class Gmail(Google):
    me = []

    @classmethod
    def handle_dataframe_per_file(cls, data, fname):
        data["subject"] = data["subject"].astype(str)
        data["to"] = data["to"].astype(str)
        data["sender"] = data["from"].str.extract("<([^>]+)>")
        data.loc[data["sender"].isnull(), "sender"] = data[data["sender"].isnull()][
            "from"
        ].str.strip('"')
        data["sent"] = data.sender.str.contains("|".join(cls.me), na=False)
        data["receiver"] = data["to"].str.extract("<([^>]+)>")
        data.loc[data["receiver"].isnull(), "receiver"] = data.loc[data["receiver"].isnull(), "to"]
        data["received"] = data.receiver.str.contains("|".join(cls.me), na=False)
        data["timestamp"] = pd.to_datetime([try_parse(x) for x in data.date], utc=True).tz_convert(
            tz
        )
        data.drop("date", axis=1, inplace=True)
        return data

    @classmethod
    def load(cls, nrows=None, from_cache=True, **kwargs):
        dfs = [
            cls.load_data_file_modified_time(file_path, nrows=nrows, from_cache=from_cache)
            for file_path in just.glob("~/nostalgia_data/input/google/Takeout/Mail/*.mbox")
        ]
        dfs = [x for x in dfs if not x.empty]
        return cls(pd.concat(dfs))

    def sent_by(self, name=None, email=None, case=False):
        if name is not None and email is not None:
            a = self.sender.str.contains(name, case=case, na=False)
            b = self.sender.str.contains(email, case=case, na=False)
            res = self[a | b]
        elif name is not None:
            res = self[self.sender.str.contains(name, case=case, na=False)]
        elif email is not None:
            res = self[self.sender.str.contains(email, case=case, na=False)]
        return self.__class__(res)

    def received_by(self, name=None, email=None, case=False):
        if name is not None and email is not None:
            a = self.receiver.str.contains(name, case=case, na=False)
            b = self.receiver.str.contains(email, case=case, na=False)
            res = self[a | b]
        elif name is not None:
            res = self[self.receiver.str.contains(name, case=case, na=False)]
        elif email is not None:
            res = self[self.receiver.str.contains(email, case=case, na=False)]
        return self.__class__(res)
