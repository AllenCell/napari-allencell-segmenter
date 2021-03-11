import pytest

from unittest import mock
from unittest.mock import MagicMock, create_autospec, PropertyMock, patch
from napari_aicssegmentation.controller.workflow_select_controller import WorkflowSelectController
from napari_aicssegmentation.core._interfaces import IApplication, IRouter
from napari_aicssegmentation.core.state import State
from napari_aicssegmentation.core.view_manager import ViewManager
from napari_aicssegmentation.model.segmenter_model import SegmenterModel


class TestWorkflowSelectController:
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

        with mock.patch("napari_aicssegmentation.controller.workflow_select_controller.WorkflowSelectView"):
            self._controller = WorkflowSelectController(self._mock_application)

    def test_index(self):
        # Act
        self._controller.index()

        # Assert
        self._mock_view_manager.load_view.assert_called_once_with(self._controller.view)
        self._controller.view.load_model.assert_called_once_with(self._controller.model)
        self._controller.model.channel_list == [
            "brightfield",
            "405nm",
            "488nm",
        ]  # TODO update once channels are loaded from image
        self._controller.model.workflows == [
            "SEC61B",
            "LMNB1",
            "ACTN1",
        ]  # TODO update once workflows loaded from Segmenter

    def test_select_channel(self):
        # Act
        self._controller.select_channel(3)

        # Assert
        assert self._controller.model.active_channel == 3

    def test_select_workflow(self):
        # Act
        workflow = "LMNB1"
        self._controller.select_workflow(workflow)

        # Assert
        assert self._controller.model.active_workflow == workflow

    def test_navigate_back(self):
        # Act
        self._controller.navigate_back()

        # Assert
        self._mock_router.mpp.assert_called_once()

    def test_navigate_next(self):
        # Act
        self._controller.navigate_next()

        # Assert
        self._mock_router.workflow_steps.assert_called_once()
