import unittest

from nostalgia.src.common.meta.category.services.music import Music
from datetime import datetime
import json

# also use doctest
from nostalgia.test.TestCase import ExampleSource


class SourceTest(unittest.TestCase):
    def test_download(self):
        start = datetime.strptime("2019-02-11 00:00", "%Y-%m-%d %H:%M")
        end = datetime.strptime("2019-02-11 23:59", "%Y-%m-%d %H:%M")
        data = ExampleSource().download(start_time=start, end_time=end)
        self.assertIsInstance(data, str)

    def test_ingest(self):
        ExampleSource().ingest()

    def test_create_sdf(self):
        sdf = ExampleSource().build_sdf()
        self.assertEqual(sdf.shape[0], 162)
        self.assertEqual(sdf.category, [Music])
        # self.assertEqual(sdf.aspects, [Time, Title])
