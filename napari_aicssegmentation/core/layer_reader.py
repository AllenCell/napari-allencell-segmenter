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
        """
        if layer is None:
            return None

        img = AICSImage(layer.data)  # gives us a 6D image

        channels = list()
        for index in range(img.shape[3]):
            channels.append(Channel(index))
        return channels
