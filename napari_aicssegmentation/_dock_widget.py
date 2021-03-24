import os

from napari_plugin_engine import napari_hook_implementation
from qtpy.QtCore import Qt, QSize
from qtpy.QtGui import QIcon
from qtpy.QtWidgets import (
    QComboBox, 
    QFrame,
    QLabel, 
    QPushButton, 
    QScrollArea, 
    QVBoxLayout, 
    QWidget
)

from napari_aicssegmentation._custom_widgets import warning_message, form_layout
from napari_aicssegmentation._stylesheet import STYLESHEET

DIR = os.path.dirname(__file__)

"""
The class name here gets converted to title case and gets displayed as both the title 
of the plugin window and the title displayed in the app menu dropdown.
"""


class AllenCellStructureSegmenter(QWidget):
    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer
        self.setLayout(QVBoxLayout())

        # Add page widget that holds all other widgets except for the scroll bar
        self.page = QFrame()
        self.page.setObjectName("page")
        self.set_page_layout()
        self.layout().addWidget(self.page)

        # Add scroll widget that holds the page widget
        scroll = QScrollArea()
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.page)
        self.layout().addWidget(scroll)

        self.setStyleSheet(STYLESHEET)

    """ Add widgets to the page and set the layout """
    def set_page_layout(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(11, 0, 11, 11)
        self.page.setLayout(layout)

        header = QLabel(
            """
            <span>
                <b>ALLEN CELL & STRUCTURE SEGMENTER</b><br/>
                v1.0 supports static 3D images only
            </span>
            """
        )
        header.setObjectName("header")
        header.setAlignment(Qt.AlignCenter)

        workflow_selection_title = QLabel("Workflow selection steps:")
        workflow_selection_title.setObjectName("workflowSelectionTitle")

        load_image_warning = warning_message("Open a 3D image in Napari first!")

        layers = ["Layer 1", "Layer 2", "Layer 3"]
        layers_dropdown = self.dropdown_row(1, "Select a 3D Napari image layer", layers)
        channels = ["Channel 1", "Channel 2", "Channel 3"]
        channels_dropdown = self.dropdown_row(2, "Select a 3D image data channel", channels, False)
        layer_channel_selections = form_layout([layers_dropdown, channels_dropdown])

        widgets = [
            header,
            workflow_selection_title,
            load_image_warning,
            layer_channel_selections,
        ]
        for widget in widgets:
            self.page.layout().addWidget(widget)

        self.set_step_3_layout()
        self.page.layout().addStretch()

    def dropdown_row(self, number, placeholder, options, enabled=True):
        label = f"{number}."

        dropdown = QComboBox()
        dropdown.addItem(placeholder)
        for option in options:
            dropdown.addItem(option)
        dropdown.setMinimumWidth(360)
        if enabled == False:
            dropdown.setDisabled(True)

        return {
            "label": label,
            "input": dropdown
        }
    
    def set_step_3_layout(self, enabled=False):
        step_3_instructions = QLabel("Choose a segmentation workflow")
        step_3_args = {
            "label": "3.",
            "input": step_3_instructions
        }
        step_3 = form_layout([step_3_args], (0, 0, 11, 0))
        
        button_instructions = QLabel(
            "Click a button that most closely resembles your image channel to start a workflow."
        )
        button_instructions.setWordWrap(True)
        button_instructions.setIndent(37)
        if enabled == False:
            step_3_instructions.setObjectName("step3InstructionsDisabled")
            button_instructions.setObjectName("btnInstructionsDisabled")

        self.page.layout().addWidget(step_3)
        self.page.layout().addWidget(button_instructions)

        # This is hacky but not sure if it's worth creating a grid just for this row
        column_labels = QLabel("Input image                               Segmentation")
        column_labels.setObjectName("columnLabels")
        column_labels.setAlignment(Qt.AlignCenter)
        if enabled == False:
            column_labels.setObjectName("columnLabelsDisabled")
        self.page.layout().addWidget(column_labels)

        workflow_image_dir = os.path.join(DIR, "assets/workflow_images")
        image_files = os.listdir(workflow_image_dir)
        for image_file in image_files:
            button = QPushButton("")
            button.setIcon(QIcon(os.path.join(workflow_image_dir, image_file)))
            button.setIconSize(QSize(360, 200))
            button.setFixedSize(400, 200)
            if enabled == False:
                button.setDisabled(True)
            self.page.layout().addWidget(button, alignment=Qt.AlignCenter)



@napari_hook_implementation
def napari_experimental_provide_dock_widget():  # pragma: no-cover
    return AllenCellStructureSegmenter
