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
    def __init__(self, step, title, children, isOpen=True, isEnabled=True):
        super().__init__()
        self.step = step
        self.title = title
        self.children = children
        self.isOpen = isOpen
        self.isEnabled = isEnabled

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 11, 0, 11)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)
        self.setFixedWidth(PAGE_CONTENT_WIDTH)
        self.setObjectName(f"collapsiblePanel{step}")

        self.set_title_box_layout()
        self.set_content_box_layout()

    def set_title_box_layout(self):
        title_box = QFrame()
        title_box_layout = QHBoxLayout()
        title_box_layout.setContentsMargins(9, 9, 9, 9)
        title_box.setLayout(title_box_layout)
        title_box.setFixedHeight(40)
        if self.isEnabled is False:
            self.isOpen = False
            title_box.setDisabled(True)
            title_box.setObjectName("collapsiblePanelDisabled")

        # Need HTML due to this bug: https://bugreports.qt.io/browse/QTBUG-90853
        title = QLabel(f'<span>{self.step}.&nbsp;{self.title}</span>')
        icon = QLabel()
        icon.setPixmap(QPixmap(str(DIR / "assets/icons/gear.svg")))
        title_box_layout.addWidget(title)
        title_box_layout.addStretch()
        title_box_layout.addWidget(icon)

        self.layout.addWidget(title_box)

    def set_content_box_layout(self):
        content_box = QFrame()
        content_box_layout = QVBoxLayout()
        content_box_layout.setContentsMargins(9, 9, 9, 9)
        content_box.setLayout(content_box_layout)
        content_box.setObjectName("contentBox")

        for child_widget in self.children:
            content_box_layout.addWidget(child_widget)
        
        self.layout.addWidget(content_box)

        if self.isOpen is False:
            content_box.hide()
