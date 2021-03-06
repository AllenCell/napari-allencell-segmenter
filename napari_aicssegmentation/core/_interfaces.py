import napari

from abc import ABC, abstractmethod, abstractproperty

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
        Get the application Router
        """
        pass
