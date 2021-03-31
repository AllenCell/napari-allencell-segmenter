from abc import ABC, abstractmethod


class IWorkflowSelectController(ABC):
    @abstractmethod
    def index(self):
        pass

    @abstractmethod
    def select_layer(self, layer_index: int):
        pass

    @abstractmethod
    def select_channel(self, channel_index: int):
        pass

    @abstractmethod
    def select_workflow(self, workflow: str):
        pass

    @abstractmethod
    def navigate_next(self):
        pass


class IWorkflowStepsController(ABC):
    @abstractmethod
    def index(self):
        pass

    @abstractmethod
    def navigate_back(self):
        pass
