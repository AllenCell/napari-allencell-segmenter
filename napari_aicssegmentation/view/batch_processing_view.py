from PyQt5.QtWidgets import QVBoxLayout, QLineEdit, QWidget
from napari_aicssegmentation.core.view import View
from napari_aicssegmentation.controller._interfaces import IBatchProcessingController
from napari_aicssegmentation.widgets.form import Form, FormRow
from ._main_template import MainTemplate


class BatchProcessingView(View):
    def __init__(self, controller: IBatchProcessingController):
        super().__init__(template_class=MainTemplate)

        if controller is None:
            raise ValueError("controller")
        self._controller = controller
        self.setObjectName("batchProcessingView")

    def load(self, model=None):
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        row1 = FormRow("1. Select file", QLineEdit()) # TODO use or create a filepicker instead of QLineEdit
        row2 = FormRow("2. Channel index", QLineEdit())
        # TODO figure out how to merge cells to display help line (use GridLayout instead of FormLayout?)
        form = QWidget()
        form.setLayout(Form([row1, row2]))
        layout.addWidget(form)
        