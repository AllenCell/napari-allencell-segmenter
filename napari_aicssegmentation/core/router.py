from napari_aicssegmentation.util.debug_utils import debug_class
from napari_aicssegmentation.controller.mpp_controller import MppController
from napari_aicssegmentation.controller.workflow_select_controller import WorkflowSelectController
from napari_aicssegmentation.controller.workflow_steps_controller import WorkflowStepsController

from ._interfaces import IApplication, IRouter

# TODO it would be nice to have all controllers injected as dependencies (better for testing)
# However I would want them to be lazily instianciated to avoid loading all Controllers/Views in memory immediately
@debug_class
class Router(IRouter):
    _controller = None

    def __init__(self, application: IApplication):
        if application is None:
            raise ValueError("application")
        self._application = application

    def mpp(self):
        self._controller = MppController(self._application)
        self._controller.index()

    def workflow_selection(self):
        self._controller = WorkflowSelectController(self._application)
        self._controller.index()

    def workflow_steps(self):
        self._controller = WorkflowStepsController(self._application)
        self._controller.index()