import os
import just
import string
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse
from datetime import timedelta
import numpy as np
import pandas as pd
from collections import Counter
import re

from nostalgia.times import try_date, tz
from nostalgia.ndf import NDF
from nostalgia.nlp import nlp

digits = set(string.digits)


def old_date(col):
    return pd.to_datetime(
        col.str.slice(0, 14), format="%d-%m-%y %H:%M", errors="coerce"
    ).dt.tz_localize(tz)


class Payments(NDF):
    keywords = ["pay", "buy", "purchase", "spend", "cost"]
    nlp_columns = ["mededelingen", "naam"]
    selected_columns = ["time", "naam", "bedrag", "mededelingen"]

    @classmethod
    def handle_dataframe_per_file(cls, data, fname=None):
        ing = data
        ing["Bedrag (EUR)"] = [float(x.replace(",", ".")) for x in ing["Bedrag (EUR)"]]
        ing["Datum"] = [pd.to_datetime(x, format="%Y%m%d") for x in ing["Datum"]]
        ing["Naam / Omschrijving"] = [x.replace("'", "''") for x in ing["Naam / Omschrijving"]]
        ing["Naam / Omschrijving"] = [x.replace('"', '""') for x in ing["Naam / Omschrijving"]]
        ing["timestamp"] = [
            x if pd.notnull(x) else try_date(y, min_level=3)  # only minutes and below
            for x, y in zip(old_date(ing["Naam / Omschrijving"]), ing.Mededelingen)
        ]
        ing["year"] = [x.year for x in ing.timestamp]

        ing["pas"] = [
            x if y == "Betaalautomaat" and x.startswith("0") else "---"
            for x, y in zip(
                ing.Mededelingen.str.replace(":", "").str.slice(10, 13), ing.MutatieSoort
            )
        ]
        # ing = ing.drop(["Code", "Tegenrekening", "Rekening", "Mededelingen"], axis=1)
        ing.columns = ["bedrag" if x == "Bedrag (EUR)" else x for x in ing.columns]
        ing.columns = ["naam" if x == "Naam / Omschrijving" else x for x in ing.columns]
        ing.columns = [x.lower().replace(" ", "_") for x in ing.columns]
        ing.loc[ing.timestamp.isnull(), "timestamp"] = ing.datum[ing.timestamp.isnull()]
        # ing = ing[ing.timestamp.notnull()]
        return ing

    @classmethod
    def load(cls, file_glob="~/Downloads/NL*20*20*.csv", nrows=None, from_cache=True):
        data = cls.latest_file_is_historic(file_glob, nrows=nrows, from_cache=from_cache)
        return cls(data)

    @property
    def expenses(self):
        return self.query("af_bij == 'Af'")

    @nlp("filter", "by me", "i", "my")
    def by_me(self):
        return self.query("pas == '010'")

    @property
    def by_card(self):
        return self.query("pas != '---'")

    @nlp("end", "how much")
    def sum(self):
        return self.bedrag.sum().round(2)

    def equal_to(self, amount):
        return self.query("bedrag == {}".format(amount))

    def amount_between(self, lower_bound, upper_bound):
        return self.query("{} < bedrag < {}".format(lower_bound, upper_bound))
