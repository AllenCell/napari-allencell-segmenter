import pytest

from unittest.mock import MagicMock, create_autospec
from napari_aicssegmentation.core.view_manager import ViewManager
from napari_aicssegmentation.core.view import View, ViewTemplate
from PyQt5.QtWidgets import QFrame, QVBoxLayout

# Custom Mock view implementations because QT doesn't like MagicMock widgets
class MockViewTemplate1(ViewTemplate):
    setup_ui_called = False
    
    def __init__(self):
        super().__init__()
        self._frame = QFrame()
        self._frame.setLayout(QVBoxLayout())
    
    def setup_ui(self):
        self.setup_ui_called = True

    def get_container(self) -> QFrame:
        return self._frame

class MockViewTemplate2(ViewTemplate):
    setup_ui_called = False
    
    def __init__(self):
        super().__init__(template_class=MockViewTemplate1)
        self._frame = QFrame()
        self._frame.setLayout(QVBoxLayout())
    
    def setup_ui(self):
        self.setup_ui_called = True

    def get_container(self) -> QFrame:
        return self._frame

class MockView(View):
    setup_ui_called = False
    def setup_ui(self):
        self.setup_ui_called = True

class TestViewManager:
    def setup_method(self):
        self._base_layout = QVBoxLayout()
        self._view_manager = ViewManager(self._base_layout)

    def test_current_view(self):
        # Arrange
        view1: MagicMock = MockView()             
        view2: MagicMock = MockView()                

        # Act / Assert
        self._view_manager.load_view(view1)
        assert self._view_manager.current_view == view1
        self._view_manager.load_view(view2)
        assert self._view_manager.current_view == view2

    def test_load_view_no_template(self):
        # Arrange        
        view = MockView()      

        # Act
        self._view_manager.load_view(view)

        # Assert
        assert self._base_layout.itemAt(0).widget() == view
        assert view.setup_ui_called == True

    def test_load_view_with_template(self):
        # Arrange                
        view = MockView(template_class=MockViewTemplate1)
        
        # Act
        self._view_manager.load_view(view)

        # Assert
        assert self._view_manager.current_view == view.template
        assert self._base_layout.itemAt(0).widget() == view.template
        assert view.template.get_container().layout().itemAt(0).widget() == view
        assert view.template.setup_ui_called == True
        assert view.setup_ui_called == True

    def test_load_view_with_nested_templates(self):
        # Arrange                
        view = MockView(template_class=MockViewTemplate2)
        
        # Act
        self._view_manager.load_view(view)

        # Assert
        assert self._view_manager.current_view == view.template.template
        assert self._base_layout.itemAt(0).widget() == view.template.template
        assert view.template.setup_ui_called == True
        assert view.template.template.setup_ui_called == True
        assert view.setup_ui_called == True

    def test_load_view_null_view(self):
        # Assert
        with pytest.raises(ValueError):
            self._view_manager.load_view(None)
