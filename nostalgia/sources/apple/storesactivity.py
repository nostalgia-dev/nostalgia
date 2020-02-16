import just
import pandas as pd

from nostalgia.ndf import NDF

class StoresActivity(NDF):
    @classmethod
    def load(cls, nrows=None):
        files = "~/nostalgia_data/input/apple/*/Apple_Media_Services/Stores Activity/Account and Transaction History/Store*History.csv"
        dfs = [pd.read_csv(f, parse_dates=["Item Purchased Date"]) for f in just.glob(files)]
        applications = pd.merge(dfs[0], dfs[1], how="outer", on="Item Purchased Date")
        return cls(applications)


if __name__ == "__main__":
    j = StoresActivity.load()
    j.as_simple()
