from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List

from aicssegmentation.workflow.workflow_step import WorkflowStep
from napari_allencell_segmenter.model.channel import Channel


class IWorkflowSelectController(ABC):
    @abstractmethod
    def select_layer(self, layer_name: str):
        """
        Handle user selection of a layer
        Inputs
            layer_name: name of the layer to select
        """
        pass

    @abstractmethod
    def unselect_layer(self):
        """
        Handle user resetting layer selection
        """
        pass

    @abstractmethod
    def select_channel(self, channel: Channel):
        """
        Handle user selection of channel
        Inputs
            channel: the channel to select
        """
        pass

    @abstractmethod
    def unselect_channel(self):
        """
        Handle user resetting channel selection
        """
        pass

    @abstractmethod
    def select_workflow(self, workflow: str):
        """
        Handle user selection of workflow
        Inputs
            workflow: name of the workflow to select
        """
        pass


class IWorkflowStepsController(ABC):
    @abstractmethod
    def close_workflow(self):
        """
        Handle user closing a workflow
        """
        pass

    @abstractmethod
    def run_all(self, parameter_inputs: List[Dict[str, List]]):
        """
        Run all steps in the active workflow.

        inputs
            parameter_inputs (List[Dict]): Each dictionary has the same shape as a WorkflowStep.parameter_values
            dictionary, but with the parameter values obtained from the UI instead of default values.
        """
        pass

    @abstractmethod
    def cancel_run_all(self):
        """
        Cancel any ongoing full workflow run
        """
        pass

    @abstractmethod
    def save_workflow(self, steps: List[WorkflowStep], output_file_path: str):
        """
        Save the current workflow as a configuration file

        inputs
            steps (List[WorkflowStep]): List of Workflow steps to save as a Workflow
            output_file_path (str): path to save the workflow file to
        """
        pass


class IBatchProcessingController(ABC):
    @abstractmethod
    def run_batch(self):
        """
        Run the batch workflow
        """
        pass

    @abstractmethod
    def cancel_run_batch(self):
        """
        Cancel the ongoing batch workflow run
        """
        pass

    @abstractmethod
    def update_batch_parameters(self, workflow_config: Path, channel_index: int, input_dir: Path, output_dir: Path):
        """
        Set / update batch processing parameters
        """
        pass
