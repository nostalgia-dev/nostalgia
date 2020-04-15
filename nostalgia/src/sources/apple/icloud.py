import just
import pandas as pd

from nostalgia.times import datetime_from_format
from src.common.meta.aspect.place import Place
from src.common.meta.aspect.time import Time
from src.common.meta.category.services import Service
from src.sources import Source


class ICloud(Source):



    @property
    def category(self) -> list:
        return [Service]

    @property
    def aspects(self) -> dict:
        return {
            "Date": Time,
            "City (IP Address Derived)": Place,
            "Country Code (IP Address Derived)": Place
        }

    def ingest(self, delta_data, **kwargs) -> pd.DataFrame:
        return pd.concat([pd.read_csv(f, skiprows=1, error_bad_lines=False) for f in just.glob("~/nostalgia_data/input/apple/*/iCloudUsageData Set*.csv")])


    def load(self, data):
        data = data.iloc[:data.loc[data.Date == "Photos: Delete photo/video from iCloud Photo Library"].index.to_list()[0]]
        data["File Capture Date"] = data["File Capture Date"].apply(lambda x: datetime_from_format(x, "%Y-%m-%d"))
        return data

if __name__ == "__main__":
    j = ICloud().build_sdf()
    print(j.as_simple())
