from napari_aicssegmentation.util.debug_utils import debug_class
from qtpy.QtWidgets import QComboBox, QLabel, QPushButton, QVBoxLayout
from napari_aicssegmentation.controller._interfaces import IWorkflowSelectController
from napari_aicssegmentation.core.view import View

@debug_class
class WorkflowSelectView(View):
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
        
        ddl_channels = QComboBox()
        ddl_channels.addItems(["brightfield", "405nm", "488nm"])
        
        btn_back = QPushButton("Back")
        btn_back.clicked.connect(self.btn_back_clicked)

        btn_next = QPushButton("Next")
        btn_next.clicked.connect(self.btn_next_clicked)

        self._layout.addWidget(lbl_title)
        self._layout.addWidget(lbl_select)
        self._layout.addWidget(ddl_channels)
        self._layout.addWidget(btn_back)
        self._layout.addWidget(btn_next)
    
    def btn_back_clicked(self, checked:bool):
        self._controller.navigate_back()

    def btn_next_clicked(self, checked:bool):
        self._controller.navigate_next()