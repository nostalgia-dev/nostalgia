import unittest
# also use doctest
from pandas._libs.tslibs.timestamps import Timestamp

from nostalgia.test.TestCase import ExampleSource


class TimeTest(unittest.TestCase):

    def test_aspect_applied(self):
        sdf = ExampleSource().build_sdf()

        a = sdf.time
        self.assertEqual(a.iloc[0], Timestamp("2019-01-29 09:04:31"))
        self.assertEqual(a.iloc[-1], Timestamp("2019-02-11 11:59:56"))

