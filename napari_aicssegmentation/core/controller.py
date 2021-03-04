from abc import ABC, abstractmethod
from napari_aicssegmentation.ui_manager import UIManager


class Controller(ABC):
    def __init__(self, ui_manager: UIManager):
        if ui_manager is None:
            raise ValueError("ui_manager")
        self._ui_manager = ui_manager
    
    @property
    def ui_manager(self):
        return self._ui_manager
