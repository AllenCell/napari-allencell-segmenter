import warnings

from pathlib import Path
from napari._qt.qthreading import GeneratorWorker
from napari.qt.threading import create_worker
from typing import Generator, Tuple
from aicssegmentation.workflow import WorkflowEngine, BatchWorkflow
from napari_allencell_segmenter.core._interfaces import IApplication
from napari_allencell_segmenter.core.controller import Controller
from napari_allencell_segmenter.view.batch_processing_view import BatchProcessingView
from napari_allencell_segmenter.widgets.batch_complete_dialog import BatchCompleteDialog
from ._interfaces import IBatchProcessingController


class BatchProcessingController(Controller, IBatchProcessingController):
    _worker: GeneratorWorker = None
    _batch_workflow: BatchWorkflow

    def __init__(self, application: IApplication, workflow_engine: WorkflowEngine):
        super().__init__(application)
        if workflow_engine is None:
            raise ValueError("workflow_engine")
        self._workflow_engine = workflow_engine
        self._view = BatchProcessingView(self)

        self._input_folder = None
        self._output_folder = None
        self._channel_index = None
        self._workflow_config = None

        self._run_lock = False  # lock to avoid triggering multiple runs at the same time
        self._canceled = False

    @property
    def view(self):
        return self._view

    def index(self):
        self.load_view(self._view)

    def run_batch(self):
        if not self._run_lock:
            self._worker: GeneratorWorker = create_worker(self._run_batch_async)
            self._worker.yielded.connect(self._on_step_processed)
            self._worker.started.connect(self._on_run_batch_started)
            self._worker.aborted.connect(self._on_run_batch_aborted)
            self._worker.finished.connect(self._on_run_batch_finished)
            self._worker.start()

    def cancel_run_batch(self):
        if self._worker is not None:
            self._worker.quit()

    def update_batch_parameters(self, workflow_config: Path, channel_index: int, input_dir: Path, output_dir: Path):
        self._workflow_config = workflow_config
        self._channel_index = channel_index
        self._input_folder = input_dir
        self._output_folder = output_dir

        ready = self._ready_to_process()
        self._view.update_button(ready)

    def _ready_to_process(self) -> bool:
        """
        Check to see if the batch processing is ready to start
        (user has provided all needed parameters to run a batch workflow)

        Outputs:
            (Bool): True if ready to start batch workflow, False if not
        """
        if self._workflow_config is None:
            return False
        if self._input_folder is None:
            return False
        if self._output_folder is None:
            return False
        if self._channel_index is None:
            return False

        return True

    def _run_batch_async(self) -> Generator[Tuple[int, int], None, None]:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")

            batch_workflow = self._workflow_engine.get_executable_batch_workflow_from_config_file(
                self._workflow_config, self._input_folder, self._output_folder, channel_index=self._channel_index
            )

            while not batch_workflow.is_done():
                batch_workflow.execute_next()
                yield batch_workflow.processed_files, batch_workflow.total_files

            batch_workflow.write_log_file_summary()

    def _on_step_processed(self, processed_args: Tuple[int, int]):
        processed_files, total_files = processed_args

        # Update progress
        progress = 100 * processed_files // total_files
        self._view.set_progress(progress)

    def _on_run_batch_started(self):
        self._run_lock = True
        self._view.set_run_batch_in_progress()

    def _on_run_batch_finished(self):
        self._run_lock = False

        if not self._canceled:
            # Open completion dialog
            # TODO: this should be moved back to batch_processing_view, but testing QDialog.exec_()
            # is tricky
            completion_dlg = BatchCompleteDialog(self._output_folder)
            completion_dlg.exec_()

        self._view.reset_run_batch()
        self._canceled = False

    def _on_run_batch_aborted(self):
        self._canceled = True
