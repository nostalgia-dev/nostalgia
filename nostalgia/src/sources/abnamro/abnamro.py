import re
import time

import just
import numpy as np
import pandas as pd

from nostalgia.times import datetime_from_format
from nostalgia.times import datetime_from_timestamp
from nostalgia.src.common.meta.aspect.money import Money
from nostalgia.src.common.meta.aspect.subject import Subject
from nostalgia.src.common.meta.aspect.time import Time
from nostalgia.src.common.meta.category.transaction import Transaction
from nostalgia.src.sources import Source


def find_date(x):
    date_regex = ".*(\d{2}[\.-]\d{2}[\.-]\d{2,4}[\/]\d{2}[\.-]\d{2}).*"
    value = str(x).replace("\\", "\\\\")
    m = re.match(date_regex, value)
    if m:
        return datetime_from_format(m.group(1), "%d.%m.%y/%H.%M")


class AbnAmro(Source):
    @property
    def category(self) -> list:
        return [Transaction]

    @property
    def aspects(self) -> dict:
        return {
            "startsaldo": Money,
            # "endsaldo": Ignore, TODO add Ignore Aspect
            "amount": Money,
            "mutationcode": Money.Currency,
            "transactiondate": Time,
            "preciseDate": Time,
            "description": Subject
            # "accountNumber": Account Anonymized TODO refactor Anonymized into Aspect
        }

    def ingest(self, delta_data, **kwargs):
        return pd.concat([pd.read_excel(x) for x in just.glob("~/nostalgia_data/input/abnamro/*.xls")])

    @classmethod
    def load(cls, data):
        """
        The only transformation is needed here is to fulfill data with precise time (more precise, than just date)
        and interpolate values for missing rows
        @param data: pd.DataFrame - dataframe after ingestion stage
        @return: pd.DataFrame - prepared dataframe for marking with Aspects and Categories
        """
        data["preciseDate"] = data["description"].apply(find_date)
        if data.preciseDate.isnull().iloc[0]:
            data.preciseDate.iloc[0] = datetime_from_format(str(data.transactiondate.iloc[0]), "%Y%m%d")
        if data.preciseDate.isnull().iloc[-1]:
            data.preciseDate.iloc[-1] = datetime_from_format(str(data.transactiondate.iloc[-1]), "%Y%m%d")

        data.preciseDate = (
            data.preciseDate.map(lambda x: time.mktime(pd.datetime.timetuple(x)) if not pd.isna(x) else np.nan)
            .interpolate("values")
            .map(datetime_from_timestamp)
        )

        return data


if __name__ == "__main__":
    d = AbnAmro().build_sdf()
    print(d)
