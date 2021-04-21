from aicssegmentation.workflow import WorkflowEngine
from napari_aicssegmentation.util.debug_utils import debug_class
from napari_aicssegmentation.controller.workflow_select_controller import WorkflowSelectController
from napari_aicssegmentation.controller.workflow_steps_controller import WorkflowStepsController
from napari_aicssegmentation.core.layer_reader import LayerReader
from ._interfaces import IApplication, IRouter


@debug_class
class Router(IRouter):
    _controller = None

    def __init__(self, application: IApplication):
        if application is None:
            raise ValueError("application")
        self._application = application
        # TODO do some proper dependency injection in the future if the project grows
        self._layer_reader = LayerReader()
        self._workflow_engine = WorkflowEngine()

    def workflow_selection(self):
        self._controller = WorkflowSelectController(self._application, self._layer_reader, self._workflow_engine)
        self._controller.index()

    def workflow_steps(self):
        self._controller = WorkflowStepsController(self._application, self._workflow_engine)
        self._controller.index()
