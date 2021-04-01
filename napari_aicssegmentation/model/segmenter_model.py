from dataclasses import dataclass
from typing import List
from napari.layers import Layer

@dataclass
class SegmenterModel:
    """
    Main Segmenter plugin model
    """

    layers: List[str] = None
    selected_layer: Layer = None
    channels: List[str] = None
    selected_channel: str = None
    workflows: List[str] = None
    active_workflow: str = None

    @property
    def selected_layer_name(self):
        return self.selected_layer.name if self.selected_layer else None
