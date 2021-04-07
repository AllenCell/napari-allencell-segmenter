from dataclasses import dataclass
from typing import List
from napari.layers import Layer
from .channel import Channel


@dataclass
class SegmenterModel:
    """
    Main Segmenter plugin model
    """

    layers: List[str] = None
    selected_layer: Layer = None
    channels: List[str] = None
    selected_channel: Channel = None
    workflows: List[str] = None
    active_workflow: str = None
