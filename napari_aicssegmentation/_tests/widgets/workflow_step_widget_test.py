from aicssegmentation.workflow import (
    WorkflowStep,
    SegmenterFunction,
    FunctionParameter,
    WidgetType,
    WorkflowStepCategory,
)
import pytest
from PyQt5.QtWidgets import QComboBox

from napari_aicssegmentation.widgets.workflow_step_widget import WorkflowStepWidget


class TestWorkflowStepWidget:
    def test_step_with_no_params(self):
        # Arrange - this step's function has no parameters
        function = SegmenterFunction("gaussian blur", "Gaussian blur", "my_function_name", "my_module_name")
        step = WorkflowStep(WorkflowStepCategory.PRE_PROCESSING, function, 1, [2])

        # Act
        widget = WorkflowStepWidget(step)

        # Assert
        assert widget.step_name == "<span>1.&nbsp;Gaussian blur</span>"
        assert len(widget.form_rows) == 1
        assert widget.form_rows[0].label == ""

    def test_step_with_single_value_per_param(self):
        # Arrange
        parameters = {
            "scaling_param": [FunctionParameter("scaling", WidgetType.DROPDOWN, "str", options=["red", "blue"])]
        }
        function = SegmenterFunction("gaussian blur", "Gaussian blur", "my_function_name", "my_module_name", parameters)
        parameter_defaults = {"scaling_param": ["blue"]}
        step = WorkflowStep(WorkflowStepCategory.PRE_PROCESSING, function, 1, [2], parameter_defaults)

        # Act
        widget = WorkflowStepWidget(step)

        # Assert
        assert len(widget.form_rows) == 1
        assert widget.form_rows[0].label == "scaling_param"
        assert isinstance(widget.form_rows[0].widget, QComboBox)

    def test_step_with_multiple_values_per_param(self):
        # Arrange
        parameters = {
            "scaling_param": [
                FunctionParameter("scaling", WidgetType.DROPDOWN, "str", options=["red", "blue"]),
                FunctionParameter("scaling", WidgetType.DROPDOWN, "str", options=["green", "yellow"]),
            ]
        }
        function = SegmenterFunction("gaussian blur", "Gaussian blur", "my_function_name", "my_module_name", parameters)
        parameter_defaults = {"scaling_param": ["blue", "green"]}
        step = WorkflowStep(WorkflowStepCategory.PRE_PROCESSING, function, 1, [2], parameter_defaults)

        # Act
        widget = WorkflowStepWidget(step)

        # Assert
        assert len(widget.form_rows) == 2
        assert widget.form_rows[0].label == "scaling_param 1"
        assert widget.form_rows[1].label == "scaling_param 2"
        assert isinstance(widget.form_rows[0].widget, QComboBox)
        assert widget.form_rows[0].widget.currentText() == "blue"
