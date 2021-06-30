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


class WorkflowStepsController(Controller, IWorkflowStepsController):
    _worker: GeneratorWorker = None

    def __init__(self, application: IApplication, workflow_engine: WorkflowEngine):
        super().__init__(application)
        if workflow_engine is None:
            raise ValueError("workflow_engine")
        self._workflow_engine = workflow_engine
        self._view = WorkflowStepsView(self)
        self._run_lock = False  # lock to avoid triggering multiple segmentation / step runs at the same time

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
            self._worker.yielded.connect(self._on_step_processed)
            self._worker.started.connect(self._on_run_all_started)
            self._worker.finished.connect(self._on_run_all_finished)
            self._worker.start()

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

    def _on_step_processed(self, processed_args: Tuple[WorkflowStep, numpy.ndarray]):
        step, result = processed_args

        # Update progress
        self.view.increment_progress_bar()

        # Add step result layer
        self.viewer.add_image_layer(result, name=f"{step.step_number}. {step.name}")

        # Hide all layers except for most recent
        for layer in self.viewer.get_layers()[:-1]:
            layer.visible = False

    def _on_run_all_started(self):
        self._run_lock = True
        self._view.set_run_all_in_progress()

    def _on_run_all_finished(self):
        self._view.reset_run_all()
        self._run_lock = False
