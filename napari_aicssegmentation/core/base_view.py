from abc import ABC, abstractmethod

class View(ABC):
    @abstractmethod
    def get_layout(self):
        pass

    @abstractmethod
    def setup_ui(self):
        pass