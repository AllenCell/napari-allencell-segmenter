from PyQt5.QtWidgets import QVBoxLayout, QWidget, QLineEdit, QPushButton
from PyQt5.QtGui import QIntValidator
from napari_aicssegmentation.core.view import View
from napari_aicssegmentation.controller._interfaces import IBatchProcessingController
from napari_aicssegmentation.widgets.form import Form, FormRow
from napari_aicssegmentation.widgets.file_input import FileInput, FileInputMode
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

        row1 = FormRow(
            "1.  Load workflow:",
            FileInput(
                mode=FileInputMode.FILE, filter="Json file (*.json)", initial_text="Load a JSON workflow file..."
            ),
        )
        channel_input = QLineEdit("0")
        channel_input.setValidator(QIntValidator(bottom=0))
        row2 = FormRow("2.  Structure channel index:", channel_input)
        row3 = FormRow(
            "3.  Input directory:", FileInput(mode=FileInputMode.DIRECTORY, initial_text="Select a directory...")
        )
        row4 = FormRow(
            "4.  Output directory:", FileInput(mode=FileInputMode.DIRECTORY, initial_text="Select a directory...")
        )

        # TODO figure out how to merge cells to display help line (use GridLayout instead of FormLayout?)
        form = QWidget()
        form.setLayout(Form([row1, row2, row3, row4]))
        layout.addWidget(form)

        self.submit_button = QPushButton("Run Batch")
        self.submit_button.clicked.connect(self.run_batch)
        self.submit_button.setEnabled(False)
        layout.addWidget(self.submit_button)


    def update_button(self, enabled: bool):
        """
       Update state of process button
       Inputs:
           enabled: True to enable the button, false to disable it
       """
        self.submit_button.setEnabled(bool)


    #####################################################################
    # Event handlers
    #####################################################################
    def run_batch(self):
        print("clicked")

    def input_folder_selected(self, input_folder):
        self._controller.select_input_folder()
