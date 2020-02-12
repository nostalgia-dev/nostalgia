import just
import pandas as pd

from nostalgia.ndf import NDF
import os

class Applications(NDF):
    @classmethod
    def load(cls, file_path="~/nostalgia_data/input/apple/*/Apple_Media_Services/Stores Activity/Account and Transaction History/", nrows=None):
        files = os.path.join(file_path, "Store*History.csv")
        dfs = [pd.read_csv(f, parse_dates=["Item Purchased Date"]) for f in just.glob(files)]
        applications = pd.merge(dfs[0], dfs[1], how="outer", on="Item Purchased Date")
        return cls(applications)


if __name__ == "__main__":
    j = Applications.load()
    j.as_simple()
