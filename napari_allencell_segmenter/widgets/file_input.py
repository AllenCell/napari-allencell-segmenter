from enum import Enum
from qtpy.QtWidgets import QHBoxLayout, QWidget, QLineEdit, QFileDialog
from qtpy.QtCore import Signal


class FileInputMode(Enum):
    DIRECTORY = "dir"
    FILE = "file"


class FileInput(QWidget):
    """
    A file input Widget that includes a file dialog for selecting a file / directory
    and a text box to display the selected file

    inputs:
        mode (FileInputMode): set file dialog selection type to File or Directory
        filter (str): standard QFileDialog file filter. Ex: "JSON Files (*.json)"
        initial_text (str): text to display in the widget before a file has been selected
    """

    file_selected = Signal(str)
    _selected_file: str = None

    def __init__(
        self,
        parent: QWidget = None,
        mode: FileInputMode = FileInputMode.FILE,
        filter: str = None,
        placeholder_text: str = None,
    ):
        super().__init__(parent)
        self._mode = mode
        self._filter = filter

        self._input_box = QLineEdit()
        self._input_box.setPlaceholderText(placeholder_text)
        self._input_box.setEnabled(False)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._input_box)
        self.setLayout(layout)

    @property
    def mode(self) -> FileInputMode:
        return self._mode

    @property
    def filter(self) -> str:
        return self._filter

    @property
    def selected_file(self) -> str:
        return self._selected_file

    def _select_file(self):  # pragma: no-cover
        if self._mode == FileInputMode.FILE:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Select a file",
                filter=self._filter,
                options=QFileDialog.Option.DontUseNativeDialog | QFileDialog.Option.DontUseCustomDirectoryIcons,
            )
        else:
            file_path = QFileDialog.getExistingDirectory(
                self,
                "Select a directory",
                options=QFileDialog.Option.DontUseNativeDialog | QFileDialog.Option.DontUseCustomDirectoryIcons,
            )

        if file_path:
            self._selected_file = file_path
            self._input_box.setText(file_path)
            self.file_selected.emit(file_path)

    def mousePressEvent(self, event):
        if self._input_box.underMouse():
            self._select_file()
