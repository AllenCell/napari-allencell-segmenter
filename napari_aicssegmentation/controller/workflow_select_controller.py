from typing import List
from napari.layers import Layer
from napari.utils.events.event import Event
from napari_aicssegmentation.util.debug_utils import debug_class
from napari_aicssegmentation.model.segmenter_model import SegmenterModel
from napari_aicssegmentation.view.workflow_select_view import WorkflowSelectView
from napari_aicssegmentation.core._interfaces import IApplication
from napari_aicssegmentation.controller._interfaces import IWorkflowSelectController
from napari_aicssegmentation.core.controller import Controller
from napari_aicssegmentation.model.channel import Channel
from aicsimageio import AICSImage

@debug_class
class WorkflowSelectController(Controller, IWorkflowSelectController):
    def __init__(self, application: IApplication):
        super().__init__(application)
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
            self.model.channels = self._get_channels(self.model.selected_layer)

        # TODO load workflow objects from Segmenter workflow engine
        # -> https://github.com/AllenCell/napari-aicssegmentation/issues/26
        self.model.workflows = ["SEC61B", "LMNB1", "ACTN1"]
        self._view.load_model(self.model)

    def select_layer(self, layer_name: str):        
        self.model.selected_layer = next(filter(lambda layer: layer.name == layer_name, self.get_layers()), None)        
        self.model.channels = self._get_channels(self.model.selected_layer)
        self._view.update_channels(self.model.channels, self.model.selected_channel)

    def unselect_layer(self):
        self.model.selected_layer = None
        self.model.channels = None
        self.model.selected_channel = None
        self._view.update_channels(self.model.channels)

    def select_channel(self, channel: Channel):
        self.model.selected_channel = channel     
        self._view.update_workflows(enabled=True)
        
    def unselect_channel(self):
        self.model.selected_channel = None
        self._view.update_workflows(enabled=False)        

    def select_workflow(self, workflow: str):
        self.model.active_workflow = workflow
        # TODO create Layer 0 -> https://github.com/AllenCell/napari-aicssegmentation/issues/27
        self.router.workflow_steps()

    def _get_3D_layers(self) -> List[str]:
        """
        Get all 3D image layers currently loaded in the Napari viewer
        """
        layers = self.get_layers()
        return [layer.name for layer in layers if layer.ndim >= 3]

    def _get_channels(self, layer: Layer) -> List[Channel]:
        """
        Get the list of image channels from a layer
        TODO this is a workaround for now and we just guess the Channel dimension based on its location for most ome tiffs
        TODO use aicsimageio to read image from the source file path and get channel names
             once Napari exposes Image layer source (next release)
        """
        if layer is None:
            return None
            
        channels = list()                
        img = AICSImage(layer.data)
        for index in range(img.shape[3]):
            channels.append(Channel(index))
        return channels

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

        if self.model.selected_layer is not None and self.model.selected_layer.name not in self.model.layers:
            self._reset_channels()
