from napari_aicssegmentation.util.debug_utils import debug_class
from napari_aicssegmentation.view.mpp_view import MppView
from napari_aicssegmentation.view.workflow_select_view import WorkflowSelectView
from napari_aicssegmentation.view.workflow_steps_view import WorkflowStepsView
from .view_manager import ViewManager
from ._interfaces import IApplication, IRouter

@debug_class
class Router(IRouter):
    def __init__(self, application: IApplication, view_manager: ViewManager):
        if application is None:
            raise ValueError("application")
        if view_manager is None:
            raise ValueError("view_manager")

        self._application = application
        self._view_manager = view_manager

    def mpp(self):
        view=MppView(self._application)
        self._view_manager.load_view(view)

    def workflow_selection(self):
        view=WorkflowSelectView(self._application)
        self._view_manager.load_view(view)

    def workflow_steps(self):
        view=WorkflowStepsView(self._application)
        self._view_manager.load_view(view)