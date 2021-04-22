import pytest
from unittest.mock import MagicMock, create_autospec

from qtpy.QtWidgets import QMessageBox

from napari_aicssegmentation.view.workflow_steps_view import (
    WorkflowStepsView,
    IWorkflowStepsController,
)


class TestWorkflowStepsView:
    def setup_method(self):
        self._mock_controller: MagicMock = create_autospec(IWorkflowStepsController)
        self._view = WorkflowStepsView(self._mock_controller)
        self._view.setup_ui()

    # TODO: Add real tests once we make the UI functional
    def test_load_model(self):
        pass

    def test_add_workflow_title(self):
        pass

    def test_add_progress_bar(self):
        pass

    def test_add_workflow_steps(self):
        pass
