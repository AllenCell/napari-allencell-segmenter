from pathlib import Path

from qtpy.QtGui import QPixmap
from qtpy.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

DIR = Path.cwd() / "napari_aicssegmentation"


"""
A collapsible box widget containing a title box and a content box. The title box can be clicked
to toggle the visibility of the content box.

Params:
    title:      String
    content:    QLayout to be nested inside the content box
    isOpen:     Boolean, whether the widget is open or collapsed
"""


class CollapsibleBox(QWidget):
    def __init__(self, title, content, isOpen=True):
        super().__init__()
        self.title = title
        self.content = content
        self.isOpen = isOpen

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 11, 0, 11)
        self.layout.setSpacing(0)  # No space between title_box and content_box
        self.setLayout(self.layout)

        self.title_box = self._create_title_box()
        self.content_box = self._create_content_box()

        self.layout.addWidget(self.title_box)
        self.layout.addWidget(self.content_box)

    def _create_title_box(self):
        title_box = QFrame()
        title_box_layout = QHBoxLayout()
        title_box_layout.setContentsMargins(9, 9, 9, 9)
        title_box.setLayout(title_box_layout)
        title_box.setFixedHeight(40)
        if self.isOpen is False:
            title_box.setObjectName("titleBoxClosed")

        title = QLabel(self.title)
        icon = QLabel()
        icon.setPixmap(QPixmap(str(DIR / "assets/icons/gear.svg")))
        title_box_layout.addWidget(title)
        title_box_layout.addStretch()
        title_box_layout.addWidget(icon)

        return title_box

    def _create_content_box(self):
        content_box = QFrame()
        content_box_layout = QVBoxLayout()
        content_box_layout.setContentsMargins(9, 9, 9, 9)
        content_box_layout.addLayout(self.content)
        content_box.setLayout(content_box_layout)
        content_box.setObjectName("contentBox")

        if self.isOpen is False:
            content_box.hide()
        return content_box

    def open(self):
        if self.isOpen is False:
            self.isOpen = True
            self.content_box.show()
            self.title_box.setObjectName("")
            self.title_box.setStyle(self.title_box.style())

    def close(self):
        if self.isOpen:
            self.isOpen = False
            self.content_box.hide()
            self.title_box.setObjectName("titleBoxClosed")
            self.title_box.setStyle(self.title_box.style())

    def toggle(self):
        if self.isOpen:
            self.close()
        else:
            self.open()

    # Overwrite default QWidget.mousePressEvent() method
    def mousePressEvent(self, event):
        if self.title_box.underMouse():
            self.toggle()
