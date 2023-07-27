from abc import ABCMeta, abstractmethod

class Asset(metaclass = ABCMeta):

    @abstractmethod
    def to_tuple(self):
        pass
