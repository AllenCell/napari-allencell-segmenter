from aicssegmentation.workflow import WorkflowEngine
from napari_allencell_segmenter.controller.workflow_select_controller import WorkflowSelectController
from napari_allencell_segmenter.controller.workflow_steps_controller import WorkflowStepsController
from napari_allencell_segmenter.controller.batch_processing_controller import BatchProcessingController
from napari_allencell_segmenter.core.layer_reader import LayerReader
from napari_allencell_segmenter.core.controller import Controller
from ._interfaces import IApplication, IRouter


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
        controller = WorkflowSelectController(self._application, self._layer_reader, self._workflow_engine)
        self._handle_navigation(controller)

    def workflow_steps(self):
        controller = WorkflowStepsController(self._application, self._workflow_engine)
        self._handle_navigation(controller)

    def batch_processing(self):
        controller = BatchProcessingController(self._application, self._workflow_engine)
        self._handle_navigation(controller)

    def _handle_navigation(self, controller: Controller):
        if self._controller:
            self._controller.cleanup()
        self._controller = controller
        self._controller.index()
