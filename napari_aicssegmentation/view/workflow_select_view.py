from napari_aicssegmentation.model.segmenter_model import SegmenterModel
from napari_aicssegmentation.util.debug_utils import debug_class
from qtpy.QtWidgets import QComboBox, QLabel, QPushButton, QVBoxLayout
from napari_aicssegmentation.controller._interfaces import IWorkflowSelectController
from napari_aicssegmentation.core.view import View


@debug_class
class WorkflowSelectView(View):  # pragma: no-cover
    _combo_channels: QComboBox
    _combo_workflows: QComboBox  # TODO this will be a fancy grid later

    def __init__(self, controller: IWorkflowSelectController):
        if controller is None:
            raise ValueError("controller")
        self._layout = QVBoxLayout()
        self._controller = controller

    def get_layout(self):
        return self._layout

    def setup_ui(self):
        lbl_title = QLabel("Segmentation workflow selection")
        lbl_select = QLabel("Select a channel")
        
        self._combo_channels = QComboBox()
        self._combo_channels.currentIndexChanged.connect(self._combo_channels_index_changed)
        self._combo_workflows = QComboBox()
        self._combo_workflows.currentIndexChanged.connect(self._combo_workflows_index_changed)
        
        btn_back = QPushButton("Back")
        btn_back.clicked.connect(self._btn_back_clicked)

        btn_next = QPushButton("Next")
        btn_next.clicked.connect(self._btn_next_clicked)

        self._layout.addWidget(lbl_title)
        self._layout.addWidget(lbl_select)
        self._layout.addWidget(self._combo_channels)
        self._layout.addWidget(self._combo_workflows)
        self._layout.addWidget(btn_back)
        self._layout.addWidget(btn_next)
        
    def load_model(self, model: SegmenterModel):
        self._combo_channels.addItems(model.channel_list)
        self._combo_workflows.addItems(model.workflows)

    def _btn_back_clicked(self, checked: bool):
        self._controller.navigate_back()

    def _btn_next_clicked(self, checked: bool):
        self._controller.navigate_next()

    def _combo_channels_index_changed(self, index: int):
        self._controller.select_channel(index)

    def _combo_workflows_index_changed(self, index: int):
        self._controller.select_workflow(self._combo_workflows.currentText())
