
from qtpy.QtCore import Qt

from napari_aicssegmentation.widgets.collapsible_box import CollapsibleBox
from qtpy.QtWidgets import QFormLayout, QLabel, QSlider, QDoubleSpinBox
from aicssegmentation.structure_wrapper.WorkflowStep import WorkflowStep
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

        with open(r'C:\Users\brian\code\work\aics-segmentation\aicssegmentation\structure_wrapper_config\all_functions.json') as file:
            widget_info = json.load(file)
        workflow_step = WorkflowStep(test_dict, widget_info)
    # Test code end


    param_info = workflow_step.widget_data["parameter"]
    widget = QFormLayout()

    for param_name, param_vals in param_info.items():
        create_step_widget(widget, param_name, param_vals)

    return CollapsibleBox(workflow_step.name, widget)



def create_step_widget(layout, param_name, param_vals):
    param_label = QLabel(param_name)
    layout.addRow(param_label)
    if isinstance(param_vals, list):
        for single_param in param_vals:
            parse_param_and_add(layout, single_param)
    else:
        parse_param_and_add(layout, param_vals)


def parse_param_and_add(layout, single_param):
    if single_param["widget_type"] == "slider":
        add_slider(layout)

def add_slider(layout):
    # TODO: basic version for now, need to implement min, max, and data types
    spinbox = QDoubleSpinBox()
    layout.addRow(spinbox)
