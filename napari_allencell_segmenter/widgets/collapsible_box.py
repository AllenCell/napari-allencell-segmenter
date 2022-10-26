from qtpy.QtGui import QPixmap, QIcon
from qtpy.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget, QPushButton

from napari_allencell_segmenter.util.directories import Directories


class CollapsibleBox(QWidget):
    """
    A collapsible box widget containing a title box and a content box. The title box can be clicked
    to toggle the visibility of the content box.

    Params:
        title (string):             To be displayed at the top of the box (only thing visible when
                                    collapsed)
        content_layout (QLayout):   QLayout to be nested inside the content box
        isOpen (bool):              Whether the widget is open or collapsed by default
    """

    def __init__(self, title, content_layout, step_widget, isOpen=False):
        super().__init__()
        self._title = title
        # TODO: Refactor to avoid requiring a content_layout argument at object creation:
        # https://github.com/AllenCell/napari-allencell-segmenter/pull/56#discussion_r615056471
        self._content_layout = content_layout
        self.isOpen = isOpen

        self.title_box = self._create_title_box(step_widget)
        self.content_box = self._create_content_box()

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 5, 0, 3)
        layout.setSpacing(0)  # No space between title_box and content_box
        self.setLayout(layout)

        layout.addWidget(self.title_box)
        layout.addWidget(self.content_box)

    def _create_title_box(self, step_widget):
        title_box = QFrame()
        title_box_layout = QHBoxLayout()
        title_box_layout.setContentsMargins(11, 9, 9, 9)
        title_box.setLayout(title_box_layout)
        title_box.setFixedHeight(38)
        if self.isOpen is False:
            title_box.setObjectName("titleBoxClosed")

        title = QLabel(self._title)

        sweep_button = QPushButton()
        sweep_button.setIcon(QIcon(QPixmap(str(Directories.get_assets_dir() / "icons/icon-parameter-sweep.svg"))))
        sweep_button.setToolTip("Open parameter sweep window")
        sweep_button.setObjectName("infoButton")
        sweep_button.clicked.connect(lambda: step_widget.steps_view.open_sweep_ui(step_widget.index))
        if step_widget.step.function.parameters is None:
            sweep_button.setEnabled(False)
        self.expand_button = QPushButton()
        self.expand_button.setIcon(
            QIcon(QPixmap(str(Directories.get_assets_dir() / "icons/expand_more_black_24dp.svg")))
        )
        self.expand_button.setToolTip("Expand to see parameters")
        self.expand_button.clicked.connect(self.toggle)

        # icon = QLabel()
        # icon.setPixmap(QPixmap(str(Directories.get_assets_dir() / "icons/expand_more_black_24dp.svg")))
        title_box_layout.addWidget(title)
        title_box_layout.addStretch()
        title_box_layout.addWidget(sweep_button)
        title_box_layout.addWidget(self.expand_button)
        # icon = QLabel()
        # icon.setPixmap(QPixmap(str(Directories.get_assets_dir() / "icons/warning.png")))
        #
        # title_box_layout.addWidget(icon)

        return title_box

    def _create_content_box(self):
        content_box = QFrame()
        content_box_layout = QVBoxLayout()
        content_box_layout.setContentsMargins(9, 9, 9, 9)
        content_box_layout.addLayout(self._content_layout)
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
            self.expand_button.setIcon(
                QIcon(QPixmap(str(Directories.get_assets_dir() / "icons/expand_less_black_24dp.svg")))
            )

    def close(self):
        if self.isOpen:
            self.isOpen = False
            self.content_box.hide()
            self.title_box.setObjectName("titleBoxClosed")
            self.title_box.setStyle(self.title_box.style())
            self.expand_button.setIcon(
                QIcon(QPixmap(str(Directories.get_assets_dir() / "icons/expand_more_black_24dp.svg")))
            )

    def toggle(self):
        if self.isOpen:
            self.close()
        else:
            self.open()

    # Overwrite default QWidget.mousePressEvent() method
    # def mousePressEvent(self, event):
    #     if self.title_box.underMouse():
    #         self.toggle()
