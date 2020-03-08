from abc import ABCMeta

import pandas as pd

class Aspect(metaclass=ABCMeta):
    @classmethod
    def apply(cls, series: pd.Series):
        return series

    def verify(self):
        pass