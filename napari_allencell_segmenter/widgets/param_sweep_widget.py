import qtpy
from qtpy.QtWidgets import (
    QDialog,
    QLineEdit,
    QVBoxLayout,
    QFrame,
    QHBoxLayout,
    QPushButton,
    QCheckBox,
    QSizePolicy,
    QLabel,
    QMessageBox,
)
from qtpy.QtCore import Qt

from typing import Dict, Any, List
from napari_allencell_segmenter.widgets.form import Form, FormRow


class ParamSweepWidget(QDialog):
    """
    A dialog box containing a workflow finished message. Also includes a button to open the output folder
    and a button to close the dialog box

    Params:
        output_folder (Path):       The output folder to open when the corresponding button is clicked by the user.
    """

    def __init__(self, param_set: Dict[str, Any], step_number, controller):
        super().__init__()
        self.live_count = None
        self.inputs = list()
        self.controller = controller
        self.step_number = step_number
        self._param_set = param_set
        rows = self._param_set_to_form_rows()
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self._create_buttons())
        self.setLayout(Form(rows))
        self.setWindowTitle("Parameter Sweep")


    def _param_set_to_form_rows(self) -> List[FormRow]:

        rows = list()

        header = QFrame()
        header.setLayout(QHBoxLayout())
        label = QLabel("min")
        label.setAlignment(Qt.AlignCenter)
        header.layout().addWidget(label)
        label = QLabel("max")
        label.setAlignment(Qt.AlignCenter)
        header.layout().addWidget(label)
        label = QLabel("step size")
        label.setAlignment(Qt.AlignCenter)
        header.layout().addWidget(label)
        rows.append(FormRow("", widget=header))

        default_params = self.controller.model.active_workflow.workflow_definition.steps[self.step_number].function.parameters

        if self._param_set:
            for key, value in self._param_set.items():
                if isinstance(value, list):
                    i = 1
                    for _ in value:
                        sweep_inputs = QFrame()
                        sweep_inputs.setLayout(QHBoxLayout())
                        min_value = default_params[key][i - 1].min_value
                        max_value = default_params[key][i - 1].max_value
                        step_size = (max_value - min_value) / 2

                        min_input = QLineEdit()
                        min_input.setText(str(min_value))
                        min_input.textChanged.connect(self.update_live_count)
                        sweep_inputs.layout().addWidget(min_input)

                        max_input = QLineEdit()
                        max_input.setText(str(max_value))
                        max_input.textChanged.connect(self.update_live_count)
                        sweep_inputs.layout().addWidget(max_input)

                        step_input = QLineEdit()
                        step_input.setText(str(step_size))
                        step_input.textChanged.connect(self.update_live_count)
                        sweep_inputs.layout().addWidget(step_input)
                        self.inputs.append(sweep_inputs)
                        rows.append(FormRow(label=f"{key} {i}", widget=sweep_inputs))
                        i = i + 1
                else:
                    sweep_inputs = QFrame()
                    sweep_inputs.setLayout(QHBoxLayout())
                    min_value = default_params[key][i - 1].min_value
                    max_value = default_params[key][i - 1].max_value
                    step_size = (max_value - min_value) / 2

                    min_input = QLineEdit()
                    min_input.setText(str(min_value))
                    min_input.textChanged.connect(self.update_live_count)
                    sweep_inputs.layout().addWidget(min_input)

                    max_input = QLineEdit()
                    max_input.setText(str(max_value))
                    max_input.textChanged.connect(self.update_live_count)
                    sweep_inputs.layout().addWidget(max_input)

                    step_input = QLineEdit()
                    step_input.setText(str(step_size))
                    step_input.textChanged.connect(self.update_live_count)
                    sweep_inputs.layout().addWidget(step_input)
                    self.inputs.append(sweep_inputs)
                    rows.append(FormRow(label=f"{key}", widget=sweep_inputs))

        def_count = self.get_live_count()
        self.live_count = QLabel(f"{def_count} images will be created")
        self.live_count.setAlignment(qtpy.QtCore.Qt.AlignCenter)
        rows.append(FormRow("", widget=self.live_count))
        rows.append(FormRow("", widget=self._create_buttons()))
        return rows

    def _create_buttons(self):
        """
        Creates buttons for the bottom of the dialog box, one for opening the output folder, and one for
            closing the dialog box

        Params:
            None

        Returns:
            (QFrame): A QFrame that has two horizontally laid out buttons, first button is Open output directory,
                second button is close.
        """
        buttons = QFrame()
        buttons.setLayout(QHBoxLayout())
        run_sweep = QPushButton("Start Sweep")
        run_sweep.clicked.connect(self._run_sweep)
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        buttons.layout().addWidget(run_sweep)
        buttons.layout().addWidget(close_button)
        return buttons

    def _run_sweep(self):
        inputs = self.grab_ui_values()
        self.sanitize_ui_inputs(inputs)
        if self.warn_images_created(inputs) == 1024:
            self.controller.run_step_sweep(self.step_number, self._param_set, inputs, "grid")


    def sanitize_ui_inputs(self, ui_inputs: List[List[str]]):

        len_of_list = None
        for i in ui_inputs:
            # make sure user has inputted a number or min:step:max notation
            for j in i:
                try:
                    # is the notation done with just numbers?
                    float(j)
                except ValueError:
                    raise ValueError("Please enter a single number or the min:step:max notation for sweeps")

    def warn_images_created(self, ui_input):
        length = 1
        for sweeps in ui_input:
            length = length * self.get_sweep_len(float(sweeps[0]), float(sweeps[1]), float(sweeps[2]))
        message = QMessageBox()
        message.setText(f"{int(length)} result image layers will be created.")
        message.setWindowTitle("Running Sweep")
        message.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        return message.exec_()

    def update_live_count(self):
        if self.live_count:
            count = self.get_live_count()
            self.live_count.setText(f"{count } images will be created")

    def get_live_count(self):
        inputs = self.grab_ui_values()
        self.sanitize_ui_inputs(inputs)
        length = 1
        for sweeps in inputs:
            length = length * self.get_sweep_len(float(sweeps[0]), float(sweeps[1]), float(sweeps[2]))
        return length

    def get_sweep_len(self, min, step, max):
        return ((max - min) / step) + 1

    def grab_ui_values(self):
        inputs = list()
        for widget in self.inputs:
            # ui is min, max, step
            # transform into min, step, max
            inputs.append([widget.children()[1].text(), widget.children()[3].text(), widget.children()[2].text()])
        return inputs

