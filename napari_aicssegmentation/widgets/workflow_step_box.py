from aicssegmentation.structure_wrapper.WorkflowStep import WorkflowStep
from magicgui.widgets import FloatSlider, Slider
from qtpy.QtWidgets import QComboBox, QVBoxLayout

from napari_aicssegmentation.widgets.collapsible_box import CollapsibleBox


class WorkflowStepBox(CollapsibleBox):
    """
    A collapsible box widget containing all the parameter controls and other necessary
    child widgets for a given WorkflowStep

    Params:
        workflow_step (WorkflowStep): WorkflowStep object for this widget
    """

    def __init__(self, workflow_step: WorkflowStep):
        super().__init__()
        self.workflow_step = workflow_step
        workflow_info = workflow_step.widget_data
        box_contents = QVBoxLayout()

        # Get all the separate parameters to put into this layout.
        for param_key in workflow_info.param_info.keys():
            self.create_step_widget(box_contents, workflow_step, param_key)

        return CollapsibleBox(workflow_step.widget_data.display_name, box_contents)

    def create_step_widget(self, layout, workflow_step, param_key):
        # Get dictionary of information for this parameter
        param_vals = workflow_step.widget_data.param_info[param_key]

        # Sometimes one parameter has multiple inputs
        if isinstance(param_vals, list):
            # Split single param- multi inputs and treat as
            # multiple single inputs
            for single_param_val in param_vals:
                self.parse_param_and_add(layout, workflow_step, param_key, single_param_val)
        else:
            # One parameter with single input
            self.parse_param_and_add(layout, workflow_step, param_key, param_vals)

    def parse_param_and_add(self, layout, workflow_step, key, single_param):
        # Parse out type of widget to be added
        widget_type = single_param["widget_type"]
        # Slider
        if widget_type == "slider":
            self.add_slider(layout, workflow_step, key, single_param)
        # # Drop Down
        # elif widget_type == "drop-down":
        #     add_dropdown(layout, widget_info, key, single_param)

    def add_slider(self, layout, workflow_step, param_key, single_param):
        # Add a slider
        widget_values = dict()

        # Build dictionary of widget information (default value, min, max, increment)
        if workflow_step.parameters is not None:
            if isinstance(workflow_step.parameters[param_key], list):
                # if given two numbers for default value default to first value given
                default_val = workflow_step.parameters[param_key][0]
            else:
                default_val = workflow_step.parameters[param_key]
            widget_values["value"] = default_val
        if "max" in single_param:
            widget_values["max"] = single_param["max"]
        if "min" in single_param:
            widget_values["min"] = single_param["min"]
        if "increment" in single_param:
            widget_values["step"] = single_param["increment"]

        # Sometimes default values are less than min or greater than max?
        if widget_values["value"] < widget_values["min"]:
            widget_values["value"] = widget_values["min"]
        if widget_values["value"] > widget_values["max"]:
            widget_values["value"] = widget_values["max"]

        # Determine which type of slider to use based on data type
        # and unpack dictionary with slider info and feed when initializing
        widget = None
        if single_param["data_type"] == "float":
            widget = FloatSlider(**widget_values)
        if single_param["data_type"] == "int":
            widget = Slider(**widget_values)

        layout.addRow(param_key, widget.native)

    def add_dropdown(self, layout, widget_info, param_key, param_vals):
        dropdown = QComboBox()
        dropdown.addItem("test")
        layout.addWidget(dropdown)
