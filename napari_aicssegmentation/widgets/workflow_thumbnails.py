from qtpy.QtGui import QPixmap
from qtpy.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

class WorkflowThumbnails(QWidget):

    """
    A widget containing thumbnail images for workflows.

    Params:
    """

    def __init__(self):
        super().__init__()
        self.buttons = list()

        layout = QVBoxLayout()
        self.enabled = False
        self.setLayout(layout)
        # layout.setContentsMargins(0, 5, 0, 3)
        # layout.setSpacing(0)  # No space between title_box and content_box
        # self.setLayout(layout)

        # self.title_box = self._create_title_box()
        # self.content_box = self._create_content_box()

        # layout.addWidget(self.title_box)
        # layout.addWidget(self.content_box)

    def add_buttons(self, button):
        self.buttons.append(button)
        self.layout.addWidget(button)

    def enable_buttons(self):
        if not self.enabled:
            for button in self.buttons:
                button.setEnabled = True
            self.enabled = True

    def disable_buttons(self):
        if self.enabled:
            for button in self.buttons:
                button.setEnabled = False
            self.enabled = False

    def get_widget(self):
        return self.layout


