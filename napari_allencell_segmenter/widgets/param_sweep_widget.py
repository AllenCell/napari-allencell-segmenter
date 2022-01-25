from qtpy.QtWidgets import QDialog, QLineEdit, QVBoxLayout, QFrame, QHBoxLayout, QPushButton, QCheckBox, QSizePolicy, QLabel, QMessageBox
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
        self.inputs = list()
        self.controller = controller
        self.step_number = step_number
        self._param_set = param_set
        self.normal_check = QCheckBox("Normal")
        self.grid_check = QCheckBox("Grid")
        rows = self._param_set_to_form_rows()
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self._create_buttons())
        self.setLayout(Form(rows))


    def _param_set_to_form_rows(self) -> List[FormRow]:

        rows = list()
        checks = QFrame()
        checks.setLayout(QHBoxLayout())
        checks.layout().addWidget(self.normal_check)
        checks.layout().addWidget(self.grid_check)
        rows.append(FormRow("", widget=checks))

        header = QFrame()
        header.setLayout(QHBoxLayout())
        label = QLabel("min")
        label.setAlignment(Qt.AlignCenter)
        header.layout().addWidget(label)
        label = QLabel("max")
        label.setAlignment(Qt.AlignCenter)
        header.layout().addWidget(label)
        label = QLabel("step")
        label.setAlignment(Qt.AlignCenter)
        header.layout().addWidget(label)
        rows.append(FormRow("", widget=header))

        if self._param_set:
            for key, value in self._param_set.items():
                if isinstance(value, list):
                    i = 1
                    for _ in value:
                        sweep_inputs = QFrame()
                        sweep_inputs.setLayout(QHBoxLayout())
                        sweep_inputs.layout().addWidget(QLineEdit())
                        sweep_inputs.layout().addWidget(QLineEdit())
                        sweep_inputs.layout().addWidget(QLineEdit())
                        self.inputs.append(sweep_inputs)
                        rows.append(FormRow(label=f"{key} {i}", widget=sweep_inputs))
                        i = i + 1
                else:
                    sweep_inputs = QFrame()
                    sweep_inputs.setLayout(QHBoxLayout())
                    sweep_inputs.layout().addWidget(QLineEdit())
                    sweep_inputs.layout().addWidget(QLineEdit())
                    sweep_inputs.layout().addWidget(QLineEdit())
                    self.inputs.append(sweep_inputs)
                    rows.append(FormRow(label=key, widget=sweep_inputs))


        rows.append(FormRow("", widget= self._create_buttons()))
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
        inputs = list()
        for widget in self.inputs:
            inputs.append([widget.children()[1].text(), widget.children()[3].text(), widget.children()[2].text()])
        normal_check: bool = self.normal_check.isChecked()
        self.sanitize_ui_inputs(inputs, normal_check)
        retval = self.warn_images_created(inputs, normal_check)
        if retval == 1024:
            if not normal_check:
                # grid search can have differing lengths
                self.controller.run_step_sweep(self.step_number, self._param_set, inputs, "grid")
            else:
                # normal sweeps have to have the same length arrays
                self.controller.run_step_sweep(self.step_number, self._param_set, inputs, "normal")

    def sanitize_ui_inputs(self, ui_inputs: List[List[str]], norm_checked: bool):

        len_of_list = None
        for i in ui_inputs:
            # make sure user has inputted a number or min:step:max notation
            for j in i:
                try:
                    # is the notation done with just numbers?
                    float(j)
                except ValueError:
                    raise ValueError("Please enter a single number or the min:step:max notation for sweeps")

            if norm_checked:
                # make sure that user has same length sweeps for normal sweeps

                length_sweep = ((float(i[2]) - float(i[0])) / float(i[1])) + 1
                if not len_of_list:
                    len_of_list = length_sweep
                elif len_of_list != length_sweep:
                    raise ValueError("When doing a normal sweep, all sweep lengths must be equal")

    def warn_images_created(self, ui_input, normal_checked):
        if normal_checked:
            # lengths already checked, can use first length
            length = ((float(ui_input[0][2]) - float(ui_input[0][0])) / float(ui_input[0][1])) + 1
        else:
            length = 1
            for sweeps in ui_input:
                length = length * (((float(sweeps[2]) - float(sweeps[0])) / float(sweeps[1])) + 1)
        message = QMessageBox()
        message.setText(f"{int(length)} result image layers will be created.")
        message.setWindowTitle("Running Sweep")
        message.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        return message.exec_()










