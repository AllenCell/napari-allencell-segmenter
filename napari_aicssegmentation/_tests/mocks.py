import numpy
from typing import NamedTuple


class MockLayer(NamedTuple):
    """
    Custom mock: napari.Layer
    """

    name: str
    data: numpy.ndarray = numpy.ones((4, 75, 100, 100))
    ndim: int = 4
