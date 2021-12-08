from typing import List
from qtpy.QtWidgets import QPushButton
import pytest

from aicssegmentation.workflow import WorkflowEngine
from napari_allencell_segmenter.widgets.workflow_thumbnails import WorkflowThumbnails


class TestWorkflowThumbnails:
    def setup_method(self):
        self._workflow_definitions = WorkflowEngine().workflow_definitions

    def test_make_widget(self):
        assert WorkflowThumbnails() is not None
        widget = WorkflowThumbnails(self._workflow_definitions)
        assert widget is not None
        assert widget.workflow_definitions == self._workflow_definitions

    def test_load_workflows(self):
        widget = WorkflowThumbnails()
        widget.load_workflows(self._workflow_definitions)
        assert widget.workflow_definitions == self._workflow_definitions

    def test_signal_workflow_selected(self):
        # Arrange
        self._counter = 0

        def _workflow_selected():
            self._counter += 1

        widget = WorkflowThumbnails(self._workflow_definitions)
        widget.workflowSelected.connect(_workflow_selected)
        buttons: List[QPushButton] = widget.findChildren(QPushButton)

        # Act
        for button in buttons:
            button.clicked.emit(False)

        # Assert
        assert len(buttons) > 0
        assert self._counter == len(buttons)
