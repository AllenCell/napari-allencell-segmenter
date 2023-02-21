import numpy
import warnings

from pathlib import Path
from typing import Dict, Generator, List, Tuple, Any
from napari.qt.threading import create_worker, GeneratorWorker
from aicssegmentation.workflow import WorkflowEngine, WorkflowStep, WorkflowDefinition
from napari_allencell_segmenter.view.workflow_steps_view import WorkflowStepsView
from napari_allencell_segmenter.core._interfaces import IApplication
from napari_allencell_segmenter.controller._interfaces import IWorkflowStepsController
from napari_allencell_segmenter.core.controller import Controller
from napari_allencell_segmenter.model.segmenter_model import SegmenterModel
from napari_allencell_segmenter.widgets.param_sweep_widget import ParamSweepWidget
import numpy as np
from qtpy.QtWidgets import QMessageBox
from napari.qt import get_stylesheet
import copy
from napari.layers import Image


class WorkflowStepsController(Controller, IWorkflowStepsController):
    _worker: GeneratorWorker = None

    def __init__(self, application: IApplication, workflow_engine: WorkflowEngine):
        super().__init__(application)
        if workflow_engine is None:
            raise ValueError("workflow_engine")
        self._workflow_engine: WorkflowEngine = workflow_engine
        self._view: WorkflowStepsView = WorkflowStepsView(self)
        self._run_lock: bool = False  # lock to avoid triggering multiple segmentation / step runs at the same time
        self._steps: int = 0  # need this to count steps completed
        self._max_step_run: int = -1
        self._number_times_run: int = 0
        # TODO package this differently
        self._current_params: Dict = None
        self.param_sweep_widget: ParamSweepWidget = None
        self._sweep_step: int = None

    @property
    def view(self):
        return self._view

    @property
    def model(self) -> SegmenterModel:
        return self.state.segmenter_model

    def index(self) -> None:
        self.load_view(self._view, self.model)

    def save_workflow(self, steps: List[WorkflowStep], output_file_path: str):
        """
        Save the current workflow as a .json file for future use
        """
        # add .json extension if not present
        if not output_file_path.lower().endswith(".json"):
            output_file_path += ".json"
        save_path = Path(output_file_path)
        workflow_def = WorkflowDefinition(save_path.name, steps)
        self._workflow_engine.save_workflow_definition(workflow_def, save_path)

    def close_workflow(self) -> None:
        """
        Close the active workflow
        """
        if self._worker is not None:
            # we're about to load a new controller/view,
            # disconnect worker events to avoid acting on deleted QT objects since worker operations are asynchronous
            # worker will be garbage collected
            self._disconnect_worker_events()
            self.cancel_run_all()
        self.model.reset()
        self.router.workflow_selection()

    def run_all(self, parameter_inputs: List[Dict[str, Any]]) -> None:
        """
        Run all steps in the active workflow.
        parameter_inputs List[Dict]: Each dictionary has the same shape as a WorkflowStep.parameter_values
        dictionary, but with the parameter values obtained from the UI instead of default values.
        """
        if not self._run_lock:
            self._worker: GeneratorWorker = create_worker(self._run_all_async, parameter_inputs)
            self._worker.yielded.connect(self._on_step_processed_all)
            self._worker.started.connect(self._on_run_all_started)
            self._worker.finished.connect(self._on_run_all_finished)
            self._worker.start()

    def run_next_step(self, parameter_inputs: Dict[str, Any]) -> None:
        """
        Run the next step in the active workflow
        parameter_inputs: Each dictionary has the same shape as a WorkflowStep.parameter_values
        dictionary, but with the parameter values obtained from the UI instead of default values.
        """
        if not self._run_lock:
            self._worker: GeneratorWorker = create_worker(self._run_next_step_async, parameter_inputs)
            self._worker.yielded.connect(self._on_step_processed)
            self._worker.started.connect(self._on_run_all_started)
            self._worker.finished.connect(self._on_run_all_finished)
            self._worker.start()

    def run_step(self, i: int, parameter_inputs: Dict[str, Any]) -> None:
        """
        Run a step in the active workflow
        i int: index of step to run in the active workflow
        parameter_inputs: Each dictionary has the same shape as a WorkflowStep.parameter_values
        dictionary, but with the parameter values obtained from the UI instead of default values.
        """
        if not self._run_lock:
            selected_layers: List[Image] = self.viewer.get_active_layer()
            cont: bool = True  # continue execution

            step_to_run: WorkflowStep = self.model.active_workflow.workflow_definition.steps[i]
            if len(step_to_run.parent) != len(selected_layers):
                # too many or too few images selected as the input layer,
                # abort run attempt and show warning
                self.warn_box(
                    f"{step_to_run.name} requires {len(step_to_run.parent)} input images, "
                    f"but you have selected {len(selected_layers)} images."
                    f"\nPlease select {len(step_to_run.parent)} images by ctrl+clicking.",
                    "Wrong number of input images selected",
                    one_option=True,
                )
                cont = False  # continue if user is running steps in order, and correct input steps are selected
            else:
                # check to see if correct layers were selected to run this segmentation in order
                # some steps require multiple layers.
                for selected_layer in selected_layers:
                    if selected_layer.name[:1].isdigit() and int(selected_layer.name[:1]) not in step_to_run.parent:
                        # check to see if the correct image input layer is selected.
                        if i == 0:
                            response = self.warn_box(
                                f"You currently have the layer {selected_layer.name} selected in napari which will "
                                f"be used as the input layer. You will run this segmentation"
                                f" out of order. \nTo run the segmentation in order, "
                                f"please select the starting image (step 0) as the "
                                f"input layer for this step. "
                                f"\n Would you still like to continue?",
                                "Run segmentation out of order",
                            )
                        else:
                            step_required_name = self.model.active_workflow.workflow_definition.steps[
                                step_to_run.parent[0] - 1
                            ].name
                            response = self.warn_box(
                                f"You currently have the layer {selected_layer.name} selected in napari which will "
                                f"be used as the input layer. You will run this segmentation"
                                f" out of order. To run the segmentation in order, "
                                f"please select a layer that is the output of "
                                f"{i}. {step_required_name}."
                                f"\n Would you like to continue?",
                                "Run segmentation out of order",
                            )
                        cont = response == 1024
                    elif not selected_layer.name[:1].isdigit():
                        if i == 0:
                            response = self.warn_box(
                                f"You currently have the layer {selected_layer.name} selected in napari which will "
                                f"be used as the input layer. You will run this segmentation"
                                f" out of order. \nTo run the segmentation in order, "
                                f"please select the starting image (step 0) as the "
                                f"input layer for this step. "
                                f"\n Would you still like to continue?",
                                "Run segmentation out of order",
                            )
                        else:
                            step_required_name = self.model.active_workflow.workflow_definition.steps[
                                step_to_run.parent[0] - 1
                            ].name
                            response = self.warn_box(
                                f"You currently have the layer {selected_layer.name} selected in napari which will "
                                f"be used as the input layer. You will run this segmentation"
                                f" out of order. To run the segmentation in order, "
                                f"please select a layer that is the output of "
                                f"{i}. {step_required_name}."
                                f"\n Would you like to continue?",
                                "Run segmentation out of order",
                            )
                        cont = response == 1024

            if cont:
                self._worker: GeneratorWorker = create_worker(self._run_step_async, i, parameter_inputs)
                self._worker.yielded.connect(self._on_step_processed)
                self._worker.started.connect(self._on_run_all_started)
                self._worker.finished.connect(self._on_run_step_finished)
                self._worker.start()

    def run_step_sweep(self, param_sweep_widget: ParamSweepWidget, ui_inputs: List[List[str]]) -> None:
        """
        Run a step in the active workflow as a sweep
        i: index of step to run in the active workflow
        parameter_inputs: Each dictionary has the same shape as a WorkflowStep.parameter_values
        dictionary, but with the parameter values obtained from the UI instead of default values.
        ui_inputs List[List[str]]: inputs for the sweep values from the sweep UI
        type str: type of sweep, either "normal" or "grid"
        """
        self.param_sweep_widget = param_sweep_widget
        i: int = param_sweep_widget.step_number
        parameter_inputs: Dict[str, Any] = param_sweep_widget.param_set

        if not self._run_lock:
            if parameter_inputs:
                parameter_inputs_2: Dict[str, Any] = self._parse_inputs(copy.deepcopy(parameter_inputs), ui_inputs)
                self._worker: GeneratorWorker = create_worker(
                    self._run_step_sweep_grid, i, parameter_inputs, parameter_inputs_2
                )
                self._worker.yielded.connect(self._on_step_processed)
                self._worker.started.connect(self._on_sweep_started)
                self._worker.finished.connect(self.on_sweep_finished)
                self._sweep_step = 0
                self._worker.start()
            else:
                self._worker: GeneratorWorker = create_worker(self._run_step_async, i, parameter_inputs)
                self._worker.yielded.connect(self._on_step_processed)
                self._worker.started.connect(self._on_sweep_started)
                self._worker.finished.connect(self.on_sweep_finished)
                self._worker.start()

    def _run_step_sweep_grid(
        self, index: int, param_original: Dict[str, Any], param_sweep: Dict[str, Any]
    ) -> Tuple[WorkflowStep, np.ndarray]:
        """
        Run sweeps and deliver the result to napari
        """
        selected_image: Image = self.viewer.get_active_layer()
        # either one param, or two params as a list
        if len(param_original) == 1:
            if not isinstance(list(param_original.values())[0], list):
                # There's only one param being swept
                for i in range(len(list(param_sweep.values())[0])):
                    yield self._handle_sweep_single(index, i, param_sweep)
            else:
                # multiple unique params in one list
                list1, list2 = self._setup_params_sweep(
                    list(param_sweep.values())[0][0], list(param_sweep.values())[0][1]
                )
                # loop through all params and run sweep
                for x in list1:
                    for y in list2:
                        run_dict: Dict[str, List[float]] = {list(param_original.keys())[0]: [round(x, 3), round(y, 3)]}
                        step: WorkflowStep = self.model.active_workflow.workflow_definition.steps[index]
                        print(f"running step {step.name} with parameters {run_dict}")
                        result: np.ndarray = self.model.active_workflow.execute_step(index, run_dict, selected_image)
                        self._steps = index
                        self._current_params = run_dict
                        yield (step, result)
        else:
            # two separate params with different keys
            list1, list2 = self._setup_params_sweep(list(param_sweep.values())[0], list(param_sweep.values())[1])

            # loop through all params and run sweep
            for x in list1:
                for y in list2:
                    run_dict: Dict[str, float] = dict()
                    if isinstance(list(param_original.values())[0], list):
                        # first param expects a list
                        x = [round(x, 3)]
                    if isinstance(list(param_original.values())[1], list):
                        # second param expects a list
                        y = [round(y, 3)]
                    run_dict[list(param_original.keys())[0]] = x
                    run_dict[list(param_original.keys())[1]] = y
                    step: WorkflowStep = self.model.active_workflow.workflow_definition.steps[index]
                    print(f"running step {step.name} with parameters {run_dict}")
                    result: np.ndarray = self.model.active_workflow.execute_step(
                        index, run_dict, selected_image=self.viewer.get_active_layer()
                    )
                    self._steps = index
                    self._current_params = run_dict
                    yield (step, result)

    def _handle_sweep_single(
        self, index: int, sweep_index: int, param_sweep: Dict[str, Any]
    ) -> Tuple[WorkflowStep, np.ndarray]:
        """
        Run a step in a sweep that contains one parameter
        """
        # get selected layer from napari
        selected_image: Image = self.viewer.get_active_layer()
        # create dictionary for this run of the sweep
        run_dict: Dict[str, Any] = dict()
        run_dict[list(param_sweep.keys())[0]] = round(list(param_sweep.values())[0][sweep_index], 3)
        # run iteration
        step: WorkflowStep = self.model.active_workflow.workflow_definition.steps[index]
        print(f"running step {step.name} with parameters {run_dict}")
        result: np.ndarray = self.model.active_workflow.execute_step(index, run_dict, selected_image)
        # update state
        self._steps = index
        self._current_params = run_dict
        return (step, result)

    def _setup_params_sweep(self, first_params: Any, second_params: Any) -> Tuple[List, List]:
        """
        Format parameters in a way that aics-segmentation expects them
        """
        # shape parameters in the way that aics-segmentation expects them
        if not isinstance(first_params, list) and not isinstance(first_params, np.ndarray):
            first_params = [first_params]
        if not isinstance(second_params, list) and not isinstance(second_params, np.ndarray):
            second_params = [second_params]
        if not isinstance(first_params[0], float) and not isinstance(first_params[0], str):
            first_params = first_params[0]
        if not isinstance(second_params[0], float) and not isinstance(second_params[0], str):
            second_params = second_params[0]
        return first_params, second_params

    def cancel_run_all(self):
        """
        Cancel running all steps
        """
        if self._worker is not None:
            self._worker.quit()

    def _disconnect_worker_events(self):
        """
        Disconnect all worker events
        """
        self._worker.started.disconnect()
        self._worker.yielded.disconnect()
        self._worker.finished.disconnect()

    def _parse_inputs(self, parameter_inputs: Dict[str, Any], ui_input: List[List[str]]) -> Dict[str, Any]:
        """
        Parse inputs from the UI to create run dictionaries to feed into the sweep functions.
        """

        if parameter_inputs:
            formatted: Dict[str, Any] = dict(parameter_inputs)
        i = 0
        for k, v in parameter_inputs.items():
            if isinstance(v, list):
                # sometimes multiple unique params are in one list
                single_item: List[Any] = list()
                for _ in v:
                    inputs = ui_input[i]
                    i = i + 1
                    values_to_run = numpy.arange(float(inputs[0]), float(inputs[2]), float(inputs[1]))
                    # if min=max, just fix parameter
                    if inputs[0] == inputs[2]:
                        values_to_run = numpy.append(values_to_run, float(inputs[0]))
                    elif values_to_run[-1] + float(inputs[1]) <= float(inputs[2]):
                        values_to_run = numpy.append(values_to_run, values_to_run[-1] + float(inputs[1]))
                    single_item.append(values_to_run)
            else:
                # most params are single entries in the param dictionary
                inputs = ui_input[i]
                i = i + 1
                if not isinstance(inputs, str):
                    # for typical sweep ranges
                    single_item = numpy.arange(float(inputs[0]), float(inputs[2]), float(inputs[1]))

                    if inputs[0] == inputs[2]:
                        single_item = [float(inputs[0])]
                    elif single_item[-1] + float(inputs[1]) <= float(inputs[2]):
                        single_item = numpy.append(single_item, single_item[-1] + float(inputs[1]))
                else:
                    # for string parameters from dropdowns
                    single_item = inputs
            formatted[k] = single_item
        return formatted

    def _run_all_async(
        self, parameter_inputs: List[Dict[str, List]]
    ) -> Generator[Tuple[WorkflowStep, numpy.ndarray], None, None]:
        """
        Run all steps in a workflow.
        """
        self.model.active_workflow.reset()

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")  # avoid spamming the UI with warnings from segmenter

            i = 0
            while not self.model.active_workflow.is_done():
                step = self.model.active_workflow.get_next_step()
                result = self.model.active_workflow.execute_next(parameter_inputs[i])
                i = i + 1
                yield (step, result)

    def _run_next_step_async(
        self, parameter_inputs: List[Dict[str, List]]
    ) -> Generator[Tuple[WorkflowStep, numpy.ndarray], None, None]:
        """
        Run the next available step in the workflow
        """
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            step = self.model.active_workflow.get_next_step()
            result = self.model.active_workflow.execute_next(parameter_inputs[self._steps])
            self._steps = self._steps + 1
            yield (step, result)

    def _run_step_async(
        self, index: int, parameter_inputs: List[Dict[str, List]]
    ) -> Generator[Tuple[WorkflowStep, numpy.ndarray], None, None]:
        """
        Run a specified step in a workflow.
        """
        selected_image = self.viewer.get_active_layer()
        step = self.model.active_workflow.workflow_definition.steps[index]
        result = self.model.active_workflow.execute_step(index, parameter_inputs, selected_image)
        self._steps = index
        yield (step, result)

    def _on_step_processed(self, processed_args: Tuple[WorkflowStep, numpy.ndarray]):
        """
        Function called when a workflow step is processed
        """
        if self._sweep_step is not None:
            self._sweep_step = self._sweep_step + 1
        if self._steps < self._max_step_run:
            # should not be able to get here
            raise RuntimeError("Should not be able to run steps before current step")
        step, result = processed_args

        # Update progress
        self.view.set_progress_bar(self._steps)
        if self._steps == self._max_step_run:
            # most recent step is being reran
            self._number_times_run = self._number_times_run + 1

        if self.param_sweep_widget:
            self.param_sweep_widget.set_progress_bar(self._sweep_step)

        # Hide all layers except for most recent
        for layer in self.viewer.get_layers()[:-1]:
            layer.visible = False

        # most recent step is being ran
        if self._steps > self._max_step_run:
            # enable button for next step
            self._max_step_run = self._steps
            if self._steps < len(self.model.active_workflow.workflow_definition.steps) - 1:
                # enable next step button if not on the last step
                self._view._get_workflow_step_widgets()[self._steps + 1].enable_button()
            # disable button for previous step
            if self._steps - 1 >= 0:
                self._view._get_workflow_step_widgets()[self._steps - 1].disable_button()
            # reset rerun counter
            self._number_times_run = 0

        active_layer = self.viewer.get_active_layer()[0]
        if self._current_params:
            if self._number_times_run == 0:
                self.viewer.add_image_layer(result, name=f"{step.step_number}: {step.name} | {self._current_params}")
            else:
                self.viewer.add_image_layer(
                    result, name=f"{step.step_number}.{self._number_times_run}: {step.name} | {self._current_params}"
                )
        else:
            # Add step result layer
            if self._number_times_run == 0:
                self.viewer.add_image_layer(result, name=f"{step.step_number}: {step.name}")
            else:
                self.viewer.add_image_layer(result, name=f"{step.step_number}.{self._number_times_run}: {step.name}")

        self.viewer.set_active_layer(active_layer)

    def _on_step_processed_all(self, processed_args: Tuple[WorkflowStep, numpy.ndarray]):
        """
        function called when a step from run_all is processed
        """
        #
        step, result = processed_args

        # Update progress
        self.view.increment_progress_bar()

        # Add step result layer
        self.viewer.add_image_layer(result, name=f"{step.step_number}: {step.name}")

        # Hide all layers except for most recent
        for layer in self.viewer.get_layers()[:-1]:
            layer.visible = False

    def _on_run_all_started(self):
        """
        function called when run_all is started
        """
        self._run_lock = True
        self._view.set_run_all_in_progress()

    def _on_sweep_started(self):
        """
        Function called when a sweep is started
        """
        self.param_sweep_widget.set_run_in_progress()
        self._run_lock = True

    def _on_run_all_finished(self):
        """
        function called when run_all is finished
        """
        self._view.reset_run_all()
        self._run_lock = False

    def _on_run_step_finished(self):
        """
        function called by worker when run_step is finished
        """
        self._view.reset_run_step()
        self._run_lock = False

    def on_sweep_finished(self):
        """
        function called by worker when a sweep is finished
        """
        self.param_sweep_widget.set_run_finished()
        self._run_lock = False

    def open_sweep_ui(self, params, step_number):
        """
        Open the UI for sweeps
        """
        dlg = ParamSweepWidget(params, step_number, self)
        dlg.exec()

    def run_lock(self):
        """
        get the status of the run_lock for workflow step executions
        """
        return self._run_lock

    def warn_box(self, message: str, title: str, one_option=False):
        """
        Display a warning box
        """
        box = QMessageBox()
        box.setText(message)
        box.setWindowTitle(title)
        box.setStyleSheet(get_stylesheet(self.viewer.get_theme()))
        if one_option:
            box.setStandardButtons(QMessageBox.Cancel)
        else:
            box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        return box.exec_()
