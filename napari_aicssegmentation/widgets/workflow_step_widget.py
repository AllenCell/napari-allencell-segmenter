import copy
from typing import List, Any, Union

from aicssegmentation.workflow import WorkflowStep, FunctionParameter, WidgetType
from magicgui.widgets import FloatSlider, Slider
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QLabel, QVBoxLayout, QWidget

from napari_aicssegmentation.widgets.collapsible_box import CollapsibleBox
from napari_aicssegmentation.widgets.form import Form, FormRow
from napari_aicssegmentation.util.ui_utils import UiUtils


class WorkflowStepWidget(QWidget):
    """
    A widget wrapping a CollapsibleBox that contains all the parameter controls
    for a given WorkflowStep

    Params:
        step (WorkflowStep): WorkflowStep object for this widget
    """

    def __init__(self, step: WorkflowStep):
        super().__init__()
        self.step_name = f"<span>{step.step_number}.&nbsp;{step.name}</span>"
        self.form_rows = []
        self.parameter_inputs = copy.deepcopy(step.parameter_defaults)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        if step.function.parameters is None:
            no_param_label = QLabel("No parameters needed")
            no_param_label.setAlignment(Qt.AlignCenter)
            no_param_label.setContentsMargins(0, 0, 6, 0)
            self.form_rows.append(FormRow("", no_param_label))
        else:
            for param_label, param_data in step.function.parameters.items():
                default_values = step.parameter_defaults[param_label]
                self._add_param_rows(param_label, param_data, default_values)

        box = CollapsibleBox(self.step_name, Form(self.form_rows, (11, 5, 5, 5)))
        layout.addWidget(box)

    def _add_param_rows(self, param_label: str, param_data: List[FunctionParameter], default_values: Union[List, Any]):
        for i, param in enumerate(param_data):
            # Append a number to the label if multiple parameter widgets share the same label
            param_label_numbered = param_label
            if len(param_data) > 1:
                param_label_numbered = f"{param_label} {i + 1}"

            # If default_values is not a list, that is the default value
            default_value = default_values
            # If default_values is a list, get the right one by index
            if isinstance(default_values, list):
                default_value = default_values[i]

            if param.widget_type == WidgetType.SLIDER:
                self._add_slider(param_label, param_label_numbered, param, default_value)
            elif param.widget_type == WidgetType.DROPDOWN:
                self._add_dropdown(param_label, param_label_numbered, param, default_value)

    def _add_slider(self, param_label, param_label_numbered_, param, default_value):
        if default_value < param.min_value or default_value > param.max_value:
            raise ValueError("Default value outside of min-max range")

        # Build dictionary of keyword args for slider widgets
        kwargs = dict()
        kwargs["step"] = param.increment
        kwargs["max"] = param.max_value
        kwargs["min"] = param.min_value
        kwargs["value"] = default_value

        widget = None
        if param.data_type == "float":
            widget = FloatSlider(**kwargs)
        if param.data_type == "int":
            widget = Slider(**kwargs)
        widget.changed.connect(self._update_parameter_inputs)
        widget = widget.native
        widget.setStyleSheet("QWidget { background-color: transparent; }")
        widget.setObjectName(param_label)

        self.form_rows.append(FormRow(param_label, widget))

    def _add_dropdown(self, param_label, param_label_numbered, param, default_value):
        dropdown_row = UiUtils.dropdown_row(
            param_label_numbered, default=default_value, options=param.options, enabled=True
        )
        dropdown_row.widget.setObjectName(param_label)
        dropdown_row.widget.currentIndexChanged.connect(self._update_parameter_inputs)
        self.form_rows.append(dropdown_row)

    def _update_parameter_inputs(self, event):
        # TODO: just need to do some dom traversal to update parameter_inputs
        print("updating parameters")
