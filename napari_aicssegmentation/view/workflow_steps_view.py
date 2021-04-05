from qtpy.QtWidgets import (
    QHBoxLayout,
    QLabel, 
    QLayout, 
    QProgressBar,
    QPushButton, 
    QVBoxLayout, 
    QWidget
)
from napari_aicssegmentation.model.segmenter_model import SegmenterModel
from napari_aicssegmentation.util.debug_utils import debug_class
from napari_aicssegmentation.controller._interfaces import IWorkflowStepsController
from napari_aicssegmentation.core.view import View
from ._main_template import MainTemplate


@debug_class
class WorkflowStepsView(View):  # pragma: no-cover
    # _lbl_selected_workflow: QLabel

    def __init__(self, controller: IWorkflowStepsController):
        super().__init__(template_class=MainTemplate)

        if controller is None:
            raise ValueError("controller")
        self._controller = controller

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

        # self._lbl_selected_workflow = QLabel()

        btn_run_all = QPushButton("Run all")
        btn_run_all.clicked.connect(self._btn_back_clicked)

        # Add all widgets
        self._add_workflow_title(layout)
        self._add_progress_bar(layout)
        layout.addStretch()
        layout.addWidget(btn_run_all)

    def load_model(self, model: SegmenterModel):
        pass
        # self._lbl_selected_workflow.setText(f"Selected workflow: {model.active_workflow}")
        # self._lbl_selected_workflow.repaint()

    def _btn_back_clicked(self, checked: bool):
        self._controller.navigate_back()

    def _add_workflow_title(self, layout: QLayout):
        widget = QWidget()
        title_layout = QHBoxLayout()
        widget.setLayout(title_layout)

        config_workflow_name = "sec61b"
        workflow_name = QLabel(f"Workflow: {config_workflow_name}")
        info = QLabel("ⓘ")

        title_layout.addStretch()
        title_layout.addWidget(workflow_name)
        title_layout.addWidget(info)
        title_layout.addStretch()

        title_layout.setSpacing(0)
        widget.setObjectName("workflowTitle")
        layout.addWidget(widget)
    
    def _add_progress_bar(self, layout: QLayout):
        widget = QProgressBar()
        widget.setValue(70)
        widget.setTextVisible(False)
        layout.addWidget(widget)
