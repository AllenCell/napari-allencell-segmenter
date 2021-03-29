# TODO: Most if not all of these functions should be converted to classes and moved to "widgets/"

from pathlib import Path

from qtpy.QtCore import Qt
from qtpy.QtGui import QPixmap
from qtpy.QtWidgets import (
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel, 
    QWidget
)

DIR = Path.cwd() / "napari_aicssegmentation"


""" 
Create a warning message with a yellow warning sign icon on the left.

Inputs:
    message:    String
Output:
    A QWidget displaying a warning symbol and a message next to it
"""


def warning_message(message):
    widget = QWidget()
    widget.setLayout(QHBoxLayout())

    icon = QLabel()
    icon.setPixmap(QPixmap(str(DIR / "assets/icons/warning.png")))

    text = QLabel(message)

    widget.layout().addStretch()
    widget.layout().addWidget(icon)
    widget.layout().addWidget(text)
    widget.layout().addStretch()
    return widget


"""
Create a nicely formatted form layout given contents to add as rows.

Inputs:
    rows:       List of dictionaries with this shape:
                    {
                        "label": string | QLabel,
                        "input": QWidget (e.g., QLabel, QComboBox)
                    }
    margins:    Tuple of 4 numbers representing left, top, right, and bottom margins for
                the form's contents. Qt defaults to (11, 11, 11, 11).
Output:
    A QFrame widget with a QFormLayout
"""


def form_layout(rows, margins=(0, 5, 11, 0)):
    widget = QFrame()
    layout = QFormLayout()
    layout.setFormAlignment(Qt.AlignLeft)
    left, top, right, bottom = margins
    layout.setContentsMargins(left, top, right, bottom)

    for row in rows:
        layout.addRow(row["label"], row["input"])
    widget.setLayout(layout)
    return widget
