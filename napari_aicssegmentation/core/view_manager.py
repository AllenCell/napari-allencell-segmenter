from napari_aicssegmentation.util.debug_utils import debug_class
from napari_aicssegmentation.core.base_view import View
from qtpy.QtWidgets import QLayout, QBoxLayout

@debug_class
class ViewManager:
    
    def __init__(self, base_layout: QBoxLayout):
        if base_layout == None:
            raise ValueError("base_layout")
        self._base_layout = base_layout
        self._current_view: View = None

    @property
    def current_view(self) -> View:
        return self._current_view

    def load_view(self, view: View):
        if view is None:
            raise ValueError("View can't be None")

        view_layout = view.get_layout()

        if view_layout is None or not isinstance(view_layout, QLayout):
            raise ValueError("Cannot load view: invalid or empty layout. \
                              Views must provide a valid QLayout through the View.get_layout method.")

        if self._current_view is not None:
            self.unload_view(self._current_view)
        
        self._base_layout.addLayout(view_layout)
        view.setup_ui()
        self._current_view = view

    def unload_view(self):
        if self._current_view is not None:            
            view_layout = self._current_view.get_layout()      
            self._deleteItemsOfLayout(view_layout)
            self._base_layout.removeItem(view_layout)
            self._currentView = None
        
        
    def _deleteItemsOfLayout(self, layout: QLayout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.setParent(None)
                else:
                    self._deleteItemsOfLayout(item.layout())           