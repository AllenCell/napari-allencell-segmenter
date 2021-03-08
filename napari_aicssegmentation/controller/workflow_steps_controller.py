from napari_aicssegmentation.view.workflow_steps_view import WorkflowStepsView
from napari_aicssegmentation.core._interfaces import IApplication
from napari_aicssegmentation.controller._interfaces import IWorkflowStepsController
from napari_aicssegmentation.core.controller import Controller


class WorkflowStepsController(Controller, IWorkflowStepsController):
    def __init__(self, application: IApplication):
        super().__init__(application)
    
    def index(self):
        self.load_view(WorkflowStepsView(self))

    def navigate_back(self):
        self.router.workflow_selection()
    