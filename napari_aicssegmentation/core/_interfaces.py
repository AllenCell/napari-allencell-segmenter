import napari

from abc import ABC, abstractmethod, abstractproperty
from napari_aicssegmentation.core.view_manager import ViewManager
from napari_aicssegmentation.core.state import State


class IRouter(ABC):
    """
    Application Router
    The router handles navigation from one view to another
    """

    @abstractmethod
    def mpp(self):
        """
        Navigate to MPP screen
        """
        pass

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


class IApplication(ABC):
    """
    Main application container
    """

    @abstractproperty
    def viewer(self) -> napari.Viewer:
        """
        Get the main Napari viewer
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
