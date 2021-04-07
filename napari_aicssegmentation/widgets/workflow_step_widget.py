
from qtpy.QtCore import Qt

from napari_aicssegmentation.widgets.collapsible_box import CollapsibleBox
from qtpy.QtWidgets import QFormLayout, QLabel, QSlider, QDoubleSpinBox
from aicssegmentation.structure_wrapper.WorkflowStep import WorkflowStep
from magicgui.widgets import FloatSlider, Slider
import json

def generate_workflow_widget(workflow_step: WorkflowStep) -> CollapsibleBox:
    """
    Using a WorkflowStep object, generate return a QVBox
    for that step

    Params:
        workflow_step (WorkflowStep): WorkflowStep object for
            this widget

    Returns:
        widget (CollapsibleBox): A widget filled with information
            for that step, parameters, and default values.
    """
    # Test code
    if workflow_step == "test":
        test_dict = dict()
        test_dict["name"] = "intensity_normalization"
        test_dict["module"] = "aicssegmentation.core.pre_processing_utils"
        test_dict["function"] = "intensity_normalization"
        test_dict["parent"] = 0
        test_dict["parameter"] = {"scaling_param": [3, 15]}
        workflow_step = WorkflowStep(test_dict)
    # Test code end


    widget_info = workflow_step.widget_data
    widget = QFormLayout()

    for param_key in widget_info.param_info.keys():
        create_step_widget(widget, widget_info, param_key)

    return CollapsibleBox(workflow_step.name, widget)



def create_step_widget(layout, widget_info, param_key):
    param_label = QLabel(widget_info.function_name)
    layout.addRow(param_label)

    param_vals = widget_info.param_info[param_key]

    if isinstance(param_vals, list):
        for single_param_val in param_vals:
            parse_param_and_add(layout, widget_info, param_key, single_param_val)
    else:
        parse_param_and_add(layout, widget_info, param_key, param_vals)


def parse_param_and_add(layout, widget_info, key, single_param):
    widget_type = single_param["widget_type"]
    if widget_type == "slider":
        add_slider(layout, widget_info, key, single_param)
    elif widget_type == "drop-down":
        add_dropdown(layout, widget_info, key, single_param)


def add_slider(layout, widget_info, param_key, single_param):
    # TODO: basic version for now, need to implement min, max, and data types
    spinbox = QDoubleSpinBox()
    widget_values = dict()

    if widget_info.parameter_defaults is not None:
        if isinstance(widget_info.parameter_defaults[param_key], list):
            default_val = widget_info.parameter_defaults[param_key][0]
        else:
            default_val = widget_info.parameter_defaults[param_key]
        widget_values["value"] = default_val
    if "max" in single_param:
        widget_values["max"] = single_param["max"]
    if "min" in single_param:
        widget_values["min"] = single_param["min"]
    if "increment" in single_param:
        widget_values["step"] = single_param["increment"]

    widget = None
    if single_param["data_type"] == "float":
        widget = FloatSlider(**widget_values)
    if single_param["data_type"] == "int":
        widget = Slider(**widget_values)


    layout.addRow(widget.native)



