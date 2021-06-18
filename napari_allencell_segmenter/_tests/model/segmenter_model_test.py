import pytest

from napari_allencell_segmenter.model.channel import Channel
from napari_allencell_segmenter.model.segmenter_model import SegmenterModel


class TestSegmenterModel:
    def test_reset(self):
        # Arrange
        layers = ["layer 1", "layer 2"]
        selected_layer = None
        channels = ["channel 1", "channel 2"]
        selected_channel = Channel(1, "channel 1")
        workflows = ["laminb", "sec61b"]
        active_workflow = "laminb"

        model = SegmenterModel(layers, selected_layer, channels, selected_channel, workflows, active_workflow)

        # Act
        model.reset()

        # Assert
        assert model.layers is None
        assert model.selected_layer is None
        assert model.channels is None
        assert model.workflows is None
        assert model.active_workflow is None
