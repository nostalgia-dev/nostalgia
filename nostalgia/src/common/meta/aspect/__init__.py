from abc import ABCMeta
from typing import Callable

import pandas as pd

class Aspect(metaclass=ABCMeta):
    @classmethod
    def apply(cls, series: pd.Series):
        return series

    # @classmethod
    # def lambda_function(cls, func) -> Callable:
    #     return ???

    def verify(self):
        pass