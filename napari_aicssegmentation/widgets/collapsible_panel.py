from qtpy.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget
)


"""
"""


class CollapsiblePanel(QWidget):
    def __init__(id, title, open=True, enabled=True):
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setObjectName(f"collapsiblePanel{id}")
