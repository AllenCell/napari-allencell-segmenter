import pytest

from unittest import mock
from unittest.mock import MagicMock, create_autospec, PropertyMock
from napari_allencell_segmenter.core.controller import Controller, IApplication, IRouter, State
from napari_allencell_segmenter.core.view_manager import ViewManager
from napari_allencell_segmenter.core.view import View
from napari_allencell_segmenter.core.viewer_abstraction import ViewerAbstraction


class MockController(Controller):
    def index():
        pass


class TestController:
    def setup_method(self):
        self._mock_application: MagicMock = create_autospec(IApplication)
        self._controller = MockController(self._mock_application)

    def test_properties(self):
        # Arrange
        state: MagicMock = create_autospec(State)
        router: MagicMock = create_autospec(IRouter)
        viewer: MagicMock = create_autospec(ViewerAbstraction)
        type(self._mock_application).state = PropertyMock(return_value=state)
        type(self._mock_application).router = PropertyMock(return_value=router)
        type(self._mock_application).viewer = PropertyMock(return_value=viewer)

        # Assert
        assert self._controller.state == state
        assert self._controller.router == router
        assert self._controller.viewer == viewer

    def test_load_view(self):
        # Arrange
        view_manager: MagicMock = create_autospec(ViewManager)
        type(self._mock_application).view_manager = PropertyMock(return_value=view_manager)
        view: MagicMock = create_autospec(View)
        model = object()

        # Act
        self._controller.load_view(view, model)

        # Assert
        view_manager.load_view.assert_called_once_with(view, model)

    @mock.patch("napari_allencell_segmenter.core.controller.QMessageBox")
    def test_show_message_box(self, mock_message_box: MagicMock):
        # Arrange
        title = "test"
        message = "this is a test"

        # Act
        self._controller.show_message_box(title, message)

        # Assert
        mock_message_box.return_value.setWindowTitle.assert_called_once_with(title)
        mock_message_box.return_value.setText.assert_called_once_with(message)
        mock_message_box.return_value.exec.assert_called_once()
