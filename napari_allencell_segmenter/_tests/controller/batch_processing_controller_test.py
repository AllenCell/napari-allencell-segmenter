import pytest
from unittest import mock
from unittest.mock import MagicMock, create_autospec, PropertyMock, patch
from pathlib import Path
from napari_allencell_segmenter.controller.batch_processing_controller import BatchProcessingController
from napari_allencell_segmenter.core._interfaces import IApplication, IRouter
from napari_allencell_segmenter.core.state import State
from napari_allencell_segmenter.core.view_manager import ViewManager
from aicssegmentation.workflow import WorkflowEngine, WorkflowStep


class TestBatchProcessingController:
    def setup_method(self):
        self._mock_application: MagicMock = create_autospec(IApplication)
        self._mock_router: MagicMock = create_autospec(IRouter)
        type(self._mock_application).router = PropertyMock(return_value=self._mock_router)
        self._mock_state: MagicMock = create_autospec(State)
        type(self._mock_application).state = PropertyMock(return_value=self._mock_state)
        self._mock_view_manager: MagicMock = create_autospec(ViewManager)
        type(self._mock_application).view_manager = PropertyMock(return_value=self._mock_view_manager)
        self._mock_workflow_engine: MagicMock = create_autospec(WorkflowEngine)

        with mock.patch("napari_allencell_segmenter.controller.batch_processing_controller.BatchProcessingView"):
            self._controller = BatchProcessingController(self._mock_application, self._mock_workflow_engine)

    def test_index(self):
        # Act
        self._controller.index()

        # Assert
        self._mock_view_manager.load_view.assert_called_once_with(self._controller.view, None)

    def test_update_batch_parameters(self):
        self._controller.update_batch_parameters(None, 1, Path("/some/dir"), Path("/some/dir"))
        self._controller.view.update_button.assert_called_with(False)

        self._controller.update_batch_parameters(Path("/some/file.json"), None, Path("/some/dir"), Path("/some/dir"))
        self._controller.view.update_button.assert_called_with(False)

        self._controller.update_batch_parameters(Path("/some/file.json"), 1, None, Path("/some/dir"))
        self._controller.view.update_button.assert_called_with(False)

        self._controller.update_batch_parameters(Path("/some/file.json"), 1, Path("/some/dir"), None)
        self._controller.view.update_button.assert_called_with(False)

        self._controller.update_batch_parameters(Path("/some/file.json"), 1, Path("/some/dir"), Path("/some/dir"))
        self._controller.view.update_button.assert_called_with(True)
