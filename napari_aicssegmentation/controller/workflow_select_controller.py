from typing import List
from napari.utils.events.event import Event
from napari_aicssegmentation.util.debug_utils import debug_class
from napari_aicssegmentation.model.segmenter_model import SegmenterModel
from napari_aicssegmentation.view.workflow_select_view import WorkflowSelectView
from napari_aicssegmentation.core._interfaces import IApplication
from napari_aicssegmentation.controller._interfaces import IWorkflowSelectController
from napari_aicssegmentation.core.controller import Controller
from napari_aicssegmentation.model.channel import Channel
from napari_aicssegmentation.core.layer_reader import LayerReader
from aicssegmentation.workflow import WorkflowEngine


@debug_class
class WorkflowSelectController(Controller, IWorkflowSelectController):
    def __init__(self, application: IApplication, layer_reader: LayerReader, workflow_engine: WorkflowEngine):
        super().__init__(application)
        if layer_reader is None:
            raise ValueError("layer_reader")
        if workflow_engine is None:
            raise ValueError("workflow_engine")
        self._layer_reader = layer_reader
        self._workflow_engine = workflow_engine
        self._view = WorkflowSelectView(self)
        self.viewer.events.layers_change.connect(self._handle_layers_change)

    @property
    def view(self) -> WorkflowSelectView:
        return self._view

    @property
    def model(self) -> SegmenterModel:
        return self.state.segmenter_model

    def index(self):
        self.load_view(self._view)
        self.model.layers = self._get_3D_layers()

        # pre-selection
        if self.get_active_layer() is not None and self.get_active_layer().name in self.model.layers:
            self.model.selected_layer = self.get_active_layer()
            self.model.channels = self._layer_reader.get_channels(self.model.selected_layer)

        self.model.workflows = self._workflow_engine.workflow_definitions
        self._view.load_model(self.model)

    def select_layer(self, layer_name: str):
        self.model.selected_layer = next(filter(lambda layer: layer.name == layer_name, self.get_layers()), None)
        self.model.channels = self._layer_reader.get_channels(self.model.selected_layer)
        self._view.update_channels(self.model.channels, self.model.selected_channel)

    def unselect_layer(self):
        self.model.selected_layer = None
        self.model.channels = None
        self.model.selected_channel = None
        self._view.update_channels(self.model.channels)
        self._view.update_workflows(enabled=False)

    def select_channel(self, channel: Channel):
        self.model.selected_channel = channel
        self._view.update_workflows(enabled=True)

    def unselect_channel(self):
        self.model.selected_channel = None
        self._view.update_workflows(enabled=False)

    def select_workflow(self, selected_workflow: str):
        self.model.active_workflow = selected_workflow
        self.viewer.add_image(
            self.model.selected_layer.data,
            name="0. " + self.model.layers[0] + ": ch[" + str(self.model.selected_channel.index) + "] " + selected_workflow,
        )
        self.router.workflow_steps(selected_workflow)

    def _get_3D_layers(self) -> List[str]:
        """
        Get all 3D image layers currently loaded in the Napari viewer
        """
        layers = self.get_layers()
        return [layer.name for layer in layers if layer.ndim >= 3]

    def _reset_channels(self):
        self.model.channels = None
        self._view.update_channels(self.model.channels)
        self.unselect_channel()

    #####################################################################
    # Event handlers
    #####################################################################

    def _handle_layers_change(self, e: Event):
        """
        Event handler for Napari viewer <layers_change> event
        This is triggered whenever changes are made to the layer list (such as adding or deleting a layer)
        """
        self.model.layers = self._get_3D_layers()
        self._view.update_layers(self.model.layers, self.model.selected_layer)

        if self.model.selected_layer is None or self.model.selected_layer.name not in self.model.layers:
            self._reset_channels()
