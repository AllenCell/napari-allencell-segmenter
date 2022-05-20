import sys
import subprocess

from qtpy.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QDialog, QPushButton
from qtpy.QtCore import Qt
from pathlib import Path


class BatchCompleteDialog(QDialog):
    """
    A dialog box containing a workflow finished message. Also includes a button to open the output folder
    and a button to close the dialog box

    Params:
        output_folder (Path):       The output folder to open when the corresponding button is clicked by the user.
    """

    def __init__(self, output_folder: Path):
        super().__init__()

        self._output_folder = output_folder

        # Create header
        header = self._create_header()

        # Create frame with messages
        messages = self._create_messages()

        # Create buttons at bottom of dialog
        buttons = self._create_buttons()

        # Add everything to dialog box, and format
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(header)
        self.layout.addWidget(messages)
        self.layout.addWidget(buttons)
        self.setLayout(self.layout)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)

        self._show_file_func = {
            "darwin": self._show_file_darwin,
            "linux": self._show_file_linux,
            "win32": self._show_file_windows,
        }

    def _create_header(self):
        """
        Creates a header with the Allen Cell Structure Segmenter title and warning message.

        Params:
            None

        Returns:
            (QLabel): A Qlabel with header + warning message inside.
        """
        # Create header
        header = QLabel(
            """
            <span>
                <b>ALLEN CELL & STRUCTURE SEGMENTER</b><br/>
                v1.0 supports static 3D images only
            </span>
            """
        )
        header.setObjectName("header")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # header.setStyleSheet("background-color:white;")
        header.setMargin(15)
        return header

    def _create_messages(self):
        """
        Creates messages to go within the dialog box

        Params:
            None

        Returns:
            (QFrame): A QFrame that has the "Batch processing is completed" message and a info message (QLabel)
        """
        # Create frame with messages
        frame = QFrame()
        frame.setLayout(QVBoxLayout())
        message = QLabel()
        message.setText("Batch Processing is completed!")
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc = QLabel()
        desc.setText("Please refer to the log.txt file in the output directory for more details.")
        frame.layout().setContentsMargins(15, 0, 15, 0)
        frame.layout().addWidget(message)
        frame.layout().addWidget(desc)
        return frame

    def _create_buttons(self):
        """
        Creates buttons for the bottom of the dialog box, one for opening the output folder, and one for
            closing the dialog box

        Params:
            None

        Returns:
            (QFrame): A QFrame that has two horizontally laid out buttons, first button is Open output directory,
                second button is close.
        """
        buttons = QFrame()
        buttons.setLayout(QHBoxLayout())
        open_output_button = QPushButton("Open output directory")
        open_output_button.clicked.connect(self._open_output_folder)
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        buttons.layout().addWidget(open_output_button)
        buttons.layout().addWidget(close_button)
        return buttons

    def _show_file_darwin(self):
        subprocess.Popen(["open", self._output_folder])

    def _show_file_linux(self):
        subprocess.Popen(["xdg-open", self._output_folder])

    def _show_file_windows(self):
        from os import startfile

        startfile(self._output_folder)

    def _open_output_folder(self):
        """
        Opens the output folder on the file explorer

        Params:
            None

        Returns:
            None
        """

        try:
            self._show_file_func[sys.platform]()
        except KeyError:
            raise OSError(f"Your platform: {sys.platform} is not supported by our app.")
