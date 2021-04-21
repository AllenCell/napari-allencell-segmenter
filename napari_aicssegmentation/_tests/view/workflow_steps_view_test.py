import pytest
from unittest.mock import MagicMock, create_autospec

from qtpy.QtWidgets import QMessageBox

from napari_aicssegmentation.model.channel import Channel
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
    def test_add_workflow_title(self):
        pass

    def test_add_progress_bar(self):
        pass

    def test_add_workflow_steps(self):
        pass

    def test_btn_close_clicked(self):
        pass

    def test_handle_modal_input_close_keep(self):
        # Arrange
        channel = Channel(0, "Brightfield")
        self._view._controller.model.selected_channel = channel

        # Act
        self._view.close_keep = self._view.confirmation_modal.addButton("Close workflow", QMessageBox.AcceptRole)
        self._view._handle_modal_input(self._view.close_keep)

        # Assert
        self._view._controller.model.selected_channel == None
