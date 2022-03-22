import numpy as np
import logging

from typing import List
from aicsimageio import AICSImage
from napari.layers import Layer
from napari_allencell_segmenter.model.channel import Channel

log = logging.getLogger(__name__)


class LayerReader:
    """
    Reader / Helper class to extract information out of Napari Layers
    """

    def get_channels(self, layer: Layer) -> List[Channel]:
        """
        Get the list of image channels from a layer

        inputs:
            layer (Layer): the Napari layer to read data from
        """
        if layer is None:
            return None

        if self._should_read_from_path(layer):
            try:
                return self._get_channels_from_path(layer.source.path)
            except Exception as ex:
                log.warning(
                    "Could not read image layer from source path even though a source path was provided."
                    "Defaulting to reading from layer data (this is less accurate). \n"
                    f"Error message: {ex}"
                )

        return self._get_channels_default(layer)

    def _get_channels_default(self, layer: Layer) -> List[Channel]:
        if len(layer.data.shape) == 6:
            # Has scenes
            image_from_layer = [layer.data[i, :, :, :, :, :] for i in range(layer.data.shape[0])]
        else:
            image_from_layer = layer.data
        img = AICSImage(image_from_layer)  # gives us a 6D image
        img.set_scene(0)

        index_c = img.dims.order.index("C")

        channels = list()
        for index in range(img.shape[index_c]):
            channels.append(Channel(index))
        return channels

    def _get_channels_from_path(self, image_path: str) -> List[Channel]:
        img = AICSImage(image_path)
        img.set_scene(0)

        channels = list()
        for index, name in enumerate(img.channel_names):
            channels.append(Channel(index, name))
        return channels

    def get_channel_data(self, channel_index: int, layer: Layer) -> np.ndarray:
        """
        Get the image data from the layer for a given channel

        inputs:
            channel_index (int): index of the channel to load
            layer (Layer): the Napari layer to read data from
        """
        if channel_index is None:
            raise ValueError("channel_index is None")
        if layer is None:
            raise ValueError("layer is None")

        if self._should_read_from_path(layer):
            try:
                return self._get_channel_data_from_path(channel_index, layer.source.path)
            except Exception as ex:
                log.warning(
                    "Could not read image layer from source path even though a source path was provided."
                    "Defaulting to reading from layer data (this is less accurate). \n"
                    f"Error message: {ex}"
                )

        return self._get_channel_data_default(channel_index, layer)

    def _get_channel_data_default(self, channel_index: int, layer: Layer):
        if len(layer.data.shape) >= 6:
            # Has scenes
            image_from_layer = [layer.data[i, :, :, :, :, :] for i in range(layer.data.shape[0])]
        else:
            image_from_layer = layer.data

        img = AICSImage(image_from_layer)  # gives us a 6D image

        # use get_image_data() to parse out ZYX dimensions
        # segmenter requries 3D images.
        img.set_scene(0)
        return img.get_image_data("ZYX", T=0, C=channel_index)

    def _get_channel_data_from_path(self, channel_index: int, image_path: str):
        img = AICSImage(image_path)
        img.set_scene(0)
        return img.get_image_data("ZYX", T=0, C=channel_index)

    def _should_read_from_path(self, layer: Layer):
        if layer.source is None:
            return False
        if layer.source.path is None:
            return False
        # Here we are making a deliberate choice to not try and load metadata from the srouce
        # if a reader plugin other than the default built-in plugin was used. This is because
        # plugins like napari-aicsimageio may convert channels into individual layers, which is not compatible
        # with the current plugin User Experience. This is a workaround to allow basic compatibility
        # with reader plugins and allow to do work with CZI files and other formats supported by napari-aicsimageio
        # TODO - come up with a better long term solution
        if layer.source.reader_plugin != "builtins":
            return False

        return True
