import pytest
import numpy as np

from qtpy import QtCore
from unittest.mock import MagicMock, PropertyMock, create_autospec
from napari_allencell_segmenter.view.workflow_select_view import (
    WorkflowSelectView,
    IWorkflowSelectController,
    SegmenterModel,
    Channel,
    WorkflowDefinition,
)
from ..mocks import MockLayer


class TestWorkflowSelectView:
    def setup_method(self):
        model = SegmenterModel()
        model.layers = ["Layer 1", "Layer 2", "Layer 3"]
        model.workflows = [
            self._get_mock_workflow_def("sec61b"),
            self._get_mock_workflow_def("lmnb1"),
            self._get_mock_workflow_def("son"),
        ]
        self._mock_controller: MagicMock = create_autospec(IWorkflowSelectController)
        self._view = WorkflowSelectView(self._mock_controller)
        self._view.load(model)

    def _get_mock_workflow_def(self, name: str) -> MagicMock:
        mock_workflow = create_autospec(WorkflowDefinition)
        type(mock_workflow).name = PropertyMock(return_value=name)
        type(mock_workflow).steps = PropertyMock(return_value=list())
        type(mock_workflow).thumbnail_pre = PropertyMock(return_value=np.ones((50, 50)))
        type(mock_workflow).thumbnail_post = PropertyMock(return_value=np.ones((50, 50)))
        return mock_workflow

    def test_load(self):
        # Assert
        assert self._view._combo_layers.count() == 4  # 4 because of header

    @pytest.mark.parametrize("layers", [None, list()])
    def test_update_layers_without_layers(self, layers):
        # Act
        self._view.update_layers(layers)

        # Assert
        assert self._view._load_image_warning.isVisibleTo(self._view)
        assert not self._view._combo_layers.isEnabled()

    def test_update_layers_with_layers(self):
        layers = ["Layer 1", "Layer 2", "Layer 3"]

        # Act
        self._view.update_layers(layers, MockLayer("Layer 2"))

        # Assert
        assert self._view._combo_layers.count() == 4  # 4 because of header
        assert self._view._combo_layers.currentText() == "Layer 2"
        assert not self._view._load_image_warning.isVisibleTo(self._view)
        assert self._view._combo_layers.isEnabled()

    @pytest.mark.parametrize("channels", [None, list()])
    def test_update_channels_without_channels(self, channels):
        # Act
        self._view.update_channels(channels)
        # Assert
        assert not self._view._combo_channels.isEnabled()

    def test_update_channels_with_channels(self):
        selected_channel = Channel(2)
        channels = [Channel(0), Channel(1), selected_channel]

        # Act
        self._view.update_channels(channels, selected_channel)

        # Assert
        assert self._view._combo_channels.count() == 4  # 4 because of header
        assert self._view._combo_channels.currentData(QtCore.Qt.UserRole) == selected_channel
        assert self._view._combo_channels.isEnabled()

    def test_combo_layers_activated_select(self):
        # Arrange
        self._view._combo_layers.addItems(["Layer 1", "Layer 2", "Layer 3"])

        # Act
        self._view._combo_layers.activated.emit(1)

        # Assert
        self._mock_controller.select_layer.assert_called_with("Layer 3")

    def test_combo_layers_activated_unselect(self):
        # Arrange
        self._view._combo_layers.addItems(["Layer 1", "Layer 2", "Layer 3"])

        # Act
        self._view._combo_layers.activated.emit(1)
        self._view._combo_layers.activated.emit(0)

        # Assert
        self._mock_controller.unselect_layer.assert_called()

    def test_combo_channels_activated_select(self):
        # Arrange
        expected_channel = Channel(0)
        channels = [expected_channel, Channel(1), Channel(2), Channel(3)]
        self._view.update_channels(channels)

        # Act
        self._view._combo_channels.activated.emit(1)

        # Assert
        self._mock_controller.select_channel.assert_called_with(expected_channel)

    def test_combo_channels_activated_unselect(self):
        # Arrange
        channels = [Channel(0), Channel(1), Channel(2), Channel(3)]
        self._view.update_channels(channels)

        # Act
        self._view._combo_channels.activated.emit(1)
        self._view._combo_channels.activated.emit(0)

        # Assert
        self._mock_controller.unselect_channel.assert_called()
