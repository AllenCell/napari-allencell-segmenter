from aicssegmentation.workflow import WorkflowEngine, BatchWorkflow
from napari_aicssegmentation.core._interfaces import IApplication
from napari_aicssegmentation.core.controller import Controller
from napari_aicssegmentation.view.batch_processing_view import BatchProcessingView
from ._interfaces import IBatchProcessingController
from pathlib import Path
from napari.qt.threading import create_worker, GeneratorWorker

import warnings


class BatchProcessingController(Controller, IBatchProcessingController):
    def __init__(self, application: IApplication, workflow_engine: WorkflowEngine):
        super().__init__(application)
        if workflow_engine is None:
            raise ValueError("workflow_engine")
        self._workflow_engine = workflow_engine
        self._view = BatchProcessingView(self)

        # Should these go into a model?
        self.input_folder: Path = None
        self.output_folder = None
        self.selected_index = None
        self.workflow_config = None

    def index(self):
        self.load_view(self._view)

    def run_batch(self):
        # workflow = self.get_batch_workflow()
        # workflow.process_all()
        self.worker = create_worker(self.run_batch_async)
        self.worker.start()
        self._view.open_completion_dialog(self.output_folder)

    def run_batch_async(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            workflow = self.get_batch_workflow()
            workflow.process_all()

    def ready_to_process(self):
        if not self.workflow_config:
            return False
        elif not self.input_folder:
            return False
        elif not self.output_folder:
            return False
        else:
            return True

    def select_config(self, selected_config):
        self.workflow_config = Path(selected_config)
        if self.ready_to_process():
            self._view.update_button(enabled=True)

    def select_input_folder(self, input_folder):
        self.input_folder = Path(input_folder)
        if self.ready_to_process():
            self._view.update_button(enabled=True)

    def select_output_folder(self, output_folder):
        self.output_folder = Path(output_folder)
        if self.ready_to_process():
            self._view.update_button(enabled=True)

    def get_batch_workflow(self):
        return self._workflow_engine.get_executable_batch_workflow_from_config_file(
            self.workflow_config, self.input_folder, self.output_folder, channel_index=self.selected_index
        )
