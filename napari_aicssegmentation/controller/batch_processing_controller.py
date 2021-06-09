from typing import Union

from aicssegmentation.workflow import WorkflowEngine, BatchWorkflow
from napari_aicssegmentation.core._interfaces import IApplication
from napari_aicssegmentation.core.controller import Controller
from napari_aicssegmentation.view.batch_processing_view import BatchProcessingView
from ._interfaces import IBatchProcessingController
from pathlib import Path
from napari.qt.threading import create_worker

import warnings


class BatchProcessingController(Controller, IBatchProcessingController):
    def __init__(self, application: IApplication, workflow_engine: WorkflowEngine):
        super().__init__(application)
        if workflow_engine is None:
            raise ValueError("workflow_engine")
        self._workflow_engine = workflow_engine
        self._view = BatchProcessingView(self)

        # Should these go into a model?
        self._input_folder: Path = None
        self._output_folder = None
        self._selected_index = 0  # defaults to 0 on UI
        self._workflow_config = None

    def index(self):
        self.load_view(self._view)

    def run_batch(self):
        """
        Run the batch workflow

        Inputs:
            None

        Outputs:
            None
        """
        workflow = self.get_batch_workflow()
        workflow.process_all()
        self._view.open_completion_dialog(self._output_folder)

    # def run_batch_async(self):
    #     """
    #     Async call for run_batch()
    #
    #     Inputs:
    #         None
    #
    #     Outputs:
    #         None
    #     """
    # with warnings.catch_warnings():
    #     warnings.simplefilter("ignore")
    #     workflow = self.get_batch_workflow()
    #     workflow.process_all()

    def ready_to_process(self) -> bool:
        """
        Check to see if the batch processing is ready to start (user has provided all needed parameters to run a batch workflow)

        Inputs:
            None

        Outputs:
            (Bool): True if ready to start batch workflow, False if not
        """
        if not self._workflow_config:
            return False
        elif not self._input_folder:
            return False
        elif not self._output_folder:
            return False
        else:
            return True

    def select_config(self, selected_config: Union[str, Path]):
        """
        Select a config file

        Inputs:
            None

        Outputs:
            None
        """
        selected_config = Path(selected_config)

        if not selected_config.exists():
            raise ValueError("Invalid config file path received from FileDialog.")
        self._workflow_config = selected_config

        # check enable button
        if self.ready_to_process():
            self._view.update_button(enabled=True)

    def select_input_folder(self, input_folder: Union[str, Path]):
        """
        Select a input folder

        Inputs:
            None

        Outputs:
            None
        """
        input_folder = Path(input_folder)

        if not input_folder.exists():
            raise ValueError("Invalid input folder path received from FileDialog.")

        self._input_folder = input_folder

        # check enable button
        if self.ready_to_process():
            self._view.update_button(enabled=True)

    def select_output_folder(self, output_folder: Union[str, Path]):
        """
        Select a output folder

        Inputs:
            None

        Outputs:
            None
        """
        output_folder = Path(output_folder)
        if not output_folder.exists():
            raise ValueError("Invalid output folder path received from FileDialog.")
        self._output_folder = output_folder
        # check enable button
        if self.ready_to_process():
            self._view.update_button(enabled=True)

    def get_batch_workflow(self) -> BatchWorkflow:
        """
        Get an executable batch workflow with the UI provided parameters

        Inputs:
            None

        Outputs:
            (BatchWorkflow): Executable batch workflow set up with UI provided parameters.
        """
        # Checking to see if values were correctly recieved from the UI
        if not self.ready_to_process():
            raise ValueError("Error in getting values from UI")

        return self._workflow_engine.get_executable_batch_workflow_from_config_file(
            self._workflow_config, self._input_folder, self._output_folder, channel_index=self._selected_index
        )
