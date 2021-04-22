import pytest
from unittest import mock
from unittest.mock import MagicMock, create_autospec, PropertyMock, patch

from napari_aicssegmentation.controller.workflow_steps_controller import WorkflowStepsController
from napari_aicssegmentation.core._interfaces import IApplication, IRouter
from napari_aicssegmentation.core.state import State
from napari_aicssegmentation.core.view_manager import ViewManager
from napari_aicssegmentation.model.channel import Channel
from napari_aicssegmentation.model.segmenter_model import SegmenterModel
from aicssegmentation.workflow import WorkflowEngine


class TestWorkflowStepsController:
    def setup_method(self):
        self._mock_application: MagicMock = create_autospec(IApplication)
        self._mock_router: MagicMock = create_autospec(IRouter)
        type(self._mock_application).router = PropertyMock(return_value=self._mock_router)
        self._mock_state: MagicMock = create_autospec(State)
        type(self._mock_application).state = PropertyMock(return_value=self._mock_state)
        self._mock_view_manager: MagicMock = create_autospec(ViewManager)
        type(self._mock_application).view_manager = PropertyMock(return_value=self._mock_view_manager)
        self._model = SegmenterModel()
        type(self._mock_state).segmenter_model = PropertyMock(return_value=self._model)
        self._workflow_engine: MagicMock = create_autospec(WorkflowEngine)

        with mock.patch("napari_aicssegmentation.controller.workflow_steps_controller.WorkflowStepsView"):
            self._controller = WorkflowStepsController(self._mock_application, self._workflow_engine)

    def test_index(self):
        # Act
        self._controller.index()

        # Assert
        self._mock_view_manager.load_view.assert_called_once_with(self._controller.view)
        self._controller.view.load_model.assert_called_once_with(self._controller.model)

    def test_navigate_back(self):
        # Act
        self._controller.navigate_back()

        # Assert
        self._mock_router.workflow_selection.assert_called_once()

    def test_close_workflow(self):
        # Arrange
        channel = Channel(0, "Brightfield")
        self._controller.model.selected_channel = channel

        # Act
        self._controller.close_workflow()

        # Assert
        self._controller.model.selected_channel == None
