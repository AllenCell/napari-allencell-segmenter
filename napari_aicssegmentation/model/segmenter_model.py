from dataclasses import dataclass
from typing import List


@dataclass
class SegmenterModel:
    """
    Main Segmenter plugin model
    """

    layer_list: List[str] = None
    active_layer: int = None
    channel_list: List[str] = None
    active_channel: int = None
    workflows: List[str] = None
    active_workflow: str = None
