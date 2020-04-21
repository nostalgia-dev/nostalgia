import unittest
# also use doctest
from pandas._libs.tslibs.timestamps import Timestamp
import pandas as pd

from nostalgia.test.TestCase import ExampleSource, TestCase
from src.common.meta.aspect.time import Time


class TimeTest(TestCase):

    def test_aspect_applied(self):
        sdf = ExampleSource().build_sdf()

        a = sdf.time
        self.assertEqual(a.iloc[0], Timestamp("2019-01-29 09:04:31"))
        self.assertEqual(a.iloc[-1], Timestamp("2019-02-11 11:59:56"))

    def test_create_aspect(self):
        df = pd.DataFrame([
            {
                "endTime": "2019-01-29 09:06",
            },
            {
                "endTime": "2019-01-30 09:11",
            },
            {
                "endTime": "2019-01-30 09:11",
            }
        ])
        time = Time.apply(df.endTime)
        print(time.dtype)
        # self.assertEqual()

    def test_infer_time(self):
        sdf = ExampleSource().build_sdf()
        sdf.infer_time()
        print(sdf)