from abc import ABC, abstractmethod

# TODO These interfaces are not needed as of now - 
# reminder to remove if Controller interfaces end up unnecessary when models get added to the mix
class IMppController(ABC):
    @abstractmethod
    def run_gaussian_blur(self):
        pass

    @abstractmethod
    def navigate_next(self):
        pass

class IWorkflowSelectController(ABC):
    @abstractmethod
    def navigate_back(self):
        pass

    @abstractmethod
    def navigate_next(self):
        pass    

class IWorkflowStepsController(ABC):
    @abstractmethod
    def navigate_back(self):
        pass    