from dataclasses import dataclass
from typing import List

@dataclass
class SegmenterModel:
    """
    Main Segmenter plugin model
    """
    
    channel_list: List[str] = None
    active_channel: int = None
    workflows: List[str] = None
    active_workflow: str = None

