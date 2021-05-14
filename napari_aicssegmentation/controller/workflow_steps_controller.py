import numpy
import warnings

from typing import Dict, Generator, List, Tuple
from napari.qt.threading import create_worker, GeneratorWorker
from aicssegmentation.workflow import WorkflowEngine, WorkflowStep
from napari_aicssegmentation.view.workflow_steps_view import WorkflowStepsView
from napari_aicssegmentation.core._interfaces import IApplication
from napari_aicssegmentation.controller._interfaces import IWorkflowStepsController
from napari_aicssegmentation.core.controller import Controller
from napari_aicssegmentation.model.segmenter_model import SegmenterModel
from napari_aicssegmentation.util.debug_utils import debug_func

class WorkflowStepsController(Controller, IWorkflowStepsController):
    _worker: GeneratorWorker = None

    def __init__(self, application: IApplication, workflow_engine: WorkflowEngine):
        super().__init__(application)
        if workflow_engine is None:
            raise ValueError("workflow_engine")
        self._view = WorkflowStepsView(self)
        self._run_lock = False # lock to avoid triggering multiple segmentation / step runs at the same time

    @property
    def view(self):
        return self._view

    @property
    def model(self) -> SegmenterModel:
        return self.state.segmenter_model

    def index(self):
        self.load_view(self._view, self.model)

    def close_workflow(self):
        self.model.reset()
        self.router.workflow_selection()

    # def run_all(self, parameter_inputs: List[Dict[str, List]]):
    #     """
    #     Run all steps in the active workflow.

    #     parameter_inputs List[Dict]: Each dictionary has the same shape as a WorkflowStep.parameter_defaults
    #     dictionary, but with the parameter values obtained from the UI instead of default values.
    #     """
    #     self.model.active_workflow.reset()

    #     step = 0
    #     while not self.model.active_workflow.is_done():
    #         # Getting info about the next step that will be run
    #         step_run = self.model.active_workflow.get_next_step()
    #         # Run step and add result image (layer names are 1-indexed, steps are 0-indexed)
    #         self.viewer.add_image(
    #             self.model.active_workflow.execute_next(parameter_inputs[step]),
    #             name=f"{str(step + 1)}. {step_run.name}",
    #         )
    #         step += 1
    #         self.view.progress_bar.setValue(step)
    #         # Hide all layers except for most recent
    #         for layer in self.viewer.layers[:-1]:
    #             if layer.visible:
    #                 layer.visible = False

    # @debug_func
    # def run_all(self, parameter_inputs: List[Dict[str, List]]):
    #     if not self._run_lock:
    #         self._run_lock = True
    #         self._worker = create_worker(self._run_all_async, parameter_inputs)
    #         self._worker.started.connect(self._on_run_all_started)  
    #         self._worker.aborted.connect(self._on_run_all_aborted)          
    #         self._worker.finished.connect(self._on_run_all_finished)
    #         #self._worker.yielded.connect(self._on_step_processed)
    #         self._worker.start()     
    @debug_func           
    def run_all(self, parameter_inputs: List[Dict[str, List]]):
        """
        Run all steps in the active workflow.
        parameter_inputs List[Dict]: Each dictionary has the same shape as a WorkflowStep.parameter_defaults
        dictionary, but with the parameter values obtained from the UI instead of default values.
        """
        if not self._run_lock:
            self._worker: GeneratorWorker = create_worker(self._run_all_async, parameter_inputs)
            self._worker.yielded.connect(self._on_step_processed)
            self._worker.started.connect(self._on_run_all_started) 
            self._worker.finished.connect(self._on_run_all_finished)
            self._worker.aborted.connect(self._on_run_all_aborted)
            self._worker.start()      

    def cancel_run_all(self):
        if self._worker is not None:
            self._worker.quit()

    def _run_all_async(self, parameter_inputs: List[Dict[str, List]]) -> Generator[Tuple[WorkflowStep, numpy.ndarray], None, None]:
        self.model.active_workflow.reset()

        with warnings.catch_warnings():
            warnings.simplefilter("ignore") # avoid spamming the UI with warnings from segmenter
            
            i = 0
            while not self.model.active_workflow.is_done():            
                step = self.model.active_workflow.get_next_step()
                result = self.model.active_workflow.execute_next(parameter_inputs[i])
                i = i + 1
                yield (step, result)

    def _on_step_processed(self, processed_args: Tuple[WorkflowStep, numpy.ndarray]):
        step, result = processed_args

        # Update progress
        self.view.progress_bar.setValue(self.view.progress_bar.value() + 1)

        # Add step result layer
        self.add_layer(result, name=f"{step.step_number}. {step.name}")

        # Hide all layers except for most recent
        for layer in self.get_layers()[:-1]:
            layer.visible = False
    
    def _on_run_all_started(self):
        self._run_lock = True
        self._view.set_run_all_in_progress()
    
    def _on_run_all_aborted(self):
        # TODO reset progress bar?
        self._view.set_run_all_available()
        self._run_lock = False
    
    def _on_run_all_finished(self):
        self._view.set_run_all_available()
        self._run_lock = False
    