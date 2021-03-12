# Hook specifications: https://napari.org/docs/dev/plugins/hook_specifications.html
import napari

from napari_aicssegmentation.core.application import Application
from napari_aicssegmentation.util.debug_utils import debug_class
from napari_plugin_engine import napari_hook_implementation
from qtpy.QtWidgets import QComboBox, QLabel, QMessageBox, QPushButton, QTextEdit, QVBoxLayout, QWidget

from ._stylesheet import GLOBAL_STYLESHEET

"""
The class name here gets converted to title case and gets displayed as both the title 
of the plugin window and the title displayed in the app menu dropdown.
"""


@debug_class
class AllenCellStructureSegmenter(QWidget):  # pragma: no-cover
    def __init__(self, napari_viewer: napari.Viewer):
        super().__init__()
        self.viewer = napari_viewer
        self.setStyleSheet(GLOBAL_STYLESHEET)

        title = QLabel("Segmentation workflow selection")
        title.setWordWrap(True)
        title.setStyleSheet("QLabel { font-weight: bold; font-size: 20px; margin-bottom: 1em }")

        # Need to supply HTML because of this bug: https://bugreports.qt.io/browse/QTBUG-90853
        step_1 = QLabel("<span>1.&nbsp;Select a channel to segment:</span>")
        dropdown = QComboBox()
        dropdown.addItem("Channel 1")
        dropdown.addItem("Channel 2")
        dropdown.addItem("Channel 3")

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(title)
        self.layout().addWidget(step_1)
        self.layout().addWidget(dropdown)
        self.layout().addStretch()
    
    # def smooth_image(self):
    #     """Guassian Blur on an image, and add it as a new layer"""
    #     if self.has_image():
    #         # Name to add based off previous image's name
    #         name = (
    #             self.viewer.layers[len(self.viewer.layers) - 1].name + ": Guassian Blur"
    #         )

    #         # Adding the image to the viewer
    #         self.viewer.add_image(
    #             image_smoothing_gaussian_3d(self.viewer.layers[0].data, sigma=3.0),
    #             name=name,
    #         )
    #     else:
    #         self.show_message_box(
    #             "Error: No Image", "Load an image before running guassian blur"
    #         )

    # def has_image(self):
    #     """Determines if there is already an image loaded onto napari"""
    #     if len(self.viewer.layers) == 0:
    #         return False
    #     else:
    #         return True

    # def show_message_box(self, title, message):
    #     """Show a message box with the specified title and message"""
    #     msg = QMessageBox()
    #     msg.setWindowTitle(title)
    #     msg.setText(message)
    #     return msg.exec()


@napari_hook_implementation
def napari_experimental_provide_dock_widget():  # pragma: no-cover
    return AllenCellStructureSegmenter
