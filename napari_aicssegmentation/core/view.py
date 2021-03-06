from abc import ABC, abstractmethod
from ._interfaces import IApplication

class View(ABC):
    # TODO maybe? 
    # def __init__(application: IApplication):
    #     if application is None:
    #         raise ValueError("application")
    #     self._application = application

    @abstractmethod
    def get_layout(self):
        pass

    @abstractmethod
    def setup_ui(self):
        pass