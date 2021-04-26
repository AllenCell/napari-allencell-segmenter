from typing import Any
import napari

from abc import ABC, abstractmethod
from napari_aicssegmentation.core.state import State
from napari_aicssegmentation.core.view import View
from napari_aicssegmentation.util.debug_utils import debug_class
from napari.layers import Layer
from napari.components.layerlist import LayerList
from qtpy.QtWidgets import QMessageBox
from napari_aicssegmentation.core._interfaces import IApplication, IRouter


@debug_class
class Controller(ABC):
    def __init__(self, application: IApplication):
        if application is None:
            raise ValueError("application")
        self._application = application

    @abstractmethod
    def index(self):
        pass

    def cleanup(self):
        """
        Perform cleanup operations such as disconnecting events
        Override in child class if needed
        """
        pass

    @property
    def state(self) -> State:
        """
        Get the application State object
        """
        return self._application.state

    @property
    def router(self) -> IRouter:
        """
        Get the application Router
        """
        return self._application.router

    @property
    def viewer(self) -> napari.Viewer:
        """
        Get the Napari viewer
        """
        return self._application.viewer

    def load_view(self, view: View, model: Any = None):
        """
        Loads the given view
        :param: view: the View to load
        """
        return self._application.view_manager.load_view(view, model)

    def add_layer(self, image_data, name: str):
        """
        Add a new image layer to the Napari viewer
        :param: image_data: image layer pixel data
        :param: name: new layer name
        """
        self._application.viewer.add_image(image_data, name=name)

    def get_layers(self) -> LayerList:
        """
        Get a list of all image layers currently loaded in the Napari viewer
        """
        return self._application.viewer.layers

    def get_active_layer(self) -> Layer:
        """
        Get the layer currently active (selected) in the Napari viewer
        """
        return self._application.viewer.active_layer

    def is_image_loaded(self) -> bool:
        """
        True if there is already an image loaded onto napari, False otherwise
        """
        return len(self.get_layers()) > 0

    def show_message_box(self, title: str, message: str):
        """
        Display a pop up message box
        :param: title: Message box title
        :param: message: message body to display
        """
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(message)
        return msg.exec()
