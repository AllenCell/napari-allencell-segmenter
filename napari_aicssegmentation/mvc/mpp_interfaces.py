from abc import ABC, abstractmethod
from napari_aicssegmentation.core.base_controller import Controller
from napari_aicssegmentation.core.base_view import View
from napari_aicssegmentation.ui_manager import UIManager

class IMppController(Controller):
    @abstractmethod
    def run_gaussian_blur(self):
        pass

    @abstractmethod
    def index(self):
        pass    

class IMppView(View):
    pass