from qtpy.QtWidgets import QWidget, QHBoxLayout, QLabel
from qtpy.QtGui import QPixmap
from napari_allencell_segmenter.util.directories import Directories


class WarningMessage(QWidget):
    """
    Warning message Widget with a yellow warning sign icon on the left.
    """

    def __init__(self, message: str, parent: QWidget = None):
        super().__init__(parent=parent)

        self.setLayout(QHBoxLayout())

        icon = QLabel()
        icon.setPixmap(QPixmap(str(Directories.get_assets_dir() / "icons" / "warning.png")))

        self._text = QLabel(message)

        self.layout().addStretch()
        self.layout().addWidget(icon)
        self.layout().addWidget(self._text)
        self.layout().addStretch()

    @property
    def message(self):
        return self.getMessage()

    def setMessage(self, message: str):
        self._text.setText(message)

    def getMessage(self):
        return self._text.text()
