from abc import ABC, abstractmethod
from PyQt5.QtWidgets import QWidget

class ViewMeta(type(QWidget), type(ABC)):
    pass

class View(ABC, QWidget, metaclass=ViewMeta):
    """
    Base View
    """

    @abstractmethod
    def setup_ui(self):        
        pass
