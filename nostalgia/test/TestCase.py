import unittest

import pytest
from datetime import datetime
import json
from datetime import datetime
from unittest.mock import MagicMock

# also use doctest
import pandas as pd

from src.common.infrastructure.utils import Functional
from src.common.meta.aspect.time import Time
from src.common.meta.aspect.title import Title
from src.common.meta.category.services.music import Music
from src.sources import Source
import os
import pathlib


class ExternalApi:
    """
    This class imitates external api, that provides data
    """

    @classmethod
    def download(cls, start_time: datetime = None, end_time: datetime = None, **kwargs):
        response = []
        if not start_time:
            start_time = datetime.fromtimestamp(0)
        if not end_time:
            end_time = datetime.now()
        with open("../../resources/test_data/example_source/data_to_download.json") as download:
            response = [
                x for x in json.loads(download.read())
                if start_time < datetime.strptime(x["endTime"], "%Y-%m-%d %H:%M") < end_time
            ]
        return json.dumps(response)


class ExampleSource(Source):

    @property
    def category(self) -> list:
        return [Music]

    @property
    def aspects(self) -> dict:
        return {
            'time_start': Time.of_duration("time_end", "seconds_listened", duration_unit='s'),
            'time_end': Time,
            'title': Title
        }

    def download(self, start_time: datetime = None, end_time: datetime = None, **kwargs) -> str:
        return ExternalApi.download(start_time, end_time)

    def ingest(self, delta_data, **kwargs):
        self.resolve_filename = MagicMock(
            return_value=TestCase.resources_path() / "test_data/example_source/ingested_data.json")
        file = self.read_file("")
        return file

    def load(self, data) -> pd.DataFrame:
        return pd.DataFrame([(
            x["endTime"],
            x["trackName"],
            x["artistName"],
            x["msPlayed"] // 1000
        ) for x in Functional.flatten(data)],
            columns=["time_end", "title", "artist", "seconds_listened"]
        )


class TestCase(unittest.TestCase):

    @classmethod
    def resources_path(cls):
        return (pathlib.Path(__file__).parent / 'resources').absolute()
