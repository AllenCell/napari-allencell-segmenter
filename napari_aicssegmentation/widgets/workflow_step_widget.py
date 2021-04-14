from typing import Dict, List, Any

# from aicssegmentation.structure_wrapper.WorkflowStep import WorkflowStep
from magicgui.widgets import FloatSlider, Slider
from qtpy.QtWidgets import QComboBox, QLabel, QVBoxLayout, QWidget

from napari_aicssegmentation.widgets.collapsible_box import CollapsibleBox


class WorkflowStepWidget(QWidget):
    """
    A widget wrapping a CollapsibleBox that contains all the parameter controls and other necessary
    child widgets for a given WorkflowStep

    Params:
        step (WorkflowStep): WorkflowStep object for this widget
    """

    # TODO: type step param as WorkflowStep
    def __init__(self, step):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)
        box_content_layout = QVBoxLayout()

        if len(step["function"]["parameters"]) == 0:
            box_content_layout.addWidget(QLabel("No parameters needed"))
        else:
            # Get all the separate parameters to put into this layout.
            for param_name, param_values in step["function"]["parameters"].items():
                self.create_param_widgets(box_content_layout, param_name, param_values)

        layout.addWidget(CollapsibleBox(step["display_name"], box_content_layout))

    def create_param_widgets(self, layout, param_name, param_values):
        # TODO: maybe do something to append a number to the label for a multi-value param
        for param_value in param_values:
            # Parse out type of widget to be added
            widget_type = param_value["widget_type"]
            # Slider
            if widget_type == "slider":
                self.add_slider(layout, key, single_param)
            # Drop Down
            elif widget_type == "drop-down":
                self.add_dropdown(layout, widget_info, key, single_param)

    def add_slider(self, layout, step, param_key, single_param):
        # Add a slider
        widget_values = dict()

        # Build dictionary of widget information (default value, min, max, increment)
        if step.parameters is not None:
            if isinstance(step.parameters[param_key], list):
                # if given two numbers for default value default to first value given
                default_val = step.parameters[param_key][0]
            else:
                default_val = step.parameters[param_key]
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
