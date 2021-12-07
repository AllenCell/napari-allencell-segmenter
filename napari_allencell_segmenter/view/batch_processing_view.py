from qtpy.QtWidgets import QProgressBar, QVBoxLayout, QWidget, QLineEdit, QPushButton, QLabel
from qtpy.QtGui import QIntValidator
from napari_allencell_segmenter.core.view import View
from napari_allencell_segmenter.controller._interfaces import IBatchProcessingController
from napari_allencell_segmenter.widgets.form import Form, FormRow
from napari_allencell_segmenter.widgets.file_input import FileInput, FileInputMode
from ._main_template import MainTemplate


class BatchProcessingView(View):
    btn_run_batch: QPushButton
    progress_bar: QProgressBar
    field_channel: QLineEdit
    field_workflow_config: FileInput
    field_input_dir: FileInput
    field_output_dir: FileInput

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

        # Workflow config
        self.field_workflow_config = FileInput(
            mode=FileInputMode.FILE, filter="Json file (*.json)", placeholder_text="Load a JSON workflow file..."
        )
        self.field_workflow_config.file_selected.connect(self._form_field_changed)
        row1 = FormRow("1.  Load workflow:", self.field_workflow_config)

        # Channel index
        self.field_channel = QLineEdit("0")
        self.field_channel.setValidator(QIntValidator(bottom=0))
        self.field_channel.textChanged.connect(self._form_field_changed)
        row2 = FormRow("2.  Structure channel index:", self.field_channel)

        # Input dir
        self.field_input_dir = FileInput(mode=FileInputMode.DIRECTORY, placeholder_text="Select a directory...")
        self.field_input_dir.file_selected.connect(self._form_field_changed)
        row3 = FormRow("3.  Input directory:", self.field_input_dir)

        # Output dir
        self.field_output_dir = FileInput(mode=FileInputMode.DIRECTORY, placeholder_text="Select a directory...")
        self.field_output_dir.file_selected.connect(self._form_field_changed)
        row4 = FormRow("4.  Output directory:", self.field_output_dir)

        # Help
        label = QLabel()
        label.setText("Supported file formats: .tif, .tiff, .czi, .ome.tif, .ome.tiff")

        form = QWidget()
        form.setLayout(Form([row1, row2, row3, row4]))
        layout.addWidget(form)
        layout.addWidget(label)

        # Submit
        self.btn_run_batch = QPushButton("Run Batch")
        self.btn_run_batch.clicked.connect(self._btn_run_batch_clicked)
        self.update_button(enabled=False)
        layout.addWidget(self.btn_run_batch)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

    def update_button(self, enabled: bool):
        """
        Update state of process button
        Inputs:
            enabled: True to enable the button, false to disable it
        """
        self.btn_run_batch.setEnabled(enabled)

    def set_run_batch_in_progress(self):
        """
        Update page to reflect that a batch run is in progress
        """
        # TODO make a CancelButton widget to avoid repeating this connect / disconnect pattern
        self.btn_run_batch.setText("Cancel")
        self.btn_run_batch.clicked.disconnect()
        self.btn_run_batch.clicked.connect(self._btn_run_batch_cancel_clicked)
        self.progress_bar.setVisible(True)

    def reset_run_batch(self):
        """
        Reset page state to reflect that there is no batch run in progress
        """
        self.progress_bar.setValue(0)
        self.btn_run_batch.setText("Run Batch")
        self.btn_run_batch.clicked.disconnect()
        self.btn_run_batch.clicked.connect(self._btn_run_batch_clicked)
        self.progress_bar.setVisible(False)

    def set_progress(self, progress: int):
        """
        Update progress bar

        Inputs:
            progress (int): numerical value to set the progress bar to
        """
        self.progress_bar.setValue(progress)

    #####################################################################
    # Event handlers
    #####################################################################
    def _btn_run_batch_clicked(self):
        self._controller.run_batch()

    def _btn_run_batch_cancel_clicked(self):
        self.btn_run_batch.setText("Canceling...")
        self._controller.cancel_run_batch()

    def _form_field_changed(self, value):
        workflow_config = self.field_workflow_config.selected_file
        channel_index = int(self.field_channel.text()) if self.field_channel.text() else None
        input_dir = self.field_input_dir.selected_file
        output_dir = self.field_output_dir.selected_file

        self._controller.update_batch_parameters(workflow_config, channel_index, input_dir, output_dir)
