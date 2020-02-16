import just
import pandas as pd

from nostalgia.ndf import NDF
from nostalgia.times import parse_date_tz


class NsChipkaart(NDF):
    @classmethod
    def load(cls, nrows=None):
        files = just.glob("~/nostalgia_data/input/ns_chipkaart/reistransacties-*.xls")
        data = pd.concat([pd.read_excel(x, nrows=nrows) for x in files]).iloc[:-1]
        data["Datum"] = data["Datum"].apply(parse_date_tz)
        data["Vertrek"], data["Bestemming"] = data["Omschrijving"].str.split(":", 1).str[1].str.split(" - ", 1).str
        return cls(data)
