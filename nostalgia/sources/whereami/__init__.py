import os
import pandas as pd
from datetime import datetime
from nostalgia.ndf import NDF
from nostalgia.times import tz


def get_time(x):
    y, z = x.split()
    try:
        d = datetime.fromtimestamp(float(y), tz)
    except Exception as e:
        print(e)
        return
    return d, z


class Whereami(NDF):
    nlp_columns = ["name"]

    @classmethod
    def load(cls, file_path="~/nostalgia_data/input/whereami/history.tsv", nrows=None, **kwargs):
        file_path = os.path.expanduser(file_path)
        ndata = []
        nrows = nrows or float("inf")
        it = 0
        with open(file_path) as f:
            for x in f.read().split("\n")[1:]:
                if not x.strip():
                    continue
                x = get_time(x)
                if x is None:
                    continue
                if it > nrows:
                    break
                ndata.append(x)
                it += 1

        whereami = pd.DataFrame(ndata, columns=["start", "name"]).sort_values("start")
        whereami = whereami[whereami.name != "unknown"]
        whereami["end"] = whereami.start.shift(-1)
        whereami["in_range"] = (whereami.end - whereami.start) < pd.Timedelta(minutes=20)
        whereami["new"] = (whereami.name != whereami.name.shift(1)).cumsum()

        groups = []
        group_id = None
        start = None
        name = None
        for s, n, e, ir, new in zip(
            whereami.start, whereami.name, whereami.end, whereami.in_range, whereami.new
        ):
            if group_id is None:
                group_id = new
                start = s
                name = n
            elif group_id != new or not ir:
                groups.append({"start": start, "end": s, "name": name})
                group_id = new
                start = s
                name = n

        return cls(pd.DataFrame(groups))
