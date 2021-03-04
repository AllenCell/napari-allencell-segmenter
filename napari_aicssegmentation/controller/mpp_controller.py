import logging

from aicssegmentation.core.pre_processing_utils import image_smoothing_gaussian_3d
from napari_aicssegmentation.view.interfaces import IMppView
from napari_aicssegmentation.ui_manager import UIManager
from napari_aicssegmentation.controller.interfaces import IMppController
from napari_aicssegmentation.util.debug_utils import debug_class

log = logging.getLogger(__name__)

@debug_class
class MppController(IMppController):
    def __init__(self, ui_manager: UIManager, view: IMppView):
        if view is None:
            raise ValueError("view")
                
        self._view = view
        super().__init__(ui_manager)
    
    def run_gaussian_blur(self):        
        if self.ui_manager.is_image_loaded():
            
            viewer = self.ui_manager.viewer
            # Name to add based off previous image's name
            name = viewer.layers[len(viewer.layers) - 1].name + ": Gaussian Blur"

            # Adding the image to the viewer
            result = image_smoothing_gaussian_3d(viewer.layers[0].data, sigma=3.0)
            viewer.add_image(result, name=name)            
        else:
            self.ui_manager.show_message_box("Error: No Image", "Load an image before running gaussian blur")
