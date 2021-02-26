import logging
from napari_aicssegmentation.mvc.mpp_interfaces import IMppView
from qtpy.QtWidgets import QLayout, QPushButton, QLabel
from .mpp_controller import MppController
from .mpp_model import MppModel
from ..ui_manager import UIManager
from ..util.debug_utils import debug_class
log = logging.getLogger(__name__)

@debug_class
class MppView(IMppView): 

    def __init__(self, ui_manager: UIManager):
        if ui_manager is None:
            raise ValueError("ui_manager")

        self._layout = ui_manager.base_layout
        self._controller = MppController(ui_manager, self)
    
    def present(self):
        btn = QPushButton("Gaussian kernel size = 3.0")
        btn.clicked.connect(self.btn_gaussian_blur_clicked)

        desc = QLabel("Click button to smooth the current viewport image, higher numbers blur more. Result is displayed as a new channel.")
        desc.setWordWrap(True)
        
        self._layout.addWidget(desc)
        self._layout.addWidget(btn)       

    # Events    
    def btn_gaussian_blur_clicked(self, sender):        
        self._controller.run_gaussian_blur()
