import pytest

from unittest.mock import MagicMock, create_autospec
from napari_aicssegmentation.view.workflow_steps_view import (
    WorkflowStepsView,
    IWorkflowStepsController,
    SegmenterModel,
)


class TestWorkflowSelectView:
    def setup_method(self):
        self._mock_controller: MagicMock = create_autospec(IWorkflowStepsController)
        self._view = WorkflowStepsView(self._mock_controller)
        self._view.setup_ui()
