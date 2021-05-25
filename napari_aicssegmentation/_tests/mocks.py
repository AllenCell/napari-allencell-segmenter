import numpy
from typing import NamedTuple
from napari.layers._source import Source


class MockLayer(NamedTuple):
    """
    Custom mock: napari.Layer
    """

    name: str
    data: numpy.ndarray = numpy.ones((4, 75, 100, 100))
    ndim: int = 4
    source: Source = None
