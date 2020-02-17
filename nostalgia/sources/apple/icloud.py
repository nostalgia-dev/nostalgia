import just
import pandas as pd

from nostalgia.ndf import NDF
from nostalgia.times import datetime_from_format


class ICloud(NDF):
    @classmethod
    def load(cls, nrows=None):
        files = "~/nostalgia_data/input/apple/*/iCloudUsageData Set*.csv"

        icloud = pd.concat([pd.read_csv(f, skiprows=1, error_bad_lines=False) for f in just.glob(files)])
        icloud = icloud.iloc[:icloud.loc[icloud.Date == "Photos: Delete photo/video from iCloud Photo Library"].index.to_list()[0]]
        icloud["File Capture Date"] = icloud["File Capture Date"].apply(lambda x: datetime_from_format(x, "%Y-%m-%d"))
        return cls(icloud)

if __name__ == "__main__":
    j = ICloud.load()
    print(j.as_simple())
