import pytest
import napari
from unittest.mock import MagicMock, create_autospec
from napari_aicssegmentation.core.application import Application, ViewManager, Router, State
from qtpy.QtWidgets import QLayout


class TestApplication:
    def test_properties(self):
        # Arrange
        viewer: MagicMock = create_autospec(napari.Viewer)

        # Act
        app = Application(viewer, create_autospec(QLayout))

        # Assert
        assert app.router is not None
        assert type(app.router) == Router
        assert app.state is not None
        assert type(app.state) == State
        assert app.view_manager is not None
        assert type(app.view_manager) == ViewManager
        assert app.viewer == viewer
