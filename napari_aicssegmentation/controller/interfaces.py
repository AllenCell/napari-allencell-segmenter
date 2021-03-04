from abc import abstractmethod
from napari_aicssegmentation.core.controller import Controller

class IMppController(Controller):
    @abstractmethod
    def run_gaussian_blur(self):
        pass 