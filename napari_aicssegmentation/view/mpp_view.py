import logging

from napari_aicssegmentation.view.interfaces import IMppView
from napari_aicssegmentation.controller.mpp_controller import MppController
from napari_aicssegmentation.ui_manager import UIManager
from napari_aicssegmentation.util.debug_utils import debug_class
from qtpy.QtWidgets import QLayout, QPushButton, QLabel, QVBoxLayout

log = logging.getLogger(__name__)

@debug_class
class MppView(IMppView):
    _btn_gaussian_blur: QPushButton
    _lbl_description: QLabel    

    def __init__(self, ui_manager: UIManager):
        if ui_manager is None:
            raise ValueError("ui_manager")
                
        self._layout = QVBoxLayout()
        self._controller = MppController(ui_manager, self)

    def get_layout(self) -> QLayout:
        return self._layout
        
    def setup_ui(self):                
        self._btn_gaussian_blur = QPushButton("Gaussian kernel size = 3.0")
        self._btn_gaussian_blur.clicked.connect(self.btn_gaussian_blur_clicked)

        self._lbl_description = QLabel("Click button to smooth the current viewport image, higher numbers blur more. Result is displayed as a new channel.")
        self._lbl_description.setWordWrap(True)
        
        self._layout.addWidget(self._lbl_description)
        self._layout.addWidget(self._btn_gaussian_blur)                

    # Event handlers        
    def btn_gaussian_blur_clicked(self, checked: bool):
        self._controller.run_gaussian_blur()     
