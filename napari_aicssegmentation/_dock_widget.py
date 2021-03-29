from pathlib import Path

from napari_plugin_engine import napari_hook_implementation
from qtpy.QtCore import Qt, QSize
from qtpy.QtGui import QIcon
from qtpy.QtWidgets import (
    QComboBox, 
    QFrame,
    QHBoxLayout,
    QLabel, 
    QPushButton, 
    QScrollArea, 
    QVBoxLayout, 
    QWidget
)

from napari_aicssegmentation.widgets.collapsible_panel import CollapsiblePanel
from napari_aicssegmentation._custom_widgets import warning_message, form_layout
from napari_aicssegmentation._style_constants import (
    PAGE_WIDTH, 
    PAGE_CONTENT_WIDTH, 
    WORKFLOW_BUTTON_HEIGHT, 
    STYLESHEET
)

DIR = Path.cwd() / "napari_aicssegmentation"

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
        self.page.setFixedWidth(PAGE_WIDTH)
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
        layout.setContentsMargins(11, 0, 11, 11)    # 11 is Qt default
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
        show_warning = False    # To be replaced with a real event listener
        if show_warning is False:
            load_image_warning.hide()

        # Dropdowns
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
        self.add_demo_widgets()

        self.page.layout().addStretch()

    """
    Given the contents of a dropdown and a number for the label, return a label and a QComboBox
    widget that can be used to create a row in a QFormLayout
    """
    def dropdown_row(self, number, placeholder, options, enabled=True):
        label = f"{number}."

        dropdown = QComboBox()
        dropdown.addItem(placeholder)
        for option in options:
            dropdown.addItem(option)
        dropdown.setMinimumWidth(PAGE_CONTENT_WIDTH - 40)
        if enabled is False:
            dropdown.setDisabled(True)

        return {
            "label": label,
            "input": dropdown
        }
    
    """ Add widgets and set the layout for the Step 3 instructions and the workflow buttons """
    def set_step_3_layout(self, enabled=False):
        step_3_label = QLabel("3.")
        step_3_label.setAlignment(Qt.AlignTop)
        step_3_instructions = QLabel(
            "Click a button below that most closely resembles your image channel to select & start a workflow"
        )
        step_3_instructions.setWordWrap(True)
        step_3_args = {
            "label": step_3_label,
            "input": step_3_instructions
        }
        step_3 = form_layout([step_3_args], (0, 0, 11, 0))

        if enabled is False:
            step_3_instructions.setObjectName("step3InstructionsDisabled")
        self.page.layout().addWidget(step_3)

        # Row of text labeling the columns of workflow images

        column_labels = QWidget()
        column_layout = QHBoxLayout()
        column_layout.setContentsMargins(11, 11, 11, 0)
        column_labels.setLayout(column_layout)
        column_labels.setFixedWidth(PAGE_CONTENT_WIDTH)

        image_input_label = QLabel("Image input")
        image_input_label.setAlignment(Qt.AlignCenter)
        segmentation_output_label = QLabel("Segmentation output")
        segmentation_output_label.setAlignment(Qt.AlignCenter)
        column_labels.layout().addWidget(image_input_label)
        column_labels.layout().addWidget(segmentation_output_label)

        column_labels.setObjectName("columnLabels")
        if enabled is False:
            column_labels.setObjectName("columnLabelsDisabled")
        self.page.layout().addWidget(column_labels, alignment=Qt.AlignCenter)

        # Workflow buttons

        image_files = Path(DIR / "assets/workflow_images").glob("*.png")
        for image_file in image_files:
            button = QPushButton("")
            button.setIcon(QIcon(str(image_file)))
            button.setIconSize(QSize(PAGE_CONTENT_WIDTH - 40, WORKFLOW_BUTTON_HEIGHT))
            button.setFixedSize(PAGE_CONTENT_WIDTH, WORKFLOW_BUTTON_HEIGHT)
            if enabled is False:
                button.setDisabled(True)
            self.page.layout().addWidget(button, alignment=Qt.AlignCenter)
    
    def add_demo_widgets(self):
        self.page.layout().addWidget(
            CollapsiblePanel(1, "Intensity normalization", [QLabel("Test")], isOpen=False, isEnabled=True)
        )
        self.page.layout().addWidget(
            CollapsiblePanel(2, "Smoothing", [QLabel("Test")], isOpen=True, isEnabled=True)
        )
        self.page.layout().addWidget(
            CollapsiblePanel(3, "2D filament filter", [QLabel("Test")], isOpen=False, isEnabled=False)
        )


@napari_hook_implementation
def napari_experimental_provide_dock_widget():  # pragma: no-cover
    return AllenCellStructureSegmenter
