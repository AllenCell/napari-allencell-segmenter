from PyQt5.QtWidgets import QVBoxLayout, QWidget, QLineEdit, QPushButton
from PyQt5.QtGui import QIntValidator
from napari_aicssegmentation.core.view import View
from napari_aicssegmentation.controller._interfaces import IBatchProcessingController
from napari_aicssegmentation.widgets.form import Form, FormRow
from napari_aicssegmentation.widgets.file_input import FileInput, FileInputMode
from ._main_template import MainTemplate
from napari_aicssegmentation.widgets.batch_complete_dialog import BatchCompleteDialog
from pathlib import Path


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
        """
        Set up the UI for the BatchProcessingView
        """
        layout = QVBoxLayout()
        self.setLayout(layout)

        row1 = FormRow(
            "1.  Load workflow:",
            FileInput(
                mode=FileInputMode.FILE, filter="Json file (*.json)", initial_text="Load a JSON workflow file..."
            ),
        )
        row1.widget.file_selected.connect(self.workflow_selected)
        channel_input = QLineEdit("0")
        channel_input.setValidator(QIntValidator(bottom=0))
        row2 = FormRow("2.  Structure channel index:", channel_input)
        row3 = FormRow(
            "3.  Input directory:", FileInput(mode=FileInputMode.DIRECTORY, initial_text="Select a directory...")
        )
        row3.widget.file_selected.connect(self.input_folder_selected)
        row4 = FormRow(
            "4.  Output directory:", FileInput(mode=FileInputMode.DIRECTORY, initial_text="Select a directory...")
        )
        row4.widget.file_selected.connect(self.output_folder_selected)

        # TODO figure out how to merge cells to display help line (use GridLayout instead of FormLayout?)
        form = QWidget()
        form.setLayout(Form([row1, row2, row3, row4]))
        layout.addWidget(form)

        self.submit_button = QPushButton("Run Batch")
        self.submit_button.clicked.connect(self.run_batch)
        self.update_button(enabled=False)
        layout.addWidget(self.submit_button)

    def update_button(self, enabled: bool):
        """
        Update state of process button
        Inputs:
            enabled: True to enable the button, false to disable it
        """
        self.submit_button.setEnabled(enabled)
        if not enabled:
            self.submit_button.setStyleSheet("QPushButton:disabled" "{ color: gray }")

    def open_completion_dialog(self, output_folder: Path):
        """
        Open the batch processing completion dialog box
        Inputs:
            output_folder (Path): output folder to open when prompted by user
        """
        dlg = BatchCompleteDialog(output_folder)
        dlg.exec()

    #####################################################################
    # Event handlers
    #####################################################################
    def run_batch(self):
        """
        Run the batch workflow
        """
        self._controller.run_batch()

    def workflow_selected(self, selected_config):
        """
        Event handler when workflow config file is selected
        """
        self._controller.select_config(selected_config)

    def input_folder_selected(self, input_folder):
        """
        Event handler when input folder is selected
        """
        self._controller.select_input_folder(input_folder)

    def output_folder_selected(self, output_folder):
        """
        Event handler when output folder is selected
        """
        self._controller.select_output_folder(output_folder)
