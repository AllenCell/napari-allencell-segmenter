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
        self.load_view(self._view, self.model)

    def close_workflow(self):
        self.model.reset()
        self.router.workflow_selection()

    def run_all(self):
        result = self.model.active_workflow.execute_all()
        self.viewer.add_image(result, name=f"Result for workflow {self.model.active_workflow.name}")

        # hide all layers except most recent layer
        for layer in self.viewer.layers[:-1]:
            layer.visible = False
