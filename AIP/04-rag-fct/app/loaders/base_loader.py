from abc import ABC, abstractmethod

class Baseloader(ABC):
    @abstractmethod
    def load(self):
        pass