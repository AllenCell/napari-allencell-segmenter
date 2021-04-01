from qtpy.QtWidgets import QLabel, QPushButton, QVBoxLayout
from napari_aicssegmentation.model.segmenter_model import SegmenterModel
from napari_aicssegmentation.util.debug_utils import debug_class
from napari_aicssegmentation.controller._interfaces import IWorkflowStepsController
from napari_aicssegmentation.core.view import View
from ._main_template import MainTemplate


@debug_class
class WorkflowStepsView(View):  # pragma: no-cover
    _lbl_selected_workflow: QLabel

    def __init__(self, controller: IWorkflowStepsController):
        super().__init__(template_class=MainTemplate)

        if controller is None:
            raise ValueError("controller")
        self._controller = controller

    def setup_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        lbl_title = QLabel("Workflow steps")
        self._lbl_selected_workflow = QLabel()

        btn_back = QPushButton("Back")
        btn_back.clicked.connect(self._btn_back_clicked)

        layout.addWidget(lbl_title)
        layout.addWidget(self._lbl_selected_workflow)
        layout.addWidget(btn_back)

    def load_model(self, model: SegmenterModel):
        self._lbl_selected_workflow.setText(f"Selected workflow: {model.active_workflow}")
        self._lbl_selected_workflow.repaint()

    def _btn_back_clicked(self, checked: bool):
        self._controller.navigate_back()
