import pytest
from unittest import mock
from unittest.mock import MagicMock, create_autospec, PropertyMock
from napari_allencell_segmenter.controller.workflow_steps_controller import WorkflowStepsController
from napari_allencell_segmenter.core._interfaces import IApplication, IRouter
from napari_allencell_segmenter.core.state import State
from napari_allencell_segmenter.core.view_manager import ViewManager
from napari_allencell_segmenter.model.channel import Channel
from napari_allencell_segmenter.model.segmenter_model import SegmenterModel
from aicssegmentation.workflow import WorkflowEngine, WorkflowStep

import numpy as np


class TestWorkflowStepsController:
    def setup_method(self):
        self._mock_application: MagicMock = create_autospec(IApplication)
        self._mock_router: MagicMock = create_autospec(IRouter)
        type(self._mock_application).router = PropertyMock(return_value=self._mock_router)
        self._mock_state: MagicMock = create_autospec(State)
        type(self._mock_application).state = PropertyMock(return_value=self._mock_state)
        self._mock_view_manager: MagicMock = create_autospec(ViewManager)
        type(self._mock_application).view_manager = PropertyMock(return_value=self._mock_view_manager)
        self._model: MagicMock = create_autospec(SegmenterModel)
        type(self._mock_state).segmenter_model = PropertyMock(return_value=self._model)
        self._mock_workflow_engine: MagicMock = create_autospec(WorkflowEngine)

        with mock.patch("napari_allencell_segmenter.controller.workflow_steps_controller.WorkflowStepsView"):
            self._controller = WorkflowStepsController(self._mock_application, self._mock_workflow_engine)

    def test_index(self):
        # Act
        self._controller.index()

        # Assert
        self._mock_view_manager.load_view.assert_called_once_with(self._controller.view, self._model)

    def test_close_workflow(self):
        # Arrange
        channel = Channel(0, "Brightfield")
        self._controller.model.selected_channel = channel

        # Act
        self._controller.close_workflow()

        # Assert
        self._controller.model.selected_channel == None
        self._mock_router.workflow_selection.assert_called_once()

    @pytest.mark.parametrize("filepath", ["/path/to/workflow.json", "/path/to/workflow.xml", "/path/to/workflow"])
    def test_save_workflow(self, filepath):
        # Arrange
        steps = [create_autospec(WorkflowStep), create_autospec(WorkflowStep), create_autospec(WorkflowStep)]

        # Act
        self._controller.save_workflow(steps, filepath)

        # Assert
        self._mock_workflow_engine.save_workflow_definition.assert_called_once()
        assert self._mock_workflow_engine.save_workflow_definition.call_args[0][1].suffix == ".json"

    @mock.patch("napari_allencell_segmenter.controller.workflow_steps_controller.SegmenterModel", return_value=0)
    def test_run_step_async(self, param):
        generator = self._controller._run_step_async(2, param)
        assert self._controller._steps == 2

    def test_parse_inputs(self):
        # test single param sweeps
        sweep_test = self._controller._parse_inputs({"param": 1}, ["1:1:10"])
        assert sweep_test[1] == 10
        assert sweep_test[0]["param"].size == 10
        assert sweep_test[0]["param"][0] == 1
        assert sweep_test[0]["param"][9] == 10

        # test single param non-sweeps
        sweep_test = self._controller._parse_inputs({"param": 1}, ["1"])
        assert sweep_test[1] == 1
        assert sweep_test[0]["param"] == 1

        # test single param as list
        sweep_test = self._controller._parse_inputs({"param": [1]}, ["1"])
        assert sweep_test[1] == 1
        assert isinstance(sweep_test[0]["param"], list)
        assert len(sweep_test[0]["param"]) == 1

        # test two params in list
        sweep_test = self._controller._parse_inputs({"param-multi":[1, 2]}, ["1:1:10", "1"])
        assert sweep_test[1] == 10
        assert isinstance(sweep_test[0]["param-multi"][0], np.ndarray)
        assert isinstance(sweep_test[0]["param-multi"][1], float)

        # test two params in dict
        sweep_test = self._controller._parse_inputs({"param1-int": 1, "param2-list":[2]}, ["1:1:10", "1"])
        assert sweep_test[1] == 10
        assert isinstance(sweep_test[0]["param1-int"], np.ndarray)
        assert isinstance(sweep_test[0]["param2-list"], list)

        # test multiple dict keys and musltiple sweeps
        sweep_test = self._controller._parse_inputs({"param1": 1, "param-single-list": [2], "param-multi-list": [3, 4]}, ["1:1:10", "2", "3", "4"])
        assert sweep_test[1] == 10
        assert isinstance(sweep_test[0]["param1"], np.ndarray)
        assert sweep_test[0]["param1"].size == 10
        assert sweep_test[0]["param-single-list"] == [2]
        assert sweep_test[0]["param-multi-list"] == [3, 4]





