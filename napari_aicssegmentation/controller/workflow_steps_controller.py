from typing import Dict, List

from napari_aicssegmentation.model.segmenter_model import SegmenterModel
from aicssegmentation.workflow import WorkflowEngine
from napari_aicssegmentation.util.debug_utils import debug_class
from napari_aicssegmentation.view.workflow_steps_view import WorkflowStepsView
from napari_aicssegmentation.core._interfaces import IApplication
from napari_aicssegmentation.controller._interfaces import IWorkflowStepsController
from napari_aicssegmentation.core.controller import Controller


@debug_class
class WorkflowStepsController(Controller, IWorkflowStepsController):
    def __init__(self, application: IApplication, workflow_engine: WorkflowEngine):
        super().__init__(application)
        if workflow_engine is None:
            raise ValueError("workflow_engine")
        self._view = WorkflowStepsView(self)

    @property
    def view(self):
        return self._view

    @property
    def model(self) -> SegmenterModel:
        return self.state.segmenter_model

    def index(self):
        self.load_view(self._view)
        self._view.load_model(self.model)

    def close_workflow(self):
        self.model.reset()
        self.router.workflow_selection()

    def run_all(self, parameter_inputs: List[Dict[str, List]]):
        """
        Run all steps in the active workflow.

        parameter_inputs List[Dict]/Dict: Each dictionary has the same shape as a WorkflowStep.parameter_defaults
        dictionary, but with the parameter values obtained from the UI instead of default values.
        """
        step = 0
        while not self.model.active_workflow.is_done():
            # Getting info about the next step that will be run
            step_run = self.model.active_workflow.get_next_step()
            # Run step and add result image (layer names are 1-indexed, steps are 0-indexed)
            self.viewer.add_image(
                self.model.active_workflow.execute_next(parameter_inputs[step]),
                name=f"{str(step + 1)}. {step_run.name}",
            )
            step += 1
            # Hide all layers except for most recent
            for layer in self.viewer.layers[:-1]:
                if layer.visible:
                    layer.visible = False
