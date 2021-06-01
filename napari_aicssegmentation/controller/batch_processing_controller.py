from aicssegmentation.workflow import WorkflowEngine
from napari_aicssegmentation.core._interfaces import IApplication
from napari_aicssegmentation.core.controller import Controller
from napari_aicssegmentation.view.batch_processing_view import BatchProcessingView
from ._interfaces import IBatchProcessingController
from pathlib import Path


class BatchProcessingController(Controller, IBatchProcessingController):
    def __init__(self, application: IApplication, workflow_engine: WorkflowEngine):
        super().__init__(application)
        if workflow_engine is None:
            raise ValueError("workflow_engine")
        self._workflow_engine = workflow_engine
        self._view = BatchProcessingView(self)

        #Should these go into a model?
        self.input_folder: Path = None
        self.output_folder = None
        self.selected_index = None
        self.workflow_config = None


    def index(self):
        self.load_view(self._view)

    def run_batch(self):
        return super().run_batch()
