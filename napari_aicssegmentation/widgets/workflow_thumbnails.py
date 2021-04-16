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


    def add_buttons(self, button):
        self.layout().addWidget(button)

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
        return self.layout()


