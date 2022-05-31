import pytest
from unittest import mock
from unittest.mock import MagicMock, create_autospec, PropertyMock, patch
from napari_allencell_segmenter.controller.workflow_steps_controller import WorkflowStepsController
from napari_allencell_segmenter.core._interfaces import IApplication, IRouter
from napari_allencell_segmenter.core.state import State
from napari_allencell_segmenter.core.view_manager import ViewManager
from napari_allencell_segmenter.model.channel import Channel
from napari_allencell_segmenter.model.segmenter_model import SegmenterModel
from napari_allencell_segmenter.core.viewer_abstraction import ViewerAbstraction
from napari_allencell_segmenter.widgets.param_sweep_widget import ParamSweepWidget
from napari.qt.threading import create_worker, GeneratorWorker
from ..mocks import MockLayer, MockWorker
from aicssegmentation.workflow import WorkflowEngine, WorkflowStep, WorkflowDefinition
from napari.layers import Image

import numpy as np


class TestWorkflowStepsController:
    def setup_method(self):
        self._mock_application: MagicMock = create_autospec(IApplication)
        self._mock_router: MagicMock = create_autospec(IRouter)
        self._mock_viewer: MagicMock = create_autospec(ViewerAbstraction)
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

    @pytest.mark.parametrize("filepath", ["/path/to/workflow.json", "/path/to/workflow.xml", "/path/to/workflow"])
    def test_save_workflow(self, filepath):
        # Arrange
        steps = [create_autospec(WorkflowStep), create_autospec(WorkflowStep), create_autospec(WorkflowStep)]

        # Act
        self._controller.save_workflow(steps, filepath)

        # Assert
        self._mock_workflow_engine.save_workflow_definition.assert_called_once()
        assert self._mock_workflow_engine.save_workflow_definition.call_args[0][1].suffix == ".json"

    def test_close_workflow(self):
        # Arrange
        channel = Channel(0, "Brightfield")
        self._controller.model.selected_channel = channel

        # Act
        self._controller.close_workflow()

        # Assert
        self._controller.model.selected_channel == None
        self._mock_router.workflow_selection.assert_called_once()

    @mock.patch("napari_allencell_segmenter.controller.workflow_steps_controller.create_worker")
    def test_run_all(self, mock_create_worker: MagicMock):
        # arrange
        self._controller._run_lock = False
        mock_create_worker.return_value = MockWorker()

        # act
        self._controller.run_all([{"param_test": 1}])

        assert self._controller._worker is not None
        mock_create_worker.assert_called_once_with(self._controller._run_all_async, [{"param_test": 1}])
        self._controller._worker.yielded.connect.assert_called_once_with(self._controller._on_step_processed_all)
        self._controller._worker.started.connect.assert_called_once_with(self._controller._on_run_all_started)
        self._controller._worker.finished.connect.assert_called_once_with(self._controller._on_run_all_finished)
        self._controller._worker.start.assert_called_once()

    @mock.patch("napari_allencell_segmenter.controller.workflow_steps_controller.create_worker")
    def test_run_next_step(self, mock_create_worker: MagicMock):
        # arrange
        self._controller._run_lock = False
        mock_create_worker.return_value = MockWorker()

        # act
        self._controller.run_next_step([{"param_test": 1}])

        assert self._controller._worker is not None
        mock_create_worker.assert_called_once_with(self._controller._run_next_step_async, [{"param_test": 1}])
        self._controller._worker.yielded.connect.assert_called_once_with(self._controller._on_step_processed)
        self._controller._worker.started.connect.assert_called_once_with(self._controller._on_run_all_started)
        self._controller._worker.finished.connect.assert_called_once_with(self._controller._on_run_all_finished)
        self._controller._worker.start.assert_called_once()

    @mock.patch("napari_allencell_segmenter.controller.workflow_steps_controller.create_worker")
    def test_run_step_no_images_selected(self, mock_create_worker: MagicMock):
        # arrange
        self._controller._run_lock = False
        mock_create_worker.return_value = MockWorker()
        workflow_with_parent = create_autospec(WorkflowDefinition)
        workflow_with_parent.parent = [create_autospec(WorkflowDefinition), create_autospec(WorkflowDefinition)]
        workflow_with_parent.name = "test_workflow_step"
        self._controller.model.active_workflow.workflow_definition.steps = [
            create_autospec(WorkflowDefinition),
            workflow_with_parent,
            create_autospec(WorkflowDefinition),
        ]
        self._controller.viewer.get_active_layer.return_value = []
        self._controller.viewer.get_theme.return_value = "dark"

        # act
        with patch(
            "napari_allencell_segmenter.controller.workflow_steps_controller.WorkflowStepsController.warn_box"
        ) as patched_func:
            self._controller.run_step(1, [{"param_test": 1}])

        self._controller.viewer.get_active_layer.assert_called_once()
        patched_func.assert_called_once_with(
            f"{workflow_with_parent.name} requires {len(workflow_with_parent.parent)} input images, "
            f"but you have selected {0} images."
            f"\nPlease select {len(workflow_with_parent.parent)} images by ctrl+clicking.",
            "Wrong number of input images selected",
            one_option=True,
        )
        assert self._controller._worker is None

        # assert self._controller._worker is not None
        # mock_create_worker.assert_called_once_with(self._controller._run_step_async, 1, [{"param_test": 1}])
        # self._controller._worker.yielded.connect.assert_called_once_with(self._controller._on_step_processed)
        # self._controller._worker.started.connect.assert_called_once_with(self._controller._on_run_all_started)
        # self._controller._worker.finished.connect.assert_called_once_with(self._controller._on_run_step_finished)
        # self._controller._worker.start.assert_called_once()

    @mock.patch("napari_allencell_segmenter.controller.workflow_steps_controller.create_worker")
    def test_run_step_out_of_order_parent_not_zero(self, mock_create_worker: MagicMock):
        # arrange
        self._controller._run_lock = False
        mock_create_worker.return_value = MockWorker()
        # step to run
        workflow_with_parent = create_autospec(WorkflowDefinition)
        workflow_with_parent.parent = [1]
        workflow_with_parent.name = "test_workflow_step"

        parent = create_autospec(WorkflowDefinition)
        parent.parent = [0]
        parent.name = "test_workflow_step_parent"
        self._controller.model.active_workflow.workflow_definition.steps = [
            parent,
            workflow_with_parent,
            create_autospec(WorkflowDefinition),
        ]
        # selected layer
        test_image = create_autospec(Image)
        test_image.name = "2. test_workflow_step"
        self._controller.viewer.get_active_layer.return_value = [test_image]
        self._controller.viewer.get_theme.return_value = "dark"

        # act
        with patch(
            "napari_allencell_segmenter.controller.workflow_steps_controller.WorkflowStepsController.warn_box"
        ) as patched_func:
            self._controller.run_step(1, [{"param_test": 2}])

        self._controller.viewer.get_active_layer.assert_called_once()
        patched_func.assert_called_once_with(
            f"You currently have the layer {test_image.name} selected in napari which will be used as the input layer."
            f" You will run this segmentation"
            f" out of order. To run the segmentation in order, please select a layer that is the output of "
            f"{1}. {parent.name}."
            f"\n Would you like to continue?",
            "Run segmentation out of order",
        )
        assert self._controller._worker is None

    @mock.patch("napari_allencell_segmenter.controller.workflow_steps_controller.create_worker")
    def test_run_step_out_of_order_parent_zero(self, mock_create_worker: MagicMock):
        # arrange
        self._controller._run_lock = False
        mock_create_worker.return_value = MockWorker()
        # step to run
        workflow_with_parent = create_autospec(WorkflowDefinition)
        workflow_with_parent.name = "test_workflow_step"
        workflow_with_parent.parent = [0]

        self._controller.model.active_workflow.workflow_definition.steps = [
            workflow_with_parent,
            create_autospec(WorkflowDefinition),
        ]
        # selected layer
        test_image = create_autospec(Image)
        test_image.name = "1. test_workflow_step"
        self._controller.viewer.get_active_layer.return_value = [test_image]
        self._controller.viewer.get_theme.return_value = "dark"

        # act
        with patch(
            "napari_allencell_segmenter.controller.workflow_steps_controller.WorkflowStepsController.warn_box"
        ) as patched_func:
            self._controller.run_step(0, [{"param_test": 2}])

        self._controller.viewer.get_active_layer.assert_called_once()
        patched_func.assert_called_once_with(
            f"You currently have the layer {test_image.name} selected in napari which will be used as the input layer. "
            f"You will run this segmentation"
            f" out of order. \nTo run the segmentation in order, please select the starting image (step 0) as the "
            f"input layer for this step. "
            f"\n Would you still like to continue?",
            "Run segmentation out of order",
        )

        assert self._controller._worker is None

    @mock.patch("napari_allencell_segmenter.controller.workflow_steps_controller.create_worker")
    def test_run_step_invalid_layer_selected(self, mock_create_worker: MagicMock):
        # arrange
        self._controller._run_lock = False
        mock_create_worker.return_value = MockWorker()
        # step to run
        workflow_with_parent = create_autospec(WorkflowDefinition)
        workflow_with_parent.name = "test_workflow_step"
        workflow_with_parent.parent = [0]

        self._controller.model.active_workflow.workflow_definition.steps = [
            workflow_with_parent,
            create_autospec(WorkflowDefinition),
        ]
        # selected layer
        test_image = create_autospec(Image)
        test_image.name = "test_workflow_step"
        self._controller.viewer.get_active_layer.return_value = [test_image]
        self._controller.viewer.get_theme.return_value = "dark"

        # act
        with patch(
            "napari_allencell_segmenter.controller.workflow_steps_controller.WorkflowStepsController.warn_box"
        ) as patched_func:
            self._controller.run_step(0, [{"param_test": 2}])

        self._controller.viewer.get_active_layer.assert_called_once()
        patched_func.assert_called_once_with(
            f"You currently have the layer {test_image.name} selected in napari which will be used as the input layer. "
            f"You will run this segmentation"
            f" out of order. \nTo run the segmentation in order, please select the starting image (step 0) as the "
            f"input layer for this step. "
            f"\n Would you still like to continue?",
            "Run segmentation out of order",
        )

        assert self._controller._worker is None

    @mock.patch("napari_allencell_segmenter.controller.workflow_steps_controller.create_worker")
    def test_run_step_no_warnings(self, mock_create_worker: MagicMock):
        # arrange
        self._controller._run_lock = False
        mock_create_worker.return_value = MockWorker()
        # step to run
        workflow_with_parent = create_autospec(WorkflowDefinition)
        workflow_with_parent.name = "test_workflow_step"
        workflow_with_parent.parent = [1]

        self._controller.model.active_workflow.workflow_definition.steps = [
            workflow_with_parent,
            create_autospec(WorkflowDefinition),
        ]
        # selected layer
        test_image = create_autospec(Image)
        test_image.name = "1. test_workflow_step"
        self._controller.viewer.get_active_layer.return_value = [test_image]
        self._controller.viewer.get_theme.return_value = "dark"

        # act
        self._controller.run_step(0, [{"param_test": 2}])

        self._controller.viewer.get_active_layer.assert_called_once()
        assert self._controller._worker is not None
        mock_create_worker.assert_called_once_with(self._controller._run_step_async, 0, [{"param_test": 2}])
        self._controller._worker.yielded.connect.assert_called_once_with(self._controller._on_step_processed)
        self._controller._worker.started.connect.assert_called_once_with(self._controller._on_run_all_started)
        self._controller._worker.finished.connect.assert_called_once_with(self._controller._on_run_step_finished)
        self._controller._worker.start.assert_called_once()

    @mock.patch("napari_allencell_segmenter.controller.workflow_steps_controller.create_worker")
    def test_run_step_sweep_no_params(self, mock_create_worker):
        mock_widget = create_autospec(ParamSweepWidget)
        mock_widget.step_number = 1
        mock_widget.param_set = None
        self._controller.run_lock = False

        self._controller.run_step_sweep(mock_widget, [["1", "1", "1"]])

        assert self._controller._worker is not None
        mock_create_worker.assert_called_once_with(self._controller._run_step_async, mock_widget.step_number, None)
        self._controller._worker.yielded.connect.assert_called_once_with(self._controller._on_step_processed)
        self._controller._worker.started.connect.assert_called_once_with(self._controller._on_sweep_started)
        self._controller._worker.finished.connect.assert_called_once_with(self._controller.on_sweep_finished)
        self._controller._worker.start.assert_called_once()

    @mock.patch("napari_allencell_segmenter.controller.workflow_steps_controller.create_worker")
    def test_run_step_sweep_with_params(self, mock_create_worker):
        mock_widget = create_autospec(ParamSweepWidget)
        mock_widget.step_number = 1
        mock_widget.param_set = {"test_param": 2}
        self._controller.run_lock = False

        with patch(
            "napari_allencell_segmenter.controller.workflow_steps_controller.WorkflowStepsController._parse_inputs"
        ) as patched_func:
            patched_func.return_value = {"test_param": 1}
            self._controller.run_step_sweep(mock_widget, [["1", "1", "1"]])

        assert self._controller._worker is not None
        mock_create_worker.assert_called_once_with(
            self._controller._run_step_sweep_grid, mock_widget.step_number, mock_widget.param_set, {"test_param": 1}
        )
        self._controller._worker.yielded.connect.assert_called_once_with(self._controller._on_step_processed)
        self._controller._worker.started.connect.assert_called_once_with(self._controller._on_sweep_started)
        self._controller._worker.finished.connect.assert_called_once_with(self._controller.on_sweep_finished)
        self._controller._worker.start.assert_called_once()

    @mock.patch("napari_allencell_segmenter.controller.workflow_steps_controller.SegmenterModel", return_value=2)
    def test_run_step_async(self, param):
        # unfinished
        generator = self._controller._run_step_async(2, param)
        assert self._controller._steps == 0

    def test_parse_inputs(self):
        # test single param sweeps
        sweep_test = self._controller._parse_inputs({"param": [1]}, [["1", "1", "10"]])

        assert sweep_test["param"][0].size == 10
        assert sweep_test["param"][0][0] == 1
        assert sweep_test["param"][0][9] == 10

        # test single param as list, fixed
        sweep_test = self._controller._parse_inputs({"param": [1]}, [["1", "10", "1"]])
        assert isinstance(sweep_test["param"], list)
        assert sweep_test["param"][0] == 1.0
        # test single param as non list, fixed
        sweep_test = self._controller._parse_inputs({"param": 1}, [["1", "10", "1"]])
        assert isinstance(sweep_test["param"], list)
        assert sweep_test["param"][0] == 1.0

        # test two params in list
        sweep_test = self._controller._parse_inputs({"param-multi": [1, 2]}, [["1", "1", "10"], ["1", "10", "1"]])
        assert sweep_test["param-multi"][0].size == 10
        assert sweep_test["param-multi"][1].size == 1
        assert isinstance(sweep_test["param-multi"][0], np.ndarray)
        assert isinstance(sweep_test["param-multi"][1], np.ndarray)

        # test two params in dict
        sweep_test = self._controller._parse_inputs(
            {"param1-int": 1, "param2-list": [2]}, [["1", "1", "10"], ["1", "10", "1"]]
        )
        assert sweep_test["param1-int"].size == 10
        assert sweep_test["param2-list"][0].size == 1
        assert isinstance(sweep_test["param1-int"], np.ndarray)
        assert isinstance(sweep_test["param2-list"], list)

        # test multiple dict keys and musltiple sweeps
        sweep_test = self._controller._parse_inputs(
            {"param1": 1, "param-single-list": [2], "param-multi-list": [3, 4]},
            [["1", "1", "10"], ["2", "10", "2"], ["3", "1", "3"], ["4", "5", "4"]],
        )
        assert sweep_test["param1"].size == 10

        assert sweep_test["param-single-list"][0].size == 1
        assert sweep_test["param-single-list"][0][0] == 2.0

        assert len(sweep_test["param-multi-list"]) == 2
        assert sweep_test["param-multi-list"][0].size == 1
        assert sweep_test["param-multi-list"][1].size == 1
        assert sweep_test["param-multi-list"][0][0] == 3.0
        assert sweep_test["param-multi-list"][1][0] == 4.0

    def test_handle_sweep_single(self):
        # arrange
        active_layer = MockLayer(name="test-layer", ndim=3)
        self._controller.viewer.get_active_layer.return_value = [active_layer]
        workflows = [
            create_autospec(WorkflowDefinition),
            create_autospec(WorkflowDefinition),
            create_autospec(WorkflowDefinition),
        ]
        type(self._mock_workflow_engine).workflow_definitions = PropertyMock(return_value=workflows)
        self._model.active_workflow.execute_step.return_value = np.zeros([2, 2, 2])
        test_dict = {"test_param": [0]}
        result_dict = {"test_param": 0}

        # act
        result = self._controller._handle_sweep_single(0, 0, test_dict)

        # assert
        assert self._controller._current_params == {"test_param": round(list(test_dict.values())[0][0], 3)}
        assert self._controller._steps == 0
        assert np.array_equal(result[1], np.zeros([2, 2, 2]))
        self._controller.model.active_workflow.execute_step.assert_called_once_with(0, result_dict, [active_layer])

    def test_setup_params_sweep(self):
        # test int and float
        assert self._controller._setup_params_sweep(3.0, 4) == ([3.0], 4)
        # test str
        assert self._controller._setup_params_sweep("test", "test1") == (["test"], ["test1"])
        # test int and float in list
        assert self._controller._setup_params_sweep([3.0], [4]) == ([3.0], 4)
        # test str in list
        assert self._controller._setup_params_sweep(["test"], ["test1"]) == (["test"], ["test1"])
        # test nested list
        assert self._controller._setup_params_sweep([[3.0]], [[4]]) == ([3.0], [4])
        # test numpy array
        result = self._controller._setup_params_sweep(np.arange(1, 2, 1), np.arange(1.0, 3.0, 1.0))
        assert result[0] == 1
        assert np.array_equal(result[1], np.arange(1.0, 3.0, 1.0))

    def test_on_step_processed_first_run(self):
        # Test when first step being ran for first time (no sweep)
        # arrange
        test_step = create_autospec(WorkflowStep)
        test_step.step_number = 1
        test_step.name = "test"
        test_array = np.zeros([2, 2, 2])
        layers = [MockLayer("test", ndim=3), MockLayer("test2", ndim=3), MockLayer("test3", ndim=3)]
        self._controller.viewer.layers = layers

        # act
        self._controller._on_step_processed((test_step, test_array))

        # assert
        # assert self._controller._sweep_step == 3
        self._controller.viewer.add_image_layer.assert_called_once_with(test_array, name="1: test")
        self._controller.view.set_progress_bar.assert_called_once_with(0)

    def test_on_step_processed_rerun(self):
        test_step = create_autospec(WorkflowStep)
        test_step.step_number = 1
        test_step.name = "test"
        test_array = np.zeros([2, 2, 2])
        self._controller._max_step_run = 0
        layers = [MockLayer("test", ndim=3), MockLayer("test2", ndim=3), MockLayer("test3", ndim=3)]
        self._controller.viewer.layers = layers

        # act
        self._controller._on_step_processed((test_step, test_array))

        # assert
        assert self._controller._number_times_run == 1
        self._controller.viewer.add_image_layer.assert_called_once_with(test_array, name="1.1: test")
        self._controller.view.set_progress_bar.assert_called_once_with(0)

    def test_on_step_processed_sweep_run(self):
        test_step = create_autospec(WorkflowStep)
        test_step.step_number = 1
        test_step.name = "test"
        test_array = np.zeros([2, 2, 2])
        self._controller._sweep_step = 2
        self._controller.param_sweep_widget = create_autospec(ParamSweepWidget)
        layers = [MockLayer("test", ndim=3), MockLayer("test2", ndim=3), MockLayer("test3", ndim=3)]
        self._controller.viewer.layers = layers

        # act
        self._controller._on_step_processed((test_step, test_array))

        assert self._controller._sweep_step == 3
        self._controller.viewer.add_image_layer.assert_called_once_with(test_array, name="1: test")
        self._controller.view.set_progress_bar.assert_called_once_with(0)
        self._controller.param_sweep_widget.set_progress_bar.assert_called_once_with(3)

    def test_on_step_processed_all(self):
        # arrange
        test_step = create_autospec(WorkflowStep)
        test_step.step_number = 1
        test_step.name = "test"
        test_array = np.zeros([2, 2, 2])

        # act
        self._controller._on_step_processed_all((test_step, test_array))

        # assert
        self._controller.view.increment_progress_bar.assert_called_once()
        self._controller.viewer.add_image_layer.assert_called_once_with(
            test_array, name=f"{test_step.step_number}: {test_step.name}"
        )

    def test_on_run_all_started(self):
        self._controller._on_run_all_started()

        assert self._controller._run_lock
        self._controller._view.set_run_all_in_progress.assert_called_once()

    def test_on_sweep_started(self):
        self._controller.param_sweep_widget = create_autospec(ParamSweepWidget)

        self._controller._on_sweep_started()

        assert self._controller._run_lock
        self._controller.param_sweep_widget.set_run_in_progress.assert_called_once()

    def test_on_run_all_finished(self):
        self._controller._on_run_all_finished()

        self._controller._view.reset_run_all.assert_called_once()
        assert not self._controller._run_lock

    def test_on_run_step_finished(self):
        self._controller._on_run_step_finished()

        self._controller._view.reset_run_step.assert_called_once()
        assert not self._controller._run_lock

    def test_on_sweep_finished(self):
        self._controller.param_sweep_widget = create_autospec(ParamSweepWidget)

        self._controller.on_sweep_finished()

        self._controller.param_sweep_widget.set_run_finished.assert_called_once()
        assert not self._controller._run_lock
