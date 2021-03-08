from napari_aicssegmentation.view.workflow_select_view import WorkflowSelectView
from napari_aicssegmentation.core._interfaces import IApplication
from napari_aicssegmentation.controller._interfaces import IWorkflowSelectController
from napari_aicssegmentation.core.controller import Controller


class WorkflowSelectController(Controller, IWorkflowSelectController):
    def __init__(self, application: IApplication):
        super().__init__(application)
    
    def index(self):
        self.load_view(WorkflowSelectView(self))

    def select_channel(self, channel_index: int):
        pass

    def navigate_back(self):
        self.router.mpp()

    def navigate_next(self):
        self.router.workflow_steps()
    