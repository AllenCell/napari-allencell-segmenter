from typing import List, NamedTuple, Union
from PyQt5.QtWidgets import (
    QComboBox,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QFrame,
    QFormLayout,
    QWidget,
    QHBoxLayout,
    QLayout,
)
from PyQt5.QtGui import QIcon
from PyQt5 import QtCore
from PyQt5.QtCore import QSize
from napari_aicssegmentation.model.segmenter_model import SegmenterModel
from napari_aicssegmentation.util.debug_utils import debug_class
from napari_aicssegmentation.controller._interfaces import IWorkflowSelectController
from napari_aicssegmentation.core.view import View
from napari_aicssegmentation.widgets.warning_message import WarningMessage
from napari_aicssegmentation.util.directories import Directories
from napari_aicssegmentation._style import PAGE_WIDTH, PAGE_CONTENT_WIDTH
from ._main_template import MainTemplate


class FormRow(NamedTuple):
    label: Union[str, QLabel]
    widget: QWidget


@debug_class
class WorkflowSelectView(View):

    combo_layers: QComboBox
    combo_channels: QComboBox
    load_image_warning: WarningMessage

    def __init__(self, controller: IWorkflowSelectController):
        super().__init__(template_class=MainTemplate)

        if controller is None:
            raise ValueError("controller")
        self._controller = controller
        self.setObjectName("workflowSelectView")

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Title
        workflow_selection_title = QLabel("Workflow selection steps:")
        workflow_selection_title.setObjectName("workflowSelectionTitle")

        # Warning
        self.load_image_warning = WarningMessage("Open a 3D image in Napari first!")
        self.load_image_warning.setVisible(False)

        # Dropdowns
        layers_dropdown = self._dropdown_row(1, "Select a 3D Napari image layer", enabled=False)
        self.combo_layers = layers_dropdown.widget
        self.combo_layers.currentIndexChanged.connect(self._combo_layers_index_changed)

        channels_dropdown = self._dropdown_row(2, "Select a 3D image data channel", enabled=False)
        self.combo_channels = channels_dropdown.widget
        layer_channel_selections = self._form_layout([layers_dropdown, channels_dropdown])

        # Add all widgets
        widgets = [
            workflow_selection_title,
            self.load_image_warning,
            layer_channel_selections,
        ]
        for widget in widgets:
            layout.addWidget(widget)
        self._add_step_3_layout(layout, enabled=False)

    def load_model(self, model: SegmenterModel):
        """
        Load and display data from model
        Inputs:
            model: the model to load
        """
        self.update_layers(model.layers, model.selected_layer_name)
        self.update_channels(model)
        self._load_workflows(model)

    def update_layers(self, layers: List[str], selected_layer_name: str = None):
        """
        Update / repopulate the list of selectable layers
        Inputs:
            layers: List of layer names
            selected_layer_name: (optional) name of the layer to pre-select
        """
        if layers is None or len(layers) == 0:
            self._reset_combo_box(self.combo_layers)
            self.load_image_warning.setVisible(True)
            self.combo_layers.setEnabled(False)
        else:
            self._reset_combo_box(self.combo_layers)
            self.combo_layers.addItems(layers)
            if selected_layer_name is not None:
                self.combo_layers.setCurrentText(selected_layer_name)
            self.combo_layers.setEnabled(True)
            self.load_image_warning.setVisible(False)

    def update_channels(self, channels: List[str]):
        """
        Update / repopulate the list of selectable channels
        Inputs:
            channels: List of channel names
        """
        # TODO load channels and update UI state -> https://github.com/AllenCell/napari-aicssegmentation/issues/24
        pass

    def _load_workflows(self, workflows):  # workflows: List[aicssegmentation.WorkflowStep]
        # TODO generate workflow grid from list of workflows
        # -> https://github.com/AllenCell/napari-aicssegmentation/issues/26
        pass

    def _reset_combo_box(self, combo: QComboBox):
        """
        Reset a combo box to its original state, keeping the header but removing all other items
        """
        if combo.count() > 0:
            header = combo.itemText(0)
            combo.clear()
            combo.addItem(header)

    def _dropdown_row(self, number: int, placeholder: str, enabled=False) -> FormRow:
        """
        Given the contents of a dropdown and a number for the label, return a label and a QComboBox
        widget that can be used to create a row in a QFormLayout
        """
        label = f"{number}."

        dropdown = QComboBox()
        dropdown.addItem(placeholder)
        dropdown.setDisabled(not enabled)

        return FormRow(label, dropdown)

    # TODO turn into an actual reusable widget if this is needed anywhere else
    def _form_layout(self, rows: List[FormRow], margins=(0, 5, 11, 0)) -> QFrame:
        """
        Create a nicely formatted form layout given contents to add as rows.

        Inputs:
            rows:       List of FormRow
            margins:    Tuple of 4 numbers representing left, top, right, and bottom margins for
                        the form's contents. Qt defaults to (11, 11, 11, 11).
        Output:
            A QFrame widget with a QFormLayout
        """
        widget = QFrame()
        layout = QFormLayout()
        layout.setFormAlignment(QtCore.Qt.AlignLeft)
        left, top, right, bottom = margins
        layout.setContentsMargins(left, top, right, bottom)

        for row in rows:
            layout.addRow(row.label, row.widget)
        widget.setLayout(layout)
        return widget

    def _add_step_3_layout(self, layout: QLayout, enabled=False):
        """
        Add widgets and set the layout for the Step 3 instructions and the workflow buttons
        """
        step_3_label = QLabel("3.")
        step_3_label.setAlignment(QtCore.Qt.AlignTop)
        step_3_instructions = QLabel(
            "Click a button below that most closely resembles your image channel to select & start a workflow"
        )
        step_3_instructions.setWordWrap(True)
        step_3 = self._form_layout([FormRow(step_3_label, step_3_instructions)], (0, 0, 11, 0))

        if enabled is False:
            step_3_instructions.setObjectName("step3InstructionsDisabled")
        layout.addWidget(step_3)

        # Row of text labeling the columns of workflow images
        column_labels = QWidget()
        column_layout = QHBoxLayout()
        column_layout.setContentsMargins(11, 11, 11, 0)
        column_labels.setLayout(column_layout)

        image_input_label = QLabel("Image input")
        image_input_label.setAlignment(QtCore.Qt.AlignCenter)
        segmentation_output_label = QLabel("Segmentation output")
        segmentation_output_label.setAlignment(QtCore.Qt.AlignCenter)
        column_labels.layout().addWidget(image_input_label)
        column_labels.layout().addWidget(segmentation_output_label)

        column_labels.setObjectName("columnLabels")
        column_labels.setFixedWidth(PAGE_CONTENT_WIDTH)

        if enabled is False:
            column_labels.setObjectName("columnLabelsDisabled")
        layout.addWidget(column_labels, alignment=QtCore.Qt.AlignCenter)

        # Workflow buttons
        image_files = (Directories.get_assets_dir() / "workflow_images").glob("*.png")
        for image_file in image_files:
            button = QPushButton("")
            button.setIcon(QIcon(str(image_file)))
            button.setIconSize(QSize(PAGE_CONTENT_WIDTH-40, 200))
            button.setFixedSize(PAGE_CONTENT_WIDTH, 200)
            if enabled is False:
                button.setDisabled(True)
            layout.addWidget(button, alignment=QtCore.Qt.AlignCenter)

    #####################################################################
    # Event handlers
    #####################################################################

    def _combo_layers_index_changed(self, index: int):
        if index == 0:  # index 0 is the dropdown header
            self._controller.unselect_layer()
        else:
            self._controller.select_layer(self.combo_layers.currentText())
