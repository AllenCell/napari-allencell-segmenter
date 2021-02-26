from abc import ABC, abstractmethod
from napari_aicssegmentation.ui_manager import UIManager

class BaseController(ABC):
    def __init__(self, ui_manager: UIManager):
        if ui_manager is None:
            raise ValueError("ui_manager")
        self._ui_manager = ui_manager
    
    @property
    def ui_manager(self):
        return self._ui_manager

    @abstractmethod
    def index(self):
        pass

class IMppController(BaseController):
    @abstractmethod
    def run_gaussian_blur(self):
        pass

    @abstractmethod
    def index(self):
        pass    

class IMppView(ABC):
    @abstractmethod
    def present(self):
        pass