from napari_aicssegmentation.model.segmenter_model import SegmenterModel
from napari_aicssegmentation.util.debug_utils import debug_class
from qtpy.QtWidgets import QLabel, QPushButton, QVBoxLayout
from napari_aicssegmentation.controller._interfaces import IWorkflowStepsController
from napari_aicssegmentation.core.view import View


@debug_class
class WorkflowStepsView(View):  # pragma: no-cover
    _lbl_selected_workflow: QLabel

    def __init__(self, controller: IWorkflowStepsController):
        if controller is None:
            raise ValueError("controller")
        self._layout = QVBoxLayout()
        self._controller = controller

    def get_layout(self):
        return self._layout

    def setup_ui(self):
        lbl_title = QLabel("Workflow steps")
        self._lbl_selected_workflow = QLabel()
                        
        btn_back = QPushButton("Back")
        btn_back.clicked.connect(self._btn_back_clicked)

        self._layout.addWidget(lbl_title)
        self._layout.addWidget(self._lbl_selected_workflow)
        self._layout.addWidget(btn_back)

    def load_model(self, model: SegmenterModel):
        self._lbl_selected_workflow.setText(f"Selected workflow: {model.active_workflow}")
        self._lbl_selected_workflow.repaint()
    
    def _btn_back_clicked(self, checked: bool):
        self._controller.navigate_back()
