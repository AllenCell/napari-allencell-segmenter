from napari_aicssegmentation.core._interfaces import IApplication
from napari_aicssegmentation.view.mpp_view import MppView
from aicssegmentation.core.pre_processing_utils import image_smoothing_gaussian_3d
from napari_aicssegmentation.core.controller import Controller
from napari_aicssegmentation.util.debug_utils import debug_class
from ._interfaces import IMppController


@debug_class
class MppController(Controller, IMppController):  # pragma: no-cover
    def __init__(self, application: IApplication):
        super().__init__(application)

    def index(self):
        self.load_view(MppView(self))

    def run_gaussian_blur(self):
        if self.is_image_loaded():

            layers = self.get_layers()
            # Name to add based off previous image's name
            name = layers[len(layers) - 1].name + ": Gaussian Blur"

            # Adding the image to the viewer
            result = image_smoothing_gaussian_3d(layers[0].data, sigma=3.0)
            self.add_layer(result, name=name)
        else:
            self.show_message_box("Error: No Image", "Load an image before running gaussian blur")

    def navigate_next(self):
        self.router.workflow_selection()
