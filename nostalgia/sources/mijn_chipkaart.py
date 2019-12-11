import just
import pandas as pd
from nostalgia.base_df import DF
from nostalgia.utils import parse_date_tz
from nostalgia.nlp import nlp


class MijnChipkaart(DF):
    @property
    def title(self):
        return [x + " - " + y for x, y in zip(self.Vertrek, self.Bestemming)]

    @nlp("end", "how much", "cost")
    def sum(self):
        return self.Bedrag.sum()

    @classmethod
    def load(cls, file_glob, nrows=None):
        files = just.glob(file_glob)
        data = pd.concat([pd.read_csv(x, sep=";", nrows=nrows) for x in files])
        data["Bedrag"] = [float(x.replace(",", ".")) for x in data["Bedrag"]]
        data["Datum"] = [
            parse_date_tz(x + " " + y).start_date for x, y in zip(data.Datum, data["Check-uit"])
        ]
        return cls(data)
