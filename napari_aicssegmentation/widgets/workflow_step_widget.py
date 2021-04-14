# from aicssegmentation.structure_wrapper.WorkflowStep import WorkflowStep
from magicgui.widgets import FloatSlider, Slider
from qtpy.QtWidgets import QLabel, QVBoxLayout, QWidget

from napari_aicssegmentation.widgets.collapsible_box import CollapsibleBox
from napari_aicssegmentation.widgets.form import Form, FormRow
from napari_aicssegmentation.util.ui_utils import UiUtils


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
        self.form_rows = []

        layout = QVBoxLayout()
        self.setLayout(layout)

        if len(step["function"]["parameters"]) == 0: # or is not None?
            self.form_rows.append(FormRow("", QLabel("No parameters needed")))
        else:
            # Get all the separate parameters to put into this layout.
            for param_label, param_data in step["function"]["parameters"].items():
                self.add_param_widgets(param_label, param_data)

        layout.addWidget(CollapsibleBox(step["display_name"], Form(self.form_rows)))

    def add_param_widgets(self, param_label, param_data):
        """
        - param_label is a string like "scaling_param"
        - param_data is a list of FunctionParameter objects
        """
        param_label_formatted = param_label
        is_label_numbered = False
        if len(param_data) > 1:
            is_label_numbered = True
        
        for i, param in enumerate(param_data):
            # Parse out type of widget to be added
            widget_type = param["widget_type"]

            if is_label_numbered:
                param_label_formatted = f"{param_label} {i + 1}"

            # Slider
            if widget_type == "slider":
                self.add_slider(param_label_formatted, param)
            # Drop Down
            elif widget_type == "drop-down":
                self.add_dropdown(param_label_formatted, param)

    def add_slider(self, param_label, param):
        # Add a slider
        widget_values = dict()

        # Build dictionary of widget information (default value, min, max, increment)
        # if step.parameters is not None:
        #     if isinstance(step.parameters[param_key], list):
        #         # if given two numbers for default value default to first value given
        #         default_val = step.parameters[param_key][0]
        #     else:
        #         default_val = step.parameters[param_key]
        #     widget_values["value"] = default_val

        widget_values["value"] = param["default_value"]

        if "max" in param:
            widget_values["max"] = param["max"]
        if "min" in param:
            widget_values["min"] = param["min"]
        if "increment" in param:
            widget_values["step"] = param["increment"]

        # Sometimes default values are less than min or greater than max?
        if widget_values["value"] < widget_values["min"]:
            widget_values["value"] = widget_values["min"]
        if widget_values["value"] > widget_values["max"]:
            widget_values["value"] = widget_values["max"]

        # Determine which type of slider to use based on data type
        # and unpack dictionary with slider info and feed when initializing
        widget = None
        if param["data_type"] == "float":
            widget = FloatSlider(**widget_values)
        if param["data_type"] == "int":
            widget = Slider(**widget_values)

        self.form_rows.append(FormRow(param_label, widget.native))

    def add_dropdown(self, param_label, param):
        dropdown = UiUtils.dropdown_row(param_label, param["default_value"], options=param["option"], enabled=True)
        self.form_rows.append(dropdown)
