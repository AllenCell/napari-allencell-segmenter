import numpy
import warnings

from pathlib import Path
from typing import Dict, Generator, List, Tuple
from napari.qt.threading import create_worker, GeneratorWorker
from aicssegmentation.workflow import WorkflowEngine, WorkflowStep, WorkflowDefinition
from napari_allencell_segmenter.view.workflow_steps_view import WorkflowStepsView
from napari_allencell_segmenter.core._interfaces import IApplication
from napari_allencell_segmenter.controller._interfaces import IWorkflowStepsController
from napari_allencell_segmenter.core.controller import Controller
from napari_allencell_segmenter.model.segmenter_model import SegmenterModel

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
        #TODO package this differently
        self._current_params = None

    @property
    def view(self):
        return self._view

    @property
    def model(self) -> SegmenterModel:
        return self.state.segmenter_model

    def index(self):
        self.load_view(self._view, self.model)

    def save_workflow(self, steps: List[WorkflowStep], output_file_path: str):
        # add .json extension if not present
        if not output_file_path.lower().endswith(".json"):
            output_file_path += ".json"
        save_path = Path(output_file_path)
        workflow_def = WorkflowDefinition(save_path.name, steps)
        self._workflow_engine.save_workflow_definition(workflow_def, save_path)

    def close_workflow(self):
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
        if not self._run_lock:
            self._worker: GeneratorWorker = create_worker(self._run_next_step_async, parameter_inputs)
            self._worker.yielded.connect(self._on_step_processed)
            self._worker.started.connect(self._on_run_all_started)
            self._worker.finished.connect(self._on_run_all_finished)
            self._worker.start()

    def run_step(self, i: int, parameter_inputs):
        if not self._run_lock:
            self._worker: GeneratorWorker = create_worker(self._run_step_async, i, parameter_inputs)
            self._worker.yielded.connect(self._on_step_processed)
            self._worker.started.connect(self._on_run_all_started)
            self._worker.finished.connect(self._on_run_step_finished)
            self._worker.start()

    def run_step_sweep(self, i: int, parameter_inputs):
        if not self._run_lock:
            if parameter_inputs:
                parameter_inputs_2, length = self._parse_inputs(copy.deepcopy(parameter_inputs))
                self._worker: GeneratorWorker = create_worker(self._run_step_sweep, i, length, parameter_inputs, parameter_inputs_2)
                self._worker.yielded.connect(self._on_step_processed)
                self._worker.started.connect(self._on_run_all_started)
                self._worker.finished.connect(self._on_run_step_finished)
                self._worker.start()

    def _run_step_sweep(self, index, length, param_original, param_sweep):
        for i in range(length):
            run_dict = dict()
            #loop over sweeps
            for k, v in param_original.items():
                # loop over parameters to build dict for this iteration
                if isinstance(v, list):
                    run_list = list()
                    if len(v) == 2:
                        run_list.append(param_sweep[k][0][i])
                        run_list.append(param_sweep[k][1][i])
                    elif len(v) == 1:
                        run_list.append(param_sweep[k][0][i])
                    run_dict[k] = run_list
                else:
                    # is single entry
                    run_dict[k] = param_sweep[k][0]
            # run iteration
            step = self.model.active_workflow.workflow_definition.steps[index]
            print(f"running step {step.name} with parameters {run_dict}")
            result = self.model.active_workflow.execute_step(index, run_dict)
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

    def _parse_inputs(self, parameter_inputs):
        # test function, get sweep values from ui somehow
        if parameter_inputs:
            dict2 = dict(parameter_inputs)
        int = 1
        length = 0
        for k, v in parameter_inputs.items():
            if isinstance(v, list):
                single_item = list()
                for value in v:
                    input_text = input(f"{str(int)} param sweep range: " )
                    int = int + 1
                    inputs = input_text.split(":")
                    length = len(numpy.arange(float(inputs[0]), float(inputs[2])+float(inputs[1]), float(inputs[1])))
                    single_item.append(numpy.arange(float(inputs[0]), float(inputs[2])+float(inputs[1]), float(inputs[1])))
            else:
                input_text = input(f"{str(int)} param sweep range: ")
                int = int + 1
                inputs = input_text.split(":")
                single_item = numpy.arange(float(inputs[0]), float(inputs[2]) + float(inputs[1]), float(inputs[1]))
                length = len(single_item)
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

        step = self.model.active_workflow.workflow_definition.steps[index]
        result = self.model.active_workflow.execute_step(index, parameter_inputs)
        self._steps = index
        yield (step, result)

    def _run_sweep(self, index: int, parameter_inputs: List[Dict[str, List]]
    ) -> Generator[Tuple[WorkflowStep, numpy.ndarray], None, None]:
        step = self.model.active_workflow.workflow_definition.steps[index]
        result = self.model.active_workflow.execute_step(index, parameter_inputs)


    def _on_step_processed(self, processed_args: Tuple[WorkflowStep, numpy.ndarray]):
        if self._steps < self._max_step_run:
            # should not be able to get here
            raise RuntimeError("Should not be able to run steps before current step")
        step, result = processed_args

        # Update progress
        self.view.set_progress_bar(self._steps)
        if self._steps == self._max_step_run:
            # most recent step is being reran
            self._number_times_run = self._number_times_run + 1

        # Hide all layers except for most recent
        for layer in self.viewer.get_layers()[:-1]:
            layer.visible = False

        # most recent step is being ran
        if self._steps > self._max_step_run:
            # enable button for next step
            self._max_step_run = self._steps
            self._view._get_workflow_step_widgets()[self._steps + 1].enable_button()
            # disable button for previous step
            if self._steps - 1 >= 0:
                self._view._get_workflow_step_widgets()[self._steps - 1].disable_button()
            # reset rerun counter
            self._number_times_run = 0


        if self._current_params:
            if self._number_times_run == 0:
                self.viewer.add_image_layer(result, name=f"{step.step_number}: {step.name} | {self._current_params}")
            else:
                self.viewer.add_image_layer(result, name=f"{step.step_number}.{self._number_times_run}: {step.name} | {self._current_params}")
        else:
            # Add step result layer
            if self._number_times_run == 0:
                self.viewer.add_image_layer(result, name=f"{step.step_number}: {step.name}")
            else:
                self.viewer.add_image_layer(result, name=f"{step.step_number}.{self._number_times_run}: {step.name}")

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

    def _on_run_all_finished(self):
        self._view.reset_run_all()
        self._run_lock = False

    def _on_run_step_finished(self):
        self._view.reset_run_step()
        self._run_lock = False
