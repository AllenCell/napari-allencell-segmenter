from pathlib import Path
import numpy as np

from unittest import mock
from unittest.mock import MagicMock, Mock, create_autospec
from napari_allencell_segmenter.view.batch_processing_view import BatchProcessingView, IBatchProcessingController
from aicssegmentation.workflow import WorkflowEngine


class TestBatchProcessingView:
    def setup_method(self):
        self._mock_controller: MagicMock = create_autospec(IBatchProcessingController)
        self._view = BatchProcessingView(self._mock_controller)
        self._view.load()

    def test_update_button(self):
        self._view.update_button(enabled=True)
        assert self._view.btn_run_batch.isEnabled()
        self._view.update_button(enabled=False)
        assert not self._view.btn_run_batch.isEnabled()

    def test_set_run_batch_in_progress(self):
        self._view.set_run_batch_in_progress()
        assert self._view.progress_bar.isVisibleTo(self._view)

    def test_reset_run_batch(self):
        self._view.set_run_batch_in_progress()
        self._view.reset_run_batch()
        assert not self._view.progress_bar.isVisibleTo(self._view)

    def test_run_batch(self):
        self._view.btn_run_batch.clicked.emit()
        self._mock_controller.run_batch.assert_called()

    def test_cancel_run_batch(self):
        self._view.set_run_batch_in_progress()
        self._view.btn_run_batch.clicked.emit()
        self._mock_controller.cancel_run_batch.assert_called()

    def test_set_progress(self):
        self._view.set_progress(45)
        assert self._view.progress_bar.value() == 45

    def test_update_channel(self):
        self._view.field_channel.textChanged.emit("1")
        self._mock_controller.update_batch_parameters.assert_called()

    def test_update_workflow_config(self):
        self._view.field_workflow_config.file_selected.emit("/some/file.json")
        self._mock_controller.update_batch_parameters.assert_called()

    def test_update_input_dir(self):
        self._view.field_input_dir.file_selected.emit("/some/dir")
        self._mock_controller.update_batch_parameters.assert_called()

    def test_update_output_dir(self):
        self._view.field_output_dir.file_selected.emit("/some/dir")
        self._mock_controller.update_batch_parameters.assert_called()
