import pytest

from unittest import mock
from unittest.mock import MagicMock, create_autospec
from napari_aicssegmentation.core.router import Router, IApplication

class TestRouter:
    def setup_method(self):
        self._mock_application: MagicMock = create_autospec(IApplication)
        self._router = Router(self._mock_application)

    @mock.patch("napari_aicssegmentation.core.router.MppController")
    def test_mpp(self, mock_mpp_controller: MagicMock):
        # Act
        self._router.mpp()
        # Assert
        mock_mpp_controller.return_value.index.assert_called_once()

    @mock.patch("napari_aicssegmentation.core.router.WorkflowSelectController")
    def test_workflow_selection(self, mock_workflow_select_controller: MagicMock):
        # Act
        self._router.workflow_selection()
        # Assert
        mock_workflow_select_controller.return_value.index.assert_called_once()

    @mock.patch("napari_aicssegmentation.core.router.WorkflowStepsController")
    def test_workflow_steps(self, mock_workflow_steps_controller: MagicMock):
        # Act
        self._router.workflow_steps()
        # Assert
        mock_workflow_steps_controller.return_value.index.assert_called_once()        
