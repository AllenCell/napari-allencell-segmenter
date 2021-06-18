import pytest
import napari
from unittest.mock import MagicMock, create_autospec
from napari_allencell_segmenter.core.application import Application, ViewManager, Router, State, ViewerAbstraction
from qtpy.QtWidgets import QLayout


class TestApplication:
    def test_properties(self):
        app = Application(create_autospec(napari.Viewer), create_autospec(QLayout))

        assert app.router is not None
        assert type(app.router) == Router
        assert app.state is not None
        assert type(app.state) == State
        assert app.view_manager is not None
        assert type(app.view_manager) == ViewManager
        assert app.viewer is not None
        assert type(app.viewer) == ViewerAbstraction
