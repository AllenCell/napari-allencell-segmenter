from napari_aicssegmentation.util.debug_utils import debug_class
from napari_aicssegmentation.view.workflow_steps_view import WorkflowStepsView
from napari_aicssegmentation.core._interfaces import IApplication
from napari_aicssegmentation.controller._interfaces import IWorkflowStepsController
from napari_aicssegmentation.core.controller import Controller

from aicssegmentation.workflow import WorkflowEngine


@debug_class
class WorkflowStepsController(Controller, IWorkflowStepsController):
    def __init__(self, application: IApplication, workflow_name: str):
        super().__init__(application)
        self.engine = WorkflowEngine(str)
        self._view = WorkflowStepsView(self)


    @property
    def view(self):
        return self._view

    @property
    def model(self):
        return self.state.segmenter_model

    def index(self):
        self.load_view(self._view)
        self._view.load_model(self.model)

    def navigate_back(self):
        self.router.workflow_selection()
