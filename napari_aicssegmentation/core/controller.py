from abc import ABC, abstractmethod
from napari_aicssegmentation.util.debug_utils import debug_class
from napari.layers import Layer
from napari.components.layerlist import LayerList
from qtpy.QtWidgets import QMessageBox
from napari_aicssegmentation.core._interfaces import IApplication, IRouter

@debug_class
class Controller(ABC):
    _application: IApplication

    def __init__(self, application: IApplication):
        if application is None:
            raise ValueError("application")
        self._application = application
    
    @property
    def router(self) -> IRouter:
        return self._application.router

    def add_layer(self, image_data, name: str):
        self._application.viewer.add_image(image_data, name=name)

    def get_layers(self) -> LayerList:
        return self._application.viewer.layers

    def get_active_layer(self) -> Layer:
        index = self._application.viewer.active_layer
        self.get_layers()[index]

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
