import logging
from abc import ABC, abstractmethod
from ..ui_manager import UIManager
from .mpp_view import MppView
from .mpp_model import MppModel

log = logging.getLogger(__name__)

class BaseController(ABC):
    def __init__(self, ui_manager: UIManager): #TODO replace with UIManager?
        if ui_manager is None:
            raise ValueError("ui_manager")
        self._ui_manager = ui_manager
        self._bind()
    
    @property
    def ui_manager(self):
        return self._ui_manager

    @abstractmethod
    def _bind(self):
        pass        

    @abstractmethod
    def index(self):
        pass


class MppController(BaseController):
    def __init__(self, ui_manager: UIManager, model: MppModel, view: MppView):
        if model is None:
            raise ValueError("model")
        if view is None:
            raise ValueError("view")
        self._model = model
        self._view = view
        super().__init__(ui_manager)

    def _bind(self):
        self._view.on_gaussian_blur_clicked = self.handleRunGaussianBlur

    def index(self):
        self._view.present()

    #TODO @logException (@eventHandler)
    def handleRunGaussianBlur(self, e):        
        log.info("handleRunGaussionBlur")
        log.info(e)
        
        if self.ui_manager.is_image_loaded():
            
            viewer = self.ui_manager.viewer
            # Name to add based off previous image's name
            name = viewer.layers[len(viewer.layers) - 1].name + ": Gaussian Blur"

            # Adding the image to the viewer
            result = self._model.smooth_image(viewer.layers[0].data)
            viewer.add_image(result, name=name)            
        else:
            self.ui_manager.show_message_box("Error: No Image", "Load an image before running gaussian blur")
