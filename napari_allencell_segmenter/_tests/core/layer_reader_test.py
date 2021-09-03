import numpy
import pytest

from aicsimageio import AICSImage
from unittest import mock
from unittest.mock import Mock, create_autospec
from napari.layers._source import Source
from napari_allencell_segmenter.core.layer_reader import LayerReader, Channel
from napari_allencell_segmenter._tests.mocks import MockLayer


class TestLayerReader:
    def setup_method(self):
        self._layer_reader = LayerReader()

    def test_get_channels_null_layer(self):
        channels = self._layer_reader.get_channels(None)
        assert channels is None

    @pytest.mark.parametrize("data", [numpy.ones((75, 4, 100, 200)), numpy.ones((75, 10, 300, 200))])  # ZCYX, CZYX
    def test_get_channels(self, data):
        # Arrange
        layer = MockLayer(name="Test", data=data)

        # Act
        channels = self._layer_reader.get_channels(layer)

        # Assert
        assert channels is not None
        # we use aicsimageio which thinks the image is in CZYX format, channels = 75
        assert len(channels) == 75

    @mock.patch("napari_allencell_segmenter.core.layer_reader.AICSImage")
    def test_get_channels_from_layer_source(self, mock_aics_image: Mock):
        # Arrange
        mock_image = create_autospec(AICSImage)

        mock_aics_image.return_value = mock_image
        img_path = "/path/to/image.tiff"
        layer = MockLayer(name="Test", source=Source(path=img_path, reader_plugin="builtins"))

        mock_channels = Mock(return_value=["Test1", "Test2", "Test3"])
        mock_image.channel_names = mock_channels.return_value

        # Act
        channels = self._layer_reader.get_channels(layer)

        # Assert
        assert channels is not None
        assert len(channels) == 3
        assert "Test1" == channels[0].name
        assert "Test2" == channels[1].name
        assert "Test3" == channels[2].name
        mock_aics_image.assert_called_with(img_path)

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

        input = numpy.ones((2, 2, 4, 5, 6, 7))
        layer = MockLayer(name="Test", data=input, ndim=6)  # 6D
        result = self._layer_reader.get_channel_data(index, layer)
        assert result.shape == (5, 6, 7)

    @pytest.mark.parametrize("index", range(0, 4))
    def test_get_channel_data_zcyx(self, index):
        # Arrange
        input = numpy.ones((75, 4, 100, 200))
        layer = MockLayer(name="Test", data=input, ndim=4)  # 4D

        # Act
        result = self._layer_reader.get_channel_data(index, layer)

        # Assert
        # no matter what, AICSIMAGE reads the numpy arrays as CZYX
        # and returns ZYX
        assert result.shape == (4, 100, 200)
        assert numpy.array_equal(result, input[index, :, :, :])

    @mock.patch("napari_allencell_segmenter.core.layer_reader.AICSImage")
    def test_get_channel_data_from_layer_source(self, mock_aics_image):
        # Arrange
        data = numpy.ones((75, 100, 100))
        mock_image = create_autospec(AICSImage)
        mock_aics_image.return_value = mock_image
        img_path = "/path/to/image.tiff"
        layer = MockLayer(name="Test", source=Source(path=img_path, reader_plugin="builtins"))
        mock_image.get_image_data.return_value = data

        # Act
        result = self._layer_reader.get_channel_data(1, layer)

        # Assert
        assert numpy.array_equal(result, data)
