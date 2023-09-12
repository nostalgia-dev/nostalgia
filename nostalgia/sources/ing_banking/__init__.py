import os
import just
import string
from datetime import datetime
from dateutil.relativedelta import relativedelta
from nostalgia.extracter import load_from_download
from dateutil.parser import parse
from datetime import timedelta
import numpy as np
import pandas as pd
from collections import Counter
import re

from nostalgia.times import try_date, tz
from nostalgia.sources.ing_banking.mijn_ing_download import scrape_ing
from nostalgia.ndf import NDF

from nostalgia.nlp import nlp

digits = set(string.digits)


def old_date(col):
    return pd.to_datetime(col.str.slice(0, 14), format="%d-%m-%y %H:%M", errors="coerce").dt.tz_localize(tz)


class Payments(NDF):
    vendor = "ing_banking"
    keywords = ["pay", "buy", "purchase", "spend", "cost"]
    nlp_columns = ["notifications", "name"]
    selected_columns = ["time", "name", "amount", "notifications"]
    anonymized = [
        "name",
        "notifications",
        "account",
        "counterparty",
        "amount",
        "date",
        "timestamp",
    ]
    ingest_settings = {
        "ingest_glob": "~/Downloads/NL*20*20*.csv",
        "recent_only": True,
        "delete_existing": False,
    }

    @classmethod
    def handle_dataframe_per_file(cls, data, fname=None):
        ing = data
        ing["amount_eur"] = [float(x.replace(",", ".")) for x in ing["amount_eur"]]
        ing["date"] = [pd.to_datetime(x, format="%Y%m%d") for x in ing["date"]]
        ing["name_description"] = [x.replace("'", "''") for x in ing["name_description"]]
        ing["name_description"] = [x.replace('"', '""') for x in ing["name_description"]]
        ing["timestamp"] = [
            x if pd.notnull(x) else try_date(y, min_level=3)  # only minutes and below
            for x, y in zip(old_date(ing["name_description"]), ing["notifications"])
        ]
        ing["year"] = [x.year if x is not None else None for x in ing.timestamp]
        print(fname, data)

        ing["pas"] = [
            x if y == "Payment terminal" and x.startswith("0") else "---"
            for x, y in zip(ing["notifications"].str.replace(":", "").str.slice(10, 13), ing["transaction_type"])
        ]
        # ing = ing.drop(["Code", "Tegenrekening", "Rekening", "Mededelingen"], axis=1)
        ing.columns = ["amount" if x == "amount_eur" else x for x in ing.columns]
        ing.columns = ["name" if x == "name_description" else x for x in ing.columns]
        ing.columns = [x.lower().replace(" ", "_") for x in ing.columns]
        ing.loc[ing.timestamp.isnull(), "timestamp"] = ing.date[ing.timestamp.isnull()]
        # ing = ing[ing.timestamp.notnull()]
        return ing.drop(["date"], axis=1)

    @classmethod
    def load(cls, nrows=None, from_cache=True):
        data = cls.latest_file_is_historic(cls.ingest_settings["ingest_glob"], nrows=nrows, from_cache=from_cache)
        return cls(data)

    @classmethod
    def ingest(cls):
        scrape_ing()
        print("rows loaded:", cls.load().shape[0])

    @property
    def expenses(self):
        return self.query("af_bij == 'Af'")

    @nlp("filter", "by me", "i", "my")
    def by_me(self):
        return self.query("pas in ['008', '010', '012']")

    def by_me_or_online(self):
        return self.query("pas in ['008', '010', '012', '---']")

    def online(self):
        return self.query("pas in ['---']")

    @property
    def by_card(self):
        return self.query("pas != '---'")

    @nlp("end", "how much")
    def sum(self):
        return self.amount.sum().round(2)

    def equal_to(self, amount):
        return self.query("amount == {}".format(amount))

    def amount_between(self, lower_bound, upper_bound):
        return self.query("({} < amount) & (amount < {})".format(lower_bound, upper_bound))
