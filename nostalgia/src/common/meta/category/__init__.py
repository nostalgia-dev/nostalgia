from abc import ABCMeta, abstractmethod


class Checkable(metaclass=ABCMeta):
    @abstractmethod
    def verify(self):
        pass



class Category(Checkable, metaclass=ABCMeta): pass