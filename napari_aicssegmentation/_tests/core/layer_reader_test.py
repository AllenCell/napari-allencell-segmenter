import numpy
import pytest

from napari_aicssegmentation.core.layer_reader import LayerReader
from ..mocks import MockLayer


class TestLayerReader:
    def setup_method(self):
        self._layer_reader = LayerReader()

    def test_get_channels_null_layer(self):
        channels = self._layer_reader.get_channels(None)
        assert channels is None

    @pytest.mark.parametrize("data", [numpy.ones((75, 4, 600, 900)), numpy.ones((4, 75, 600, 900))])  # ZCYX, CZYX
    def test_get_channels(self, data):
        # Arrange
        layer = MockLayer(name="Test", data=data)

        # Act
        channels = self._layer_reader.get_channels(layer)

        # Assert
        assert channels is not None
        assert len(channels) == 4
