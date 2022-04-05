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


class WorkflowStepsController(Controller, IWorkflowStepsController):
    _worker: GeneratorWorker = None

    def __init__(self, application: IApplication, workflow_engine: WorkflowEngine):
        super().__init__(application)
        if workflow_engine is None:
            raise ValueError("workflow_engine")
        self._workflow_engine = workflow_engine
        self._view = WorkflowStepsView(self)
        self._run_lock = False  # lock to avoid triggering multiple segmentation / step runs at the same time
        self._steps = 0  # need this to count steps completed
        self._max_step_run: int = -1
        self._number_times_run = 0
        # TODO package this differently
        self._current_params = None
        self.param_sweep_widget = None
        self._sweep_step = None

    @property
    def view(self):
        return self._view

    @property
    def model(self) -> SegmenterModel:
        return self.state.segmenter_model

    def index(self):
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

    def close_workflow(self):
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

    def run_all(self, parameter_inputs: List[Dict[str, List]]):
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
        # # test step index
        # self.run_step(0,parameter_inputs)
        #
        # # test step by step
        # self.run_next_step(parameter_inputs)

    def run_next_step(self, parameter_inputs):
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

    def run_step(self, i: int, parameter_inputs):
        """
        Run a step in the active workflow
        i int: index of step to run in the active workflow
        parameter_inputs: Each dictionary has the same shape as a WorkflowStep.parameter_values
        dictionary, but with the parameter values obtained from the UI instead of default values.
        """
        if not self._run_lock:
            selected_layers = self.viewer.get_active_layer()
            cont = True

            step_to_run = self.model.active_workflow.workflow_definition.steps[i]
            if len(step_to_run.parent) != len(selected_layers):
                # too many or too few images selected as the input layer,
                # abort run attempt and show warning
                self.warn_box(
                    f"{step_to_run.name} requires {len(step_to_run.parent)} input images, but you have selected {len(selected_layers)} images."
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
                                f"You currently have the layer {selected_layer.name} selected in napari which will be used as the input layer. You will run this segmentation"
                                f" out of order. \nTo run the segmentation in order, please select the starting image (step 0) as the "
                                f"input layer for this step. "
                                f"\n Would you still like to continue?",
                                "Run segmentation out of order",
                            )
                        else:
                            response = self.warn_box(
                                f"You currently have the layer {selected_layer.name} selected in napari which will be used as the input layer. You will run this segmentation"
                                f" out of order. To run the segmentation in order, please select a layer that is the output of "
                                f"{i}. {self.model.active_workflow.workflow_definition.steps[step_to_run.parent[0] - 1].name}."
                                f"\n Would you like to continue?",
                                "Run segmentation out of order",
                            )
                        cont = response == 1024
                    elif not selected_layer.name[:1].isdigit():
                        if i == 0:
                            response = self.warn_box(
                                f"You currently have the layer {selected_layer.name} selected in napari which will be used as the input layer. You will run this segmentation"
                                f" out of order. \nTo run the segmentation in order, please select the starting image (step 0) as the "
                                f"input layer for this step. "
                                f"\n Would you still like to continue?",
                                "Run segmentation out of order",
                            )
                        else:
                            response = self.warn_box(
                                f"You currently have the layer {selected_layer.name} selected in napari which will be used as the input layer. You will run this segmentation"
                                f" out of order. To run the segmentation in order, please select a layer that is the output of "
                                f"{i}. {self.model.active_workflow.workflow_definition.steps[step_to_run.parent[0] - 1].name}."
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

    def run_step_sweep(self, param_sweep_widget, ui_inputs):
        """
        Run a step in the active workflow as a sweep
        i: index of step to run in the active workflow
        parameter_inputs: Each dictionary has the same shape as a WorkflowStep.parameter_values
        dictionary, but with the parameter values obtained from the UI instead of default values.
        ui_inputs List[str]: inputs for the sweep values from the sweep UI
        type str: type of sweep, either "normal" or "grid"
        """
        self.param_sweep_widget = param_sweep_widget
        i = param_sweep_widget.step_number
        parameter_inputs = param_sweep_widget.param_set

        if not self._run_lock:
            if parameter_inputs:
                parameter_inputs_2, length = self._parse_inputs(copy.deepcopy(parameter_inputs), ui_inputs)
                self._worker: GeneratorWorker = create_worker(
                    self._run_step_sweep_grid, i, length, parameter_inputs, parameter_inputs_2
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

    def _run_step_sweep(self, index, length, param_original, param_sweep):
        selected_image = self.viewer.get_active_layer()
        for i in range(length):
            run_dict = dict()
            # loop over sweeps
            for k, v in param_original.items():
                # loop over parameters to build dict for this iteration
                if isinstance(v, list):
                    run_list = list()
                    if len(v) == 2:
                        if isinstance(param_sweep[k][0], numpy.ndarray):
                            run_list.append(round(param_sweep[k][0][i], 3))
                        else:
                            run_list.append(round(param_sweep[k][0], 3))
                        if isinstance(param_sweep[k][1], numpy.ndarray):
                            run_list.append(round(param_sweep[k][1][i], 3))
                        else:
                            run_list.append(round(param_sweep[k][1], 3))
                    elif len(v) == 1:
                        if isinstance(param_sweep[k][0], numpy.ndarray):
                            run_list.append(round(param_sweep[k][0][i], 3))
                        else:
                            run_list.append(round(param_sweep[k][0], 3))
                    run_dict[k] = run_list
                else:
                    # is single entry
                    run_dict[k] = round(param_sweep[k][0], 3)
            # run iteration
            step = self.model.active_workflow.workflow_definition.steps[index]
            print(f"running step {step.name} with parameters {run_dict}")
            result = self.model.active_workflow.execute_step(index, run_dict, selected_image)
            self._steps = index
            self._current_params = run_dict
            return step, result

    def _run_step_sweep_grid(self, index, length, param_original, param_sweep):
        selected_image = self.viewer.get_active_layer()
        # either one param, or two params as a list
        if len(param_original) == 1:
            if not isinstance(list(param_original.values())[0], list):
                # There's only one param being swept
                selected_image = self.viewer.get_active_layer()
                run_dict = dict()
                for i in list(param_sweep.values())[0]:
                    run_dict[list(param_sweep.keys())[0]] = round(i, 3)
                    # run iteration
                    step = self.model.active_workflow.workflow_definition.steps[index]
                    print(f"running step {step.name} with parameters {run_dict}")
                    result = self.model.active_workflow.execute_step(index, run_dict, selected_image)
                    self._steps = index
                    self._current_params = run_dict
                    yield (step, result)
            else:
                # multiple unique params in one list
                list1 = list(param_sweep.values())[0][0]
                list2 = list(param_sweep.values())[0][1]
                if not isinstance(list1, list) and not isinstance(list1, np.ndarray):
                    list1 = [list1]
                if not isinstance(list2, list) and not isinstance(list2, np.ndarray):
                    list2 = [list2]
                for x in list1:
                    for y in list2:
                        run_dict = {list(param_original.keys())[0]: [round(x, 3), round(y, 3)]}
                        step = self.model.active_workflow.workflow_definition.steps[index]
                        print(f"running step {step.name} with parameters {run_dict}")
                        result = self.model.active_workflow.execute_step(index, run_dict, selected_image)
                        self._steps = index
                        self._current_params = run_dict
                        yield (step, result)
        else:
            # two separate params with different keys
            list1 = list(param_sweep.values())[0]
            list2 = list(param_sweep.values())[1]
            # if the function expects a nested list
            nested_list_1 = isinstance(list(param_original.values())[0], list)  # first param is a list
            nested_list_2 = isinstance(list(param_original.values())[1], list)  # second param is a list
            # shape parameters in the way that aics-segmentation expects them
            if not isinstance(list1, list) and not isinstance(list1, np.ndarray):
                list1 = [list1]
            if not isinstance(list2, list) and not isinstance(list2, np.ndarray):
                list2 = [list2]
            if not isinstance(list1[0], float) and not isinstance(list1[0], str):
                list1 = list1[0]
            if not isinstance(list2[0], float) and not isinstance(list2[0], str):
                list2 = list2[0]

            # loop through all params and sweep
            for x in list1:
                for y in list2:
                    run_dict = dict()
                    if nested_list_1:
                        x = [round(x, 3)]
                    if nested_list_2:
                        y = [round(y, 3)]
                    run_dict[list(param_original.keys())[0]] = x
                    run_dict[list(param_original.keys())[1]] = y
                    step = self.model.active_workflow.workflow_definition.steps[index]
                    print(f"running step {step.name} with parameters {run_dict}")
                    result = self.model.active_workflow.execute_step(
                        index, run_dict, selected_image=self.viewer.get_active_layer()
                    )
                    self._steps = index
                    self._current_params = run_dict
                    yield (step, result)

    def cancel_run_all(self):
        if self._worker is not None:
            self._worker.quit()

    def _disconnect_worker_events(self):
        """
        Disconnect all worker events
        """
        self._worker.started.disconnect()
        self._worker.yielded.disconnect()
        self._worker.finished.disconnect()

    def _parse_inputs(self, parameter_inputs: dict[str, Any], ui_input: List[List[str]]):
        """
        Parse inputs from the UI to create dictionaries to feed into the sweep functions.
        """
        # test function, get sweep values from ui somehow
        if parameter_inputs:
            dict2 = dict(parameter_inputs)
        i = 0
        length = 0
        for k, v in parameter_inputs.items():
            if isinstance(v, list):
                # sometimes multiple unique params are in one list
                single_item = list()
                for value in v:
                    inputs = ui_input[i]
                    i = i + 1
                    length = len(numpy.arange(float(inputs[0]), float(inputs[2]), float(inputs[1])))
                    values_to_run = numpy.arange(float(inputs[0]), float(inputs[2]), float(inputs[1]))
                    # if min=max, just fix parameter
                    if inputs[0] == inputs[2]:
                        values_to_run = numpy.append(values_to_run, float(inputs[0]))
                    elif values_to_run[len(values_to_run) - 1] + float(inputs[1]) <= float(inputs[2]):
                        values_to_run = numpy.append(
                            values_to_run, values_to_run[len(values_to_run) - 1] + float(inputs[1])
                        )
                    single_item.append(values_to_run)
            else:
                # most params are single entries in the param dictionary
                inputs = ui_input[i]
                i = i + 1
                if not isinstance(inputs, str):
                    # for typical sweep ranges
                    single_item = numpy.arange(float(inputs[0]), float(inputs[2]), float(inputs[1]))
                    length = max(len(single_item), length)
                else:
                    # for string parameters from dropdowns
                    single_item = inputs
            dict2[k] = single_item
        return dict2, length

    def _run_all_async(
        self, parameter_inputs: List[Dict[str, List]]
    ) -> Generator[Tuple[WorkflowStep, numpy.ndarray], None, None]:
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
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            step = self.model.active_workflow.get_next_step()
            result = self.model.active_workflow.execute_next(parameter_inputs[self._steps])
            self._steps = self._steps + 1
            yield (step, result)

    def _run_step_async(
        self, index: int, parameter_inputs: List[Dict[str, List]]
    ) -> Generator[Tuple[WorkflowStep, numpy.ndarray], None, None]:
        selected_image = self.viewer.get_active_layer()
        step = self.model.active_workflow.workflow_definition.steps[index]
        result = self.model.active_workflow.execute_step(index, parameter_inputs, selected_image)
        self._steps = index
        yield (step, result)

    def _on_step_processed(self, processed_args: Tuple[WorkflowStep, numpy.ndarray]):
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
        step, result = processed_args

        # Update progress
        self.view.increment_progress_bar()

        # Add step result layer
        self.viewer.add_image_layer(result, name=f"{step.step_number}: {step.name}")

        # Hide all layers except for most recent
        for layer in self.viewer.get_layers()[:-1]:
            layer.visible = False

    def _on_run_all_started(self):
        self._run_lock = True
        self._view.set_run_all_in_progress()

    def _on_run_all_step_started(self):
        self._run_lock = True
        self._view.set_run_all_in_progress()
        # disable previous step button

    def _on_sweep_started(self):
        self.param_sweep_widget.set_run_in_progress()
        self._run_lock = True

    def _on_run_all_finished(self):
        self._view.reset_run_all()
        self._run_lock = False

    def _on_run_step_finished(self):
        self._view.reset_run_step()
        self._run_lock = False

    def on_sweep_finished(self):
        self.param_sweep_widget.set_run_finished()
        self._run_lock = False

    def open_sweep_ui(self, params, step_number):
        dlg = ParamSweepWidget(params, step_number, self)
        dlg.exec()

    def run_lock(self):
        return self._run_lock

    def warn_box(self, message, title, one_option=False):
        box = QMessageBox()
        box.setText(message)
        box.setWindowTitle(title)
        box.setStyleSheet(get_stylesheet(self.viewer.get_theme()))
        if one_option:
            box.setStandardButtons(QMessageBox.Cancel)
        else:
            box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        return box.exec_()
