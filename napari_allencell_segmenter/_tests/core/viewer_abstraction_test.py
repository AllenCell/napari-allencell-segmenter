import pytest
import napari

from unittest.mock import MagicMock, create_autospec, PropertyMock
from napari_allencell_segmenter.core.viewer_abstraction import ViewerAbstraction, Layer, LayerList


class TestViewerAbstraction:
    def setup_method(self):
        self._viewer = create_autospec(napari.Viewer)
        self._viewer_abstraction = ViewerAbstraction(self._viewer)

    def test_add_image_layer(self):
        # Arrange
        expected_layer = create_autospec(Layer)
        self._viewer.add_image.return_value = expected_layer

        # Act
        result = self._viewer_abstraction.add_image_layer([1, 2, 3, 4, 5], "Layer 1")

        # Assert
        assert result == expected_layer

    def test_get_layers(self):
        # Arrange
        layers = [create_autospec(Layer), create_autospec(Layer), create_autospec(Layer)]
        type(self._viewer).layers = PropertyMock(return_value=layers)

        # Assert
        assert self._viewer_abstraction.get_layers() == layers

    def test_get_active_layer(self):
        # Arrange
        expected_layer = create_autospec(Layer)
        layers: MagicMock = create_autospec(LayerList)
        layers.selection = MagicMock()
        layers.selection.active = expected_layer
        type(self._viewer).layers = PropertyMock(return_value=layers)

        # Act
        active_layer = self._viewer_abstraction.get_active_layer()

        # Assert
        assert active_layer == [expected_layer]
