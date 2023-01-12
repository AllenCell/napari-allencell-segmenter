import qtpy
from qtpy.QtWidgets import (
    QDialog,
    QLineEdit,
    QVBoxLayout,
    QFrame,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QMessageBox,
    QProgressBar,
    QComboBox,
)
from qtpy.QtCore import Qt
from typing import Dict, Any, List
from napari_allencell_segmenter.widgets.form import Form, FormRow
from functools import partial
from napari.qt import get_stylesheet
from napari_allencell_segmenter.widgets.warning_message import WarningMessage


class ParamSweepWidget(QDialog):
    """
    A dialog box containing a workflow finished message. Also includes a button to open the output folder
    and a button to close the dialog box

    Params:
        output_folder (Path):       The output folder to open when the corresponding button is clicked by the user.
    """

    def __init__(self, param_set: Dict[str, Any], step_number, controller):
        super().__init__()
        # Track UI elements
        self.live_count: QLabel = None
        self.progress_bar: QProgressBar = None
        self.inputs: Dict[str, QFrame] = dict()
        self.default_sweep_values: Dict = dict()
        self.layout: QVBoxLayout = QVBoxLayout()
        # State
        self.controller = controller
        self.step_number: int = step_number
        self.param_set: Dict[str, Any] = param_set
        rows: List[FormRow] = self._create_sweep_ui()

        # Format UI on init
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self._create_buttons())
        self.setLayout(Form(rows))
        self.setStyleSheet(get_stylesheet(self.controller.viewer.get_theme()))
        self.setWindowTitle("Parameter Sweep")

    def _create_sweep_ui(self) -> List[FormRow]:
        """
        Populate the sweep widget with this workflow step's parameters and their default values as well as other
        UI elements needed to run a sweep.

         Params:
            none
        """
        rows: List[FormRow] = list()
        # add ui elements in order
        rows.append(FormRow("", widget=self.create_sweep_headers()))

        # convert parameter set to form rows
        default_params: Dict = self.controller.model.active_workflow.workflow_definition.steps[
            self.step_number
        ].function.parameters
        if self.param_set:
            for key, value in self.param_set.items():
                # sometimes multiple unique params are in one list, need to separate out for UI
                if isinstance(value, list):
                    if not isinstance(value[0], str):
                        i = 1
                        for _ in value:
                            sweep_inputs: QFrame = QFrame()
                            sweep_inputs.setLayout(QHBoxLayout())
                            # get default value
                            min_value: int = default_params[key][i - 1].min_value
                            max_value: int = default_params[key][i - 1].max_value
                            step_size: float = (max_value - min_value) / 2

                            # Create UI Elements and populate with default values
                            min_input: QLineEdit = QLineEdit()
                            min_input.setText(str(min_value))
                            min_input.editingFinished.connect(self._on_change_textbox)
                            sweep_inputs.layout().addWidget(min_input)

                            max_input: QLineEdit = QLineEdit()
                            max_input.setText(str(max_value))
                            max_input.editingFinished.connect(self._on_change_textbox)
                            sweep_inputs.layout().addWidget(max_input)

                            step_input = QLineEdit()
                            step_input.setText(str(step_size))
                            step_input.editingFinished.connect(self._on_change_textbox)
                            sweep_inputs.layout().addWidget(step_input)

                            # Reset button for row (reset to default values)
                            reset_button: QPushButton = QPushButton("reset")
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
                        dropdown.setStyleSheet("QComboBox { combobox-popup: 0; }")
                        dropdown.addItems(default_params[key][0].options)
                        self.inputs[key] = dropdown
                        rows.append(FormRow(key, widget=dropdown))
                    else:
                        # for typical sweep params
                        sweep_inputs: QFrame = QFrame()
                        sweep_inputs.setLayout(QHBoxLayout())
                        # get the default values
                        min_value: int = default_params[key][0].min_value
                        max_value: int = default_params[key][0].max_value
                        step_size: float = (max_value - min_value) / 2

                        # Create UI elements and populate with default values
                        min_input: QLineEdit = QLineEdit()
                        min_input.setText(str(min_value))
                        min_input.editingFinished.connect(self._on_change_textbox)
                        sweep_inputs.layout().addWidget(min_input)

                        max_input: QLineEdit = QLineEdit()
                        max_input.setText(str(max_value))
                        max_input.editingFinished.connect(self._on_change_textbox)
                        sweep_inputs.layout().addWidget(max_input)

                        step_input: QLineEdit = QLineEdit()
                        step_input.setText(str(step_size))
                        step_input.editingFinished.connect(self._on_change_textbox)
                        sweep_inputs.layout().addWidget(step_input)
                        self.inputs[key] = sweep_inputs

                        # Create button to reset back to default values
                        reset_button: QPushButton = QPushButton("reset")
                        reset_button.setStyleSheet("border: none;")
                        reset_button.clicked.connect(lambda: self._reset_row_to_default(key))
                        sweep_inputs.layout().addWidget(reset_button)
                        rows.append(FormRow(key, widget=sweep_inputs))

        # Grab user input as str
        def_params_values: List[List[str]] = self.grab_ui_values(grab_combo=False)

        # Display how many images will be create with this sweep
        def_count: int = self.get_live_count(def_params_values)
        self.live_count = QLabel(f"{def_count} images will be created")
        self.live_count.setAlignment(qtpy.QtCore.Qt.AlignCenter)

        # Create progress bar with length of sweep
        self.create_progress_bar(bar_len=def_count)

        rows.append(FormRow("", widget=self.live_count))
        rows.append(FormRow("", widget=self.progress_bar))
        rows.append(FormRow("", widget=self._create_buttons()))
        return rows

    def _create_buttons(self) -> QFrame:
        """
        Creates buttons for the bottom of the dialog box, one for opening the output folder, and one for
            closing the dialog box

        Params:
            None

        Returns:
            (QFrame): A QFrame that has two horizontally laid out buttons, first button is Open output directory,
                second button is close.
        """
        buttons: QFrame = QFrame()
        buttons.setLayout(QHBoxLayout())
        self.run_sweep_button = QPushButton("Start Sweep")
        self.run_sweep_button.setToolTip("Start sweep using the selected napari layer as the input image.")
        self.run_sweep_button.clicked.connect(self._run_sweep)
        self.run_sweep_button.setAutoDefault(False)
        close_button: QPushButton = QPushButton("Cancel")
        close_button.setToolTip("Cancel an active parameter sweep.")
        close_button.clicked.connect(self.cancel)
        close_button.setAutoDefault(False)
        buttons.layout().addWidget(self.run_sweep_button)
        buttons.layout().addWidget(close_button)
        return buttons

    def _run_sweep(self) -> None:
        """
        Initiate a sweep (called when run sweep button is pressed) with the values provided in the UI

        Params:
           none
        """
        inputs: List[List[str]] = self.grab_ui_values(grab_combo=False)
        try:
            self.sanitize_ui_inputs(inputs)
        except ValueError:
            WarningMessage("Please enter valid numbers for sweep parameters.").show()

        count: int = self.get_live_count(inputs)
        if count > 20:
            # warn if too many images will be generated
            if self.warn_images_created(count) == 1024:
                self.set_run_in_progress()
                self.controller.run_step_sweep(self, self.grab_ui_values())
        else:
            self.set_run_in_progress()
            self.controller.run_step_sweep(self, self.grab_ui_values())

    def sanitize_ui_inputs(self, ui_inputs: List[List[str]]) -> None:
        """
        Check that all user inputs in the UI (passed as str) can be converted to a valid float
        Params:
           ui_inputs (List[List[str]]): inputs recieved from the UI as str
        """
        for i in ui_inputs:
            for j in i:
                try:
                    # ensure user input (passed as str) is a valid number
                    float(j)
                except ValueError:
                    raise ValueError("Please enter a single number or the min:step:max notation for sweeps")

    def warn_images_created(self, count: int) -> None:
        """
        Create a popup to warn a user that they will be creating a large number of layers by running a sweep.

        Params:
           count (int): number of images that user will create for warning
        """
        message: QMessageBox = QMessageBox()
        message.setText(f"{int(count)} result image layers will be created.")
        message.setStyleSheet(get_stylesheet(self.controller.viewer.get_theme()))
        message.setWindowTitle("Running Sweep")
        message.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        return message.exec_()

    def update_live_count(self, count: int) -> None:
        """
        Update the Live count on the param sweep widget

        Params:
            count (int): new live count to update with
        """
        if self.live_count:
            self.live_count.setText(f"{count } images will be created")

    def get_live_count(self, inputs: List[List[str]]) -> int:
        """
        Calculate how many images will be created with the user provided values for this sweep

        Params:
            inputs (List[List[str]]): user inputs from the paramsweepwidget to calculate how many total result layers
            will be created
        """
        # make sure all user inputs are valid numbers
        self.sanitize_ui_inputs(inputs)
        length: int = 1
        for sweeps in inputs:
            # multiplying the result layers for all parameters will give total result layers
            # (ex: if param1 creates 5 combinations and param2 creates 5 combinations, there will be
            # 25 result layers created 5x5=25)
            length = length * self.get_sweep_len(float(sweeps[0]), float(sweeps[1]), float(sweeps[2]))
        return length

    def get_sweep_len(self, min: float, step: float, max: float) -> int:
        """
        Calculate how many result layers will be created for one parameter's sweep values

        Params:
            min (float): starting range of sweep provided by user
            step (float): increment value of sweep provided by user
            max (float): end value of sweep provided by user
        """
        i: float = min
        count: int = 0
        while i <= max:
            i = i + step
            count = count + 1
        return count

    def grab_ui_values(self, grab_combo=True) -> List[List[str]]:
        """
        Update the Live count on the param sweep widget

        Params:
            count (int): new live count to update with
        """
        inputs: List[List[str]] = list()
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
                except IndexError:
                    # is a combobox(string parameters)
                    inputs.append(widget.currentText())
                except AttributeError:
                    inputs.append(widget.currentText())
            else:
                # do not grab values from combobox (for checking inputs and getting size of sweeps)
                try:
                    inputs.append(
                        [widget.children()[1].text(), widget.children()[3].text(), widget.children()[2].text()]
                    )
                except Exception:
                    pass
        return inputs

    def create_progress_bar(self, bar_len: int = 10) -> QProgressBar:
        """
        Create a progress bar with the given length

        Params:
            bar_len (int): length of progress bar to be created
        """
        self.progress_bar: QProgressBar = QProgressBar()
        self.progress_bar.setRange(0, bar_len)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        return self.progress_bar

    def update_progress_bar_len(self, new_len: int) -> None:
        """
        Update the progress bar so it has the given length

        Params:
            new_len (int): new length to update progress bar
        """
        if self.progress_bar:
            self.progress_bar.setRange(0, new_len)
            self.progress_bar.setValue(0)

    def increment_progress_bar(self) -> None:
        """
        Increment the progress bar by one step

        Params:
            none
        """
        if self.controller.run_lock:
            self.progress_bar.setValue(self.progress_bar.value() + 1)

    def reset_progress_bar(self) -> None:
        """
        Reset the progress bar to 0

        Params:
            none
        """
        self.progress_bar.setValue(0)

    def set_progress_bar(self, val: int) -> None:
        """
        Set the progress bar to the value provided

        Params:
            val: value to set the progess bar to
        """
        self.progress_bar.setValue(val)

    def create_sweep_headers(self) -> QFrame:
        """
        Create headers for the sweep UI

        Params:
            none
        """
        # headers
        header: QFrame = QFrame()
        header.setLayout(QHBoxLayout())
        label: QLabel = QLabel("min")
        label.setAlignment(Qt.AlignCenter)
        header.layout().addWidget(label)
        label: QLabel = QLabel("max")
        label.setAlignment(Qt.AlignCenter)
        header.layout().addWidget(label)
        label: QLabel = QLabel("step size")
        label.setAlignment(Qt.AlignCenter)
        header.layout().addWidget(label)
        return header

    def _on_change_textbox(self) -> None:
        """
        Event listener called when textboxes in widget are edited

        Params:
            none
        """
        # grab new values
        inputs: List[List[str]] = self.grab_ui_values(grab_combo=False)
        # calculate new count
        new_count: int = self.get_live_count(inputs)
        # update ui
        self.update_live_count(new_count)
        self.update_progress_bar_len(new_count)

    def set_run_in_progress(self) -> None:
        """
        function called when a run is in progress

        Params:
            none
        """
        self.run_sweep_button.setText("Cancel")

    def set_run_finished(self) -> None:
        """
        function called when a run is finished

        Params:
            none
        """
        self.run_sweep_button.setText("Run Sweep")
        self.run_sweep_button.clicked.connect(self._run_sweep)

    def cancel(self) -> None:
        """
        Cancel the current sweep

        Params:
            none
        """
        if self.controller.run_lock:
            # if running, cancel
            self.controller.cancel_run_all()
        else:
            # if not running, close window
            self.close()

    def _reset_row_to_default(self, key_of_row: str, list_index: int = None):
        """
        Reset a parameter row to its default values

        Params:
            key_of_row (str): Name of row in ui to change back to default values
            list_index (int): index of parameter if there are multiple with the same name
        """
        default_param_set: Dict = self.controller.model.active_workflow.workflow_definition.steps[
            self.step_number
        ].function.parameters

        if list_index:
            input_boxes: List = self.inputs[key_of_row + str(list_index)].children()
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

        updated_values: List[List[str]] = self.grab_ui_values(grab_combo=False)
        self.update_live_count(self.get_live_count(updated_values))
