import pytest

from unittest.mock import MagicMock, create_autospec
from napari_aicssegmentation.view.workflow_select_view import WorkflowSelectView, IWorkflowSelectController, SegmenterModel
from PyQt5.QtWidgets import QLayout

class TestWorkflowSelectView:
    def setup_method(self):
        self._mock_controller: MagicMock = create_autospec(IWorkflowSelectController)
        self._view = WorkflowSelectView(self._mock_controller)

    @pytest.fixture(autouse=True)
    def setup_qt(self, qapp):
        # the pytestqt.qapp fixture sets up the QApplication required to run QT code
        # see https://pytest-qt.readthedocs.io/en/latest/reference.html
        yield

    def test_setup_ui(self):
        # Act
        self._view.setup_ui()

        # Assert
        assert self._view.combo_channels is not None
        assert self._view.combo_workflows is not None
        assert self._view.lbl_select is not None
        assert self._view.lbl_title is not None
        assert self._view.btn_back is not None
        assert self._view.btn_next is not None

    def test_get_layout(self):
        layout = self._view.get_layout()
        assert layout is not None
        assert isinstance(layout, QLayout)

    def test_load_model(self):
        # Arrange
        self._view.setup_ui()
        model = SegmenterModel()
        model.channel_list = ["a", "b", "c"]
        model.workflows = ["d", "e", "f", "g"]

        # Act
        self._view.load_model(model)

        # Assert
        assert self._view.combo_channels.count() == 3
        assert self._view.combo_workflows.count() == 4

    def test_btn_back_clicked(self):
        # Arrange
        self._view.setup_ui()

        # Act
        self._view.btn_back.click()

        # Assert
        self._mock_controller.navigate_back.assert_called_once()

    def test_btn_next_clicked(self):
        # Arrange
        self._view.setup_ui()  

        # Act
        self._view.btn_next.click()

        # Assert
        self._mock_controller.navigate_next.assert_called_once()

    def test_combo_channels_index_changed(self):
        # Arrange
        self._view.setup_ui()
        self._view.combo_channels.addItems(["a", "b", "c"])

        # Act
        self._view.combo_channels.setCurrentIndex(1)

        # Assert
        self._mock_controller.select_channel.assert_called()

    def test_combo_workflows_index_changed(self):
        # Arrange
        self._view.setup_ui()
        self._view.combo_workflows.addItems(["a", "b", "c"])

        # Act
        self._view.combo_workflows.setCurrentIndex(1)

        # Assert
        self._mock_controller.select_workflow.assert_called()
