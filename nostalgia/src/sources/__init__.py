from abc import ABCMeta
from abc import *
from collections import defaultdict
from datetime import datetime

import just

from nostalgia import NDF
import pandas as pd

from src.common.meta.aspect import Aspect


class Vendor(metaclass=ABCMeta):
    @property
    def vendor(self):
        return self.__class__.__name__

    ingest_settings = {
        "ingest_glob": "~/Downloads/takeout-20*-*.zip",
        "recent_only": False,
        "delete_existing": False,
    }


class Source(Vendor, metaclass=ABCMeta):

    @property
    @abstractmethod
    def category(self) -> list:
        pass

    @property
    @abstractmethod
    def aspects(self) -> dict:
        pass

    @property
    def data_path(self):
        return "~/nostalgia_data/input/"


    def download(self, start_time: datetime = None, end_time: datetime = None, **kwargs) -> str:
        """
        This method is used for retrieving data from some external resource.
        That can be some API, parsed page etc.
        @param start_time:
        @param end_time:
        @param kwargs:
        @return: csv, json or xml format string
        """
        return ""

    @abstractmethod
    def ingest(self, delta_data, **kwargs):
        """
        TODO what exactly should it do and why we should expose it
        Data will be stored in internal long-running storage.
        It's recommended to save data as it is without any modifications.
        Nostalgia will use that method for scheduled updates of historical data.
        If your datasource supports time range, please use start_time and end_time, so Nostalgia can download your data
        more granularly.

        auth, compress and secure should be handled here

        @return:
        """
        pass

    @abstractmethod
    def load(self, data) -> pd.DataFrame:
        """
        This method should return marked Source Data Frame
        Mandatory: specify one of columns with Time aspect
        Also please provide any other Aspect marks on columns to allow Nostalgia to interconnect SDFs more tightly.
        @return: pd.DataFrame
        """
        pass

    def verify(self, df: NDF):
        """
        Check basic stuff:
            mandatory aspect (time), correct dates
            shape of df
            presence of values
        Each aspect.check()
        Each category.check()
        @param df:
        @return:
        """

        return df

    def __resolve_aspects(self, sdf: pd.DataFrame):
        aspects = self.aspects if isinstance(self.aspects, defaultdict) else defaultdict(lambda: Aspect, **self.aspects)
        columns = sdf.columns.to_list()
        for column in columns:
            aspects[column](sdf[column])

        return sdf

    def __resolve_categories(self, sdf: pd.DataFrame):
        sdf.__class__.__bases__ = tuple(sdf.__class__.__bases__ + tuple(self.category))
        return sdf

    def __resolve_meta(self, sdf: pd.DataFrame):
        return self.__resolve_categories(self.__resolve_aspects(sdf))

    def build_source_dataframe(self) -> NDF:
        # Here it should be decided if it's needed to download data,
        """
        download new data
        ingest data - compact data and store into long storage without date intersections
        load data - mark data, convert columns and clean it to make work easier
        verify result dataframe before putting it into regustry
        @return:
        """
        downloaded_data = self.download()
        data = self.ingest(downloaded_data)
        sdf = self.load(data)
        #inspect sdf categories and aspects
        sdf = self.__resolve_meta(sdf)
        ndf = NDF(sdf)

        ndf = self.verify(ndf)
        return ndf

    def resolve_filename(self, file: str) -> str:
        return "%s/%s/%s" % (self.data_path, self.vendor, file)

    def read_file(self, file: str) -> list:
        return just.multi_read(self.resolve_filename(file)).values()

