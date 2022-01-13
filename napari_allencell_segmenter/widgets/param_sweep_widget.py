from qtpy.QtWidgets import QDialog, QLineEdit, QVBoxLayout, QFrame, QHBoxLayout, QPushButton, QCheckBox

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
        if self._param_set:
            for key, value in self._param_set.items():
                if isinstance(value, list):
                    i = 1
                    for _ in value:
                        rows.append(FormRow(label=f"{key} {i}", widget=QLineEdit()))
                        i = i + 1
                else:
                    rows.append(FormRow(label=key, widget=QLineEdit()))

            checks = QFrame()
            checks.setLayout(QHBoxLayout())
            checks.layout().addWidget(self.normal_check)
            checks.layout().addWidget(self.grid_check)
            rows.append(FormRow("", widget=checks))

        button = QPushButton("start sweep")
        button.clicked.connect(self._run_sweep)
        rows.append(FormRow(label="", widget=button))
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
        run_sweep = QPushButton("Open output directory")
        run_sweep.clicked.connect(self._run_sweep)
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        buttons.layout().addWidget(run_sweep)
        buttons.layout().addWidget(close_button)
        return buttons

    def _run_sweep(self):
        inputs = list()
        for widget in self.children():
            if isinstance(widget, QLineEdit):
                inputs.append(widget.text())

        self.sanitize_ui_inputs(inputs, self.normal_check.isChecked())
        if self.grid_check.isChecked():
            # grid search can have differing lengths
            self.controller.run_step_sweep(self.step_number, self._param_set, inputs, "grid")
        elif self.normal_check.isChecked():
            # normal sweeps have to have the same length arrays
            self.controller.run_step_sweep(self.step_number, self._param_set, inputs, "normal")

    def sanitize_ui_inputs(self, ui_inputs: List[str], norm_checked: bool):

        len_of_list = None
        for i in ui_inputs:
        # make sure user has inputted a number or min:step:max notation
            numbers = None
            try:
                # is it a number?
                float(i)
            except ValueError:
                # is it the min:step:max notation?
                numbers = i.split(":")
                for j in numbers:
                    try:
                        float(j)
                    except ValueError:
                        raise ValueError("Please enter a single number or the min:step:max notation for sweeps")

            if norm_checked:
                # make sure that user has same length sweeps for normal sweeps
                if numbers:
                    length_sweep = ((numbers[2] - numbers[0]) / numbers[1]) + 1
                    if not len_of_list:
                        len_of_list = length_sweep
                    elif len_of_list != length_sweep:
                        raise ValueError("When doing a normal sweep, all sweep lengths must be equal")







