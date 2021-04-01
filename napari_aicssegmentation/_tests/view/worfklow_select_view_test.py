import pytest

from unittest.mock import MagicMock, create_autospec
from napari_aicssegmentation.view.workflow_select_view import (
    WorkflowSelectView,
    IWorkflowSelectController,
    SegmenterModel,
)


class TestWorkflowSelectView:
    def setup_method(self):
        self._mock_controller: MagicMock = create_autospec(IWorkflowSelectController)
        self._view = WorkflowSelectView(self._mock_controller)
        self._view.setup_ui()

    def test_load_model(self):
        # Arrange        
        model = SegmenterModel()
        model.layers = ["Layer 1", "Layer 2", "Layer 3"]                

        # Act
        self._view.load_model(model)

        # Assert
        assert self._view.combo_layers.count() == 4 # 4 because of header        

    @pytest.mark.parametrize("layers", [None, list()])
    def test_update_layers_without_layers(self, layers):
        # Act
        self._view.update_layers(layers)

        # Assert
        assert self._view.load_image_warning.isVisibleTo(self._view)
        assert not self._view.combo_layers.isEnabled()

    def test_update_layers_with_layers(self):
        layers = ["Layer 1", "Layer 2", "Layer 3"]

        # Act
        self._view.update_layers(layers, "Layer 2")

        # Assert
        assert self._view.combo_layers.count() == 4 # 4 because of header 
        assert self._view.combo_layers.currentText() == "Layer 2"
        assert self._view.combo_layers.itemText(1) == "Layer 1"
        assert self._view.combo_layers.itemText(2) == "Layer 2"
        assert self._view.combo_layers.itemText(3) == "Layer 3"
        assert not self._view.load_image_warning.isVisibleTo(self._view)
        assert self._view.combo_layers.isEnabled()        

    def test_combo_layers_index_changed_select(self):
        # Arrange        
        self._view.combo_layers.addItems(["Layer 1", "Layer 2", "Layer 3"])

        # Act
        self._view.combo_layers.setCurrentIndex(1)

        # Assert
        self._mock_controller.select_layer.assert_called_with("Layer 1")

    def test_combo_layers_index_changed_unselect(self):
        # Arrange        
        self._view.combo_layers.addItems(["Layer 1", "Layer 2", "Layer 3"])

        # Act
        self._view.combo_layers.setCurrentIndex(1)
        self._view.combo_layers.setCurrentIndex(0)

        # Assert
        self._mock_controller.unselect_layer.assert_called()
    