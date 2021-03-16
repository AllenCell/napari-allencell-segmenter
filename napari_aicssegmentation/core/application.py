import napari

from qtpy.QtWidgets import QLayout
from napari_aicssegmentation.core.state import State
from .router import Router
from .view_manager import ViewManager
from ._interfaces import IApplication


class Application(IApplication):
    def __init__(self, viewer: napari.Viewer, root_layout: QLayout):
        if viewer is None:
            raise ValueError("viewer")
        if root_layout is None:
            raise ValueError("root_layout")

        self._viewer = viewer

        # build object tree
        self._view_manager = ViewManager(root_layout)
        self._router = Router(self)
        self._state = State()

    @property
    def router(self) -> Router:
        return self._router

    @property
    def viewer(self) -> napari.Viewer:
        return self._viewer

    @property
    def view_manager(self) -> ViewManager:
        return self._view_manager

    @property
    def state(self) -> State:
        return self._state
