from pathlib import Path

from qtpy.QtGui import QPixmap
from qtpy.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget
)

from napari_aicssegmentation._style_constants import PAGE_CONTENT_WIDTH

DIR = Path.cwd() / "napari_aicssegmentation"


"""
"""


class CollapsiblePanel(QWidget):
    def __init__(self, step, title, open=True, enabled=True):
        super().__init__()
        self.step = step
        self.title = title

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 11, 0, 11)
        self.setLayout(self.layout)
        self.setFixedWidth(PAGE_CONTENT_WIDTH)
        self.setObjectName(f"collapsiblePanel{step}")

        self.set_title_box_layout()

    def set_title_box_layout(self):
        title_box = QFrame()
        title_box_layout = QHBoxLayout()
        title_box.setLayout(title_box_layout)

        # Need HTML due to this bug: https://bugreports.qt.io/browse/QTBUG-90853
        title = QLabel(f'<span>{self.step}.&nbsp;{self.title}</span>')
        icon = QLabel()
        icon.setPixmap(QPixmap(str(DIR / "assets/icons/gear.svg")))
        title_box_layout.addWidget(title)
        title_box_layout.addStretch()
        title_box_layout.addWidget(icon)

        self.layout.addWidget(title_box)
