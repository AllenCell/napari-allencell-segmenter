from qtpy.QtGui import QPixmap
from qtpy.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QDialog, QPushButton
from PyQt5.QtCore import Qt
from pathlib import Path

from napari_aicssegmentation.util.directories import Directories
from os import startfile

class BatchCompleteDialog(QDialog):
    def __init__(self, output_folder: Path):
        super().__init__()

        self.output_folder = output_folder

        # Create header
        header = self.create_header()

        # Create frame with messages
        messages = self.create_messages()

        # Create buttons at bottom of dialog
        buttons = self.create_buttons()

        # Add everything to dialog box, and format
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(header)
        self.layout.addWidget(messages)
        self.layout.addWidget(buttons)
        self.setLayout(self.layout)

    def create_header(self):
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
        header.setStyleSheet("background-color:white;")
        header.setMargin(15)
        return header

    def create_messages(self):
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

    def create_buttons(self):
        buttons = QFrame()
        buttons.setLayout(QHBoxLayout())
        open_output_button = QPushButton("Open output directory")
        open_output_button.clicked.connect(self.open_output_folder)
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        buttons.layout().addWidget(open_output_button)
        buttons.layout().addWidget(close_button)
        return buttons

    def open_output_folder(self):
        # TODO: is there a pathlib way to do this?
        startfile(self.output_folder)


