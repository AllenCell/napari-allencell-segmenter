import numpy as np

from typing import List
from aicsimageio import AICSImage
from napari.layers import Layer
from napari_aicssegmentation.model.channel import Channel


class LayerReader:
    """
    Reader / Helper class to extract information out of Napari Layers
    """

    def get_channels(self, layer: Layer) -> List[Channel]:
        """
        Get the list of image channels from a layer
        TODO this is a workaround for now and we just guess the Channel dimension based on its
             location for most ome tiffs
        TODO use aicsimageio to read image from the source file path and get channel names
             once Napari exposes Image layer source (next release)

        inputs:
            layer (Layer): the Napari layer to read data from
        """
        if layer is None:
            return None

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

    def get_channel_data(self, channel_index: int, layer: Layer) -> np.ndarray:
        """
        Get the image data from the layer for a given channel
        TODO this is a workaround for now and we just guess the Channel dimension based on its
             location for most ome tiffs
        TODO use aicsimageio to read image from the source file path and get channel names
             once Napari exposes Image layer source (next release)

        inputs:
            channel_index (int): index of the channel to load
            layer (Layer): the Napari layer to read data from
        """
        if layer is None:
            raise ValueError("layer cannot be None")

        img = AICSImage(layer.data)  # gives us a 6D image

        # we're expecting either STCZYX or STZCYX but we don't know for sure
        # Attempt to guess based on array length. Channels array should be shorter in general.
        if img.shape[2] > img.shape[3]:
            return img.data[0, 0, :, channel_index, :, :]  # STZCYX

        return img.data[0, 0, channel_index, :, :, :]  # STCZYX
