import os

from napari_aicssegmentation.core.application import Application
from napari_aicssegmentation.util.debug_utils import debug_class
from napari_plugin_engine import napari_hook_implementation
from qtpy.QtCore import Qt, QSize
from qtpy.QtGui import QIcon, QPixmap
from qtpy.QtWidgets import QComboBox, QLabel, QMessageBox, QPushButton, QScrollArea, QTextEdit, QVBoxLayout, QWidget

from ._stylesheet import GLOBAL_STYLESHEET

DIR = os.path.dirname(__file__)

"""
The class name here gets converted to title case and gets displayed as both the title 
of the plugin window and the title displayed in the app menu dropdown.
"""

class AllenCellStructureSegmenter(QWidget):
    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer
        self.setStyleSheet(GLOBAL_STYLESHEET)

        # This widget is necessary because QScrollArea needs a child that is not AllenCellStructureSegmenter
        self.widget = QWidget()
        self.set_page_layout()

    def set_page_layout(self):
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.widget)
        self.widget.setLayout(QVBoxLayout())

        title = QLabel("Segmentation workflow selection")
        title.setStyleSheet(
            "QLabel { font-weight: bold; font-size: 20px; margin-top: 0.3em }")

        # Need to supply HTML because of this bug: https://bugreports.qt.io/browse/QTBUG-90853
        step_1 = QLabel("<span>1.&nbsp;Select a channel to segment:</span>")
        dropdown = QComboBox()
        dropdown.addItem("Channel 1")
        dropdown.addItem("Channel 2")
        dropdown.addItem("Channel 3")

        step_2 = QLabel(
            "<span>2.&nbsp;Select segmentation workflow.&nbsp;"
            "The image I want to segment most closely resembles <b>(click an image)</b>:</span>"
        )
        step_2.setWordWrap(True)

        column_labels = QLabel("Input image            Segmentation")
        column_labels.setStyleSheet("QLabel { font-size: 12px; font-weight: bold }")
        column_labels.setAlignment(Qt.AlignCenter)

        widgets = [title, step_1, dropdown, step_2, column_labels]

        image_files = os.listdir(os.path.join(DIR, '_assets/_workflow_images'))
        for image_file in image_files:
            # pixmap = QPixmap(os.path.join(DIR, '_assets/_workflow_images', image_file))
            button = QPushButton("")
            # button.setStyleSheet("QPushButton { background-image: url(os.path.join(DIR, '_assets/_workflow_images', image_file)) }")
            button.setIcon(QIcon(os.path.join(DIR, '_assets/_workflow_images', image_file)))
            button.setIconSize(QSize(200, 200))
            widgets.append(button)

        for widget in widgets:
            self.widget.layout().addWidget(widget)
        
        self.widget.layout().addStretch()
        
        scroll = QScrollArea()
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.widget)
        
        self.layout().addWidget(scroll)


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
