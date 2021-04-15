from typing import List

from aicssegmentation.workflow import WorkflowStep
from aicssegmentation.workflow.segmenter_function import FunctionParameter, WidgetType
from magicgui.widgets import FloatSlider, Slider
from qtpy.QtWidgets import QLabel, QVBoxLayout, QWidget

from napari_aicssegmentation.widgets.collapsible_box import CollapsibleBox
from napari_aicssegmentation.widgets.form import Form, FormRow
from napari_aicssegmentation.util.ui_utils import UiUtils


class WorkflowStepWidget(QWidget):
    """
    A widget wrapping a CollapsibleBox that contains all the parameter controls and other
    necessary child widgets for a given WorkflowStep

    Params:
        step (WorkflowStep): WorkflowStep object for this widget
    """

    def __init__(self, step: WorkflowStep):
        super().__init__()
        self.form_rows = []

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # if len(step.function.parameters) is None:
        #     self.form_rows.append(FormRow("", QLabel("No parameters needed")))
        # else:
        #     # Get all the separate parameters to put into this layout.
        #     for param_label, param_data in step.function.parameters.items():
        #         self.add_param_widgets(param_label, param_data)

        step_name = f"<span>{step.step_number}.&nbsp;{step.name}</span>"
        layout.addWidget(CollapsibleBox(step_name, Form(self.form_rows)))

    def add_param_widgets(self, param_label: str, param_data: List[FunctionParameter]):
        # Prepare to append a number to the label if multiple parameter widgets
        # share the same label
        param_label_numbered = param_label
        is_label_numbered = False
        if len(param_data) > 1:
            is_label_numbered = True

        for i, param in enumerate(param_data):
            if is_label_numbered:
                param_label_numbered = f"{param_label} {i + 1}"

            if param.widget_type == WidgetType.SLIDER:
                self.add_slider(param_label_numbered, param)
            elif param.widget_type == WidgetType.DROPDOWN:
                self.add_dropdown(param_label_numbered, param)

    def add_slider(self, param_label, param):
        widget_kwargs = dict()

        # if step.parameters is not None:
        #     if isinstance(step.parameters[param_key], list):
        #         # if given two numbers for default value default to first value given
        #         default_val = step.parameters[param_key][0]
        #     else:
        #         default_val = step.parameters[param_key]
        #     widget_kwargs["value"] = default_val

        # Build dictionary of widget information (default value, min, max, increment)
        widget_kwargs["step"] = param.increment
        widget_kwargs["max_value"] = param.max_value
        widget_kwargs["min_value"] = param.min_value
        widget_kwargs["value"] = param["default_value"]

        # NOTE: This is on Jianxu's radar to fix
        # Sometimes default values are less than min or greater than max?
        if widget_kwargs["value"] < widget_kwargs["min_value"]:
            widget_kwargs["value"] = widget_kwargs["min_value"]
        if widget_kwargs["value"] > widget_kwargs["max_value"]:
            widget_kwargs["value"] = widget_kwargs["max_value"]

        # Determine which type of slider to use based on data type
        # and unpack dictionary with slider info and feed when initializing
        widget = None
        if param.data_type == "float":
            widget = FloatSlider(**widget_kwargs)
        if param.data_type == "int":
            widget = Slider(**widget_kwargs)

        self.form_rows.append(FormRow(param_label, widget.native))

    def add_dropdown(self, param_label, param):
        dropdown = UiUtils.dropdown_row(
            param_label, param["default_value"], options=param.options, enabled=True
        )
        self.form_rows.append(dropdown)