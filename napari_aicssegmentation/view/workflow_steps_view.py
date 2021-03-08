from napari_aicssegmentation.util.debug_utils import debug_class
from qtpy.QtWidgets import QLabel, QPushButton, QVBoxLayout
from napari_aicssegmentation.controller._interfaces import IWorkflowStepsController
from napari_aicssegmentation.core.view import View

@debug_class
class WorkflowStepsView(View):
    def __init__(self, controller: IWorkflowStepsController):
        if controller is None:
            raise ValueError("controller")
        self._layout = QVBoxLayout()
        self._controller = controller

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