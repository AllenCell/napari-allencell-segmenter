from abc import ABC, abstractmethod
from napari_aicssegmentation.core.controller import Controller
from napari_aicssegmentation.core.view import View
from napari_aicssegmentation.ui_manager import UIManager

class IMppController(Controller):
    @abstractmethod
    def run_gaussian_blur(self):
        pass 

class IMppView(View):
    pass