import napari

from qtpy.QtWidgets import QLayout
from .router import Router
from .view_manager import ViewManager

class Application:
    def __init__(self, viewer: napari.Viewer, root_layout: QLayout):
        if viewer is None:
            raise ValueError("viewer")
        if root_layout is None:
            raise ValueError("root_layout")

        self._viewer = viewer

        # build object tree
        view_manager = ViewManager(root_layout)
        self._router = Router(self, view_manager)

    @property
    def router(self) -> Router: 
        return self._router

    @property
    def viewer(self) -> napari.Viewer:
        return self._viewer
    
    # TODO - Application State

