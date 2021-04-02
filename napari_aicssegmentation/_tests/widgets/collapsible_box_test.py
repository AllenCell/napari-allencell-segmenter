import pytest
from PyQt5.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

from napari_aicssegmentation.widgets.collapsible_box import CollapsibleBox


class TestCollapsibleBox:
    def setup_class(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("This is a label"))
        layout.addWidget(QPushButton("This is a button"))

        self.collapsible_box = CollapsibleBox("1. Intensity Normalization", layout)

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

    def test_toggle(self):
        # Arrange - Box starts out open
        assert self.collapsible_box.isOpen is True
        assert self.collapsible_box.content_box.isHidden() is False
        assert self.collapsible_box.title_box.objectName() == ""

        # Act
        self.collapsible_box.toggle()

        # Assert - box should be closed and contents hidden
        assert self.collapsible_box.isOpen is False
        assert self.collapsible_box.content_box.isHidden() is True
        assert self.collapsible_box.title_box.objectName() == "titleBoxClosed"

        # Act
        self.collapsible_box.toggle()

        # Assert - box should be open and contents visible
        assert self.collapsible_box.isOpen is True
        assert self.collapsible_box.content_box.isHidden() is False
        assert self.collapsible_box.title_box.objectName() == ""
