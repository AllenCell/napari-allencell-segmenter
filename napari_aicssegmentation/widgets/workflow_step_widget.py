import copy
from typing import List, Union

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
        self.parameter_defaults = step.parameter_defaults
        self.parameter_inputs = copy.deepcopy(self.parameter_defaults)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        if step.function.parameters is None:
            label_no_param = QLabel("No parameters needed")
            label_no_param.setAlignment(Qt.AlignCenter)
            label_no_param.setContentsMargins(0, 0, 6, 0)
            self.form_rows.append(FormRow("", label_no_param))
        else:
            for param_name, param_data in step.function.parameters.items():
                default_values = self.parameter_defaults[param_name]
                self._add_param_rows(param_name, param_data, default_values)

        box = CollapsibleBox(self.step_name, Form(self.form_rows, (11, 5, 5, 5)))
        layout.addWidget(box)

    def _add_param_rows(
        self, param_name: str, param_data: List[FunctionParameter], default_values: Union[List, str, bool, int, float]
    ):
        for i, param in enumerate(param_data):
            param_label = param_name
            # Append a number to the label if multiple parameter widgets share the same name
            if len(param_data) > 1:
                param_label = f"{param_name} {i + 1}"

            # If default_values is not a list, that is the default value
            default_value = default_values
            # If default_values is a list, get the right one by index
            if isinstance(default_values, list):
                default_value = default_values[i]

            # param_name will become the widget's objectName
            # param_label will be displayed in the UI
            if param.widget_type == WidgetType.SLIDER:
                self._add_slider(param_name, param_label, param, default_value)
            elif param.widget_type == WidgetType.DROPDOWN:
                self._add_dropdown(param_name, param_label, param, default_value)

    def _add_slider(
        self, param_name: str, param_label: str, param: FunctionParameter, default_value: Union[str, bool, int, float]
    ):
        if default_value < param.min_value or default_value > param.max_value:
            raise ValueError("Default value outside of min-max range")

        # Build dictionary of keyword args for slider widgets
        kwargs = dict()
        kwargs["step"] = param.increment
        kwargs["max"] = param.max_value
        kwargs["min"] = param.min_value
        kwargs["value"] = default_value

        magicgui_widget = None
        if param.data_type == "float":
            magicgui_widget = FloatSlider(**kwargs)
        if param.data_type == "int":
            magicgui_widget = Slider(**kwargs)
        magicgui_widget.changed.connect(self._update_parameter_inputs)
        magicgui_widget.native.setStyleSheet("QWidget { background-color: transparent; }")
        magicgui_widget.native.setObjectName(param_name)

        self.form_rows.append(FormRow(param_label, magicgui_widget))

    def _add_dropdown(
        self, param_name: str, param_label: str, param: FunctionParameter, default_value: Union[str, bool, int, float]
    ):
        dropdown_row = UiUtils.dropdown_row(param_label, default=default_value, options=param.options, enabled=True)
        dropdown_row.widget.setObjectName(param_name)
        dropdown_row.widget.currentIndexChanged.connect(self._update_parameter_inputs)
        self.form_rows.append(dropdown_row)

    def _update_parameter_inputs(self, event):
        # Reset self.parameter_inputs
        for parameter_name in self.parameter_defaults.keys():
            # If default values for this param came in a list, we need to save values
            # from the UI in a list
            if isinstance(self.parameter_defaults[parameter_name], list):
                self.parameter_inputs[parameter_name] = []
            else:
                self.parameter_inputs[parameter_name] = 0

        for param_row in self.form_rows:
            name = ""
            value = 0

            # Grab the current value from the row, along with its param name
            if isinstance(param_row.widget, QWidget):
                # Row contains a dropdown
                name = param_row.widget.objectName()
                value = param_row.widget.currentText()
                # Convert string back to boolean if it was originally boolean
                if isinstance(self.parameter_defaults[name], bool):
                    value = value.lower() == "true"
            else:
                # Row contains a Magicgui Slider or FloatSlider
                name = param_row.widget.native.objectName()
                value = param_row.widget.get_value()

            # Populate self.parameter_inputs
            if isinstance(self.parameter_inputs[name], list):
                self.parameter_inputs[name].append(value)
            else:
                self.parameter_inputs[name] = value
