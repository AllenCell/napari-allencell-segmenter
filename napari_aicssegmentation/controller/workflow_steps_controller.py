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
        parameter_inputs is a list of dictionaries, one dictionary (or None if no parameters) 
        for each step. Each dictionary has the same shape as a WorkflowStep.parameter_defaults
        dictionary, but with the parameter values obtained from the UI instead of default values.
        """

        workflow = self.model.active_workflow

        # This is equivalent to running workflow.execute_all(), but with non-default params
        workflow.reset()
        step = 0
        while not workflow.is_done():
            workflow.execute_next(parameter_inputs[step])
            step += 1
        result = workflow.get_most_recent_result()

        self.viewer.add_image(result, name=f"Result for workflow {self.model.active_workflow.workflow_definition.name}")

        # hide all layers except most recent layer
        for layer in self.viewer.layers[:-1]:
            layer.visible = False
