from aicssegmentation.workflow import (
    WorkflowEngine,
    WorkflowStep,
    SegmenterFunction,
    FunctionParameter,
    WidgetType,
    WorkflowStepCategory,
)
from qtpy.QtWidgets import QComboBox
from napari_allencell_segmenter.widgets.workflow_step_widget import WorkflowStepWidget


class TestWorkflowStepWidget:
    def test_all_workflows(self):
        """Make sure none of the workflow steps crash the widget"""
        engine = WorkflowEngine()
        for workflow in engine.workflow_definitions:
            for step in workflow.steps:
                print(f"{workflow.name} - {step.name}")
                step_widget = WorkflowStepWidget(step)

    def test_step_with_no_params(self):
        # Arrange - this step's function has no parameters
        function = SegmenterFunction("gaussian blur", "Gaussian blur", "my_function_name", "my_module_name")
        step = WorkflowStep(WorkflowStepCategory.PRE_PROCESSING, function, 1, [2])

        # Act
        widget = WorkflowStepWidget(step)

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
        parameter_values = {"scaling_param": ["blue", "green"]}
        step = WorkflowStep(WorkflowStepCategory.PRE_PROCESSING, function, 1, [2], parameter_values)

        # Act
        widget = WorkflowStepWidget(step)

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
        widget = WorkflowStepWidget(step)

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
        widget = WorkflowStepWidget(step)

        # Act
        widget.form_rows[0].widget.value = 50  # x
        widget.form_rows[1].widget.value = 11  # y 1
        widget.form_rows[2].widget.value = 22  # y 2
        parameter_inputs = widget.get_parameter_inputs()

        # Assert
        assert parameter_inputs == expected_values
