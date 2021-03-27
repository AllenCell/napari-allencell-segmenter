from napari_aicssegmentation.util.debug_utils import debug_class
from napari_aicssegmentation.core.view import View
from qtpy.QtWidgets import QLayout

@debug_class
class ViewManager:
    def __init__(self, base_layout: QLayout):
        if base_layout is None:
            raise ValueError("base_layout")
        self._base_layout = base_layout
        self._current_view: View = None

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

        # TODO refactor (loop)
        if view.has_template():
            tpl = view.template                        
            tpl.setup_ui()
            tpl.get_container().layout().addWidget(view)
            view.setup_ui()
            self._base_layout.addWidget(tpl)
            self._current_view = tpl
        else:
            self._base_layout.addWidget(view)
            view.setup_ui()
            self._current_view = view

    def _unload_view(self):
        if self._current_view is not None:            
            self._current_view.setParent(None)
            self._current_view.deleteLater()                      
            self._current_view = None
