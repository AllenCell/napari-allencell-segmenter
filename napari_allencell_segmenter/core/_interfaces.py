from abc import ABC, abstractmethod, abstractproperty
from napari_allencell_segmenter.core.view_manager import ViewManager
from napari_allencell_segmenter.core.state import State
from .viewer_abstraction import ViewerAbstraction


class IRouter(ABC):
    """
    Application Router
    The router handles navigation from one view to another
    """

    @abstractmethod
    def workflow_selection(self):
        """
        Navigate to workflow selection screen
        """
        pass

    @abstractmethod
    def workflow_steps(self):
        """
        Navigate to workflow selection screen
        """
        pass

    @abstractmethod
    def batch_processing(self):
        """
        Navigate to batch processing screen
        """
        pass


class IApplication(ABC):
    """
    Main application container
    """

    @abstractproperty
    def viewer(self) -> ViewerAbstraction:
        """
        Get the Napari viewer (abstracted)
        """
        pass

    @abstractproperty
    def router(self) -> IRouter:
        """
        Get the Router
        """
        pass

    @abstractproperty
    def view_manager(self) -> ViewManager:
        """
        Get the View Manager
        """
        pass

    @abstractproperty
    def state(self) -> State:
        """
        Get the application State object
        """
        pass
