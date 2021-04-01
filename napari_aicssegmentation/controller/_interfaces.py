from abc import ABC, abstractmethod


class IWorkflowSelectController(ABC):
    @abstractmethod
    def index(self):
        pass

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
    def select_channel(self, channel_name: str):
        """
        Handle user selection of channel
        Inputs
            channel_name: name of the channel to select
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
    def index(self):
        pass

    @abstractmethod
    def navigate_back(self):
        pass
