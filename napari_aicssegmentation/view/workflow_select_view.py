from typing import List
from napari.layers.base.base import Layer
from PyQt5.QtWidgets import (
    QComboBox,
    QLabel,
    QVBoxLayout,
    QWidget,
    QHBoxLayout,
    QLayout,
)
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5 import QtCore
from napari_aicssegmentation.model.channel import Channel
from napari_aicssegmentation.model.segmenter_model import SegmenterModel
from napari_aicssegmentation.util.debug_utils import debug_class
from napari_aicssegmentation.controller._interfaces import IWorkflowSelectController
from napari_aicssegmentation.core.view import View
from napari_aicssegmentation.widgets.form import Form, FormRow
from napari_aicssegmentation.widgets.warning_message import WarningMessage
from napari_aicssegmentation.util.ui_utils import UiUtils
from napari_aicssegmentation._style import PAGE_CONTENT_WIDTH
from napari_aicssegmentation.widgets.workflow_thumbnails import WorkflowThumbnails
from aicssegmentation.workflow.workflow_definition import WorkflowDefinition
from ._main_template import MainTemplate

@debug_class
class WorkflowSelectView(View):

    combo_layers: QComboBox
    combo_channels: QComboBox
    load_image_warning: WarningMessage
    workflow_grid: WorkflowThumbnails

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
        layers_dropdown = UiUtils.dropdown_row("1.", "Select a 3D Napari image layer", enabled=False)
        self.combo_layers = layers_dropdown.widget
        self.combo_layers.activated.connect(self._combo_layers_activated)

        channels_dropdown = UiUtils.dropdown_row("2.", "Select a 3D image data channel", enabled=False)
        self.combo_channels = channels_dropdown.widget
        self.combo_channels.activated.connect(self._combo_channels_activated)

        layer_channel_selections = QWidget()
        layer_channel_selections.setLayout(Form([layers_dropdown, channels_dropdown]))

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
        self.update_layers(model.layers, model.selected_layer)
        self.update_channels(model.channels, model.selected_channel)
        self._load_workflows(model.workflows)

    def update_layers(self, layers: List[str], selected_layer: Layer = None):
        """
        Update / repopulate the list of selectable layers
        Inputs:
            layers: List of layer names
            selected_layer_name: (optional) name of the layer to pre-select
        """
        self._reset_combo_box(self.combo_layers)

        if layers is None or len(layers) == 0:
            self.load_image_warning.setVisible(True)
            self.combo_layers.setEnabled(False)
        else:
            self.combo_layers.addItems(layers)
            if selected_layer is not None:
                self.combo_layers.setCurrentText(selected_layer.name)
            self.combo_layers.setEnabled(True)
            self.load_image_warning.setVisible(False)

    def update_channels(self, channels: List[Channel], selected_channel: Channel = None):
        """
        Update / repopulate the list of selectable channels
        Inputs:
            channels: List of channel names
        """
        self._reset_combo_box(self.combo_channels)

        if channels is None or len(channels) == 0:
            self.combo_channels.setEnabled(False)
        else:
            model = QStandardItemModel()
            model.appendRow(QStandardItem(self.combo_channels.itemText(0)))

            for channel in channels:
                item = QStandardItem(channel.display_name)
                item.setData(channel, QtCore.Qt.UserRole)
                model.appendRow(item)

            self.combo_channels.setModel(model)

            if selected_channel is not None:
                # TODO relying on display name isn't the best as it will probably
                #      cause issues if channel names aren't unique
                # TODO refactor by making Channel derive from QStandardItem and do something like this:
                #      selected_index = model.indexFromItem(selected_channel)
                #      self.combo_channels.setCurrentIndex(selected_index)
                self.combo_channels.setCurrentText(selected_channel.display_name)

            self.combo_channels.setEnabled(True)

    def update_workflows(self, enabled: bool):
        """
        Update state of workflow list
        Inputs:
            enabled: True to enable the list, False to disable it
        """
        self.workflow_grid.setEnabled(enabled)

    def _load_workflows(self, workflows: List[WorkflowDefinition]):
        """
        Load workflows into workflow grid
        """
        self.workflow_grid.load_workflows(workflows)

    def _reset_combo_box(self, combo: QComboBox):
        """
        Reset a combo box to its original state, keeping the header but removing all other items
        """
        if combo.count() > 0:
            header = combo.itemText(0)
            combo.clear()
            combo.addItem(header)

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
        step_3 = QWidget()
        step_3.setLayout(Form([FormRow(step_3_label, step_3_instructions)], (0, 0, 11, 0)))

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

        # Add workflow buttons        
        self.workflow_grid = WorkflowThumbnails()
        layout.addWidget(self.workflow_grid)         

    #####################################################################
    # Event handlers
    #####################################################################

    def _combo_layers_activated(self, index: int):
        if index == 0:  # index 0 is the dropdown header
            self._controller.unselect_layer()
        else:
            self._controller.select_layer(self.combo_layers.itemText(index))

    def _combo_channels_activated(self, index: int):
        if index == 0:
            self._controller.unselect_channel()
        else:
            self._controller.select_channel(self.combo_channels.itemData(index, role=QtCore.Qt.UserRole))
