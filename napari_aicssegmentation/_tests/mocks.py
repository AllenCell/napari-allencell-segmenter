import numpy
from typing import NamedTuple


class MockLayer(NamedTuple):
    """
    Custom mock: napari.Layer
    """

    name: str
    data: numpy.ndarray = numpy.ones((1, 1, 1, 1))
    ndim: int = 0
