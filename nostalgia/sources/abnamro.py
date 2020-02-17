import pandas as pd
from nostalgia.ndf import NDF
from nostalgia.times import datetime_from_format
import re
import just
import time
import numpy as np
from nostalgia.times import datetime_from_timestamp
import os

def convert_date(date):
    return datetime_from_format(str(date),"%Y%m%d")

def find_date(x):
    date_regex = ".*(\d{2}[\.-]\d{2}[\.-]\d{2,4}[\/]\d{2}[\.-]\d{2}).*"
    value = str(x).replace('\\','\\\\')
    m = re.match(date_regex, value)
    if m:
        return datetime_from_format(m.group(1),"%d.%m.%y/%H.%M")

class AbnAmro(NDF):
    @classmethod
    def load(cls, nrows=None):
        files = just.glob('~/nostalgia_data/input/abnamro/*.xls')
        abn = pd.concat([pd.read_excel(x, nrows=nrows, converters={'transactiondate': convert_date}) for x in files])
        abn["preciseDate"] = abn["description"].apply(find_date)
        if abn.preciseDate.isnull().iloc[0]:
            abn.preciseDate.iloc[0] = abn.transactiondate.iloc[0]
        if abn.preciseDate.isnull().iloc[-1]:
            abn.preciseDate.iloc[-1] = abn.transactiondate.iloc[-1]

        abn.preciseDate = abn.preciseDate.map(lambda x: time.mktime(pd.datetime.timetuple(x)) if not pd.isna(x) else np.nan) \
            .interpolate('values') \
            .map(datetime_from_timestamp)


        return cls(abn)

if __name__ == "__main__":
    d = AbnAmro.load()
    print(d)