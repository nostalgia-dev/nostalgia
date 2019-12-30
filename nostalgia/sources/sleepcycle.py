import re
import just
import json
import pandas as pd
import getpass

from nostalgia.ndf import NDF
from nostalgia.times import tz

login_url = "https://s.sleepcycle.com/site/login"
export_url = 'https://s.sleepcycle.com/export/original'


class SleepCycle(NDF):
    @classmethod
    def ingest(cls, credentials, **kwargs):
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
            if len(x["events"]) < 15:
                continue
            for y in x["events"]:
                res.append(y[-1])
                times.append(y[0])
                nums.append(num)
            xs.extend(
                [
                    pd.Timestamp(x["start"], tz=tz) + pd.Timedelta(seconds=int(y))
                    for y in pd.Series(times).rolling(15).mean().fillna(method="bfill")
                ]
            )
            ys.extend(pd.Series(res).rolling(15).mean().fillna(method="bfill"))
        df = pd.DataFrame({"time": xs, "score": ys, "num": nums}).drop_duplicates()
        df["score"] = df["score"].clip(0, 0.025)

        cls.save_df(df)

        return cls(df)
