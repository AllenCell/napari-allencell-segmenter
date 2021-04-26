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
        # we're expecting either STCZYX or STZCYX but we don't know for sure
        # Attempt to guess based on array length. Channels array should be shorter in general.
        index_c = 2
        if img.shape[2] > img.shape[3]:
            index_c = 3

        channels = list()
        for index in range(img.shape[index_c]):
            channels.append(Channel(index))
        return channels

    def get_channel(self, index: int):
        """
        Get the channel at this index
        """
        return self.get_channels()[index]

    @staticmethod
    def get_channel_data(channel: Channel, layer: Layer, channel_index: int = 0):
        """
        Get the selected channel in the layer
        """
        if len(layer.data.shape) != 4:
            raise TypeError("get selected channel given Layer with < 4 dimensions")
        if channel_index == 0:
            return layer.data[channel.index, :, :, :]
        elif channel_index == 1:
            return layer.data[:, channel.index, :, :]
        elif channel_index == 2:
            return layer.data[:, :, channel.index, :]
        else:
            return layer.data[:, :, :, channel_index]
