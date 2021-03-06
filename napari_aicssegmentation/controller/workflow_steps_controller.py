from napari_aicssegmentation.view._interfaces import IWorkflowStepsView
from napari_aicssegmentation.core._interfaces import IApplication
from napari_aicssegmentation.controller._interfaces import IWorkflowStepsController
from napari_aicssegmentation.core.controller import Controller


class WorkflowStepsController(Controller, IWorkflowStepsController):
    def __init__(self, application: IApplication, view: IWorkflowStepsView):
        super().__init__(application)
        self._view = view

    def navigate_back(self):
        self.router.workflow_selection()
    