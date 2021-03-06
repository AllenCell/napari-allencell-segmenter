from napari_aicssegmentation.view._interfaces import IWorkflowSelectView
from napari_aicssegmentation.core._interfaces import IApplication
from napari_aicssegmentation.controller._interfaces import IWorkflowSelectController
from napari_aicssegmentation.core.controller import Controller


class WorkflowSelectController(Controller, IWorkflowSelectController):
    def __init__(self, application: IApplication, view: IWorkflowSelectView):
        super().__init__(application)
        self._view = view

    def navigate_back(self):
        self.router.mpp()

    def navigate_next(self):
        self.router.workflow_steps()
    