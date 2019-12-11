import os
import re
import pandas as pd
from datetime import datetime
from nostalgia.utils import tz

from nostalgia.base_df import DF


class FileVisits(DF):
    @classmethod
    def load(cls, fname, nrows=None):
        with open(fname) as f:
            results = []
            files = []
            ds = []
            num = 0
            for line in f.read().split("\n"):
                if not line:
                    continue
                y, z = line.split(",", 1)
                if not y:
                    continue
                files.append(z)
                d = datetime.fromtimestamp(float(y), tz)
                ds.append(d)
                for key in ["egoroot/", "/ssh:", "gits/", "site-packages/"]:
                    if key in z:
                        z = re.split("[:/]", z.split(key)[1])[0]
                results.append(z)
                if num == nrows:
                    break
                num += 1
        data = pd.DataFrame({"file": files, "name": results, "time": ds})
        return cls(data)
