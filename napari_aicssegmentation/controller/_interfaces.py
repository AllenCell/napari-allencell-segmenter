from abc import ABC, abstractmethod
from typing import Dict, List
from napari_aicssegmentation.model.channel import Channel


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
        pass
