import os

from napari_plugin_engine import napari_hook_implementation
from qtpy.QtCore import Qt, QSize
from qtpy.QtGui import QIcon
from qtpy.QtWidgets import QComboBox, QLabel, QPushButton, QScrollArea, QVBoxLayout, QWidget

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
        self.setLayout(QVBoxLayout())

        # Add page widget that holds all other widgets except for the scroll bar
        self.page = QWidget()
        self.page.setStyleSheet("QWidget { margin-right: 20px }")
        self.set_page_layout()
        self.layout().addWidget(self.page)
        
        # Add scroll widget that holds the page widget
        scroll = QScrollArea()
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.page)
        self.layout().addWidget(scroll)

    """ Add widgets to the page and set the layout """
    def set_page_layout(self):
        self.page.setLayout(QVBoxLayout())

        title = QLabel("Segmentation workflow selection")
        title.setStyleSheet(
            "QLabel { font-weight: bold; font-size: 20px; margin-top: 0px }")

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

        # This is hacky but not sure if it's worth creating a grid just for this row
        column_labels = QLabel("Input image                               Segmentation")
        column_labels.setStyleSheet("QLabel { font-size: 12px; font-weight: bold }")
        column_labels.setAlignment(Qt.AlignCenter)

        widgets = [title, step_1, dropdown, step_2, column_labels]
        for widget in widgets:
            self.page.layout().addWidget(widget)

        image_dir = os.path.join(DIR, '_assets/_workflow_images')
        image_files = os.listdir(image_dir)
        for image_file in image_files:
            button = QPushButton("")
            button.setIcon(QIcon(os.path.join(image_dir, image_file)))
            button.setIconSize(QSize(360, 200))
            button.setFixedSize(400, 200)
            self.page.layout().addWidget(button, alignment=Qt.AlignCenter)
        
        self.page.layout().addStretch()

@napari_hook_implementation
def napari_experimental_provide_dock_widget():  # pragma: no-cover
    return AllenCellStructureSegmenter
