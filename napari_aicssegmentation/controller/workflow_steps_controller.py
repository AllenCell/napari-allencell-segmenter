from napari_aicssegmentation.util.debug_utils import debug_class
from napari_aicssegmentation.view.workflow_steps_view import WorkflowStepsView
from napari_aicssegmentation.core._interfaces import IApplication
from napari_aicssegmentation.controller._interfaces import IWorkflowStepsController
from napari_aicssegmentation.core.controller import Controller
from napari_aicssegmentation.model.segmenter_model import SegmenterModel

@debug_class
class WorkflowStepsController(Controller, IWorkflowStepsController):
    def __init__(self, application: IApplication):
        super().__init__(application)
        self._view = WorkflowStepsView(self)
        self._model: SegmenterModel = self.state.segmenter_model        
    
    def index(self):
        self.load_view(self._view)
        self._view.load_model(self._model)

    def navigate_back(self):
        self.router.workflow_selection()
    