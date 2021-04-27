import pytest
import numpy as np

from unittest.mock import MagicMock, create_autospec
from napari_aicssegmentation.view.workflow_steps_view import WorkflowStepsView, IWorkflowStepsController, SegmenterModel
from aicssegmentation.workflow import WorkflowEngine


class TestWorkflowStepsView:
    def setup_method(self):
        model = SegmenterModel()
        # TODO mock this?
        model.active_workflow = WorkflowEngine().get_executable_workflow("sec61b", np.ones((1, 1, 1)))
        self._mock_controller: MagicMock = create_autospec(IWorkflowStepsController)
        self._view = WorkflowStepsView(self._mock_controller)
        self._view.load(model)

    # TODO: Add real tests once we make the UI functional
    def test_load_model(self):
        pass

    def test_add_workflow_title(self):
        pass

    def test_add_progress_bar(self):
        pass

    def test_add_workflow_steps(self):
        pass
