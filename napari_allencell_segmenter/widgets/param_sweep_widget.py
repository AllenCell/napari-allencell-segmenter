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
    QProgressBar,
    QComboBox,
)
from qtpy.QtCore import Qt

from typing import Dict, Any, List
from napari_allencell_segmenter.widgets.form import Form, FormRow
from functools import partial


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
        self.progress_bar = None
        self.inputs = dict()
        self.default_sweep_values = dict()
        self.controller = controller
        self.step_number = step_number
        self.param_set = param_set
        rows = self._create_sweep_ui()
        self.layout = QVBoxLayout()

        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self._create_buttons())
        self.setLayout(Form(rows))
        self.setWindowTitle("Parameter Sweep")

    def _create_sweep_ui(self) -> List[FormRow]:
        rows = list()
        # add ui elements in order
        rows.append(FormRow("", widget=self.create_sweep_headers()))

        # convert parameter set to form rows
        default_params = self.controller.model.active_workflow.workflow_definition.steps[
            self.step_number
        ].function.parameters
        if self.param_set:
            for key, value in self.param_set.items():
                # sometimes multiple unique params are in one list, need to separate out for UI
                if isinstance(value, list):
                    if not isinstance(value[0], str):
                        i = 1
                        for _ in value:
                            sweep_inputs = QFrame()
                            sweep_inputs.setLayout(QHBoxLayout())
                            min_value = default_params[key][i - 1].min_value
                            max_value = default_params[key][i - 1].max_value
                            step_size = (max_value - min_value) / 2

                            min_input = QLineEdit()
                            min_input.setText(str(min_value))
                            min_input.editingFinished.connect(self._on_change_textbox)
                            sweep_inputs.layout().addWidget(min_input)

                            max_input = QLineEdit()
                            max_input.setText(str(max_value))
                            max_input.editingFinished.connect(self._on_change_textbox)
                            sweep_inputs.layout().addWidget(max_input)

                            step_input = QLineEdit()
                            step_input.setText(str(step_size))
                            step_input.editingFinished.connect(self._on_change_textbox)
                            sweep_inputs.layout().addWidget(step_input)

                            reset_button = QPushButton("reset")
                            reset_button.setStyleSheet("border: none;")
                            # pass the key and value as values for calling function later on
                            reset_button.clicked.connect(
                                partial(lambda k, val: self._reset_row_to_default(k, val), key, i)
                            )
                            sweep_inputs.layout().addWidget(reset_button)

                            # store the index of this parameter in its list appended to the parameter key
                            self.inputs[key + str(i)] = sweep_inputs
                            rows.append(FormRow(f"{key} {i}", widget=sweep_inputs))
                            i = i + 1
                else:
                    # most params are single entries in the param dictionary
                    # for params that are a dropdown
                    if default_params[key][0].widget_type.name == "DROPDOWN":
                        dropdown = QComboBox()
                        dropdown.addItems(default_params[key][0].options)
                        self.inputs[key] = dropdown
                        rows.append(FormRow(key, widget=dropdown))
                    else:
                        # for typical sweep params
                        sweep_inputs = QFrame()
                        sweep_inputs.setLayout(QHBoxLayout())
                        min_value = default_params[key][0].min_value
                        max_value = default_params[key][0].max_value
                        step_size = (max_value - min_value) / 2

                        min_input = QLineEdit()
                        min_input.setText(str(min_value))
                        min_input.editingFinished.connect(self._on_change_textbox)
                        sweep_inputs.layout().addWidget(min_input)

                        max_input = QLineEdit()
                        max_input.setText(str(max_value))
                        max_input.editingFinished.connect(self._on_change_textbox)
                        sweep_inputs.layout().addWidget(max_input)

                        step_input = QLineEdit()
                        step_input.setText(str(step_size))
                        step_input.editingFinished.connect(self._on_change_textbox)
                        sweep_inputs.layout().addWidget(step_input)
                        self.inputs[key] = sweep_inputs

                        reset_button = QPushButton("reset")
                        reset_button.setStyleSheet("border: none;")
                        reset_button.clicked.connect(lambda: self._reset_row_to_default(key))
                        sweep_inputs.layout().addWidget(reset_button)
                        rows.append(FormRow(key, widget=sweep_inputs))

        def_params_values = self.grab_ui_values(grab_combo=False)
        def_count = self.get_live_count(def_params_values)
        self.live_count = QLabel(f"{def_count} images will be created")
        self.live_count.setAlignment(qtpy.QtCore.Qt.AlignCenter)
        self.create_progress_bar(bar_len=def_count)
        rows.append(FormRow("", widget=self.live_count))
        rows.append(FormRow("", widget=self.progress_bar))
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
        self.run_sweep_button = QPushButton("Start Sweep")
        self.run_sweep_button.clicked.connect(self._run_sweep)
        self.run_sweep_button.setAutoDefault(False)
        close_button = QPushButton("Cancel")
        close_button.clicked.connect(self.cancel)
        close_button.setAutoDefault(False)
        buttons.layout().addWidget(self.run_sweep_button)
        buttons.layout().addWidget(close_button)
        return buttons

    def _run_sweep(self):
        inputs = self.grab_ui_values(grab_combo=False)
        count = self.get_live_count(inputs)
        if count > 20:
            # warn if too many images will be generated
            if self.warn_images_created(count) == 1024:
                self.set_run_in_progress()
                self.controller.run_step_sweep(self, self.grab_ui_values())
        else:
            self.set_run_in_progress()
            self.controller.run_step_sweep(self, self.grab_ui_values())

    def sanitize_ui_inputs(self, ui_inputs: List[List[str]]):
        for i in ui_inputs:
            # make sure user has inputted a number or min:step:max notation
            for j in i:
                try:
                    # is the notation done with just numbers?
                    float(j)
                except ValueError:
                    raise ValueError("Please enter a single number or the min:step:max notation for sweeps")

    def warn_images_created(self, count):
        message = QMessageBox()
        message.setText(f"{int(count)} result image layers will be created.")
        message.setWindowTitle("Running Sweep")
        message.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        return message.exec_()

    def update_live_count(self, count):
        if self.live_count:
            self.live_count.setText(f"{count } images will be created")

    def get_live_count(self, inputs):
        self.sanitize_ui_inputs(inputs)
        length = 1
        for sweeps in inputs:
            length = length * self.get_sweep_len(float(sweeps[0]), float(sweeps[1]), float(sweeps[2]))
        return length

    def get_sweep_len(self, min, step, max):
        # TODO make this more efficient
        i = min
        count = 0
        while i <= max:
            i = i + step
            count = count + 1
        return count

    def grab_ui_values(self, grab_combo=True):
        inputs = list()
        for widget in self.inputs.values():
            # grab values from combobox (when calling run_sweep function)
            if grab_combo:
                # ui is min, max, step
                # transform into min, step, max
                try:
                    # is a set of numbers for sweep
                    inputs.append(
                        [widget.children()[1].text(), widget.children()[3].text(), widget.children()[2].text()]
                    )
                except IndexError as err:
                    # is a combobox(string parameters)
                    inputs.append(widget.currentText())
            else:
                # do not grab values from combobox (for checking inputs and getting size of sweeps)
                try:
                    inputs.append(
                        [widget.children()[1].text(), widget.children()[3].text(), widget.children()[2].text()]
                    )
                except:
                    pass
        return inputs

    def create_progress_bar(self, bar_len=10) -> QProgressBar:
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, bar_len)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        return self.progress_bar

    def create_sweep_headers(self) -> QFrame:
        # headers
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
        return header

    def update_progress_bar_len(self, new_len):
        if self.progress_bar:
            self.progress_bar.setRange(0, new_len)
            self.progress_bar.setValue(0)

    def _on_change_textbox(self):
        # event handler for when textboxes are changed
        inputs = self.grab_ui_values(grab_combo=False)

        new_count = self.get_live_count(inputs)
        self.update_live_count(new_count)

        self.update_progress_bar_len(new_count)

    def increment_progress_bar(self):
        if self.controller.run_lock:
            self.progress_bar.setValue(self.progress_bar.value() + 1)

    def reset_progress_bar(self):
        self.progress_bar.setValue(0)

    def set_progress_bar(self, val: int):
        self.progress_bar.setValue(val)

    def set_run_in_progress(self):
        self.run_sweep_button.setText("Cancel")

    def set_run_finished(self):
        self.run_sweep_button.setText("Run Sweep")
        self.run_sweep_button.clicked.connect(self._run_sweep)

    def cancel(self):
        if self.controller.run_lock:
            # if running, cancel
            self.controller.cancel_run_all()
        else:
            # if not running, close window
            self.close()

    def _reset_row_to_default(self, key_of_row: str, list_index=None):
        default_param_set = self.controller.model.active_workflow.workflow_definition.steps[
            self.step_number
        ].function.parameters

        if list_index:
            input_boxes = self.inputs[key_of_row + str(list_index)].children()
        else:
            input_boxes = self.inputs[key_of_row].children()

        if list_index:
            default_params = default_param_set[key_of_row][list_index - 1]
        else:
            default_params = default_param_set[key_of_row][0]

        # reset min value
        input_boxes[1].setText(str(default_params.min_value))
        # reset max value
        input_boxes[2].setText(str(default_params.max_value))
        # reset step_size value
        input_boxes[3].setText(str((default_params.max_value - default_params.min_value) / 2))

        updated_values = self.grab_ui_values(grab_combo=False)
        self.update_live_count(self.get_live_count(updated_values))
