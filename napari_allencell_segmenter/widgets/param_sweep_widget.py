
from qtpy.QtWidgets import QDialog, QLineEdit, QVBoxLayout, QFrame, QHBoxLayout, QPushButton, QCheckBox

from typing import Dict, Any, List
from widgets.form import FormRow, Form


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
                    rows.append(FormRow(label=f"{key} 1", widget= QLineEdit()))
                    rows.append(FormRow(label=f"{key} 2", widget=QLineEdit()))
                else:
                    rows.append(FormRow(label=key, widget=QLineEdit()))




            checks = QFrame()
            checks.setLayout(QHBoxLayout())
            normal = QCheckBox("Normal")
            grid = QCheckBox("Grid")
            checks.layout().addWidget(normal)
            checks.layout().addWidget(grid)
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
        type = "normal"
        for widget in self.children():
            if isinstance(widget, QLineEdit):
                inputs.append(widget.text())
            if isinstance(widget, QFrame):
                try:
                    if widget.children()[2].isChecked():
                        type="grid"
                except:
                    print("is label")
        self.controller.run_step_sweep(self.step_number, self._param_set, inputs, type)






