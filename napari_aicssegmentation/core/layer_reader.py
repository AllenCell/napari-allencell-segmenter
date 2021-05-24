import numpy as np
import logging

from typing import List
from aicsimageio import AICSImage
from napari.layers import Layer
from napari_aicssegmentation.model.channel import Channel

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

        if layer.source is not None and layer.source.path is not None:
            try:
                return self._get_channels_from_path(layer.source.path)
            except Exception as ex:
                log.warning("Could not read image layer from source path even though a source path was provided."
                            "Defaulting to reading from layer data (this is less accurate). \n"
                            f"Error message: {ex}")

        return self._get_channels_default(layer)
    
    def _get_channels_default(self, layer: Layer):
        img = AICSImage(layer.data)  # gives us a 6D image

        # we're expecting either STCZYX or STZCYX but we don't know for sure
        # Attempt to guess based on array length. Channels array should be shorter in general.
        index_c = 2
        if img.shape[2] > img.shape[3]:
            index_c = 3

        channels = list()
        for index in range(img.shape[index_c]):
            channels.append(Channel(index))
        return channels

    def _get_channels_from_path(self, image_path: str) -> List[Channel]:
        img = AICSImage(image_path)

        channels = list()
        for index, name in enumerate(img.get_channel_names()):
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

        if layer.source is not None and layer.source.path is not None:
            try:
                return self._get_channel_data_from_path(channel_index, layer.source.path)
            except Exception as ex:
                log.warning("Could not read image layer from source path even though a source path was provided."
                            "Defaulting to reading from layer data (this is less accurate). \n"
                            f"Error message: {ex}")

        return self._get_channel_data_default(channel_index, layer)

    def _get_channel_data_default(self, channel_index: int, layer: Layer):
        img = AICSImage(layer.data)  # gives us a 6D image

        # we're expecting either STCZYX or STZCYX but we don't know for sure
        # Attempt to guess based on array length. Channels array should be shorter in general.
        if img.shape[2] > img.shape[3]:
            return img.data[0, 0, :, channel_index, :, :]  # STZCYX

        return img.data[0, 0, channel_index, :, :, :]  # STCZYX

    def _get_channel_data_from_path(self, channel_index: int, image_path: str):
        img = AICSImage(image_path)
        return img.get_image_data("ZYX", T=0, S=0, C=channel_index)
