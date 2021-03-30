import pytest
from PyQt5.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

from napari_aicssegmentation.widgets.collapsible_box import CollapsibleBox

class TestCollapsibleBox:
    def setup_method(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("This is a label"))
        layout.addWidget(QPushButton("This is a button"))

        collapsible_box = CollapsibleBox(1, "Intensity Normalization", layout)

    @pytest.fixture(autouse=True)
    def setup_qt(self, qapp):
        # the pytestqt.qapp fixture sets up the QApplication required to run QT code
        # see https://pytest-qt.readthedocs.io/en/latest/reference.html
        yield

    def test_open(self):
        # Arrange


        # Act
        

        # Assert
        assert True