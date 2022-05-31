import numpy
from typing import NamedTuple
from napari.layers._source import Source
from unittest.mock import Mock


class MockLayer(NamedTuple):
    """
    Custom mock: napari.Layer
    """

    name: str
    data: numpy.ndarray = numpy.ones((4, 75, 100, 100))
    ndim: int = 4
    source: Source = None
    visible: bool = True


class MockWorker:
    """
    Custom mock: napari.qt.GeneratorWorker
    """

    def __init__(self):
        self.yielded = Mock()
        self.started = Mock()
        self.finished = Mock()
        self.start = Mock()
