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

    def run_all_and_add_image(self, parameters):
        """ parameters is list of dictionaries of parameters, one dictionary for each step"""
        workflow = self.model.active_workflow
        workflow.reset()

        step = 0
        while not workflow.is_done():
            workflow.execute_next(parameters[step])
            step += 1

        result = workflow.get_most_recent_result()

        self.viewer.add_image(result, name="Result for workflow " + self.model.active_workflow.workflow_definition.name)
