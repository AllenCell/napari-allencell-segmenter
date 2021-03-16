from PyQt5.QtWidgets import QVBoxLayout
import pytest

from unittest import mock
from unittest.mock import MagicMock, create_autospec
from napari_aicssegmentation.core.view_manager import ViewManager, View


class TestViewManager:
    def setup_method(self):
        self._base_layout = QVBoxLayout()
        self._view_manager = ViewManager(self._base_layout)

    def test_current_view(self):
        # Arrange
        view1: MagicMock = create_autospec(View)
        view1.get_layout.return_value = QVBoxLayout()
        view2: MagicMock = create_autospec(View)
        view2.get_layout.return_value = QVBoxLayout()

        # Act / Assert
        self._view_manager.load_view(view1)
        assert self._view_manager.current_view == view1
        self._view_manager.load_view(view2)
        assert self._view_manager.current_view == view2

    def test_load_view_happy_path(self):
        # Arrange
        layout = QVBoxLayout()
        view: MagicMock = create_autospec(View)
        view.get_layout.return_value = layout

        # Act
        self._view_manager.load_view(view)

        # Assert
        assert self._base_layout.children()[0] == layout
        view.setup_ui.assert_called_once()

    def test_load_view_replaces_existing_layout(self):
        # Arrange
        view1: MagicMock = create_autospec(View)
        view1.get_layout.return_value = QVBoxLayout()
        view2: MagicMock = create_autospec(View)
        view2.get_layout.return_value = QVBoxLayout()

        # Act
        self._view_manager.load_view(view1)
        self._view_manager.load_view(view2)

        # Assert
        assert len(self._base_layout.children()) == 1

    def test_load_view_null_view(self):
        # Assert
        with pytest.raises(ValueError):
            self._view_manager.load_view(None)

    @pytest.mark.parametrize("layout", [None, object()])
    def test_load_view_invalid_layout(self, layout):
        # Arrange
        view: MagicMock = create_autospec(View)
        view.get_layout.return_value = layout

        # Assert
        with pytest.raises(ValueError):
            self._view_manager.load_view(view)
