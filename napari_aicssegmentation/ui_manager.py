from napari import Viewer
from qtpy.QtWidgets import QBoxLayout, QMessageBox

class UIManager:
    def __init__(self, viewer: Viewer, base_layout: QBoxLayout):
        if viewer is None:
            raise ValueError("viewer")
        if base_layout is None:
            raise ValueError("base_layout")
        self._viewer = viewer
        self._base_layout = base_layout

    @property
    def viewer(self):
        return self._viewer

    @property
    def base_layout(self) -> QBoxLayout:
        return self._base_layout
        
    def show_message_box(self, title: str, message: str):
        """Show a message box with the specified title and message"""
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(message)
        return msg.exec()

    def is_image_loaded(self) -> bool:
        """Determines if there is already an image loaded onto napari"""
        return len(self.viewer.layers) > 0
            