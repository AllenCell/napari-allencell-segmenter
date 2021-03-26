from napari_aicssegmentation.model.segmenter_model import SegmenterModel
from napari_aicssegmentation.util.debug_utils import debug_class
from qtpy.QtWidgets import QComboBox, QLabel, QPushButton, QVBoxLayout
from napari_aicssegmentation.controller._interfaces import IWorkflowSelectController
from napari_aicssegmentation.core.view import View


@debug_class
class WorkflowSelectView(View):
    # UI elements
    combo_channels: QComboBox
    combo_workflows: QComboBox  # TODO this will be a fancy grid later
    lbl_title: QLabel
    lbl_select: QLabel
    btn_back: QPushButton
    btn_next: QPushButton

    def __init__(self, controller: IWorkflowSelectController):
        if controller is None:
            raise ValueError("controller")
        self._controller = controller


    def setup_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
                
        self.lbl_title = QLabel("Segmentation workflow selection")
        self.lbl_select = QLabel("Select a channel")

        self.combo_channels = QComboBox()
        self.combo_channels.currentIndexChanged.connect(self._combo_channels_index_changed)
        self.combo_workflows = QComboBox()
        self.combo_workflows.currentIndexChanged.connect(self._combo_workflows_index_changed)

        self.btn_back = QPushButton("Back")
        self.btn_back.clicked.connect(self._btn_back_clicked)

        self.btn_next = QPushButton("Next")
        self.btn_next.clicked.connect(self._btn_next_clicked)

        layout.addWidget(self.lbl_title)
        layout.addWidget(self.lbl_select)
        layout.addWidget(self.combo_channels)
        layout.addWidget(self.combo_workflows)
        layout.addWidget(self.btn_back)
        layout.addWidget(self.btn_next)

    def load_model(self, model: SegmenterModel):
        self.combo_channels.addItems(model.channel_list)
        self.combo_workflows.addItems(model.workflows)

    def _btn_back_clicked(self, checked: bool):
        self._controller.navigate_back()

    def _btn_next_clicked(self, checked: bool):
        self._controller.navigate_next()

    def _combo_channels_index_changed(self, index: int):
        self._controller.select_channel(index)

    def _combo_workflows_index_changed(self, index: int):
        self._controller.select_workflow(self.combo_workflows.currentText())
