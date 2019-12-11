import re
import just
import json
import pandas as pd
import getpass

from nostalgia.base_df import DF
from nostalgia.source_to_fast import save, load
from nostalgia.utils import tz

login_url = "https://s.sleepcycle.com/site/login"
export_url = 'https://s.sleepcycle.com/export/original'


class SleepCycle(DF):
    @classmethod
    def download(cls, file_path, credentials, **kwargs):
        html = just.get(login_url)
        token = re.findall('name="csrftoken" value="([^"]+)', html)[0]

        data = {
            "username": credentials.username,
            "csrftoken": token,
            "password": credentials.password,
        }
        _ = just.post(login_url, data=data)

        str_data = just.get('https://s.sleepcycle.com/export/original')

        start = str_data.index("data_json.txt") + len("data_json.txt")
        end = str_data[start:].index("}]PK") + 2

        data = json.loads(str_data[start:][:end])

        xs = []
        ys = []
        nums = []
        for num, x in enumerate(data):
            res = []
            times = []
            for y in x["events"]:
                res.append(y[-1])
                times.append(y[0])
                nums.append(num)
            xs.extend(
                [
                    pd.Timestamp(x["start"], tz=tz) + pd.Timedelta(seconds=y)
                    for y in pd.Series(times).rolling(15).mean().fillna(method="bfill")
                ]
            )
            ys.extend(pd.Series(res).rolling(15).mean().fillna(method="bfill"))

        df = pd.DataFrame({"time": xs, "score": ys, "num": nums}).drop_duplicates()
        df["score"] = df["score"].clip(0, 0.025)

        save(df, file_path)

        return cls(df)

    @classmethod
    def load(cls, file_path, credentials, nrows=None):
        return cls(load(file_path))
