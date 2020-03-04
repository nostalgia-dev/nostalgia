"""
Can be scheduled per 2 minutes with:

sysdm create "python -m nostalgia.sources.whereami.scheduler" --extensions "" --timer "*:0/2"
"""

import time
import whereami
import os

if __name__ == "__main__":
    with open(os.path.expanduser("~/nostalgia_data/input/whereami/history.tsv"), "a") as f:
        res = whereami.predict()
        print(res)
        f.write("{}\t{}\n".format(time.time(), res))
