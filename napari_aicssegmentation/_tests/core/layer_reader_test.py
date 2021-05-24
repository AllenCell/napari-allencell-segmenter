import numpy
import pytest

from napari_aicssegmentation.core.layer_reader import LayerReader, Channel
from ..mocks import MockLayer


class TestLayerReader:
    def setup_method(self):
        self._layer_reader = LayerReader()

    def test_get_channels_null_layer(self):
        channels = self._layer_reader.get_channels(None)
        assert channels is None

    @pytest.mark.parametrize("data", [numpy.ones((75, 4, 100, 200)), numpy.ones((4, 75, 100, 200))])  # ZCYX, CZYX
    def test_get_channels(self, data):
        # Arrange
        layer = MockLayer(name="Test", data=data)

        # Act
        channels = self._layer_reader.get_channels(layer)

        # Assert
        assert channels is not None
        assert len(channels) == 4
    
    def test_get_channels_from_layer_source(self, resources_dir):
        # Arrange
        # TODO mock AICSImage
        pass


    def test_get_channel_data_null_layer_fails(self):
        # Assert
        with pytest.raises(ValueError):
            self._layer_reader.get_channel_data(1, None)

    @pytest.mark.parametrize("index", range(0, 4))
    def test_get_channel_data_czyx(self, index):
        # Arrange
        input = numpy.ones((4, 75, 100, 100))
        layer = MockLayer(name="Test", data=input, ndim=4)  # 4D

        # Act
        result = self._layer_reader.get_channel_data(index, layer)

        # Assert
        assert result.shape == (75, 100, 100)
        assert numpy.array_equal(result, input[index])

    @pytest.mark.parametrize("index", range(0, 4))
    def test_get_channel_data_zcyx(self, index):
        # Arrange
        input = numpy.ones((75, 4, 100, 200))
        layer = MockLayer(name="Test", data=input, ndim=4)  # 4D

        # Act
        result = self._layer_reader.get_channel_data(index, layer)

        # Assert
        assert result.shape == (75, 100, 200)
        assert numpy.array_equal(result, input[:, index, :, :])
