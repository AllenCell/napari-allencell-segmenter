import pytest
from qtpy.QtWidgets import QLabel, QPushButton, QVBoxLayout

from napari_allencell_segmenter.widgets.collapsible_box import CollapsibleBox
from napari_allencell_segmenter.widgets.workflow_step_widget import WorkflowStepWidget
from aicssegmentation.workflow import WorkflowStep, SegmenterFunction
from unittest.mock import MagicMock, create_autospec


class TestCollapsibleBox:
    def setup_class(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("This is a label"))
        layout.addWidget(QPushButton("This is a button"))
        widget = create_autospec(WorkflowStepWidget)
        step = create_autospec(WorkflowStep)
        step.function = create_autospec(SegmenterFunction)
        step.function.parameters = None
        widget.step = step

        self.collapsible_box = CollapsibleBox("1. Intensity Normalization", layout, widget)

    def test_open(self):
        # Assert - box should be closed and contents hidden
        assert self.collapsible_box.isOpen is False
        assert self.collapsible_box.content_box.isHidden() is True
        assert self.collapsible_box.title_box.objectName() == "titleBoxClosed"

        # Act
        self.collapsible_box.open()

        # Assert - box should be open and contents visible
        assert self.collapsible_box.isOpen is True
        assert self.collapsible_box.content_box.isHidden() is False
        assert self.collapsible_box.title_box.objectName() == ""

    def test_close(self):
        # Arrange - box starts out open
        assert self.collapsible_box.isOpen is True
        assert self.collapsible_box.content_box.isHidden() is False
        assert self.collapsible_box.title_box.objectName() == ""

        # Act
        self.collapsible_box.close()

        # Assert - box should be closed and contents hidden
        assert self.collapsible_box.isOpen is False
        assert self.collapsible_box.content_box.isHidden() is True
        assert self.collapsible_box.title_box.objectName() == "titleBoxClosed"

    def test_toggle(self):
        # Arrange - Box starts out closed
        assert self.collapsible_box.isOpen is False
        assert self.collapsible_box.content_box.isHidden() is True
        assert self.collapsible_box.title_box.objectName() == "titleBoxClosed"

        # Act
        self.collapsible_box.toggle()

        # Assert - box should be open and contents visible
        assert self.collapsible_box.isOpen is True
        assert self.collapsible_box.content_box.isHidden() is False
        assert self.collapsible_box.title_box.objectName() == ""

        # Act
        self.collapsible_box.toggle()

        # Assert - box should be closed and contents hidden
        assert self.collapsible_box.isOpen is False
        assert self.collapsible_box.content_box.isHidden() is True
        assert self.collapsible_box.title_box.objectName() == "titleBoxClosed"
