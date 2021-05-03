import pytest
import numpy as np
import os

from unittest.mock import MagicMock, create_autospec
from napari_aicssegmentation.view.workflow_steps_view import WorkflowStepsView, IWorkflowStepsController, SegmenterModel
from aicssegmentation.workflow import WorkflowEngine


class TestWorkflowStepsView:
    def setup_method(self):
        model = SegmenterModel()
        model.active_workflow = WorkflowEngine().get_executable_workflow("sec61b", np.ones((1, 1, 1)))
        self._mock_controller: MagicMock = create_autospec(IWorkflowStepsController)
        self._view = WorkflowStepsView(self._mock_controller)
        self._view.load(model)

    def test_show_workflow_diagram(self):
        assert not self._view.window_workflow_diagram.isVisible()
        self._view.btn_workflow_info.clicked.emit(False)
        assert self._view.window_workflow_diagram.isVisible()

    def test_run_all(self):
        self._view.btn_run_all.clicked.emit(False)
        self._mock_controller.run_all.assert_called_once()

    def test_close_workflow_keep_layers(self):
        self._view.btn_close_keep.clicked.emit(False)
        self._mock_controller.close_workflow.assert_called_once()
