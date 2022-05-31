import numpy

from napari.utils.events.event import Event
from unittest import mock
from unittest.mock import MagicMock, create_autospec, PropertyMock
from aicssegmentation.workflow.workflow import Workflow
from aicssegmentation.workflow import WorkflowEngine, WorkflowDefinition
from napari_allencell_segmenter.controller.workflow_select_controller import WorkflowSelectController
from napari_allencell_segmenter.core._interfaces import IApplication, IRouter
from napari_allencell_segmenter.core.layer_reader import LayerReader
from napari_allencell_segmenter.core.state import State
from napari_allencell_segmenter.core.view_manager import ViewManager
from napari_allencell_segmenter.model.segmenter_model import SegmenterModel
from napari_allencell_segmenter.model.channel import Channel
from napari_allencell_segmenter.core.viewer_abstraction import ViewerAbstraction
from ..mocks import MockLayer


class TestWorkflowSelectController:
    def setup_method(self):
        self._mock_application: MagicMock = create_autospec(IApplication)
        self._mock_viewer: MagicMock = create_autospec(ViewerAbstraction)
        type(self._mock_application).viewer = PropertyMock(return_value=self._mock_viewer)
        self._mock_router: MagicMock = create_autospec(IRouter)
        type(self._mock_application).router = PropertyMock(return_value=self._mock_router)
        self._mock_state: MagicMock = create_autospec(State)
        type(self._mock_application).state = PropertyMock(return_value=self._mock_state)
        self._mock_view_manager: MagicMock = create_autospec(ViewManager)
        type(self._mock_application).view_manager = PropertyMock(return_value=self._mock_view_manager)
        self._model = SegmenterModel()
        type(self._mock_state).segmenter_model = PropertyMock(return_value=self._model)
        self._mock_layer_reader: MagicMock = create_autospec(LayerReader)
        self._mock_workflow_engine: MagicMock = create_autospec(WorkflowEngine)

        with mock.patch("napari_allencell_segmenter.controller.workflow_select_controller.WorkflowSelectView"):
            self._controller = WorkflowSelectController(
                self._mock_application, self._mock_layer_reader, self._mock_workflow_engine
            )

    def test_index(self):
        # Arrange
        active_layer = MockLayer(name="Layer 1", ndim=3)
        layers = [
            active_layer,
            MockLayer(name="Layer 2", ndim=3),
            MockLayer(name="Layer 3", ndim=3),
            MockLayer(name="2D Layer", ndim=2),
        ]
        channels = [Channel(0), Channel(1), Channel(2), Channel(3)]
        workflows = [
            create_autospec(WorkflowDefinition),
            create_autospec(WorkflowDefinition),
            create_autospec(WorkflowDefinition),
        ]
        self._mock_viewer.get_layers.return_value = layers
        self._mock_viewer.get_active_layer.return_value = [active_layer]
        type(self._mock_workflow_engine).workflow_definitions = PropertyMock(return_value=workflows)
        self._mock_layer_reader.get_channels.return_value = channels

        # Act
        self._controller.index()

        # Assert
        self._mock_view_manager.load_view.assert_called_once_with(self._controller.view, self._model)
        assert self._controller.model.layers == ["Layer 1", "Layer 2", "Layer 3"]
        assert self._controller.model.selected_layer == active_layer
        assert self._controller.model.channels == channels
        assert self._controller.model.workflows == workflows

    def test_select_layer(self):
        # Arrange
        expected_layer = MockLayer(name="Layer 2")
        layers = [MockLayer(name="Layer 1", ndim=3), expected_layer, MockLayer(name="Layer 3", ndim=3)]
        channels = [Channel(0), Channel(1), Channel(2), Channel(3)]
        self._mock_viewer.get_layers.return_value = layers
        self._mock_layer_reader.get_channels.return_value = channels

        # Act
        self._controller.select_layer("Layer 2")

        # Assert
        assert self._controller.model.selected_layer == expected_layer

    def test_unselect_layer(self):
        # Act
        self._controller.unselect_layer()

        # Assert
        assert self._controller.model.selected_layer is None
        assert self._controller.model.channels is None
        assert self._controller.model.selected_channel is None
        self._controller.view.update_channels.assert_called_once()

    def test_select_channel(self):
        # Act
        channel = Channel(0, "Brightfield")
        self._controller.select_channel(channel)

        # Assert
        assert self._controller.model.selected_channel == channel
        self._controller.view.update_workflows.assert_called_with(enabled=True)

    def test_unselect_channel(self):
        # Act
        self._controller.unselect_channel()

        # Assert
        assert self._controller.model.selected_channel is None
        self._controller.view.update_workflows.assert_called_with(enabled=False)

    def test_select_workflow(self):
        # Arrange
        layer0 = MockLayer("Layer 0", ndim=4)
        expected_workflow = create_autospec(Workflow)
        self._model.channels = [Channel(0), Channel(1), Channel(2), Channel(3)]
        self._model.selected_channel = Channel(0)
        self._model.selected_layer = MockLayer("Layer 1", ndim=4)
        self._mock_workflow_engine.get_executable_workflow.return_value = expected_workflow
        self._mock_viewer.add_image_layer.return_value = layer0
        self._mock_layer_reader.get_channel_data.return_value = numpy.ones((75, 100, 100))

        # Act
        self._controller.select_workflow("sec61b")

        # Assert
        assert self._controller.model.active_workflow == expected_workflow
        self._mock_router.workflow_steps.assert_called_once()

    def test_handle_layers_change_resets_channels(self):
        # Arrange
        layers = [
            MockLayer(name="Layer 1", ndim=3),
            MockLayer(name="Layer 2", ndim=3),
            MockLayer(name="Layer 3", ndim=3),
        ]
        self._mock_viewer.get_layers.return_value = layers
        self._controller.model.channels = [Channel(0), Channel(1), Channel(2), Channel(3)]

        # Act
        self._controller._handle_layers_change(Event("test"))

        # Assert
        self._controller.model.layers == layers
        self._controller.view.update_layers.assert_called_once()
        self._controller.model.channels is None
        self._controller.model.selected_channel is None
        self._controller.view.update_workflows.assert_called_with(enabled=False)

    def test_handle_layers_change_keeps_channels(self):
        # Arrange
        selected_layer = MockLayer(name="Layer 1", ndim=3)
        layers = [
            selected_layer,
            MockLayer(name="Layer 2", ndim=3),
            MockLayer(name="Layer 3", ndim=3),
        ]
        selected_channel = Channel(3)
        channels = [Channel(0), Channel(1), Channel(2), selected_channel]
        self._mock_viewer.get_layers.return_value = layers
        self._controller.model.channels = channels
        self._controller.model.selected_layer = selected_layer
        self._controller.model.selected_channel = selected_channel

        # Act
        self._controller._handle_layers_change(Event("test"))

        # Assert
        self._controller.model.layers == layers
        self._controller.view.update_layers.assert_called_once()
        self._controller.model.channels == channels
        self._controller.model.selected_channel == selected_channel
