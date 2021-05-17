import pytest
import napari

from unittest import mock
from unittest.mock import MagicMock, create_autospec, PropertyMock
from napari_aicssegmentation.core.controller import Controller, IApplication, IRouter, State, Layer, LayerList
from napari_aicssegmentation.core.view_manager import ViewManager
from napari_aicssegmentation.core.view import View


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
        type(self._mock_application).state = PropertyMock(return_value=state)
        type(self._mock_application).router = PropertyMock(return_value=router)

        # Assert
        assert self._controller.state == state
        assert self._controller.router == router

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

    def test_add_layer(self):
        # Arrange
        viewer: MagicMock = create_autospec(napari.Viewer)
        type(self._mock_application).viewer = PropertyMock(return_value=viewer)
        image_data = [1, 2, 3, 4, 5]
        name = "Layer 1"

        # Act
        self._controller.add_layer(image_data, name)

        # Assert
        viewer.add_image.assert_called_once_with(image_data, name=name)

    def test_get_layers(self):
        # Arrange
        viewer: MagicMock = create_autospec(napari.Viewer)
        type(self._mock_application).viewer = PropertyMock(return_value=viewer)
        layers = [create_autospec(Layer), create_autospec(Layer), create_autospec(Layer)]
        viewer.layers = layers

        # Assert
        assert self._controller.get_layers() == layers

    def test_get_active_layer(self):
        # Arrange
        viewer: MagicMock = create_autospec(napari.Viewer)
        type(self._mock_application).viewer = PropertyMock(return_value=viewer)
        expected_layer = create_autospec(Layer)
        layers: MagicMock = create_autospec(LayerList)
        layers.selection = MagicMock()
        layers.selection.active = expected_layer
        viewer.layers = layers

        # Act
        active_layer = self._controller.get_active_layer()

        # Assert
        assert active_layer == expected_layer

    def test_is_image_loaded_true(self):
        # Arrange
        viewer: MagicMock = create_autospec(napari.Viewer)
        type(self._mock_application).viewer = PropertyMock(return_value=viewer)
        layers = [create_autospec(Layer), create_autospec(Layer), create_autospec(Layer)]
        viewer.layers = layers

        # Assert
        assert self._controller.is_image_loaded() == True

    def test_is_image_loaded_false(self):
        # Arrange
        viewer: MagicMock = create_autospec(napari.Viewer)
        type(self._mock_application).viewer = PropertyMock(return_value=viewer)
        viewer.layers = []

        # Assert
        assert self._controller.is_image_loaded() == False

    @mock.patch("napari_aicssegmentation.core.controller.QMessageBox")
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
