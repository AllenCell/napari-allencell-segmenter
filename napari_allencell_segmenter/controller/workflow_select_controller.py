from typing import List
from napari.utils.events.event import Event
from napari_allencell_segmenter.model.segmenter_model import SegmenterModel
from napari_allencell_segmenter.view.workflow_select_view import WorkflowSelectView
from napari_allencell_segmenter.core._interfaces import IApplication
from napari_allencell_segmenter.controller._interfaces import IWorkflowSelectController
from napari_allencell_segmenter.core.controller import Controller
from napari_allencell_segmenter.model.channel import Channel
from napari_allencell_segmenter.core.layer_reader import LayerReader
from aicssegmentation.workflow import WorkflowEngine


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
        self.model.layers = self._get_3D_layers()

        # pre-selection
        active_layer = None
        if len(self.viewer.get_active_layer()) > 0:
            active_layer = self.viewer.get_active_layer()[0]

        if active_layer is not None and active_layer.name in self.model.layers:
            self.model.selected_layer = active_layer
            self.model.channels = self._layer_reader.get_channels(self.model.selected_layer)

        self.model.workflows = self._workflow_engine.workflow_definitions

        self.load_view(self._view, self.model)

    def cleanup(self):
        # Disconnect events so that controller instances aren't kept around
        self.viewer.events.layers_change.disconnect(self._handle_layers_change)

    def select_layer(self, layer_name: str):
        self.model.selected_layer = next(filter(lambda layer: layer.name == layer_name, self.viewer.get_layers()), None)
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

    def select_workflow(self, workflow_name: str):
        channel_data = self._layer_reader.get_channel_data(self.model.selected_channel.index, self.model.selected_layer)
        self.model.active_workflow = self._workflow_engine.get_executable_workflow(workflow_name, channel_data)

        self.viewer.add_image_layer(
            channel_data,
            name="0: "
            + self.model.selected_layer.name
            + ": ch["
            + str(self.model.selected_channel.index)
            + "] "
            + workflow_name,
        )  # layer 0

        self.router.workflow_steps()

    def _get_3D_layers(self) -> List[str]:
        """
        Get all 3D image layers currently loaded in the Napari viewer
        """
        layers = self.viewer.get_layers()
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
