from typing import List, NamedTuple
from PyQt5.QtWidgets import QComboBox, QLabel, QPushButton, QVBoxLayout, QFrame, QFormLayout, QWidget, QHBoxLayout, QLayout
from PyQt5.QtGui import QIcon
from PyQt5 import QtCore
from PyQt5.QtCore import QSize
from napari_aicssegmentation.model.segmenter_model import SegmenterModel
from napari_aicssegmentation.util.debug_utils import debug_class
from napari_aicssegmentation.controller._interfaces import IWorkflowSelectController
from napari_aicssegmentation.core.view import View
from napari_aicssegmentation.widgets.warning_message import WarningMessage
from napari_aicssegmentation.util.directories import Directories
from ._main_template import MainTemplate

class FormRow(NamedTuple):
    label: str
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
        layers_dropdown = self._dropdown_row(1, "Select a 3D Napari image layer")
        self.combo_layers = layers_dropdown.widget    
        self.combo_layers.setEnabled(False)        
        self.combo_layers.currentIndexChanged.connect(self._combo_layers_index_changed)

        channels_dropdown = self._dropdown_row(2, "Select a 3D image data channel", True)
        self.combo_channels = channels_dropdown.widget
        self.combo_channels.setEnabled(False)
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
        if len(model.layer_list) == 0:
            self.load_image_warning.setVisible(True)
            self.combo_layers.setEnabled(False)
        else:
            self.combo_layers.addItems(model.layer_list)        
            self.combo_layers.setEnabled(True)      
            self.load_image_warning.setVisible(False)      
            #self.combo_channels.addItems(model.channel_list)
    
    def _combo_layers_index_changed(self, index: int):
        self._controller.select_layer(index) # TODO does index work here?
        # TODO repopulate channel list (in next story)
    
    def _dropdown_row(self, number: int, placeholder: str, enabled=True):
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
            rows:       List of dictionaries with this shape:
                            {
                                "label": string | QLabel,
                                "input": QWidget (e.g., QLabel, QComboBox)
                            }
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
    
    """ Add widgets and set the layout for the Step 3 instructions and the workflow buttons """
    def _add_step_3_layout(self, layout: QLayout, enabled=False):
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
        #column_labels.setFixedWidth(PAGE_CONTENT_WIDTH)

        image_input_label = QLabel("Image input")
        image_input_label.setAlignment(QtCore.Qt.AlignCenter)
        segmentation_output_label = QLabel("Segmentation output")
        segmentation_output_label.setAlignment(QtCore.Qt.AlignCenter)
        column_labels.layout().addWidget(image_input_label)
        column_labels.layout().addWidget(segmentation_output_label)

        column_labels.setObjectName("columnLabels")
        if enabled is False:
            column_labels.setObjectName("columnLabelsDisabled")
        layout.addWidget(column_labels, alignment=QtCore.Qt.AlignCenter)

        # Workflow buttons
        image_files = (Directories.get_assets_dir() / "workflow_images").glob("*.png")
        for image_file in image_files:
            button = QPushButton("")
            button.setIcon(QIcon(str(image_file)))
            button.setIconSize(QSize(360, 200)) # TODO possible to move sizes to stylesheet?
            button.setFixedSize(400, 200) # TODO possible to move sizes stylesheet?
            if enabled is False:
                button.setDisabled(True)
            layout.addWidget(button, alignment=QtCore.Qt.AlignCenter)    
