from napari_aicssegmentation.util.debug_utils import debug_class
from napari_aicssegmentation.model.segmenter_model import SegmenterModel
from napari_aicssegmentation.view.workflow_select_view import WorkflowSelectView
from napari_aicssegmentation.core._interfaces import IApplication
from napari_aicssegmentation.controller._interfaces import IWorkflowSelectController
from napari_aicssegmentation.core.controller import Controller


@debug_class
class WorkflowSelectController(Controller, IWorkflowSelectController):
    def __init__(self, application: IApplication):
        super().__init__(application)
        self._view = WorkflowSelectView(self)

    @property
    def view(self) -> WorkflowSelectView:
        return self._view

    @property
    def model(self) -> SegmenterModel:
        return self.state.segmenter_model

    def index(self):
        self.load_view(self._view)
        self.model.channel_list = ["brightfield", "405nm", "488nm"]  # TODO read channels from image
        self.model.workflows = ["SEC61B", "LMNB1", "ACTN1"]  # TODO load workflow objects from Segmenter workflow engine
        self._view.load_model(self.model)

    def select_channel(self, channel_index: int):
        self.model.active_channel = channel_index

    def select_workflow(self, workflow: str):
        self.model.active_workflow = workflow

    def navigate_back(self):
        self.router.mpp()

    def navigate_next(self):
        self.router.workflow_steps()
