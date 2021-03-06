from napari_aicssegmentation.util.debug_utils import debug_class
from qtpy.QtWidgets import QLabel, QPushButton, QVBoxLayout
from napari_aicssegmentation.controller.workflow_steps_controller import WorkflowStepsController
from napari_aicssegmentation.core._interfaces import IApplication
from napari_aicssegmentation.core.view import View
from napari_aicssegmentation.view._interfaces import IWorkflowStepsView

@debug_class
class WorkflowStepsView(View, IWorkflowStepsView):
    def __init__(self, application: IApplication):
        self._layout = QVBoxLayout()
        self._controller = WorkflowStepsController(application, self)

    def get_layout(self):
        return self._layout

    def setup_ui(self):
        lbl_title = QLabel("Workflow - SEC61B")
        lbl_select = QLabel("Pre processing steps")
                
        
        btn_back = QPushButton("Back")
        btn_back.clicked.connect(self.btn_back_clicked)

        self._layout.addWidget(lbl_title)
        self._layout.addWidget(lbl_select)        
        self._layout.addWidget(btn_back)
    
    def btn_back_clicked(self, checked:bool):
        self._controller.navigate_back()