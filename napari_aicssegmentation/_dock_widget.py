"""
This module is an example of a barebones QWidget plugin for napari

It implements the ``napari_experimental_provide_dock_widget`` hook specification.
see: https://napari.org/docs/dev/plugins/hook_specifications.html

Replace code below according to your needs.
"""
from aicssegmentation.core.pre_processing_utils import image_smoothing_gaussian_3d
from napari_plugin_engine import napari_hook_implementation
from qtpy.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel

"""
The class name here gets converted to title case and gets displayed as both the title of the
plugin window and the title displayed in the app menu dropdown.
"""
class AllenCellStructureSegmenter(QWidget):
    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer

        btn = QPushButton("Gaussian kernel size = 3.0")
        btn.clicked.connect(self._smooth_image)

        desc = QLabel("Click button to smooth the current viewport image,\n higher numbers blur more. Result is displayed as a new channel.")

        self.setLayout(QHBoxLayout())
        self.layout().addWidget(desc)
        self.layout().addWidget(btn)

    def _smooth_image(self):
        self.viewer.layers[0].data = image_smoothing_gaussian_3d(self.viewer.layers[0].data, sigma=3.0)


@napari_hook_implementation
def napari_experimental_provide_dock_widget():
    return AllenCellStructureSegmenter
