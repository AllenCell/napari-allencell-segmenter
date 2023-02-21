import copy
from unittest import mock

from aicssegmentation.workflow import (
    WorkflowEngine,
    WorkflowStep,
    SegmenterFunction,
    FunctionParameter,
    WidgetType,
    WorkflowStepCategory,
)
from qtpy.QtWidgets import QComboBox, QPushButton
from napari_allencell_segmenter.widgets.workflow_step_widget import WorkflowStepWidget
from unittest.mock import MagicMock, create_autospec


class TestWorkflowStepWidget:
    def test_all_workflows(self):
        """Make sure none of the workflow steps crash the widget"""
        engine = WorkflowEngine()
        for workflow in engine.workflow_definitions:
            for step in workflow.steps:
                step_widget = WorkflowStepWidget(step, 0)

    def test_get_workflow_step_with_inputs(self):
        #! todo test this
        step_to_use = create_autospec(WorkflowStep)
        step_to_use.function = create_autospec(SegmenterFunction)
        step_to_use.function.parameters = None
        step_to_use.step_number = 1
        widget = WorkflowStepWidget(step_to_use, 0)

        assert widget.get_workflow_step_with_inputs() == step_to_use

    def test_step_with_no_params(self):
        # Arrange - this step's function has no parameters
        function = SegmenterFunction("gaussian blur", "Gaussian blur", "my_function_name", "my_module_name")
        step = WorkflowStep(WorkflowStepCategory.PRE_PROCESSING, function, 1, [2])

        # Act
        widget = WorkflowStepWidget(step, 0)

        # Assert
        assert len(widget.form_rows) == 1
        assert widget.form_rows[0].label == ""

    def test_step_with_single_value_per_param(self):
        # Arrange
        parameters = {
            "scaling_param": [FunctionParameter("scaling", WidgetType.DROPDOWN, "str", options=["red", "blue"])]
        }
        function = SegmenterFunction("gaussian blur", "Gaussian blur", "my_function_name", "my_module_name", parameters)
        parameter_values = {"scaling_param": ["blue"]}
        step = WorkflowStep(WorkflowStepCategory.PRE_PROCESSING, function, 1, [2], parameter_values)

        # Act
        widget = WorkflowStepWidget(step, 0)

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
        parameter_values = {"scaling_param": ["blue", "green"]}
        step = WorkflowStep(WorkflowStepCategory.PRE_PROCESSING, function, 1, [2], parameter_values)

        # Act
        widget = WorkflowStepWidget(step, 0)

        # Assert
        assert len(widget.form_rows) == 2
        assert widget.form_rows[0].label == "scaling_param 1"
        assert widget.form_rows[1].label == "scaling_param 2"
        assert isinstance(widget.form_rows[0].widget, QComboBox)
        assert widget.form_rows[0].widget.currentText() == "blue"

    def test_get_parameter_inputs_default_params(self):
        # Arrange
        parameters = {
            "x": [FunctionParameter("x", WidgetType.SLIDER, "int", min_value=1, max_value=100, increment=1)],
            "y": [
                FunctionParameter("y", WidgetType.SLIDER, "int", min_value=1, max_value=100, increment=1),
                FunctionParameter("y", WidgetType.SLIDER, "int", min_value=1, max_value=100, increment=1),
            ],
        }
        function = SegmenterFunction("Test", "Test", "my_function_name", "my_module_name", parameters)
        parameter_values = {"x": 5, "y": [1, 2]}
        step = WorkflowStep(WorkflowStepCategory.PRE_PROCESSING, function, 1, [0], parameter_values)
        widget = WorkflowStepWidget(step, 0)

        # Act
        parameter_inputs = widget.get_parameter_inputs()

        # Assert
        assert parameter_inputs == parameter_values

    def test_get_parameter_inputs_modified_params(self):
        # Arrange
        parameters = {
            "x": [FunctionParameter("x", WidgetType.SLIDER, "int", min_value=1, max_value=100, increment=1)],
            "y": [
                FunctionParameter("y", WidgetType.SLIDER, "int", min_value=1, max_value=100, increment=1),
                FunctionParameter("y", WidgetType.SLIDER, "int", min_value=1, max_value=100, increment=1),
            ],
        }
        function = SegmenterFunction("Test", "Test", "my_function_name", "my_module_name", parameters)
        parameter_values = {"x": 5, "y": [1, 2]}
        expected_values = {"x": 50, "y": [11, 22]}
        step = WorkflowStep(WorkflowStepCategory.PRE_PROCESSING, function, 1, [0], parameter_values)
        widget = WorkflowStepWidget(step, 0)

        # Act
        widget.form_rows[0].widget.value = 50  # x
        widget.form_rows[1].widget.value = 11  # y 1
        widget.form_rows[2].widget.value = 22  # y 2
        parameter_inputs = widget.get_parameter_inputs()

        # Assert
        assert parameter_inputs == expected_values

    def test_enable_button(self):
        step_to_use = create_autospec(WorkflowStep)
        step_to_use.function = create_autospec(SegmenterFunction)
        step_to_use.step_number = 1

        widget = WorkflowStepWidget(step_to_use, 0)
        widget.button = create_autospec(QPushButton)

        widget.enable_button()

        widget.button.setEnabled.assert_called_once_with(True)

    def test_disable_button(self):
        step_to_use = create_autospec(WorkflowStep)
        step_to_use.function = create_autospec(SegmenterFunction)
        step_to_use.step_number = 1

        widget = WorkflowStepWidget(step_to_use, 0)
        widget.button = create_autospec(QPushButton)
        widget.disable_button()

        widget.button.setDisabled.assert_called_once_with(True)

    @mock.patch("napari_allencell_segmenter.widgets.workflow_step_widget.WorkflowStepWidget._add_slider")
    def test_add_param_rows(self, mocked: MagicMock):
        param_data = [
            FunctionParameter("x", WidgetType.SLIDER, "int", min_value=1, max_value=100, increment=10),
            FunctionParameter("y", WidgetType.SLIDER, "int", min_value=1, max_value=10, increment=1),
            FunctionParameter("z", WidgetType.DROPDOWN, "int", min_value=1, max_value=1000, increment=100),
        ]
        step_to_use = create_autospec(WorkflowStep)
        step_to_use.function = create_autospec(SegmenterFunction)
        step_to_use.function.parameters = None
        step_to_use.step_number = 1

        widget = WorkflowStepWidget(step_to_use, 0)

        widget._add_param_rows("test_param", param_data, 2.0)

        mocked.assert_called_with("test_param", "test_param 2", param_data[1], 2.0)
