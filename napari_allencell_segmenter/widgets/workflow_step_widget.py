import copy
from typing import Any, Dict, List, Union
from aicssegmentation.workflow import WorkflowStep, FunctionParameter, WidgetType
from magicgui.widgets import Slider
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QLabel, QVBoxLayout, QWidget, QComboBox, QPushButton, QFrame, QHBoxLayout
from napari_allencell_segmenter.widgets.collapsible_box import CollapsibleBox
from napari_allencell_segmenter.widgets.form import Form, FormRow
from napari_allencell_segmenter.util.ui_utils import UiUtils
from napari_allencell_segmenter.util.convert import Convert
from .float_slider import FloatSlider


class WorkflowStepWidget(QWidget):
    """
    A widget wrapping a CollapsibleBox that contains all the parameter controls
    for a given WorkflowStep

    Params:
        step (WorkflowStep): WorkflowStep object for this widget
    """

    def __init__(self, step: WorkflowStep, index: int, steps_view=None, enable_button: bool = False):
        super().__init__()
        if step is None:
            raise ValueError("step")
        self.step = step
        self.name = step.name
        self.index = index
        self.form_rows: List[FormRow] = list()
        self.button = QPushButton(f"Run {step.name}")
        self.button.clicked.connect(lambda: steps_view.btn_run_clicked(self.index))
        self.steps_view = steps_view

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
                default_values = step.parameter_values[param_name]
                self._add_param_rows(param_name, param_data, default_values)

        buttons = QFrame()
        buttons.setStyleSheet("border: none;")
        buttons.setLayout(QHBoxLayout())

        buttons.layout().addWidget(self.button)

        if not enable_button:
            self.button.setDisabled(True)
        box_contents = QVBoxLayout()
        box_contents.addLayout(Form(self.form_rows, (11, 5, 5, 5)))
        box_contents.addWidget(buttons)

        step_name = f"<span>{step.step_number}.&nbsp;{step.name}</span>"
        box = CollapsibleBox(step_name, box_contents, self)

        layout.addWidget(box)

    def get_workflow_step_with_inputs(self) -> WorkflowStep:
        """
        Returns a new WorkflowStep object with updated parameter values to reflect user input
        """
        new_step = copy.deepcopy(self.step)
        new_step.parameter_values = self.get_parameter_inputs()
        return new_step

    def get_parameter_inputs(self) -> Dict[str, Any]:
        """
        Returns all parameter input values for the as a dictionary {param_name: param_value}
        """
        if self.step.parameter_values is None:
            return None

        parameter_inputs = copy.deepcopy(self.step.parameter_values)

        for parameter_name in parameter_inputs.keys():
            # If default values for this param came in a list, we need to save values
            # from the UI in a list
            if isinstance(parameter_inputs[parameter_name], list):
                parameter_inputs[parameter_name] = []
            else:
                parameter_inputs[parameter_name] = 0

        for param_row in self.form_rows:
            # Grab the current value from the row, along with its param name
            if not isinstance(param_row.widget, QFrame):
                # skip buttons
                if isinstance(param_row.widget, QComboBox):
                    # Row contains a dropdown
                    name = param_row.widget.objectName()
                    value = param_row.widget.currentText()

                    # Convert for each data datatype
                    data_type = self.step.function.parameters[name][0].data_type
                    if data_type == "bool":
                        value = Convert.to_boolean(value)
                    elif data_type == "int":
                        value = int(value)
                    elif data_type == "float":
                        value = float(value)
                else:
                    # Row contains a Magicgui Slider or FloatSlider
                    name = param_row.widget.native.objectName()
                    value = param_row.widget.get_value()

                # Populate self.parameter_inputs
                if isinstance(parameter_inputs[name], list):
                    parameter_inputs[name].append(value)
                else:
                    parameter_inputs[name] = value

        return parameter_inputs

    def enable_button(self):
        self.button.setEnabled(True)

    def disable_button(self):
        self.button.setDisabled(True)

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
        self, param_name: str, param_label: str, param: FunctionParameter, default_value: Union[int, float]
    ):
        if param.data_type not in ["int", "float"]:
            raise RuntimeError(f"Cannot create slider for non numerical parameter <{param.name}>")

        if param.min_value is None or param.max_value is None or param.increment is None:
            raise ValueError("Parameter min_value, max_value and increment cannot be None")

        if default_value is not None and (default_value < param.min_value or default_value > param.max_value):
            raise ValueError("Default value outside of min-max range")

        magicgui_slider = None
        if param.data_type == "float":
            magicgui_slider = FloatSlider()
            magicgui_slider.setDecimals(3)
        if param.data_type == "int":
            magicgui_slider = Slider()

        magicgui_slider.min = param.min_value
        magicgui_slider.max = param.max_value
        magicgui_slider.step = param.increment
        magicgui_slider.value = default_value
        magicgui_slider.native.setStyleSheet("QWidget { background-color: transparent; }")
        magicgui_slider.native.setObjectName(param_name)

        self.form_rows.append(FormRow(param_label, magicgui_slider))

    def _add_dropdown(
        self, param_name: str, param_label: str, param: FunctionParameter, default_value: Union[str, bool, int, float]
    ):
        dropdown_row = UiUtils.dropdown_row(param_label, default=default_value, options=param.options, enabled=True)
        dropdown_row.widget.setObjectName(param_name)
        self.form_rows.append(dropdown_row)
