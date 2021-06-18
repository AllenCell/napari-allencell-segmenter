from typing import Any
from napari_allencell_segmenter.core.view import View
from qtpy.QtWidgets import QLayout


class ViewManager:
    def __init__(self, base_layout: QLayout):
        if base_layout is None:
            raise ValueError("base_layout")
        self._base_layout = base_layout
        self._current_view: View = None

    @property
    def current_view(self) -> View:
        return self._current_view

    def load_view(self, view: View, model: Any = None):
        """
        Loads the given view
        The currently active view will be removed and garbage collected
        and the given View will become the new active view

        inputs
            view (View): View to load
            model: optional Model to pass to the view at load time
        """
        if view is None:
            raise ValueError("View can't be None")

        if self._current_view is not None:
            self._unload_view()

        _view = view
        _view.load(model)
        i = 0
        while _view.has_template():
            if i > 10:  # protect against infinite loops just in case
                raise OverflowError("Detected more than 10 nested templates")
            tpl = _view.template
            tpl.load()
            tpl.get_container().layout().addWidget(_view)
            _view = tpl
            i += 1

        self._base_layout.addWidget(_view)
        self._current_view = _view

    def _unload_view(self):
        if self._current_view is not None:
            self._current_view.setParent(None)
            self._current_view.deleteLater()
            self._current_view = None
