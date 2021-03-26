from napari_aicssegmentation.util.debug_utils import debug_class
from napari_aicssegmentation.core.view import View
from qtpy.QtWidgets import QLayout
from PyQt5 import sip

@debug_class
class ViewManager:
    def __init__(self, base_layout: QLayout):
        if base_layout is None:
            raise ValueError("base_layout")
        self._base_layout = base_layout
        self._current_view: View = None

    # def _delete_items_from_layout(self, layout: QLayout):
    #     if layout is not None:
    #         while layout.count():
    #             item = layout.takeAt(0)
    #             widget = item.widget()
    #             if widget is not None:
    #                 widget.setParent(None)
    #             else:
    #                 self._delete_items_from_layout(item.layout())

    @property
    def current_view(self) -> View:
        return self._current_view

    def load_view(self, view: View):
        """
        Loads the given view
        The currently active view will be removed and garbage collected
        and the given View will become the new active view
        :param: view: View to load
        """
        if view is None:
            raise ValueError("View can't be None")

        if self._current_view is not None:
            self._unload_view()

        self._base_layout.addWidget(view)
        view.setup_ui()
        self._current_view = view

    def _unload_view(self):
        if self._current_view is not None:            
            self._current_view.setParent(None)
            self._current_view.deleteLater()                      
            self._currentView = None
