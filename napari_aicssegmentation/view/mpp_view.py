import logging
from napari_aicssegmentation.core.view import View
from napari_aicssegmentation.controller._interfaces import IMppController
from napari_aicssegmentation.util.debug_utils import debug_class
from qtpy.QtWidgets import QLayout, QPushButton, QLabel, QVBoxLayout

log = logging.getLogger(__name__)

@debug_class
class MppView(View):
    def __init__(self, controller: IMppController):
        if controller is None:
            raise ValueError("controller")

        self._layout = QVBoxLayout()
        self._controller = controller

    def get_layout(self) -> QLayout:
        return self._layout
        
    def setup_ui(self):
        btn_gaussian_blur = QPushButton("Gaussian kernel size = 3.0")
        btn_gaussian_blur.clicked.connect(self.btn_gaussian_blur_clicked)

        lbl_description = QLabel("Click button to smooth the current viewport image, higher numbers blur more. Result is displayed as a new channel.")
        lbl_description.setWordWrap(True)

        btn_next = QPushButton("Next")
        btn_next.clicked.connect(self.btn_next_clicked)
        
        self._layout.addWidget(lbl_description)
        self._layout.addWidget(btn_gaussian_blur)
        self._layout.addWidget(btn_next)

    # Event handlers        
    def btn_gaussian_blur_clicked(self, checked: bool):
        self._controller.run_gaussian_blur()

    def btn_next_clicked(self, checked: bool):
        self._controller.navigate_next()
